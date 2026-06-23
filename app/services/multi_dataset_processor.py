"""
Multi-Dataset Processor
========================
Handles simultaneous ingestion of multiple CSV/Excel files.
Each file is processed independently, then results are merged
into a single unified report with per-dataset KPI sections.
"""

import os
import logging
from typing import Any

import pandas as pd

from app.services.kpi_engine import calculate_kpis

logger = logging.getLogger(__name__)

# Supported file extensions
_SUPPORTED_EXTENSIONS = {"csv", "xlsx"}


def _load_dataframe(file_path: str, original_filename: str) -> pd.DataFrame:
    """
    Load a single CSV or Excel file into a DataFrame.

    Args:
        file_path:         Path to the temporary file on disk.
        original_filename: Original filename used to infer file type.

    Returns:
        Loaded DataFrame.

    Raises:
        ValueError: If the file extension is unsupported or the file is empty.
    """
    ext = original_filename.rsplit(".", 1)[-1].lower()

    if ext not in _SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '.{ext}' for '{original_filename}'. "
            f"Accepted formats: {', '.join(_SUPPORTED_EXTENSIONS)}."
        )

    if ext == "csv":
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path, engine="openpyxl")

    if df.empty:
        raise ValueError(f"File '{original_filename}' is empty.")

    return df


def process_multiple_datasets(
    file_paths: list[tuple[str, str]],
) -> dict[str, Any]:
    """
    Process multiple datasets and return a unified result structure.

    Each file is loaded and its KPIs are computed independently.
    A merged summary is also produced by concatenating all DataFrames
    and computing aggregate KPIs across the full dataset.

    Args:
        file_paths: List of (temp_file_path, original_filename) tuples.

    Returns:
        A dict with the following structure:
        {
            "datasets": [
                {
                    "name": "sales.csv",
                    "row_count": 120,
                    "column_count": 8,
                    "columns": [...],
                    "kpis": {...},
                    "dataframe": <DataFrame>,
                }
            ],
            "merged_kpis": {...},
            "total_rows": 350,
            "dataset_count": 3,
        }

    Raises:
        ValueError: If no valid files are provided.
    """
    if not file_paths:
        raise ValueError("At least one file must be provided.")

    dataset_results = []
    valid_dataframes = []
    errors = []

    for temp_path, filename in file_paths:
        try:
            df = _load_dataframe(temp_path, filename)
            kpis = calculate_kpis(df)

            dataset_results.append({
                "name": filename,
                "row_count": len(df),
                "column_count": len(df.columns),
                "columns": list(df.columns),
                "kpis": kpis,
                "dataframe": df,
            })
            valid_dataframes.append(df)
            logger.info("Processed dataset '%s' — %d rows.", filename, len(df))

        except Exception as exc:
            logger.warning("Skipping '%s': %s", filename, exc)
            errors.append({"file": filename, "error": str(exc)})

    if not dataset_results:
        raise ValueError(
            f"No valid datasets could be processed. Errors: {errors}"
        )

    # --- Merged aggregate KPIs across all valid datasets ---
    merged_df = pd.concat(valid_dataframes, ignore_index=True)
    merged_kpis = calculate_kpis(merged_df)

    return {
        "datasets": dataset_results,
        "merged_kpis": merged_kpis,
        "total_rows": len(merged_df),
        "dataset_count": len(dataset_results),
        "errors": errors,
    }
