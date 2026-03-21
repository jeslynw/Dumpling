# ...existing imports...
from typing import Tuple
import json
from pathlib import Path

def suggest_folder(content: str, meta: dict) -> Tuple[str, float]:
    """
    Suggest a folder/category for the note.
    Replace this with LLM or rules-based logic.
    """
    # Example: simple keyword-based categorization
    if "finance" in content.lower():
        return "Finance", 0.9
    elif "health" in content.lower():
        return "Health", 0.85
    else:
        return "General", 0.5
    
def update_folder_registry(folder: str, meta_path: str = "backend/data/qdrant_db/meta.json"):
    meta_file = Path(meta_path)
    if meta_file.exists():
        with open(meta_file, "r") as f:
            data = json.load(f)
    else:
        data = {}
    data.setdefault("folders", []).append(folder)
    with open(meta_file, "w") as f:
        json.dump(data, f, indent=2)