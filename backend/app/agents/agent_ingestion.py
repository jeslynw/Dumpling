"""
Ingestion agent (ReAct, 4 tools):
  - scrape_url_tool        : web pages
  - parse_document_tool    : PDF / DOCX / PPTX / HTML via Docling
  - analyze_image_tool     : PNG / JPG / JPEG / GIF / WEBP via Vision API
  - wrap_text_tool         : plain text

build_ingestion_agent() creates a fresh agent + collected_docs per item (closure pattern).
run_ingestion_agent()   is the public entry point.
"""
import base64
import mimetypes
import os

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from app.core.constants import ALLOWED_IMAGE_CATEGORIES, OPENAI_VISION_MODEL
from app.services.openai import llm, vision_client
from app.helpers.helper_ingestion import (
    chunk_with_context,
    docling_converter,
    scrape_and_chunk,
)

import re, json


def _parse_json_response(raw_text: str) -> dict:
    text = re.sub(r"^```(?:json)?\s*", "", raw_text.strip())
    text = re.sub(r"\s*```$", "", text.strip())
    try:
        return json.loads(text)
    except Exception:
        return {}


def print_trace(response: dict) -> None:
    """Pretty-print the Thought → Action → Observation trace."""
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


def build_ingestion_agent():
    """
    Returns (agent, collected_docs).
    Create a new instance for EVERY item, never reuse across items.
    Tools are closures that write chunks to collected_docs as a side channel.
    """
    collected_docs: list = []

    @tool
    def scrape_url_tool(url: str) -> str:
        """
        Use this when the input is a web URL (starts with http:// or https://).
        Scrapes the page and returns a summary.
        """
        chunks = scrape_and_chunk(url)
        collected_docs.extend(chunks)
        if not chunks:
            return ""
        return f"Successfully scraped {len(chunks)} chunks from {url}."

    @tool
    def parse_document_tool(filepath: str) -> str:
        """
        Use this STRICTLY when the input is a document (.pdf, .docx, .doc, .pptx, .html).
        Pass the exact filepath. Docling will extract the text.
        """
        try:
            filename = os.path.basename(filepath)
            result = docling_converter.convert(filepath)
            full_text = result.document.export_to_markdown()
            if not full_text.strip():
                return f"Could not extract content from '{filename}'"
            chunks = chunk_with_context(full_text, filename=filename, input_type="document")
            collected_docs.extend(chunks)
            return f"Successfully extracted {len(chunks)} chunks from '{filename}'."
        except Exception as e:
            return f"Parsing failed for '{filepath}': {str(e)}"

    @tool
    def analyze_image_tool(filepath: str, filename: str = "") -> str:
        """
        Use this STRICTLY when the input is an image (.png, .jpg, .jpeg, .gif, .webp).
        Pass the exact filepath. Reads and encodes the image internally.
        """
        if not filename:
            filename = os.path.basename(filepath)

        mime_type, _ = mimetypes.guess_type(filepath)
        mime_type = mime_type or "image/jpeg"

        with open(filepath, "rb") as f:
            image_b64 = base64.b64encode(f.read()).decode("utf-8")

        prompt = f"""
        You are a production image classification API. Analyze the image and return STRICT JSON ONLY. No markdown.
        Tasks:
        1. Provide a concise summary (max 100 words).
        2. Generate 3-5 relevant tags.
        3. Assign ONE category from: {ALLOWED_IMAGE_CATEGORIES}

        JSON FORMAT: {{"summary": "...", "tags": ["tag1", "tag2"], "category": "category_name"}}
        """
        response = vision_client.chat.completions.create(
            model=OPENAI_VISION_MODEL,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{image_b64}"}},
                    {"type": "text", "text": prompt},
                ],
            }],
            temperature=0.1,
        )
        result_dict = _parse_json_response(response.choices[0].message.content)
        full_text = (
            f"Image Filename: {filename}\n"
            f"Category: {result_dict.get('category')}\n"
            f"Tags: {', '.join(result_dict.get('tags', []))}\n"
            f"Summary: {result_dict.get('summary')}"
        )
        chunks = chunk_with_context(full_text, filename=filename, input_type="image")
        collected_docs.extend(chunks)
        return f"Successfully analyzed image '{filename}'. Summary: {result_dict.get('summary')}"

    @tool
    def wrap_text_tool(text: str) -> str:
        """
        Use this when the input is plain text — not a URL, image, or document.
        Returns a summary for the agent to reason about.
        """
        if not text.strip():
            return ""
        chunks = chunk_with_context(text, filename="", input_type="text")
        collected_docs.extend(chunks)
        return f"Successfully processed {len(chunks)} text chunks."

    agent = create_agent(
        llm,
        tools=[scrape_url_tool, parse_document_tool, analyze_image_tool, wrap_text_tool],
        system_prompt="""\
        You are an ingestion agent for a personal notebook app.
        Your job is to extract clean, readable content from the user's input so it can be stored and searched.

        Inspect the content and filename to decide which tool to use:
        - Content starts with "http" or "https": scrape_url_tool
        - Filename ends in .pdf/.docx/.doc/.pptx/.html: parse_document_tool with the filepath
        - If parse_document_tool returns empty (scanned PDF): fall back to analyze_image_tool
        - Filename ends in .png/.jpg/.jpeg/.gif/.webp: analyze_image_tool
        - Plain text: wrap_text_tool

        Always use exactly one tool.""",
    )
    return agent, collected_docs


def _generate_title_and_summary(content: str, source_hint: str = "") -> tuple[str, str]:
    """Generate a short title and 150-word summary from the first chunk."""
    safe_content = content[:2000].encode("utf-8", errors="ignore").decode("utf-8").replace("\x00", "")
    prompt = (
        "Given this content, provide:\n"
        "TITLE: <a short descriptive title (max 8 words)>\n"
        "SUMMARY: <a 150 word summary of what this content is about>\n\n"
        "Content:\n" + safe_content
    )
    response = llm.invoke(prompt)
    raw = response.content.strip()

    title = source_hint or "Untitled"
    summary = ""

    # Extract TITLE
    title_match = re.search(r"TITLE:\s*(.+)", raw)
    if title_match:
        title = title_match.group(1).strip()

    # Extract SUMMARY, handles multiline responses
    summary_match = re.search(r"SUMMARY:\s*(.+?)(?=\nTITLE:|\Z)", raw, re.DOTALL)
    if summary_match:
        summary = " ".join(summary_match.group(1).strip().splitlines())

    # Hard fallback: use raw content if summary still empty
    if not summary:
        summary = safe_content[:300]

    return title, summary


def run_ingestion_agent(raw_content: str, filename: str = "") -> tuple[list, str, str]:
    """
    Public entry point.
    Returns (docs, title, summary).
    Creates a fresh agent per call — no state bleed between items.
    """
    agent, collected_docs = build_ingestion_agent()

    if filename and os.path.isfile(raw_content):
        agent_message = (
            f"Filename: {filename}\nFilepath: {raw_content}\n"
            "Use parse_document_tool with the filepath."
        )
    else:
        agent_message = f"Filename: {filename or 'untitled'}\nContent: {raw_content[:4000]}"

    response = agent.invoke({"messages": [HumanMessage(content=agent_message)]})
    print_trace(response)

    docs = collected_docs if collected_docs else []
    first_content = docs[0].page_content if docs else raw_content[:500]
    title, summary = _generate_title_and_summary(first_content, source_hint=filename or raw_content[:60])

    print(f"\n✅ Ingestion complete: {len(docs)} chunks, title='{title}'")
    return docs, title, summary
