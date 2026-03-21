import json
import re


def parse_json_response(raw_text: str) -> dict:
    """Strip markdown fences and parse JSON from LLM output."""
    text = re.sub(r"^```(?:json)?\s*", "", (raw_text or "").strip())
    text = re.sub(r"\s*```$", "", text.strip())
    try:
        return json.loads(text)
    except Exception:
        return {}
