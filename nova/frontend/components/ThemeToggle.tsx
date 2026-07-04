"use client";

import { useEffect } from "react";
import { Moon, Sun } from "lucide-react";
import { useThemeStore } from "@/store/useThemeStore";

export default function ThemeToggle() {
  const { theme, toggle, setTheme } = useThemeStore();

  useEffect(() => {
    const stored = typeof window !== "undefined" ? localStorage.getItem("nova_theme") : null;
    if (stored === "light" || stored === "dark") setTheme(stored);
    else setTheme("dark");
  }, [setTheme]);

  return (
    <button
      onClick={toggle}
      aria-label="Toggle theme"
      className="h-9 w-9 rounded-full flex items-center justify-center border border-border bg-surface hover:bg-surface2 text-text"
    >
      {theme === "dark" ? <Sun size={16} /> : <Moon size={16} />}
    </button>
  );
}
