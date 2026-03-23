OPENAI_LLM_MODEL = "gpt-4o-mini"
OPENAI_EMBED_MODEL = "text-embedding-3-small"
OPENAI_VISION_MODEL = "gpt-4o-mini"
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

CHUNK_SIZE = 3000
CHUNK_OVERLAP = 200
RAG_TOP_K = 5
RAG_TOP_K_EVAL = 10
RAG_TOP_K_LARGE = RAG_TOP_K * 3

EMBED_DIMENSIONS = 1536

CATEGORIZER_CONFIDENCE_THRESHOLD = 0.7

QDRANT_PATH = "./qdrant_db"
FOLDER_REGISTRY_PATH = "folder_registry.json"
NOTEBOOK_CONTENT_DIR = "each_notebook_content"

ALLOWED_IMAGE_CATEGORIES = ["Work", "Finance", "Personal", "Travel", "Food", "Education", "Other"]