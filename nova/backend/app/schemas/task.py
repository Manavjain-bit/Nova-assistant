from datetime import datetime

from pydantic import BaseModel


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    priority: str = "medium"
    due_date: datetime | None = None
    recurrence: str | None = None
    parent_id: int | None = None
    category: str | None = None
    estimated_duration: int | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    priority: str | None = None
    due_date: datetime | None = None
    recurrence: str | None = None
    category: str | None = None
    estimated_duration: int | None = None


class TaskOut(BaseModel):
    id: int
    user_id: int
    title: str
    description: str | None
    status: str
    priority: str
    due_date: datetime | None
    recurrence: str | None
    parent_id: int | None
    category: str | None
    estimated_duration: int | None
    priority_score: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
