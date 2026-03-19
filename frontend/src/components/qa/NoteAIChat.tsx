"use client";

import { useState, useRef, useEffect } from "react";
import ChatMessageBubble from "@/components/qa/ChatMessage";
import Spinner from "@/components/ui/Spinner";
import { queryRAG } from "@/lib/api/search";
import type { ChatMessage, Note } from "@/lib/types";

interface NoteAIChatProps {
  note: Pick<Note, "id" | "title">;
}

export default function NoteAIChat({ note }: NoteAIChatProps) {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      role: "assistant",
      content: `Hi! I'm scoped to your note "${note.title}". Ask me anything about it — I'll answer using its content and attached sources.`,
      timestamp: new Date().toISOString(),
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  /* Load suggestions once when opened */
  useEffect(() => {
    if (open && suggestions.length === 0) {
      setSuggestions(['Summarize this note']);
    }
  }, [open, note.id, suggestions.length]);

  /* Scroll to bottom on new messages */
  useEffect(() => {
    if (open) bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading, open]);

  /* Focus input when opened */
  useEffect(() => {
    if (open) setTimeout(() => inputRef.current?.focus(), 120);
  }, [open]);

  const sendMessage = async (text: string) => {
    if (!text.trim() || loading) return;

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: text.trim(),
      timestamp: new Date().toISOString(),
    };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    setLoading(true);

    try {
      // TODO: BACKEND — queryRAG calls POST /api/search
      // Passing context_note_ids: [note.id] scopes the RAG retrieval to this note's content
      const result = await queryRAG({ query: text.trim(), context_note_ids: [note.id] });
      setMessages((m) => [
        ...m,
        {
          id: `ai-${Date.now()}`,
          role: "assistant",
          content: result.answer,
          sources: result.sources,
          timestamp: new Date().toISOString(),
        },
      ]);
    } catch {
      setMessages((m) => [
        ...m,
        {
          id: `err-${Date.now()}`,
          role: "assistant",
          content: "Couldn't reach the AI backend — please try again.",
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* ── Chat panel ── */}
      <div
        className={`
          fixed bottom-20 right-9 z-50
          w-[460px] h-[500px]
          bg-white rounded-2xl shadow-warm-xl border border-warm-400/60
          flex flex-col overflow-hidden
          transition-all duration-300 origin-bottom-left
          ${open
            ? "opacity-100 scale-100 pointer-events-auto"
            : "opacity-0 scale-95 pointer-events-none"
          }
        `}
      >
        {/* Panel header */}
        <div className="flex items-center justify-between gap-3 px-4 py-3 bg-primary text-white flex-shrink-0">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-full bg-white/20 flex items-center justify-center flex-shrink-0">
              <span className="material-symbols-outlined text-white text-[15px]">smart_toy</span>
            </div>
            <div className="min-w-0">
              <p className="text-base font-bold leading-tight">Chat with Bao</p>
            </div>
          </div>
          <div className="flex items-center gap-1 flex-shrink-0">
            {/* Clear chat */}
            <button
              onClick={() =>
                setMessages([
                  {
                    id: "welcome-reset",
                    role: "assistant",
                    content: `Chat cleared. Still scoped to "${note.title}". What would you like to know?`,
                    timestamp: new Date().toISOString(),
                  },
                ])
              }
              title="Clear chat"
              className="p-1 rounded-full hover:bg-white/15 transition-colors"
            >
              <span className="material-symbols-outlined text-[16px]">delete_sweep</span>
            </button>
            {/* Close */}
            <button
              onClick={() => setOpen(false)}
              title="Close"
              className="p-1 rounded-full hover:bg-white/15 transition-colors"
            >
              <span className="material-symbols-outlined text-[16px]">close</span>
            </button>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4 min-h-0">
          {messages.map((msg) => (
            <ChatMessageBubble key={msg.id} message={msg} />
          ))}

          {/* Typing dots */}
          {loading && (
            <div className="flex gap-2.5 chat-bubble-enter">
              <div className="w-6 h-6 rounded-full bg-primary/10 flex-shrink-0 flex items-center justify-center">
                <span className="material-symbols-outlined text-primary text-[13px]">auto_awesome</span>
              </div>
              <div className="bg-warm-50 border border-warm-400/60 px-3 py-2.5 rounded-2xl rounded-tl-sm">
                <div className="flex items-center gap-1">
                  <span className="typing-dot" />
                  <span className="typing-dot" />
                  <span className="typing-dot" />
                </div>
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        {/* Suggestion pills — only before first user message */}
        {suggestions.length > 0 && messages.filter((m) => m.role === "user").length === 0 && (
          <div className="px-4 pb-2 flex flex-wrap gap-1.5 flex-shrink-0">
            {suggestions.map((s) => (
              <button
                key={s}
                onClick={() => sendMessage(s)}
                className="text-[11px] font-medium bg-warm-100 border border-warm-400/60 text-slate-600 px-2.5 py-1 rounded-full hover:bg-primary/8 hover:border-primary/30 hover:text-primary transition-all"
              >
                {s}
              </button>
            ))}
          </div>
        )}

        {/* Input row */}
        <div className="flex-shrink-0 flex items-center gap-2 px-3 py-3 border-t border-warm-300/60">
          <input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) sendMessage(input);
            }}
            placeholder="Ask about this note…"
            className="flex-1 h-9 px-3 text-sm bg-warm-50 border border-warm-400/50 rounded-xl text-slate-700 placeholder:text-warm-400 focus:outline-none focus:ring-2 focus:ring-primary/25 focus:bg-white transition-all"
          />
          <button
            onClick={() => sendMessage(input)}
            disabled={!input.trim() || loading}
            className="w-9 h-9 flex items-center justify-center rounded-xl bg-primary text-white hover:bg-primary-dark disabled:opacity-30 disabled:cursor-not-allowed transition-all flex-shrink-0"
          >
            {loading ? (
              <Spinner size="sm" className="border-white/30 border-t-white" />
            ) : (
              <span className="material-symbols-outlined text-[17px]">send</span>
            )}
          </button>
        </div>
      </div>

      {/* ── FAB trigger button ── */}
      <button
        onClick={() => setOpen((o) => !o)}
        title="Ask AI about this note"
        className={`
          fixed bottom-6 right-9
          z-50 w-12 h-12 rounded-full shadow-warm-lg
          flex items-center justify-center
          transition-all duration-200 active:scale-95
          ${open
            ? "bg-slate-700 hover:bg-slate-800 rotate-0"
            : "bg-primary hover:bg-primary-dark hover:shadow-glow"
          }
        `}
      >
        <span
          className={`material-symbols-outlined text-white text-[22px] transition-transform duration-200 ${
            open ? "rotate-0" : ""
          }`}
        >
          {open ? "close" : "chat_bubble"}
        </span>

        {/* Tooltip */}
        {!open && (
          <span className="absolute -top-9 left-1/2 -translate-x-1/2 bg-slate-800 text-white text-[10px] px-2 py-1 rounded-md whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity">
            Ask AI
          </span>
        )}
      </button>
    </>
  );
}
