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
from functools import lru_cache
from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from langchain_core.documents import Document
from qdrant_client.models import Distance, VectorParams
from langchain_community.retrievers import BM25Retriever
from langchain_community.cross_encoders import HuggingFaceCrossEncoder

from app.core.config import QDRANT_PATH, RAG_TOP_K, RERANKER_MODEL
from app.core.json_utils import parse_json_response as _shared_parse_json_response
from app.services.openai import openai_embeddings as embeddings


qdrant = QdrantClient(path=QDRANT_PATH)

# Checked
def sanitize_name(name: str) -> str:
    return "".join(c for c in name.lower() if c.isalnum() or c == "_")

# Checked
def parse_json_response(raw_text: str) -> dict:
    """Backward-compatible wrapper around shared JSON parser utility."""
    return _shared_parse_json_response(raw_text)

# Checked
def get_existing_collections() -> list[str]:
    try:
        return [c.name for c in qdrant.get_collections().collections]
    except Exception:
        return []

# Checked
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
# Checked
def add_documents(collection_name: str, docs: list[Document]):
    vs = get_vectorstore(collection_name)
    vs.add_documents(docs)
    print(f"Added {len(docs)} chunks to '{sanitize_name(collection_name)}'")

# scroll through Qdrant to get every stored chunk's text bcs BM25 is exact keyword
# was get_all_documents_from_qdrant but renamed to clarify it's for BM25 retrieval, not vector search
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

def _doc_key(doc: Document) -> str:
    md = doc.metadata or {}
    source = md.get("source") or md.get("filename") or md.get("file_id") or "unknown"
    snippet = (doc.page_content or "")[:200]
    return f"{source}::{snippet}"


def _rrf_fuse_ranked_docs(dense_docs: list[Document], sparse_docs: list[Document], k: int = 60) -> list[Document]:
    scores: dict[str, float] = {}
    docs_by_key: dict[str, Document] = {}

    for rank, doc in enumerate(dense_docs, start=1):
        key = _doc_key(doc)
        scores[key] = scores.get(key, 0.0) + 1.0 / (k + rank)
        docs_by_key[key] = doc

    for rank, doc in enumerate(sparse_docs, start=1):
        key = _doc_key(doc)
        scores[key] = scores.get(key, 0.0) + 1.0 / (k + rank)
        if key not in docs_by_key:
            docs_by_key[key] = doc

    ranked_keys = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
    return [docs_by_key[key] for key in ranked_keys]


@lru_cache(maxsize=1)
def _get_cross_encoder() -> HuggingFaceCrossEncoder:
    return HuggingFaceCrossEncoder(model_name=RERANKER_MODEL)


def _rerank_docs(query: str, docs: list[Document], top_k: int) -> list[Document]:
    if not docs:
        return []

    try:
        model = _get_cross_encoder()
        pairs = [[query, (d.page_content or "")[:2000]] for d in docs]
        scores = model.score(pairs)
        ranked = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in ranked[:top_k]]
    except Exception:
        # Graceful fallback to fused rank if reranker model unavailable.
        return docs[:top_k]


def search_hybrid_qdrant_with_sources(
    query: str,
    top_k: int = 5,
    collection_name: str = "default",
    file_id: str | None = None,
) -> list[dict]:
    """
    Hybrid retrieval: dense + BM25, then RRF fusion, then cross-encoder rerank.
    """
    safe_collection = sanitize_name(collection_name)
    candidate_k = max(top_k * 4, RAG_TOP_K * 2)

    # Dense retrieval from Qdrant.
    vs = get_vectorstore(safe_collection)
    dense = vs.similarity_search(query, k=candidate_k)

    # Sparse retrieval (BM25) over full collection text.
    all_docs = get_all_documents_for_bm25(safe_collection)
    if file_id:
        all_docs = [d for d in all_docs if (d.metadata or {}).get("file_id") == file_id]

    if not all_docs:
        dense_top = dense[:top_k]
        return [
            {
                "text": doc.page_content,
                "source": (doc.metadata or {}).get("source") or (doc.metadata or {}).get("filename") or "unknown",
                "collection": safe_collection,
            }
            for doc in dense_top
        ]

    bm25 = BM25Retriever.from_documents(all_docs)
    bm25.k = candidate_k
    sparse = bm25.invoke(query)

    if file_id:
        dense = [d for d in dense if (d.metadata or {}).get("file_id") == file_id]
        sparse = [d for d in sparse if (d.metadata or {}).get("file_id") == file_id]

    fused = _rrf_fuse_ranked_docs(dense, sparse)
    reranked = _rerank_docs(query, fused, top_k=top_k)

    results = []
    for doc in reranked:
        md = doc.metadata or {}
        results.append(
            {
                "text": doc.page_content,
                "source": md.get("source") or md.get("filename") or md.get("file_id") or "unknown",
                "collection": safe_collection,
            }
        )
    return results