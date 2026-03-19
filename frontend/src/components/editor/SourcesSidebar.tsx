"use client";

import { useRef } from "react";
import type { Attachment, AttachmentType } from "@/lib/types";

interface SourcesSidebarProps {
  attachments: Attachment[];
  activeId?: string;
  onSelect?: (att: Attachment) => void;
  onAdd?: (files: FileList) => void;
  onDelete?: (id: string) => void;
}

/* ── Icon + colour per file type ── */
const TYPE_CFG: Record<
  AttachmentType,
  { icon: string; color: string; bg: string }
> = {
  pdf:   { icon: "picture_as_pdf", color: "text-red-500",     bg: "bg-red-50"     },
  docx:  { icon: "description",    color: "text-blue-500",    bg: "bg-blue-50"    },
  image: { icon: "image",          color: "text-emerald-500", bg: "bg-emerald-50" },
  url:   { icon: "link",           color: "text-green-500",   bg: "bg-green-50"   },
  txt:   { icon: "article",        color: "text-slate-400",   bg: "bg-slate-50"   },
  json:  { icon: "data_object",    color: "text-amber-500",   bg: "bg-amber-50"   },
};

function formatDate(iso: string) {
  const d = new Date(iso);
  return d.toLocaleString("en-GB", {
    hour: "2-digit",
    minute: "2-digit",
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function formatSize(bytes?: number) {
  if (!bytes) return null;
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function SourcesSidebar({
  attachments,
  activeId,
  onSelect,
  onAdd,
  onDelete,
}: SourcesSidebarProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      onAdd?.(e.target.files);
    }
    // reset so same file can be re-selected
    e.target.value = "";
  };

  return (
    <aside className="w-64 flex-shrink-0 border-r border-warm-400/50 bg-warm-50/60 flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-warm-400/40">
        <h3 className="text-[11px] font-bold uppercase tracking-widest text-slate-400">
          Sources
        </h3>
        <button
          onClick={() => fileInputRef.current?.click()}
          title="Add attachment"
          className="w-6 h-6 flex items-center justify-center rounded-md hover:bg-primary/10 text-slate-400 hover:text-primary transition-all"
        >
          <span className="material-symbols-outlined text-[18px]">add</span>
        </button>
        {/* Hidden file input */}
        {/* TODO: BACKEND — when a file is picked, call POST /api/upload with FormData
            then push the returned { id, name, type, url, uploaded_at } into note.attachments
            via PATCH /api/notes/:id { attachments: [...note.attachments, newAttachment] } */}
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.docx,.doc,.txt,.json,.png,.jpg,.jpeg,.gif,.webp,.url"
          className="hidden"
          onChange={handleFileChange}
        />
      </div>

      {/* List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-1.5">
        {attachments.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-10 text-center px-3">
            <div className="w-10 h-10 rounded-xl bg-warm-200 flex items-center justify-center mb-3">
              <span className="material-symbols-outlined text-[20px] text-warm-400">
                attach_file
              </span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              No sources yet.
              <br />
              Click <strong className="font-semibold text-primary">+</strong> to add files or links.
            </p>
          </div>
        ) : (
          attachments.map((att) => {
            const cfg = TYPE_CFG[att.type] ?? TYPE_CFG.txt;
            const isActive = att.id === activeId;
            const size = formatSize(att.size_bytes);

            return (
              <div
                key={att.id}
                onClick={() => onSelect?.(att)}
                className={`
                  group relative flex items-start gap-2.5 p-2.5 rounded-xl
                  border cursor-pointer transition-all duration-150
                  ${
                    isActive
                      ? "bg-white border-primary/40 shadow-warm-sm"
                      : "bg-white/60 border-warm-400/40 hover:bg-white hover:border-primary/20 hover:shadow-warm-sm"
                  }
                `}
              >
                {/* File type icon */}
                <div
                  className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5 ${cfg.bg}`}
                >
                  <span className={`material-symbols-outlined text-[17px] ${cfg.color}`}>
                    {cfg.icon}
                  </span>
                </div>

                {/* Info */}
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-medium text-slate-700 truncate leading-snug">
                    {att.name}
                  </p>
                  <p className="text-[10px] text-slate-400 mt-0.5 leading-tight">
                    {formatDate(att.uploaded_at)}
                    {size && <span className="ml-1.5 text-warm-400">· {size}</span>}
                  </p>
                </div>

                {/* Actions: shown on hover */}

              </div>
            );
          })
        )}
      </div>

    </aside>
  );
}