"""
Voice service: Speech-to-Text (Whisper) and Text-to-Speech (OpenAI TTS / ElevenLabs).

If no AI provider keys are configured, these functions return a structured
"fallback" response telling the frontend to use the browser's Web Speech API
(SpeechRecognition for STT, SpeechSynthesis for TTS) instead of failing.
"""
import io

from app.core.config import settings

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover
    OpenAI = None


def stt_available() -> bool:
    return bool(settings.OPENAI_API_KEY) and OpenAI is not None


def tts_available() -> bool:
    return bool(settings.OPENAI_API_KEY or settings.ELEVENLABS_API_KEY) and OpenAI is not None


def transcribe_audio(file_bytes: bytes, filename: str = "audio.webm") -> dict:
    """Returns {"text": str, "source": "whisper"} or a fallback instruction."""
    if not stt_available():
        return {
            "text": None,
            "source": "fallback",
            "fallback_reason": "No OPENAI_API_KEY configured. Use the browser's Web Speech API "
                                "(SpeechRecognition) for client-side speech-to-text instead.",
        }

    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        audio_file = io.BytesIO(file_bytes)
        audio_file.name = filename
        transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
        return {"text": transcript.text, "source": "whisper"}
    except Exception as exc:  # pragma: no cover - network/key errors
        return {
            "text": None,
            "source": "fallback_error",
            "fallback_reason": f"Whisper request failed ({exc.__class__.__name__}). "
                                "Use the browser's Web Speech API instead.",
        }


def synthesize_speech(text: str, voice: str = "alloy") -> dict:
    """Returns {"audio_base64": str, "source": "openai_tts"} or a fallback instruction
    telling the client to use window.speechSynthesis instead."""
    if not tts_available():
        return {
            "audio_base64": None,
            "source": "fallback",
            "fallback_reason": "No TTS provider configured. Use the browser's Web Speech "
                                "Synthesis API (SpeechSynthesisUtterance) instead.",
            "text": text,
        }

    if settings.OPENAI_API_KEY:
        try:
            import base64

            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            response = client.audio.speech.create(model="tts-1", voice=voice, input=text)
            audio_bytes = response.read() if hasattr(response, "read") else response.content
            return {"audio_base64": base64.b64encode(audio_bytes).decode(), "source": "openai_tts"}
        except Exception as exc:  # pragma: no cover
            return {
                "audio_base64": None,
                "source": "fallback_error",
                "fallback_reason": f"OpenAI TTS request failed ({exc.__class__.__name__}). "
                                    "Use the browser's Web Speech Synthesis API instead.",
                "text": text,
            }

    return {
        "audio_base64": None,
        "source": "fallback",
        "fallback_reason": "ElevenLabs integration not implemented in this build. "
                            "Use the browser's Web Speech Synthesis API instead.",
        "text": text,
    }
