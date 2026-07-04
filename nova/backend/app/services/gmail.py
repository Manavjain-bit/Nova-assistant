"""
Gmail connector service.

If GOOGLE_CLIENT_ID/SECRET (and a stored refresh token) are configured for the
user, this would call the real Gmail API. Since that's out of scope for local
execution, it currently always serves from an in-memory simulated inbox,
structured the same way real results would be, so the rest of the app
(and the frontend) can be built against a stable contract.
"""
from datetime import datetime, timedelta

from app.core.config import settings

_MOCK_INBOX = [
    {
        "id": "mock-1",
        "from": "team@calendarapp.com",
        "subject": "Your weekly schedule digest",
        "snippet": "Here's what's coming up this week...",
        "received_at": datetime.utcnow() - timedelta(hours=3),
        "is_unread": True,
    },
    {
        "id": "mock-2",
        "from": "rahul@example.com",
        "subject": "Re: project kickoff",
        "snippet": "Sounds good, let's sync tomorrow after lunch.",
        "received_at": datetime.utcnow() - timedelta(hours=20),
        "is_unread": True,
    },
    {
        "id": "mock-3",
        "from": "billing@service.com",
        "subject": "Your invoice is ready",
        "snippet": "Your latest invoice has been generated.",
        "received_at": datetime.utcnow() - timedelta(days=2),
        "is_unread": False,
    },
]


def is_live() -> bool:
    return bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET)


def list_messages(user, unread_only: bool = False) -> dict:
    """Returns recent inbox messages. Falls back to simulated data when no live
    Google credentials are configured for this user."""
    if is_live() and getattr(user, "google_refresh_token", None):
        # Real Gmail API integration would go here using google-api-python-client.
        # Left unimplemented since no credentials are available in this environment.
        pass

    messages = _MOCK_INBOX
    if unread_only:
        messages = [m for m in messages if m["is_unread"]]
    return {"source": "mock", "messages": messages}
