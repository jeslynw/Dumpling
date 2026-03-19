# Dumpling Frontend — CLAUDE.md

Complete reference for the frontend codebase. Every file is documented here so future sessions can orient quickly without re-exploring.

---

## Project Overview

**Dumpling** is an AI-powered smart notebook. Users dump content (text, URLs, PDFs, images) and the app automatically organises, indexes, and connects that knowledge using a Hybrid RAG + Multi-Agent AI backend. The frontend is fully scaffolded with mock data so it works without a running backend.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | Next.js 16.2, App Router |
| Language | TypeScript (strict) |
| UI | React 18, Tailwind CSS v3 |
| Rich Text | TipTap v2 (StarterKit + extensions) |
| Data Fetching | native `fetch` via custom `apiFetch` wrapper |
| Fonts | DM Serif Display, DM Sans, JetBrains Mono, Material Symbols Outlined (Google Fonts) |
| Styles | Tailwind + global CSS + SCSS partials for TipTap vars/animations |

---

## Environment Variables

Copy `.env.example` to `.env.local`:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
# Backend FastAPI base URL. Used by apiFetch in src/lib/api/client.ts.

NEXT_PUBLIC_USE_MOCKS=true
# Set to "false" when the FastAPI backend is running.
# When "true", all API calls return mock data (no network requests to backend).
```

---

## Directory Structure

```
frontend/
├── public/
│   └── dumpling.png           # Favicon / app icon
├── src/
│   ├── app/                   # Next.js App Router
│   │   ├── globals.css        # Global styles (fonts, theme vars, TipTap, animations)
│   │   ├── layout.tsx         # Root HTML shell, metadata, Google Fonts link
│   │   ├── page.tsx           # Route "/" — Homepage (Server Component)
│   │   ├── notes/
│   │   │   ├── new/page.tsx   # Route "/notes/new" — New note editor (Client Component)
│   │   │   └── [id]/page.tsx  # Route "/notes/[id]" — Edit note editor (Client Component)
│   │   ├── chat/page.tsx      # Route "/chat" — Chat with Bao (Client Component)
│   │   └── trash/page.tsx     # Route "/trash" — Trash (Client Component)
│   ├── components/
│   │   ├── editor/            # Note editor and related UI
│   │   ├── home/              # Homepage-specific components
│   │   ├── layout/            # App shell, sidebar, top nav
│   │   ├── qa/                # AI chat components
│   │   └── ui/                # Generic reusable UI primitives
│   ├── lib/
│   │   ├── api/               # All API calls (with mock fallbacks)
│   │   ├── mocks/             # Mock data for development
│   │   └── types/             # Shared TypeScript interfaces
│   └── styles/                # SCSS partials imported by globals.css
├── .env.example               # Environment variable template
├── next.config.mjs            # Next.js config
├── postcss.config.js          # PostCSS (Tailwind + autoprefixer)
├── tailwind.config.ts         # Tailwind theme (colors, fonts, shadows, animations)
└── tsconfig.json              # TypeScript config with @/* path alias
```

---

## Pages / Routes

### `src/app/layout.tsx` — Root Layout
- Sets HTML `<html lang="en">` wrapper.
- Defines `metadata` (title `"Dumpling | Smart Notebook"`, description, favicon).
- Loads **Material Symbols Outlined** variable font via a `<link>` in `<head>` (not `next/font`, because it's a variable icon font).
- No layout chrome here — `AppShell` handles sidebar/nav inside each page.

---

### `src/app/globals.css` — Global Styles
Large CSS file that covers:
- **Google Fonts** imports: DM Serif Display (`--font-display`), DM Sans (`--font-body`), JetBrains Mono (`--font-mono`), Material Symbols.
- **CSS custom properties** on `:root` for `--primary`, `--primary-dark`, `--bg-light`, `--bg-card`, `--text-primary`, `--text-secondary`, `--border-subtle`, `--shadow-warm`.
- **Material Symbols** helper classes (`.material-symbols-outlined`).
- **Scrollbar** thin-style overrides.
- **Stagger animation** utility classes (`.stagger-2`, `.stagger-3`, etc.) for `animation-delay` on homepage cards.
- **Shimmer** skeleton keyframe for loading states.
- **TipTap editor** base styles (`.tiptap-editor` prose, headings, lists, blockquote, code blocks, image, links, placeholder text).
- **Warm grain** SVG overlay effect (`.warm-grain`).
- **Chat bubble** entry animation (`.chat-bubble-enter`) and **typing dots** (`.typing-dot`).

---

### `src/app/page.tsx` — Homepage (`/`)
- Server Component.
- Wraps content in `<AppShell>`.
- Renders:
  1. Animated hero badge + headline ("Dump Here, Sort Later") + subtitle.
  2. `<HeroInput />` — the main content-ingestion widget.
  3. `<FeatureCards />` — four AI feature cards.
- Uses `animate-fade-up` + `stagger-*` classes for staggered entrance animations.

---

### `src/app/notes/new/page.tsx` — New Note (`/notes/new`)
Client Component (`"use client"`).

**State:** `note` (partial Note), `saving`, `savedId` (null until first save), `activeAttId`, `saveTimer` ref.

**Key behavior:**
- On first content/title change, calls `createNote()` → sets `savedId`.
- Subsequent changes call `updateNote(savedId, patch)`.
- Auto-save debounce: 1 500 ms (`scheduleAutoSave` → `setTimeout` → `persist`).
- Attachment add creates optimistic local `Attachment` objects (real upload TODO).
- Renders `SourcesSidebar` + `NoteEditor` + `NoteMeta` + `NoteAIChat`.

---

### `src/app/notes/[id]/page.tsx` — Edit Note (`/notes/[id]`)
Client Component.

**State:** `note` (full Note), `loading`, `saving`, `activeAttId`, `saveTimer` ref.

**Key behavior:**
- On mount, calls `getNote(id)`. If not found, redirects to `/notes`.
- Same 1 500 ms auto-save debounce pattern as New Note.
- `handleAttachmentAdd` / `handleAttachmentDelete` modify local state and schedule a save.
- Attachment type is inferred from file extension (pdf / docx / json / txt / image).
- All TODO comments mark backend integration points: `GET /api/notes/:id`, `PATCH /api/notes/:id`, `POST /api/upload`.
- Renders breadcrumb nav (Home → note title), `SourcesSidebar`, `NoteMeta`, `NoteEditor`, floating `NoteAIChat`.

---

### `src/app/chat/page.tsx` — Chat with Bao (`/chat`)
Client Component, split into two parts:

**`GlobalChat`** (inner):
- Maintains `messages: ChatMessage[]` starting with a welcome message: "Hi! I have access to all your notes. Ask me anything — I'll search across your entire knowledge base."
- No suggestion pills.
- `sendMessage()` calls `queryRAG()` with no `context_note_ids` (global scope across all notes).
- Auto-scrolls to bottom on new messages.

**`ChatPage`** (outer, default export):
- Wraps `GlobalChat` in `<Suspense>`.

---

### `src/app/trash/page.tsx` — Trash (`/trash`)
Client Component.

**Key behavior:**
- Loads soft-deleted notes via `getNotes({ deleted: true })`.
- Each note card shows title, deletion time (via `timeAgo()`), and attachment count.
- **Restore** calls `restoreNote(id)` → `PATCH /api/notes/:id { deleted: false }`.
- **Delete forever** shows a two-step confirm UI before calling `permanentDeleteNote(id)` → `DELETE /api/notes/:id`.
- Uses `actionId` to disable the acting card and show a `Spinner`.
- Uses `confirmId` for the confirmation state machine.
- Shows `<EmptyState>` when trash is empty.

---

## Components

### `src/components/layout/`

#### `AppShell.tsx`
Client Component. The top-level layout frame for every page.

**Props:** `children: ReactNode`, `activeNoteId?: string`

**Behavior:**
- Manages `sidebarOpen` boolean state.
- Renders `<Sidebar>` (collapsible) + `<TopNav>` + `<main>`.
- The `activeNoteId` is passed to `Sidebar` so the current note is highlighted.

---

#### `Sidebar.tsx`
Client Component. Left navigation panel.

**Key features:**
- Links to Home (`/`), Trash (`/trash`), and **Chat with Bao** (`/chat`, `forum` icon).
- Fetches the notes list via `getNotes()` on mount.
- Shows skeleton loading state (3 shimmer blocks) while loading.
- Each note row shows title (or "Untitled"), relative time, and a hover-reveal delete button.
- Delete calls `softDeleteNote(id)` — note moves to Trash, list updates immediately.
- "New note" button navigates to `/notes/new`.
- `activeNoteId` prop highlights the currently open note.
- `timeAgo()` utility formats timestamps (today/yesterday/Xd ago/date).
- Collapses when `open` prop is `false` (controlled by AppShell).

---

#### `TopNav.tsx`
Client Component. Slim top header.

- Hamburger menu button calls `onMenuClick` prop (toggles sidebar in AppShell).
- Search bar form is present in markup but currently commented out/non-functional.
- User avatar placeholder (initials "JW") at the right.

---

### `src/components/editor/`

#### `NoteEditor.tsx`
Client Component. The main TipTap rich-text editor.

**Props:** `content?: string` (TipTap JSON stringified), `onChange?: (json: string) => void`, `noteId?: string`

**TipTap extensions configured:**
- `StarterKit` (bold, italic, headings, lists, blockquote, code, etc.)
- `Image` (inline: false, allowBase64: true)
- `Placeholder` ("Start writing… or paste content here.")
- `Underline`, `TextAlign` (heading + paragraph), `Highlight`, `Link` (openOnClick: false)

**Key behavior:**
- `content` is parsed as JSON (TipTap JSON format); falls back to plain string if parse fails.
- `onUpdate` serialises the editor state back to JSON string and calls `onChange`.
- `immediatelyRender: false` prevents SSR hydration mismatch.
- Image upload via hidden `<input type="file">`: previews immediately with base64, then calls `uploadImage()` for the real URL (TODO backend). If `extracted_text` comes back, appends it as a paragraph.
- Renders `<EditorToolbar>` above `<EditorContent>`.

---

#### `EditorToolbar.tsx`
Client Component. Sticky toolbar above the TipTap editor.

**Props:** `editor: Editor | null`, `onImageUpload: () => void`

**Buttons (grouped with dividers):**
- Text formatting: Bold, Italic, Underline, Strikethrough.
- Headings: H1, H2, H3.
- Lists: Bullet list, Numbered list, Blockquote, Code block.
- Alignment: Left, Center, Right.
- Media: Insert image (delegates to `onImageUpload` prop).
- Undo / Redo (pushed to right with `ml-auto`).

Active state is detected via `editor.isActive(...)`. Disabled state for undo/redo via `editor.can().undo/redo()`.

---

#### `NoteMeta.tsx`
Client Component. Title input + meta row + tag editor above the TipTap editor.

**Props:** `note: Partial<Note>`, `onTitleChange?`, `onTagAdd?`, `onTagRemove?`, `saving?: boolean`

**Renders:**
- Large bare `<input>` for title (DM Serif Display font, 3xl).
- Meta row: attachment count badge, save status ("Saving…" with spin icon, or "Saved HH:MM" with check icon).
- Tag chips with remove buttons + inline tag input (press Enter to add).

---

#### `SourcesSidebar.tsx`
Client Component. Left panel inside the note editor showing file attachments.

**Props:** `attachments: Attachment[]`, `activeId?: string`, `onSelect?`, `onAdd?`, `onDelete?`

**Type config** (`TYPE_CFG`): maps each `AttachmentType` to a Material Symbol icon + colour scheme:
- `pdf` → red, `docx` → blue, `image` → emerald, `url` → green, `txt` → slate, `json` → amber.

**Key behavior:**
- Hidden `<input type="file" multiple>` accepts pdf / docx / txt / json / images.
- Clicking `+` triggers the file input; `onAdd` receives the `FileList`.
- Each attachment card shows icon, name (truncated), upload date + size.
- Active attachment highlighted with border/shadow.
- Empty state with instructions when no attachments.

---

### `src/components/home/`

#### `HeroInput.tsx`
Client Component. The central content-ingestion widget on the homepage.

**Key behavior:**
- Textarea for freeform text input.
- Ctrl/Cmd+Enter submits.
- Submit calls `createNote({ content, title: "New Note" })` then navigates to the new note's edit page.
- File attach button opens a hidden `<input type="file">` (calls `uploadFile()` from `src/lib/api/upload.ts` — TODO backend).
- Shows `<Spinner>` and "Processing…" label while loading.

---

#### `FeatureCards.tsx`
Server Component (no `"use client"`). Purely presentational.

Renders a 2-column grid of 4 feature cards:
1. Ingestion Agent
2. Categorisation Agent
3. Critic Agent
4. Semantic Search

Each card has a gradient background, icon, title (DM Serif Display), description, and staggered fade-up animation.

---

### `src/components/qa/`

#### `NoteAIChat.tsx`
Client Component. Floating AI chat panel scoped to a single note.

**Props:** `note: { id: string; title: string }`

**Panel header:** "Chat with Bao"

**Key behavior:**
- Hidden by default; FAB (floating action button) in bottom-right corner toggles it.
- Maintains `messages: ChatMessage[]` state, `input`, `loading`, `isOpen`.
- `sendMessage()` appends user message, calls `queryRAG({ query, context_note_ids: [note.id] })`, appends AI response with sources.
- Shows typing indicator dots while `loading`.
- Shows one hard-coded suggestion pill — **"Summarize this note"** — until the first user message; loaded on first open.
- Auto-scrolls to bottom.
- FAB shows unread badge (red dot) when chat has responses and panel is closed.

---

#### `ChatMessage.tsx`
Pure presentational component. Renders a single chat message bubble.

**Props:** `message: ChatMessage`

**Behavior:**
- User messages: right-aligned, primary-colour bubble.
- Assistant messages: left-aligned, white card with border + `auto_awesome` icon.
- Sources (if present on assistant message): pill badges showing `file_name`.
- Timestamp shown below each bubble.

---

### `src/components/ui/`

#### `EmptyState.tsx`
Reusable empty state component.

**Props:** `icon: string` (Material Symbol name), `title: string`, `description: string`, `action?: ReactNode`

Centred layout with icon in a warm-bg circle, heading, subtitle, optional action slot.

---

#### `Spinner.tsx`
Animated loading ring.

**Props:** `size?: "sm" | "md" | "lg"` (default `"md"`), `className?: string`

Size map: sm = 16 px, md = 24 px, lg = 40 px. Uses `border-t-primary` + `animate-spin` Tailwind classes.

---

## API Layer (`src/lib/api/`)

### `client.ts`
Foundation for all API calls.

**Exports:**
- `BASE_URL` — reads `NEXT_PUBLIC_API_URL`, defaults to `http://localhost:8000`.
- `USE_MOCKS` — `true` unless `NEXT_PUBLIC_USE_MOCKS === "false"`.
- `apiFetch<T>(path, options?)` — thin `fetch` wrapper. Sets `Content-Type: application/json` automatically (skipped for `FormData`). Throws on non-2xx responses with status + body text. TODO comment marks where auth headers (Bearer token) should be added.

