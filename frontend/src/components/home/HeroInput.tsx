"use client";

import { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { createNote } from "@/lib/api/notes";
import { scrapeUrl } from "@/lib/api/upload";
import Spinner from "@/components/ui/Spinner";

export default function HeroInput() {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [mode] = useState<"text">("text");
  const fileRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  const handleSubmit = async () => {
    if (!text.trim()) return;
    setLoading(true);
    try {
      // Only text mode now
      const note = await createNote({ content: text.trim(), title: "New Note" });
      router.push(`//${note.id}`);
    } finally {
      setLoading(false);
    }
  };
  
  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setLoading(true);
    try {
      // TODO: BACKEND — uploadFile calls POST /api/upload with FormData
      const { uploadFile } = await import("@/lib/api/upload");
      const fd = new FormData();
      fd.append("file", file);
      await uploadFile(fd);
      router.push("/");
    } finally {
      setLoading(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  };

  return (
    <div className="w-full bg-white border border-warm-400/70 rounded-2xl shadow-warm-lg overflow-hidden focus-within:ring-2 focus-within:ring-primary/20 focus-within:border-primary/30 transition-all duration-200">
      <div className="flex items-start gap-3 p-4">
        <div className="pt-1 flex-shrink-0">
        <span className="material-symbols-outlined text-[#e4b27e] text-[22px]">
            psychology
          </span>

        </div>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Drop resources here or type a question…"
          rows={4}
          className="
            flex-1 bg-transparent border-none outline-none resize-none
            text-slate-700  placeholder:text-[#e4b27e]
            text-base leading-relaxed
          "
          onKeyDown={(e) => {
            if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) handleSubmit();
          }}
        />
      </div>

      <div className="flex items-center justify-between px-4 py-3 border-t border-warm-300/60 bg-warm-50/50">
        <div className="flex items-center gap-1">
          {/* File attach */}
          <input
            ref={fileRef}
            type="file"
            accept=".pdf,.txt,.png,.jpg,.jpeg,.json"
            className="hidden"
            onChange={handleFileChange}
          />
          <IconBtn
            icon="attach_file"
            label="Attach file"
            onClick={() => fileRef.current?.click()}
          />
          {/* Image */}
          <IconBtn
            icon="image"
            label="Attach image"
            onClick={() => fileRef.current?.click()}
          />
        </div>

        <button
          onClick={handleSubmit}
          disabled={!text.trim() || loading}
          className="
            flex items-center gap-2 bg-primary text-white
            px-5 py-2 rounded-xl text-sm font-semibold
            hover:bg-primary-dark disabled:opacity-40 disabled:cursor-not-allowed
            transition-all duration-200 shadow-warm-sm hover:shadow-warm-md
          "
        >
          {loading ? (
            <Spinner size="sm" className="border-white/30 border-t-white" />
          ) : (
            <span className="material-symbols-outlined text-[16px]">send</span>
          )}
          {loading ? "Processing…" : "Create"}
        </button>
      </div>
    </div>
  );
}

function IconBtn({
  icon,
  label,
  onClick,
  active,
}: {
  icon: string;
  label: string;
  onClick: () => void;
  active?: boolean;
}) {
  return (
    <button
      type="button"
      title={label}
      onClick={onClick}
      className={`p-2 rounded-lg transition-all duration-150 ${
        active
          ? "text-primary bg-primary/10"
          : "text-[#e4b27e] hover:text-primary hover:bg-primary/5"
      }`}
    >
      <span className="material-symbols-outlined text-[19px]">{icon}</span>
    </button>
  );
}
