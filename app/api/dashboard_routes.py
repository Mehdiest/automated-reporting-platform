"""
Dashboard Routes
================
REST endpoints that power the reporting dashboard.
Provides aggregated KPI summaries and a catalogue of generated reports
for consumption by the frontend or any BI tool.

GET /dashboard/        — Serve the dashboard HTML page
GET /dashboard/stats   — Aggregated KPI summary across all reports
GET /dashboard/reports — List of all generated PDF reports on disk
"""

import os
import json
import glob
import logging
from datetime import datetime

from fastapi import APIRouter
from fastapi.responses import HTMLResponse, JSONResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

_REPORTS_DIR = "reports"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _scan_reports() -> list[dict]:
    """
    Scan the reports directory and return metadata for every PDF found.

    Returns:
        List of dicts with name, size_kb, created_at, and path.
    """
    pattern = os.path.join(_REPORTS_DIR, "*.pdf")
    files = glob.glob(pattern)

    report_list = []
    for filepath in sorted(files, key=os.path.getmtime, reverse=True):
        stat = os.stat(filepath)
        report_list.append({
            "name": os.path.basename(filepath),
            "size_kb": round(stat.st_size / 1024, 1),
            "created_at": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "path": filepath,
        })

    return report_list


def _build_stats(reports: list[dict]) -> dict:
    """
    Derive simple dashboard statistics from the reports list.

    Args:
        reports: Output of _scan_reports().

    Returns:
        Dict of summary stats shown on the dashboard.
    """
    total_size_kb = sum(r["size_kb"] for r in reports)

    # Separate single vs multi reports by naming convention
    single = [r for r in reports if not r["name"].startswith("multi_")]
    multi = [r for r in reports if r["name"].startswith("multi_")]
    scheduled = [r for r in reports if r["name"].startswith("report_")]

    return {
        "total_reports": len(reports),
        "single_dataset_reports": len(single),
        "multi_dataset_reports": len(multi),
        "scheduled_reports": len(scheduled),
        "total_size_kb": round(total_size_kb, 1),
        "last_generated": reports[0]["created_at"] if reports else None,
    }


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/reports", response_class=JSONResponse)
def list_reports() -> dict:
    """
    Return a catalogue of all PDF reports currently on disk.
    Sorted by most recently generated first.
    """
    reports = _scan_reports()
    return {
        "status": "ok",
        "count": len(reports),
        "reports": reports,
    }


@router.get("/stats", response_class=JSONResponse)
def get_stats() -> dict:
    """
    Return aggregated dashboard statistics derived from generated reports.
    Used by the frontend to populate summary cards and charts.
    """
    reports = _scan_reports()
    stats = _build_stats(reports)
    return {"status": "ok", "stats": stats}


@router.get("/", response_class=HTMLResponse)
def serve_dashboard() -> HTMLResponse:
    """
    Serve the dashboard HTML page.
    The page fetches live data from /dashboard/stats and /dashboard/reports.
    """
    html_path = os.path.join("app", "static", "dashboard.html")

    if not os.path.isfile(html_path):
        return HTMLResponse(content="<h2>Dashboard not found.</h2>", status_code=404)

    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    return HTMLResponse(content=content)
