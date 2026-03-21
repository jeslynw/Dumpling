from pydantic import BaseModel
from typing import List

class RAGChatRequest(BaseModel):
    query: str
    top_k: int = 5

class RAGChatResponse(BaseModel):
    query: str
    context: List[str]