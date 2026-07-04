"""
AI core service.

Wraps OpenAI's chat completion API for Nova's conversational brain. If
OPENAI_API_KEY is not configured, falls back to a lightweight rule-based/
semantic-matcher planner so the assistant still responds usefully offline.
"""
import re

from app.core.config import settings

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover
    OpenAI = None


def is_live() -> bool:
    return bool(settings.OPENAI_API_KEY) and OpenAI is not None


def _client() -> "OpenAI":
    return OpenAI(api_key=settings.OPENAI_API_KEY)


SYSTEM_PROMPT = (
    "You are Nova, a helpful, concise AI personal assistant. You help the user manage "
    "tasks, reminders, habits, goals, and notes, and you answer general questions."
)

# --- Local fallback rule-based planner -------------------------------------------------

_INTENT_PATTERNS = [
    (re.compile(r"\bremind me\b", re.IGNORECASE), "reminder"),
    (re.compile(r"\b(add|create) (a )?task\b", re.IGNORECASE), "task"),
    (re.compile(r"\bhabit\b", re.IGNORECASE), "habit"),
    (re.compile(r"\bgoal\b", re.IGNORECASE), "goal"),
    (re.compile(r"\bnote\b", re.IGNORECASE), "note"),
    (re.compile(r"\b(hi|hello|hey)\b", re.IGNORECASE), "greeting"),
    (re.compile(r"\bhow are you\b", re.IGNORECASE), "smalltalk"),
]

_FALLBACK_RESPONSES = {
    "reminder": "Got it — I can set up a reminder for that. Try the Reminders panel, or tell me the exact phrase like 'remind me to X tomorrow at 9am'.",
    "task": "I can add that as a task for you. Give me a title and, optionally, a due date and priority.",
    "habit": "Tracking a habit? I can log today's completion or show your current streak.",
    "goal": "Let's break that goal down into milestones so we can track progress.",
    "note": "I'll save that as a note. Want me to pin it or add any tags?",
    "greeting": "Hey! I'm Nova. What can I help you get done today?",
    "smalltalk": "I'm running well and ready to help — what's on your plate today?",
}

_DEFAULT_FALLBACK = (
    "I'm currently running in local fallback mode (no OpenAI key configured), so my answers "
    "are limited to simple task/reminder/habit/goal/note assistance. Ask me to add a task, "
    "set a reminder, or check your schedule."
)


def _local_fallback_reply(user_message: str) -> str:
    for pattern, intent in _INTENT_PATTERNS:
        if pattern.search(user_message):
            return _FALLBACK_RESPONSES[intent]
    return _DEFAULT_FALLBACK


def generate_reply(user_message: str, context_messages: list[dict] | None = None) -> dict:
    """Returns {"reply": str, "source": "openai"|"local_fallback"}.

    `context_messages` is a list of {"role": "user"|"assistant", "content": str}
    representing prior turns (typically supplied by the Memory Manager).
    """
    if not is_live():
        return {"reply": _local_fallback_reply(user_message), "source": "local_fallback"}

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(context_messages or [])
    messages.append({"role": "user", "content": user_message})

    try:
        client = _client()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=400,
        )
        reply = response.choices[0].message.content
        return {"reply": reply, "source": "openai"}
    except Exception:
        # Network/auth/quota error -> degrade gracefully rather than failing the request.
        return {"reply": _local_fallback_reply(user_message), "source": "local_fallback_error"}
