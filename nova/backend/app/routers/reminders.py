from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.misc import Reminder, Notification
from app.models.user import User
from app.schemas.reminder import (
    ReminderCreate,
    ReminderFromText,
    ReminderUpdate,
    ReminderOut,
    NotificationOut,
)
from app.services.reminder_parser import parse_reminder
from app.services.scheduler import dispatch_due_reminders

router = APIRouter(prefix="/reminders", tags=["reminders"])
notif_router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.post("", response_model=ReminderOut, status_code=201)
def create_reminder(payload: ReminderCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    reminder = Reminder(user_id=user.id, **payload.model_dump())
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder


@router.post("/parse", response_model=ReminderOut, status_code=201)
def create_reminder_from_text(payload: ReminderFromText, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Creates a reminder from a natural-language phrase, e.g.
    'Remind me to call Rahul tomorrow after lunch'."""
    parsed = parse_reminder(payload.text)
    reminder = Reminder(
        user_id=user.id,
        title=parsed.title,
        type=parsed.type,
        cron_expression=parsed.cron_expression,
        next_trigger=parsed.next_trigger,
        email_notification=payload.email_notification,
    )
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder


@router.get("", response_model=list[ReminderOut])
def list_reminders(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Reminder).filter(Reminder.user_id == user.id).order_by(Reminder.next_trigger.asc()).all()


@router.patch("/{reminder_id}", response_model=ReminderOut)
def update_reminder(reminder_id: int, payload: ReminderUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id, Reminder.user_id == user.id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(reminder, field, value)
    db.commit()
    db.refresh(reminder)
    return reminder


@router.delete("/{reminder_id}", status_code=204)
def delete_reminder(reminder_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id, Reminder.user_id == user.id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    db.delete(reminder)
    db.commit()
    return None


@router.post("/dispatch-due", status_code=200)
def trigger_dispatch():
    """Manually triggers a dispatch sweep (useful for tests/demo without waiting for the
    background scheduler's 1-minute interval)."""
    count = dispatch_due_reminders()
    return {"dispatched": count}


@notif_router.get("", response_model=list[NotificationOut])
def list_notifications(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Notification).filter(Notification.user_id == user.id).order_by(Notification.created_at.desc()).all()


@notif_router.patch("/{notification_id}/read", response_model=NotificationOut)
def mark_read(notification_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    notification = db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == user.id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return notification
