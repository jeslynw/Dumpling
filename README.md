# 📓 SmartNotebook (To be updated)

> An AI-powered smart notebook that automatically organizes messy text and images into structured, searchable knowledge.

SmartNotebook addresses the problem of unstructured content using **Agentic AI + LLMs + Retrieval-Augmented Generation (RAG)**.

---

## 🚀 Overview

Current notes and content suffer from:
- Unstructured, messy, and scattered across topics  
- Poorly categorized  
- Hard to find or search  
- Time-consuming to organize and review  

SmartNotebook solves this by:
- 📷 Extracting text from images
- 📝 Summarizing long content
- 🗂 Automatically categorizing notes
- 🧠 Storing notes with semantic memory
- 🔎 Allowing contextual question answering over past notes

---

## 🧠 How It Works

- **Content Ingestion** — Paste text, upload PDFs/images/URLs, or use the homepage hero input. Files are processed by the Ingestion Agent, which extracts text and metadata.
- **AI Categorisation** — The Categorisation Agent automatically assigns tags and categories to each note using an LLM, keeping your knowledge base organised without manual effort.
- **Semantic Search** — Notes and attachments are embedded into a vector database (Qdrant). The RAG pipeline retrieves the most relevant chunks to answer your questions accurately.
- **Ask Dumpling AI (Global Chat)** — The `/chat` page lets you ask anything across your entire knowledge base. The AI searches all notes and returns an answer with source references.
- **Note-Scoped Chat** — Inside any note editor, the floating "Chat with Bao" panel lets you query just that note's content using the same RAG backend, scoped by `context_note_ids`.

---

## 🔁 High-Level Workflow

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
- **Multimodal LLM** - summarizes and classifies images and links  
- **Retrieval-Augmented Generation (RAG)**

### Web Scraping

---

## ⚙️ Installation

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

**Run backend**: ``` ```


