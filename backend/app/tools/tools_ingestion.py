import base64
import mimetypes
from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_core.messages import HumanMessage
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import CHUNK_SIZE, CHUNK_OVERLAP
from app.services.openai import openai_llm, openai_vision


def _sanitize_text(text: str) -> str:
    if not text:
        return ""
    return text.encode("utf-8", errors="ignore").decode("utf-8").replace("\x00", "")


def generate_document_summary(full_text: str) -> str:
    safe_text = _sanitize_text(full_text[:15000])
    if not safe_text.strip():
        return ""

    prompt = (
        "You are summarizing a document for retrieval.\n"
        "Write a concise 3-5 sentence summary of the whole document.\n"
        "Focus on key topics, entities, and intent.\n\n"
        f"DOCUMENT:\n{safe_text}"
    )
    response = openai_llm.invoke(prompt)
    return (response.content or "").strip()


def generate_chunk_context(doc_summary: str, chunk_text: str) -> str:
    safe_summary = _sanitize_text(doc_summary[:4000])
    safe_chunk = _sanitize_text(chunk_text[:4000])

    prompt = (
        "Given a document summary and one chunk from that document, "
        "write 2-3 sentences of context that help retrieval.\n"
        "Do not repeat the chunk verbatim.\n\n"
        f"DOCUMENT SUMMARY:\n{safe_summary}\n\n"
        f"CHUNK:\n{safe_chunk}"
    )
    response = openai_llm.invoke(prompt)
    return (response.content or "").strip()


def chunk_with_context(full_text: str, filename: str = "", input_type: str = "document") -> List[Document]:
    if not full_text or not full_text.strip():
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""],
    )

    chunks = splitter.create_documents(
        [full_text],
        metadatas=[{
            "filename": filename,
            "input_type": input_type,
            "file_id": filename or input_type,
        }],
    )

    doc_summary = generate_document_summary(full_text)

    enriched = []
    for chunk in chunks:
        context = generate_chunk_context(doc_summary, chunk.page_content)
        chunk.page_content = f"CONTEXT: {context}\n\nCHUNK CONTENT:\n{chunk.page_content}"
        enriched.append(chunk)

    return enriched


def scrape_and_chunk(url: str) -> List[Document]:
    loader = WebBaseLoader(url)
    docs = loader.load()
    if not docs:
        return []

    full_text = "\n\n".join(d.page_content for d in docs if d.page_content)
    chunks = chunk_with_context(full_text, filename=url, input_type="url")

    for c in chunks:
        c.metadata["source"] = url
        c.metadata["file_id"] = url

    return chunks


def parse_document(filepath: str) -> List[Document]:
    """
    Docling-based parser for PDF/DOCX/etc.
    """
    try:
        from docling.document_converter import DocumentConverter
    except Exception as exc:
        raise RuntimeError("Docling is not installed. Please install docling.") from exc

    p = Path(filepath)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    converter = DocumentConverter()
    result = converter.convert(str(p))
    full_text = result.document.export_to_markdown() if result else ""
    if not full_text.strip():
        return []

    chunks = chunk_with_context(full_text, filename=p.name, input_type="document")
    for c in chunks:
        c.metadata["source"] = str(p)
        c.metadata["file_id"] = p.name
    return chunks


def analyze_image(filepath: str) -> List[Document]:
    p = Path(filepath)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    mime_type, _ = mimetypes.guess_type(str(p))
    mime_type = mime_type or "image/jpeg"

    with open(p, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode("utf-8")

    prompt = (
        "Analyze this image and return STRICT JSON only:\n"
        "{"
        "\"summary\": \"max 100 words\", "
        "\"tags\": [\"tag1\", \"tag2\", \"tag3\"], "
        "\"category\": \"Work|Finance|Personal|Travel|Food|Education|Other\""
        "}"
    )

    msg = HumanMessage(
        content=[
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{image_b64}"}},
        ]
    )
    response = openai_vision.invoke([msg])
    analysis_text = _sanitize_text(response.content if hasattr(response, "content") else str(response))

    chunks = chunk_with_context(
        full_text=f"Image filename: {p.name}\nImage analysis:\n{analysis_text}",
        filename=p.name,
        input_type="image",
    )
    for c in chunks:
        c.metadata["source"] = str(p)
        c.metadata["file_id"] = p.name
    return chunks


def wrap_text(text: str) -> List[Document]:
    safe = _sanitize_text(text)
    if not safe.strip():
        return []

    chunks = chunk_with_context(safe, filename="", input_type="text")
    for c in chunks:
        c.metadata["source"] = "raw_text"
        c.metadata["file_id"] = "raw_text"
    return chunks