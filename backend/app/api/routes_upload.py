import os
import uuid
import logging

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.models.response_models import UploadResponse
from app.rag.document_loader import load_document, chunk_text
from app.rag.vector_store import add_documents
from app.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Upload"])

_ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload a PDF / DOCX / TXT document into the RAG knowledge base."""

    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in _ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format '{ext}'. Allowed: {', '.join(sorted(_ALLOWED_EXTENSIONS))}",
        )

    settings = get_settings()
    os.makedirs(settings.upload_dir, exist_ok=True)

    file_id = uuid.uuid4().hex[:12]
    safe_name = f"{file_id}_{file.filename}"
    file_path = os.path.join(settings.upload_dir, safe_name)

    try:
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        text = load_document(file_path)
        chunks = chunk_text(text, settings.chunk_size, settings.chunk_overlap)

        if not chunks:
            raise HTTPException(status_code=400, detail="No text content could be extracted from the document")

        ids = [f"{file_id}_chunk_{i}" for i in range(len(chunks))]
        metadata = [
            {"source": file.filename, "file_id": file_id, "chunk_index": i}
            for i in range(len(chunks))
        ]

        stored = add_documents(chunks, metadata, ids)
        logger.info("Uploaded %s → %d chunks stored", file.filename, stored)

        return UploadResponse(
            filename=file.filename,
            chunks_stored=stored,
            message=f"Successfully processed and stored {stored} chunks from '{file.filename}'",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Upload processing failed for %s", file.filename)
        raise HTTPException(status_code=500, detail=f"Processing failed: {e}")
