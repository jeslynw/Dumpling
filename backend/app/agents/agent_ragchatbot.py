from app.tools.tools_ragchatbot import (
    load_folder_registry,
    pick_relevant_folders,
    search_folder,
    search_folder_rows,
    search_source,
    search_source_rows,
)
from app.services.qdrant import get_existing_collections
from app.services.openai import openai_llm
from app.core.config import RAG_TOP_K_EVAL, TAVILY_API_KEY
import importlib


class _ToolWrapper:
    def __init__(self, fn):
        self._fn = fn
        self.name = fn.__name__
        self.description = (fn.__doc__ or "").strip()

    def invoke(self, payload):
        if isinstance(payload, dict):
            return self._fn(**payload)
        return self._fn(payload)

    def __call__(self, *args, **kwargs):
        return self._fn(*args, **kwargs)


def tool(_name: str | None = None):
    def decorator(fn):
        wrapped = _ToolWrapper(fn)
        if _name:
            wrapped.name = _name
        return wrapped

    return decorator


def _resolve_tool_decorator():
    try:
        tools_mod = importlib.import_module("langchain_core.tools")
        return getattr(tools_mod, "tool")
    except Exception:
        return tool


def _build_react_executor(tools: list, folder_names: list[str] | None = None, max_iterations: int = 5):
    try:
        agents_mod = importlib.import_module("langchain.agents")
        prompts_mod = importlib.import_module("langchain_core.prompts")
        AgentExecutor = getattr(agents_mod, "AgentExecutor")
        create_react_agent = getattr(agents_mod, "create_react_agent")
        PromptTemplate = getattr(prompts_mod, "PromptTemplate")

        folder_names_text = ", ".join(folder_names or [])
        if not folder_names_text:
            folder_names_text = "(none)"

        react_prompt = PromptTemplate.from_template(
            """You are a helpful assistant for a personal notebook app.
You have access to the user's saved notes, links, documents, and images.

Available folders: {folder_names}

INSTRUCTIONS:
1. ALWAYS call pick_relevant_folders first to find which folders are relevant
2. If pick_relevant_folders returns relevant folders, call search_folder for each one
3. If pick_relevant_folders returns NO relevant folders, still call search_folder
   on the first available folder - this triggers the CRAG fallback chain which
   will broaden the query, retry with larger top_k, and finally fall back to
   Tavily web search if nothing is found in the notebook
4. If the user asks about a specific source/file, call search_source instead
5. NEVER say "I couldn't find that" without calling at least one search tool first
6. If the answer comes from [WEB SEARCH RESULT], say so explicitly
7. Always cite which folder and source your answer came from
8. Only say "I couldn't find that in your notes." after all search tools have
   been tried and returned nothing

Tools:
{tools}

Question: {input}
Thought: think about next step
Action: one of [{tool_names}]
Action Input: the tool input
Observation: tool output
... (repeat as needed)
Thought: I now know the final answer
Final Answer: concise answer with supporting evidence

{agent_scratchpad}"""
    ).partial(folder_names=folder_names_text)
        agent = create_react_agent(openai_llm, tools, react_prompt)
        return AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=False,
            handle_parsing_errors=True,
            max_iterations=max_iterations,
        )
    except Exception:
        return None


def _grade_chunks(question: str, results: list[dict]) -> bool:
    """
    True if any top chunks are relevant to the user question.
    Matches notebook CRAG behavior in simplified backend form.
    """
    if not results:
        return False

    for item in results[:3]:
        chunk = (item.get("text") or "")[:500]
        prompt = (
            "You are a grader assessing whether a retrieved document chunk is relevant to the user's question.\n"
            "Return ONLY JSON: {\"relevant\": true or false, \"reason\": \"brief reason\"}.\n"
            "Be lenient: mark relevant if the chunk has ANY useful signal.\n\n"
            f"Question: {question}\n\nChunk:\n{chunk}"
        )
        try:
            resp = openai_llm.invoke(prompt)
            text = (resp.content or "").strip().lower()
            if '"relevant": true' in text or "'relevant': true" in text:
                return True
            if '"relevant": false' in text or "'relevant': false" in text:
                continue
            # If model deviates from strict JSON, keep behavior lenient.
            if "yes" in text or "relevant" in text:
                return True
        except Exception:
            # Keep notebook's lenient default-on-error behavior.
            return True

    return False


def _broaden_query(question: str) -> str:
    prompt = (
        "The following search query failed to find relevant results. "
        "Rewrite it as a broader, more general question that might find related information. "
        "Return ONLY the rewritten question, nothing else.\n\n"
        f"Original question: {question}"
    )
    resp = openai_llm.invoke(prompt)
    broader = (resp.content or "").strip()
    return broader or question


def _retrieve_across_folders(query: str, folders: list[str], top_k: int) -> list[dict]:
    all_results = []
    for folder in folders:
        all_results.extend(search_folder_rows(query=query, folder_name=folder, top_k=top_k))
    return all_results[:top_k]


def _tavily_search(question: str) -> list[dict]:
    if not TAVILY_API_KEY:
        return []
    try:
        import importlib

        tavily_mod = importlib.import_module("langchain_community.tools.tavily_search")
        TavilySearchResults = getattr(tavily_mod, "TavilySearchResults")

        tavily = TavilySearchResults(max_results=3, tavily_api_key=TAVILY_API_KEY)
        results = tavily.invoke(question)

        web_docs = []
        for r in results:
            content = f"[WEB SEARCH RESULT: not from your notebook]\n{r.get('content', '')}"
            web_docs.append(
                {
                    "text": content,
                    "source": r.get("url", "web"),
                    "collection": "web_search",
                }
            )
        return web_docs
    except Exception:
        return []

