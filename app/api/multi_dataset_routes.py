"""
Multi-Dataset Routes
=====================
REST endpoints for uploading multiple datasets simultaneously
and generating a single combined PDF report.

POST /multi/upload-and-report — Upload multiple files and get a unified PDF
GET  /multi/download-report   — Download the last generated combined report
"""

import os
import tempfile

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from typing import List

from app.services.multi_dataset_processor import process_multiple_datasets
from app.services.multi_report_generator import generate_multi_report

router = APIRouter(prefix="/multi", tags=["Multi-Dataset"])

_OUTPUT_PATH = "reports/multi_report.pdf"
_MAX_FILE_SIZE_MB = 10
_MAX_FILE_SIZE_BYTES = _MAX_FILE_SIZE_MB * 1024 * 1024


@router.post("/upload-and-report")
async def upload_multiple_and_report(
    files: List[UploadFile] = File(...),
) -> dict:
    """
    Accept multiple CSV or Excel files, compute KPIs for each,
    merge results, and generate a unified PDF report.

    Returns a summary of each dataset's KPIs plus merged aggregate KPIs.
    The generated PDF can be downloaded via GET /multi/download-report.
    """
    if len(files) < 2:
        raise HTTPException(
            status_code=400,
            detail="Please upload at least 2 files for a combined report.",
        )

    temp_files = []

    try:
        # --- Save uploads to temp files ---
        for upload in files:
            content = await upload.read()

            if len(content) > _MAX_FILE_SIZE_BYTES:
                raise HTTPException(
                    status_code=413,
                    detail=f"File '{upload.filename}' exceeds the {_MAX_FILE_SIZE_MB}MB limit.",
                )

            suffix = os.path.splitext(upload.filename)[-1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(content)
                temp_files.append((tmp.name, upload.filename))

        # --- Process all datasets ---
        result = process_multiple_datasets(temp_files)

        # --- Generate combined PDF ---
        os.makedirs("reports", exist_ok=True)
        generate_multi_report(result, output_path=_OUTPUT_PATH)

        # --- Build API response (exclude raw DataFrames) ---
        datasets_summary = [
            {
                "name": ds["name"],
                "row_count": ds["row_count"],
                "column_count": ds["column_count"],
                "columns": ds["columns"],
                "kpis": ds["kpis"],
            }
            for ds in result["datasets"]
        ]

        return {
            "status": "report_generated",
            "dataset_count": result["dataset_count"],
            "total_rows": result["total_rows"],
            "datasets": datasets_summary,
            "merged_kpis": result["merged_kpis"],
            "errors": result["errors"],
            "report": _OUTPUT_PATH,
        }

    finally:
        # --- Clean up temp files regardless of success or failure ---
        for temp_path, _ in temp_files:
            if os.path.exists(temp_path):
                os.remove(temp_path)


@router.get("/download-report")
def download_multi_report() -> FileResponse:
    """
    Download the most recently generated combined PDF report.

    Returns 404 if no report has been generated yet.
    """
    if not os.path.isfile(_OUTPUT_PATH):
        raise HTTPException(
            status_code=404,
            detail="No combined report found. Generate one via POST /multi/upload-and-report.",
        )

    return FileResponse(
        path=_OUTPUT_PATH,
        media_type="application/pdf",
        filename="combined_report.pdf",
    )
