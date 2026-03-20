"""
Ingest Router
POST /ingest → text/URL/base64 content
POST /ingest/upload → multipart file upload (PDF, DOCX, images)
"""
from fastapi import APIRouter

router = APIRouter(prefix="/ingest", tags=["ingest"])

@router.get("/ping")
def ping_ingest():
    return {"ok": True, "module": "ingest"}