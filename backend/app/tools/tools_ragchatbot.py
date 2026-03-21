import json
from pathlib import Path
from app.services.openai import openai_llm
from app.services.qdrant import sanitize_name, search_hybrid_qdrant_with_sources

def load_folder_registry(meta_path: str = "backend/data/qdrant_db/meta.json") -> dict:
    meta_file = Path(meta_path)
    if not meta_file.exists():
        return {}

    with open(meta_file, "r") as f:
        payload = json.load(f)

    # Preferred schema used by milestone 3+: {"folders": {"name": {"description": "..."}}}
    folders = payload.get("folders")
    if folders is None:
        # Backward-compatible schema from Qdrant local metadata: {"collections": {...}}
        collections = payload.get("collections", {})
        if isinstance(collections, dict):
            return {name: {"description": ""} for name in collections.keys()}
        return {}

    if isinstance(folders, list):
        # Backward-compatible migration from legacy list format.
        return {name: {"description": ""} for name in folders}
    if isinstance(folders, dict):
        return folders
    return {}

def pick_relevant_folders(query: str, folder_registry: dict) -> list[str]:
    """
    Use LLM to select relevant folders for the query, based on descriptions.
    """
    prompt = (
        "Given the following user query and folder descriptions, "
        "list the folders most relevant to answer the query.\n\n"
        f"Query: {query}\n\n"
        "Folders:\n"
    )
    for name, meta in folder_registry.items():
        prompt += f"- {name}: {meta.get('description', '')}\n"
    prompt += "\nReturn a comma-separated list of folder names."

    resp = openai_llm.invoke(prompt)
    return [sanitize_name(f.strip()) for f in resp.content.split(",") if f.strip()]


def search_folder(query: str, folder_name: str, top_k: int = 5) -> list[dict]:
    """
    Search a single folder collection using hybrid retrieval.
    """
    return search_hybrid_qdrant_with_sources(
        query=query,
        top_k=top_k,
        collection_name=sanitize_name(folder_name),
    )


def search_source(query: str, folder_name: str, source: str, top_k: int = 5) -> list[dict]:
    """
    Search a single source/file within a folder by filtering on file_id metadata.
    """
    return search_hybrid_qdrant_with_sources(
        query=query,
        top_k=top_k,
        collection_name=sanitize_name(folder_name),
        file_id=source,
    )