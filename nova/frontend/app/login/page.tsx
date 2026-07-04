"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { api } from "@/lib/api";
import { useAuthStore } from "@/store/useAuthStore";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [mode, setMode] = useState<"login" | "register">("login");
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const setToken = useAuthStore((s) => s.setToken);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      if (mode === "register") {
        await api.post("/auth/register", { email, password });
      }
      const form = new URLSearchParams();
      form.set("username", email);
      form.set("password", password);
      const { data } = await api.post("/auth/login", form, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      });
      setToken(data.access_token);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Something went wrong. Try again.");
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <motion.form
        onSubmit={handleSubmit}
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-sm rounded-2xl border border-border bg-surface p-8 shadow-card"
      >
        <h1 className="font-display text-2xl font-semibold mb-1">Nova</h1>
        <p className="text-sm text-muted mb-6">
          {mode === "login" ? "Welcome back." : "Create your account."}
        </p>

        <label className="block text-xs font-mono text-muted mb-1">Email</label>
        <input
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full mb-4 px-3 py-2 rounded-xl bg-surface2 border border-border text-sm outline-none focus:ring-2"
          style={{ "--tw-ring-color": "var(--accent-1)" } as React.CSSProperties}
        />

        <label className="block text-xs font-mono text-muted mb-1">Password</label>
        <input
          type="password"
          required
          minLength={8}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full mb-4 px-3 py-2 rounded-xl bg-surface2 border border-border text-sm outline-none focus:ring-2"
        />

        {error && <p className="text-sm mb-3" style={{ color: "var(--danger)" }}>{error}</p>}

        <button
          type="submit"
          className="w-full py-2.5 rounded-xl text-white text-sm font-medium"
          style={{ background: "linear-gradient(135deg, var(--accent-1), var(--accent-2))" }}
        >
          {mode === "login" ? "Sign in" : "Create account"}
        </button>

        <button
          type="button"
          onClick={() => setMode(mode === "login" ? "register" : "login")}
          className="w-full mt-3 text-xs text-muted hover:text-text"
        >
          {mode === "login" ? "Need an account? Sign up" : "Already have an account? Sign in"}
        </button>
      </motion.form>
    </div>
  );
}
