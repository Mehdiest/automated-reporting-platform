from fastapi import FastAPI

from app.api.routes import router as doc_router
from app.api.data_routes import router as data_router

app = FastAPI(
    title="Automated Reporting Platform",
    version="1.0.0"
)

app.include_router(doc_router)
app.include_router(data_router)