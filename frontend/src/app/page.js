"use client";

import Sidebar from "@/components/Sidebar";
import Homepage from "./Homepage";

export default function page() {
  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <Homepage />
    </div>
  );
}
