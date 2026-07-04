"""Streak calculation logic for habits."""
from datetime import date, timedelta

from app.models.habit_goal import Habit


def record_completion(habit: Habit, log_date: date) -> Habit:
    """Updates streak_count given a new completion on log_date.

    - If log_date is exactly one day after last_completed_date -> streak continues (+1).
    - If log_date == last_completed_date -> no-op (already logged today).
    - If log_date is more than one day after last_completed_date -> streak resets to 1.
    - If there's no prior completion -> streak starts at 1.
    """
    if habit.last_completed_date is None:
        habit.streak_count = 1
    elif log_date == habit.last_completed_date:
        return habit  # already logged for this date
    elif log_date == habit.last_completed_date + timedelta(days=1):
        habit.streak_count += 1
    elif log_date > habit.last_completed_date:
        habit.streak_count = 1
    # if log_date is earlier than last_completed_date (backfilled past log), don't touch streak

    if habit.last_completed_date is None or log_date >= habit.last_completed_date:
        habit.last_completed_date = log_date

    return habit


def record_miss(habit: Habit, log_date: date) -> Habit:
    """A missed day resets the streak if it's the day right after the last completion."""
    if habit.last_completed_date and log_date > habit.last_completed_date:
        habit.streak_count = 0
    return habit
