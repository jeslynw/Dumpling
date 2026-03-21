import importlib
import json

from app.tools.tools_categorizer import (
    suggest_folder,
    find_or_suggest_folder,
    get_folder_contents_sample,
)
from app.schemas.folder import CategorizationRequest, CategorizationResult


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


def _fallback_tool(_name: str | None = None):
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
        return _fallback_tool


def _build_react_executor(tools: list, max_iterations: int = 4):
    try:
        from app.services.openai import openai_llm

        agents_mod = importlib.import_module("langchain.agents")
        prompts_mod = importlib.import_module("langchain_core.prompts")
        AgentExecutor = getattr(agents_mod, "AgentExecutor")
        create_react_agent = getattr(agents_mod, "create_react_agent")
        PromptTemplate = getattr(prompts_mod, "PromptTemplate")

        react_prompt = PromptTemplate.from_template(
                """You are an AI Librarian organizing a personal notebook.
Your job is to decide which folder a piece of content belongs to.

You will receive input as title, summary, and content preview.

DECISION PROCESS (follow in order):
1. Call find_or_suggest_folder first using the full input fields (content, title, summary).
    It returns folder_name, is_new_folder, confidence, reason.
2. If confidence > 0.7 AND is_new_folder = false:
    - Call get_folder_contents_sample(folder_name) to verify folder fit.
    - If sample appears not to match, call find_or_suggest_folder again with the same content/title/summary.
3. If confidence <= 0.7, this is uncertain and should be treated as confirmation-needed by downstream logic.
4. If is_new_folder = true, skip verification.

CONFIDENCE GUIDE:
0.9-1.0 = clearly fits
0.7-0.9 = good match, verify first
0.5-0.7 = uncertain
< 0.5 = suggest new folder

Always return a final answer consistent with keys:
folder_name, is_new_folder, confidence, reason.
Do not invent unsupported fields.

Tools:
{tools}

Question: {input}
Thought: think about best action
Action: one of [{tool_names}]
Action Input: input for the tool
Observation: tool output
... (repeat as needed)
Thought: I now know the final answer
Final Answer: result

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


def _confidence_band(confidence: float) -> str:
    if confidence >= 0.9:
        return "clearly_fits"
    if confidence > 0.7:
        return "good_match"
    if confidence >= 0.5:
        return "uncertain"
    return "suggest_new"


def build_categorizer_agent() -> dict:
    state = {"candidate": None}
    tool_decorator = _resolve_tool_decorator()

    @tool_decorator("find_or_suggest_folder")
    def find_or_suggest_folder_tool(content: str, title: str = "", summary: str = "") -> str:
        """Suggest the best folder for note content and return JSON with confidence and reason."""
        result = find_or_suggest_folder(content=content, title=title, summary=summary)
        state["candidate"] = result
        return json.dumps(result)

    @tool_decorator("get_folder_contents_sample")
    def get_folder_contents_sample_tool(folder_name: str, limit: int = 3) -> str:
        """Return a small sample of existing chunks from a folder for verification."""
        return get_folder_contents_sample(folder_name=folder_name, limit=limit)

    tools = [find_or_suggest_folder_tool, get_folder_contents_sample_tool]
    executor = _build_react_executor(tools)

    return {
        "state": state,
        "tools": {
            "find_or_suggest_folder": find_or_suggest_folder_tool,
            "get_folder_contents_sample": get_folder_contents_sample_tool,
        },
        "executor": executor,
    }


def run_categorizer_agent(request: CategorizationRequest) -> dict:
    ctx = build_categorizer_agent()
    executor = ctx.get("executor")
    title = str((request.meta or {}).get("title", ""))
    summary = str((request.meta or {}).get("summary", ""))

    if executor is not None:
        prompt = (
            "Categorize this note into the best folder.\n"
            f"title={title}\n"
            f"summary={summary}\n"
            f"content={(request.content or '')[:2500]}"
        )
        try:
            executor.invoke({"input": prompt})
        except Exception:
            pass

    result = ctx["state"].get("candidate")
    if not result:
        result = suggest_folder(request.content, request.meta)
    return result


def categorize_note(request: CategorizationRequest) -> CategorizationResult:
    result = run_categorizer_agent(request)
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