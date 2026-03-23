/**
 * folders.ts — direct access to backend folder endpoints
 *
 * Use this when a component needs raw folder data (name, description, sources)
 * rather than the Note-shaped data from notes.ts.
 */
import { apiFetch, USE_MOCKS } from "./client";

export interface Folder {
  name: string;
  description: string;
  sources: string[];
}

// ── GET /folders ──────────────────────────────────────────────────────────────
export async function getFolders(): Promise<Folder[]> {
  if (USE_MOCKS) return [];
  const response = await apiFetch<{ folders: Folder[] }>("/folders");
  return response.folders;
}

// ── GET /folders/:name ────────────────────────────────────────────────────────
export async function getFolder(name: string): Promise<Folder> {
  if (USE_MOCKS) return { name, description: "", sources: [] };
  return apiFetch<Folder>(`/folders/${name}`);
}

// ── DELETE /folders/:name ─────────────────────────────────────────────────────
export async function deleteFolder(name: string): Promise<{ deleted: string; remaining: string[] }> {
  if (USE_MOCKS) return { deleted: name, remaining: [] };
  return apiFetch<{ deleted: string; remaining: string[] }>(`/folders/${name}`, {
    method: "DELETE",
  });
}
