"use client";

import Link from "next/link";
import Image from "next/image";
import { useRouter, usePathname } from "next/navigation";
import { useEffect, useState, useCallback } from "react";
import { getNotes, deleteNote } from "@/lib/api/notes";
import type { Note } from "@/lib/types";

interface SidebarProps {
  open: boolean;
  activeNoteId?: string;
}

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  if (days === 1) return "yesterday";
  if (days < 7) return `${days}d ago`;
  return new Date(iso).toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

export default function Sidebar({ open, activeNoteId }: SidebarProps) {
  const router = useRouter();
  const pathname = usePathname();
  const [notes, setNotes] = useState<Note[]>([]);
  const [loading, setLoading] = useState(true);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const loadNotes = useCallback(() => {
    // TODO: BACKEND — getNotes calls GET /api/notes (excludes deleted by default)
    getNotes().then(setNotes).finally(() => setLoading(false));
  }, []);

  useEffect(() => { loadNotes(); }, [loadNotes]);

  const handleDelete = async (e: React.MouseEvent, noteId: string) => {
    e.preventDefault(); // don't navigate
    e.stopPropagation();
    setDeletingId(noteId);
    try {
      // TODO: BACKEND — deleteNote calls PATCH /api/notes/:id { deleted: true }
      await deleteNote(noteId);
      setNotes((prev) => prev.filter((n) => n.id !== noteId));
      // If we just deleted the active note, go home
      if (activeNoteId === noteId || pathname === `/notes/${noteId}`) {
        router.push("/");
      }
    } finally {
      setDeletingId(null);
    }
  };

  const isHome = pathname === "/";
  const isTrash = pathname === "/trash";
  const isChat = pathname === "/chat" || pathname.startsWith("/chat");

  return (
    <aside
      className={`
        flex flex-col border-r border-warm-400/60 bg-warm-50
        transition-all duration-300 ease-in-out flex-shrink-0
        ${open ? "w-60" : "w-0 overflow-hidden"}
      `}
    >
      {/* Logo */}
      <div className="flex items-center gap-3 px-5 py-5 border-b border-warm-400/40 flex-shrink-0">
        {/* TODO: Replace with <Image src="/logo.svg" …/> when logo asset is ready */}
        <Image src="/dumpling.png" alt="Logo" width={40} height={40} />        
        <span
          className="font-display text-2xl font-normal tracking-tight text-slate-800 whitespace-nowrap ml-2"
          style={{ fontFamily: "var(--font-display)" }}
        >
          Dumpling
        </span>
      </div>

      {/* Fixed nav: Home + Trash */}
      <div className="px-3 pt-3 pb-2 flex-shrink-0 space-y-0.5">
        <NavLink href="/" icon="home" label="Home" active={isHome} />
        <NavLink href="/trash" icon="delete_outline" label="Trash" active={isTrash} />
        <NavLink href="/chat" icon="forum" label="Ask Dumpling AI" active={isChat} />
      </div>

      {/* Notes section header */}
      <div className="flex items-center justify-between px-4 py-2 flex-shrink-0">
        <p className="text-[10px] font-bold uppercase tracking-widest text-slate-400 select-none">
          Notes
        </p>
        <button
          onClick={() => router.push("/notes/new")}
          title="New note"
          className="w-5 h-5 flex items-center justify-center rounded-md text-slate-400 hover:text-primary hover:bg-primary/10 transition-all"
        >
          <span className="material-symbols-outlined text-[16px]">add</span>
        </button>
      </div>

      {/* Scrollable note list */}
      <div className="flex-1 overflow-y-auto px-2 pb-2 space-y-0.5 min-h-0">
        {loading ? (
          <div className="space-y-1.5 px-2 pt-1">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="skeleton h-9 rounded-lg" />
            ))}
          </div>
        ) : notes.length === 0 ? (
          <p className="text-xs text-slate-400 text-center py-6 px-3">
            No notes yet. Click + to create one.
          </p>
        ) : (
          notes.map((note) => {
            const isActive =
              activeNoteId === note.id ||
              (!activeNoteId && pathname === `/notes/${note.id}`);
            const isDeleting = deletingId === note.id;

            return (
              <div key={note.id} className="relative group/row">
                <Link
                  href={`/notes/${note.id}`}
                  className={`
                    flex flex-col gap-0.5 px-3 py-2 rounded-lg pr-8
                    transition-all duration-150 cursor-pointer
                    border-l-2 -ml-px pl-[11px]
                    ${isActive
                      ? "bg-primary/5 border-primary"
                      : "hover:bg-[warm-200] border-transparent"
                    }
                    ${isDeleting ? "opacity-40 pointer-events-none" : ""}
                  `}
                >
                  <span
                    className={`text-sm leading-snug line-clamp-1 font-medium transition-colors ${
                      isActive ? "text-primary" : "text-slate-700 group-hover/row:text-slate-900"
                    }`}
                  >
                    {note.title || "Untitled"}
                  </span>
                  <span className="text-[13px] text-slate-400">
                    {timeAgo(note.updated_at)}
                    {note.attachments.length > 0 && (
                      <span className="ml-1.5 text-primary">
                        · {note.attachments.length} source{note.attachments.length !== 1 ? "s" : ""}
                      </span>
                    )}
                  </span>
                </Link>

                {/* Delete button — revealed on row hover */}
                <button
                  onClick={(e) => handleDelete(e, note.id)}
                  title="Move to Trash"
                  disabled={isDeleting}
                  className="
                    absolute right-1.5 top-1/2 -translate-y-1/2
                    w-6 h-6 flex items-center justify-center rounded-md
                    text-slate-300 hover:text-red-400 hover:bg-red-50
                    opacity-0 group-hover/row:opacity-100
                    transition-all duration-150 disabled:opacity-30
                  "
                >
                  {isDeleting ? (
                    <span className="material-symbols-outlined text-[13px] animate-spin-slow">sync</span>
                  ) : (
                    <span className="material-symbols-outlined text-[13px]">delete</span>
                  )}
                </button>
              </div>
            );
          })
        )}
      </div>

      {/* New Note CTA */}
      <div className="px-3 py-4 border-t border-warm-400/40 flex-shrink-0">
        <button
          onClick={() => router.push("/notes/new")}
          className="
            w-full flex items-center justify-center gap-2
            bg-primary text-white py-2.5 rounded-xl
            text-sm font-medium tracking-wide
            hover:bg-primary-dark transition-colors duration-200
            shadow-warm-sm hover:shadow-warm-md
          "
        >
          <span className="material-symbols-outlined text-[18px]">add</span>
          New Note
        </button>
      </div>
    </aside>
  );
}

function NavLink({
  href, icon, label, active,
}: {
  href: string; icon: string; label: string; active: boolean;
}) {
  return (
    <Link
      href={href}
      className={`
        group flex items-center gap-3 px-3 py-2 rounded-lg text-sm
        transition-all duration-150
        ${active
          ? "bg-primary/10 text-primary font-medium"
          : "text-slate-500 hover:bg-warm-100 hover:text-slate-700"
        }
      `}
    >
      <span className={`material-symbols-outlined text-[18px] flex-shrink-0 ${active ? "text-primary" : "text-slate-400 group-hover:text-slate-600"}`}>
        {icon}
      </span>
      <span className="whitespace-nowrap">{label}</span>
    </Link>
  );
}
