"use client";

import { useState } from "react";
import type { ReactNode } from "react";
import Sidebar from "./Sidebar";
import TopNav from "./TopNav";

interface AppShellProps {
  children: ReactNode;
  activeNoteId?: string;
}

export default function AppShell({ children, activeNoteId }: AppShellProps) {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div className="flex h-screen overflow-hidden bg-bg-light">
      <Sidebar open={sidebarOpen} activeNoteId={activeNoteId} />
      <div className="flex flex-1 flex-col overflow-hidden min-w-0">
        <TopNav onMenuClick={() => setSidebarOpen((o) => !o)} />
        <main className="flex-1 overflow-y-auto">{children}</main>
      </div>
    </div>
  );
}
