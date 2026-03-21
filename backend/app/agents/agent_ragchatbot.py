from app.tools.tools_ragchatbot import retrieve_relevant_chunks
from app.schemas.chat import RAGChatRequest, RAGChatResponse

def run_rag_agent(request: RAGChatRequest) -> RAGChatResponse:
    """
    Accepts a user query, retrieves relevant chunks from Qdrant, and returns them.
    """
    context_chunks = retrieve_relevant_chunks(request.query, top_k=request.top_k)
    return RAGChatResponse(
        query=request.query,
        context=context_chunks
    )