def test_morning_briefing_structure(client, auth_headers):
    client.post("/tasks", json={"title": "Finish slides", "priority": "urgent"}, headers=auth_headers)
    resp = client.get("/briefing/morning", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert "greeting" in body
    assert "schedule" in body
    assert "top_tasks" in body
    assert any(t["title"] == "Finish slides" for t in body["top_tasks"])


def test_night_review_reflects_completed_tasks(client, auth_headers):
    resp = client.post("/tasks", json={"title": "Ship feature"}, headers=auth_headers)
    task_id = resp.json()["id"]
    client.patch(f"/tasks/{task_id}", json={"status": "completed"}, headers=auth_headers)

    review = client.post("/briefing/night-review", json={"mood": "good", "productivity_rating": 8}, headers=auth_headers)
    assert review.status_code == 200
    body = review.json()
    assert body["mood"] == "good"
    assert any(t["title"] == "Ship feature" for t in body["completed_today"])
