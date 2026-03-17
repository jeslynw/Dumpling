'''
MAY OR MAY NOT IMPLEMENT IT THIS WAY

Folder Contextual Summary service.
This is NOT RAG.
It reads File.summary stored in SQLite (created from agent_ingest) and create 1-2 sentence overview.
Using stored summaries is cheaper and gives a better holistic picture than running a Qdrant retrieval query.
Example output: "You have 8 links on Tokyo travel, mostly covering food spots."
'''
from langchain_core.messages import HumanMessage
from app.services.openai import openai_llm


def generate_folder_summary(folder_name: str, file_summaries: list[str]) -> str:
    if not file_summaries:
        return f'The folder "{folder_name}" is empty.'

    summaries_text = "\n".join(f"- {s}" for s in file_summaries)

    prompt = f"""You are summarising the contents of a personal notebook folder called "{folder_name}".

    Below are short summaries of each file in the folder:
    {summaries_text}

    Write a single 1-2 sentence description of what this folder is about and what themes dominate.
    Address the user directly (e.g., "You have..."). Be concise and conversational.    
    """

    response = openai_llm.invoke([HumanMessage(content=prompt)])
    return response.content.strip()