"""
Qdrant client + all retrieval logic:
  - sanitize_name, get_vectorstore, add_documents, get_all_documents_from_qdrant
  - get_hybrid_retriever  (BM25 + Dense + RRF + CrossEncoder reranker)
  - grade_chunks, broaden_query, increase_k_broaden_query, tavily_search
  - retrieve_with_crag   (the full CRAG fallback chain)
"""
import re

import qdrant_client
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever, ContextualCompressionRetriever
from langchain_classic.retrievers.document_compressors import CrossEncoderReranker
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_qdrant import QdrantVectorStore
from langchain_community.tools.tavily_search import TavilySearchResults
from qdrant_client.models import Distance, VectorParams, Filter, FieldCondition, MatchValue

from app.core.config import TAVILY_API_KEY
from app.core.constants import (
    EMBED_DIMENSIONS,
    RAG_TOP_K,
    RAG_TOP_K_LARGE,
    QDRANT_PATH,
)
from app.services.openai import openai_embeddings, llm, cross_encoder

# ── Qdrant client (local on-disk) ─────────────────────────────────────────────
qdrant = qdrant_client.QdrantClient(path=QDRANT_PATH)


# ── Helpers ───────────────────────────────────────────────────────────────────

def sanitize_name(name: str) -> str:
    """Qdrant collection names: lowercase alphanumeric + underscores only."""
    return "".join(c for c in name.lower() if c.isalnum() or c == "_")


def get_existing_collections() -> list[str]:
    try:
        return [c.name for c in qdrant.get_collections().collections]
    except Exception:
        return []


def get_vectorstore(collection_name: str) -> QdrantVectorStore:
    safe_name = sanitize_name(collection_name)
    if not qdrant.collection_exists(safe_name):
        print(f"Creating new collection: '{safe_name}'")
        qdrant.create_collection(
            collection_name=safe_name,
            vectors_config=VectorParams(size=EMBED_DIMENSIONS, distance=Distance.COSINE),
        )
    return QdrantVectorStore(client=qdrant, collection_name=safe_name, embedding=openai_embeddings)


def add_documents(collection_name: str, docs: list[Document]) -> None:
    vs = get_vectorstore(collection_name)
    vs.add_documents(docs)
    print(f"Added {len(docs)} chunks to '{sanitize_name(collection_name)}'")


def get_all_documents_from_qdrant(collection_name: str) -> list[Document]:
    """Scroll every chunk from a collection (needed for BM25 which requires all docs)."""
    safe_name = sanitize_name(collection_name)
    all_docs: list[Document] = []
    offset = None
    while True:
        results, next_offset = qdrant.scroll(
            collection_name=safe_name,
            limit=100,
            offset=offset,
            with_payload=True,
            with_vectors=False,
        )
        for point in results:
            payload = point.payload or {}
            text = payload.get("page_content", "")
            metadata = payload.get("metadata", {})
            if text:
                all_docs.append(Document(page_content=text, metadata=metadata))
        if next_offset is None:
            break
        offset = next_offset
    return all_docs


# ── Hybrid RAG ────────────────────────────────────────────────────────────────

def get_hybrid_retriever(collection_name: str, top_k: int = RAG_TOP_K, file_id: str | None = None):
    """
    Dense (Qdrant) + BM25 fused with RRF, then re-ranked by cross-encoder.
    If the collection is empty, falls back to dense-only.
    """
    safe_name = sanitize_name(collection_name)
    vectorstore = get_vectorstore(safe_name)

    search_kwargs: dict = {"k": top_k * 2}
    if file_id:
        search_kwargs["filter"] = Filter(
            must=[FieldCondition(key="metadata.file_id", match=MatchValue(value=file_id))]
        )
    dense_retriever = vectorstore.as_retriever(search_kwargs=search_kwargs)

    all_docs = get_all_documents_from_qdrant(safe_name)
    if not all_docs:
        print("No documents found for BM25, using dense only")
        return dense_retriever

    bm25_retriever = BM25Retriever.from_documents(all_docs, k=top_k * 2)
    ensemble = EnsembleRetriever(
        retrievers=[dense_retriever, bm25_retriever],
        weights=[0.5, 0.5],
    )

    reranker = CrossEncoderReranker(model=cross_encoder, top_n=top_k)
    return ContextualCompressionRetriever(base_compressor=reranker, base_retriever=ensemble)


