"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import AppShell from "@/components/layout/AppShell";
import Spinner from "@/components/ui/Spinner";
import EmptyState from "@/components/ui/EmptyState";
import { getNotes, restoreNote, permanentDeleteNote } from "@/lib/api/notes";
import type { Note } from "@/lib/types";

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const days = Math.floor(diff / 86400000);
  if (days === 0) return "today";
  if (days === 1) return "yesterday";
  if (days < 7) return `${days}d ago`;
  return new Date(iso).toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

export default function TrashPage() {
  const router = useRouter();
  const [notes, setNotes] = useState<Note[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionId, setActionId] = useState<string | null>(null);
  const [confirmId, setConfirmId] = useState<string | null>(null);

  useEffect(() => {
    // TODO: BACKEND — getNotes({ deleted: true }) calls GET /api/notes?deleted=true
    getNotes({ deleted: true })
      .then(setNotes)
      .finally(() => setLoading(false));
  }, []);

  const handleRestore = async (id: string) => {
    setActionId(id);
    try {
      // TODO: BACKEND — restoreNote calls PATCH /api/notes/:id { deleted: false }
      await restoreNote(id);
      setNotes((prev) => prev.filter((n) => n.id !== id));
    } finally {
      setActionId(null);
    }
  };

  const handlePermanentDelete = async (id: string) => {
    setActionId(id);
    setConfirmId(null);
    try {
      // TODO: BACKEND — permanentDeleteNote calls DELETE /api/notes/:id
      // This removes the note and all its attachments from storage permanently
      await permanentDeleteNote(id);
      setNotes((prev) => prev.filter((n) => n.id !== id));
    } finally {
      setActionId(null);
    }
  };

  return (
    <AppShell>
      <div className="max-w-2xl mx-auto px-6 py-8">

        {/* Header */}
        <div className="flex items-center gap-3 mb-8">
          <div className="w-9 h-9 rounded-xl bg-slate-100 flex items-center justify-center">
            <span className="material-symbols-outlined text-slate-500 text-[20px]">delete_outline</span>
          </div>
          <div>
            <h1
              className="text-2xl text-slate-800"
              style={{ fontFamily: "var(--font-display)" }}
            >
              Trash
            </h1>
            <p className="text-xs text-slate-400 mt-0.5">
              Notes here are soft-deleted — restore them or remove permanently.
            </p>
          </div>
        </div>

        {/* Content */}
        {loading ? (
          <div className="flex justify-center py-20">
            <Spinner size="lg" />
          </div>
        ) : notes.length === 0 ? (
          <EmptyState
            icon="delete_outline"
            title="Trash is empty"
            description="Deleted notes will appear here. You can restore or permanently remove them."
            action={
              <button
                onClick={() => router.push("/")}
                className="text-sm text-primary font-medium hover:underline"
              >
                ← Back to Home
              </button>
            }
          />
        ) : (
          <div className="space-y-2">
            {notes.map((note) => {
              const isActing = actionId === note.id;
              const isConfirming = confirmId === note.id;

              return (
                <div
                  key={note.id}
                  className={`
                    bg-white border border-warm-400/60 rounded-xl p-4
                    transition-opacity duration-200
                    ${isActing ? "opacity-40 pointer-events-none" : ""}
                  `}
                >
                  <div className="flex items-start justify-between gap-4">
                    {/* Note info */}
                    <div className="flex-1 min-w-0">
                      <h3 className="text-sm font-semibold text-slate-700 truncate">
                        {note.title || "Untitled"}
                      </h3>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-[11px] text-slate-400">
                          Deleted {timeAgo(note.updated_at)}
                        </span>
                        {note.attachments.length > 0 && (
                          <>
                            <span className="text-warm-300">·</span>
                            <span className="text-[11px] text-slate-400 flex items-center gap-1">
                              <span className="material-symbols-outlined text-[11px]">attach_file</span>
                              {note.attachments.length} source{note.attachments.length !== 1 ? "s" : ""}
                            </span>
                          </>
                        )}
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-2 flex-shrink-0">
                      {isActing ? (
                        <Spinner size="sm" />
                      ) : isConfirming ? (
                        /* Confirm permanent delete */
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-red-500 font-medium">Delete forever?</span>
                          <button
                            onClick={() => handlePermanentDelete(note.id)}
                            className="text-xs font-semibold text-white bg-red-500 hover:bg-red-600 px-2.5 py-1.5 rounded-lg transition-colors"
                          >
                            Confirm
                          </button>
                          <button
                            onClick={() => setConfirmId(null)}
                            className="text-xs font-medium text-slate-500 hover:text-slate-700 px-2 py-1.5 rounded-lg hover:bg-warm-100 transition-colors"
                          >
                            Cancel
                          </button>
                        </div>
                      ) : (
                        <>
                          {/* Restore */}
                          <button
                            onClick={() => handleRestore(note.id)}
                            title="Restore note"
                            className="flex items-center gap-1.5 text-xs font-medium text-primary bg-primary/8 hover:bg-primary/15 px-3 py-1.5 rounded-lg border border-primary/15 transition-all"
                          >
                            <span className="material-symbols-outlined text-[14px]">restore</span>
                            Restore
                          </button>
                          {/* Permanent delete */}
                          <button
                            onClick={() => setConfirmId(note.id)}
                            title="Delete permanently"
                            className="flex items-center gap-1.5 text-xs font-medium text-red-400 bg-red-50 hover:bg-red-100 px-3 py-1.5 rounded-lg border border-red-100 transition-all"
                          >
                            <span className="material-symbols-outlined text-[14px]">delete_forever</span>
                            Delete forever
                          </button>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </AppShell>
  );
}
