import json
from app.services.openai import openai_llm

def load_folder_registry(meta_path: str = "backend/data/qdrant_db/meta.json") -> dict:
    with open(meta_path, "r") as f:
        return json.load(f).get("folders", {})

def pick_relevant_folders(query: str, folder_registry: dict) -> list[str]:
    """
    Use LLM to select relevant folders for the query, based on descriptions.
    """
    prompt = (
        "Given the following user query and folder descriptions, "
        "list the folders most relevant to answer the query.\n\n"
        f"Query: {query}\n\n"
        "Folders:\n"
    )
    for name, meta in folder_registry.items():
        prompt += f"- {name}: {meta.get('description', '')}\n"
    prompt += "\nReturn a comma-separated list of folder names."

    resp = openai_llm.invoke(prompt)
    return [f.strip() for f in resp.content.split(",") if f.strip()]