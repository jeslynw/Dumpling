import { apiFetch, USE_MOCKS } from "./client";
import { mockNotes } from "../mocks/notes";
import type { Note } from "../types";

// TODO: BACKEND — Remove mock branches once FastAPI /notes routes are live

export async function getNotes(params?: {
  deleted?: boolean;
}): Promise<Note[]> {
  if (USE_MOCKS) {
    let notes = [...mockNotes];
    // Default: only return non-deleted notes. Pass deleted:true to get trash.
    if (params?.deleted === true) {
      notes = notes.filter((n) => n.deleted === true);
    } else {
      notes = notes.filter((n) => !n.deleted);
    }
    return notes;
  }
  // TODO: BACKEND — GET /api/notes  (default excludes deleted)
  //                 GET /api/notes?deleted=true  (returns trash)
  const query = new URLSearchParams(params as Record<string, string>);
  return apiFetch<Note[]>(`/api/notes?${query}`);
}

export async function getNote(id: string): Promise<Note | undefined> {
  if (USE_MOCKS) return mockNotes.find((n) => n.id === id);
  // TODO: BACKEND — GET /api/notes/:id
  return apiFetch<Note>(`/api/notes/${id}`);
}

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
  // TODO: BACKEND — POST /api/notes
  return apiFetch<Note>("/api/notes", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

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
  // TODO: BACKEND — PATCH /api/notes/:id
  return apiFetch<Note>(`/api/notes/${id}`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

export async function deleteNote(id: string): Promise<void> {
  if (USE_MOCKS) {
    const idx = mockNotes.findIndex((n) => n.id === id);
    if (idx !== -1) mockNotes[idx].deleted = true;
    return;
  }
  // TODO: BACKEND — PATCH /api/notes/:id { deleted: true }  (soft-delete to Trash)
  return apiFetch<void>(`/api/notes/${id}`, {
    method: "PATCH",
    body: JSON.stringify({ deleted: true }),
  });
}

export async function restoreNote(id: string): Promise<void> {
  if (USE_MOCKS) {
    const idx = mockNotes.findIndex((n) => n.id === id);
    if (idx !== -1) mockNotes[idx].deleted = false;
    return;
  }
  // TODO: BACKEND — PATCH /api/notes/:id { deleted: false }  (restore from Trash)
  return apiFetch<void>(`/api/notes/${id}`, {
    method: "PATCH",
    body: JSON.stringify({ deleted: false }),
  });
}

export async function permanentDeleteNote(id: string): Promise<void> {
  if (USE_MOCKS) {
    const idx = mockNotes.findIndex((n) => n.id === id);
    if (idx !== -1) mockNotes.splice(idx, 1);
    return;
  }
  // TODO: BACKEND — DELETE /api/notes/:id  (permanent, removes from DB and storage)
  return apiFetch<void>(`/api/notes/${id}`, { method: "DELETE" });
}
