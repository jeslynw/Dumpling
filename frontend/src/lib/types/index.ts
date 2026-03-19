export type AttachmentType = "pdf" | "docx" | "image" | "url" | "txt" | "json";

export interface Attachment {
  id: string;
  name: string;
  type: AttachmentType;
  url?: string;        // for type:"url" — the external link to open/scrape
  file_path?: string;  // for uploaded files — the path the backend serves
                       // e.g. /api/files/:id  →  FastAPI: GET /api/files/{id} streams the file
                       // TODO: BACKEND — FastAPI should serve uploaded files at this path
  uploaded_at: string;
  size_bytes?: number;
}

export interface Note {
  id: string;
  title: string;
  content: string; // Tiptap JSON stringified
  attachments: Attachment[]; // files/links attached to this note
  tags: string[];
  created_at: string; // ISO 8601
  updated_at: string;
  thumbnail_color?: string;
  deleted?: boolean;  // soft-delete flag — true means note is in Trash
                      // TODO: BACKEND — PATCH /api/notes/:id { deleted: true } to soft-delete
                      // TODO: BACKEND — DELETE /api/notes/:id for permanent deletion
}

// Category is used by the categories API (lib/api/categories.ts) which is
// scaffolded for future AI-assigned categorisation. Kept for backend integration.
export interface Category {
  id: string;
  name: string;
  note_count: number;
  icon?: string;
}

export interface Source {
  id: string;
  file_url: string;
  file_type: "pdf" | "image" | "json" | "text";
  file_name: string;
  file_size_bytes: number;
  uploaded_at: string;
  summary?: string;
  extracted_fields?: Record<string, string>;
  note_id?: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
  timestamp: string;
}

export interface SearchResult {
  answer: string;
  sources: Source[];
}
