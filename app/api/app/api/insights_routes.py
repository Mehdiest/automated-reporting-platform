"""
AI Insights Routes
==================
Generate natural-language insights from an uploaded dataset.

Requires authentication. The caller's organization must be on a plan that
includes AI insights, and within its monthly AI-insight quota.

POST /insights/generate — Upload a CSV/Excel file and receive KPIs + insights
"""

import os
import tempfile

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.organization import Organization
from app.services.kpi_engine import calculate_kpis
from app.services.ai_insights import generate_insights
from app.services.subscription_service import (
    get_plan, check_quota, record_usage, QuotaExceededError,
)

router = APIRouter(prefix="/insights", tags=["AI Insights"])

_SUPPORTED = {"csv", "xlsx"}


@router.post("/generate")
async def generate(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Compute KPIs for an uploaded dataset and generate AI insights."""
    # --- Tenant & plan gating ---
    if not current_user.organization_id:
        raise HTTPException(
            status_code=400,
            detail="Join or create an organization first (POST /saas/organizations).",
        )
    org = db.get(Organization, current_user.organization_id)
    plan = get_plan(org.plan)

    if not plan["ai_insights"]:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"AI insights are not included in the {plan['name']} plan. Upgrade to Pro or Enterprise.",
        )
    try:
        quota = check_quota(db, org, event_type="ai_insight")
    except QuotaExceededError as exc:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(exc)) from exc

    # --- Load dataset ---
    ext = (file.filename.rsplit(".", 1)[-1] if "." in file.filename else "").lower()
    if ext not in _SUPPORTED:
        raise HTTPException(status_code=400, detail=f"Unsupported file type '.{ext}'. Use CSV or XLSX.")

    content = await file.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    try:
        df = pd.read_csv(tmp_path) if ext == "csv" else pd.read_excel(tmp_path, engine="openpyxl")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    if df.empty:
        raise HTTPException(status_code=400, detail="Uploaded dataset is empty.")

    # --- KPIs + AI insights ---
    kpis = calculate_kpis(df)
    insights = generate_insights(kpis)

    # --- Record billable usage ---
    record_usage(db, org.id, "ai_insight")

    return {
        "status": "ok",
        "organization": org.name,
        "plan": org.plan,
        "quota": {"used": quota["used"] + 1, "limit": quota["limit"]},
        "rows": len(df),
        "kpis": kpis,
        "insights": insights,
    }
