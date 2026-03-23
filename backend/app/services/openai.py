"""
Singleton clients for OpenAI LLM, embeddings, vision, and the local cross-encoder.
Import these objects directly — they are initialised once at startup.
"""
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from openai import OpenAI as RawOpenAI

from app.core.config import OPENAI_API_KEY
from app.core.constants import (
    OPENAI_LLM_MODEL,
    OPENAI_EMBED_MODEL,
    RERANKER_MODEL,
)

# LangChain LLM
llm = ChatOpenAI(
    model=OPENAI_LLM_MODEL,
    api_key=OPENAI_API_KEY,
    temperature=0.1,
)

# Embeddings (1536-dim, stored in Qdrant)
openai_embeddings = OpenAIEmbeddings(
    model=OPENAI_EMBED_MODEL,
    api_key=OPENAI_API_KEY,
)

# Raw OpenAI client
vision_client = RawOpenAI(api_key=OPENAI_API_KEY)

# Cross-encoder reranker
cross_encoder = HuggingFaceCrossEncoder(model_name=RERANKER_MODEL)
