"""
Chat Router
POST /chat

The agent_ragchatbot reasons about scope internally based on what's provided.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.agents.agent_ragchatbot import query

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    result = query(
        question=payload.question,
        folder_id=payload.folder_id,    # None if not selected
        file_id=payload.file_id,        # None if not selected
    )
    return ChatResponse(answer=result["answer"], sources=result["sources"])