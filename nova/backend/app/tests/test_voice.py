import io


def test_voice_capabilities_reports_fallback_when_no_keys(client, auth_headers):
    resp = client.get("/voice/capabilities", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["stt_available_server_side"] is False
    assert body["tts_available_server_side"] is False
    assert "browser_fallback" in body


def test_tts_falls_back_without_key(client, auth_headers):
    resp = client.post("/voice/tts", json={"text": "Hello there"}, headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["source"] == "fallback"
    assert body["audio_base64"] is None
    assert "Web Speech" in body["fallback_reason"]


def test_stt_falls_back_without_key(client, auth_headers):
    fake_audio = io.BytesIO(b"not real audio bytes")
    resp = client.post(
        "/voice/stt",
        headers=auth_headers,
        files={"audio": ("test.webm", fake_audio, "audio/webm")},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["source"] == "fallback"
    assert body["text"] is None
