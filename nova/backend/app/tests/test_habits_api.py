from datetime import date, timedelta


def test_create_habit_and_log_streak(client, auth_headers):
    resp = client.post("/habits", json={"name": "Drink water", "category": "health"}, headers=auth_headers)
    assert resp.status_code == 201
    habit_id = resp.json()["id"]

    day1 = date(2026, 6, 1)
    day2 = day1 + timedelta(days=1)
    day3 = day1 + timedelta(days=2)

    r1 = client.post(f"/habits/{habit_id}/logs", json={"date": day1.isoformat(), "status": "completed"}, headers=auth_headers)
    assert r1.status_code == 201

    r2 = client.post(f"/habits/{habit_id}/logs", json={"date": day2.isoformat(), "status": "completed"}, headers=auth_headers)
    assert r2.status_code == 201

    r3 = client.post(f"/habits/{habit_id}/logs", json={"date": day3.isoformat(), "status": "completed"}, headers=auth_headers)
    assert r3.status_code == 201

    habit = client.get(f"/habits/{habit_id}", headers=auth_headers).json()
    assert habit["streak_count"] == 3
    assert habit["last_completed_date"] == day3.isoformat()


def test_streak_resets_after_gap(client, auth_headers):
    resp = client.post("/habits", json={"name": "Meditate"}, headers=auth_headers)
    habit_id = resp.json()["id"]

    day1 = date(2026, 6, 1)
    gap_day = day1 + timedelta(days=5)

    client.post(f"/habits/{habit_id}/logs", json={"date": day1.isoformat()}, headers=auth_headers)
    client.post(f"/habits/{habit_id}/logs", json={"date": gap_day.isoformat()}, headers=auth_headers)

    habit = client.get(f"/habits/{habit_id}", headers=auth_headers).json()
    assert habit["streak_count"] == 1


def test_habit_logs_listing(client, auth_headers):
    resp = client.post("/habits", json={"name": "Read"}, headers=auth_headers)
    habit_id = resp.json()["id"]
    client.post(f"/habits/{habit_id}/logs", json={"date": "2026-06-01"}, headers=auth_headers)
    client.post(f"/habits/{habit_id}/logs", json={"date": "2026-06-02"}, headers=auth_headers)

    logs = client.get(f"/habits/{habit_id}/logs", headers=auth_headers).json()
    assert len(logs) == 2
