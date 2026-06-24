"""
User Model
===========
SQLAlchemy ORM model representing a registered user.
Stores hashed passwords only — plaintext is never persisted.
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime

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

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username!r}>"
