# 📓 SmartNotebook

> An AI-powered smart notebook that automatically organizes messy text and images into structured, searchable knowledge.

SmartNotebook transforms unstructured content, such as screenshots, handwritten notes, lecture slides, random text into clean, categorized, summarized, and searchable notes using **Agentic AI + LLMs + Retrieval-Augmented Generation (RAG)**.

---

## 🚀 Overview

Problem with digital notes today are:
- Not structure, messy and scattered across topics
- Poorly categorized
- Hard to search later
- Time consuming to organize

SmartNotebook solves this by:

- 📷 Extracting text from images (OCR / image captioning)
- 📝 Summarizing long content
- 🗂 Automatically categorizing notes
- 🧠 Storing notes with semantic memory
- 🔎 Allowing contextual question answering over past notes

---

## 🧠 How It Works

SmartNotebook uses an **Agentic AI architecture**.

Instead of a fixed pipeline, an AI agent decides:
- Which tools to use
- In what order
- Whether retrieval (RAG) is needed

### 🔁 High-Level Workflow



## 🏗 Tech Stack

### Frontend
- Next.js
- Tiptap Editor

### Backend  (To be updated)
- Python 3.13
- FastAPI
- Vector Database

### AI Components
- OCR (doctr / Tesseract)
- Image Captioning Model
- LLM for Summarization & Reasoning
- Embedding Model
- Retrieval-Augmented Generation (RAG)

---

## ⚙️ Installation

---

### 1. Frontend Setup

Install Next.js: ```npx create-next-app frontend```

Inside the frontend folder, add Tiptap:
1. cd frontend
2. ```npx @tiptap/cli@latest add simple-editor```

Start frontend: ```npm run dev```

```

### 2. Backend Setup

#### Environment Setup
Create env: ```conda create -p ./env python=3.13 -y```

Activate env: ```conda activate ./env```

Install dependencies: ```pip install -r requirements.txt```

Run backend: ``` ```


