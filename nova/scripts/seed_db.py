"""
Quick dev-environment seed script: creates a demo user with sample tasks,
habits, a goal, and a note so the dashboard has something to show immediately.

Usage (from backend/ with deps installed):
    python ../scripts/seed_db.py
"""
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.core.database import Base, engine, SessionLocal  # noqa
from app.core.security import hash_password  # noqa
from app.models.user import User  # noqa
from app.models.task import Task  # noqa
from app.models.habit_goal import Habit, Goal, Milestone  # noqa
from app.models.misc import Note  # noqa

Base.metadata.create_all(bind=engine)
db = SessionLocal()

DEMO_EMAIL = "demo@nova.ai"
existing = db.query(User).filter(User.email == DEMO_EMAIL).first()
if existing:
    print(f"Demo user already exists: {DEMO_EMAIL} / demo12345")
else:
    user = User(email=DEMO_EMAIL, hashed_password=hash_password("demo12345"), full_name="Demo User")
    db.add(user)
    db.commit()
    db.refresh(user)

    db.add_all(
        [
            Task(user_id=user.id, title="Finish quarterly report", priority="urgent",
                 due_date=datetime.utcnow() + timedelta(hours=6)),
            Task(user_id=user.id, title="Book dentist appointment", priority="medium",
                 due_date=datetime.utcnow() + timedelta(days=5)),
            Task(user_id=user.id, title="Plan weekend trip", priority="low"),
        ]
    )

    habit = Habit(user_id=user.id, name="Morning run", category="health", streak_count=4,
                   last_completed_date=datetime.utcnow().date())
    db.add(habit)

    goal = Goal(user_id=user.id, title="Learn Spanish", type="long-term")
    db.add(goal)
    db.commit()
    db.refresh(goal)
    db.add_all(
        [
            Milestone(goal_id=goal.id, title="Finish beginner course", is_completed=True),
            Milestone(goal_id=goal.id, title="Have a 10 minute conversation"),
        ]
    )

    db.add(Note(user_id=user.id, title="Welcome to Nova", content="This is a sample pinned note.", is_pinned=True))

    db.commit()
    print(f"Seeded demo user: {DEMO_EMAIL} / demo12345")

db.close()