---

### `notes.ts`
All note-related API operations. Every function checks `USE_MOCKS` first and falls back to mock data; real calls go to the FastAPI backend.

**Exported functions:**

| Function | Mock behaviour | Real endpoint |
|----------|---------------|---------------|
| `getNotes(opts?)` | Returns `MOCK_NOTES` filtered by `opts.deleted` | `GET /api/notes?deleted=...` |
| `getNote(id)` | Finds note in `MOCK_NOTES` by id | `GET /api/notes/:id` |
| `createNote(data)` | Creates new note with generated id, pushes to `MOCK_NOTES` | `POST /api/notes` |
| `updateNote(id, patch)` | Merges patch into matching mock note | `PATCH /api/notes/:id` |
| `softDeleteNote(id)` | Sets `deleted: true` on mock | `PATCH /api/notes/:id { deleted: true }` |
| `restoreNote(id)` | Sets `deleted: false` on mock | `PATCH /api/notes/:id { deleted: false }` |
| `permanentDeleteNote(id)` | Removes from `MOCK_NOTES` array | `DELETE /api/notes/:id` |

---

### `search.ts`
RAG search endpoint.

**Exported function:** `queryRAG({ query, context_note_ids? }) → Promise<SearchResult>`

- Mock: 1 200 ms delay, returns one of several canned answers based on keyword matching (hotel/flight/restaurant/default).
- Real: `POST /api/search` with `{ query, context_note_ids? }`, returns `{ answer: string, sources: Source[] }`.

