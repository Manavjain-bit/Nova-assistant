from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, engine
import app.models  # noqa: ensures all models are registered on Base.metadata
from app.routers import auth, tasks, reminders, habits, goals, notes, integrations, chat, briefing, voice
from app.services.scheduler import start_scheduler, stop_scheduler

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    # Creates tables if they don't exist yet. For production use Alembic migrations instead.
    Base.metadata.create_all(bind=engine)
    start_scheduler()


@app.on_event("shutdown")
def on_shutdown():
    stop_scheduler()


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.APP_NAME, "env": settings.ENV}


app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(reminders.router)
app.include_router(reminders.notif_router)
app.include_router(habits.router)
app.include_router(goals.router)
app.include_router(notes.router)
app.include_router(integrations.router)
app.include_router(chat.router)
app.include_router(briefing.router)
app.include_router(voice.router)
