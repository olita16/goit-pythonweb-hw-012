from fastapi import APIRouter, Depends, Query, status
from src.db.models import User
from src.db.connect import get_db
from src.repository import contacts
from src.schemas import contacts as schemas_contact
from src.services.auth import auth_service

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.post(
    "/",
    response_model=schemas_contact.ContactResponse,
    name="API for create contact",
    status_code=status.HTTP_201_CREATED,
)
async def create_contact(
    body: schemas_contact.ContactModel,
    db=Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    """
    Створює новий контакт для поточного користувача.

    :param body: Дані нового контакту.
    :type body: ContactModel
    :param db: Сесія бази даних.
    :param user: Поточний авторизований користувач.
    :return: Створений контакт.
    :rtype: ContactResponse
    """
    contact = await contacts.create_contact(body, db, user)
    return contact


@router.get("/search", name="Search contacts")
async def search_contacts(
    first_name: str | None = Query(default=None),
    last_name: str | None = Query(default=None),
    email: str | None = Query(default=None),
    db=Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    """
    Пошук контактів по імені, прізвищу та/або email.

    :param first_name: Ім'я для пошуку (необов’язково).
    :param last_name: Прізвище для пошуку (необов’язково).
    :param email: Email для пошуку (необов’язково).
    :param db: Сесія бази даних.
    :param user: Поточний авторизований користувач.
    :return: Список контактів, які відповідають критеріям пошуку.
    """
    return await contacts.search_contacts(first_name, last_name, email, db, user)


@router.get("/birthdays", name="Upcoming birthdays (7 days)")
async def get_upcoming_birthdays(
    db=Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    """
    Отримати контакти з днями народження, які наступають протягом 7 днів.

    :param db: Сесія бази даних.
    :param user: Поточний авторизований користувач.
    :return: Список контактів з майбутніми днями народження.
    """
    return await contacts.upcoming_birthdays(db, user)


@router.get(
    "/",
    name="List of contacts",
    status_code=200,
)
async def get_contacts(db=Depends(get_db), user=Depends(auth_service.get_current_user)):
    """
    Отримати список усіх контактів користувача.

    :param db: Сесія бази даних.
    :param user: Поточний авторизований користувач.
    :return: Список контактів користувача.
    """
    all_contacts = await contacts.get_contacts(db, user)
    return all_contacts


@router.get(
    "/{contact_id}",
    name="Get contact by id",
    response_model=schemas_contact.ContactResponse,
    status_code=200,
)
async def get_contact_by_id(
    contact_id: int,
    db=Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    """
    Отримати контакт за його ID.

    :param contact_id: ID контакту.
    :param db: Сесія бази даних.
    :param user: Поточний авторизований користувач.
    :return: Контакт з заданим ID.
    """
    return await contacts.get_contact_by_id(contact_id, db, user)


@router.delete(
    "/{contact_id}",
    name="Delete contact by id",
    status_code=200,
)
async def delete_contact(
    contact_id: int,
    db=Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    """
    Видалити контакт за його ID.

    :param contact_id: ID контакту.
    :param db: Сесія бази даних.
    :param user: Поточний авторизований користувач.
    :return: Результат видалення.
    """
    return await contacts.delete_contact(contact_id, db, user)


@router.patch(
    "/{contact_id}",
    name="Update contact",
    status_code=200,
)
async def update_contact(
    contact_id: int,
    body: schemas_contact.ContactUpdate,
    db=Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    """
    Оновити дані контакту.

    :param contact_id: ID контакту.
    :param body: Дані для оновлення.
    :param db: Сесія бази даних.
    :param user: Поточний авторизований користувач.
    :return: Оновлений контакт.
    """
    return await contacts.update_contact(contact_id, body, db, user)
