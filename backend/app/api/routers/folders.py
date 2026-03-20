from fastapi import APIRouter

router = APIRouter(prefix="/folders", tags=["folders"])

@router.get("/ping")
def ping_folders():
    return {"ok": True, "module": "folders"}