from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    question: str
    folder_id: Optional[str] = None     # None = global search across all folders
    file_id: Optional[str] = None       # set when user selects a file from dropdown


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]