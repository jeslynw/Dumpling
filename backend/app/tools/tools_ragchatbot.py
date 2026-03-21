"""
Factory function that returns the 3 RAG-chatbot tools.
Called fresh per query so the registry is always up to date.
"""
import json

from langchain.tools import tool
from langchain_core.documents import Document

from app.core.constants import RAG_TOP_K
from app.db.database import load_registry
from app.services.openai import llm
from app.services.qdrant import (
    get_hybrid_retriever,
    retrieve_with_crag,
    sanitize_name,
    qdrant,
)
from app.db.database import load_registry


def make_chatbot_tools():
    """
    Create the 3 tools for the RAG chatbot agent.
    Returns a list: [pick_relevant_folders, search_folder, search_source]
    """

    @tool
    def pick_relevant_folders(query: str) -> str:
        """
        ALWAYS call this first before searching.
        Reads the folder registry and picks which folders are relevant to the user's query.
        Returns the full registry entries (description + sources) for relevant folders.
        """
        registry = load_registry()
        if not registry:
            return "No folders in registry yet."

        folder_info = "\n".join([
            f"- {name}: {data['description']} "
            f"(sources: {', '.join(data['sources'][:3])}"
            f"{'...' if len(data['sources']) > 3 else ''})"
            for name, data in registry.items()
        ])

        prompt = (
            f"Given this user query: '{query}'\n\n"
            "Match folders based primarily on the DESCRIPTION, not the folder name.\n"
            f"Available folders:\n{folder_info}\n\n"
            'Return ONLY a JSON array of relevant folder names. Example: ["wildlife_ducks", "tokyo_travel"]'
        )

        response = llm.invoke(prompt)
        raw_text = response.content.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        try:
            import json as _json
            relevant = _json.loads(raw_text)
        except Exception:
            relevant = list(registry.keys())

        if not isinstance(relevant, list):
            relevant = list(registry.keys())

        result = {name: registry[name] for name in relevant if name in registry}
        return json.dumps(result, indent=2)

    @tool
    def search_folder(query: str, folder_name: str) -> str:
        """
        Search within a specific folder using Hybrid RAG + CRAG.
        Call this after pick_relevant_folders for each relevant folder.
        Only call this if pick_relevant_folders returned a non-empty list.
        """
        if not qdrant.collection_exists(sanitize_name(folder_name)):
            return f"Folder '{folder_name}' does not exist."

        retriever = get_hybrid_retriever(folder_name, top_k=RAG_TOP_K)
        docs = retrieve_with_crag(
            query, retriever, label=f"folder:{folder_name}", collection_name=folder_name
        )
        if not docs:
            return f"No relevant information found in folder '{folder_name}'."
        return "\n\n---\n\n".join(d.page_content[:400] for d in docs)

    @tool
    def search_source(query: str, folder_name: str, source: str) -> str:
        """
        Search within a specific source (URL or filename) inside a folder.
        Use this when the user asks about a specific document or source.
        source is the exact string from the registry's sources list.
        """
        if not qdrant.collection_exists(sanitize_name(folder_name)):
            return f"Folder '{folder_name}' does not exist."

        retriever = get_hybrid_retriever(folder_name, top_k=RAG_TOP_K, file_id=source)
        docs = retrieve_with_crag(
            query, retriever,
            label=f"folder:{folder_name}",
            collection_name=folder_name,
            file_id=source,
        )
        if not docs:
            return f"No relevant information found for source '{source}' in folder '{folder_name}'."
        return "\n\n---\n\n".join(d.page_content[:400] for d in docs)

    return [pick_relevant_folders, search_folder, search_source]
