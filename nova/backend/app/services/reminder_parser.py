"""
Natural-language reminder parser.

Parses phrases like:
  "Remind me to call Rahul tomorrow after lunch"
  "Remind me to take medicine every day at 9am"
  "Remind me to submit the report in 2 hours"
  "Remind me to pay rent on the 1st of every month"

This is a regex/rule-based parser (no LLM dependency required), matching the
plan's "regex and simple semantic rules" approach. It returns a structured
result with the cleaned title, reminder type (one-time/recurring), an optional
cron expression, and the computed next_trigger datetime.
"""
import re
from datetime import datetime, timedelta, time

# Rough anchor times for vague phrases
TIME_ANCHORS = {
    "morning": time(8, 0),
    "after lunch": time(13, 30),
    "lunch": time(12, 30),
    "afternoon": time(15, 0),
    "evening": time(18, 0),
    "night": time(21, 0),
    "noon": time(12, 0),
    "midnight": time(0, 0),
}

WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


class ParsedReminder:
    def __init__(self, title: str, type_: str, next_trigger: datetime, cron_expression: str | None = None):
        self.title = title
        self.type = type_
        self.next_trigger = next_trigger
        self.cron_expression = cron_expression

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "type": self.type,
            "next_trigger": self.next_trigger,
            "cron_expression": self.cron_expression,
        }


def _extract_clock_time(text: str) -> time | None:
    match = re.search(r"\b(\d{1,2})(:(\d{2}))?\s*(am|pm)\b", text)
    if not match:
        return None
    hour = int(match.group(1))
    minute = int(match.group(3) or 0)
    meridiem = match.group(4)
    if meridiem == "pm" and hour != 12:
        hour += 12
    if meridiem == "am" and hour == 12:
        hour = 0
    return time(hour, minute)


def _extract_anchor_time(text: str) -> time | None:
    for phrase, t in TIME_ANCHORS.items():
        if phrase in text:
            return t
    return None


