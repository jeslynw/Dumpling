from app.tools.tools_ragchatbot import load_folder_registry, pick_relevant_folders
from app.services.qdrant import search_qdrant

def search_rag_across_folders(query: str, top_k: int = 5) -> list[str]:
    """
    1. Load folder registry (with descriptions)
    2. Use LLM to pick relevant folders
    3. Search each folder and aggregate results
    """
    folder_registry = load_folder_registry()
    relevant_folders = pick_relevant_folders(query, folder_registry)

    all_results = []
    for folder in relevant_folders:
        results = search_qdrant(query, top_k=top_k, collection_name=folder)
        all_results.extend(results)

    # Optionally sort/limit aggregated results
    return all_results[:top_k]