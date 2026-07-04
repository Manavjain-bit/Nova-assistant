import os


def test_gmail_mock_messages(client, auth_headers):
    resp = client.get("/integrations/gmail/messages", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["source"] == "mock"
    assert len(body["messages"]) > 0


def test_gmail_unread_filter(client, auth_headers):
    resp = client.get("/integrations/gmail/messages?unread_only=true", headers=auth_headers)
    assert resp.status_code == 200
    assert all(m["is_unread"] for m in resp.json()["messages"])


def test_calendar_mock_events(client, auth_headers):
    resp = client.get("/integrations/calendar/events?days_ahead=2", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["source"] == "mock"
    assert len(body["events"]) > 0


def test_file_search_finds_indexed_text_file(client, auth_headers, tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "todo.txt").write_text("buy milk and call the bank")
    (workspace / "ignore.bin").write_text("binary stuff")

    from app.core.config import settings
    monkeypatch.setattr(settings, "FILE_SEARCH_WORKSPACE_DIR", str(workspace))

    resp = client.get("/integrations/files/search?q=bank", headers=auth_headers)
    assert resp.status_code == 200
    results = resp.json()["results"]
    assert len(results) == 1
    assert results[0]["filename"] == "todo.txt"
