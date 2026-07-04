from datetime import datetime, timedelta, timezone

from app.models.task import Task
from app.services.prioritization import compute_priority_score


def make_task(**kwargs) -> Task:
    defaults = dict(user_id=1, title="t", status="pending", priority="medium")
    defaults.update(kwargs)
    return Task(**defaults)


def test_overdue_task_scores_higher_than_far_future():
    overdue = make_task(due_date=datetime.now(timezone.utc) - timedelta(days=1))
    future = make_task(due_date=datetime.now(timezone.utc) + timedelta(days=30))

    assert compute_priority_score(overdue) > compute_priority_score(future)


def test_urgent_priority_scores_higher_than_low_at_same_due_date():
    due = datetime.now(timezone.utc) + timedelta(days=2)
    urgent = make_task(priority="urgent", due_date=due)
    low = make_task(priority="low", due_date=due)

    assert compute_priority_score(urgent) > compute_priority_score(low)


def test_shorter_estimated_duration_gets_slight_boost():
    due = datetime.now(timezone.utc) + timedelta(days=2)
    quick = make_task(due_date=due, estimated_duration=10)
    long_task = make_task(due_date=due, estimated_duration=300)

    assert compute_priority_score(quick) > compute_priority_score(long_task)


def test_score_is_bounded_reasonably():
    task = make_task(priority="urgent", due_date=datetime.now(timezone.utc) - timedelta(days=5), estimated_duration=5)
    score = compute_priority_score(task)
    assert 0 <= score <= 100
