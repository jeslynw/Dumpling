from app.services.qdrant import search_qdrant

def retrieve_relevant_chunks(query: str, top_k: int = 5):
    """
    Embed the query, search Qdrant, and return the most relevant chunks.
    """
    # This assumes search_qdrant returns a list of chunk texts
    return search_qdrant(query, top_k=top_k)