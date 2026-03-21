import base64
import mimetypes
from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_core.messages import HumanMessage
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import CHUNK_SIZE, CHUNK_OVERLAP
from app.core.json_utils import parse_json_response
from app.services.openai import openai_llm, openai_vision


def _sanitize_text(text: str) -> str:
    if not text:
        return ""
    return text.encode("utf-8", errors="ignore").decode("utf-8").replace("\x00", "")

#checked
def generate_document_summary(full_text: str) -> str:
    safe_text = _sanitize_text(full_text[:15000])
    if not safe_text.strip():
        return ""

    prompt = f"""
    Please read the following document and provide a highly condensed, global summary (approx 150-300 words). 
    Focus on the core subject matter, the main entities (names, places, organizations), and the overall theme.
    This summary will be used to provide context to isolated chunks of this document, so ensure the main 'Who, What, Where' is clear.
    
    <document>
    {safe_text}
    </document>
    """

    response = openai_llm.invoke(prompt)
    return (response.content or "").strip()

#checked
def generate_chunk_context(doc_summary: str, chunk_text: str) -> str:
    # sanitize: remove null bytes and non-UTF8 chars that corrupt JSON payload
    safe_doc = doc_summary.encode("utf-8", errors="ignore").decode("utf-8")
    safe_doc = safe_doc.replace("\x00", "")   # remove null bytes
    safe_chunk = chunk_text.encode("utf-8", errors="ignore").decode("utf-8")
    safe_chunk = safe_chunk.replace("\x00", "")

    prompt = (
        "<summarized document>\n"
        + safe_doc
        + "\n</summarized document>\n\n"
        "Here is the chunk we want to situate within the whole document:\n"
        "<chunk>\n"
        + safe_chunk
        + "\n</chunk>\n\n"
        "Please give a short context (2-3 sentences) to situate this chunk within the overall document "
        "for the purposes of improving search retrieval. Answer ONLY with the brief context and nothing else."
    )
    response = openai_llm.invoke(prompt)
    return (response.content or "").strip()

#checked
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

#checked
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

#checked
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

    allowed_categories = ["Work", "Finance", "Personal", "Travel", "Food", "Education", "Other"]
    prompt = (
        "You are a production image classification API. Analyze the image and return STRICT JSON ONLY "
        "following the JSON format below. No markdown.\n"
        "Tasks:\n"
        "1. Provide a concise summary (max 100 words).\n"
        "2. Generate 3-5 relevant tags.\n"
        f"3. Assign ONE category from: {allowed_categories}\n\n"
        "JSON FORMAT: {\"summary\": \"...\", \"tags\": [\"tag1\", \"tag2\"], \"category\": \"category_name\"}"
    )

    msg = HumanMessage(
        content=[
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{image_b64}"}},
        ]
    )
    response = openai_vision.invoke([msg])
    raw_response = _sanitize_text(response.content if hasattr(response, "content") else str(response))
    result_dict = parse_json_response(raw_response)

    full_text = (
        f"Image Filename: {p.name}\n"
        f"Category: {result_dict.get('category')}\n"
        f"Tags: {', '.join(result_dict.get('tags', []))}\n"
        f"Summary: {result_dict.get('summary')}"
    )

    chunks = chunk_with_context(
        full_text=full_text,
        filename=p.name,
        input_type="image",
    )
    for c in chunks:
        c.metadata["source"] = str(p)
        c.metadata["file_id"] = p.name
    return chunks

#checked
def wrap_text(text: str) -> List[Document]:
    safe = _sanitize_text(text)
    if not safe.strip():
        return []

    chunks = chunk_with_context(safe, filename="", input_type="text")
    for c in chunks:
        c.metadata["source"] = "raw_text"
        c.metadata["file_id"] = "raw_text"
    return chunks