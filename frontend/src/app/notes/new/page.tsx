"use client";

import { useState, useCallback, useRef } from "react";
import { useRouter } from "next/navigation";
import AppShell from "@/components/layout/AppShell";
import NoteEditor from "@/components/editor/NoteEditor";
import NoteMeta from "@/components/editor/NoteMeta";
import SourcesSidebar from "@/components/editor/SourcesSidebar";
import NoteAIChat from "@/components/qa/NoteAIChat";
import { createNote, updateNote } from "@/lib/api/notes";
import type { Note, Attachment } from "@/lib/types";

export default function NewNotePage() {
  const router = useRouter();
  const [note, setNote] = useState<Partial<Note>>({
    title: "",
    content: "",
    attachments: [],
    tags: [],
  });
  const [saving, setSaving] = useState(false);
  const [savedId, setSavedId] = useState<string | null>(null);
  const [activeAttId, setActiveAttId] = useState<string | undefined>();
  const saveTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const persist = useCallback(
    async (patch: Partial<Note>) => {
      setSaving(true);
      try {
        if (savedId) {
          // TODO: BACKEND — updateNote calls PATCH /api/notes/:id
          await updateNote(savedId, patch);
        } else {
          // TODO: BACKEND — createNote calls POST /api/notes
          const created = await createNote({
            title: patch.title ?? "",
            content: patch.content ?? "",
          });
          setSavedId(created.id);
          setNote((n) => ({ ...n, ...created }));
        }
      } finally {
        setSaving(false);
      }
    },
    [savedId]
  );

  const scheduleAutoSave = useCallback(
    (patch: Partial<Note>) => {
      if (saveTimer.current) clearTimeout(saveTimer.current);
      saveTimer.current = setTimeout(() => persist(patch), 1500);
    },
    [persist]
  );

  const handleAttachmentAdd = (files: FileList) => {
    // TODO: BACKEND — call POST /api/upload for each file, then PATCH /api/notes/:id
    const newAtts: Attachment[] = Array.from(files).map((f) => {
      const ext = f.name.split(".").pop()?.toLowerCase() ?? "";
      const type = (
        ext === "pdf" ? "pdf"
        : ext === "docx" || ext === "doc" ? "docx"
        : ext === "json" ? "json"
        : ext === "txt" ? "txt"
        : ["png","jpg","jpeg","gif","webp"].includes(ext) ? "image"
        : "txt"
      ) as Attachment["type"];
      return {
        id: `att-new-${Date.now()}-${Math.random().toString(36).slice(2)}`,
        name: f.name,
        type,
        uploaded_at: new Date().toISOString(),
        size_bytes: f.size,
      };
    });
    setNote((n) => {
      const updated = { ...n, attachments: [...(n.attachments ?? []), ...newAtts] };
      scheduleAutoSave({ attachments: updated.attachments });
      return updated;
    });
    if (!activeAttId && newAtts.length > 0) setActiveAttId(newAtts[0].id);
  };

  const handleAttachmentDelete = (attId: string) => {
    setNote((n) => {
      const updated = { ...n, attachments: (n.attachments ?? []).filter((a) => a.id !== attId) };
      scheduleAutoSave({ attachments: updated.attachments });
      if (activeAttId === attId) setActiveAttId(updated.attachments?.[0]?.id);
      return updated;
    });
  };

  const chatNote = { id: savedId ?? "new-note", title: note.title || "New Note" };

  return (
    <AppShell activeNoteId={savedId ?? undefined}>
      <div className="flex h-full overflow-hidden">

        {/* Sources sidebar */}
        <SourcesSidebar
          attachments={note.attachments ?? []}
          activeId={activeAttId}
          onSelect={(att) => setActiveAttId(att.id)}
          onAdd={handleAttachmentAdd}
          onDelete={handleAttachmentDelete}
        />

        {/* Editor */}
        <div className="flex-1 overflow-y-auto bg-white">
          <div className="max-w-3xl mx-auto px-8 py-8">
            <nav className="flex items-center gap-1.5 text-xs text-slate-400 mb-6">
              <button onClick={() => router.push("/")} className="hover:text-primary transition-colors">
                Home
              </button>
              <span className="material-symbols-outlined text-[13px]">chevron_right</span>
              <span className="text-slate-600">New Note</span>
            </nav>

            <NoteMeta
              note={note}
              onTitleChange={(title) => {
                setNote((n) => ({ ...n, title }));
                scheduleAutoSave({ title });
              }}
              onTagAdd={(tag) => setNote((n) => ({ ...n, tags: [...(n.tags ?? []), tag] }))}
              onTagRemove={(tag) => setNote((n) => ({ ...n, tags: (n.tags ?? []).filter((t) => t !== tag) }))}
              saving={saving}
            />

            <NoteEditor
              content={note.content}
              onChange={(content) => {
                setNote((n) => ({ ...n, content }));
                scheduleAutoSave({ content });
              }}
              noteId={savedId ?? undefined}
            />
          </div>
        </div>
      </div>

      {/* Floating AI chat scoped to this note */}
      <NoteAIChat note={chatNote} />
    </AppShell>
  );
}