---

### `upload.ts`
File and image upload helpers.

**Exported functions:**

| Function | Mock behaviour | Real endpoint |
|----------|---------------|---------------|
| `uploadImage(formData)` | Returns mock `{ url, extracted_text: "[Mock] ..." }` | `POST /api/upload/image` |
| `uploadFile(formData)` | Returns mock `{ id, name, type, url }` | `POST /api/upload` |
| `scrapeUrl(url)` | Returns mock scraped content object | `POST /api/upload/url` |

---

## Types (`src/lib/types/index.ts`)

### `AttachmentType`
```
"pdf" | "docx" | "image" | "url" | "txt" | "json"
```

### `Attachment`
| Field | Type | Notes |
|-------|------|-------|
| `id` | `string` | |
| `name` | `string` | Display filename |
| `type` | `AttachmentType` | |
| `url` | `string?` | For `type: "url"` — the external link |
| `file_path` | `string?` | Backend-served path, e.g. `/api/files/:id` |
| `uploaded_at` | `string` | ISO 8601 |
| `size_bytes` | `number?` | |

### `Note`
| Field | Type | Notes |
|-------|------|-------|
| `id` | `string` | |
| `title` | `string` | |
| `content` | `string` | TipTap JSON stringified |
| `attachments` | `Attachment[]` | |
| `tags` | `string[]` | |
| `created_at` | `string` | ISO 8601 |
| `updated_at` | `string` | ISO 8601 |
| `thumbnail_color` | `string?` | Unused in current UI |
| `deleted` | `boolean?` | `true` = note is in Trash |

