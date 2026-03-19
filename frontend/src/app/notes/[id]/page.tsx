"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { useRouter, useParams } from "next/navigation";
import AppShell from "@/components/layout/AppShell";
import NoteEditor from "@/components/editor/NoteEditor";
import NoteMeta from "@/components/editor/NoteMeta";
import SourcesSidebar from "@/components/editor/SourcesSidebar";
import NoteAIChat from "@/components/qa/NoteAIChat";
import Spinner from "@/components/ui/Spinner";
import { getNote, updateNote } from "@/lib/api/notes";
import type { Note, Attachment } from "@/lib/types";

export default function EditNotePage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [note, setNote] = useState<Note | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [activeAttId, setActiveAttId] = useState<string | undefined>();
  const saveTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    // TODO: BACKEND — getNote calls GET /api/notes/:id
    getNote(id)
      .then((n) => {
        if (n) {
          setNote(n);
          if (n.attachments.length > 0) setActiveAttId(n.attachments[0].id);
        } else {
          router.push("/notes");
        }
      })
      .finally(() => setLoading(false));
  }, [id, router]);

  const persist = useCallback(
    async (patch: Partial<Note>) => {
      if (!note) return;
      setSaving(true);
      try {
        // TODO: BACKEND — updateNote calls PATCH /api/notes/:id
        const updated = await updateNote(note.id, patch);
        setNote(updated);
      } finally {
        setSaving(false);
      }
    },
    [note]
  );

  const scheduleAutoSave = useCallback(
    (patch: Partial<Note>) => {
      if (saveTimer.current) clearTimeout(saveTimer.current);
      saveTimer.current = setTimeout(() => persist(patch), 1500);
    },
    [persist]
  );

  const handleAttachmentAdd = (files: FileList) => {
    // TODO: BACKEND — for each file call POST /api/upload, then PATCH /api/notes/:id
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
      if (!n) return n;
      const updated = { ...n, attachments: [...n.attachments, ...newAtts] };
      scheduleAutoSave({ attachments: updated.attachments });
      return updated;
    });
  };

  const handleAttachmentDelete = (attId: string) => {
    setNote((n) => {
      if (!n) return n;
      const updated = { ...n, attachments: n.attachments.filter((a) => a.id !== attId) };
      scheduleAutoSave({ attachments: updated.attachments });
      if (activeAttId === attId) setActiveAttId(updated.attachments[0]?.id);
      return updated;
    });
  };

  if (loading) {
    return (
      <AppShell>
        <div className="flex items-center justify-center h-full">
          <Spinner size="lg" />
        </div>
      </AppShell>
    );
  }

  if (!note) return null;

  return (
    <AppShell activeNoteId={note.id}>
      <div className="flex h-full overflow-hidden">

        {/* Sources sidebar */}
        <SourcesSidebar
          attachments={note.attachments}
          activeId={activeAttId}
          onSelect={(att) => setActiveAttId(att.id)}
          onAdd={handleAttachmentAdd}
          onDelete={handleAttachmentDelete}
        />

        {/* Editor */}
        <div className="flex-1 overflow-y-auto bg-white">
          <div className="max-w-3xl mx-auto px-8 py-8">
            <nav className="flex items-center gap-1.5 text-xs text-slate-400 mb-6">
              <button onClick={() => router.push("/")} className="hover:text-primary transition-colors">Home</button>
              <span className="material-symbols-outlined text-[13px]">chevron_right</span>
              <span className="text-slate-600 truncate max-w-[200px]">{note.title || "Untitled"}</span>
            </nav>

            <NoteMeta
              note={note}
              onTitleChange={(title) => {
                setNote((n) => (n ? { ...n, title } : n));
                scheduleAutoSave({ title });
              }}
              onTagAdd={(tag) => setNote((n) => (n ? { ...n, tags: [...n.tags, tag] } : n))}
              onTagRemove={(tag) => setNote((n) => (n ? { ...n, tags: n.tags.filter((t) => t !== tag) } : n))}
              saving={saving}
            />

            <NoteEditor
              content={note.content}
              onChange={(content) => {
                setNote((n) => (n ? { ...n, content } : n));
                scheduleAutoSave({ content });
              }}
              noteId={note.id}
            />
          </div>
        </div>
      </div>

      {/* Floating AI chat — scoped to this note */}
      <NoteAIChat note={{ id: note.id, title: note.title }} />
    </AppShell>
  );
}
