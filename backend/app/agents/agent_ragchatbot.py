"""
RAG Chatbot agent (ReAct, 3 tools):
  - pick_relevant_folders : reads registry, LLM picks relevant folders
  - search_folder         : Hybrid RAG + CRAG within one folder
  - search_source         : Hybrid RAG + CRAG filtered to one source

build_rag_chatbot() is called fresh per query so the registry is always current.
query_notebook()    is the public entry point.
"""
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

from app.db.database import load_registry
from app.services.openai import llm
from app.tools.tools_ragchatbot import make_chatbot_tools


def build_rag_chatbot():
    registry = load_registry()
    folder_names = list(registry.keys())
    chatbot_tools = make_chatbot_tools()

    return create_agent(
        llm,
        tools=chatbot_tools,
        system_prompt=f"""\
        You are a helpful assistant for a personal notebook app.
        You have access to the user's saved notes, links, documents, and images.

        Available folders: {folder_names}

        INSTRUCTIONS:
        1. ALWAYS call pick_relevant_folders first to find which folders are relevant.
        2. If pick_relevant_folders returns relevant folders, call search_folder for each one.
        3. If pick_relevant_folders returns NO relevant folders, still call search_folder
        on the first available folder — this triggers the CRAG fallback chain which
        will broaden the query, retry with larger top_k, and finally fall back to
        Tavily web search if nothing is found in the notebook.
        4. If the user asks about a specific source/file, call search_source instead.
        5. NEVER say "I couldn't find that" without calling at least one search tool first.
        6. If the answer comes from [WEB SEARCH RESULT], say so explicitly.
        7. Always cite which folder and source your answer came from.
        8. Only say "I couldn't find that in your notes." after all search tools have
        been tried and returned nothing."""
    )


def query_notebook(question: str) -> str:
    """Public entry point — builds a fresh chatbot and returns the answer string."""
    chatbot = build_rag_chatbot()
    result = chatbot.invoke({"messages": [HumanMessage(content=question)]})
    return result["messages"][-1].content
