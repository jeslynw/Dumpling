from pathlib import Path
from typing import List, Tuple, Dict, Any
import importlib

from app.services.openai import openai_llm
from app.tools.tools_ingestion import (
    scrape_and_chunk,
    parse_document,
    analyze_image,
    wrap_text,
)
from app.agents.agent_categorizer import categorize_note
from app.schemas.folder import CategorizationRequest

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".jfif"}
DOC_EXTS = {".pdf", ".docx", ".doc", ".pptx", ".html", ".htm", ".md", ".txt"}


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


def _build_react_executor(tools: list[Any], max_iterations: int = 4):
    try:
        agents_mod = importlib.import_module("langchain.agents")
        prompts_mod = importlib.import_module("langchain_core.prompts")
        AgentExecutor = getattr(agents_mod, "AgentExecutor")
        create_react_agent = getattr(agents_mod, "create_react_agent")
        PromptTemplate = getattr(prompts_mod, "PromptTemplate")

        react_prompt = PromptTemplate.from_template(
            """You are an ingestion agent for a notebook system.
Choose tools to extract content based on input type.
- URL -> scrape_url
- Document/image local filepath -> parse_document_and_image
- Plain text -> wrap_text
Call at least one tool before giving final answer.

You have access to the following tools:
{tools}

Use this format:
Question: {input}
Thought: think about what to do
Action: one of [{tool_names}]
Action Input: the tool input
Observation: tool result
... (repeat Thought/Action/Action Input/Observation as needed)
Thought: I now know the final answer
Final Answer: concise summary

{agent_scratchpad}"""
        )

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


def _is_url(text: str) -> bool:
    t = (text or "").strip().lower()
    return t.startswith("http://") or t.startswith("https://")


def _detect_input_type(raw_content: str, filename: str = "") -> str:
    """
    Returns one of: url | image | document | text
    """
    if _is_url(raw_content):
        return "url"

    # If raw_content is a local file path, use that extension
    if raw_content and Path(raw_content).exists():
        ext = Path(raw_content).suffix.lower()
        if ext in IMAGE_EXTS:
            return "image"
        if ext in DOC_EXTS:
            return "document"

    # Otherwise use filename hint
    ext = Path(filename).suffix.lower() if filename else ""
    if ext in IMAGE_EXTS:
        return "image"
    if ext in DOC_EXTS:
        return "document"

    return "text"


def _generate_title_and_summary(content: str, source_hint: str = "") -> Tuple[str, str]:
    safe_content = (content or "")[:2500].encode("utf-8", errors="ignore").decode("utf-8").replace("\x00", "")

    prompt = (
        "Given this content, provide exactly:\n"
        "TITLE: <short descriptive title, max 8 words>\n"
        "SUMMARY: <about 120-180 words>\n\n"
        f"Content:\n{safe_content}"
    )

    resp = openai_llm.invoke(prompt)
    text = (resp.content or "").strip()

    title = source_hint.strip() if source_hint else "Untitled"
    summary = ""

    for line in text.splitlines():
        if line.startswith("TITLE:"):
            title = line.replace("TITLE:", "", 1).strip() or title
        elif line.startswith("SUMMARY:"):
            summary = line.replace("SUMMARY:", "", 1).strip()

    if not summary:
        summary = "No summary available."

    return title, summary


def run_ingestion_agent(raw_content: str, filename: str = "") -> Tuple[List[Any], str, str, Dict[str, Any]]:
    """Notebook-style ingestion runner. Returns: (docs, title, summary, categorization)."""
    agent_ctx = build_ingestion_agent()
    tools = agent_ctx["tools"]
    executor = agent_ctx.get("executor")

    if executor is not None:
        preview = (raw_content or "")[:3500]
        query = (
            "Ingest this input into notebook chunks. "
            "Use the proper tool based on type.\n"
            f"filename={filename or 'none'}\n"
            f"raw_content={preview}"
        )
        try:
            executor.invoke({"input": query})
        except Exception:
            # Fall back to deterministic dispatch if ReAct run fails.
            pass

    if not agent_ctx["collected_docs"]:
        input_type = _detect_input_type(raw_content=raw_content, filename=filename)
        if input_type == "url":
            tools["scrape_url"].invoke({"url": raw_content})
        elif input_type in {"document", "image"}:
            filepath = raw_content if Path(raw_content).exists() else filename
            tools["parse_document_and_image"].invoke({"filepath": filepath})
        else:
            tools["wrap_text"].invoke({"text": raw_content})

    docs = agent_ctx["collected_docs"]

    first_content = docs[0].page_content if docs else (raw_content or "")[:600]
    source_hint = filename or (raw_content[:60] if raw_content else "Untitled")
    title, summary = _generate_title_and_summary(first_content, source_hint=source_hint)
    # --- Categorizer integration ---
    cat_request = CategorizationRequest(content=first_content, meta={"filename": filename})
    cat_result = categorize_note(cat_request)
    categorization = {
        "folder_name": cat_result.folder_name,
        "is_new_folder": cat_result.is_new_folder,
        "confidence": cat_result.confidence,
        "reason": cat_result.reason,
        "needs_confirmation": cat_result.needs_confirmation,
        "confidence_band": cat_result.confidence_band,
        "verification_required": cat_result.verification_required,
        "action": cat_result.action,
    }

    return docs, title, summary, categorization


def build_ingestion_agent() -> Dict[str, Any]:
    """
    Build a fresh ingestion context with closure tools.
    This mirrors notebook behavior while preserving backend contracts.
    """
    collected_docs: List[Any] = []
    tool_decorator = _resolve_tool_decorator()

    @tool_decorator("scrape_url")
    def scrape_url_tool(url: str) -> str:
        """Use this when the input is a web URL (http/https)."""
        chunks = scrape_and_chunk(url)
        collected_docs.extend(chunks)
        if not chunks:
            return ""
        joined = "\n\n".join(c.page_content for c in chunks)[:8000]
        return (openai_llm.invoke(f"Summarize in 3-5 sentences:\n\n{joined}").content or "").strip()

    @tool_decorator("parse_document_and_image")
    def parse_document_and_image_tool(filepath: str) -> str:
        """Use this when input is a local document/image path for parsing and contextual chunking."""
        path = Path(filepath)
        if not path.exists():
            return f"File not found: {filepath}"

        ext = path.suffix.lower()
        try:
            if ext in IMAGE_EXTS:
                chunks = analyze_image(str(path))
            else:
                chunks = parse_document(str(path))
            collected_docs.extend(chunks)
            if not chunks:
                return f"Could not extract content from '{path.name}'"
            joined = "\n\n".join(c.page_content for c in chunks)[:8000]
            return (openai_llm.invoke(f"Summarize in 3-5 sentences:\n\n{joined}").content or "").strip()
        except Exception as exc:
            return f"Parsing failed for '{filepath}': {exc}"

    @tool_decorator("wrap_text")
    def wrap_text_tool(text: str) -> str:
        """Use this when the input is plain text."""
        chunks = wrap_text(text)
        collected_docs.extend(chunks)
        if not chunks:
            return ""
        joined = "\n\n".join(c.page_content for c in chunks)[:8000]
        return (openai_llm.invoke(f"Summarize in 3-5 sentences:\n\n{joined}").content or "").strip()

    tools_list = [scrape_url_tool, parse_document_and_image_tool, wrap_text_tool]
    executor = _build_react_executor(tools_list)

    return {
        "collected_docs": collected_docs,
        "executor": executor,
        "tools": {
            "scrape_url": scrape_url_tool,
            "parse_document_and_image": parse_document_and_image_tool,
            "wrap_text": wrap_text_tool,
        },
    }