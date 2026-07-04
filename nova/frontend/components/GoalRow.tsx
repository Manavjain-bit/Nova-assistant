"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import ProgressRing from "./ProgressRing";

interface Goal {
  id: number;
  title: string;
  progress_percentage: number;
}

export default function GoalRow() {
  const [goals, setGoals] = useState<Goal[]>([]);

  useEffect(() => {
    api
      .get("/goals")
      .then(({ data }) => setGoals(data))
      .catch(() => setGoals([]));
  }, []);

  return (
    <div className="rounded-2xl p-6 bg-surface border border-border shadow-card">
      <h2 className="font-display text-lg font-semibold mb-4">Goals</h2>
      {goals.length === 0 ? (
        <p className="text-sm text-muted">No goals yet — set one to start tracking progress.</p>
      ) : (
        <div className="flex gap-5 overflow-x-auto pb-1">
          {goals.map((goal) => (
            <ProgressRing
              key={goal.id}
              progress={goal.progress_percentage}
              color="var(--accent-1)"
              size={76}
              strokeWidth={6}
              label={goal.title}
            />
          ))}
        </div>
      )}
    </div>
  );
}
