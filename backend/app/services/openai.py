'''
OpenAI services (import from here)
- openai_llm: ChatOpenAI (gpt-4o-mini) for general text tasks
- openai_vision: ChatOpenAI (gpt-4o-mini) for multimodal image analysis
- openai_embeddings: OpenAIEmbeddings (text-embedding-3-small) for Qdrant
'''
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from app.core.config import OPENAI_API_KEY, OPENAI_EMBED_MODEL, OPENAI_LLM_MODEL, OPENAI_VISION_MODEL


openai_llm = ChatOpenAI(
    model=OPENAI_LLM_MODEL,
    api_key=OPENAI_API_KEY,
    temperature=0,          # deterministic for classification/RAG
)

openai_vision = ChatOpenAI(
    model=OPENAI_VISION_MODEL,
    api_key=OPENAI_API_KEY,
    temperature=0.1,        # matches notebook's vision temperature
)

openai_embeddings = OpenAIEmbeddings(
    model=OPENAI_EMBED_MODEL,
    api_key=OPENAI_API_KEY,
)