from app.tools.tools_ragchatbot import load_folder_registry, pick_relevant_folders
from app.services.qdrant import search_qdrant_with_sources, get_existing_collections
from app.services.openai import openai_llm
from app.core.config import RAG_TOP_K_EVAL, TAVILY_API_KEY


def _grade_chunks(question: str, results: list[dict]) -> bool:
    """
    True if any top chunks are relevant to the user question.
    Matches notebook CRAG behavior in simplified backend form.
    """
    if not results:
        return False

    for item in results[:3]:
        chunk = (item.get("text") or "")[:500]
        prompt = (
            "You are a grader assessing whether a retrieved document chunk is relevant to the user's question.\n"
            "Return ONLY JSON: {\"relevant\": true or false, \"reason\": \"brief reason\"}.\n"
            "Be lenient: mark relevant if the chunk has ANY useful signal.\n\n"
            f"Question: {question}\n\nChunk:\n{chunk}"
        )
        try:
            resp = openai_llm.invoke(prompt)
            text = (resp.content or "").strip().lower()
            if '"relevant": true' in text or "'relevant': true" in text:
                return True
            if '"relevant": false' in text or "'relevant': false" in text:
                continue
            # If model deviates from strict JSON, keep behavior lenient.
            if "yes" in text or "relevant" in text:
                return True
        except Exception:
            # Keep notebook's lenient default-on-error behavior.
            return True

    return False


def _broaden_query(question: str) -> str:
    prompt = (
        "The following search query failed to find relevant results. "
        "Rewrite it as a broader, more general question that might find related information. "
        "Return ONLY the rewritten question, nothing else.\n\n"
        f"Original question: {question}"
    )
    resp = openai_llm.invoke(prompt)
    broader = (resp.content or "").strip()
    return broader or question


def _retrieve_across_folders(query: str, folders: list[str], top_k: int) -> list[dict]:
    all_results = []
    for folder in folders:
        all_results.extend(search_qdrant_with_sources(query, top_k=top_k, collection_name=folder))
    return all_results[:top_k]


def _tavily_search(question: str) -> list[dict]:
    if not TAVILY_API_KEY:
        return []
    try:
        import importlib

        tavily_mod = importlib.import_module("langchain_community.tools.tavily_search")
        TavilySearchResults = getattr(tavily_mod, "TavilySearchResults")

        tavily = TavilySearchResults(max_results=3, tavily_api_key=TAVILY_API_KEY)
        results = tavily.invoke(question)

        web_docs = []
        for r in results:
            content = f"[WEB SEARCH RESULT: not from your notebook]\n{r.get('content', '')}"
            web_docs.append(
                {
                    "text": content,
                    "source": r.get("url", "web"),
                    "collection": "web_search",
                }
            )
        return web_docs
    except Exception:
        return []

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

    # CRAG step 1: initial retrieval
    limited = _retrieve_across_folders(query, relevant_folders, top_k)

    # CRAG backup 1: broaden query and retry
    if not _grade_chunks(query, limited):
        broader = _broaden_query(query)
        limited = _retrieve_across_folders(broader, relevant_folders, top_k)

        # CRAG backup 2: larger k retrieval
        if not _grade_chunks(query, limited):
            larger_k = max(top_k * 3, RAG_TOP_K_EVAL)
            limited = _retrieve_across_folders(broader, relevant_folders, larger_k)
            limited = limited[:top_k]

            # CRAG backup 3: Tavily web fallback
            if not _grade_chunks(query, limited):
                web = _tavily_search(query)
                if web:
                    limited = web

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