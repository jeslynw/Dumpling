# ...existing imports...
from typing import Tuple
import json
import re
from pathlib import Path
from app.core.json_utils import parse_json_response
from app.services.qdrant import qdrant, sanitize_name
from app.services.openai import openai_llm


def _sanitize_folder_name(name: str) -> str:
    clean = re.sub(r"[^a-z0-9_]", "_", (name or "").strip().lower()).strip("_")
    parts = [p for p in clean.split("_") if p]
    # Keep new folder names concise like notebook guidance.
    return "_".join(parts[:2]) if parts else "general"

#checked
def _load_registry(meta_path: str = "backend/data/qdrant_db/meta.json") -> dict:
    meta_file = Path(meta_path)
    if not meta_file.exists():
        return {}

    with open(meta_file, "r") as f:
        payload = json.load(f)

    folders = payload.get("folders")
    if isinstance(folders, dict):
        return folders

    # Compatibility with Qdrant local metadata format used in this project.
    collections = payload.get("collections", {})
    if isinstance(collections, dict):
        return {name: {"description": ""} for name in collections.keys()}

    if isinstance(folders, list):
        return {name: {"description": ""} for name in folders}

    return {}

def suggest_folder(content: str, meta: dict) -> dict:
    safe_content = (content or "")[:2500]
    meta = meta or {}
    title = (meta.get("title") or "").strip()
    summary = (meta.get("summary") or "").strip()

    registry = _load_registry()
    if not registry:
        folder_info = "No folders exist yet."
    else:
        folder_info = "\n".join(
            f"- {name}: {(data or {}).get('description', '')}"
            for name, data in registry.items()
        )

    preview = f"Title: {title}\nSummary: {summary}\nContent Preview: {safe_content}"

    def _run_once(exclude_folder: str = "") -> dict:
        prompt = _build_folder_prompt(preview, folder_info, exclude_folder=exclude_folder)
        response = openai_llm.invoke(prompt)
        parsed = parse_json_response(response.content or "")
        folder_name = _sanitize_folder_name(parsed.get("folder_name", "general"))
        confidence = float(parsed.get("confidence", 0.5))
        confidence = max(0.0, min(1.0, confidence))
        is_new_folder = bool(parsed.get("is_new_folder", False))
        reason = str(parsed.get("reason", "")).strip() or "No reason provided."
        return {
            "folder_name": folder_name,
            "is_new_folder": is_new_folder,
            "confidence": confidence,
            "reason": reason,
        }

    # First suggestion
    result = _run_once()

    # Notebook-like verify/retry: high confidence existing folder -> sample check -> optional retry
    if result["confidence"] > 0.7 and not result["is_new_folder"]:
        sample = _sample_folder_contents(result["folder_name"])
        if sample:
            verify_prompt = (
                "Given CONTENT and FOLDER SAMPLE, answer ONLY YES or NO if this folder is a good fit.\n\n"
                f"CONTENT:\n{preview}\n\n"
                f"FOLDER SAMPLE:\n{sample}"
            )
            verify = (openai_llm.invoke(verify_prompt).content or "").strip().upper()
            if verify.startswith("N"):
                retry = _run_once(exclude_folder=result["folder_name"])
                if retry["confidence"] >= result["confidence"]:
                    result = retry

    return result


def find_or_suggest_folder(content: str, title: str = "", summary: str = "") -> dict:
    """Notebook tool: find existing folder or suggest a new one."""
    return suggest_folder(content, {"title": title, "summary": summary})


def get_folder_contents_sample(folder_name: str, limit: int = 3) -> str:
    """Notebook tool: fetch a small sample of chunks from a folder."""
    return _sample_folder_contents(folder_name, limit=limit)


def update_folder_registry(
    folder_name: str,
    title: str = "",
    summary: str = "",
    source: str = "",
    is_new_folder: bool = False,
    meta_path: str = "backend/data/qdrant_db/meta.json",
):
    """Update folder metadata used by folder selection prompts."""
    meta_file = Path(meta_path)
    data = {}
    if meta_file.exists():
        with open(meta_file, "r") as f:
            data = json.load(f)

    folders = data.get("folders", {})
    if isinstance(folders, list):
        folders = {name: {"description": "", "sources": []} for name in folders}
    if not isinstance(folders, dict):
        folders = {}

    safe_summary = (summary or "")[:1200]
    safe_title = (title or "").strip()
    seed_text = (f"{safe_title}\n{safe_summary}").strip() or folder_name

    if is_new_folder or folder_name not in folders:
        desc_prompt = (
            f"Write a concise 2-sentence folder description for '{folder_name}' "
            f"based on this content:\n{seed_text}"
        )
        description = (openai_llm.invoke(desc_prompt).content or "").strip()
        folders[folder_name] = {
            "description": description,
            "sources": [source] if source else [],
        }
    else:
        existing_desc = (folders[folder_name].get("description") or "").strip()
        update_prompt = (
            "Update this folder description to include new content.\n"
            f"Current description: {existing_desc}\n"
            f"New content: {seed_text}\n"
            "Return ONLY updated 2-sentence description."
        )
        folders[folder_name]["description"] = (openai_llm.invoke(update_prompt).content or "").strip()
        srcs = folders[folder_name].get("sources", [])
        if not isinstance(srcs, list):
            srcs = []
        if source and source not in srcs:
            srcs.append(source)
        folders[folder_name]["sources"] = srcs

    data["folders"] = folders
    with open(meta_file, "w") as f:
        json.dump(data, f, indent=2)


def _build_folder_prompt(content_preview: str, folder_info: str, exclude_folder: str = "") -> str:
    exclude_note = (
        f"\nDo NOT use folder '{exclude_folder}' - it was checked and does not fit."
        if exclude_folder else ""
    )
    return (
        "You are organizing a personal notebook. Decide where this item belongs.\n"
        "IMPORTANT: related topics must go into the same folder family.\n\n"
        f"ITEM:\n{content_preview}\n\n"
        f"EXISTING FOLDERS:\n{folder_info}{exclude_note}\n\n"
        "RULES:\n"
        "1. Group by TOPIC or SUBJECT MATTER (not by file format).\n"
        "2. DO NOT use generic names like weblinks, urls, images, pictures, misc.\n"
        "3. Match primarily on description, secondarily on title.\n"
        "4. Avoid near-duplicate folders.\n"
        "5. Only suggest a new folder if nothing existing scores >= 0.5.\n"
        "6. New names must be lowercase alphanumeric with underscores only.\n"
        "7. Prefer broadening an existing folder over creating a near-duplicate.\n"
        "8. New folder names must be maximum 2 words and must not use prefixes content_, data_, file_, info_.\n\n"
        "CONFIDENCE GUIDE:\n"
        "0.9-1.0 = clearly_fits\n"
        "0.7-0.9 = good_match\n"
        "0.5-0.7 = uncertain\n"
        "< 0.5 = suggest_new\n\n"
        "Return ONLY JSON:\n"
        "{\"folder_name\":\"finance\",\"is_new_folder\":false,\"confidence\":0.82,\"reason\":\"...\"}"
    )

#checked
def _sample_folder_contents(folder_name: str, limit: int = 3) -> str:
    safe = sanitize_name(folder_name)
    if not qdrant.collection_exists(safe):
        return ""
    results, _ = qdrant.scroll(
        collection_name=safe,
        limit=limit,
        with_payload=True,
    )
    snippets = []
    for point in results:
        payload = point.payload or {}
        text = payload.get("page_content", "")[:200]
        if text:
            snippets.append(text)
    return "\n".join(snippets)