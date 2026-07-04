"""
Memory Manager.

- Short-Term Memory: returns the last N turns of a conversation as chat-style messages.
- Long-Term Memory: extracts simple key user facts (name, preferences, friends, work)
  using regex/rule-based matchers (no LLM dependency required) and upserts them into
  `memory_entries`.
- Summarization: compresses old messages into a `conversations.summary` once a
  conversation grows past a token/length threshold, keeping only the most recent
  turns verbatim.
"""
import re

from sqlalchemy.orm import Session

from app.models.misc import Message, Conversation, MemoryEntry

SHORT_TERM_TURNS = 10
SUMMARIZE_AFTER_MESSAGES = 30
KEEP_VERBATIM_AFTER_SUMMARY = 10

_FACT_PATTERNS = [
    (re.compile(r"\bmy name is (\w+)", re.IGNORECASE), "name"),
    (re.compile(r"\bi work (at|for) ([\w\s]+?)(?:\.|,|$)", re.IGNORECASE), "work"),
    (re.compile(r"\bi'?m a (\w[\w\s]*?)(?:\.|,|$)", re.IGNORECASE), "occupation"),
    (re.compile(r"\bmy friend(?:'s name)? is (\w+)", re.IGNORECASE), "friend"),
    (re.compile(r"\bi (like|love|prefer) ([\w\s]+?)(?:\.|,|$)", re.IGNORECASE), "preference"),
    (re.compile(r"\bi (hate|dislike) ([\w\s]+?)(?:\.|,|$)", re.IGNORECASE), "dislike"),
]


def get_short_term_context(db: Session, conversation_id: int, n_turns: int = SHORT_TERM_TURNS) -> list[dict]:
    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(n_turns)
        .all()
    )
    messages.reverse()
    return [{"role": "user" if m.sender == "user" else "assistant", "content": m.text_content or ""} for m in messages]


def extract_facts(user_id: int, text: str) -> list[tuple[str, str]]:
    """Returns a list of (key, value) facts found in the text."""
    facts = []
    for pattern, key in _FACT_PATTERNS:
        match = pattern.search(text)
        if match:
            value = match.group(match.lastindex).strip()
            facts.append((key, value))
    return facts


def update_long_term_memory(db: Session, user_id: int, text: str) -> list[MemoryEntry]:
    facts = extract_facts(user_id, text)
    saved = []
    for key, value in facts:
        existing = (
            db.query(MemoryEntry)
            .filter(MemoryEntry.user_id == user_id, MemoryEntry.key == key, MemoryEntry.category == "long-term")
            .first()
        )
        if existing:
            existing.value = value
        else:
            existing = MemoryEntry(user_id=user_id, key=key, value=value, category="long-term")
            db.add(existing)
        saved.append(existing)
    if saved:
        db.commit()
    return saved


def maybe_summarize(db: Session, conversation: Conversation) -> bool:
    """If the conversation has grown long, compress older messages into `summary`,
    leaving only the most recent messages verbatim. Returns True if summarization ran."""
    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation.id)
        .order_by(Message.created_at.asc())
        .all()
    )
    if len(messages) <= SUMMARIZE_AFTER_MESSAGES:
        return False

    to_summarize = messages[:-KEEP_VERBATIM_AFTER_SUMMARY]
    summary_lines = [f"{m.sender}: {m.text_content}" for m in to_summarize if m.text_content]
    new_summary_chunk = " | ".join(summary_lines)[:2000]

    conversation.summary = (
        f"{conversation.summary} || {new_summary_chunk}" if conversation.summary else new_summary_chunk
    )

    for m in to_summarize:
        db.delete(m)

    db.commit()
    return True
