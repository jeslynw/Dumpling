# 🥟 Dumpling | Smart Notebook

> An AI-powered smart notebook that automatically organizes, categorizes, and retrieves unstructured content using Agentic AI, LLMs, and Retrieval-Augmented Generation (RAG).

## 🚀 Overview
Managing notes and saved content is messy, URLs, PDFs, images, and plain text scattered across topics with no structure. Dumpling solves this by automatically ingesting, categorizing, and making all your content queryable.

## 🏛️ Architecture Flow
<img width="2073" height="1085" alt="agentic_flow1" src="https://github.com/user-attachments/assets/95d5fb0a-a09f-4849-be2c-b9b4ef60a987" />

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

### Environment Setup
- **Create env**: ```conda create -p ./env python=3.13.5 -y```

- **Activate env**: ```conda activate ./env```

- **Install dependencies**: ```pip install -r requirements.txt```

---

**Run backend**: ```uvicorn main:app --reload --port 8000```

**Start frontend**: ```npm run dev```

---

## How Dumpling Looks Like
<img width="2877" height="1699" alt="1_homepage" src="https://github.com/user-attachments/assets/dca37d35-7dbd-4093-8cf2-85e406cc5901" />
<img width="1919" height="1124" alt="2_folder" src="https://github.com/user-attachments/assets/67f42e6e-a4b0-4711-a131-91ffda5dd944" />
<img width="1919" height="1124" alt="3_smallbao" src="https://github.com/user-attachments/assets/76cccf9c-9faf-41b1-928c-0c0a5ba346db" /><img width="1919" height="1125" alt="4_bao" src="https://github.com/user-attachments/assets/dfe5cdc2-fdcb-4742-926b-6fd355df2246" />

