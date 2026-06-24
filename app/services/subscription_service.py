"""
Subscription Service
=====================
Defines SaaS subscription plans and enforces per-organization monthly
quotas. Usage is accounted by counting UsageRecord rows in the current
calendar month.
"""

import logging
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.organization import Organization, UsageRecord

logger = logging.getLogger(__name__)


class QuotaExceededError(Exception):
    """Raised when an organization exceeds its plan's monthly quota."""


class FeatureNotAvailableError(Exception):
    """Raised when a plan does not include a requested feature."""


# ---------------------------------------------------------------------------
# Plan catalogue
# ---------------------------------------------------------------------------
PLANS = {
    "free": {
        "name": "Free",
        "max_reports_per_month": 5,
        "max_datasets_per_report": 2,
        "ai_insights": False,
        "max_ai_insights_per_month": 0,
    },
    "pro": {
        "name": "Pro",
        "max_reports_per_month": 100,
        "max_datasets_per_report": 10,
        "ai_insights": True,
        "max_ai_insights_per_month": 50,
    },
    "enterprise": {
        "name": "Enterprise",
        "max_reports_per_month": None,        # unlimited
        "max_datasets_per_report": None,      # unlimited
        "ai_insights": True,
        "max_ai_insights_per_month": None,    # unlimited
    },
}


def get_plan(plan_name: str) -> dict:
    """Return the plan definition, defaulting to 'free' for unknown names."""
    return PLANS.get(plan_name, PLANS["free"])


def _current_period_start() -> datetime:
    """First moment of the current calendar month (UTC)."""
    now = datetime.utcnow()
    return datetime(now.year, now.month, 1)


def get_usage_count(db: Session, organization_id: int, event_type: str) -> int:
    """Count billable events of a given type for the current month."""
    return (
        db.query(UsageRecord)
        .filter(
            UsageRecord.organization_id == organization_id,
            UsageRecord.event_type == event_type,
            UsageRecord.created_at >= _current_period_start(),
        )
        .count()
    )


def record_usage(db: Session, organization_id: int, event_type: str) -> None:
    """Log a billable event for quota accounting."""
    db.add(UsageRecord(organization_id=organization_id, event_type=event_type))
    db.commit()


def _limit_for(plan: dict, event_type: str) -> Optional[int]:
    if event_type == "ai_insight":
        return plan["max_ai_insights_per_month"]
    return plan["max_reports_per_month"]


def check_quota(db: Session, org: Organization, event_type: str = "report_generated") -> dict:
    """
    Verify the organization is within its monthly quota for an event type.

    Raises:
        QuotaExceededError: if the limit has been reached.

    Returns:
        Dict with used/limit/remaining for the event type.
    """
    plan = get_plan(org.plan)
    limit = _limit_for(plan, event_type)
    used = get_usage_count(db, org.id, event_type)

    if limit is not None and used >= limit:
        raise QuotaExceededError(
            f"Monthly quota reached for '{event_type}' on the {plan['name']} plan "
            f"({used}/{limit}). Upgrade your plan to continue."
        )

    return {
        "used": used,
        "limit": limit,
        "remaining": None if limit is None else max(limit - used, 0),
    }


def usage_summary(db: Session, org: Organization) -> dict:
    """Return a full usage-vs-limit snapshot for the organization."""
    plan = get_plan(org.plan)
    return {
        "plan": org.plan,
        "plan_details": plan,
        "usage": {
            "reports": {
                "used": get_usage_count(db, org.id, "report_generated"),
                "limit": plan["max_reports_per_month"],
            },
            "ai_insights": {
                "used": get_usage_count(db, org.id, "ai_insight"),
                "limit": plan["max_ai_insights_per_month"],
            },
        },
    }
