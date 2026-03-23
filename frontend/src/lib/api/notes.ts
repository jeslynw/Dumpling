import { apiFetch, USE_MOCKS } from "./client";
import { mockNotes } from "../mocks/notes";
import type { Note } from "../types";

// ── Backend folder shape ──────────────────────────────────────────────────────
interface BackendFolder {
  name: string;
  description: string;
  sources: string[];
}

interface FolderListResponse {
  folders: BackendFolder[];
}

// Map a backend folder → frontend Note shape so the rest of the UI works unchanged
function folderToNote(folder: BackendFolder): Note {
  return {
    id: folder.name,                        // folder name is the stable ID
    title: folder.name.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()),
    content: folder.description,
    attachments: folder.sources.map((src, i) => ({
      id: `${folder.name}-src-${i}`,
      name: src.startsWith("http") ? new URL(src).hostname : src,
      url: src,
      type: src.startsWith("http") ? "link" : "file",
    })),
    tags: [],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    thumbnail_color: "from-purple-400/30 to-violet-200/20",
    source_count: folder.sources.length,
  };
}

// ── getNotes → GET /folders ───────────────────────────────────────────────────
export async function getNotes(params?: {
  deleted?: boolean;
}): Promise<Note[]> {
  if (USE_MOCKS) {
    let notes = [...mockNotes];
    if (params?.deleted === true) {
      notes = notes.filter((n) => n.deleted === true);
    } else {
      notes = notes.filter((n) => !n.deleted);
    }
    return notes;
  }

  // Trash is not supported in the backend yet — return empty for deleted view
  if (params?.deleted === true) return [];

  const response = await apiFetch<FolderListResponse>("/folders");
  return response.folders.map(folderToNote);
}

// ── getNote → GET /folders/:name ─────────────────────────────────────────────
export async function getNote(id: string): Promise<Note | undefined> {
  if (USE_MOCKS) return mockNotes.find((n) => n.id === id);

  try {
    const folder = await apiFetch<BackendFolder>(`/folders/${id}`);
    return folderToNote(folder);
  } catch {
    return undefined;
  }
}

// ── createNote — not directly supported; ingest creates folders automatically ─
// Use upload.ts → ingestText() / uploadFile() / scrapeUrl() to add content.
export async function createNote(body: {
  content?: string;
  title?: string;
}): Promise<Note> {
  if (USE_MOCKS) {
    const note: Note = {
      id: `note-${Date.now()}`,
      title: body.title ?? "Untitled Note",
      content: body.content ?? "",
      attachments: [],
      tags: [],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      thumbnail_color: "from-purple-400/30 to-violet-200/20",
    };
    mockNotes.unshift(note);
    return note;
  }

  // Backend creates folders automatically via /ingest — no direct create endpoint.
  // For now fall back to mock behaviour so the UI doesn't break.
  const note: Note = {
    id: `note-${Date.now()}`,
    title: body.title ?? "Untitled Note",
    content: body.content ?? "",
    attachments: [],
    tags: [],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    thumbnail_color: "from-purple-400/30 to-violet-200/20",
  };
  return note;
}

// ── updateNote — not yet supported in backend ─────────────────────────────────
export async function updateNote(
  id: string,
  body: Partial<Note>
): Promise<Note> {
  if (USE_MOCKS) {
    const idx = mockNotes.findIndex((n) => n.id === id);
    if (idx !== -1) {
      mockNotes[idx] = {
        ...mockNotes[idx],
        ...body,
        updated_at: new Date().toISOString(),
      };
      return mockNotes[idx];
    }
    throw new Error("Note not found");
  }
  // TODO: backend folder rename/edit endpoint not yet implemented
  throw new Error("updateNote not yet supported in backend");
}

// ── deleteNote → DELETE /folders/:name ───────────────────────────────────────
export async function deleteNote(id: string): Promise<void> {
  if (USE_MOCKS) {
    const idx = mockNotes.findIndex((n) => n.id === id);
    if (idx !== -1) mockNotes[idx].deleted = true;
    return;
  }

  // Backend DELETE is permanent — no soft-delete/trash support yet
  await apiFetch<void>(`/folders/${id}`, { method: "DELETE" });
}

// ── restoreNote — no trash in backend yet ────────────────────────────────────
export async function restoreNote(id: string): Promise<void> {
  if (USE_MOCKS) {
    const idx = mockNotes.findIndex((n) => n.id === id);
    if (idx !== -1) mockNotes[idx].deleted = false;
    return;
  }
  // Not supported yet
}

// ── permanentDeleteNote → DELETE /folders/:name ───────────────────────────────
export async function permanentDeleteNote(id: string): Promise<void> {
  if (USE_MOCKS) {
    const idx = mockNotes.findIndex((n) => n.id === id);
    if (idx !== -1) mockNotes.splice(idx, 1);
    return;
  }

  await apiFetch<void>(`/folders/${id}`, { method: "DELETE" });
}
