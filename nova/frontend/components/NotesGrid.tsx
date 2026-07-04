"use client";

import { useEffect, useState } from "react";
import { Pin } from "lucide-react";
import { api } from "@/lib/api";

interface Note {
  id: number;
  title: string;
  content: string | null;
  is_pinned: boolean;
}

export default function NotesGrid() {
  const [notes, setNotes] = useState<Note[]>([]);

  useEffect(() => {
    api
      .get("/notes")
      .then(({ data }) => setNotes(data))
      .catch(() => setNotes([]));
  }, []);

  return (
    <div className="rounded-2xl p-6 bg-surface border border-border shadow-card">
      <h2 className="font-display text-lg font-semibold mb-4">Notes</h2>
      {notes.length === 0 ? (
        <p className="text-sm text-muted">No notes saved yet.</p>
      ) : (
        <div className="grid grid-cols-2 gap-3">
          {notes.slice(0, 4).map((note) => (
            <div key={note.id} className="rounded-xl p-3 bg-surface2 border border-border">
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-body font-medium truncate">{note.title}</span>
                {note.is_pinned && <Pin size={12} style={{ color: "var(--accent-1)" }} />}
              </div>
              <p className="text-xs text-muted line-clamp-2">{note.content}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
