"use client";

import { useState, useEffect, useRef, Suspense } from "react";
import AppShell from "@/components/layout/AppShell";
import ChatMessageBubble from "@/components/qa/ChatMessage";
import Spinner from "@/components/ui/Spinner";
import { queryRAG } from "@/lib/api/search";
import type { ChatMessage } from "@/lib/types";

function GlobalChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      role: "assistant",
      content:
        "Hi! I have access to all your notes. Ask me anything — I'll search across your entire knowledge base.",
      timestamp: new Date().toISOString(),
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

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
      const result = await queryRAG({ query: text.trim() });
      const aiMsg: ChatMessage = {
        id: `ai-${Date.now()}`,
        role: "assistant",
        content: result.answer,
        sources: result.sources,
        timestamp: new Date().toISOString(),
      };
      setMessages((m) => [...m, aiMsg]);
    } catch {
      setMessages((m) => [
        ...m,
        {
          id: `err-${Date.now()}`,
          role: "assistant",
          content: "Sorry, I couldn't reach the AI backend. Please try again.",
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full max-w-2xl mx-auto px-4 py-6">
      {/* Header */}
      <div className="mb-4 flex-shrink-0">
        <div className="flex items-center gap-3 mb-1">
          <div className="w-9 h-9 rounded-xl bg-primary flex items-center justify-center shadow-warm-sm">
            <span className="material-symbols-outlined text-white text-[18px]">smart_toy</span>
          </div>
          <div>
            <h1
              className="text-lg text-slate-800 leading-tight"
              style={{ fontFamily: "var(--font-display)" }}
            >
              Chat with Bao
            </h1>
            <div className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse-soft" />
              <span className="text-[11px] text-slate-400">Online · Processing your notes</span>
            </div>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-5 pb-4 min-h-0">
        {messages.map((msg) => (
          <ChatMessageBubble key={msg.id} message={msg} />
        ))}

        {/* Typing indicator */}
        {loading && (
          <div className="flex gap-3 chat-bubble-enter">
            <div className="w-7 h-7 rounded-full bg-primary/10 flex-shrink-0 flex items-center justify-center">
              <span className="material-symbols-outlined text-primary text-[15px]">auto_awesome</span>
            </div>
            <div className="bg-white border border-warm-400/60 px-4 py-3 rounded-2xl rounded-tl-sm shadow-warm-sm">
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

      {/* Input */}
      <div className="flex-shrink-0 flex items-center gap-2 bg-white border border-warm-400/60 rounded-2xl px-3 py-2 shadow-warm-sm focus-within:ring-2 focus-within:ring-primary/20">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && sendMessage(input)}
          placeholder="Ask anything about your notes…"
          className="flex-1 bg-transparent text-sm text-slate-700 placeholder:text-warm-400 border-none outline-none"
        />
        <button
          onClick={() => sendMessage(input)}
          disabled={!input.trim() || loading}
          className="p-2 rounded-xl bg-primary text-white hover:bg-primary-dark disabled:opacity-30 disabled:cursor-not-allowed transition-all"
        >
          {loading ? (
            <Spinner size="sm" className="border-white/30 border-t-white" />
          ) : (
            <span className="material-symbols-outlined text-[18px]">send</span>
          )}
        </button>
      </div>
    </div>
  );
}

export default function ChatPage() {
  return (
    <AppShell>
      <Suspense
        fallback={
          <div className="flex items-center justify-center h-full">
            <Spinner size="lg" />
          </div>
        }
      >
        <GlobalChat />
      </Suspense>
    </AppShell>
  );
}
