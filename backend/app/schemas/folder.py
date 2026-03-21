from pydantic import BaseModel
from typing import Optional, Dict

class CategorizationRequest(BaseModel):
    content: str
    meta: Optional[Dict] = None

class CategorizationResult(BaseModel):
    suggested_folder: str
    confidence: float