### `Category`
Scaffolded for future AI-assigned categorisation. Fields: `id`, `name`, `note_count`, `icon?`.

### `Source`
Backend RAG source reference. Fields: `id`, `file_url`, `file_type`, `file_name`, `file_size_bytes`, `uploaded_at`, `summary?`, `extracted_fields?`, `note_id?`.

### `ChatMessage`
| Field | Type |
|-------|------|
| `id` | `string` |
| `role` | `"user" \| "assistant"` |
| `content` | `string` |
| `sources` | `Source[]?` |
| `timestamp` | `string` (ISO 8601) |

### `SearchResult`
```typescript
{ answer: string; sources: Source[] }
```

---

## Mock Data (`src/lib/mocks/notes.ts`)

**When it activates:** whenever `USE_MOCKS` is `true` (i.e. `NEXT_PUBLIC_USE_MOCKS !== "false"`).

**Contents:** A mutable `MOCK_NOTES: Note[]` array with 6 entries:
1. **Tokyo Trip 2024** — travel note with PDF (flight booking) + URL attachment, tags: travel, japan.
2. **Recipe Collection** — food note with image attachment, tags: food, cooking.
3. **Research Notes: ML Papers** — technical note with multiple PDFs + JSON, tags: research, ml, ai.
4. **Reading List** — URL-heavy note with book links, tags: books, reading.
5. **Project Ideas** — brainstorm note, no attachments, tags: ideas, projects.
6. **Old Todo List** *(deleted: true)* — appears only in Trash.

