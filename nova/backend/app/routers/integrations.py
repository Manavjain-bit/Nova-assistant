from fastapi import APIRouter, Depends

from app.core.config import settings
from app.core.deps import get_current_user
from app.models.user import User
from app.services import gmail, calendar as calendar_service, file_search

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.get("/gmail/messages")
def get_gmail_messages(unread_only: bool = False, user: User = Depends(get_current_user)):
    return gmail.list_messages(user, unread_only=unread_only)


@router.get("/calendar/events")
def get_calendar_events(days_ahead: int = 1, user: User = Depends(get_current_user)):
    return calendar_service.list_events(user, days_ahead=days_ahead)


@router.get("/files/search")
def search_workspace_files(q: str = "", user: User = Depends(get_current_user)):
    results = file_search.search_files(settings.FILE_SEARCH_WORKSPACE_DIR, q)
    return {"query": q, "results": results}
