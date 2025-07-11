import pytest
from fastapi import status
from src.repository.auth import Hash

@pytest.mark.asyncio
async def test_signup_success(client):
    user_data = {
        "email": "newuser@example.com",
        "password": "newpassword",
        "first_name": "New",
        "last_name": "User"
    }
    response = await client.post("/auth/signup", json=user_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == user_data["email"]

@pytest.mark.asyncio
async def test_signup_existing_email(client):

    user_data = {
        "email": "ironman@example.com",
        "password": "anyPassword123",
        "first_name": "Tony",
        "last_name": "Stark"
    }
    response = await client.post("/auth/signup", json=user_data)
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "Account already exists"

@pytest.mark.asyncio
async def test_login_success(client):
    login_data = {"email": "ironman@example.com", "password": "supersecure123"}
    response = await client.post("/auth/login", json=login_data)
    assert response.status_code == status.HTTP_201_CREATED
    tokens = response.json()
    assert "access_token" in tokens
    assert tokens["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_invalid_email(client):
    login_data = {"email": "no_such_user@example.com", "password": "password"}
    response = await client.post("/auth/login", json=login_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Invalid email"

@pytest.mark.asyncio
async def test_login_invalid_password(client):
    login_data = {"email": "ironman@example.com", "password": "wrongpassword"}
    response = await client.post("/auth/login", json=login_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Invalid password"

@pytest.mark.asyncio
async def test_login_unconfirmed_email(client):

    user_data = {
        "email": "unconfirmed@example.com",
        "password": "password123",
        "first_name": "Unconfirmed",
        "last_name": "User"
    }
    await client.post("/auth/signup", json=user_data)

    login_data = {"email": "unconfirmed@example.com", "password": "password123"}
    response = await client.post("/auth/login", json=login_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Email not confirmed"


@pytest.mark.asyncio
async def test_request_reset_password_nonexistent_email(client, monkeypatch):
    async def fake_send_reset_password_email(email, reset_link):
        pytest.fail("Email should not be sent for nonexistent user")

    monkeypatch.setattr("src.services.email.send_reset_password_email", fake_send_reset_password_email)

    response = await client.post("/auth/request-reset-password", json={"email": "noone@example.com"})
    assert response.status_code == status.HTTP_200_OK
    assert "message" in response.json()


@pytest.mark.asyncio
async def test_hash_and_verify_password():
    hasher = Hash()
    password = "securepassword"
    hashed = hasher.get_password_hash(password)
    assert hasher.verify_password(password, hashed)
    assert not hasher.verify_password("wrongpassword", hashed)
