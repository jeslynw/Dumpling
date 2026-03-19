import type { Note } from "../types";

// BASE_FILE_URL mirrors what the FastAPI backend will serve.
// TODO: BACKEND — add a route:  GET /api/files/{attachment_id}
//   that streams the stored file from disk / object storage.
//   The frontend will request this path to open or download attachments.
const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const fp = (id: string) => `${API}/api/files/${id}`;

export const mockNotes: Note[] = [
  // ─────────────────────────────────────────────────────────────────
  // ACTIVE NOTES
  // ─────────────────────────────────────────────────────────────────
  {
    id: "note-1",
    title: "Tokyo Trip",
    content: JSON.stringify({
      type: "doc",
      content: [
        { type: "heading", attrs: { level: 1 }, content: [{ type: "text", text: "Trip to Tokyo 🇯🇵" }] },
        { type: "heading", attrs: { level: 2 }, content: [{ type: "text", text: "Overview" }] },
        {
          type: "paragraph",
          content: [{ type: "text", text: "A comprehensive summary of documents related to the upcoming journey. Flight departs on Oct 12th from SFO, arriving at Narita (NRT). Accommodations secured at the Park Hyatt Tokyo, Shinjuku." }],
        },
        { type: "heading", attrs: { level: 2 }, content: [{ type: "text", text: "Key Dates" }] },
        {
          type: "bulletList",
          content: [
            { type: "listItem", content: [{ type: "paragraph", content: [{ type: "text", text: "Arrival — Oct 12, 14:30" }] }] },
            { type: "listItem", content: [{ type: "paragraph", content: [{ type: "text", text: "Dining (Jiro) — Oct 15, 19:00" }] }] },
            { type: "listItem", content: [{ type: "paragraph", content: [{ type: "text", text: "Departure — Oct 20, 11:00" }] }] },
          ],
        },
        { type: "heading", attrs: { level: 2 }, content: [{ type: "text", text: "Must-visit Temples & Sights" }] },
        {
          type: "bulletList",
          content: [
            { type: "listItem", content: [{ type: "paragraph", content: [{ type: "text", text: "Senso-ji (Asakusa) — Cultural hub" }] }] },
            { type: "listItem", content: [{ type: "paragraph", content: [{ type: "text", text: "Meiji Jingu (Harajuku) — Peaceful forest" }] }] },
            { type: "listItem", content: [{ type: "paragraph", content: [{ type: "text", text: "Kiyomizu-dera (Day trip to Kyoto)" }] }] },
            { type: "listItem", content: [{ type: "paragraph", content: [{ type: "text", text: "Shibuya Crossing — Sunset view" }] }] },
          ],
        },
      ],
    }),
    attachments: [
      {
        id: "att-1-1", name: "Flight Booking.pdf", type: "pdf",
        file_path: fp("att-1-1"),   // GET /api/files/att-1-1 → streams PDF
        uploaded_at: "2024-10-12T14:30:00Z", size_bytes: 1258291,
      },
      {
        id: "att-1-2", name: "Itinerary.docx", type: "docx",
        file_path: fp("att-1-2"),   // GET /api/files/att-1-2 → streams DOCX
        uploaded_at: "2024-10-14T09:15:00Z", size_bytes: 432100,
      },
      {
        id: "att-1-3", name: "Hotel Pin.url", type: "url",
        url: "https://maps.google.com/?q=Park+Hyatt+Tokyo",  // external link — no file_path needed
        uploaded_at: "2024-10-12T18:45:00Z",
      },
    ],
    tags: ["tokyo", "japan", "travel"],
    created_at: "2024-10-12T10:00:00Z",
    updated_at: "2024-10-24T08:00:00Z",
    thumbnail_color: "from-violet-400/30 to-purple-200/20",
    deleted: false,
  },
  {
    id: "note-2",
    title: "Basketball Team Uniform Ideas",
    content: JSON.stringify({
      type: "doc",
      content: [
        { type: "heading", attrs: { level: 1 }, content: [{ type: "text", text: "Uniform Design Brief 🏀" }] },
        {
          type: "paragraph",
          content: [{ type: "text", text: "Collecting references for the new team uniform. Primary colour: navy blue with gold accents. Jersey number font should be bold and condensed." }],
        },
        { type: "heading", attrs: { level: 2 }, content: [{ type: "text", text: "Design Requirements" }] },
        {
          type: "bulletList",
          content: [
            { type: "listItem", content: [{ type: "paragraph", content: [{ type: "text", text: "Moisture-wicking fabric" }] }] },
            { type: "listItem", content: [{ type: "paragraph", content: [{ type: "text", text: "Sublimation print — no iron-on" }] }] },
            { type: "listItem", content: [{ type: "paragraph", content: [{ type: "text", text: "Sponsor logo placement: left chest" }] }] },
          ],
        },
      ],
    }),
    attachments: [
      {
        id: "att-2-1", name: "Reference_Jersey.png", type: "image",
        file_path: fp("att-2-1"),   // GET /api/files/att-2-1 → streams image
        uploaded_at: "2024-10-18T09:00:00Z", size_bytes: 892041,
      },
      {
        id: "att-2-2", name: "Colour_Palette.pdf", type: "pdf",
        file_path: fp("att-2-2"),   // GET /api/files/att-2-2 → streams PDF
        uploaded_at: "2024-10-18T09:30:00Z", size_bytes: 210000,
      },
      {
        id: "att-2-3", name: "Supplier Quote.docx", type: "docx",
        file_path: fp("att-2-3"),   // GET /api/files/att-2-3 → streams DOCX
        uploaded_at: "2024-10-19T11:00:00Z", size_bytes: 85000,
      },
    ],
    tags: ["basketball", "design", "uniform"],
    created_at: "2024-10-18T09:00:00Z",
    updated_at: "2024-10-24T03:00:00Z",
    thumbnail_color: "from-orange-400/30 to-amber-200/20",
    deleted: false,
  },
  {
    id: "note-3",
    title: "Project Roadmap Q4",
    content: JSON.stringify({
      type: "doc",
      content: [
        { type: "heading", attrs: { level: 1 }, content: [{ type: "text", text: "SmartNotebook — Q4 Roadmap" }] },
        {
          type: "paragraph",
          content: [{ type: "text", text: "Tracking deliverables and milestones for the Q4 sprint across frontend and backend teams." }],
        },
        { type: "heading", attrs: { level: 2 }, content: [{ type: "text", text: "Milestones" }] },
        {
          type: "bulletList",
          content: [
            { type: "listItem", content: [{ type: "paragraph", content: [{ type: "text", text: "Phase 1: Frontend scaffolding ✅" }] }] },
            { type: "listItem", content: [{ type: "paragraph", content: [{ type: "text", text: "Phase 2: Tiptap integration ✅" }] }] },
            { type: "listItem", content: [{ type: "paragraph", content: [{ type: "text", text: "Phase 3: Backend API connection 🔄" }] }] },
            { type: "listItem", content: [{ type: "paragraph", content: [{ type: "text", text: "Phase 4: RAG search go-live ⏳" }] }] },
          ],
        },
      ],
    }),
    attachments: [
      {
        id: "att-3-1", name: "PRD_v2.pdf", type: "pdf",
        file_path: fp("att-3-1"),   // GET /api/files/att-3-1 → streams PDF
        uploaded_at: "2024-10-15T14:00:00Z", size_bytes: 1540000,
      },
      {
        id: "att-3-2", name: "API_Spec.json", type: "json",
        file_path: fp("att-3-2"),   // GET /api/files/att-3-2 → streams JSON
        uploaded_at: "2024-10-16T10:00:00Z", size_bytes: 32000,
      },
      {
        id: "att-3-3", name: "Figma Designs", type: "url",
        url: "https://figma.com",   // external link — no file_path needed
        uploaded_at: "2024-10-17T09:00:00Z",
      },
      {
        id: "att-3-4", name: "Sprint_Notes.docx", type: "docx",
        file_path: fp("att-3-4"),   // GET /api/files/att-3-4 → streams DOCX
        uploaded_at: "2024-10-20T15:00:00Z", size_bytes: 128000,
      },
    ],
    tags: ["project", "roadmap", "planning"],
    created_at: "2024-10-15T14:00:00Z",
    updated_at: "2024-10-23T18:00:00Z",
    thumbnail_color: "from-blue-400/30 to-cyan-200/20",
    deleted: false,
  },
  {
    id: "note-4",
    title: "Weekly Review — Oct 21",
    content: JSON.stringify({
      type: "doc",
      content: [
        { type: "heading", attrs: { level: 1 }, content: [{ type: "text", text: "Week of Oct 21 📋" }] },
        { type: "heading", attrs: { level: 2 }, content: [{ type: "text", text: "Completed" }] },
        {
          type: "bulletList",
          content: [
            { type: "listItem", content: [{ type: "paragraph", content: [{ type: "text", text: "API design doc" }] }] },
            { type: "listItem", content: [{ type: "paragraph", content: [{ type: "text", text: "Frontend wireframes" }] }] },
          ],
        },
        { type: "heading", attrs: { level: 2 }, content: [{ type: "text", text: "Blockers" }] },
        {
          type: "paragraph",
          content: [{ type: "text", text: "Qdrant cloud quota — need to upgrade plan before RAG can be tested end-to-end." }],
        },
      ],
    }),
    attachments: [
      {
        id: "att-4-1", name: "Standup_Notes.txt", type: "txt",
        file_path: fp("att-4-1"),   // GET /api/files/att-4-1 → streams TXT
        uploaded_at: "2024-10-21T09:00:00Z", size_bytes: 4096,
      },
      {
        id: "att-4-2", name: "Blocker_Screenshot.png", type: "image",
        file_path: fp("att-4-2"),   // GET /api/files/att-4-2 → streams image
        uploaded_at: "2024-10-21T14:00:00Z", size_bytes: 340000,
      },
    ],
    tags: ["weekly-review", "reflection"],
    created_at: "2024-10-21T20:00:00Z",
    updated_at: "2024-10-21T20:30:00Z",
    thumbnail_color: "from-emerald-400/30 to-teal-200/20",
    deleted: false,
  },
  {
    id: "note-5",
    title: "AI Research — RAG Architecture",
    content: JSON.stringify({
      type: "doc",
      content: [
        { type: "heading", attrs: { level: 1 }, content: [{ type: "text", text: "RAG Architecture Research 🧠" }] },
        {
          type: "paragraph",
          content: [{ type: "text", text: "Retrieval-Augmented Generation combines dense retrieval with generative models. Key components: embedding model, vector store (Qdrant), reranker, LLM." }],
        },
        { type: "heading", attrs: { level: 2 }, content: [{ type: "text", text: "Reference Papers" }] },
        {
          type: "bulletList",
          content: [
            { type: "listItem", content: [{ type: "paragraph", content: [{ type: "text", text: "Lewis et al. 2020 — original RAG paper" }] }] },
            { type: "listItem", content: [{ type: "paragraph", content: [{ type: "text", text: "Gao et al. 2023 — survey of RAG techniques" }] }] },
          ],
        },
      ],
    }),
    attachments: [
      {
        id: "att-5-1", name: "RAG_Paper.pdf", type: "pdf",
        file_path: fp("att-5-1"),   // GET /api/files/att-5-1 → streams PDF
        uploaded_at: "2024-10-17T16:00:00Z", size_bytes: 2340000,
      },
      {
        id: "att-5-2", name: "Qdrant Docs", type: "url",
        url: "https://qdrant.tech/documentation",  // external link
        uploaded_at: "2024-10-18T10:00:00Z",
      },
      {
        id: "att-5-3", name: "Experiment_Results.json", type: "json",
        file_path: fp("att-5-3"),   // GET /api/files/att-5-3 → streams JSON
        uploaded_at: "2024-10-19T14:00:00Z", size_bytes: 56000,
      },
    ],
    tags: ["AI", "RAG", "LLM", "research"],
    created_at: "2024-10-17T16:00:00Z",
    updated_at: "2024-10-20T09:00:00Z",
    thumbnail_color: "from-indigo-400/30 to-violet-200/20",
    deleted: false,
  },

  // ─────────────────────────────────────────────────────────────────
  // PRE-DELETED NOTE — appears in /trash, hidden from main list
  // TODO: BACKEND — notes with deleted:true should be returned only
  //   by GET /api/notes?deleted=true, not the default GET /api/notes
  // ─────────────────────────────────────────────────────────────────
  {
    id: "note-deleted-1",
    title: "Old Meeting Notes — Sep 10",
    content: JSON.stringify({
      type: "doc",
      content: [
        { type: "heading", attrs: { level: 1 }, content: [{ type: "text", text: "Meeting Notes — Sep 10" }] },
        {
          type: "paragraph",
          content: [{ type: "text", text: "Discussed sprint priorities, backlog grooming, and upcoming demo day schedule. Archived as no longer relevant." }],
        },
      ],
    }),
    attachments: [
      {
        id: "att-d1-1", name: "Meeting_Agenda.pdf", type: "pdf",
        file_path: fp("att-d1-1"),
        uploaded_at: "2024-09-10T09:00:00Z", size_bytes: 92000,
      },
    ],
    tags: ["meeting", "archived"],
    created_at: "2024-09-10T09:00:00Z",
    updated_at: "2024-09-10T11:00:00Z",
    thumbnail_color: "from-slate-300/40 to-gray-200/20",
    deleted: true,  // ← this note lives in the Trash
  },
];
