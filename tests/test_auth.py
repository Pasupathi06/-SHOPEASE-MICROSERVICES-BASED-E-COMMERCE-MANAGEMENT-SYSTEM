"""
Pytest integration tests for ShopEase Auth Service.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.connection import SessionLocal, init_db
from app.models.user_model import User


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    init_db()


@pytest.fixture
def client():
    return TestClient(app)


def test_health_check(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_default_seeded_user_login(client: TestClient):
    """Verify default seeded credentials pasu / pasupathi@123 login works."""
    response = client.post("/api/auth/login", json={
        "email": "pasu@shopease.com",
        "password": "pasupathi@123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "pasu@shopease.com"


def test_get_current_user_me(client: TestClient):
    """Test /api/auth/me using JWT token."""
    login_res = client.post("/api/auth/login", json={
        "email": "pasu@shopease.com",
        "password": "pasupathi@123"
    })
    token = login_res.json()["access_token"]

    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["email"] == "pasu@shopease.com"
    assert me_data["full_name"] == "pasu"


def test_protected_me_without_token(client: TestClient):
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_verify_token_endpoint(client: TestClient):
    login_res = client.post("/api/auth/login", json={
        "email": "pasu@shopease.com",
        "password": "pasupathi@123"
    })
    token = login_res.json()["access_token"]

    verify_res = client.post("/api/auth/verify-token", json={"token": token})
    assert verify_res.status_code == 200
    assert verify_res.json()["valid"] is True
