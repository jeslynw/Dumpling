from fastapi import APIRouter
from app.agents.agent_categorizer import categorize_note
from app.schemas.folder import CategorizationRequest, CategorizationResult

router = APIRouter()

@router.post("/categorize", response_model=CategorizationResult)
def categorize(request: CategorizationRequest):
    return categorize_note(request)