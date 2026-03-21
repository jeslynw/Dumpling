from pydantic import BaseModel
from typing import List

class RAGChatRequest(BaseModel):
    query: str
    top_k: int = 5


class SourceItem(BaseModel):
    source: str
    collection: str


class RAGChatResponse(BaseModel):
    answer: str
    sources: List[SourceItem]