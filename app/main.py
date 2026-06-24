"""
Automated Reporting Platform
=============================
FastAPI application entry point.

Startup:  loads .env, initialises the database, starts the APScheduler.
Shutdown: gracefully stops the scheduler.
"""

from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

# Load .env before anything else
load_dotenv()

from app.api.routes import router as document_router
from app.api.data_routes import router as data_router
from app.api.scheduler_routes import router as scheduler_router
from app.api.email_routes import router as email_router
from app.api.multi_dataset_routes import router as multi_dataset_router
from app.api.dashboard_routes import router as dashboard_router
from app.api.auth_routes import router as auth_router
from app.core.database import init_db
from app.services.scheduler import start_scheduler, shutdown_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage startup and shutdown events for long-lived resources."""
    init_db()          # Create DB tables if they don't exist
    start_scheduler()
    yield
    shutdown_scheduler()


app = FastAPI(
    title="Automated Reporting Platform",
    description="Upload structured data or documents to extract KPIs and generate PDF reports.",
    version="3.0.0",
    lifespan=lifespan,
)

app.include_router(auth_router)
app.include_router(document_router, prefix="/docs", tags=["Documents"])
app.include_router(data_router, prefix="/data", tags=["Data"])
app.include_router(scheduler_router)
app.include_router(email_router)
app.include_router(multi_dataset_router)
app.include_router(dashboard_router)


@app.get("/health", tags=["System"])
def health_check() -> dict:
    """Liveness check for deployment monitoring."""
    return {"status": "ok", "version": "3.0.0"}
