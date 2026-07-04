from datetime import datetime
from datetime import date as date_type

from pydantic import BaseModel


class HabitCreate(BaseModel):
    name: str
    category: str | None = None
    custom_rules: dict = {}


class HabitOut(BaseModel):
    id: int
    user_id: int
    name: str
    category: str | None
    custom_rules: dict
    streak_count: int
    last_completed_date: date_type | None
    created_at: datetime

    class Config:
        from_attributes = True


class HabitLogCreate(BaseModel):
    date: date_type | None = None
    status: str = "completed"


class HabitLogOut(BaseModel):
    id: int
    habit_id: int
    date: date_type
    status: str

    class Config:
        from_attributes = True


class MilestoneCreate(BaseModel):
    title: str
    description: str | None = None
    due_date: datetime | None = None


class MilestoneOut(BaseModel):
    id: int
    goal_id: int
    title: str
    description: str | None
    is_completed: bool
    due_date: datetime | None

    class Config:
        from_attributes = True


class GoalCreate(BaseModel):
    title: str
    description: str | None = None
    type: str = "short-term"
    deadline: datetime | None = None


class GoalUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    type: str | None = None
    progress_percentage: float | None = None
    deadline: datetime | None = None


class GoalOut(BaseModel):
    id: int
    user_id: int
    title: str
    description: str | None
    type: str
    progress_percentage: float
    deadline: datetime | None
    created_at: datetime
    milestones: list[MilestoneOut] = []

    class Config:
        from_attributes = True
