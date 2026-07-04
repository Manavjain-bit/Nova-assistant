def test_register_and_login(client):
    resp = client.post("/auth/register", json={"email": "a@nova.ai", "password": "pass1234"})
    assert resp.status_code == 201
    assert resp.json()["email"] == "a@nova.ai"

    resp = client.post("/auth/login", data={"username": "a@nova.ai", "password": "pass1234"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password(client):
    client.post("/auth/register", json={"email": "b@nova.ai", "password": "pass1234"})
    resp = client.post("/auth/login", data={"username": "b@nova.ai", "password": "wrong"})
    assert resp.status_code == 401


def test_duplicate_registration_rejected(client):
    client.post("/auth/register", json={"email": "dup@nova.ai", "password": "pass1234"})
    resp = client.post("/auth/register", json={"email": "dup@nova.ai", "password": "pass1234"})
    assert resp.status_code == 400
