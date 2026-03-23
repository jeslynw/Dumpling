"""
RAG Chatbot agent (ReAct, 3 tools):
  - pick_relevant_folders : reads registry, LLM picks relevant folders
  - search_folder         : Hybrid RAG + CRAG within one folder
  - search_source         : Hybrid RAG + CRAG filtered to one source

build_rag_chatbot() is called fresh per query so the registry is always current.
query_notebook()    is the public entry point.
"""
from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

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
        1. ALWAYS call pick_relevant_folders first to find which folders are relevant. It returns the folder names AND their sources list (URLs, filenames).
        2. If pick_relevant_folders returns relevant folders, call search_folder for each one.
        3. If pick_relevant_folders returns NO relevant folders, still call search_folder
        on the folder with the highest relevance — this triggers the CRAG fallback chain which
        will broaden the query, retry with larger top_k, and finally fall back to
        Tavily web search if nothing is found in the notebook.
        4. DETECT if the user is asking about a specific source. Signs include:
            - They mention a filename: "Topic 6", "GenAI slides", "nikuiku.pdf", "the Bali article"
            - They mention a URL: "the Wikipedia page", "that willflyforfood link"
            - They use phrases like: "in that document", "from that file", "that specific article",
                "in [document name]", "from [source name]"
        5. If a specific source IS mentioned:
            - The user must EXPLICITLY name or reference a specific document/URL in their question
            - Examples that qualify: "summarize the Wikipedia article", "what does topic 6 say", "from that PDF"
            - Call pick_relevant_folders to get the folder + its sources list
            - Find the best matching source string from the sources list
                (match by filename, URL domain, or keyword — pick the closest one)
            - Call search_source(query, folder_name, source) with that exact source string
            - Do NOT call search_source for every source in the folder
            - Do NOT call search_folder — search_source is more precise
        6. If NO specific source is mentioned (most queries fall here):
            - Call search_folder ONCE per relevant folder — do not loop through sources
        7. NEVER say "I couldn't find that" without calling at least one search tool first.
        8. If the answer comes from [WEB SEARCH RESULT], say so explicitly.
        9. Always cite which folder and source your answer came from.
        10. Only say "I couldn't find that in your notes." after all search tools have
        been tried and returned nothing.
        11. NEVER produce content that is harmful, offensive, discriminatory, or unethical. If the question asks for such content, respond with: "I'm sorry, I cannot help with that request." and nothing else.
        """
    )

def print_trace(response: dict) -> None:
    msgs = response.get("messages", [])
    print(f"Trace ({len(msgs)} messages)\n" + "-" * 50)
    for i, msg in enumerate(msgs):
        if isinstance(msg, HumanMessage):
            print(f"[{i}] USER       : {msg.content}")
        elif isinstance(msg, AIMessage) and msg.tool_calls:
            for tc in msg.tool_calls:
                print(f"[{i}] TOOL CALL  : {tc['name']}({tc['args']})")
        elif isinstance(msg, AIMessage):
            print(f"[{i}] FINAL ANS  : {msg.content}")
        elif isinstance(msg, ToolMessage):
            print(f"[{i}] TOOL RESP  : [{msg.name}] → {msg.content[:300]}")

def query_notebook(question: str) -> str:
    """Public entry point — builds a fresh chatbot and returns the answer string."""
    chatbot = build_rag_chatbot()
    result = chatbot.invoke({"messages": [HumanMessage(content=question)]})
    print_trace(result)
    return result["messages"][-1].content
