from fastapi import APIRouter, Depends, UploadFile, File
from pydantic import BaseModel

from app.core.deps import get_current_user
from app.models.user import User
from app.services import voice

router = APIRouter(prefix="/voice", tags=["voice"])


class TTSRequest(BaseModel):
    text: str
    voice: str = "alloy"


@router.get("/capabilities")
def voice_capabilities(user: User = Depends(get_current_user)):
    return {
        "stt_available_server_side": voice.stt_available(),
        "tts_available_server_side": voice.tts_available(),
        "browser_fallback": {
            "stt": "Web Speech API SpeechRecognition",
            "tts": "Web Speech API SpeechSynthesis",
            "wake_word": "\"Hey Nova\" via continuous SpeechRecognition listening, handled client-side",
        },
    }


@router.post("/stt")
async def speech_to_text(user: User = Depends(get_current_user), audio: UploadFile = File(...)):
    file_bytes = await audio.read()
    return voice.transcribe_audio(file_bytes, filename=audio.filename or "audio.webm")


@router.post("/tts")
def text_to_speech(payload: TTSRequest, user: User = Depends(get_current_user)):
    return voice.synthesize_speech(payload.text, voice=payload.voice)
