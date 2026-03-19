"use client";

import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";

interface TopNavProps {
  onMenuClick: () => void;
}

export default function TopNav({ onMenuClick }: TopNavProps) {
  const [search, setSearch] = useState("");
  const router = useRouter();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (search.trim()) router.push(`/search?q=${encodeURIComponent(search)}`);
  };

  return (
    <header className="h-14 flex-shrink-0 border-b border-warm-400/50 bg-warm-50/80 backdrop-blur-md flex items-center justify-between px-4 gap-4 sticky top-0 z-20">
      {/* Left: hamburger */}
      <button
        onClick={onMenuClick}
        className="p-2 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-warm-200 transition-colors"
        aria-label="Toggle sidebar"
      >
        <span className="material-symbols-outlined text-[22px]">menu</span>
      </button>

      {/* Center: search */}
      {/* <form onSubmit={handleSearch} className="flex-1 max-w-md">
        <div className="relative">
          <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-[18px] text-warm-400">
            search
          </span>
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search notes…"
            className="
              w-full h-9 pl-9 pr-4 text-sm rounded-xl
              bg-warm-200/70 border border-warm-400/40
              text-slate-700 placeholder:text-warm-400
              focus:outline-none focus:ring-2 focus:ring-primary/30 focus:bg-white
              transition-all duration-200
            "
          />
        </div>
      </form> */}

      {/* Right: actions */}
      <div className="flex items-center gap-2">
        {/* Avatar */}
        <button className="h-8 w-8 rounded-full bg-primary/15 border border-primary/20 flex items-center justify-center text-primary font-semibold text-sm hover:bg-primary/25 transition-colors flex-shrink-0">
          {/* TODO: Replace with actual user avatar when auth is implemented */}
          <span className="material-symbols-outlined text-[17px]">person</span>
        </button>
      </div>
    </header>
  );
}
