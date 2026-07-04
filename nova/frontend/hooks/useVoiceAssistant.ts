"use client";

import { useCallback, useEffect, useRef, useState } from "react";

/**
 * Browser-native voice assistant hook for Nova.
 *
 * Uses the Web Speech API (SpeechRecognition + SpeechSynthesis) directly in
 * the browser. This is the always-available fallback path described in the
 * implementation plan, and works with zero backend AI keys configured.
 *
 * Also implements lightweight "Hey Nova" wake-word detection by running a
 * continuous-listening recognizer and checking each interim transcript for
 * the wake phrase before triggering the main listening flow.
 */

type VoiceState = "idle" | "wake_listening" | "listening" | "speaking" | "unsupported";

interface UseVoiceAssistantOptions {
  wakeWord?: string;
  onTranscript?: (text: string) => void;
  autoStartWakeWord?: boolean;
}

function getSpeechRecognition(): any {
  if (typeof window === "undefined") return null;
  return (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition || null;
}

export function useVoiceAssistant(options: UseVoiceAssistantOptions = {}) {
  const { wakeWord = "hey nova", onTranscript, autoStartWakeWord = false } = options;

  const [state, setState] = useState<VoiceState>("idle");
  const [transcript, setTranscript] = useState("");
  const recognitionRef = useRef<any>(null);
  const wakeRecognitionRef = useRef<any>(null);

  const SpeechRecognitionCtor = getSpeechRecognition();
  const supported = !!SpeechRecognitionCtor && typeof window !== "undefined" && "speechSynthesis" in window;

  const stopListening = useCallback(() => {
    recognitionRef.current?.stop();
    setState("idle");
  }, []);

  const startListening = useCallback(() => {
    if (!SpeechRecognitionCtor) {
      setState("unsupported");
      return;
    }
    wakeRecognitionRef.current?.stop();

    const recognition = new SpeechRecognitionCtor();
    recognition.lang = "en-US";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onresult = (event: any) => {
      const text = event.results[0][0].transcript;
      setTranscript(text);
      onTranscript?.(text);
    };
    recognition.onend = () => {
      setState("idle");
      if (autoStartWakeWord) startWakeWordListening();
    };
    recognition.onerror = () => setState("idle");

    recognitionRef.current = recognition;
    setState("listening");
    recognition.start();
  }, [SpeechRecognitionCtor, onTranscript, autoStartWakeWord]);

  const startWakeWordListening = useCallback(() => {
    if (!SpeechRecognitionCtor) {
      setState("unsupported");
      return;
    }
    const recognition = new SpeechRecognitionCtor();
    recognition.lang = "en-US";
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = (event: any) => {
      const results = event.results;
      const latest = results[results.length - 1];
      const text = latest[0].transcript.toLowerCase();
      if (text.includes(wakeWord)) {
        recognition.stop();
        startListening();
      }
    };
    recognition.onend = () => {
      // Browsers auto-stop continuous recognition periodically; restart if we're still meant to be wake-listening.
      if (state === "wake_listening") {
        try {
          recognition.start();
        } catch {
          /* already started */
        }
      }
    };

    wakeRecognitionRef.current = recognition;
    setState("wake_listening");
    recognition.start();
  }, [SpeechRecognitionCtor, wakeWord, startListening, state]);

  const speak = useCallback((text: string, onEnd?: () => void) => {
    if (typeof window === "undefined" || !("speechSynthesis" in window)) return;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.onstart = () => setState("speaking");
    utterance.onend = () => {
      setState("idle");
      onEnd?.();
    };
    window.speechSynthesis.speak(utterance);
  }, []);

  useEffect(() => {
    return () => {
      recognitionRef.current?.stop();
      wakeRecognitionRef.current?.stop();
    };
  }, []);

  return {
    state,
    supported,
    transcript,
    startListening,
    stopListening,
    startWakeWordListening,
    speak,
  };
}
