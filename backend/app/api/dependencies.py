"""
Shared FastAPI dependencies — imported by routers via Depends().
"""
from app.services.qdrant import get_existing_collections


def get_collections() -> list[str]:
    """Returns all current Qdrant collection names."""
    return get_existing_collections()