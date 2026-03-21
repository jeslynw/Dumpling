import json
from pathlib import Path
from app.services.openai import openai_llm
from app.services.qdrant import qdrant, sanitize_name, search_hybrid_qdrant_with_sources


def _resolve_meta_file(meta_path: str) -> Path:
    p = Path(meta_path)
    if p.is_absolute():
        return p

    repo_root = Path(__file__).resolve().parents[3]
    backend_root = Path(__file__).resolve().parents[2]

    candidates = [
        Path.cwd() / p,
        repo_root / p,
    ]
    meta_posix = str(p).replace("\\", "/")
    if meta_posix.startswith("backend/"):
        candidates.append(backend_root / meta_posix[len("backend/"):])

    for c in candidates:
        if c.exists():
            return c

    return repo_root / p

def load_folder_registry(meta_path: str = "backend/data/qdrant_db/meta.json") -> dict:
    meta_file = _resolve_meta_file(meta_path)
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
    folder_lines = []
    for name, meta in folder_registry.items():
        folder_lines.append(f"- {name}: {meta.get('description', '')}")
    folder_info = "\n".join(folder_lines)

    prompt = (
        f"Given this user query: '{query}'\n\n"
        "Match folders based primarily on the DESCRIPTION, not the folder name.\n"
        "The folder name is just a technical identifier.\n\n"
        f"Available folders:\n{folder_info}\n\n"
        "Return ONLY a JSON array of relevant folder names. "
        "Example: [\"wildlife_ducks\", \"tokyo_travel\"], except if nothing really matches, "
        "return an empty JSON"
    )

    resp = openai_llm.invoke(prompt)
    text = (resp.content or "").strip()

    # Prefer strict JSON array output as requested by the prompt.
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return [sanitize_name(str(name).strip()) for name in parsed if str(name).strip()]
    except Exception:
        pass

    # Backward-compatible fallback for non-JSON responses.
    return [sanitize_name(f.strip()) for f in text.split(",") if f.strip()]


def search_folder_rows(query: str, folder_name: str, top_k: int = 5) -> list[dict]:
    """
    Structured hybrid retrieval rows for a single folder.
    """
    safe_folder = sanitize_name(folder_name)
    if not qdrant.collection_exists(safe_folder):
        return []

    return search_hybrid_qdrant_with_sources(
        query=query,
        top_k=top_k,
        collection_name=safe_folder,
    )


def search_folder(query: str, folder_name: str, top_k: int = 5) -> str:
    """
    Search within a specific folder using Hybrid RAG + CRAG.
    Call this after pick_relevant_folders for each relevant folder.
    Input: query (user question), folder_name (exact name from pick_relevant_folders).
    Only call this if pick_relevant_folders returned a non-empty list.
    """
    safe_folder = sanitize_name(folder_name)
    if not qdrant.collection_exists(safe_folder):
        return f"Folder '{folder_name}' does not exist."

    docs = search_folder_rows(query=query, folder_name=folder_name, top_k=top_k)
    if not docs:
        return f"No relevant information found in folder '{folder_name}'."

    return "\n\n---\n\n".join((d.get("text") or "")[:400] for d in docs)


def search_source_rows(query: str, folder_name: str, source: str, top_k: int = 5) -> list[dict]:
    """
    Structured hybrid retrieval rows for a single source/file inside a folder.
    """
    safe_folder = sanitize_name(folder_name)
    if not qdrant.collection_exists(safe_folder):
        return []

    return search_hybrid_qdrant_with_sources(
        query=query,
        top_k=top_k,
        collection_name=safe_folder,
        file_id=source,
    )


def search_source(query: str, folder_name: str, source: str, top_k: int = 5) -> str:
    """
    Search a single source/file within a folder by filtering on file_id metadata.
    """
    safe_folder = sanitize_name(folder_name)
    if not qdrant.collection_exists(safe_folder):
        return f"Folder '{folder_name}' does not exist."

    docs = search_source_rows(query=query, folder_name=folder_name, source=source, top_k=top_k)
    if not docs:
        return f"No relevant information found in source '{source}' under folder '{folder_name}'."

    return "\n\n---\n\n".join((d.get("text") or "")[:400] for d in docs)