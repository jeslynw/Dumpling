"""
Chat Router
POST /chat

The agent_ragchatbot reasons about scope internally based on what's provided.
"""
from fastapi import APIRouter
from app.agents.agent_ragchatbot import search_rag_across_folders
from app.schemas.chat import RAGChatRequest, RAGChatResponse

router = APIRouter()

@router.post("/chat/rag")
def chat_rag(payload: RAGChatRequest) -> RAGChatResponse:
    result = search_rag_across_folders(payload.query, payload.top_k)
    return RAGChatResponse(**result)

#@router.post("", response_model=ChatResponse)
#def chat(payload: ChatRequest, db: Session = Depends(get_db)):
#    result = query(
#        question=payload.question,
#        folder_id=payload.folder_id,    # None if not selected
#        file_id=payload.file_id,        # None if not selected
#    )
#    return ChatResponse(answer=result["answer"], sources=result["sources"])