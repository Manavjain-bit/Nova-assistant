def test_send_message_creates_conversation_and_fallback_reply(client, auth_headers):
    resp = client.post("/chat/message", json={"text": "remind me about my plans"}, headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["source"] in ("local_fallback", "local_fallback_error")
    assert body["user_message"]["text_content"] == "remind me about my plans"
    assert body["assistant_message"]["sender"] == "assistant"


def test_send_message_continues_existing_conversation(client, auth_headers):
    first = client.post("/chat/message", json={"text": "hello"}, headers=auth_headers).json()
    conv_id = first["conversation_id"]

    second = client.post(
        "/chat/message", json={"text": "how are you", "conversation_id": conv_id}, headers=auth_headers
    )
    assert second.status_code == 200
    assert second.json()["conversation_id"] == conv_id

    messages = client.get(f"/chat/conversations/{conv_id}/messages", headers=auth_headers)
    assert messages.status_code == 200
    assert len(messages.json()) == 4  # 2 user + 2 assistant


def test_long_term_memory_extracted_from_chat(client, auth_headers):
    client.post("/chat/message", json={"text": "my name is Priya"}, headers=auth_headers)
    resp = client.get("/chat/memory", headers=auth_headers)
    assert resp.status_code == 200
    keys = [m["key"] for m in resp.json()]
    assert "name" in keys


def test_list_conversations(client, auth_headers):
    client.post("/chat/message", json={"text": "first conversation"}, headers=auth_headers)
    resp = client.get("/chat/conversations", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 1
