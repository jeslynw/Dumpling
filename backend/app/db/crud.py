"""
Higher-level operations that coordinate multiple services:
  - parse_json_response         (strips markdown fences, parses LLM JSON output)
  - parse_user_input            (LLM splits messy textbox input into typed items)
  - prepare_input               (resolves local file paths)
  - run_ingestion_agent_batch   (full ingest → categorize → store loop)
  - generate_notebook_content_files  (per-folder synthesis JSON after a batch)
"""
import json
import os
import re
import time

from app.core.constants import FOLDER_REGISTRY_PATH, NOTEBOOK_CONTENT_DIR
from app.services.openai import llm
from app.services.qdrant import (
    add_documents,
    get_all_documents_from_qdrant,
    get_existing_collections,
    sanitize_name,
)
from app.services.summarizer import generate_notebook_content
from app.db.database import update_folder_registry
from app.agents.agent_ingestion import run_ingestion_agent
from app.agents.agent_categorizer import run_categorizer_agent


# ── JSON parsing ──────────────────────────────────────────────────────────────

def parse_json_response(raw_text: str) -> dict | list:
    """Strip markdown fences and parse JSON from LLM output."""
    text = re.sub(r"^```(?:json)?\s*", "", raw_text.strip())
    text = re.sub(r"\s*```$", "", text.strip())
    try:
        return json.loads(text)
    except Exception as e:
        print(f"JSON parse error: {e}")
        return {}


# ── Input parsing ─────────────────────────────────────────────────────────────

def parse_user_input(raw_input: str) -> list[dict]:
    """
    Use LLM to extract individual items from a messy user textbox.
    Returns: [{"content": ..., "type_hint": "url"|"document"|"image"|"text"}]
    """
    prompt = f"""The user submitted the following input to a notebook app.
    Extract every individual item they want to save and return a JSON array.

    Each item should have:
    - "content": the URL, filename, or the text snippet itself
    - "type_hint": one of "url", "document", "image", or "text"

    Rules:
    - URLs start with http:// or https://
    - Images have extensions like .png, .jpg, .jpeg, .gif, .webp
    - Documents have extensions like .pdf, .docx, .doc, .pptx, .html
    - Everything else is plain text
    - If there is a large block of plain text, keep it as one "text" item

    Input:
    {raw_input}

    Return ONLY a valid JSON array. No markdown, no explanation.
    Example: [{{"content": "https://example.com", "type_hint": "url"}}, {{"content": "notes.pdf", "type_hint": "document"}}, {{"content": "Some notes here", "type_hint": "text"}}]"""

    response = llm.invoke(prompt)
    parsed = parse_json_response(response.content)
    if not isinstance(parsed, list):
        return [{"content": raw_input, "type_hint": "text"}]
    return parsed


def prepare_input(item: dict) -> dict:
    """
    If item is a local document or image file, resolve the filepath.
    URLs and plain text pass through unchanged.
    """
    content = item["content"]
    type_hint = item.get("type_hint", "")

    if type_hint in ["file", "document", "image"] and os.path.isfile(content):
        return {
            "content": content,
            "filename": os.path.basename(content),
            "type_hint": type_hint,
        }
    return {"content": content, "filename": "", "type_hint": type_hint}


# ── Notebook content file generation ─────────────────────────────────────────

def generate_notebook_content_files(batch_results: list[dict]) -> None:
    """
    Called once after run_ingestion_agent_batch() completes.
    Writes one {folder_name}_notebook_content.json per folder touched in this batch.
    """
    touched_folders = {r["folder"] for r in batch_results if r.get("folder")}
    if not touched_folders:
        print("  ⚠️  No folders to generate notebook content for")
        return

    print(f"\n📒 Generating notebook content for {len(touched_folders)} folder(s): {touched_folders}")
    os.makedirs(NOTEBOOK_CONTENT_DIR, exist_ok=True)

    for folder_name in touched_folders:
        print(f"\n  📂 Processing folder: '{folder_name}'")
        docs = get_all_documents_from_qdrant(folder_name)
        content = generate_notebook_content(folder_name, docs)
        if not content:
            continue

        output = {folder_name: {"notebook_content": content}}
        filepath = f"{NOTEBOOK_CONTENT_DIR}/{folder_name}_notebook_content.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        print(f"  ✅ Written: {filepath}")

    print("\n✅ All notebook content files generated")


# ── Batch ingestion pipeline ──────────────────────────────────────────────────

def run_ingestion_agent_batch(inputs: list[dict]) -> list[dict]:
    """
    Full pipeline for a list of prepared inputs:
      ingest → categorize → (confirm?) → store → update registry

    Each input dict: {"content": ..., "filename": ..., "type_hint": ...}
    Returns list of result dicts: {docs, title, summary, folder, needs_confirmation}
    """
    results = []

    for item in inputs:
        label = item.get("filename") or item["content"]
        print(f"\n{'='*60}\nProcessing: {label}")

        try:
            # Step 1: ingestion agent
            docs, title, summary = run_ingestion_agent(
                raw_content=item["content"],
                filename=item.get("filename", ""),
            )

            if not docs:
                print("  ⚠️  No content extracted, skipping")
                results.append({"docs": [], "title": title, "summary": summary, "folder": None})
                continue

            # Step 2: categorizer
            source = item.get("filename") or item["content"]
            category = run_categorizer_agent(title=title, summary=summary, source=source)
            folder_name = category.get("folder_name", "uncategorized")
            is_new_folder = category.get("is_new_folder", False)
            needs_confirmation = category.get("needs_confirmation", False)

            # Step 3: store + registry
            add_documents(folder_name, docs)
            print(f"  ✅ Stored {len(docs)} chunks in '{folder_name}'")
            update_folder_registry(folder_name, title, summary, source, is_new_folder)

            results.append({
                "docs": docs,
                "title": title,
                "summary": summary,
                "folder": folder_name,
                "needs_confirmation": needs_confirmation,
            })

        except Exception as e:
            print(f"  ❌ Failed: {e}")
            results.append({"docs": [], "title": "", "summary": "", "folder": None})

        time.sleep(3)

    generate_notebook_content_files(results)
    return results
