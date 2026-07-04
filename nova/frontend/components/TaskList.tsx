"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { api } from "@/lib/api";

interface Task {
  id: number;
  title: string;
  status: string;
  priority: string;
  priority_score: number;
  due_date: string | null;
}

const PRIORITY_COLOR: Record<string, string> = {
  urgent: "var(--danger)",
  high: "var(--warning)",
  medium: "var(--accent-1)",
  low: "var(--text-muted)",
};

export default function TaskList() {
  const [tasks, setTasks] = useState<Task[]>([]);

  useEffect(() => {
    api
      .get("/tasks", { params: { prioritized: true } })
      .then(({ data }) => setTasks(data))
      .catch(() => setTasks([]));
  }, []);

  return (
    <div className="rounded-2xl p-6 bg-surface border border-border shadow-card">
      <div className="flex items-center justify-between mb-4">
        <h2 className="font-display text-lg font-semibold">Top priorities</h2>
        <span className="text-xs font-mono text-muted">sorted by Nova</span>
      </div>

      {tasks.length === 0 && (
        <p className="text-sm text-muted">Nothing on your plate — add a task to get started.</p>
      )}

      <ul className="space-y-2">
        {tasks.slice(0, 6).map((task, i) => (
          <motion.li
            key={task.id}
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.04 }}
            className="flex items-center gap-3 rounded-xl px-3 py-2.5 bg-surface2"
          >
            <span
              className="h-2 w-2 rounded-full flex-shrink-0"
              style={{ backgroundColor: PRIORITY_COLOR[task.priority] ?? "var(--accent-1)" }}
            />
            <span className="flex-1 text-sm font-body truncate">{task.title}</span>
            <span className="text-xs font-mono text-muted">{Math.round(task.priority_score)}</span>
          </motion.li>
        ))}
      </ul>
    </div>
  );
}
