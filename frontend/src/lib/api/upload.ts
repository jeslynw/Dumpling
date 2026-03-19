import { apiFetch, USE_MOCKS } from "./client";

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
  // TODO: BACKEND — POST /api/upload/image
  // Do NOT set Content-Type header — browser sets multipart boundary automatically
  return apiFetch<{ extracted_text: string; image_url: string; note_id: string }>(
    "/api/upload/image",
    { method: "POST", body: formData, headers: {} }
  );
}

export async function uploadFile(formData: FormData): Promise<{
  source_id: string;
  summary: string;
  category: string;
}> {
  if (USE_MOCKS) {
    await new Promise((r) => setTimeout(r, 1000));
    return {
      source_id: `src-${Date.now()}`,
      summary: "[Mock] File uploaded and processed by AI.",
      category: "Uncategorized",
    };
  }
  // TODO: BACKEND — POST /api/upload
  return apiFetch<{ source_id: string; summary: string; category: string }>(
    "/api/upload",
    { method: "POST", body: formData, headers: {} }
  );
}

export async function scrapeUrl(url: string): Promise<{
  note_id: string;
  summary: string;
  category: string;
}> {
  if (USE_MOCKS) {
    await new Promise((r) => setTimeout(r, 1500));
    return {
      note_id: `note-${Date.now()}`,
      summary: `[Mock] Content scraped and summarized from: ${url}`,
      category: "Research",
    };
  }
  // TODO: BACKEND — POST /api/scrape
  // Powered by Tavily web scraping + AI summarization
  return apiFetch<{ note_id: string; summary: string; category: string }>(
    "/api/scrape",
    { method: "POST", body: JSON.stringify({ url }) }
  );
}
