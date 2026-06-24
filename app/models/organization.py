"""
Organization & Usage Models
============================
SaaS multi-tenancy layer. Each Organization represents a tenant on a
subscription plan. Users belong to an organization, and every billable
action is logged as a UsageRecord for monthly quota enforcement.
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class Organization(Base):
    """A tenant account on a subscription plan."""

    __tablename__ = "organizations"

    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String(128), unique=True, index=True, nullable=False)
    plan       = Column(String(32), default="free", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    users = relationship("User", back_populates="organization")

    def __repr__(self) -> str:
        return f"<Organization id={self.id} name={self.name!r} plan={self.plan!r}>"


class UsageRecord(Base):
    """A single billable event used for monthly quota accounting."""

    __tablename__ = "usage_records"

    id              = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), index=True, nullable=False)
    event_type      = Column(String(64), nullable=False)   # "report_generated" | "ai_insight"
    created_at      = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)

    def __repr__(self) -> str:
        return f"<UsageRecord org={self.organization_id} type={self.event_type!r}>"
