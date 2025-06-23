from datetime import datetime, timedelta
from fastapi import Depends, HTTPException

from src.databases.models import Contact, User
from src.services.auth import auth_service


async def create_contact(body, db, user: User = Depends(auth_service.get_current_user)):
    """
    Створює новий контакт для користувача.

    :param body: Дані нового контакту.
    :param db: Сесія бази даних.
    :param user: Поточний автентифікований користувач.
    :return: Об'єкт створеного контакту.
    """
    contact = Contact(**body.model_dump())
    contact.user_id = user.id
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def get_contacts(db, user: User = Depends(auth_service.get_current_user)):
    """
    Повертає всі контакти користувача.

    :param db: Сесія бази даних.
    :param user: Поточний автентифікований користувач.
    :return: Список контактів користувача.
    """
    return db.query(Contact).filter(Contact.user_id == user.id).all()


async def get_contact_by_id(
    contact_id, db, user: User = Depends(auth_service.get_current_user)
):
    """
    Повертає контакт за id користувача.

    :param contact_id: Ідентифікатор контакту.
    :param db: Сесія бази даних.
    :param user: Поточний автентифікований користувач.
    :raises HTTPException: Якщо контакт не знайдено (404).
    :return: Об'єкт контакту.
    """
    contact = (
        db.query(Contact)
        .filter(Contact.id == contact_id, Contact.user_id == user.id)
        .first()
    )
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


async def delete_contact(
    contact_id, db, user: User = Depends(auth_service.get_current_user)
):
    """
    Видаляє контакт за id користувача.

    :param contact_id: Ідентифікатор контакту.
    :param db: Сесія бази даних.
    :param user: Поточний автентифікований користувач.
    :raises HTTPException: Якщо контакт не знайдено (404).
    :return: Об'єкт видаленого контакту.
    """
    contact = (
        db.query(Contact)
        .filter(Contact.id == contact_id, Contact.user_id == user.id)
        .first()
    )
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    db.delete(contact)
    db.commit()
    return contact


async def update_contact(
    contact_id: int, body, db, user: User = Depends(auth_service.get_current_user)
):
    """
    Оновлює контакт за id користувача.

    :param contact_id: Ідентифікатор контакту.
    :param body: Дані для оновлення контакту.
    :param db: Сесія бази даних.
    :param user: Поточний автентифікований користувач.
    :raises HTTPException: Якщо контакт не знайдено (404).
    :return: Оновлений об'єкт контакту.
    """
    contact = (
        db.query(Contact)
        .filter(Contact.id == contact_id, Contact.user_id == user.id)
        .first()
    )
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(contact, key, value)

    db.commit()
    db.refresh(contact)
    return contact


async def search_contacts(
    first_name: str | None,
    last_name: str | None,
    email: str | None,
    db,
    user: User = Depends(auth_service.get_current_user),
):
    """
    Шукає контакти користувача за ім'ям, прізвищем або email.

    :param first_name: Ім'я для пошуку (необов'язково).
    :param last_name: Прізвище для пошуку (необов'язково).
    :param email: Email для пошуку (необов'язково).
    :param db: Сесія бази даних.
    :param user: Поточний автентифікований користувач.
    :raises HTTPException: Якщо контакти не знайдені (404).
    :return: Список знайдених контактів.
    """
    query = db.query(Contact).filter(Contact.user_id == user.id)

    if first_name:
        query = query.filter(Contact.first_name.ilike(f"%{first_name}%"))
    if last_name:
        query = query.filter(Contact.last_name.ilike(f"%{last_name}%"))
    if email:
        query = query.filter(Contact.email.ilike(f"%{email}%"))

    results = query.all()

    if not results:
        raise HTTPException(status_code=404, detail="Contact not found")
    return results


async def upcoming_birthdays(db, user: User = Depends(auth_service.get_current_user)):
    """
    Повертає контакти користувача з днями народження найближчого тижня.

    :param db: Сесія бази даних.
    :param user: Поточний автентифікований користувач.
    :raises HTTPException: Якщо дні народження не знайдені (404).
    :return: Список контактів з майбутніми днями народження.
    """
    today = datetime.today().date()
    next_week = today + timedelta(days=7)

    contacts_all = db.query(Contact).filter(Contact.user_id == user.id).all()
    upcoming = []

    for contact in contacts_all:
        if contact.birthday:
            birthday_this_year = contact.birthday.replace(year=today.year)

            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)

            if today <= birthday_this_year <= next_week:
                upcoming.append(contact)

    if not upcoming:
        raise HTTPException(status_code=404, detail="No upcoming birthdays found")

    return upcoming
