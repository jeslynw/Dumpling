"""
POST /ingest/text   — parse raw textbox input → ingest batch → return results
POST /ingest/file   — upload a single file (multipart) → ingest → return result
POST /ingest/confirm — confirm / rename a folder after low-confidence categorisation
"""
import os
import tempfile

from fastapi import APIRouter, HTTPException, UploadFile, File, Form

from app.db.crud import (
    parse_user_input,
    prepare_input,
    run_ingestion_agent_batch,
)
from app.db.database import update_folder_registry
from app.agents.agent_ingestion import run_ingestion_agent
from app.agents.agent_categorizer import run_categorizer_agent
from app.services.qdrant import add_documents, get_existing_collections, sanitize_name
from app.schemas.schema import (
    IngestTextRequest,
    IngestResponse,
    IngestItemResult,
    ConfirmFolderRequest,
    ConfirmFolderResponse,
)

router = APIRouter(prefix="/ingest", tags=["Ingestion"])


# ── POST /ingest/text ─────────────────────────────────────────────────────────
@router.post("/text", response_model=IngestResponse, summary="Ingest raw text / URLs")
def ingest_text(body: IngestTextRequest):
    """
    Accepts a raw user textbox string (may contain URLs, filenames, plain text).
    The LLM parses it into individual items, then runs the full pipeline:
      parse → ingest → categorize → store → update registry.

    Items that need folder confirmation (confidence < 0.7) are still stored
    in the suggested folder — call POST /ingest/confirm to rename them.
    """
    parsed_items = parse_user_input(body.raw_input)
    prepared = [prepare_input(item) for item in parsed_items]
    batch_results = run_ingestion_agent_batch(prepared)

    results = [
        IngestItemResult(
            title=r["title"],
            summary=r["summary"],
            folder=r["folder"],
            chunk_count=len(r["docs"]),
            needs_confirmation=r.get("needs_confirmation", False),
        )
        for r in batch_results
    ]
    return IngestResponse(results=results, collections=get_existing_collections())


# ── POST /ingest/file ─────────────────────────────────────────────────────────
@router.post("/file", response_model=IngestItemResult, summary="Upload and ingest a single file")
async def ingest_file(file: UploadFile = File(...)):
    """
    Accepts a multipart file upload (PDF, DOCX, PPTX, PNG, JPG, etc.).
    Saves it to a temp path, runs ingestion + categorisation, stores chunks.
    """
    suffix = os.path.splitext(file.filename or "upload")[1]
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        contents = await file.read()
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        filename = file.filename or os.path.basename(tmp_path)
        docs, title, summary = run_ingestion_agent(raw_content=tmp_path, filename=filename)

        if not docs:
            raise HTTPException(status_code=422, detail="No content could be extracted from the file.")

        category = run_categorizer_agent(title=title, summary=summary, source=filename)
        folder_name = category.get("folder_name", "uncategorized")
        is_new = category.get("is_new_folder", False)

        add_documents(folder_name, docs)
        update_folder_registry(folder_name, title, summary, filename, is_new)

        return IngestItemResult(
            title=title,
            summary=summary,
            folder=folder_name,
            chunk_count=len(docs),
            needs_confirmation=category.get("needs_confirmation", False),
        )
    finally:
        os.unlink(tmp_path)


# ── POST /ingest/confirm ──────────────────────────────────────────────────────
@router.post("/confirm", response_model=ConfirmFolderResponse, summary="Confirm or rename a folder")
def confirm_folder(body: ConfirmFolderRequest):
    """
    Called after the frontend shows the user a low-confidence folder suggestion.
    If confirmed_folder differs from suggested_folder, re-categorises and re-stores.

    Note: this endpoint re-runs ingestion for the same source.
    For a simple rename, the frontend can also call PATCH /folders/{name} instead.
    """
    folder_name = sanitize_name(body.confirmed_folder)

    # Re-ingest the source so we have fresh docs
    docs, title, summary = run_ingestion_agent(
        raw_content=body.source,
        filename=body.source if not body.source.startswith("http") else "",
    )

    if not docs:
        raise HTTPException(status_code=422, detail="Re-ingestion returned no content.")

    add_documents(folder_name, docs)
    is_new = folder_name not in get_existing_collections()
    update_folder_registry(folder_name, title, summary, body.source, is_new)

    return ConfirmFolderResponse(folder=folder_name, chunk_count=len(docs))
