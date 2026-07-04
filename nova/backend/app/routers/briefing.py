from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.chat import NightReviewIn
from app.services.briefing import build_daily_briefing, build_night_review

router = APIRouter(prefix="/briefing", tags=["briefing"])


@router.get("/morning")
def morning_briefing(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return build_daily_briefing(db, user)


@router.post("/night-review")
def night_review(payload: NightReviewIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return build_night_review(db, user, mood=payload.mood, productivity_rating=payload.productivity_rating)
