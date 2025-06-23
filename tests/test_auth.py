from fastapi import HTTPException
import pytest
from jose import jwt, JWTError
from src.repository.auth import (
    Hash,
    create_access_token,
    create_email_token,
    get_email_from_token,
)
from src.settings.base import SECRET_KEY, ALGORITHM


@pytest.mark.asyncio
async def test_create_access_token_and_decode():
    """Перевіряє, що токен створюється і коректно декодується."""
    data = {"sub": "test@example.com"}
    token = await create_access_token(data, expires_delta=60)
    decoded_email = await get_email_from_token(token)
    assert decoded_email == "test@example.com"


def test_create_email_token_valid():
    """Перевіряє, що токен для email містить коректну підписану інформацію."""
    token = create_email_token({"sub": "mail@example.com"})
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "mail@example.com"
    assert "exp" in payload
    assert "iat" in payload


@pytest.mark.asyncio
async def test_get_email_from_token_invalid():
    """Перевірка, що викликається помилка для невалідного токена."""
    with pytest.raises(HTTPException) as exc:
        await get_email_from_token("invalid.token.value")
    assert exc.value.status_code == 422
    assert exc.value.detail == "Invalid token for email verification"


def test_hash_and_verify_password():
    """Перевіряє, що паролі хешуються і перевірка працює коректно."""
    hasher = Hash()
    password = "securepassword"
    hashed = hasher.get_password_hash(password)
    assert hasher.verify_password(password, hashed)
    assert not hasher.verify_password("wrongpassword", hashed)
