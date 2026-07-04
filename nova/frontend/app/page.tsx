"use client";

import Link from "next/link";
import { motion } from "framer-motion";

export default function HomePage() {
  return (
    <main className="min-h-screen flex items-center justify-center px-4">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="text-center space-y-5"
      >
        <h1 className="font-display text-5xl font-semibold tracking-tight">Nova</h1>
        <p className="text-muted max-w-sm mx-auto">
          A calm, capable voice assistant for the work of running your day —
          tasks, habits, goals, and notes, all in one place.
        </p>
        <Link
          href="/login"
          className="inline-block mt-2 px-5 py-2.5 rounded-xl text-white text-sm font-medium"
          style={{ background: "linear-gradient(135deg, var(--accent-1), var(--accent-2))" }}
        >
          Get started
        </Link>
      </motion.div>
    </main>
  );
}
