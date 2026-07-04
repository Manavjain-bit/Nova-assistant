"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Mic, Loader2 } from "lucide-react";
import { useVoiceAssistant } from "@/hooks/useVoiceAssistant";
import { api } from "@/lib/api";

/**
 * Nova's signature element: a glowing voice orb docked at the bottom of the
 * dashboard. Reacts to state (idle / listening / speaking) with ambient
 * pulsing rings. Tap to talk, or say "Hey Nova" if wake-word listening is on.
 */
export default function VoiceOrb() {
  const [lastReply, setLastReply] = useState<string | null>(null);
  const [thinking, setThinking] = useState(false);

  const { state, supported, startListening, speak } = useVoiceAssistant({
    onTranscript: async (text) => {
      setThinking(true);
      try {
        const { data } = await api.post("/chat/message", { text });
        setLastReply(data.assistant_message.text_content);
        speak(data.assistant_message.text_content);
      } catch {
        setLastReply("I couldn't reach the server just now.");
      } finally {
        setThinking(false);
      }
    },
  });

  const isListening = state === "listening";
  const isSpeaking = state === "speaking";
  const isActive = isListening || isSpeaking || thinking;

  return (
    <div className="fixed bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-3 z-50">
      <AnimatePresence>
        {lastReply && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 8 }}
            className="max-w-xs text-center text-sm font-body bg-surface border border-border rounded-xl px-4 py-2 shadow-card"
          >
            {lastReply}
          </motion.div>
        )}
      </AnimatePresence>

      <div className="relative h-24 w-24 flex items-center justify-center">
        {isActive && (
          <>
            <span className="absolute inset-0 rounded-full animate-pulseRing" style={{ backgroundColor: "var(--accent-1)" }} />
            <span
              className="absolute inset-0 rounded-full animate-pulseRing"
              style={{ backgroundColor: "var(--accent-1)", animationDelay: "0.6s" }}
            />
          </>
        )}

        <motion.button
          onClick={supported ? startListening : undefined}
          whileTap={{ scale: 0.94 }}
          aria-label="Talk to Nova"
          disabled={!supported}
          className="relative h-20 w-20 rounded-full flex items-center justify-center shadow-glow disabled:opacity-50"
          style={{ background: "radial-gradient(circle at 30% 30%, var(--accent-2), var(--accent-1))" }}
        >
          {thinking ? (
            <Loader2 className="text-white animate-spin" size={22} />
          ) : (
            <Mic className="text-white" size={22} />
          )}
        </motion.button>
      </div>

      <span className="text-xs font-mono text-muted">
        {!supported ? "Voice needs Chrome/Edge" : isListening ? "Listening..." : isSpeaking ? "Speaking..." : "Tap or say \u201cHey Nova\u201d"}
      </span>
    </div>
  );
}
