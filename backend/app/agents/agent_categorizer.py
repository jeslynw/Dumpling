"""
Categorizer agent (ReAct, 2 tools):
  - find_or_suggest_folder     : single LLM call → existing or new folder
  - get_folder_contents_sample : verify a candidate folder by peeking at its chunks
"""
from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from app.core.constants import CATEGORIZER_CONFIDENCE_THRESHOLD
from app.services.openai import llm
from app.tools.tools_categorizer import find_or_suggest_folder, get_folder_contents_sample
import re, json

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
            print(f"[{i}] TOOL RESP  : [{msg.name}] → {msg.content}")


def _parse_json_response(raw_text: str) -> dict:
    text = re.sub(r"^```(?:json)?\s*", "", raw_text.strip())
    text = re.sub(r"\s*```$", "", text.strip())
    try:
        return json.loads(text)
    except Exception:
        return {}


# Module-level agent (stateless — safe to reuse) 
_categorizer_agent = create_agent(
    llm,
    tools=[find_or_suggest_folder, get_folder_contents_sample],
    system_prompt="""\
    You are an AI Librarian organizing a personal notebook.
    Your job is to decide which folder a piece of content belongs to.

    You will receive input as:
    Title: <title>
    Summary: <summary>

    DECISION PROCESS (follow in order):
    1. Call find_or_suggest_folder(content_preview) with the full input you received — always first
        - It returns: folder_name | is_new | confidence | reason
    2. If confidence > 0.7 AND is_new=false:
        - Call get_folder_contents_sample(folder_name) to verify the folder fits
        - If the sample MATCHES the content: use that folder
        - If the sample does NOT match: call find_or_suggest_folder again
        with exclude_folder='<folder_name>' to get a different suggestion
    3. If confidence <= 0.7: skip verification, set needs_confirmation=true
    4. If confidence > 0.7 AND is_new=true: skip verification, it's a new folder

    CONFIDENCE GUIDE:
    0.9-1.0 = clearly fits, assign confidently
    0.7-0.9 = good match, verify first
    0.5-0.7 = uncertain, set needs_confirmation: true
    < 0.5 = find_or_suggest_folder will suggest a new folder

    Always return a JSON object with keys:
    - folder_name (str): sanitized folder name
    - is_new_folder (bool)
    - confidence (float 0.0-1.0)
    - needs_confirmation (bool)"""
    )


def run_categorizer_agent(title: str, summary: str, source: str = "") -> dict:
    """
    Decide which folder `title`+`summary` belongs to.
    Returns: {folder_name, is_new_folder, confidence, needs_confirmation, source}
    """
    content_preview = f"Title: {title}\nSummary: {summary}"
    print(f"Categorizer input: {content_preview[:300]}")

    result = _categorizer_agent.invoke({
        "messages": [HumanMessage(content=content_preview)]
    })
    print_trace(result)
    output = result["messages"][-1].content

    try:
        parsed = _parse_json_response(output)
    except Exception:
        parsed = {}

    if "needs_confirmation" not in parsed:
        parsed["needs_confirmation"] = parsed.get("confidence", 0.0) < CATEGORIZER_CONFIDENCE_THRESHOLD

    parsed.setdefault("source", source)
    return parsed
