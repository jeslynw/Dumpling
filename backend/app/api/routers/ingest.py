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

router = APIRouter(prefix="/ingest", tags=["ingest"])


class IngestRequest(BaseModel):
    content: str
    filename: Optional[str] = ""


@router.get("/ping")
def ping_ingest():
    return {"ok": True, "module": "ingest"}


@router.post("")
def ingest(payload: IngestRequest):
    try:
        docs, title, summary = run_ingestion_agent(
            raw_content=payload.content,
            filename=payload.filename or "",
        )
        return {
            "ok": True,
            "title": title,
            "summary": summary,
            "chunk_count": len(docs),
            "input_filename": payload.filename or "",
            "sample_metadata": docs[0].metadata if docs else {},
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ingestion failed: {e}")


@router.post("/upload")
async def ingest_upload(
    file: UploadFile = File(...),
    note_id: Optional[str] = Form(default=None),
):
    """
    Prototype upload path:
    1) save uploaded bytes to a temp file
    2) run ingestion on that temp filepath
    """
    try:
        suffix = Path(file.filename or "").suffix or ".bin"

        with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            data = await file.read()
            tmp.write(data)
            temp_path = tmp.name

        docs, title, summary = run_ingestion_agent(
            raw_content=temp_path,
            filename=file.filename or "",
        )

        return {
            "ok": True,
            "note_id": note_id,
            "filename": file.filename,
            "title": title,
            "summary": summary,
            "chunk_count": len(docs),
            "sample_metadata": docs[0].metadata if docs else {},
            "temp_path": temp_path,  # keep for prototype visibility
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Upload ingestion failed: {e}")