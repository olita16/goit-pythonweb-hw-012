from datetime import datetime, timedelta
from fastapi import Depends, HTTPException

from src.db.models import Contact, User
from src.services.auth import auth_service


async def create_contact(body, db, user: User = Depends(auth_service.get_current_user)):
    """
    Створює новий контакт для поточного користувача.

    :param body: Дані нового контакту.
    :type body: ContactModel (або Pydantic модель)
    :param db: Сесія бази даних.
    :type db: Session
    :param user: Поточний користувач (отримується через Depends).
    :type user: User
    :return: Створений контакт.
    :rtype: Contact
    """
    contact = Contact(**body.model_dump())
    contact.user_id = user.id
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def get_contacts(db, user: User = Depends(auth_service.get_current_user)):
    """
    Повертає всі контакти для поточного користувача.

    :param db: Сесія бази даних.
    :type db: Session
    :param user: Поточний користувач.
    :type user: User
    :return: Список контактів.
    :rtype: list[Contact]
    """
    return db.query(Contact).filter(Contact.user_id == user.id).all()


async def get_contact_by_id(contact_id, db, user: User = Depends(auth_service.get_current_user)):
    """
    Отримує контакт за ідентифікатором.

    :param contact_id: Ідентифікатор контакту.
    :type contact_id: int
    :param db: Сесія бази даних.
    :type db: Session
    :param user: Поточний користувач.
    :type user: User
    :raises HTTPException: Якщо контакт не знайдено.
    :return: Контакт.
    :rtype: Contact
    """
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == user.id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


async def delete_contact(contact_id, db, user: User = Depends(auth_service.get_current_user)):
    """
    Видаляє контакт за ідентифікатором.

    :param contact_id: Ідентифікатор контакту.
    :type contact_id: int
    :param db: Сесія бази даних.
    :type db: Session
    :param user: Поточний користувач.
    :type user: User
    :raises HTTPException: Якщо контакт не знайдено.
    :return: Видалений контакт.
    :rtype: Contact
    """
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == user.id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    db.delete(contact)
    db.commit()
    return contact


async def update_contact(contact_id: int, body, db, user: User = Depends(auth_service.get_current_user)):
    """
    Оновлює дані контакту за ідентифікатором.

    :param contact_id: Ідентифікатор контакту.
    :type contact_id: int
    :param body: Нові дані для оновлення.
    :type body: ContactUpdateModel (або Pydantic модель)
    :param db: Сесія бази даних.
    :type db: Session
    :param user: Поточний користувач.
    :type user: User
    :raises HTTPException: Якщо контакт не знайдено.
    :return: Оновлений контакт.
    :rtype: Contact
    """
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == user.id).first()
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
    Пошук контактів за іменем, прізвищем або email.

    :param first_name: Ім'я для пошуку.
    :type first_name: str | None
    :param last_name: Прізвище для пошуку.
    :type last_name: str | None
    :param email: Email для пошуку.
    :type email: str | None
    :param db: Сесія бази даних.
    :type db: Session
    :param user: Поточний користувач.
    :type user: User
    :raises HTTPException: Якщо не знайдено жодного контакту.
    :return: Список знайдених контактів.
    :rtype: list[Contact]
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
    Повертає контакти з днями народження протягом наступних 7 днів.

    :param db: Сесія бази даних.
    :type db: Session
    :param user: Поточний користувач.
    :type user: User
    :raises HTTPException: Якщо не знайдено жодного контакту з наближеним днем народження.
    :return: Список контактів з майбутніми днями народження.
    :rtype: list[Contact]
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
