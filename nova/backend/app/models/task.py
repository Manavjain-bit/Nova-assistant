from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, Integer, Float, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="pending")  # pending/in_progress/completed/cancelled
    priority: Mapped[str] = mapped_column(String(16), default="medium")  # low/medium/high/urgent
    due_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    recurrence: Mapped[str | None] = mapped_column(String(255), nullable=True)  # JSON/cron-like string
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("tasks.id"), nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    estimated_duration: Mapped[int | None] = mapped_column(Integer, nullable=True)  # minutes
    priority_score: Mapped[float] = mapped_column(Float, default=0.0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="tasks")
    subtasks = relationship("Task", backref="parent", remote_side=[id])
