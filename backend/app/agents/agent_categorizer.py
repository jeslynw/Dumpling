# ...existing imports...
from app.tools.tools_categorizer import suggest_folder
from app.schemas.folder import CategorizationRequest, CategorizationResult

def categorize_note(request: CategorizationRequest) -> CategorizationResult:
    """
    Suggest a folder/category for a note using LLM or rules.
    """
    folder, confidence = suggest_folder(request.content, request.meta)
    return CategorizationResult(
        suggested_folder=folder,
        confidence=confidence
    )