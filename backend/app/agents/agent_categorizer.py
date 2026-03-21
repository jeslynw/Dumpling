from app.tools.tools_categorizer import suggest_folder
from app.schemas.folder import CategorizationRequest, CategorizationResult


def _confidence_band(confidence: float) -> str:
    if confidence >= 0.9:
        return "clearly_fits"
    if confidence > 0.7:
        return "good_match"
    if confidence >= 0.5:
        return "uncertain"
    return "suggest_new"


def categorize_note(request: CategorizationRequest) -> CategorizationResult:
    result = suggest_folder(request.content, request.meta)
    confidence = float(result["confidence"])
    is_new_folder = bool(result["is_new_folder"])
    band = _confidence_band(confidence)

    # Notebook policy: <= 0.7 requires confirmation; > 0.7 existing folders require verification.
    needs_confirmation = confidence <= 0.7
    verification_required = confidence > 0.7 and not is_new_folder

    if verification_required:
        action = "verify_existing_folder"
    elif needs_confirmation:
        action = "ask_user_confirmation"
    elif is_new_folder:
        action = "create_new_folder"
    else:
        action = "auto_assign"

    return CategorizationResult(
        folder_name=result["folder_name"],
        is_new_folder=is_new_folder,
        confidence=confidence,
        reason=result["reason"],
        needs_confirmation=needs_confirmation,
        confidence_band=band,
        verification_required=verification_required,
        action=action,
    )