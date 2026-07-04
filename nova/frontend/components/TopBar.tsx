"use client";

import { Bell } from "lucide-react";
import ThemeToggle from "./ThemeToggle";

export default function TopBar() {
  return (
    <header className="flex items-center justify-between px-6 md:px-10 py-5">
      <div>
        <p className="font-mono text-xs text-muted uppercase tracking-wider">Nova</p>
        <h1 className="font-display text-xl font-semibold">Dashboard</h1>
      </div>
      <div className="flex items-center gap-3">
        <button
          aria-label="Notifications"
          className="h-9 w-9 rounded-full flex items-center justify-center border border-border bg-surface hover:bg-surface2"
        >
          <Bell size={16} />
        </button>
        <ThemeToggle />
      </div>
    </header>
  );
}
