"use client";

import { useState } from "react";
import { useVoiceAssistant } from "@/hooks/useVoiceAssistant";
import { api } from "@/lib/api";

/**
 * The large glowing circular voice button described in Phase 7's dashboard spec.
 * Wired here functionally (Phase 6); final premium animation polish lands in Phase 7.
 */
export default function VoiceButton() {
  const [lastReply, setLastReply] = useState<string | null>(null);

  const { state, supported, startListening, speak } = useVoiceAssistant({
    onTranscript: async (text) => {
      try {
        const { data } = await api.post("/chat/message", { text });
        setLastReply(data.assistant_message.text_content);
        speak(data.assistant_message.text_content);
      } catch {
        setLastReply("Sorry, I couldn't reach the server.");
      }
    },
  });

  if (!supported) {
    return (
      <div className="text-sm text-zinc-400">
        Voice features need a browser that supports the Web Speech API (e.g. Chrome).
      </div>
    );
  }

  const isActive = state === "listening" || state === "speaking";

  return (
    <div className="flex flex-col items-center gap-4">
      <button
        onClick={startListening}
        aria-label="Talk to Nova"
        className={`relative h-24 w-24 rounded-full flex items-center justify-center transition-transform duration-300 ${
          isActive ? "scale-110" : "scale-100"
        }`}
        style={{
          background: "radial-gradient(circle at 30% 30%, #8FA6FF, #4658C9)",
          boxShadow: isActive
            ? "0 0 40px 10px rgba(110,139,255,0.55)"
            : "0 0 20px 4px rgba(110,139,255,0.3)",
        }}
      >
        <span className="text-white text-sm font-medium">{state === "idle" ? "Talk" : state}</span>
      </button>
      {lastReply && <p className="text-zinc-300 text-sm max-w-sm text-center">{lastReply}</p>}
    </div>
  );
}
