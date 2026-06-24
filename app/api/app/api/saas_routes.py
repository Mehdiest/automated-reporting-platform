"""
SaaS / Organization Routes
==========================
Multi-tenant account management: create an organization, view the active
subscription plan and usage, and upgrade between plans.

All endpoints require a valid JWT Bearer token.

GET  /saas/plans                 — List available subscription plans
POST /saas/organizations         — Create an organization (caller becomes owner)
GET  /saas/organizations/me      — Current organization, plan, and usage
POST /saas/organizations/upgrade — Change the organization's plan (owner only)
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.organization import Organization
from app.services.subscription_service import PLANS, get_plan, usage_summary

router = APIRouter(prefix="/saas", tags=["SaaS"])


class CreateOrgRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=128, example="Acme Analytics")
    plan: str = Field(default="free", example="free")


class UpgradeRequest(BaseModel):
    plan: str = Field(..., example="pro")


def _require_org(db: Session, user: User) -> Organization:
    if not user.organization_id:
        raise HTTPException(
            status_code=400,
            detail="You are not part of an organization. Create one via POST /saas/organizations.",
        )
    org = db.get(Organization, user.organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found.")
    return org


@router.get("/plans")
def list_plans() -> dict:
    """Return the catalogue of available subscription plans."""
    return {"status": "ok", "plans": PLANS}


@router.post("/organizations", status_code=201)
def create_organization(
    payload: CreateOrgRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Create a new organization and assign the caller as its owner."""
    if current_user.organization_id:
        raise HTTPException(status_code=400, detail="You already belong to an organization.")
    if payload.plan not in PLANS:
        raise HTTPException(status_code=400, detail=f"Unknown plan '{payload.plan}'.")
    if db.query(Organization).filter(Organization.name == payload.name).first():
        raise HTTPException(status_code=400, detail=f"Organization '{payload.name}' already exists.")

    org = Organization(name=payload.name, plan=payload.plan)
    db.add(org)
    db.commit()
    db.refresh(org)

    current_user.organization_id = org.id
    current_user.role = "owner"
    db.commit()

    return {"status": "created", "organization": {"id": org.id, "name": org.name, "plan": org.plan}}


@router.get("/organizations/me")
def my_organization(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Return the caller's organization, its plan, and current usage."""
    org = _require_org(db, current_user)
    return {
        "status": "ok",
        "organization": {"id": org.id, "name": org.name, "role": current_user.role},
        **usage_summary(db, org),
    }


@router.post("/organizations/upgrade")
def upgrade_plan(
    payload: UpgradeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Change the organization's subscription plan (owner only)."""
    org = _require_org(db, current_user)

    if current_user.role != "owner":
        raise HTTPException(status_code=403, detail="Only the organization owner can change the plan.")
    if payload.plan not in PLANS:
        raise HTTPException(status_code=400, detail=f"Unknown plan '{payload.plan}'.")

    previous = org.plan
    org.plan = payload.plan
    db.commit()

    return {
        "status": "upgraded",
        "from": previous,
        "to": org.plan,
        "plan_details": get_plan(org.plan),
    }
