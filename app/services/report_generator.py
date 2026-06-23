"""
Report Generator
================
Builds a formatted PDF report from a DataFrame and its computed KPIs.
Uses ReportLab's Platypus layout engine for structured document generation.
"""

import os
import logging
from typing import Optional

import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

logger = logging.getLogger(__name__)

# Default output location used when no explicit path is provided
_DEFAULT_OUTPUT_DIR = "reports"
_DEFAULT_OUTPUT_PATH = os.path.join(_DEFAULT_OUTPUT_DIR, "output.pdf")


def generate_report(
    df: pd.DataFrame,
    kpis: dict,
    output_path: Optional[str] = None,
) -> str:
    """
    Generate a PDF report summarising the dataset and its KPIs.

    Args:
        df:          Source DataFrame (used for column/row metadata).
        kpis:        Dictionary of computed KPI values from kpi_engine.
        output_path: Full path (including filename) for the output PDF.
                     Defaults to 'reports/output.pdf'.

    Returns:
        The absolute path of the generated PDF file.

    Raises:
        RuntimeError: If ReportLab fails to build the document.
    """
    resolved_path = output_path or _DEFAULT_OUTPUT_PATH
    os.makedirs(os.path.dirname(resolved_path) or ".", exist_ok=True)

    styles = getSampleStyleSheet()
    content = []

    # --- Title ---
    content.append(Paragraph("Automated Report", styles["Title"]))
    content.append(Spacer(1, 0.2 * inch))

    # --- Dataset summary ---
    content.append(Paragraph("Dataset Summary", styles["Heading2"]))
    content.append(Paragraph(f"Total Rows: {len(df)}", styles["Normal"]))
    content.append(Paragraph(f"Total Columns: {len(df.columns)}", styles["Normal"]))
    content.append(Spacer(1, 0.15 * inch))

    # --- KPI table ---
    content.append(Paragraph("Key Performance Indicators", styles["Heading2"]))
    content.append(Spacer(1, 0.1 * inch))

    kpi_rows = [["Metric", "Value"]]
    for key, value in kpis.items():
        if isinstance(value, dict):
            # Flatten nested dicts (e.g. revenue_by_category, date_range)
            for sub_key, sub_val in value.items():
                kpi_rows.append([f"{key} — {sub_key}", str(sub_val)])
        else:
            kpi_rows.append([str(key).replace("_", " ").title(), str(value)])

    kpi_table = Table(kpi_rows, colWidths=[3 * inch, 3 * inch])
    kpi_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2D3748")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
            ("PADDING", (0, 0), (-1, -1), 6),
        ])
    )
    content.append(kpi_table)

    # --- Build PDF ---
    try:
        doc = SimpleDocTemplate(resolved_path)
        doc.build(content)
        logger.info("Report generated: %s", resolved_path)
    except Exception as exc:
        raise RuntimeError(f"Failed to build PDF report: {exc}") from exc

    return resolved_path
