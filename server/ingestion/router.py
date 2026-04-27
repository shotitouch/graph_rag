import os
import tempfile

from fastapi import APIRouter, Form, HTTPException, UploadFile, status

from ingestion.service import ingest_pdf
from shared.logging import get_logger

router = APIRouter(prefix="/ingest")
logger = get_logger(__name__)


@router.post("/")
async def ingest_10q_multimodal(
    file: UploadFile,
    mode: str = Form("fast"),
):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDFs are allowed.",
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File extension must be .pdf",
        )

    if mode not in {"fast", "full"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ingest mode. Expected 'fast' or 'full'.",
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        pdf_path = tmp.name

    try:
        return await ingest_pdf(file, pdf_path, mode)
    except Exception as exc:
        logger.exception(
            "event=ingest_failed filename=%s mode=%s error=%s",
            file.filename,
            mode,
            str(exc),
        )
        raise HTTPException(
            status_code=500,
            detail=f"Ingestion failed: {str(exc)}",
        )
    finally:
        if os.path.exists(pdf_path):
            os.unlink(pdf_path)
