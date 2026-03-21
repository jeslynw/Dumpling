"""
Folder registry: persists folder metadata to disk so the RAG chatbot can pick folders.
Structure (folder_registry.json):
  { "folder_name": { "description": str, "sources": [str] } }
"""
import json
import os

from app.core.constants import FOLDER_REGISTRY_PATH
from app.services.openai import llm


def _sanitize_text(text: str) -> str:
    """Remove null bytes and invalid UTF-8 that corrupt OpenAI JSON payload."""
    return text.encode("utf-8", errors="ignore").decode("utf-8").replace("\x00", "")


def load_registry() -> dict:
    if os.path.exists(FOLDER_REGISTRY_PATH):
        with open(FOLDER_REGISTRY_PATH) as f:
            return json.load(f)
    return {}


def save_registry(registry: dict) -> None:
    with open(FOLDER_REGISTRY_PATH, "w") as f:
        json.dump(registry, f, indent=2)


def update_folder_registry(
    folder_name: str,
    title: str,
    summary: str,
    source: str,
    is_new_folder: bool,
) -> None:
    """
    Create or update a folder's registry entry.
    - New folder  → LLM generates initial 2-sentence description.
    - Existing    → LLM updates description to include new content.
    Always appends source to the sources list.
    """
    registry = load_registry()
    safe_summary = _sanitize_text(summary)

    if folder_name not in registry:
        desc_prompt = (
            f"Write a 2-sentence description for a notebook folder called '{folder_name}' "
            f"that contains content about: {safe_summary}. Be concise and specific."
        )
        description = llm.invoke(desc_prompt).content.strip()
        registry[folder_name] = {"description": description, "sources": [source]}
        print(f"  📁 Created registry entry for '{folder_name}'")
    else:
        existing_desc = _sanitize_text(registry[folder_name]["description"])
        update_prompt = (
            f"Update this folder description to also include new content being added.\n"
            f"Current description: {existing_desc}\n"
            f"New content summary: {safe_summary}\n"
            f"Return ONLY the updated 2-sentence description. Be concise."
        )
        registry[folder_name]["description"] = llm.invoke(update_prompt).content.strip()
        if source not in registry[folder_name]["sources"]:
            registry[folder_name]["sources"].append(source)
        print(f"  📁 Updated registry entry for '{folder_name}'")

    save_registry(registry)
