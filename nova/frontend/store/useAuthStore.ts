import { create } from "zustand";

interface AuthState {
  token: string | null;
  setToken: (t: string | null) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: typeof window !== "undefined" ? localStorage.getItem("nova_token") : null,
  setToken: (t) => {
    if (typeof window !== "undefined") {
      if (t) localStorage.setItem("nova_token", t);
      else localStorage.removeItem("nova_token");
    }
    set({ token: t });
  },
}));
