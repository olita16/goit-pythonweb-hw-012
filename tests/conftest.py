import sys
import os
import pytest
import asyncio
import pytest_asyncio
from sqlalchemy import create_engine

# Додаємо корінь проєкту в sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from main import app
from src.databases.models import User
from src.databases.connect import Base, get_db
from src.repository.auth import create_access_token, Hash


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"


engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

test_user = {
    "email": "deadpool@example.com",
    "password": "12345678",
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
        first_name="Wade",
        last_name="Wilson",
        confirmed=True,
        avatar="https://twitter.com/gravatar",
    )
    db.add(current_user)
    db.commit()
    db.close()


@pytest.fixture(scope="module")
def client():
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)


@pytest.fixture()
def get_token():
    from asyncio import run

    return run(create_access_token(data={"sub": test_user["email"]}))
