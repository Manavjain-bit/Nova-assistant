def test_create_and_search_notes(client, auth_headers):
    client.post("/notes", json={"title": "Grocery list", "content": "milk, eggs, bread", "tags": ["home"]}, headers=auth_headers)
    client.post("/notes", json={"title": "Meeting notes", "content": "discuss roadmap", "tags": ["work"]}, headers=auth_headers)

    resp = client.get("/notes?q=roadmap", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["title"] == "Meeting notes"


def test_pin_and_filter_notes(client, auth_headers):
    resp = client.post("/notes", json={"title": "Important", "is_pinned": True}, headers=auth_headers)
    assert resp.status_code == 201

    pinned = client.get("/notes?pinned_only=true", headers=auth_headers).json()
    assert any(n["title"] == "Important" for n in pinned)


def test_update_and_delete_note(client, auth_headers):
    resp = client.post("/notes", json={"title": "Draft"}, headers=auth_headers)
    note_id = resp.json()["id"]

    update_resp = client.patch(f"/notes/{note_id}", json={"content": "final content"}, headers=auth_headers)
    assert update_resp.status_code == 200
    assert update_resp.json()["content"] == "final content"

    del_resp = client.delete(f"/notes/{note_id}", headers=auth_headers)
    assert del_resp.status_code == 204
