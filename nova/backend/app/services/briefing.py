"""
Daily Briefing & Night Review generator.

Daily Briefing pulls together: weather (if available), today's calendar events
(mock or live), task workload (prioritized list), and any due reminders.

Night Review prompts the user to reflect on mood/productivity and offers to
auto-update task statuses for anything marked done during the conversation.
"""
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.task import Task
from app.models.misc import Reminder
from app.services import calendar as calendar_service
from app.services.prioritization import rescore_all_for_user


def build_daily_briefing(db: Session, user) -> dict:
    events = calendar_service.list_events(user, days_ahead=1)["events"]
    prioritized_tasks = rescore_all_for_user(db, user.id)[:5]

    now = datetime.utcnow()
    horizon = now + timedelta(hours=24)
    upcoming_reminders = (
        db.query(Reminder)
        .filter(Reminder.user_id == user.id, Reminder.is_sent.is_(False))
        .filter(Reminder.next_trigger != None)  # noqa: E711
        .filter(Reminder.next_trigger <= horizon)
        .order_by(Reminder.next_trigger.asc())
        .all()
    )

    workload_summary = _summarize_workload(prioritized_tasks)

    return {
        "greeting": _time_of_day_greeting(now),
        "schedule": [
            {"title": e["title"], "start": e["start"], "end": e["end"], "location": e.get("location")}
            for e in events
        ],
        "top_tasks": [
            {"id": t.id, "title": t.title, "priority_score": t.priority_score, "due_date": t.due_date}
            for t in prioritized_tasks
        ],
        "upcoming_reminders": [
            {"id": r.id, "title": r.title, "next_trigger": r.next_trigger} for r in upcoming_reminders
        ],
        "workload_summary": workload_summary,
    }


def _time_of_day_greeting(now: datetime) -> str:
    hour = now.hour
    if hour < 12:
        return "Good morning! Here's your briefing for today."
    if hour < 18:
        return "Good afternoon! Here's where things stand today."
    return "Good evening! Here's a look at today."


def _summarize_workload(tasks: list[Task]) -> str:
    if not tasks:
        return "You have a clear plate today — nothing urgent on your task list."
    urgent_count = sum(1 for t in tasks if t.priority_score >= 70)
    if urgent_count:
        return f"You have {len(tasks)} active tasks, {urgent_count} of which are high priority. Focus there first."
    return f"You have {len(tasks)} active tasks today, none critically urgent."


def build_night_review(db: Session, user, mood: str | None = None, productivity_rating: int | None = None) -> dict:
    today = datetime.utcnow().date()
    completed_today = (
        db.query(Task)
        .filter(Task.user_id == user.id, Task.status == "completed")
        .filter(Task.updated_at >= datetime.combine(today, datetime.min.time()))
        .all()
    )
    still_pending = (
        db.query(Task)
        .filter(Task.user_id == user.id)
        .filter(Task.status.in_(["pending", "in_progress"]))
        .filter(Task.due_date != None)  # noqa: E711
        .filter(Task.due_date <= datetime.combine(today, datetime.max.time()))
        .all()
    )

    prompt = "How did today go? Reflect on your mood and productivity, and I can carry over anything unfinished to tomorrow."

    return {
        "prompt": prompt,
        "mood": mood,
        "productivity_rating": productivity_rating,
        "completed_today": [{"id": t.id, "title": t.title} for t in completed_today],
        "overdue_or_due_today_still_pending": [{"id": t.id, "title": t.title} for t in still_pending],
        "suggestion": (
            f"Nice work — you completed {len(completed_today)} task(s) today."
            if completed_today
            else "No tasks marked complete today — want to reschedule anything to tomorrow?"
        ),
    }
