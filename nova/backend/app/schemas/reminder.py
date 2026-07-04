from datetime import datetime

from pydantic import BaseModel


class ReminderCreate(BaseModel):
    title: str
    type: str = "one-time"
    cron_expression: str | None = None
    next_trigger: datetime | None = None
    email_notification: bool = False
    metadata_json: dict = {}


class ReminderFromText(BaseModel):
    text: str
    email_notification: bool = False


class ReminderUpdate(BaseModel):
    title: str | None = None
    type: str | None = None
    cron_expression: str | None = None
    next_trigger: datetime | None = None
    email_notification: bool | None = None
    is_sent: bool | None = None


class ReminderOut(BaseModel):
    id: int
    user_id: int
    title: str
    type: str
    cron_expression: str | None
    next_trigger: datetime | None
    email_notification: bool
    is_sent: bool
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationOut(BaseModel):
    id: int
    user_id: int
    title: str
    message: str | None
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
