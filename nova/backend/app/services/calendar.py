"""
Google Calendar connector service. Same mock-fallback pattern as gmail.py.
"""
from datetime import datetime, timedelta

from app.core.config import settings

_now = datetime.utcnow()

_MOCK_EVENTS = [
    {
        "id": "evt-1",
        "title": "Team standup",
        "start": _now.replace(hour=9, minute=30, second=0, microsecond=0),
        "end": _now.replace(hour=9, minute=45, second=0, microsecond=0),
        "location": "Zoom",
    },
    {
        "id": "evt-2",
        "title": "1:1 with manager",
        "start": _now.replace(hour=14, minute=0, second=0, microsecond=0),
        "end": _now.replace(hour=14, minute=30, second=0, microsecond=0),
        "location": "Office",
    },
    {
        "id": "evt-3",
        "title": "Dentist appointment",
        "start": (_now + timedelta(days=1)).replace(hour=11, minute=0, second=0, microsecond=0),
        "end": (_now + timedelta(days=1)).replace(hour=12, minute=0, second=0, microsecond=0),
        "location": "Downtown Clinic",
    },
]


def is_live() -> bool:
    return bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET)


def list_events(user, days_ahead: int = 1) -> dict:
    """Returns upcoming calendar events within `days_ahead` days. Falls back to
    simulated events when no live Google credentials are configured."""
    if is_live() and getattr(user, "google_refresh_token", None):
        # Real Calendar API integration would go here using google-api-python-client.
        pass

    horizon = datetime.utcnow() + timedelta(days=days_ahead)
    events = [e for e in _MOCK_EVENTS if e["start"] <= horizon]
    return {"source": "mock", "events": events}
