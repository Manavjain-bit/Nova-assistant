"use client";

import { LayoutGrid, CheckSquare, Repeat, Target, StickyNote, Bell, Sparkles } from "lucide-react";

const NAV_ITEMS = [
  { icon: LayoutGrid, label: "Today" },
  { icon: CheckSquare, label: "Tasks" },
  { icon: Repeat, label: "Habits" },
  { icon: Target, label: "Goals" },
  { icon: StickyNote, label: "Notes" },
  { icon: Bell, label: "Alerts" },
];

export default function Sidebar() {
  return (
    <aside className="hidden md:flex flex-col items-center w-16 py-6 gap-8 border-r border-border bg-surface">
      <div
        className="h-9 w-9 rounded-xl flex items-center justify-center"
        style={{ background: "linear-gradient(135deg, var(--accent-1), var(--accent-2))" }}
      >
        <Sparkles size={18} className="text-white" />
      </div>
      <nav className="flex flex-col gap-5">
        {NAV_ITEMS.map(({ icon: Icon, label }, i) => (
          <button
            key={label}
            aria-label={label}
            className={`h-10 w-10 rounded-xl flex items-center justify-center transition-colors ${
              i === 0 ? "bg-surface2 text-accent-1" : "text-muted hover:bg-surface2 hover:text-text"
            }`}
            style={i === 0 ? { color: "var(--accent-1)" } : undefined}
          >
            <Icon size={18} />
          </button>
        ))}
      </nav>
    </aside>
  );
}
