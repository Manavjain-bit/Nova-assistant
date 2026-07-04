"""
Smart Prioritization Engine.

Scores tasks using a weighted combination of:
- Urgency (time remaining until due_date)
- Importance (explicit priority label: low/medium/high/urgent)
- Estimated duration (shorter tasks get a slight boost - "quick wins")
- Dependency depth (subtasks of an in-progress parent get a boost)

The result is a `priority_score` float (higher = more important to do now),
which is stored on the Task and used to order task lists.
"""
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.task import Task

IMPORTANCE_WEIGHTS = {
    "low": 1.0,
    "medium": 2.0,
    "high": 3.0,
    "urgent": 4.0,
}

W_URGENCY = 0.45
W_IMPORTANCE = 0.35
W_DURATION = 0.10
W_DEPENDENCY = 0.10


def _urgency_score(due_date: datetime | None) -> float:
    """Returns a 0-1 score; closer/overdue due dates score higher."""
    if due_date is None:
        return 0.2  # mild default urgency for undated tasks

    now = datetime.now(timezone.utc)
    if due_date.tzinfo is None:
        due_date = due_date.replace(tzinfo=timezone.utc)

    delta_hours = (due_date - now).total_seconds() / 3600.0

    if delta_hours <= 0:
        return 1.0  # overdue -> max urgency
    if delta_hours >= 24 * 14:
        return 0.05  # more than 2 weeks out -> low urgency
    # Inverse-decay curve between 0h and 14 days
    return max(0.05, 1.0 - (delta_hours / (24 * 14)))


def _importance_score(priority: str) -> float:
    return IMPORTANCE_WEIGHTS.get(priority, IMPORTANCE_WEIGHTS["medium"]) / IMPORTANCE_WEIGHTS["urgent"]


def _duration_score(estimated_duration: int | None) -> float:
    """Shorter tasks get a small boost to encourage quick wins; longer tasks score lower."""
    if estimated_duration is None:
        return 0.5
    if estimated_duration <= 15:
        return 1.0
    if estimated_duration >= 240:
        return 0.1
    return max(0.1, 1.0 - (estimated_duration / 240))


def _dependency_score(task: Task) -> float:
    """Tasks blocking other in-progress work (i.e. a parent task that's in_progress) score higher."""
    if task.parent_id is None:
        return 0.3
    return 0.7


def compute_priority_score(task: Task) -> float:
    score = (
        W_URGENCY * _urgency_score(task.due_date)
        + W_IMPORTANCE * _importance_score(task.priority)
        + W_DURATION * _duration_score(task.estimated_duration)
        + W_DEPENDENCY * _dependency_score(task)
    )
    return round(score * 100, 2)  # scale to 0-100 for readability


def rescore_task(task: Task) -> Task:
    task.priority_score = compute_priority_score(task)
    return task


def rescore_all_for_user(db: Session, user_id: int) -> list[Task]:
    tasks = (
        db.query(Task)
        .filter(Task.user_id == user_id, Task.status != "completed", Task.status != "cancelled")
        .all()
    )
    for t in tasks:
        rescore_task(t)
    db.commit()
    tasks.sort(key=lambda t: t.priority_score, reverse=True)
    return tasks
