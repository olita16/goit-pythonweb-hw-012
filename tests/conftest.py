import sys
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest_asyncio


import fakeredis
from httpx import AsyncClient, ASGITransport

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from fastapi.testclient import TestClient
from main import app
from src.db.models import User
from src.db.connect import Base, get_db
from src.repository.auth import create_access_token, Hash
from src.settings.config import settings 

SQLALCHEMY_DATABASE_URL = settings.DB_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

test_user = {
    "email": "ironman@example.com",
    "password": "supersecure123",
    "first_name": "Tony",
    "last_name": "Stark",
    "avatar": "https://example.com/ironman.png",
    "confirmed": True,
}


@pytest.fixture(scope="module", autouse=True)
def init_models_wrap():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    hash_password = Hash().get_password_hash(test_user["password"])
    current_user = User(
        email=test_user["email"],
        password=hash_password,
        first_name=test_user["first_name"],
        last_name=test_user["last_name"],
        confirmed=test_user["confirmed"],
        avatar=test_user["avatar"],
    )
    db.add(current_user)
    db.commit()
    db.close()


@pytest_asyncio.fixture(scope="module")
async def client():
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture()
def get_token():
    from asyncio import run

    return run(create_access_token(data={"sub": test_user["email"]}))

@pytest.fixture(autouse=True)
def mock_redis(monkeypatch):
    fake_redis = fakeredis.FakeRedis(decode_responses=True)

    monkeypatch.setattr("src.services.auth.Auth.r", fake_redis)

@pytest.fixture(autouse=True)
def disable_email_sending(monkeypatch):
    async def fake_send_email(*args, **kwargs):
        return None

    monkeypatch.setattr("src.services.email.send_email", fake_send_email)
    monkeypatch.setattr("src.services.email.send_reset_password_email", fake_send_email)
