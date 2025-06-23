from unittest.mock import Mock

import pytest
from sqlalchemy import select

from src.databases.models import User
from tests.conftest import TestingSessionLocal
from src.repository.auth import Hash

user_data = {
    "email": "agent007@gmail.com",
    "password": "12345678",
    "first_name": "James",
    "last_name": "Bond",
}


def test_signup(client, monkeypatch):

    mock_send_email = Mock()
    monkeypatch.setattr("src.services.email.send_email", mock_send_email)

    response = client.post("/auth/signup", json=user_data)
    assert response.status_code == 201, response.text

    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["first_name"] == user_data["first_name"]
    assert data["last_name"] == user_data["last_name"]
    assert "id" in data
    assert "avatar" in data
    assert "password" not in data


def test_login_success(client, monkeypatch):
    # спочатку реєструємо (чи переконуємося, що є) цей користувач
    client.post("/auth/signup", json=user_data)

    # вручну ставимо confirmed=True
    db = TestingSessionLocal()
    user = db.query(User).filter_by(email=user_data["email"]).first()
    user.confirmed = True
    db.commit()
    db.close()

    # тепер логін
    response = client.post(
        "/auth/login",
        json={"email": user_data["email"], "password": user_data["password"]},
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_email(client):
    response = client.post(
        "/auth/login", json={"email": "wrong@example.com", "password": "any"}
    )
    assert response.status_code == 401


def test_login_invalid_password(client):
    response = client.post(
        "/auth/login", json={"email": user_data["email"], "password": "wrongpassword"}
    )
    assert response.status_code == 401
