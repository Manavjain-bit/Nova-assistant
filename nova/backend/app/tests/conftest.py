import os
import pytest
from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite:///./test_nova.db"
os.environ["SECRET_KEY"] = "test-secret"

from app.main import app  # noqa: E402
from app.core.database import Base, engine  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test_nova.db"):
        os.remove("./test_nova.db")


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers(client):
    client.post("/auth/register", json={"email": "test@nova.ai", "password": "secret123", "full_name": "Test User"})
    resp = client.post("/auth/login", data={"username": "test@nova.ai", "password": "secret123"})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
