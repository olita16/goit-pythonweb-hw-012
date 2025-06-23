import pytest
from unittest.mock import MagicMock

from src.repository import user as user_repo
from src.databases.models import User
from src.schemas.auth import UserModel


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def test_user():
    return User(
        id=1, email="test@example.com", confirmed=False, avatar=None, password="old"
    )


@pytest.mark.asyncio
async def test_get_user_by_email(mock_db, test_user):
    mock_db.query().filter_by().first.return_value = test_user
    result = await user_repo.get_user_by_email("test@example.com", mock_db)
    assert result.email == "test@example.com"


@pytest.mark.asyncio
async def test_create_user(mock_db):
    body = UserModel(username="john", email="john@example.com", password="secret")
    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock()

    result = await user_repo.create_user(body, mock_db)
    assert result.email == body.email
    mock_db.add.assert_called()
    mock_db.commit.assert_called()


@pytest.mark.asyncio
async def test_change_confirmed_email(mock_db, test_user):
    mock_db.query().filter_by().first.return_value = test_user
    await user_repo.change_confirmed_email("test@example.com", mock_db)
    assert test_user.confirmed is True
    mock_db.commit.assert_called()


@pytest.mark.asyncio
async def test_update_avatar_url(mock_db, test_user):
    mock_db.query().filter_by().first.return_value = test_user
    url = "http://example.com/avatar.png"

    result = await user_repo.update_avatar_url("test@example.com", url, mock_db)
    assert result.avatar == url
    mock_db.commit.assert_called()
    mock_db.refresh.assert_called()


@pytest.mark.asyncio
async def test_update_user_password(mock_db, test_user):
    mock_db.query().filter_by().first.return_value = test_user
    result = await user_repo.update_user_password(
        "test@example.com", "hashed123", mock_db
    )
    assert result.password == "hashed123"
    mock_db.commit.assert_called()


@pytest.mark.asyncio
async def test_update_user_password_user_not_found(mock_db):
    mock_db.query().filter_by().first.return_value = None
    result = await user_repo.update_user_password(
        "unknown@example.com", "hashed123", mock_db
    )
    assert result is None
