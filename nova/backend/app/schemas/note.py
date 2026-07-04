from datetime import datetime

from pydantic import BaseModel


class NoteCreate(BaseModel):
    title: str
    content: str | None = None
    is_pinned: bool = False
    tags: list[str] = []


class NoteUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    is_pinned: bool | None = None
    tags: list[str] | None = None


class NoteOut(BaseModel):
    id: int
    user_id: int
    title: str
    content: str | None
    is_pinned: bool
    tags: list[str]
    voice_url: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