def search_rag_across_folders(query: str, top_k: int = 5) -> dict:
    return query_notebook(query=query, top_k=top_k)


def make_chatbot_tools(folder_registry: dict, existing: set[str], top_k: int = 5) -> dict:
    """Create notebook-style chatbot tools and mutable per-query state."""
    state = {"relevant_folders": [], "results": []}
    tool_decorator = _resolve_tool_decorator()

    @tool_decorator("pick_relevant_folders")
    def pick_relevant_folders_tool(question: str) -> str:
        """Pick comma-separated relevant notebook folders for a question."""
        folders = pick_relevant_folders(question, folder_registry)
        valid = [f for f in folders if f in existing]
        if not valid:
            valid = list(existing)
        state["relevant_folders"] = valid
        return ", ".join(valid)

    @tool_decorator("search_folder")
    def search_folder_tool(question: str, folder_name: str) -> str:
        """Search one folder and return compact text context."""
        rows = search_folder_rows(question, folder_name=folder_name, top_k=top_k)
        state["results"].extend(rows)
        return search_folder(question, folder_name=folder_name, top_k=top_k)

    @tool_decorator("search_source")
    def search_source_tool(question: str, folder_name: str, source: str) -> str:
        """Search one specific source/file inside a folder."""
        rows = search_source_rows(question, folder_name=folder_name, source=source, top_k=top_k)
        state["results"].extend(rows)
        return search_source(question, folder_name=folder_name, source=source, top_k=top_k)

    tools = [pick_relevant_folders_tool, search_folder_tool, search_source_tool]
    return {
        "state": state,
        "tool_list": tools,
        "tools": {
            "pick_relevant_folders": pick_relevant_folders_tool,
            "search_folder": search_folder_tool,
            "search_source": search_source_tool,
        },
    }


def build_rag_chatbot(top_k: int = 5) -> dict:
    """Build notebook-style chatbot tools as a fresh context per query."""
    folder_registry = load_folder_registry()
    existing = set(get_existing_collections())
    tools_ctx = make_chatbot_tools(folder_registry=folder_registry, existing=existing, top_k=top_k)
    executor = _build_react_executor(tools_ctx["tool_list"], folder_names=sorted(existing))

    return {
        "top_k": top_k,
        "folder_registry": folder_registry,
        "existing": existing,
        "state": tools_ctx["state"],
        "executor": executor,
        "tools": tools_ctx["tools"],
    }


def query_notebook(query: str, top_k: int = 5) -> dict:
    """
    Query runner with folder picking, hybrid retrieval, and CRAG backups.
    """
    chatbot = build_rag_chatbot(top_k=top_k)
    folder_registry = chatbot["folder_registry"]
    existing = chatbot["existing"]
    executor = chatbot.get("executor")

    if executor is not None:
        try:
            executor.invoke(
                {
                    "input": (
                        "Answer this notebook question using tools. "
                        "Call pick_relevant_folders first, then search_folder for likely folders. "
                        f"Question: {query}"
                    )
                }
            )
        except Exception:
            pass

    relevant_folders = chatbot["state"].get("relevant_folders") or pick_relevant_folders(query, folder_registry)
    relevant_folders = [f for f in relevant_folders if f in existing]

    # Fallback to all existing collections if LLM returns nothing valid.
    if not relevant_folders:
        relevant_folders = list(existing)

    # CRAG step 1: initial retrieval
    limited = chatbot["state"].get("results", [])[:top_k]
    if not limited:
        limited = _retrieve_across_folders(query, relevant_folders, top_k)
    had_notebook_hits = bool(limited)

    # CRAG backup 1: broaden query and retry
    if not _grade_chunks(query, limited):
        broader = _broaden_query(query)
        limited = _retrieve_across_folders(broader, relevant_folders, top_k)
        had_notebook_hits = had_notebook_hits or bool(limited)

        # CRAG backup 2: larger k retrieval
        if not _grade_chunks(query, limited):
            larger_k = max(top_k * 3, RAG_TOP_K_EVAL)
            limited = _retrieve_across_folders(broader, relevant_folders, larger_k)
            limited = limited[:top_k]
            had_notebook_hits = had_notebook_hits or bool(limited)

            # CRAG backup 3: Tavily web fallback
            if not _grade_chunks(query, limited):
                # Keep notebook-first behavior: only use web fallback when no notebook hits exist.
                if not had_notebook_hits:
                    web = _tavily_search(query)
                    if web:
                        limited = web

    if not limited:
        return {
            "answer": "I could not find relevant notes for this query.",
            "sources": [],
        }

    context = "\n\n".join(r.get("text", "") for r in limited)
    prompt = (
        "Answer the user question using only the provided context. "
        "If the context is insufficient, say so briefly.\n\n"
        f"QUESTION:\n{query}\n\n"
        f"CONTEXT:\n{context}"
    )
    response = openai_llm.invoke(prompt)
    answer = (response.content or "").strip()

    sources = [
        {
            "source": r.get("source", "unknown"),
            "collection": r.get("collection", "unknown"),
        }
        for r in limited
    ]

    return {
        "answer": answer,
        "sources": sources,
    }