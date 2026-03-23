"use client";

import { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { ingestText, uploadFile } from "@/lib/api/upload";
import Spinner from "@/components/ui/Spinner";

interface StagedFile {
  id: string;
  file: File;
  name: string;
}

export default function HeroInput() {
  const [text, setText] = useState("");
  const [stagedFiles, setStagedFiles] = useState<StagedFile[]>([]);
  const [loading, setLoading] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  // ── Stage files locally — do NOT upload yet ──────────────────────────────
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files ?? []);
    if (!files.length) return;

    const newStaged: StagedFile[] = files.map((f) => ({
      id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
      file: f,
      name: f.name,
    }));
    setStagedFiles((prev) => [...prev, ...newStaged]);

    // reset input so same file can be re-selected
    if (fileRef.current) fileRef.current.value = "";
  };

  const removeStaged = (id: string) => {
    setStagedFiles((prev) => prev.filter((f) => f.id !== id));
  };

  // ── Process everything at once when Create is clicked ────────────────────
  const handleSubmit = async () => {
    const hasText = text.trim().length > 0;
    const hasFiles = stagedFiles.length > 0;
    if (!hasText && !hasFiles) return;

    setLoading(true);
    try {
      const promises: Promise<any>[] = [];

      if (hasText) {
        promises.push(ingestText(text.trim()));
      }

      for (const staged of stagedFiles) {
        const fd = new FormData();
        fd.append("file", staged.file);
        promises.push(uploadFile(fd));
      }

      await Promise.all(promises);

      setText("");
      setStagedFiles([]);
      router.refresh();
    } finally {
      setLoading(false);
    }
  };

  const hasContent = text.trim().length > 0 || stagedFiles.length > 0;

  return (
    <div className="w-full flex flex-col gap-3">
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
            placeholder="Drop URLs here or type a question…"
            rows={4}
            className="flex-1 bg-transparent border-none outline-none resize-none text-slate-700 placeholder:text-[#e4b27e] text-base leading-relaxed"
            onKeyDown={(e) => {
              if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) handleSubmit();
            }}
          />
        </div>

        {/* Staged files preview — shown before processing */}
        {stagedFiles.length > 0 && (
          <div className="px-4 pb-3 flex flex-wrap gap-2">
            {stagedFiles.map((sf) => (
              <div
                key={sf.id}
                className="flex items-center gap-1.5 bg-warm-100 border border-warm-300 text-slate-700 text-xs px-2.5 py-1 rounded-full"
              >
                <span className="material-symbols-outlined text-[13px] text-primary">
                  {sf.name.match(/\.(png|jpg|jpeg|gif|webp)$/i) ? "image" : "description"}
                </span>
                <span className="max-w-[160px] truncate">{sf.name}</span>
                <button
                  onClick={() => removeStaged(sf.id)}
                  className="ml-0.5 text-slate-400 hover:text-red-400 transition-colors"
                  disabled={loading}
                >
                  <span className="material-symbols-outlined text-[13px]">close</span>
                </button>
              </div>
            ))}
          </div>
        )}

        <div className="flex items-center justify-between px-4 py-3 border-t border-warm-300/60 bg-warm-50/50">
          <div className="flex items-center gap-1">
            <input
              ref={fileRef}
              type="file"
              accept=".pdf,.txt,.png,.jpg,.jpeg,.json,.docx,.pptx,.gif,.webp"
              multiple
              className="hidden"
              onChange={handleFileChange}
            />
            <IconBtn icon="attach_file" label="Attach file" onClick={() => fileRef.current?.click()} disabled={loading} />
            <IconBtn icon="image" label="Attach image" onClick={() => fileRef.current?.click()} disabled={loading} />
          </div>

          <button
            onClick={handleSubmit}
            disabled={!hasContent || loading}
            className="flex items-center gap-2 bg-primary text-white px-5 py-2 rounded-xl text-sm font-semibold hover:bg-primary-dark disabled:opacity-40 disabled:cursor-not-allowed transition-all duration-200 shadow-warm-sm hover:shadow-warm-md"
          >
            {loading ? (
              <Spinner size="sm" className="border-white/30 border-t-white" />
            ) : (
              <span className="material-symbols-outlined text-[16px]">send</span>
            )}
            {loading
              ? "Processing…"
              : `Create`
            }
          </button>
        </div>
      </div>
    </div>
  );
}

function IconBtn({ icon, label, onClick, disabled }: { icon: string; label: string; onClick: () => void; disabled?: boolean }) {
  return (
    <button
      type="button"
      title={label}
      onClick={onClick}
      disabled={disabled}
      className="p-2 rounded-lg transition-all duration-150 text-[#e4b27e] hover:text-primary hover:bg-primary/5 disabled:opacity-40"
    >
      <span className="material-symbols-outlined text-[19px]">{icon}</span>
    </button>
  );
}

