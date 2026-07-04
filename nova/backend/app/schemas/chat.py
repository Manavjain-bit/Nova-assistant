from datetime import datetime

from pydantic import BaseModel


class ChatMessageIn(BaseModel):
    text: str
    conversation_id: int | None = None


class MessageOut(BaseModel):
    id: int
    conversation_id: int
    sender: str
    text_content: str | None
    audio_url: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class ChatReplyOut(BaseModel):
    conversation_id: int
    user_message: MessageOut
    assistant_message: MessageOut
    source: str


class ConversationOut(BaseModel):
    id: int
    user_id: int
    summary: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class MemoryEntryOut(BaseModel):
    id: int
    key: str
    value: str
    category: str
    last_accessed: datetime

    class Config:
        from_attributes = True


class NightReviewIn(BaseModel):
    mood: str | None = None
    productivity_rating: int | None = None
