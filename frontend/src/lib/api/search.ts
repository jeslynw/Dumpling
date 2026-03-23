import { apiFetch, USE_MOCKS } from "./client";
import type { SearchResult } from "../types";

const MOCK_RESPONSES: Record<string, string> = {
  default:
    "Based on your notes, I found relevant information across multiple documents. Your Tokyo trip includes a flight on NH008 departing Nov 6 at 17:05, hotel at Park Hyatt Tokyo (check-in Nov 1), and 12 restaurant bookmarks including Sukiyabashi Jiro in Ginza.",
};

// ── queryRAG → POST /chat ─────────────────────────────────────────────────────
export async function queryRAG(body: {
  query: string;
  context_note_ids?: string[];
}): Promise<SearchResult> {
  if (USE_MOCKS) {
    await new Promise((r) => setTimeout(r, 1200));
    const q = body.query.toLowerCase();
    let answer = MOCK_RESPONSES.default;
    if (q.includes("hotel") || q.includes("booking")) answer = MOCK_RESPONSES.hotel ?? MOCK_RESPONSES.default;
    else if (q.includes("flight") || q.includes("plane")) answer = MOCK_RESPONSES.flight ?? MOCK_RESPONSES.default;
    else if (q.includes("restaurant") || q.includes("food") || q.includes("eat"))
      answer = MOCK_RESPONSES.restaurant ?? MOCK_RESPONSES.default;
    return { answer, sources: [] };
  }

  // POST /chat — RAG chatbot agent
  // The agent internally: picks folders → Hybrid RAG + CRAG → synthesizes answer
  const response = await apiFetch<{ answer: string }>("/chat", {
    method: "POST",
    body: JSON.stringify({ question: body.query }),
  });

  return {
    answer: response.answer,
    sources: [], // TODO: parse [WEB SEARCH RESULT] tags from answer to populate sources
  };
}
