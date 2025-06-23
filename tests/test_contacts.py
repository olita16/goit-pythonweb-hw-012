import pytest
from unittest.mock import MagicMock, AsyncMock

from src.repository import contacts
from src.databases.models import Contact, User
from datetime import date, timedelta


@pytest.fixture
def mock_user():
    return User(id=1, email="test@example.com")


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.mark.asyncio
async def test_create_contact(mock_db, mock_user):
    body = MagicMock()
    body.model_dump.return_value = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
    }

    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock()

    result = await contacts.create_contact(body, mock_db, mock_user)

    assert result.user_id == mock_user.id
    mock_db.add.assert_called()
    mock_db.commit.assert_called()


@pytest.mark.asyncio
async def test_get_contacts(mock_db, mock_user):
    expected_contacts = [Contact(id=1), Contact(id=2)]
    mock_db.query().filter().all.return_value = expected_contacts

    result = await contacts.get_contacts(mock_db, mock_user)

    assert result == expected_contacts


@pytest.mark.asyncio
async def test_get_contact_by_id_found(mock_db, mock_user):
    contact = Contact(id=1, user_id=mock_user.id)
    mock_db.query().filter().first.return_value = contact

    result = await contacts.get_contact_by_id(1, mock_db, mock_user)
    assert result == contact


@pytest.mark.asyncio
async def test_get_contact_by_id_not_found(mock_db, mock_user):
    mock_db.query().filter().first.return_value = None

    with pytest.raises(Exception) as exc:
        await contacts.get_contact_by_id(99, mock_db, mock_user)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_contact(mock_db, mock_user):
    contact = Contact(id=1, user_id=mock_user.id)
    mock_db.query().filter().first.return_value = contact

    result = await contacts.delete_contact(1, mock_db, mock_user)
    mock_db.delete.assert_called_with(contact)
    assert result == contact


@pytest.mark.asyncio
async def test_update_contact(mock_db, mock_user):
    contact = Contact(id=1, user_id=mock_user.id, first_name="Old")
    mock_db.query().filter().first.return_value = contact

    body = MagicMock()
    body.model_dump.return_value = {"first_name": "New"}

    result = await contacts.update_contact(1, body, mock_db, mock_user)
    assert contact.first_name == "New"
    assert result == contact


@pytest.mark.asyncio
async def test_search_contacts_by_email(mock_db, mock_user):
    expected = [Contact(id=1, email="a@example.com")]
    mock_db.query().filter().filter().all.return_value = expected

    result = await contacts.search_contacts(
        None, None, "a@example.com", mock_db, mock_user
    )
    assert result == expected


@pytest.mark.asyncio
async def test_upcoming_birthdays(mock_db, mock_user):
    today = date.today()
    next_week = today + timedelta(days=5)
    contact = Contact(id=1, user_id=mock_user.id, birthday=next_week)

    mock_db.query().filter().all.return_value = [contact]
    result = await contacts.upcoming_birthdays(mock_db, mock_user)

    assert contact in result
