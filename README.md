# 🥟 Dumpling | Smart Notebook

> An AI-powered smart notebook that automatically organizes, categorizes, and retrieves unstructured content using Agentic AI, LLMs, and Retrieval-Augmented Generation (RAG).

## 🚀 Overview
Managing notes and saved content is messy, URLs, PDFs, images, and plain text scattered across topics with no structure. Dumpling solves this by automatically ingesting, categorizing, and making all your content queryable.

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
| LLM (main) | OpenAI `gpt-4o-mini` (API from https://openai.com/api/) |
| LLM for alt flow 2 (chatbot) | Groq `llama-3.3-70b-versatile` (API from https://console.groq.com/landing/llama-api) |
| Embeddings | OpenAI `text-embedding-3-small` (API from https://openai.com/api/) |
| Reranker | `cross-encoder/ms-marco-MiniLM-L-6-v2` (API from https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2) |
| Document parsing | Docling (PDF, DOCX, PPTX, HTML, images, OCR) (API from https://www.docling.ai/) |
| Web search | Tavily (API from https://www.tavily.com/) |
| RAG framework | LangChain |
| Vector Database | Qdrant (API from https://qdrant.tech/documentation/interfaces/) |

---

## ⚙️ Installation
### Prerequisites
- Conda
- Node.js 18+
- OpenAI API key
- Groq API key
- Tavily API key  
---

### 1. Backend Setup

#### Environment Setup
- **Create env**: ```conda create -p ./env python=3.13.5 -y```

- **Activate env**: ```conda activate ./env```

- **Install dependencies**: ```pip install -r requirements.txt```

**Run backend**: ```uvicorn main:app --reload --port 8000```


### 2. Frontend

**Start frontend**: ```npm run dev```
