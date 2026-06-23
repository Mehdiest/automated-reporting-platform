"""
Email Routes
============
REST endpoints for sending report emails manually.

POST /email/send-report — Send a generated PDF report to a recipient
"""

import os

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field

from app.services.email_service import send_report_email

router = APIRouter(prefix="/email", tags=["Email"])


# ---------------------------------------------------------------------------
# Request schema
# ---------------------------------------------------------------------------
class SendReportRequest(BaseModel):
    """Payload for sending a report email with an optional PDF attachment."""

    recipient: EmailStr = Field(..., example="client@example.com")
    subject: str = Field(default="Your Automated Report", example="Sales Report — June 2026")
    body: str = Field(
        default="Please find your automated report attached.",
        example="Hi,\n\nPlease find this week's sales report attached.\n\nBest regards.",
    )
    attachment_path: str = Field(
        default="reports/output.pdf",
        example="reports/output.pdf",
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@router.post("/send-report")
def send_report(payload: SendReportRequest) -> dict:
    """
    Send a PDF report to the specified recipient via Gmail SMTP.

    Requires EMAIL_SENDER and EMAIL_PASSWORD environment variables to be set.
    The attachment_path must point to an existing PDF file on the server.
    """
    if not os.path.isfile(payload.attachment_path):
        raise HTTPException(
            status_code=404,
            detail=f"Report file not found: '{payload.attachment_path}'. "
                   "Generate a report first via POST /data/upload-data.",
        )

    try:
        send_report_email(
            recipient=payload.recipient,
            subject=payload.subject,
            body=payload.body,
            attachment_path=payload.attachment_path,
        )
        return {
            "status": "sent",
            "recipient": payload.recipient,
            "attachment": payload.attachment_path,
        }

    except EnvironmentError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {exc}") from exc
