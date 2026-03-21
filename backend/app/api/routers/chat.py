"""
Chat Router
POST /chat

The agent_ragchatbot reasons about scope internally based on what's provided.
"""
from fastapi import APIRouter
from app.agents.agent_ragchatbot import search_rag_across_folders

router = APIRouter()

@router.post("/chat/rag")
def chat_rag(query: str, top_k: int = 5):
    return {"results": search_rag_across_folders(query, top_k)}

#@router.post("", response_model=ChatResponse)
#def chat(payload: ChatRequest, db: Session = Depends(get_db)):
#    result = query(
#        question=payload.question,
#        folder_id=payload.folder_id,    # None if not selected
#        file_id=payload.file_id,        # None if not selected
#    )
#    return ChatResponse(answer=result["answer"], sources=result["sources"])