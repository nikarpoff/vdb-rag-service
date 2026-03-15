import asyncio
import uuid
from typing import List

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.core.logger import logger
from app.engine.document_processor import document_processor
from app.engine.weaviate_client import weaviate_client

router = APIRouter(prefix="/documents", tags=["Documents"])

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

documents_db: dict = {}


class DocumentResponse(BaseModel):
    id: str
    filename: str
    content_type: str
    size: int = 0
    embedded: bool = False
    chunks: int = 0


class DocumentDetailResponse(BaseModel):
    id: str
    filename: str
    content: str
    content_type: str
    embedded: bool


def _chunk_text(text: str, chunk_size: int = 800, overlap: int = 120) -> List[str]:
    cleaned = " ".join(text.split())
    if not cleaned:
        return []

    chunks: List[str] = []
    start = 0
    while start < len(cleaned):
        end = min(start + chunk_size, len(cleaned))
        chunks.append(cleaned[start:end])
        if end == len(cleaned):
            break
        start = max(0, end - overlap)

    return chunks


@router.get("", response_model=List[DocumentResponse])
async def list_documents():
    return [
        DocumentResponse(**{k: v for k, v in doc.items() if k != "content"})
        for doc in documents_db.values()
    ]


@router.post("", response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...)):
    content = await file.read()
    size = len(content)

    if size > MAX_FILE_SIZE:
        logger.warning(f"File too large: {file.filename} ({size} bytes)")
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)} MB",
        )

    doc_id = str(uuid.uuid4())

    loop = asyncio.get_event_loop()
    text_content = await loop.run_in_executor(
        None,
        document_processor.process,
        content,
        file.filename or "document.pdf",
    )
    chunks = _chunk_text(text_content)

    doc = DocumentResponse(
        id=doc_id,
        filename=file.filename or "unknown",
        content_type=file.content_type or "application/octet-stream",
        size=size,
        embedded=False,
        chunks=len(chunks),
    )

    documents_db[doc_id] = {
        "id": doc.id,
        "filename": doc.filename,
        "content_type": doc.content_type,
        "size": doc.size,
        "content": text_content,
        "embedded": False,
        "chunks": len(chunks),
    }

    try:
        if chunks:
            weaviate_client.add_document_chunks(
                doc_id=doc_id,
                filename=doc.filename,
                content_type=doc.content_type,
                chunks=chunks,
            )
            documents_db[doc_id]["embedded"] = True
            doc.embedded = True

        logger.info(f"Document indexed: {doc.filename} (id: {doc_id}, chunks: {len(chunks)})")
    except Exception as e:
        logger.error(f"Failed to index document {doc.filename}: {e}")

    return doc


@router.get("/{doc_id}", response_model=DocumentDetailResponse)
async def get_document(doc_id: str):
    doc = documents_db.get(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    return DocumentDetailResponse(
        id=doc["id"],
        filename=doc["filename"],
        content=doc.get("content", ""),
        content_type=doc["content_type"],
        embedded=doc["embedded"],
    )


@router.delete("/{doc_id}")
async def delete_document(doc_id: str):
    if doc_id not in documents_db:
        raise HTTPException(status_code=404, detail="Document not found")

    doc = documents_db.pop(doc_id)

    try:
        weaviate_client.delete_document(doc_id)
        logger.info(f"Document deleted: {doc['filename']} (id: {doc_id})")
    except Exception as e:
        logger.error(f"Failed to delete document from Weaviate: {e}")

    return {"status": "deleted", "id": doc_id}
