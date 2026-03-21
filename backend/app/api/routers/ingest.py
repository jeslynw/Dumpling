"""
Ingest Router
POST /ingest -> text/URL/filepath content
POST /ingest/upload -> multipart upload (prototype: saves temp file path then ingests)
"""
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from app.agents.agent_ingestion import run_ingestion_agent
from app.services.qdrant import add_documents

router = APIRouter(prefix="/ingest", tags=["ingest"])
LOW_CONFIDENCE_THRESHOLD = 0.7


class IngestRequest(BaseModel):
    content: str
    filename: Optional[str] = ""
    store_to_qdrant: bool = False
    folder_name: Optional[str] = None


@router.get("/ping")
def ping_ingest():
    return {"ok": True, "module": "ingest"}


@router.post("")
def ingest(payload: IngestRequest):
    try:
        docs, title, summary, suggested_folder, confidence = run_ingestion_agent(
            raw_content=payload.content,
            filename=payload.filename or "",
        )

        explicit_folder = (payload.folder_name or "").strip()
        target_folder = explicit_folder or suggested_folder or "inbox"
        stored = False
        if payload.store_to_qdrant and docs:
            add_documents(target_folder, docs)
            stored = True

        return {
            "ok": True,
            "title": title,
            "summary": summary,
            "suggested_folder": suggested_folder,
            "confidence": confidence,
            "needs_user_confirmation": confidence < LOW_CONFIDENCE_THRESHOLD,
            "chunk_count": len(docs),
            "input_filename": payload.filename or "",
            "sample_metadata": docs[0].metadata if docs else {},
            "stored_to_qdrant": stored,
            "folder_name": target_folder,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ingestion failed: {e}")


@router.post("/upload")
async def ingest_upload(
    file: UploadFile = File(...),
    note_id: Optional[str] = Form(default=None),
    store_to_qdrant: bool = Form(default=False),
    folder_name: Optional[str] = Form(default=None),
):
    """
    Prototype upload path:
    1) save uploaded bytes to a temp file
    2) run ingestion on that temp filepath
    """
    temp_path = ""
    try:
        suffix = Path(file.filename or "").suffix or ".bin"

        with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            data = await file.read()
            tmp.write(data)
            temp_path = tmp.name

        docs, title, summary, suggested_folder, confidence = run_ingestion_agent(
            raw_content=temp_path,
            filename=file.filename or "",
        )

        explicit_folder = (folder_name or "").strip()
        target_folder = explicit_folder or suggested_folder or "inbox"
        stored = False
        if store_to_qdrant and docs:
            add_documents(target_folder, docs)
            stored = True

        return {
            "ok": True,
            "note_id": note_id,
            "filename": file.filename,
            "title": title,
            "summary": summary,
            "suggested_folder": suggested_folder,
            "confidence": confidence,
            "needs_user_confirmation": confidence < LOW_CONFIDENCE_THRESHOLD,
            "chunk_count": len(docs),
            "sample_metadata": docs[0].metadata if docs else {},
            "stored_to_qdrant": stored,
            "folder_name": target_folder,
            "temp_path": temp_path,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Upload ingestion failed: {e}")