"""
Shared FastAPI dependencies — imported by routers via Depends().
Keeps routers clean; add auth, rate limiting, etc. here later.
"""
from app.db.database import get_db  # re-export so routers import from one place

__all__ = ["get_db"]