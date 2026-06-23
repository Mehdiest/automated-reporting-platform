from fastapi import APIRouter, UploadFile, File
from app.services.file_extractor import FileExtractor

router = APIRouter()

ALLOWED_TYPES = ["pdf", "docx", "txt"]

@router.post("/upload-document")
async def upload_document(file: UploadFile = File(...)):

    file_type = file.filename.rsplit(".", 1)[-1].lower()

    if file_type not in ALLOWED_TYPES:
        return {
            "status": "error",
            "detail": "unsupported_file_type"
        }

    text = FileExtractor.extract(file.file, file_type)

    return {
        "status": "success",
        "file_type": file_type,
        "data": {
            "text": text,
            "length": len(text),
            "word_count": len(text.split())
        }
    }