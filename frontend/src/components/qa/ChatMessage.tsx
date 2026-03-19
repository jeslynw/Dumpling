import type { ChatMessage } from "@/lib/types";

interface ChatMessageProps {
  message: ChatMessage;
}

function timeStr(iso: string) {
  return new Date(iso).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

export default function ChatMessageBubble({ message }: ChatMessageProps) {
  const isUser = message.role === "user";

  if (isUser) {
    return (
      <div className="flex justify-end gap-3 chat-bubble-enter">
        <div className="max-w-[80%]">
          <div className="bg-primary text-white px-4 py-2.5 rounded-2xl rounded-tr-sm text-sm leading-relaxed shadow-warm-sm">
            {message.content}
          </div>
          <p className="text-[10px] text-slate-300 mt-1 text-right pr-1">
            {timeStr(message.timestamp)}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex gap-3 chat-bubble-enter">
      <div className="w-7 h-7 rounded-full bg-primary/10 flex-shrink-0 flex items-center justify-center mt-0.5">
        <span className="material-symbols-outlined text-primary text-[15px]">auto_awesome</span>
      </div>
      <div className="max-w-[85%]">
        <div className="bg-white border border-warm-400/60 px-4 py-3 rounded-2xl rounded-tl-sm text-sm text-slate-700 leading-relaxed shadow-warm-sm">
          {message.content}
        </div>
        {message.sources && message.sources.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-2">
            {message.sources.map((s) => (
              <span
                key={s.id}
                className="inline-flex items-center gap-1 text-[10px] font-medium bg-primary/8 text-primary border border-primary/15 px-2 py-0.5 rounded-full"
              >
                <span className="material-symbols-outlined text-[10px]">description</span>
                {s.file_name}
              </span>
            ))}
          </div>
        )}
        <p className="text-[10px] text-slate-300 mt-1 pl-1">
          {`ai-${Date.now()}`}
        </p>
      </div>
    </div>
  );
}
