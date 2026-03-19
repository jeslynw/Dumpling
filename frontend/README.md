# Dumpling — SmartNotebook Frontend

> Next.js 14 · TypeScript · Tailwind CSS · Tiptap Editor  
> AI-powered note-taking and research companion UI

---

## Quick Start

### Prerequisites
- Node.js 18+ ([download](https://nodejs.org))
- npm 9+ (comes with Node)

---

## Setup Steps

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

```bash
cp .env.example .env.local
```

Open `.env.local` and set:

```env
# Points to your FastAPI backend (leave as-is if running locally)
NEXT_PUBLIC_API_URL=http://localhost:8000

# "true"  → use built-in mock data (no backend needed)
# "false" → make real API calls to NEXT_PUBLIC_API_URL
NEXT_PUBLIC_USE_MOCKS=true
```

> **During frontend-only development**, keep `NEXT_PUBLIC_USE_MOCKS=true`.  
> When the backend is ready, flip it to `false`.

### 3. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## Pages

| Route | Description |
|-------|-------------|
| `/` | Home — hero input, feature cards, recent documents |
| `/notes` | All notes, filterable by AI-assigned category |
| `/notes/new` | Create a new note in the Tiptap rich-text editor |
| `/notes/[id]` | Edit an existing note (auto-saves every 1.5s) |
| `/search` | AI Q&A chat powered by RAG (asks questions over your notes) |
| `/source/[id]` | Three-panel source viewer: PDF/image + AI summary + quick actions |

---

## Folder Structure

```
src/
├── app/
│   ├── page.tsx           Route "/" — Homepage
│   ├── chat/page.tsx      Route "/chat" — Chat with Bao
│   ├── notes/
│   │   ├── new/page.tsx   Route "/notes/new" — New note editor
│   │   └── [id]/page.tsx  Route "/notes/[id]" — Edit note editor
│   └── trash/page.tsx     Route "/trash" — Trash
├── components/
│   ├── layout/        AppShell, Sidebar, TopNav
│   ├── home/          HeroInput, FeatureCards
│   ├── editor/        NoteEditor (Tiptap), EditorToolbar, NoteMeta, SourcesSidebar
│   ├── qa/            NoteAIChat, ChatMessage
│   └── ui/            Spinner, EmptyState
├── lib/
│   ├── api/           All backend API calls (with mock fallback)
│   ├── mocks/         Sample data for development
│   └── types/         Shared TypeScript interfaces
└── styles/            Tiptap SCSS stubs
```

---

## Connecting the Backend (FastAPI)

All backend calls are isolated in `src/lib/api/`. Each function has a
`// TODO: BACKEND` comment showing the exact endpoint and payload.

**To connect:**
1. Set `NEXT_PUBLIC_USE_MOCKS=false` in `.env.local`
2. Set `NEXT_PUBLIC_API_URL=http://localhost:8000` (or your deployed URL)
3. Start the FastAPI server (`uvicorn backend.main:app --reload`)

### Backend Integration Checklist

| # | Endpoint | Method | Frontend consumer |
|---|----------|--------|-------------------|
| 1 | `/api/notes` | GET | RecentDocuments, Notes page |
| 2 | `/api/notes` | POST | HeroInput "Create" |
| 3 | `/api/notes/:id` | GET | Edit note page on load |
| 4 | `/api/notes/:id` | PATCH | Auto-save in editor |
| 5 | `/api/notes/:id` | DELETE | NoteCard delete button |
| 6 | `/api/categories` | GET | Sidebar category list |
| 7 | `/api/upload/image` | POST | Image upload in editor |
| 8 | `/api/upload` | POST | HeroInput file attach |
| 9 | `/api/scrape` | POST | HeroInput URL/link mode |
| 10 | `/api/search` | POST | Q&A chat page |
| 11 | `/api/search/suggestions` | GET | Chat suggestion pills |
| 12 | `/api/sources/:id` | GET | Source viewer page |
| 13 | `/api/sources/:id/summary` | GET | Source summary panel |
| 14 | `/api/sources/:id/export` | GET | Export JSON action |
| 15 | `/api/sources/:id/translate` | POST | Translate action |

---

## Logo

The sidebar currently uses a `auto_awesome` Material Symbol as a placeholder.

**To add your logo:**
1. Place your file at `public/logo.svg` (or `public/logo.png`)
2. Open `src/components/layout/Sidebar.tsx`
3. Replace the placeholder `<div>` with:

```tsx
import Image from 'next/image'
<Image src="/dumpling.png" alt="Dumpling" width={32} height={32} />
```

---

## Design Tokens

| Token | Value | Usage |
|-------|-------|-------|
| `primary` | `#ffd59e` | Buttons, active states, accents |
| `bg-light` | `#fdfcf9` | Page background |
| `warm-50–400` | `#fffbf6 → #f5e3cd` | Cards, borders, fills |

Defined in `tailwind.config.ts` and mirrored as CSS variables in `src/app/globals.css`.

---

## Build for Production

```bash
npm run build
npm run start
```

---

## Tech Stack

| Package | Purpose |
|---------|---------|
| `next@14` | App Router, SSR, routing |
| `@tiptap/react` + extensions | Rich-text note editor |
| `tailwindcss` | Utility-first styling |
| `swr` | Data fetching hooks (add as needed) |
| `clsx` | Conditional class names |

---

## SCSS Note (Tiptap)

Tiptap's `simple-editor` requires these two imports in `globals.css`:

```css
@import '../styles/_variables.scss';
@import '../styles/_keyframe-animations.scss';
```

These stub files are already in `src/styles/`. If you run `npx @tiptap/cli@latest add simple-editor` later, it will populate them with its own variables — just merge yours in.

---

*SmartNotebook / Dumpling — Frontend scaffold v0.1*
