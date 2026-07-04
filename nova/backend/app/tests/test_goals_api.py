def test_create_goal_and_complete_milestones(client, auth_headers):
    resp = client.post("/goals", json={"title": "Learn Spanish", "type": "long-term"}, headers=auth_headers)
    assert resp.status_code == 201
    goal_id = resp.json()["id"]

    m1 = client.post(f"/goals/{goal_id}/milestones", json={"title": "Finish beginner course"}, headers=auth_headers)
    m2 = client.post(f"/goals/{goal_id}/milestones", json={"title": "Have a 10 min conversation"}, headers=auth_headers)
    assert m1.status_code == 201 and m2.status_code == 201

    m1_id = m1.json()["id"]
    complete_resp = client.patch(f"/goals/{goal_id}/milestones/{m1_id}/complete", headers=auth_headers)
    assert complete_resp.status_code == 200
    assert complete_resp.json()["is_completed"] is True

    goal = client.get(f"/goals/{goal_id}", headers=auth_headers).json()
    assert goal["progress_percentage"] == 50.0


def test_update_goal(client, auth_headers):
    resp = client.post("/goals", json={"title": "Run a marathon"}, headers=auth_headers)
    goal_id = resp.json()["id"]

    update_resp = client.patch(f"/goals/{goal_id}", json={"progress_percentage": 25.0}, headers=auth_headers)
    assert update_resp.status_code == 200
    assert update_resp.json()["progress_percentage"] == 25.0


def test_delete_goal(client, auth_headers):
    resp = client.post("/goals", json={"title": "Temp goal"}, headers=auth_headers)
    goal_id = resp.json()["id"]

    del_resp = client.delete(f"/goals/{goal_id}", headers=auth_headers)
    assert del_resp.status_code == 204
