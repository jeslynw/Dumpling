"use client";

import { useState } from "react";
import type { Note } from "@/lib/types";

interface NoteMetaProps {
  note: Partial<Note>;
  onTitleChange?: (title: string) => void;
  onTagAdd?: (tag: string) => void;
  onTagRemove?: (tag: string) => void;
  saving?: boolean;
}

export default function NoteMeta({
  note,
  onTitleChange,
  onTagAdd,
  onTagRemove,
  saving,
}: NoteMetaProps) {
  const [tagInput, setTagInput] = useState("");

  const handleTagKey = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && tagInput.trim()) {
      onTagAdd?.(tagInput.trim().toLowerCase());
      setTagInput("");
    }
  };

  return (
    <div className="mb-6 space-y-3">
      {/* Title */}
      <input
        type="text"
        value={note.title ?? ""}
        onChange={(e) => onTitleChange?.(e.target.value)}
        placeholder="Untitled Note"
        className="
          w-full bg-transparent border-none outline-none
          text-3xl text-slate-800 placeholder:text-warm-300
          font-normal leading-tight
        "
        style={{ fontFamily: "var(--font-display)" }}
      />

      {/* Meta row */}
      <div className="flex flex-wrap items-center gap-2 text-xs text-slate-400">
        {/* Attachment count */}
        {(note.attachments ?? []).length > 0 && (
          <div className="flex items-center gap-1 text-slate-400">
            <span className="material-symbols-outlined text-[13px] text-primary">attach_file</span>
            <span className="text-warm-400">
              {(note.attachments ?? []).length} attachment{(note.attachments ?? []).length !== 1 ? "s" : ""}
            </span>
          </div>
        )}

        {/* Last saved */}
        {note.updated_at && (
          <>
            <span className="text-warm-300">·</span>
            <span className="flex items-center gap-1">
              {saving ? (
                <>
                  <span className="material-symbols-outlined text-[12px] animate-spin-slow text-primary">
                    sync
                  </span>
                  Saving…
                </>
              ) : (
                <>
                  <span className="material-symbols-outlined text-[12px] text-emerald-400">
                    check_circle
                  </span>
                  Saved {new Date(note.updated_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                </>
              )}
            </span>
          </>
        )}
      </div>

      {/* Tags */}
      <div className="flex flex-wrap items-center gap-2">
        {(note.tags ?? []).map((tag) => (
          <span
            key={tag}
            className="inline-flex items-center gap-1 bg-warm-200 text-slate-500 text-xs px-2 py-1 rounded-full"
          >
            #{tag}
            {onTagRemove && (
              <button
                onClick={() => onTagRemove(tag)}
                className="ml-0.5 text-slate-300 hover:text-red-400 transition-colors"
              >
                <span className="material-symbols-outlined text-[12px]">close</span>
              </button>
            )}
          </span>
        ))}
        {onTagAdd && (
          <input
            value={tagInput}
            onChange={(e) => setTagInput(e.target.value)}
            onKeyDown={handleTagKey}
            placeholder="+ add tag"
            className="text-xs bg-transparent text-slate-400 placeholder:text-warm-300 border-none outline-none w-20"
          />
        )}
      </div>
    </div>
  );
}
