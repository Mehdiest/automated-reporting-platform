from fastapi import APIRouter, UploadFile, File
import pandas as pd
from io import BytesIO, StringIO
from app.services.kpi_engine import calculate_kpis

router = APIRouter()


@router.post("/upload-data")
async def upload_data(file: UploadFile = File(...)):

    try:
        content = await file.read()
        filename = file.filename.lower()

        # -------------------------
        # CSV
        # -------------------------
        if filename.endswith(".csv"):
            decoded = content.decode("utf-8", errors="ignore")
            df = pd.read_csv(StringIO(decoded))

        # -------------------------
        # Excel
        # -------------------------
        elif filename.endswith(".xlsx"):
            df = pd.read_excel(BytesIO(content), engine="openpyxl")

        else:
            return {
                "status": "error",
                "detail": "unsupported_file_type"
            }

        if df.empty:
            return {
                "status": "error",
                "detail": "empty_dataset"
            }

        kpis = calculate_kpis(df)

        return {
            "status": "success",
            "rows": len(df),
            "columns": list(df.columns),
            "kpis": kpis
        }

    except Exception as e:
        return {
            "status": "error",
            "detail": str(e)
        }