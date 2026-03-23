import { apiFetch, USE_MOCKS } from "./client";

// ── Backend response shapes ───────────────────────────────────────────────────
interface IngestItemResult {
  title: string;
  summary: string;
  folder: string | null;
  chunk_count: number;
  needs_confirmation: boolean;
  confidence: number;
  confidence_band: string;
  action: string;
}

interface IngestTextResponse {
  results: IngestItemResult[];
  collections: string[];
}

// ── uploadFile → POST /ingest/file ────────────────────────────────────────────
export async function uploadFile(formData: FormData): Promise<{
  source_id: string;
  summary: string;
  category: string;
  needs_confirmation: boolean;
  confidence: number;
  action: string;
}> {
  if (USE_MOCKS) {
    await new Promise((r) => setTimeout(r, 1000));
    return {
      source_id: `src-${Date.now()}`,
      summary: "[Mock] File uploaded and processed by AI.",
      category: "Uncategorized",
      needs_confirmation: false,
      confidence: 0.9,
      action: "auto_assign",
    };
  }

  const result = await apiFetch<IngestItemResult>("/ingest/file", {
    method: "POST",
    body: formData,
    headers: {}, // let browser set multipart boundary
  });

  return {
    source_id: result.folder ?? `src-${Date.now()}`,
    summary: result.summary,
    category: result.folder ?? "Uncategorized",
    needs_confirmation: result.needs_confirmation,
    confidence: result.confidence,
    action: result.action,
  };
}

// ── scrapeUrl → POST /ingest/text ─────────────────────────────────────────────
export async function scrapeUrl(url: string): Promise<{
  note_id: string;
  summary: string;
  category: string;
  needs_confirmation: boolean;
  confidence: number;
  action: string;
}> {
  if (USE_MOCKS) {
    await new Promise((r) => setTimeout(r, 1500));
    return {
      note_id: `note-${Date.now()}`,
      summary: `[Mock] Content scraped and summarized from: ${url}`,
      category: "Research",
      needs_confirmation: false,
      confidence: 0.9,
      action: "auto_assign",
    };
  }

  const response = await apiFetch<IngestTextResponse>("/ingest/text", {
    method: "POST",
    body: JSON.stringify({ raw_input: url }),
  });

  // ingest/text returns an array of results — take the first one
  const first = response.results[0];
  return {
    note_id: first?.folder ?? `note-${Date.now()}`,
    summary: first?.summary ?? "",
    category: first?.folder ?? "Uncategorized",
    needs_confirmation: first?.needs_confirmation ?? false,
    confidence: first?.confidence ?? 0,
    action: first?.action ?? "",
  };
}

// ── ingestText → POST /ingest/text (batch, raw textbox input) ─────────────────
// Use this when the user pastes a mix of URLs, filenames, and plain text.
export async function ingestText(
  rawInput: string,
  options?: { auto_categorize?: boolean; target_folder?: string }
): Promise<IngestTextResponse> {
  if (USE_MOCKS) {
    await new Promise((r) => setTimeout(r, 1000));
    return {
      results: [
        {
          title: "[Mock] Ingested content",
          summary: "[Mock] AI processed your input.",
          folder: "mock_folder",
          chunk_count: 3,
          needs_confirmation: false,
          confidence: 0.9,
          confidence_band: "clearly_fits",
          action: "auto_assign",
        },
      ],
      collections: ["mock_folder"],
    };
  }

  return apiFetch<IngestTextResponse>("/ingest/text", {
    method: "POST",
    body: JSON.stringify({
      raw_input: rawInput,
      auto_categorize: options?.auto_categorize ?? true,
      target_folder: options?.target_folder ?? "",
    }),
  });
}

// ── confirmFolder → POST /ingest/confirm ──────────────────────────────────────
// Call this when needs_confirmation=true and the user has typed their folder name.
export async function confirmFolder(body: {
  title: string;
  summary: string;
  source: string;
  suggested_folder: string;
  confirmed_folder: string;
}): Promise<{ folder: string; chunk_count: number }> {
  if (USE_MOCKS) {
    return { folder: body.confirmed_folder, chunk_count: 1 };
  }

  return apiFetch<{ folder: string; chunk_count: number }>("/ingest/confirm", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

// ── uploadImage → kept as-is (no backend endpoint yet) ───────────────────────
export async function uploadImage(formData: FormData): Promise<{
  extracted_text: string;
  image_url: string;
  note_id: string;
}> {
  if (USE_MOCKS) {
    await new Promise((r) => setTimeout(r, 800));
    return {
      extracted_text:
        "[Mock] Text extracted from image: Sample extracted content from uploaded image.",
      image_url: URL.createObjectURL(formData.get("image") as File),
      note_id: "note-mock",
    };
  }
  // Images go through /ingest/file — reuse uploadFile logic
  return apiFetch<{ extracted_text: string; image_url: string; note_id: string }>(
    "/ingest/file",
    { method: "POST", body: formData, headers: {} }
  );
}