Notes 1–5 have realistic TipTap JSON content structures. The array is mutated in-place by mock `createNote`, `updateNote`, `softDeleteNote`, `restoreNote`, `permanentDeleteNote` — so changes persist for the lifetime of the browser session.

---

## Styles (`src/styles/`)

### `_variables.scss`
SCSS partial imported by TipTap. Defines CSS custom properties for the TipTap editor:
- Font families (`--tiptap-font-family`, `--tiptap-font-family-mono`).
- Color tokens for editor chrome (borders, backgrounds, text).
- Border radius values.

### `_keyframe-animations.scss`
SCSS partial with TipTap-specific keyframes:
- `tiptap-fade-in` — opacity 0 → 1.
- `tiptap-spin` — 360° rotation (used for loading states inside TipTap UI).

---

## Config Files

### `tailwind.config.ts`
Extended Tailwind theme:

**Colors:**
- `primary` / `primary-dark` — warm orange brand colour.
- `warm` palette (50–500) — cream/warm grays for backgrounds, borders, text.
- `bg-light` / `bg-card` — page and card backgrounds.

**Fonts:**
- `display` → DM Serif Display
- `body` → DM Sans
- `mono` → JetBrains Mono

**Shadows:**
- `shadow-warm-sm`, `shadow-warm-md`, `shadow-warm-lg` — warm-toned box shadows.

