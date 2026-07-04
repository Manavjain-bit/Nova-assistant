import { create } from "zustand";

interface ThemeState {
  theme: "dark" | "light";
  toggle: () => void;
  setTheme: (t: "dark" | "light") => void;
}

export const useThemeStore = create<ThemeState>((set, get) => ({
  theme: "dark",
  toggle: () => {
    const next = get().theme === "dark" ? "light" : "dark";
    set({ theme: next });
    if (typeof document !== "undefined") {
      document.documentElement.classList.toggle("dark", next === "dark");
      localStorage.setItem("nova_theme", next);
    }
  },
  setTheme: (t) => {
    set({ theme: t });
    if (typeof document !== "undefined") {
      document.documentElement.classList.toggle("dark", t === "dark");
      localStorage.setItem("nova_theme", t);
    }
  },
}));
