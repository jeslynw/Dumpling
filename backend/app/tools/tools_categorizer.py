"""
LangChain tools for the categorizer agent.
Both tools are module-level (not closures) — the categorizer agent has no side-channel state.
"""
import json
import re

from langchain.tools import tool

from app.db.database import load_registry
from app.services.openai import llm
from app.services.qdrant import qdrant, sanitize_name


@tool
def find_or_suggest_folder(content_previews: list[str], exclude_folder: str = "") -> str:
    """
    Decide which folder this content belongs to — existing or new.
    ALWAYS call this first.
    Input: list of content_previews, each as 'Title: X\nSummary: Y'
    - Matches based primarily on folder DESCRIPTION, secondarily on title.
    - Avoids creating near-duplicate folders (e.g. won't create 'duck_pond' if 'wildlife_ducks' exists).
    Returns one line: folder_name | is_new (true/false) | confidence (0.0-1.0) | reason
    """
    registry = load_registry()

    if not registry:
        folder_info = "No folders exist yet."
    else:
        entries = [
            f"- {name}: {data['description']}"
            for name, data in registry.items()
            if name != exclude_folder
        ]
        folder_info = "\n".join(entries) if entries else "No folders exist yet."

    exclude_note = (
        f"\nDo NOT use folder '{exclude_folder}' — it was already verified and does not fit."
        if exclude_folder else ""
    )

    items_text = "\n\n".join(
        f"ITEM {i}:\n{preview}" for i, preview in enumerate(content_previews)
    )

    prompt = f"""You are organizing a personal notebook. Decide where each item belongs.
    IMPORTANT: Items about related topics MUST go in the same folder.

    ITEMS:
    {items_text}

    EXISTING FOLDERS (name: description):
    {folder_info}{exclude_note}

    RULES:
    1. Group items strictly by their TOPIC or SUBJECT MATTER or GEOGRAPHY (e.g., 'ducks', 'tokyo', 'cancer', 'finance').
    2. Related items (e.g. two math images) MUST share the same folder
    3. DO NOT group items by file format. NEVER use generic names like 'weblinks', 'images', 'misc'.
    4. Match based PRIMARILY on description, secondarily on title, partial keyword matches (e.g. "food") are NOT enough. The overall subject must match.
    5. Avoid near-duplicate folders (e.g. don't create "duck_pond" if "wildlife_ducks" exists).
    6. Only suggests a new sanitized folder name if confidence < 0.5.
    7. New folder names: lowercase, alphanumeric + underscores only, max 2 words.
    8. NEVER use prefixes like 'content_', 'data_', 'file_', 'info_'.
    9. ALWAYS prefer broadening an existing folder over creating a near-duplicate. "NEVER create 'mathematics' if 'algebra' already exists — they're the same domain.\n""

    CRITICAL NAMING RULE FOR NEW FOLDERS:
    - Maximum 2 words total. 
    - "NEVER use generic prefixes like 'content_', 'data_', 'file_', 'info_' in folder names.\n"
    - "GOOD: 'llm_training', 'generative_ai', 'bali_travel'\n"
    - "BAD: 'content_training_llms', 'content_creation_ai'\n"

    CONFIDENCE GUIDE:
    0.9-1.0 = clearly fits
    0.7-0.9 = good match
    0.5-0.7 = uncertain
    < 0.5 = suggest new folder

    Return ONLY a JSON object:
    {{
    "0": {{"folder_name": "bali_travel", "is_new": true, "confidence": 0.9, "reason": "..."}},
    "1": {{"folder_name": "bali_travel", "is_new": false, "confidence": 0.95, "reason": "..."}}
    }}"""

    response = llm.invoke(prompt)

    # Strip markdown fences if present
    raw_text = re.sub(r"^```(?:json)?\s*", "", response.content.strip())
    raw_text = re.sub(r"\s*```$", "", raw_text.strip())
    try:
        raw = json.loads(raw_text)
    except Exception:
        raw = {}

    # Sanitize folder names
    for k in raw:
        raw[k]["folder_name"] = re.sub(
            r"[^a-z0-9_]", "_", raw[k]["folder_name"].strip().lower()
        ).strip("_")

    return json.dumps(raw)


@tool
def get_folder_contents_sample(folder_name: str) -> str:
    """
    Peek inside an existing folder to verify it's a good fit.
    Call this after find_or_suggest_folder returns confidence > 0.7.
    If the sample does NOT match the content, call find_or_suggest_folder again
    with exclude_folder='{folder_name}' to get a different suggestion.
    Input: exact folder name.
    Returns 3 sample chunk snippets from the folder.
    """
    safe_name = sanitize_name(folder_name)
    if not qdrant.collection_exists(safe_name):
        return f"Folder '{safe_name}' does not exist."

    results, _ = qdrant.scroll(
        collection_name=safe_name, 
        limit=3, 
        with_payload=True
    )
    if not results:
        return f"Folder '{safe_name}' is empty."

    snippets = [
        f"- {(point.payload or {}).get('page_content', '')[:200]}..."
        for point in results
    ]
    return f"Sample from '{safe_name}':\n" + "\n".join(snippets)
