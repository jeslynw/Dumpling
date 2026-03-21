"""Internal Pydantic models (not API schemas — see schemas/ for those)."""
from pydantic import BaseModel


class FolderEntry(BaseModel):
    description: str
    sources: list[str]


class CategorizerResult(BaseModel):
    folder_name: str
    is_new_folder: bool
    confidence: float
    needs_confirmation: bool
    source: str = ""


class IngestionResult(BaseModel):
    title: str
    summary: str
    folder: str | None
    chunk_count: int
    needs_confirmation: bool = False
