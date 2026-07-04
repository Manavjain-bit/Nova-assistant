from datetime import datetime, timedelta

from app.services.reminder_parser import parse_reminder


def test_relative_in_n_hours():
    now = datetime(2026, 6, 27, 10, 0)
    result = parse_reminder("Remind me to submit the report in 2 hours", now=now)
    assert result.type == "one-time"
    assert result.next_trigger == now + timedelta(hours=2)
    assert "submit the report" in result.title.lower()


def test_tomorrow_after_lunch():
    now = datetime(2026, 6, 27, 9, 0)
    result = parse_reminder("Remind me to call Rahul tomorrow after lunch", now=now)
    assert result.type == "one-time"
    assert result.next_trigger.date() == (now + timedelta(days=1)).date()
    assert result.next_trigger.hour == 13
    assert "call rahul" in result.title.lower()


def test_daily_recurring_with_clock_time():
    now = datetime(2026, 6, 27, 9, 0)
    result = parse_reminder("Remind me to take medicine every day at 9am", now=now)
    assert result.type == "recurring"
    assert result.cron_expression == "0 9 * * *"


def test_today_with_explicit_time_in_past_rolls_to_tomorrow():
    now = datetime(2026, 6, 27, 20, 0)
    result = parse_reminder("Remind me to water the plants at 8am", now=now)
    assert result.next_trigger.date() == (now + timedelta(days=1)).date()
    assert result.next_trigger.hour == 8


def test_monthly_recurring_with_day_of_month():
    now = datetime(2026, 6, 27, 9, 0)
    result = parse_reminder("Remind me to pay rent on the 1st of every month", now=now)
    assert result.type == "recurring"
    assert result.next_trigger.day == 1
    assert result.next_trigger.month == 7  # next month since 27th has passed the 1st
