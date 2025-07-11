import pytest
from fastapi import HTTPException
from jose import jwt
from src.repository.auth import (
    Hash,
    create_access_token,
    create_email_token,
    get_email_from_token,
)
from src.settings.base import SECRET_KEY, ALGORITHM


def test_hash_and_verify_password():

    password = "securepassword123"
    hasher = Hash()
    hashed = hasher.get_password_hash(password)

    assert hashed != password
    assert hasher.verify_password(password, hashed) 
    assert not hasher.verify_password("wrongpassword", hashed) 


@pytest.mark.asyncio
async def test_create_access_token_and_get_email():

    payload = {"sub": "user@example.com"}
    token = await create_access_token(payload, expires_delta=60)

    assert isinstance(token, str)

    email = await get_email_from_token(token)
    assert email == "user@example.com"


def test_create_email_token_contents():

    token = create_email_token({"sub": "mail@example.com"})
    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert decoded["sub"] == "mail@example.com"
    assert "exp" in decoded
    assert "iat" in decoded


@pytest.mark.asyncio
async def test_get_email_from_token_invalid():
    with pytest.raises(HTTPException) as exc_info:
        await get_email_from_token("this.is.invalid")

    exc = exc_info.value
    assert exc.status_code == 422
    assert exc.detail == "Invalid token for email verification"
