"""
Qdrant service that manages vector collections and document storage.

Architecture: one Qdrant collection per folder.
Folder "Tokyo Travel" to collection "tokyo_travel"
The sanitized_name is stored on the SQLite Folder model so rename never breaks the mapping.

Hybrid retrieval pipeline (used by agent_ragchatbot):
1. Dense retrieval: Qdrant vector similarity (semantic)
2. Sparse retrieval: BM25 keyword match (lexical)
3. RRF fusion: merges both ranked lists
4. Reranker: cross-encoder reorders final candidates
"""
import re
import json
from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from langchain_core.documents import Document
from qdrant_client.models import Distance, VectorParams, Filter, FieldCondition, MatchValue
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from langchain_classic.retrievers.document_compressors import CrossEncoderReranker
from langchain_classic.retrievers import ContextualCompressionRetriever
from langchain_community.cross_encoders import HuggingFaceCrossEncoder

from app.core.config import QDRANT_PATH, RAG_TOP_K, RERANKER_MODEL
from app.services.openai import openai_embeddings as embeddings


qdrant = QdrantClient(path=QDRANT_PATH)


def sanitize_name(name: str) -> str:
    return "".join(c for c in name.lower() if c.isalnum() or c == "_")


def parse_json_response(raw_text: str) -> dict:
    """Strip markdown fences and parse JSON from LLM output."""
    text = re.sub(r"^```(?:json)?\s*", "", raw_text.strip())
    text = re.sub(r"\s*```$", "", text.strip())
    try:
        return json.loads(text)
    except Exception as e:
        print(f"JSON parse error: {e}")
        return {}


def get_existing_collections() -> list[str]:
    try:
        return [c.name for c in qdrant.get_collections().collections]
    except Exception:
        return []


def get_vectorstore(collection_name: str) -> QdrantVectorStore:
    safe_name = sanitize_name(collection_name)
    
    # Create the Qdrant collection if it doesn't exist yet
    if not qdrant.collection_exists(safe_name):
        print(f"Creating new collection: '{safe_name}'")
        qdrant.create_collection(
            collection_name=safe_name,
            vectors_config=VectorParams(
                size=1536,  # text-embedding-3-small outputs 1536-dim vectors
                distance=Distance.COSINE
            )
        )
    
    # wrap it in LangChain's QdrantVectorStore (handles embed + store + query)
    return QdrantVectorStore(
        client=qdrant,
        collection_name=safe_name,
        embedding=embeddings
    )

def add_documents(collection_name: str, docs: list[Document]):
    vs = get_vectorstore(collection_name)
    vs.add_documents(docs)
    print(f"Added {len(docs)} chunks to '{sanitize_name(collection_name)}'")

# scroll through Qdrant to get every stored chunk's text bcs BM25 is exact keyword
def get_all_documents_for_bm25(collection_name: str) -> list[Document]:
    safe_name = sanitize_name(collection_name)
    all_docs = []
    offset = None
    
    while True:
        # Qdrant scroll: fetches up to 100 points at a time
        results, next_offset = qdrant.scroll(
            collection_name=safe_name,
            limit=100,  # adjust if needed
            offset=offset,
            with_payload=True,
            with_vectors=False   # only need text, not vectors
        )
        
        for point in results:
            payload = point.payload or {}
            # LangChain stores chunk text in payload["page_content"]
            text = payload.get("page_content", "")
            metadata = payload.get("metadata", {})
            if text:
                all_docs.append(Document(page_content=text, metadata=metadata))
        
        if next_offset is None:
            break
        offset = next_offset
    
    return all_docs