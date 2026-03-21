from app.tools.tools_categorizer import suggest_folder
from app.schemas.folder import CategorizationRequest, CategorizationResult


def categorize_note(request: CategorizationRequest) -> CategorizationResult:
    result = suggest_folder(request.content, request.meta)
    return CategorizationResult(
        folder_name=result["folder_name"],
        is_new_folder=result["is_new_folder"],
        confidence=result["confidence"],
        reason=result["reason"],
    )