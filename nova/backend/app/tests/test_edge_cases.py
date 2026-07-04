from datetime import datetime, timedelta


def test_task_404_paths(client, auth_headers):
    assert client.get("/tasks/9999", headers=auth_headers).status_code == 404
    assert client.patch("/tasks/9999", json={"title": "x"}, headers=auth_headers).status_code == 404
    assert client.delete("/tasks/9999", headers=auth_headers).status_code == 404
    assert client.get("/tasks/9999/subtasks", headers=auth_headers).status_code == 404


def test_create_task_with_invalid_parent_404(client, auth_headers):
    resp = client.post("/tasks", json={"title": "Orphan", "parent_id": 9999}, headers=auth_headers)
    assert resp.status_code == 404


def test_habit_404_paths(client, auth_headers):
    assert client.get("/habits/9999", headers=auth_headers).status_code == 404
    assert client.delete("/habits/9999", headers=auth_headers).status_code == 404
    assert client.post("/habits/9999/logs", json={}, headers=auth_headers).status_code == 404
    assert client.get("/habits/9999/logs", headers=auth_headers).status_code == 404


def test_goal_404_paths(client, auth_headers):
    assert client.get("/goals/9999", headers=auth_headers).status_code == 404
    assert client.patch("/goals/9999", json={"title": "x"}, headers=auth_headers).status_code == 404
    assert client.delete("/goals/9999", headers=auth_headers).status_code == 404
    assert client.post("/goals/9999/milestones", json={"title": "x"}, headers=auth_headers).status_code == 404


def test_milestone_404(client, auth_headers):
    goal = client.post("/goals", json={"title": "Goal"}, headers=auth_headers).json()
    resp = client.patch(f"/goals/{goal['id']}/milestones/9999/complete", headers=auth_headers)
    assert resp.status_code == 404


def test_note_404_paths(client, auth_headers):
    assert client.get("/notes/9999", headers=auth_headers).status_code == 404
    assert client.patch("/notes/9999", json={"title": "x"}, headers=auth_headers).status_code == 404
    assert client.delete("/notes/9999", headers=auth_headers).status_code == 404


def test_reminder_404_paths(client, auth_headers):
    assert client.patch("/reminders/9999", json={"title": "x"}, headers=auth_headers).status_code == 404
    assert client.delete("/reminders/9999", headers=auth_headers).status_code == 404


def test_chat_with_invalid_conversation_id_404(client, auth_headers):
    resp = client.post("/chat/message", json={"text": "hi", "conversation_id": 9999}, headers=auth_headers)
    assert resp.status_code == 404
    resp2 = client.get("/chat/conversations/9999/messages", headers=auth_headers)
    assert resp2.status_code == 404


def test_recurring_reminder_dispatch_reschedules(client, auth_headers):
    past_time = (datetime.utcnow() - timedelta(minutes=1)).isoformat()
    resp = client.post(
        "/reminders",
        json={
            "title": "Daily standup",
            "type": "recurring",
            "cron_expression": "0 9 * * *",
            "next_trigger": past_time,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    reminder_id = resp.json()["id"]

    dispatch_resp = client.post("/reminders/dispatch-due", headers=auth_headers)
    assert dispatch_resp.status_code == 200

    reminders = client.get("/reminders", headers=auth_headers).json()
    updated = next(r for r in reminders if r["id"] == reminder_id)
    assert updated["is_sent"] is False  # recurring reminders stay active
    assert updated["next_trigger"] is not None
