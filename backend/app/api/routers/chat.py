"""
Chat Router
POST /chat

The agent_ragchatbot reasons about scope internally based on what's provided.
"""
from fastapi import APIRouter, HTTPException
from app.agents.agent_ragchatbot import query_notebook
from app.schemas.schema import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("", response_model=ChatResponse, summary="Ask the notebook a question")
def chat(body: ChatRequest):
    """
    Runs the RAG chatbot agent:
      1. pick_relevant_folders  → selects relevant Qdrant collections
      2. search_folder / search_source  → Hybrid RAG + CRAG retrieval
      3. LLM synthesises answer, cites sources, flags web-search results

    If no relevant content is found, CRAG falls back to Tavily web search.
    """
    if not body.question.strip():
        raise HTTPException(status_code=422, detail="Question must not be empty.")

    answer = query_notebook(body.question)
    return ChatResponse(answer=answer)