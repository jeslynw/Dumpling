"""
Ingest Router
POST /ingest -> text/URL/filepath content
POST /ingest/upload -> multipart upload (prototype: saves temp file path then ingests)
"""
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from app.agents.agent_ingestion import run_ingestion_agent
from app.services.qdrant import add_documents
from app.core.config import CATEGORIZER_CONFIDENCE_THRESHOLD

router = APIRouter(prefix="/ingest", tags=["ingest"])

# In-memory pending queue for approval flow.
# This keeps docs out of Qdrant until user approves.
PENDING_INGESTIONS = {}


class IngestRequest(BaseModel):
    content: str
    filename: Optional[str] = ""
    store_to_qdrant: bool = False
    folder_name: Optional[str] = None


class ConfirmIngestRequest(BaseModel):
    pending_id: str
    approved: bool
    folder_name: Optional[str] = None


def _requires_confirmation(categorization: dict) -> bool:
    return bool(
        categorization.get("needs_confirmation", False)
        or categorization.get("verification_required", False)
        or categorization.get("action") in {"ask_user_confirmation", "verify_existing_folder"}
    )


def _create_pending_item(docs, title: str, summary: str, categorization: dict, suggested_folder: str, source_name: str = "") -> str:
    pending_id = str(uuid4())
    PENDING_INGESTIONS[pending_id] = {
        "docs": docs,
        "title": title,
        "summary": summary,
        "categorization": categorization,
        "suggested_folder": suggested_folder,
        "source_name": source_name,
    }
    return pending_id


@router.get("/ping")
def ping_ingest():
    return {"ok": True, "module": "ingest"}


@router.post("")
def ingest(payload: IngestRequest):
    try:
        docs, title, summary, categorization = run_ingestion_agent(
            raw_content=payload.content,
            filename=payload.filename or "",
        )
        suggested_folder = categorization.get("folder_name", "")
        confidence = float(categorization.get("confidence", 0.0))

        explicit_folder = (payload.folder_name or "").strip()
        target_folder = explicit_folder or suggested_folder or "inbox"
        stored = False
        pending_id = None
        requires_confirmation = _requires_confirmation(categorization)

        if payload.store_to_qdrant and docs:
            # If user explicitly chooses folder, treat it as approval.
            if explicit_folder or not requires_confirmation:
                add_documents(target_folder, docs)
                stored = True
            else:
                pending_id = _create_pending_item(
                    docs=docs,
                    title=title,
                    summary=summary,
                    categorization=categorization,
                    suggested_folder=suggested_folder,
                    source_name=payload.filename or payload.content[:120],
                )

        return {
            "ok": True,
            "title": title,
            "summary": summary,
            "suggested_folder": suggested_folder,
            "confidence": confidence,
            "needs_user_confirmation": bool(categorization.get("needs_confirmation", confidence <= CATEGORIZER_CONFIDENCE_THRESHOLD)),
            "confidence_band": categorization.get("confidence_band", "uncertain"),
            "verification_required": bool(categorization.get("verification_required", False)),
            "action": categorization.get("action", "ask_user_confirmation"),
            "is_new_folder": bool(categorization.get("is_new_folder", False)),
            "reason": categorization.get("reason", ""),
            "chunk_count": len(docs),
            "input_filename": payload.filename or "",
            "sample_metadata": docs[0].metadata if docs else {},
            "stored_to_qdrant": stored,
            "folder_name": target_folder,
            "pending_approval": bool(pending_id),
            "pending_id": pending_id,
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

        docs, title, summary, categorization = run_ingestion_agent(
            raw_content=temp_path,
            filename=file.filename or "",
        )
        suggested_folder = categorization.get("folder_name", "")
        confidence = float(categorization.get("confidence", 0.0))

        explicit_folder = (folder_name or "").strip()
        target_folder = explicit_folder or suggested_folder or "inbox"
        stored = False
        pending_id = None
        requires_confirmation = _requires_confirmation(categorization)

        if store_to_qdrant and docs:
            if explicit_folder or not requires_confirmation:
                add_documents(target_folder, docs)
                stored = True
            else:
                pending_id = _create_pending_item(
                    docs=docs,
                    title=title,
                    summary=summary,
                    categorization=categorization,
                    suggested_folder=suggested_folder,
                    source_name=file.filename or temp_path,
                )

        return {
            "ok": True,
            "note_id": note_id,
            "filename": file.filename,
            "title": title,
            "summary": summary,
            "suggested_folder": suggested_folder,
            "confidence": confidence,
            "needs_user_confirmation": bool(categorization.get("needs_confirmation", confidence <= CATEGORIZER_CONFIDENCE_THRESHOLD)),
            "confidence_band": categorization.get("confidence_band", "uncertain"),
            "verification_required": bool(categorization.get("verification_required", False)),
            "action": categorization.get("action", "ask_user_confirmation"),
            "is_new_folder": bool(categorization.get("is_new_folder", False)),
            "reason": categorization.get("reason", ""),
            "chunk_count": len(docs),
            "sample_metadata": docs[0].metadata if docs else {},
            "stored_to_qdrant": stored,
            "folder_name": target_folder,
            "pending_approval": bool(pending_id),
            "pending_id": pending_id,
            "temp_path": temp_path,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Upload ingestion failed: {e}")


@router.post("/confirm")
def confirm_ingest(payload: ConfirmIngestRequest):
    item = PENDING_INGESTIONS.get(payload.pending_id)
    if not item:
        raise HTTPException(status_code=404, detail="Pending ingestion item not found.")

    if not payload.approved:
        PENDING_INGESTIONS.pop(payload.pending_id, None)
        return {
            "ok": True,
            "approved": False,
            "stored_to_qdrant": False,
            "message": "Ingestion rejected by user. Nothing stored.",
        }

    suggested = item.get("suggested_folder", "")
    target_folder = (payload.folder_name or "").strip() or suggested or "inbox"
    docs = item.get("docs", [])

    if docs:
        add_documents(target_folder, docs)

    PENDING_INGESTIONS.pop(payload.pending_id, None)
    return {
        "ok": True,
        "approved": True,
        "stored_to_qdrant": bool(docs),
        "folder_name": target_folder,
        "title": item.get("title", ""),
        "summary": item.get("summary", ""),
    }