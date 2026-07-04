"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { api } from "@/lib/api";

interface Briefing {
  greeting: string;
  workload_summary: string;
  schedule: { title: string; start: string; location?: string }[];
  upcoming_reminders: { title: string; next_trigger: string }[];
}

export default function BriefingHero() {
  const [briefing, setBriefing] = useState<Briefing | null>(null);

  useEffect(() => {
    api
      .get("/briefing/morning")
      .then(({ data }) => setBriefing(data))
      .catch(() => setBriefing(null));
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
      className="rounded-2xl p-6 md:p-8 bg-surface border border-border shadow-card"
    >
      <p className="font-display text-2xl md:text-3xl font-semibold tracking-tight">
        {briefing?.greeting ?? "Good day! Here's your briefing."}
      </p>
      <p className="text-muted mt-2 font-body text-sm md:text-base">
        {briefing?.workload_summary ?? "Loading your day..."}
      </p>

      {briefing && briefing.schedule.length > 0 && (
        <div className="mt-5 flex flex-wrap gap-3">
          {briefing.schedule.slice(0, 4).map((event, idx) => (
            <div
              key={idx}
              className="px-3 py-2 rounded-xl bg-surface2 border border-border text-sm font-mono"
            >
              <span className="text-accent-1" style={{ color: "var(--accent-1)" }}>
                {new Date(event.start).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })}
              </span>{" "}
              <span className="font-body text-text">{event.title}</span>
            </div>
          ))}
        </div>
      )}
    </motion.div>
  );
}