**Animations / keyframes:**
- `fade-up` — slides up + fades in (used for homepage hero + cards).
- `pulse-soft` — gentle opacity pulse (online indicator dot).
- `spin-slow` — slow rotation (saving icon).
- `shimmer` — skeleton loading sweep.

**Content paths:** `./src/**/*.{js,ts,jsx,tsx}`.

---

### `next.config.mjs`
Minimal config. Allows `next/image` to load from any HTTPS hostname (`remotePatterns: [{ protocol: "https", hostname: "**" }]`).

---

### `tsconfig.json`
- Target: `ESNext`, module resolution: `bundler`.
- `strict: true`.
- Path alias: `@/*` → `./src/*` (used throughout all imports).
- `jsx: preserve` (Next.js handles transform).

---

### `postcss.config.js`
Standard PostCSS setup:
```js
{ plugins: { tailwindcss: {}, autoprefixer: {} } }
```

---

## Key Patterns

### Auto-save Debounce
Both `/notes/new` and `/notes/[id]` use the same pattern:
1. User changes fire `scheduleAutoSave(patch)`.
2. `scheduleAutoSave` clears any pending `setTimeout`, then sets a new one for **1 500 ms**.
3. After the timer fires, `persist(patch)` calls `createNote` or `updateNote`.
4. `saving` state drives the "Saving…" indicator in `NoteMeta`.

### Soft Delete
Notes are never hard-deleted from the sidebar. `softDeleteNote(id)` sets `deleted: true`. The Trash page fetches `getNotes({ deleted: true })`. Permanent deletion only happens from Trash.

### Scoped AI Chat
`NoteAIChat` passes `context_note_ids: [note.id]` to `queryRAG`, scoping retrieval to that note. The global `/chat` page omits `context_note_ids` for across-all-notes search and is the primary sidebar-accessible chat surface.

### Mock / Real Toggle
The single env var `NEXT_PUBLIC_USE_MOCKS` controls all API calls. Setting it to `"false"` and pointing `NEXT_PUBLIC_API_URL` at the FastAPI server switches the entire app to live data with no code changes.

### Type-safe File Handling
Attachment types are inferred from file extensions in `handleAttachmentAdd` in both note pages using a cascading ternary. The `TYPE_CFG` map in `SourcesSidebar` then drives icon and colour per type.
