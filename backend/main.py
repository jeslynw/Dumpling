# fastapi
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import Base, engine    # db tables + connection
from app.api.routers import ingest, folders, files, chat    # route handlers



Base.metadata.create_all(bind=engine)

# API app instance for project
app = FastAPI(
    title="SmartNotebook API",
    description="AI-powered notebook with auto-categorization, RAG chat, and contextual summaries.",
    version="1.0.0",
)

# CORS -> middleware: code that runs before request reaches specific route

########## DELETE if we dont end up creating user db ##########
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000/simple"],  # Next.js dev server + TipTap
    allow_credentials=True,
    allow_methods=["*"],    # allow all http requests
    allow_headers=["*"],    # allow auth token
)
################################################################

# routing
app.include_router(ingest.router)
app.include_router(folders.router)
app.include_router(files.router)
app.include_router(chat.router)


# testing
@app.get("/health")
def health():
    return {"status": "ok"}