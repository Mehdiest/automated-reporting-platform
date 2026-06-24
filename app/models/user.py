"""
User Model
===========
SQLAlchemy ORM model representing a registered user.
Stores hashed passwords only — plaintext is never persisted.
Each user optionally belongs to an Organization (SaaS tenant).
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    """Database table for registered users."""

    __tablename__ = "users"

    id              = Column(Integer, primary_key=True, index=True)
    username        = Column(String(64), unique=True, index=True, nullable=False)
    email           = Column(String(128), unique=True, index=True, nullable=False)
    hashed_password = Column(String(256), nullable=False)
    is_active       = Column(Boolean, default=True, nullable=False)
    created_at      = Column(DateTime, default=datetime.utcnow, nullable=False)

    # --- SaaS multi-tenancy ---
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    role            = Column(String(32), default="member", nullable=False)  # "owner" | "member"

    organization = relationship("Organization", back_populates="users")

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username!r}>"
