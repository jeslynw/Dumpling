import { apiFetch, USE_MOCKS } from "./client";
import type { SearchResult } from "../types";

const MOCK_RESPONSES: Record<string, string> = {
  default:
    "Based on your notes, I found relevant information across multiple documents. Your Tokyo trip includes a flight on NH008 departing Nov 6 at 17:05, hotel at Park Hyatt Tokyo (check-in Nov 1), and 12 restaurant bookmarks including Sukiyabashi Jiro in Ginza.",
};

export async function queryRAG(body: {
  query: string;
  context_note_ids?: string[];
}): Promise<SearchResult> {
  if (USE_MOCKS) {
    // Simulate network delay
    await new Promise((r) => setTimeout(r, 1200));
    const q = body.query.toLowerCase();
    let answer = MOCK_RESPONSES.default;
    if (q.includes("hotel") || q.includes("booking")) answer = MOCK_RESPONSES.hotel;
    else if (q.includes("flight") || q.includes("plane")) answer = MOCK_RESPONSES.flight;
    else if (q.includes("restaurant") || q.includes("food") || q.includes("eat"))
      answer = MOCK_RESPONSES.restaurant;
    return { answer, sources: [] };
  }
  // TODO: BACKEND — POST /api/search
  // Body: { query: string, context_note_ids?: string[] }
  // Returns: { answer: string, sources: Source[] }
  return apiFetch<SearchResult>("/api/search", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

// export async function getSuggestions(noteId?: string): Promise<string[]> {
//   if (USE_MOCKS) {
//     return [
//       "Summarize hotel info",
//     ];
//   }
//   // TODO: BACKEND — GET /api/search/suggestions?note_id=:id
//   const query = noteId ? `?note_id=${noteId}` : "";
//   return apiFetch<string[]>(`/api/search/suggestions${query}`);
// }
