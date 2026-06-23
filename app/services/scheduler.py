"""
Scheduler Service
=================
Manages background report-generation jobs using APScheduler.
Each job runs on an interval, processes a registered dataset,
calculates KPIs, produces a timestamped PDF report, and optionally
sends the report to a recipient via email.
"""

import os
import logging
from datetime import datetime
from typing import Optional

import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import JobLookupError

from app.services.kpi_engine import calculate_kpis
from app.services.report_generator import generate_report

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Module-level scheduler instance (singleton for the lifetime of the process)
# ---------------------------------------------------------------------------
_scheduler = BackgroundScheduler(timezone="UTC")


def start_scheduler() -> None:
    """Start the APScheduler background scheduler if it is not already running."""
    if not _scheduler.running:
        _scheduler.start()
        logger.info("APScheduler started.")


def shutdown_scheduler() -> None:
    """Gracefully shut down the scheduler on application exit."""
    if _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("APScheduler shut down.")


# ---------------------------------------------------------------------------
# Internal job function executed by APScheduler on each tick
# ---------------------------------------------------------------------------
def _run_report_job(
    job_id: str,
    dataset_path: str,
    output_dir: str,
    email_recipient: Optional[str] = None,
    email_subject: Optional[str] = None,
) -> None:
    """
    Core task executed by the scheduler for a given job.

    Loads the dataset from disk, computes KPIs, writes a timestamped PDF
    report, and optionally emails the report to a recipient.

    Args:
        job_id:           Unique identifier of the scheduled job.
        dataset_path:     Absolute or relative path to the CSV/XLSX file.
        output_dir:       Directory where the generated PDF will be saved.
        email_recipient:  If provided, the report PDF is emailed to this address.
        email_subject:    Subject line for the report email.
    """
    logger.info("[Job %s] Starting scheduled report run.", job_id)

    if not os.path.exists(dataset_path):
        logger.error("[Job %s] Dataset not found: %s", job_id, dataset_path)
        return

    try:
        ext = dataset_path.rsplit(".", 1)[-1].lower()
        if ext == "csv":
            df = pd.read_csv(dataset_path)
        elif ext == "xlsx":
            df = pd.read_excel(dataset_path, engine="openpyxl")
        else:
            logger.error("[Job %s] Unsupported file type: %s", job_id, ext)
            return

        if df.empty:
            logger.warning("[Job %s] Dataset is empty — skipping report.", job_id)
            return

        kpis = calculate_kpis(df)

        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(output_dir, f"report_{job_id}_{timestamp}.pdf")

        generate_report(df, kpis, output_path=output_path)
        logger.info("[Job %s] Report saved to %s", job_id, output_path)

        # --- Optional email delivery ---
        if email_recipient:
            try:
                from app.services.email_service import send_report_email
                subject = email_subject or f"Scheduled Report — {job_id} — {timestamp}"
                send_report_email(
                    recipient=email_recipient,
                    subject=subject,
                    body=f"Your scheduled report for job '{job_id}' is attached.",
                    attachment_path=output_path,
                )
                logger.info("[Job %s] Report emailed to %s", job_id, email_recipient)
            except Exception as email_exc:
                logger.error("[Job %s] Email delivery failed: %s", job_id, email_exc)

    except Exception as exc:
        logger.exception("[Job %s] Unexpected error during report run: %s", job_id, exc)


# ---------------------------------------------------------------------------
# Public API used by the route layer
# ---------------------------------------------------------------------------
def add_job(
    job_id: str,
    dataset_path: str,
    interval_minutes: int,
    output_dir: str = "reports",
    email_recipient: Optional[str] = None,
    email_subject: Optional[str] = None,
) -> dict:
    """
    Register a new recurring report job.

    Args:
        job_id:            Unique name for the job.
        dataset_path:      Path to the source CSV or XLSX file.
        interval_minutes:  How often (in minutes) the job should run.
        output_dir:        Directory to write generated PDF reports.
        email_recipient:   Optional email address to receive the report.
        email_subject:     Optional subject line for the report email.

    Returns:
        A dict describing the registered job.

    Raises:
        ValueError: If a job with the same ID already exists, or interval is invalid.
    """
    if interval_minutes < 1:
        raise ValueError("interval_minutes must be >= 1.")

    if _scheduler.get_job(job_id):
        raise ValueError(f"A job with id '{job_id}' already exists.")

    _scheduler.add_job(
        func=_run_report_job,
        trigger="interval",
        minutes=interval_minutes,
        id=job_id,
        kwargs={
            "job_id": job_id,
            "dataset_path": dataset_path,
            "output_dir": output_dir,
            "email_recipient": email_recipient,
            "email_subject": email_subject,
        },
        replace_existing=False,
    )

    logger.info("Job '%s' registered — runs every %d minute(s).", job_id, interval_minutes)
    return {
        "job_id": job_id,
        "dataset_path": dataset_path,
        "interval_minutes": interval_minutes,
        "output_dir": output_dir,
        "email_recipient": email_recipient,
    }


def list_jobs() -> list[dict]:
    """
    Return a summary of all currently registered jobs.

    Returns:
        List of dicts with job_id, next_run_time, and trigger info.
    """
    return [
        {
            "job_id": job.id,
            "next_run_time": str(job.next_run_time) if job.next_run_time else "paused",
            "trigger": str(job.trigger),
        }
        for job in _scheduler.get_jobs()
    ]


def remove_job(job_id: str) -> bool:
    """
    Remove a registered job by its ID.

    Args:
        job_id: The unique job identifier to remove.

    Returns:
        True if the job was found and removed, False if it did not exist.
    """
    try:
        _scheduler.remove_job(job_id)
        logger.info("Job '%s' removed.", job_id)
        return True
    except JobLookupError:
        return False
