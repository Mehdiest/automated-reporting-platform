"""
Scheduler Routes
================
REST endpoints for managing scheduled report jobs.

POST   /scheduler/jobs          — Register a new recurring job
GET    /scheduler/jobs          — List all active jobs
DELETE /scheduler/jobs/{job_id} — Remove a job by ID
"""

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field

from app.services.scheduler import add_job, list_jobs, remove_job

router = APIRouter(prefix="/scheduler", tags=["Scheduler"])


# ---------------------------------------------------------------------------
# Request schema
# ---------------------------------------------------------------------------
class ScheduleJobRequest(BaseModel):
    """Payload for registering a new scheduled report job."""

    job_id: str = Field(..., min_length=1, max_length=64, example="daily_sales_report")
    dataset_path: str = Field(..., example="data/sample.csv")
    interval_minutes: int = Field(..., ge=1, example=60)
    output_dir: str = Field(default="reports", example="reports")
    email_recipient: Optional[EmailStr] = Field(
        default=None,
        example="client@example.com",
        description="If provided, the generated report will be emailed to this address.",
    )
    email_subject: Optional[str] = Field(
        default=None,
        example="Your Scheduled Sales Report",
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@router.post("/jobs", status_code=201)
def create_job(payload: ScheduleJobRequest) -> dict:
    """
    Register a new recurring report job.

    The job loads the dataset at `dataset_path`, computes KPIs, and writes
    a PDF to `output_dir` every `interval_minutes` minutes.
    If `email_recipient` is set, the PDF is also emailed after each run.
    """
    try:
        job = add_job(
            job_id=payload.job_id,
            dataset_path=payload.dataset_path,
            interval_minutes=payload.interval_minutes,
            output_dir=payload.output_dir,
            email_recipient=payload.email_recipient,
            email_subject=payload.email_subject,
        )
        return {"status": "scheduled", "job": job}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/jobs")
def get_jobs() -> dict:
    """Return a list of all currently registered scheduled jobs."""
    return {"status": "ok", "jobs": list_jobs()}


@router.delete("/jobs/{job_id}")
def delete_job(job_id: str) -> dict:
    """
    Remove a scheduled job by its ID.

    Returns 404 if the job does not exist.
    """
    removed = remove_job(job_id)
    if not removed:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")
    return {"status": "removed", "job_id": job_id}
