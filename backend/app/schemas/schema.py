"""
API schemas (request bodies + response models).
Imported by routers — keep these free of business logic.
"""
from __future__ import annotations

from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────────────────────────
# /ingest
# ─────────────────────────────────────────────────────────────────────────────

class IngestTextRequest(BaseModel):
    """Ingest raw user textbox input (URLs, filenames, plain text mixed together)."""
    raw_input: str = Field(..., description="Raw text from the user's input box")


class IngestItemResult(BaseModel):
    title: str
    summary: str
    folder: str | None
    chunk_count: int
    needs_confirmation: bool


class IngestResponse(BaseModel):
    results: list[IngestItemResult]
    collections: list[str]


class ConfirmFolderRequest(BaseModel):
    """Confirm or rename a folder after low-confidence categorisation."""
    title: str
    summary: str
    source: str
    suggested_folder: str
    confirmed_folder: str = Field(..., description="Accepted name (can equal suggested_folder)")


class ConfirmFolderResponse(BaseModel):
    folder: str
    chunk_count: int


# ─────────────────────────────────────────────────────────────────────────────
# /folders
# ─────────────────────────────────────────────────────────────────────────────

class FolderInfo(BaseModel):
    name: str
    description: str
    sources: list[str]


class FolderListResponse(BaseModel):
    folders: list[FolderInfo]


class FolderDeleteResponse(BaseModel):
    deleted: str
    remaining: list[str]


# ─────────────────────────────────────────────────────────────────────────────
# /chat
# ─────────────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    question: str = Field(..., description="User's question to the notebook")


class ChatResponse(BaseModel):
    answer: str