def _strip_reminder_prefix(text: str) -> str:
    text = re.sub(r"^\s*remind me to\s+", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^\s*remind me\s+", "", text, flags=re.IGNORECASE)
    return text.strip()


def _strip_time_phrases(title: str) -> str:
    patterns = [
        r"\bevery\s+day\b", r"\bevery\s+\w+\b", r"\bdaily\b", r"\bweekly\b", r"\bmonthly\b",
        r"\btomorrow\b", r"\btoday\b", r"\btonight\b",
        r"\bin\s+\d+\s+(minute|minutes|hour|hours|day|days)\b",
        r"\bat\s+\d{1,2}(:\d{2})?\s*(am|pm)\b",
        r"\b\d{1,2}(:\d{2})?\s*(am|pm)\b",
        r"\bafter lunch\b", r"\bafter\s+\w+\b",
        r"\bon the \d{1,2}(st|nd|rd|th) of every month\b",
        r"\bmorning\b", r"\bafternoon\b", r"\bevening\b", r"\bnight\b", r"\bnoon\b", r"\bmidnight\b", r"\blunch\b",
    ]
    cleaned = title
    for p in patterns:
        cleaned = re.sub(p, "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip(" ,.")
    return cleaned


def parse_reminder(text: str, now: datetime | None = None) -> ParsedReminder:
    now = now or datetime.now()
    raw = text.strip()
    lowered = raw.lower()
    body = _strip_reminder_prefix(raw)
    lowered_body = body.lower()

    # --- Recurring: "every day", "every monday", "daily", "every month" ---
    recurring_match = re.search(r"\bevery\s+(day|week|month|year|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", lowered_body)
    is_daily = "daily" in lowered_body or (recurring_match and recurring_match.group(1) == "day")
    is_weekly_day = recurring_match and recurring_match.group(1) in WEEKDAYS
    is_monthly = recurring_match and recurring_match.group(1) == "month"
    monthly_date_match = re.search(r"\bon the (\d{1,2})(st|nd|rd|th)? of every month\b", lowered_body)

    clock = _extract_clock_time(lowered_body) or _extract_anchor_time(lowered_body)

    if is_daily or "daily" in lowered_body:
        t = clock or time(9, 0)
        cron = f"{t.minute} {t.hour} * * *"
        next_trigger = _next_daily_occurrence(now, t)
        title = _strip_time_phrases(body) or "Reminder"
        return ParsedReminder(title=title.capitalize(), type_="recurring", next_trigger=next_trigger, cron_expression=cron)

    if is_weekly_day:
        weekday_name = recurring_match.group(1)
        t = clock or time(9, 0)
        cron = f"{t.minute} {t.hour} * * {WEEKDAYS.index(weekday_name)}"
        next_trigger = _next_weekday_occurrence(now, WEEKDAYS.index(weekday_name), t)
        title = _strip_time_phrases(body) or "Reminder"
        return ParsedReminder(title=title.capitalize(), type_="recurring", next_trigger=next_trigger, cron_expression=cron)

    if monthly_date_match or is_monthly:
        day_of_month = int(monthly_date_match.group(1)) if monthly_date_match else now.day
        t = clock or time(9, 0)
        cron = f"{t.minute} {t.hour} {day_of_month} * *"
        next_trigger = _next_monthly_occurrence(now, day_of_month, t)
        title = _strip_time_phrases(body) or "Reminder"
        return ParsedReminder(title=title.capitalize(), type_="recurring", next_trigger=next_trigger, cron_expression=cron)

    # --- Relative: "in 2 hours", "in 30 minutes" ---
    relative_match = re.search(r"\bin\s+(\d+)\s+(minute|minutes|hour|hours|day|days)\b", lowered_body)
    if relative_match:
        amount = int(relative_match.group(1))
        unit = relative_match.group(2)
        if "minute" in unit:
            next_trigger = now + timedelta(minutes=amount)
        elif "hour" in unit:
            next_trigger = now + timedelta(hours=amount)
        else:
            next_trigger = now + timedelta(days=amount)
        title = _strip_time_phrases(body) or "Reminder"
        return ParsedReminder(title=title.capitalize(), type_="one-time", next_trigger=next_trigger)

    # --- One-time: "tomorrow", "today", with optional clock/anchor time ---
    base_day = now
    if "tomorrow" in lowered_body:
        base_day = now + timedelta(days=1)
    elif "tonight" in lowered_body:
        base_day = now
        clock = clock or time(20, 0)

    t = clock or time(9, 0)
    next_trigger = datetime.combine(base_day.date(), t)
    if next_trigger <= now and "tomorrow" not in lowered_body:
        next_trigger += timedelta(days=1)

    title = _strip_time_phrases(body) or "Reminder"
    return ParsedReminder(title=title.capitalize(), type_="one-time", next_trigger=next_trigger)


def _next_daily_occurrence(now: datetime, t: time) -> datetime:
    candidate = datetime.combine(now.date(), t)
    if candidate <= now:
        candidate += timedelta(days=1)
    return candidate


def _next_weekday_occurrence(now: datetime, weekday: int, t: time) -> datetime:
    days_ahead = (weekday - now.weekday()) % 7
    candidate = datetime.combine((now + timedelta(days=days_ahead)).date(), t)
    if candidate <= now:
        candidate += timedelta(days=7)
    return candidate


def _next_monthly_occurrence(now: datetime, day_of_month: int, t: time) -> datetime:
    year, month = now.year, now.month
    try:
        candidate = datetime(year, month, day_of_month, t.hour, t.minute)
    except ValueError:
        candidate = datetime(year, month, 28, t.hour, t.minute)
    if candidate <= now:
        month += 1
        if month > 12:
            month = 1
            year += 1
        try:
            candidate = datetime(year, month, day_of_month, t.hour, t.minute)
        except ValueError:
            candidate = datetime(year, month, 28, t.hour, t.minute)
    return candidate
