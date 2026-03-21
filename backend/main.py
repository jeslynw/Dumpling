"""
SmartNotebook Backend
Run with:  uvicorn main:app --reload --port 8000
Docs at:   http://localhost:8000/docs
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import chat, folders, ingest

app = FastAPI(
    title="SmartNotebook API",
    description="Agentic RAG notebook: ingest URLs / files / text, chat with your notes.",
    version="1.0.0",
)

# ── CORS (adjust origins for production) ─────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(ingest.router)
app.include_router(folders.router)
app.include_router(chat.router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "SmartNotebook API is running"}


@app.get("/health", tags=["Health"])
def health():
    from app.services.qdrant import get_existing_collections
    return {
        "status": "ok",
        "collections": get_existing_collections(),
    }
