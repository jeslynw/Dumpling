"""
LLM-powered summarisation helpers:
  - generate_document_summary   (whole-doc condensed summary for context generation)
  - generate_chunk_context      (2-3 sentence contextual prefix per chunk)
  - generate_notebook_content   (full folder synthesis for notebook content JSON)
"""
from app.services.openai import llm


def generate_document_summary(whole_document: str) -> str:
    """Condense a whole document into ~150-300 words for context generation."""
    safe_document = whole_document[:15000]
    prompt = f"""Please read the following document and provide a highly condensed, global summary (approx 150-300 words).
Focus on the core subject matter, the main entities (names, places, organizations), and the overall theme.
This summary will be used to provide context to isolated chunks of this document, so ensure the main 'Who, What, Where' is clear.

<document>
{safe_document}
</document>
"""
    response = llm.invoke(prompt)
    return response.content.strip()


def generate_chunk_context(summarized_doc: str, chunk_text: str) -> str:
    """Generate a 2-3 sentence context prefix for a single chunk (Contextual RAG)."""
    safe_doc = summarized_doc.encode("utf-8", errors="ignore").decode("utf-8").replace("\x00", "")
    safe_chunk = chunk_text.encode("utf-8", errors="ignore").decode("utf-8").replace("\x00", "")

    prompt = (
        "<summarized document>\n"
        + safe_doc
        + "\n</summarized document>\n\n"
        "Here is the chunk we want to situate within the whole document:\n"
        "<chunk>\n"
        + safe_chunk
        + "\n</chunk>\n\n"
        "Please give a short context (2-3 sentences) to situate this chunk within the overall document "
        "for the purposes of improving search retrieval. Answer ONLY with the brief context and nothing else."
    )
    response = llm.invoke(prompt)
    return response.content.strip()


def generate_notebook_content(folder_name: str, docs) -> str:
    """
    Synthesise all chunks from a folder into one detailed narrative summary.
    `docs` is a list of LangChain Document objects.
    """
    if not docs:
        return ""

    combined = "\n\n---\n\n".join(doc.page_content for doc in docs)
    safe_combined = combined[:40000].encode("utf-8", errors="ignore").decode("utf-8").replace("\x00", "")

    prompt = (
        f"You are summarizing all content stored in a personal notebook folder called '{folder_name}'.\n"
        "Below are all the text chunks stored in this folder, retrieved from the knowledge base.\n"
        "Write a single, detailed, well-structured summary (300-500 words) that covers the key topics, "
        "entities, facts, and themes across ALL the content. Do not list chunks separately — "
        "synthesize everything into one coherent narrative summary.\n\n"
        "CHUNKS:\n"
        + safe_combined
    )
    response = llm.invoke(prompt)
    return response.content.strip()
