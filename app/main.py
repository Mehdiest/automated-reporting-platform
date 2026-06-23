"""
Automated Reporting Platform
=============================
FastAPI application entry point.

Startup:  loads .env variables, initialises the APScheduler background scheduler.
Shutdown: gracefully stops the scheduler to prevent dangling threads.
"""

from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

# Load .env file before anything else so all services can read credentials
load_dotenv()

from app.api.routes import router as document_router
from app.api.data_routes import router as data_router
from app.api.scheduler_routes import router as scheduler_router
from app.api.email_routes import router as email_router
from app.api.multi_dataset_routes import router as multi_dataset_router
from app.services.scheduler import start_scheduler, shutdown_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage startup and shutdown events for long-lived resources."""
    start_scheduler()
    yield
    shutdown_scheduler()


app = FastAPI(
    title="Automated Reporting Platform",
    description="Upload structured data or documents to extract KPIs and generate PDF reports.",
    version="2.0.0",
    lifespan=lifespan,
)

app.include_router(document_router, prefix="/docs", tags=["Documents"])
app.include_router(data_router, prefix="/data", tags=["Data"])
app.include_router(scheduler_router)
app.include_router(email_router)
app.include_router(multi_dataset_router)


@app.get("/health", tags=["System"])
def health_check() -> dict:
    """Liveness check for deployment monitoring."""
    return {"status": "ok", "version": "2.0.0"}
