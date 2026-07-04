"""
APScheduler-backed background scheduler for reminders.

Runs a single background job every minute that checks for due reminders
and "dispatches" them (creates a Notification row; in a full deployment this
would also push a browser/desktop notification and optionally send email).
"""
import logging
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.misc import Reminder, Notification

logger = logging.getLogger("nova.scheduler")

scheduler = BackgroundScheduler()


def dispatch_due_reminders() -> int:
    """Finds reminders whose next_trigger has passed and aren't yet sent, dispatches them."""
    db: Session = SessionLocal()
    dispatched = 0
    try:
        now = datetime.utcnow()
        due = (
            db.query(Reminder)
            .filter(Reminder.is_sent.is_(False))
            .filter(Reminder.next_trigger != None)  # noqa: E711
            .filter(Reminder.next_trigger <= now)
            .all()
        )
        for reminder in due:
            notification = Notification(
                user_id=reminder.user_id,
                title="Reminder",
                message=reminder.title,
            )
            db.add(notification)

            if reminder.type == "recurring" and reminder.cron_expression:
                reminder.next_trigger = _advance_cron(reminder.next_trigger, reminder.cron_expression)
                reminder.is_sent = False
            else:
                reminder.is_sent = True

            dispatched += 1
            logger.info("Dispatched reminder id=%s title=%s", reminder.id, reminder.title)

        db.commit()
    finally:
        db.close()
    return dispatched


def _advance_cron(previous_trigger: datetime, cron_expression: str) -> datetime:
    """Given a 5-field cron string, compute the next fire time after previous_trigger."""
    minute, hour, day, month, day_of_week = cron_expression.split()
    trigger = CronTrigger(
        minute=minute, hour=hour, day=day, month=month, day_of_week=day_of_week,
    )
    next_fire = trigger.get_next_fire_time(None, previous_trigger + timedelta(seconds=1))
    if next_fire is None:
        return previous_trigger + timedelta(days=1)
    return next_fire.replace(tzinfo=None)


def start_scheduler():
    if scheduler.running:
        return
    scheduler.add_job(dispatch_due_reminders, "interval", minutes=1, id="dispatch_due_reminders", replace_existing=True)
    scheduler.start()
    logger.info("Nova reminder scheduler started")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
