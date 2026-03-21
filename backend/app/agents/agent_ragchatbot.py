from app.tools.tools_ragchatbot import load_folder_registry, pick_relevant_folders
from app.services.qdrant import search_qdrant_with_sources, get_existing_collections
from app.services.openai import openai_llm

def search_rag_across_folders(query: str, top_k: int = 5) -> dict:
    """
    1. Load folder registry (with descriptions)
    2. Use LLM to pick relevant folders
    3. Search each folder and aggregate results
    """
    folder_registry = load_folder_registry()
    existing = set(get_existing_collections())
    relevant_folders = pick_relevant_folders(query, folder_registry)
    relevant_folders = [f for f in relevant_folders if f in existing]

    # Fallback to all existing collections if LLM returns nothing valid.
    if not relevant_folders:
        relevant_folders = list(existing)

    all_results = []
    for folder in relevant_folders:
        results = search_qdrant_with_sources(query, top_k=top_k, collection_name=folder)
        all_results.extend(results)

    limited = all_results[:top_k]

    if not limited:
        return {
            "answer": "I could not find relevant notes for this query.",
            "sources": [],
        }

    context = "\n\n".join(r.get("text", "") for r in limited)
    prompt = (
        "Answer the user question using only the provided context. "
        "If the context is insufficient, say so briefly.\n\n"
        f"QUESTION:\n{query}\n\n"
        f"CONTEXT:\n{context}"
    )
    response = openai_llm.invoke(prompt)
    answer = (response.content or "").strip()

    sources = [
        {
            "source": r.get("source", "unknown"),
            "collection": r.get("collection", "unknown"),
        }
        for r in limited
    ]

    return {
        "answer": answer,
        "sources": sources,
    }