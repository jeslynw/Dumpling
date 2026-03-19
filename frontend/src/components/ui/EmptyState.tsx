import type { ReactNode } from "react";

interface EmptyStateProps {
  icon?: string;
  title: string;
  description?: string;
  action?: ReactNode;
}

export default function EmptyState({
  icon = "notes",
  title,
  description,
  action,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-20 px-6 text-center">
      <div className="w-16 h-16 rounded-2xl bg-warm-200 flex items-center justify-center mb-5">
        <span className="material-symbols-outlined text-[32px] text-warm-400">
          {icon}
        </span>
      </div>
      <h3
        className="text-lg font-normal text-slate-700 mb-1"
        style={{ fontFamily: "var(--font-display)" }}
      >
        {title}
      </h3>
      {description && (
        <p className="text-sm text-slate-400 max-w-xs mb-6">{description}</p>
      )}
      {action}
    </div>
  );
}
