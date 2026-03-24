# 🥟 Dumpling | Smart Notebook

> An AI-powered smart notebook that automatically organizes, categorizes, and retrieves unstructured content using Agentic AI, LLMs, and Retrieval-Augmented Generation (RAG).

---

## 🚀 Overview
Managing notes and saved content is messy, URLs, PDFs, images, and plain text scattered across topics with no structure. Dumpling solves this by automatically ingesting, categorizing, and making all your content queryable.

**The problem:**
- Unstructured, messy, and scattered across topics  
- People tend to dump important sources and not organize them.
- Finding specific information across many saved items is time-consuming

**Dumpling solves this by:**
- 📄 Extracts text from PDFs, DOCX, PPTX, and images
- 🌐 Scrapes web URLs
- 🗂️ Automatically categorizes content into folders
- 🔎 Answers domain specific question over your saved content
- ✅ Self-evaluates answers for hallucinations

---

## 🧠 How It Works
Dumpling is built with 3 agentics AI
### Ingestion Agent
Accepts messy multi-type input (URLs, file paths, plain text) in a single textbox. An LLM first parses the input into individual items, then a ReAct agent picks the right tool for each:
- `scrape_url_tool`: Fetches web pages via WebBaseLoader
- `parse_document_tool`: Extracts text from PDF, DOCX, PPTX, HTML, and images via Docling
- `analyze_image_tool`: Analyze image from PNG / JPG / JPEG / GIF / WEBP via Vision API 
- `wrap_text_tool`: Processes plain text directly

Every chunk is enriched with a 2–3 sentence LLM-generated context before storage (Contextual RAG), improving retrieval accuracy.

### Categorizer Agent
Takes the title and summary from the Ingestion Agent and decides which folder the content belongs to. Uses two tools:
- `find_or_suggest_folder`: Reads the folder registry and matches content to an existing folder or proposes a new one
- `get_folder_contents_sample`: Peeks at existing folder contents to verify the match

Results are stored in Qdrant and the folder registry is updated with an LLM-generated description.

### RAG Chatbot Agent
Answer user query uses three tools:
- `pick_relevant_folders`: Picks which folder is relevant to the user’s question
- `search_folder`: Search within a specific folder using Hybrid RAG + CRAG
- `search_source`: Search within a specific source (URL or filename) inside a folder.
  
Answers are retrieved by a Hybrid RAG:
- **Dense retrieval**: Qdrant semantic search (OpenAI `text-embedding-3-small`)
- **Sparse retrieval**: BM25 keyword search
- **Fusion**: Reciprocal Rank Fusion (RRF)
- **Reranking**: CrossEncoder (`ms-marco-MiniLM-L-6-v2`)
- **CRAG fallback**: if retrieved chunks are not relevant, the agent broadens the query, retries with a larger top-K, and finally falls back to Tavily web search

### Critic-Eval Agent
Wraps the RAG Chatbot Agent and acts as a quality gate. Evaluates every derived answer for hallucination using LLM-as-a-judge. If the faithfulness score falls below the threshold, it regenerates the answer with a refined prompt and re-evaluates, up to a configurable maximum number of retries. Answers sourced from Tavily web search bypass the critic.
Uses these tools:
`get_full_chunks_from_qdrant`: Retrieve the full chunks from Qdrant for the searched folders as the grounding truth context for judge evaluation.
`judge_answer`: Evaluate whether the generated answer is grounded
`regenerate_answer`: Re-runs the RAG Chatbot Agent with a refined prompt when score falls below threshold

---

## 🏗 Tech Stack

### Frontend
- Next.js 16 (App Router)
- TypeScript (strict)
- Tailwind CSS v3
- TipTap v2 (rich-text editor)

### Backend
- Python 3.13.5
- FastAPI
- Vector Database (Qdrant)

### AI Components
| Component | Model / Library |
|---|---|
| LLM (main) | OpenAI `gpt-4o-mini` |
| LLM for alt flow 2 (chatbot) | Groq `llama-3.3-70b-versatile` |
| Embeddings | OpenAI `text-embedding-3-small` |
| Reranker | `cross-encoder/ms-marco-MiniLM-L-6-v2` |
| Document parsing | Docling (PDF, DOCX, PPTX, HTML, images, OCR) |
| Web search | Tavily |
| RAG framework | LangChain / LangGraph |
| Vector Database | Qdrant |

---

## ⚙️ Installation
### Prerequisites
- Conda
- Node.js 18+
- OpenAI API key
- Groq API key
- Tavily API key  
---

### 1. Frontend Setup

**Install Next.js**: ```npx create-next-app frontend```

**Inside the frontend folder, install Tiptap**: ```npx @tiptap/cli@latest add simple-editor```

**Add the following imports in `./src/app/globals.css`**:
- @import '../styles/_variables.scss';
- @import '../styles/_keyframe-animations.scss';

**Copy environment variables**: ```cp .env.example .env.local```

Pages live in `src/` as named components (`HomePage.tsx`, `ChatPage.tsx`, `NewNotePage.tsx`, `EditNotePage.tsx`, `TrashPage.tsx`). The `src/app/` directories contain one-line re-export wrappers required by Next.js App Router.

**Start frontend**: ```npm run dev```


### 2. Backend Setup

#### Environment Setup
- **Create env**: ```conda create -p ./env python=3.13.5 -y```

- **Activate env**: ```conda activate ./env```

- **Install dependencies**: ```pip install -r requirements.txt```

**Run backend**: ```uvicorn main:app --reload --port 8000```
