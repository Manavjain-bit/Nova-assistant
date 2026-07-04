def test_create_and_get_task(client, auth_headers):
    resp = client.post("/tasks", json={"title": "Buy groceries", "priority": "medium"}, headers=auth_headers)
    assert resp.status_code == 201
    body = resp.json()
    assert body["title"] == "Buy groceries"
    assert body["priority_score"] > 0

    task_id = body["id"]
    resp = client.get(f"/tasks/{task_id}", headers=auth_headers)
    assert resp.status_code == 200


def test_update_task_status(client, auth_headers):
    resp = client.post("/tasks", json={"title": "Write report"}, headers=auth_headers)
    task_id = resp.json()["id"]

    resp = client.patch(f"/tasks/{task_id}", json={"status": "completed"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "completed"


def test_delete_task(client, auth_headers):
    resp = client.post("/tasks", json={"title": "Temp task"}, headers=auth_headers)
    task_id = resp.json()["id"]

    resp = client.delete(f"/tasks/{task_id}", headers=auth_headers)
    assert resp.status_code == 204

    resp = client.get(f"/tasks/{task_id}", headers=auth_headers)
    assert resp.status_code == 404


def test_subtasks(client, auth_headers):
    parent = client.post("/tasks", json={"title": "Plan trip"}, headers=auth_headers).json()
    child = client.post(
        "/tasks", json={"title": "Book flights", "parent_id": parent["id"]}, headers=auth_headers
    )
    assert child.status_code == 201

    resp = client.get(f"/tasks/{parent['id']}/subtasks", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_unauthenticated_access_rejected(client):
    resp = client.get("/tasks")
    assert resp.status_code == 401
