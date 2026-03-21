from pathlib import Path
from typing import List, Tuple

from langchain_core.documents import Document

from app.services.openai import openai_llm
from app.tools.tools_ingestion import (
    scrape_and_chunk,
    parse_document,
    analyze_image,
    wrap_text,
)
from app.agents.agent_categorizer import categorize_note
from app.schemas.folder import CategorizationRequest

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".jfif"}
DOC_EXTS = {".pdf", ".docx", ".doc", ".pptx", ".html", ".htm", ".md", ".txt"}


def _is_url(text: str) -> bool:
    t = (text or "").strip().lower()
    return t.startswith("http://") or t.startswith("https://")


def _detect_input_type(raw_content: str, filename: str = "") -> str:
    """
    Returns one of: url | image | document | text
    """
    if _is_url(raw_content):
        return "url"

    # If raw_content is a local file path, use that extension
    if raw_content and Path(raw_content).exists():
        ext = Path(raw_content).suffix.lower()
        if ext in IMAGE_EXTS:
            return "image"
        if ext in DOC_EXTS:
            return "document"

    # Otherwise use filename hint
    ext = Path(filename).suffix.lower() if filename else ""
    if ext in IMAGE_EXTS:
        return "image"
    if ext in DOC_EXTS:
        return "document"

    return "text"


def _generate_title_and_summary(content: str, source_hint: str = "") -> Tuple[str, str]:
    safe_content = (content or "")[:2500].encode("utf-8", errors="ignore").decode("utf-8").replace("\x00", "")

    prompt = (
        "Given this content, provide exactly:\n"
        "TITLE: <short descriptive title, max 8 words>\n"
        "SUMMARY: <about 120-180 words>\n\n"
        f"Content:\n{safe_content}"
    )

    resp = openai_llm.invoke(prompt)
    text = (resp.content or "").strip()

    title = source_hint.strip() if source_hint else "Untitled"
    summary = ""

    for line in text.splitlines():
        if line.startswith("TITLE:"):
            title = line.replace("TITLE:", "", 1).strip() or title
        elif line.startswith("SUMMARY:"):
            summary = line.replace("SUMMARY:", "", 1).strip()

    if not summary:
        summary = "No summary available."

    return title, summary


def run_ingestion_agent(raw_content: str, filename: str = "") -> Tuple[List[Document], str, str, str, float]:
    """
    Prototype ingestion orchestrator.
    Returns: (docs, title, summary, suggested_folder, confidence)
    """
    input_type = _detect_input_type(raw_content=raw_content, filename=filename)

    if input_type == "url":
        docs = scrape_and_chunk(raw_content)

    elif input_type == "document":
        # Prefer raw_content if it's a real filepath; else fallback to filename
        filepath = raw_content if Path(raw_content).exists() else filename
        docs = parse_document(filepath)

    elif input_type == "image":
        filepath = raw_content if Path(raw_content).exists() else filename
        docs = analyze_image(filepath)

    else:
        docs = wrap_text(raw_content)

    first_content = docs[0].page_content if docs else (raw_content or "")[:600]
    source_hint = filename or (raw_content[:60] if raw_content else "Untitled")
    title, summary = _generate_title_and_summary(first_content, source_hint=source_hint)
    # --- Categorizer integration ---
    cat_request = CategorizationRequest(content=first_content, meta={"filename": filename})
    cat_result = categorize_note(cat_request)
    suggested_folder = cat_result.folder_name
    confidence = cat_result.confidence

    return docs, title, summary, suggested_folder, confidence