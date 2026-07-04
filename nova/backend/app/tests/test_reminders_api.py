from datetime import datetime, timedelta


def test_create_reminder_from_text(client, auth_headers):
    resp = client.post(
        "/reminders/parse",
        json={"text": "Remind me to call Rahul tomorrow after lunch"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    body = resp.json()
    assert "call rahul" in body["title"].lower()
    assert body["type"] == "one-time"


def test_dispatch_due_reminder_creates_notification(client, auth_headers):
    past_time = (datetime.utcnow() - timedelta(minutes=5)).isoformat()
    resp = client.post(
        "/reminders",
        json={"title": "Past due reminder", "type": "one-time", "next_trigger": past_time},
        headers=auth_headers,
    )
    assert resp.status_code == 201

    dispatch_resp = client.post("/reminders/dispatch-due", headers=auth_headers)
    assert dispatch_resp.status_code == 200
    assert dispatch_resp.json()["dispatched"] >= 1

    notif_resp = client.get("/notifications", headers=auth_headers)
    assert notif_resp.status_code == 200
    titles = [n["message"] for n in notif_resp.json()]
    assert "Past due reminder" in titles


def test_list_and_delete_reminder(client, auth_headers):
    resp = client.post("/reminders", json={"title": "Some reminder"}, headers=auth_headers)
    reminder_id = resp.json()["id"]

    list_resp = client.get("/reminders", headers=auth_headers)
    assert any(r["id"] == reminder_id for r in list_resp.json())

    del_resp = client.delete(f"/reminders/{reminder_id}", headers=auth_headers)
    assert del_resp.status_code == 204
