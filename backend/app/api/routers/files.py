from fastapi import APIRouter

router = APIRouter(prefix="/files", tags=["files"])

@router.get("/ping")
def ping_files():
    return {"ok": True, "module": "files"}