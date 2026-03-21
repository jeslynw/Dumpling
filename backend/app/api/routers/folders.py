"""
GET  /folders          — list all folders with description + sources
GET  /folders/{name}   — get a single folder's metadata
DELETE /folders/{name} — delete a Qdrant collection + registry entry
"""
from fastapi import APIRouter, HTTPException

from app.db.database import load_registry, save_registry
from app.services.qdrant import qdrant, sanitize_name, get_existing_collections
from app.schemas.schema import FolderListResponse, FolderInfo, FolderDeleteResponse

router = APIRouter(prefix="/folders", tags=["Folders"])


@router.get("", response_model=FolderListResponse, summary="List all folders")
def list_folders():
    """Returns every folder in the registry with its description and sources."""
    registry = load_registry()
    folders = [
        FolderInfo(
            name=name,
            description=data.get("description", ""),
            sources=data.get("sources", []),
        )
        for name, data in registry.items()
    ]
    return FolderListResponse(folders=folders)


@router.get("/{name}", response_model=FolderInfo, summary="Get a single folder")
def get_folder(name: str):
    """Returns metadata for one folder."""
    registry = load_registry()
    safe = sanitize_name(name)
    if safe not in registry:
        raise HTTPException(status_code=404, detail=f"Folder '{safe}' not found in registry.")
    data = registry[safe]
    return FolderInfo(name=safe, description=data["description"], sources=data.get("sources", []))


@router.delete("/{name}", response_model=FolderDeleteResponse, summary="Delete a folder")
def delete_folder(name: str):
    """
    Deletes the Qdrant collection AND removes the folder from the registry.
    This is irreversible — all stored chunks will be lost.
    """
    safe = sanitize_name(name)

    # Remove from Qdrant
    if qdrant.collection_exists(safe):
        qdrant.delete_collection(safe)

    # Remove from registry
    registry = load_registry()
    registry.pop(safe, None)
    save_registry(registry)

    return FolderDeleteResponse(deleted=safe, remaining=get_existing_collections())
