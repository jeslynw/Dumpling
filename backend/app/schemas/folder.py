from pydantic import BaseModel
from typing import Optional, Dict

class CategorizationRequest(BaseModel):
    content: str
    meta: Optional[Dict] = None

class CategorizationResult(BaseModel):
    folder_name: str
    is_new_folder: bool
    confidence: float
    reason: str