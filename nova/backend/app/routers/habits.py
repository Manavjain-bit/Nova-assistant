from datetime import date as date_cls

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.habit_goal import Habit, HabitLog
from app.models.user import User
from app.schemas.habit_goal import HabitCreate, HabitOut, HabitLogCreate, HabitLogOut
from app.services.habit_tracker import record_completion, record_miss

router = APIRouter(prefix="/habits", tags=["habits"])


@router.post("", response_model=HabitOut, status_code=201)
def create_habit(payload: HabitCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    habit = Habit(user_id=user.id, **payload.model_dump())
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return habit


@router.get("", response_model=list[HabitOut])
def list_habits(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Habit).filter(Habit.user_id == user.id).all()


@router.get("/{habit_id}", response_model=HabitOut)
def get_habit(habit_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    habit = db.query(Habit).filter(Habit.id == habit_id, Habit.user_id == user.id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    return habit


@router.delete("/{habit_id}", status_code=204)
def delete_habit(habit_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    habit = db.query(Habit).filter(Habit.id == habit_id, Habit.user_id == user.id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    db.delete(habit)
    db.commit()
    return None


@router.post("/{habit_id}/logs", response_model=HabitLogOut, status_code=201)
def log_habit(habit_id: int, payload: HabitLogCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    habit = db.query(Habit).filter(Habit.id == habit_id, Habit.user_id == user.id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    log_date = payload.date or date_cls.today()
    log = HabitLog(habit_id=habit.id, date=log_date, status=payload.status)
    db.add(log)

    if payload.status == "completed":
        record_completion(habit, log_date)
    else:
        record_miss(habit, log_date)

    db.commit()
    db.refresh(log)
    return log


@router.get("/{habit_id}/logs", response_model=list[HabitLogOut])
def get_habit_logs(habit_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    habit = db.query(Habit).filter(Habit.id == habit_id, Habit.user_id == user.id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    return db.query(HabitLog).filter(HabitLog.habit_id == habit_id).order_by(HabitLog.date.desc()).all()
