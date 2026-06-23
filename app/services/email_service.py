"""
Email Service
=============
Handles outbound email delivery via Mailtrap SMTP (TLS on port 587).
Supports plain-text body and an optional PDF attachment.

Environment variables required (set in .env — never commit this file):
    EMAIL_SENDER    — Sender address (e.g. hello@demomailtrap.co)
    EMAIL_PASSWORD  — Mailtrap API token
"""

import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# SMTP configuration — Mailtrap
# ---------------------------------------------------------------------------
_SMTP_HOST = "live.smtp.mailtrap.io"
_SMTP_PORT = 587
_SMTP_USERNAME = "api"


def _get_credentials() -> tuple[str, str]:
    """
    Read sender address and Mailtrap API token from environment variables.

    Returns:
        Tuple of (sender_email, api_token).

    Raises:
        EnvironmentError: If either variable is missing.
    """
    sender = os.getenv("EMAIL_SENDER", "").strip()
    token = os.getenv("EMAIL_PASSWORD", "").strip()

    if not sender or not token:
        raise EnvironmentError(
            "EMAIL_SENDER and EMAIL_PASSWORD must be set as environment variables."
        )
    return sender, token


def send_report_email(
    recipient: str,
    subject: str,
    body: str,
    attachment_path: Optional[str] = None,
) -> None:
    """
    Send an email via Mailtrap SMTP, optionally attaching a PDF report.

    Args:
        recipient:       Destination email address.
        subject:         Email subject line.
        body:            Plain-text email body.
        attachment_path: Path to a PDF file to attach.
                         If None or file does not exist, email is sent without attachment.

    Raises:
        EnvironmentError: If Mailtrap credentials are not configured.
        ValueError: If the recipient address is invalid.
        smtplib.SMTPException: If the SMTP session fails.
    """
    if not recipient or "@" not in recipient:
        raise ValueError(f"Invalid recipient address: '{recipient}'")

    sender, token = _get_credentials()

    # --- Build message ---
    message = MIMEMultipart()
    message["From"] = sender
    message["To"] = recipient
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    # --- Attach PDF if provided and valid ---
    if attachment_path:
        if not os.path.isfile(attachment_path):
            logger.warning("Attachment not found, skipping: %s", attachment_path)
        else:
            filename = os.path.basename(attachment_path)
            with open(attachment_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())

            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f'attachment; filename="{filename}"')
            message.attach(part)
            logger.info("Attached file: %s", filename)

    # --- Send via Mailtrap SMTP ---
    try:
        with smtplib.SMTP(_SMTP_HOST, _SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(_SMTP_USERNAME, token)
            server.sendmail(sender, recipient, message.as_string())

        logger.info("Email sent to %s | Subject: %s", recipient, subject)

    except smtplib.SMTPAuthenticationError as exc:
        raise smtplib.SMTPAuthenticationError(
            exc.smtp_code,
            "Mailtrap authentication failed. Check your API token in .env.",
        ) from exc
