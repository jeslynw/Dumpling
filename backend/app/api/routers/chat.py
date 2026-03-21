"""
Chat Router
POST /chat

The agent_ragchatbot reasons about scope internally based on what's provided.
"""
from fastapi import APIRouter
from app.agents.agent_ragchatbot import run_rag_agent
from app.schemas.chat import RAGChatRequest, RAGChatResponse

router = APIRouter()

@router.post("/chat/rag", response_model=RAGChatResponse)
def chat_rag(request: RAGChatRequest):
    return run_rag_agent(request)

#@router.post("", response_model=ChatResponse)
#def chat(payload: ChatRequest, db: Session = Depends(get_db)):
#    result = query(
#        question=payload.question,
#        folder_id=payload.folder_id,    # None if not selected
#        file_id=payload.file_id,        # None if not selected
#    )
#    return ChatResponse(answer=result["answer"], sources=result["sources"])