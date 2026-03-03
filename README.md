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

---

## 🔁 High-Level Workflow

---

## 🏗 Tech Stack

### Frontend
- Next.js
- Tiptap Editor

### Backend
- Python 3.13
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

**Add the following imports in `./src/app`**:
- @import '../styles/_variables.scss';
- @import '../styles/_keyframe-animations.scss';


**Start frontend**: ```npm run dev```


### 2. Backend Setup

#### Environment Setup
- **Create env**: ```conda create -p ./env python=3.13 -y```

- **Activate env**: ```conda activate ./env```

- **Install dependencies**: ```pip install -r requirements.txt```

**Run backend**: ``` ```


