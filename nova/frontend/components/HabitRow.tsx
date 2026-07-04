"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import ProgressRing from "./ProgressRing";

interface Habit {
  id: number;
  name: string;
  streak_count: number;
}

export default function HabitRow() {
  const [habits, setHabits] = useState<Habit[]>([]);

  useEffect(() => {
    api
      .get("/habits")
      .then(({ data }) => setHabits(data))
      .catch(() => setHabits([]));
  }, []);

  return (
    <div className="rounded-2xl p-6 bg-surface border border-border shadow-card">
      <h2 className="font-display text-lg font-semibold mb-4">Habits</h2>
      {habits.length === 0 ? (
        <p className="text-sm text-muted">No habits tracked yet.</p>
      ) : (
        <div className="flex gap-5 overflow-x-auto pb-1">
          {habits.map((habit) => (
            <ProgressRing
              key={habit.id}
              progress={Math.min(habit.streak_count * 100 / 7, 100)}
              color="var(--success)"
              size={76}
              strokeWidth={6}
              label={habit.name}
              sublabel={`${habit.streak_count}d streak`}
            />
          ))}
        </div>
      )}
    </div>
  );
}
