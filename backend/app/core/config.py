from dotenv import load_dotenv
import os

load_dotenv()

# --- LLMs ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_LLM_MODEL = "gpt-4o-mini"       # used by openai_llm in services/openai.py
OPENAI_EMBED_MODEL = "text-embedding-3-small"
OPENAI_VISION_MODEL = "gpt-4o-mini"    # used by openai_vision in services/openai.py

# --- Databases ---
QDRANT_PATH = "./data/qdrant_db"        # local mode — swap for QDRANT_URL in prod
SQLITE_URL = "sqlite:///./data/notebook.db"

# --- RAG (change later) ---
RAG_TOP_K = 5           # default retrieval k for chat
RAG_TOP_K_EVAL = 10     # wider k used during RAGAS evaluation for better context recall
CHUNK_SIZE = 1000       # matches notebook's RecursiveCharacterTextSplitter
CHUNK_OVERLAP = 200     # matches notebook's chunk_overlap

# Reranker — cross-encoder model for hybrid RAG reranking step
# ms-marco is a strong general-purpose cross-encoder, runs locally via HuggingFace
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

# --- Tavily ---
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
CATEGORIZER_CONFIDENCE_THRESHOLD = 0.7

# folder registry
FOLDER_REGISTRY_PATH = "folder_registry.json"