# ── CRAG helpers ──────────────────────────────────────────────────────────────

_GRADER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a grader assessing whether a retrieved document chunk is relevant to the user's question.
Return ONLY a JSON object: {{"relevant": true or false, "reason": "brief reason"}}
Be lenient: mark as relevant if the chunk contains ANY information useful to answering the question."""),
    ("human", "Question: {question}\n\nChunk:\n{chunk}"),
])
_grader_chain = _GRADER_PROMPT | llm | JsonOutputParser()


def grade_chunks(question: str, docs: list[Document]) -> bool:
    """Return True if ANY of the top-3 chunks is relevant to the question."""
    if not docs:
        return False
    for doc in docs[:3]:
        try:
            result = _grader_chain.invoke({
                "question": question,
                "chunk": doc.page_content[:500],
            })
            if result.get("relevant", True):
                return True
        except Exception:
            return True
    return False


def broaden_query(question: str) -> str:
    """Ask LLM to rephrase a failed query more broadly."""
    prompt = (
        "The following search query failed to find relevant results. "
        "Rewrite it as a broader, more general question that might find related information. "
        "Return ONLY the rewritten question, nothing else.\n\n"
        f"Original question: {question}"
    )
    response = llm.invoke(prompt)
    broadened = response.content.strip()
    print(f"Broadened query: '{broadened}'")
    return broadened


def increase_k_broaden_query(
    broader: str, collection_name: str, file_id: str | None = None
) -> list[Document]:
    """Same broadened query but casts a wider net (RAG_TOP_K_LARGE) with a fresh retriever."""
    print(f"  🔍 Retrying with larger top_k={RAG_TOP_K_LARGE}...")
    retriever = get_hybrid_retriever(collection_name, top_k=RAG_TOP_K_LARGE, file_id=file_id)
    return retriever.invoke(broader)


def tavily_search(question: str) -> list[Document]:
    """Web-search fallback. Results are tagged [WEB SEARCH RESULT]."""
    try:
        tavily = TavilySearchResults(max_results=3, tavily_api_key=TAVILY_API_KEY)
        results = tavily.invoke(question)
        web_docs = []
        for r in results:
            content = f"[WEB SEARCH RESULT: not from your notebook]\n{r.get('content', '')}"
            web_docs.append(Document(
                page_content=content,
                metadata={"source": r.get("url", "web"), "type": "web_search"},
            ))
        print(f"🌐 Tavily found {len(web_docs)} web results")
        return web_docs
    except Exception as e:
        print(f"❌ Tavily search failed: {e}")
        return []


def retrieve_with_crag(
    question: str,
    retriever,
    label: str = "",
    collection_name: str | None = None,
    file_id: str | None = None,
) -> list[Document]:
    """
    Full CRAG fallback chain:
      1. Initial retrieval → grade
      2. Broaden query    → grade
      3. Larger top_k     → grade
      4. Tavily web search
    """
    prefix = f"[{label}] " if label else ""

    docs = retriever.invoke(question)
    if grade_chunks(question, docs):
        print(f"{prefix}✅ Chunks are relevant")
        return docs

    print(f"{prefix}⚠️ Chunks not relevant, broadening query...")
    broader = broaden_query(question)
    docs = retriever.invoke(broader)
    if grade_chunks(question, docs):
        print(f"{prefix}✅ Broadened query found relevant chunks")
        return docs

    print(f"{prefix}⚠️ Still not relevant, increasing top_k...")
    if collection_name:
        docs = increase_k_broaden_query(broader, collection_name, file_id)
        if grade_chunks(question, docs):
            print(f"{prefix}✅ Larger top_k found relevant chunks")
            return docs

    print(f"{prefix}🌐 Falling back to web search...")
    return tavily_search(question)
