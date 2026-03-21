"""
Ingestion helper functions (called by the agent tools defined inside build_ingestion_agent).
These are pure helpers — they do NOT write to collected_docs directly.
"""
import os
import re
import tempfile
import time

from docling.document_converter import DocumentConverter
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.constants import CHUNK_OVERLAP, CHUNK_SIZE
from app.services.openai import vision_client
from app.services.summarizer import generate_document_summary, generate_chunk_context

# Docling converter — handles PDF, DOCX, PPTX, HTML, images (loaded once)
docling_converter = DocumentConverter()


# ── Web scraping ──────────────────────────────────────────────────────────────

def scrape_and_chunk(url: str) -> list[Document]:
    """WebBaseLoader → clean whitespace → split → Contextual RAG → tag chunks with file_id=url."""
    print(f"Scraping: {url}")
    try:
        loader = WebBaseLoader(url)
        raw_docs = loader.load()
    except Exception as e:
        print(f"  ❌ Failed to scrape {url}: {e}")
        return []

    if not raw_docs:
        return []

    for doc in raw_docs:
        doc.page_content = re.sub(r"\s+", " ", doc.page_content).strip()

    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    chunks = splitter.split_documents(raw_docs)

    # Generate a whole-document summary once — used as context for every chunk
    full_text = raw_docs[0].page_content
    doc_summary = generate_document_summary(full_text)

    enriched = []
    for i, chunk in enumerate(chunks):
        context = generate_chunk_context(doc_summary, chunk.page_content)
        chunk.page_content = f"CONTEXT: {context}\n\nCHUNK CONTENT:\n{chunk.page_content}"
        chunk.metadata["file_id"] = url
        enriched.append(chunk)
        if (i + 1) % 5 == 0:   # brief pause every 5 chunks to avoid rate limits
            time.sleep(1)

    print(f"✅ Got {len(enriched)} contextual chunks from {url}")
    return enriched


# ── Docling parsing ───────────────────────────────────────────────────────────

def parse_with_docling(file_bytes: bytes, filename: str) -> str:
    """Write bytes to a temp file, let Docling extract text → markdown string."""
    with tempfile.NamedTemporaryFile(suffix=f"_{filename}", delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name
    try:
        result = docling_converter.convert(tmp_path)
        return result.document.export_to_markdown()
    except Exception as e:
        print(f"Docling parse error for '{filename}': {e}")
        return ""
    finally:
        os.unlink(tmp_path)


# ── Chunking with context metadata ───────────────────────────────────────────

def chunk_with_context(full_text: str, filename: str = "", input_type: str = "document") -> list[Document]:
    if not full_text.strip():
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""]   # markdown-aware
    )
    chunks = splitter.create_documents(
        [full_text],
        metadatas=[{
            "filename": filename,
            "input_type": input_type,
            "file_id": filename   # file_id matches filename so search_source filter works
        }]
    )

    # apply contextual RAG to every chunk
    enriched = []
    doc_summary = generate_document_summary(full_text)
    for chunk in chunks:
        context = generate_chunk_context(doc_summary, chunk.page_content)
        chunk.page_content = f"CONTEXT: {context}\n\nCHUNK CONTENT:\n{chunk.page_content}"
        enriched.append(chunk)

    print(f"  ✅ {len(enriched)} contextual chunks from '{filename or input_type}'")
    return enriched
