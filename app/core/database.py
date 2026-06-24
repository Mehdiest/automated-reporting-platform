"""
Database Configuration
=======================
Sets up a SQLite database using SQLAlchemy.
Creates the engine, session factory, and base model class
used across all ORM models in the application.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from typing import Generator

# SQLite file stored in the project root
_DATABASE_URL = "sqlite:///./reporting_platform.db"

engine = create_engine(
    _DATABASE_URL,
    connect_args={"check_same_thread": False},  # Required for SQLite with FastAPI
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session per request.
    Ensures the session is always closed after the request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Create all database tables defined in ORM models.
    Called once at application startup.
    """
    from app.models.user import User  # noqa: F401 — registers model with Base
    Base.metadata.create_all(bind=engine)
