"""
Ingest Router
POST /ingest → text/URL/base64 content
POST /ingest/upload → multipart file upload (PDF, DOCX, images)
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from sqlalchemy.orm import Session
import base64

from app.api.dependencies import get_db
# from app.schemas.file import IngestRequest, IngestResponse
# from app.graph.pipeline import ingest_pipeline, IngestState
from app.db import crud

router = APIRouter(prefix="/ingest", tags=["ingest"])