from sqlalchemy.orm import Session
from src.db.models import User
from src.schemas.auth import UserModel


async def get_user_by_email(email: str, db: Session):
    """
    Повертає користувача за email.

    :param email: Email користувача.
    :type email: str
    :param db: Сесія бази даних.
    :type db: Session
    :return: Об'єкт користувача або None, якщо не знайдено.
    :rtype: User | None
    """
    user = db.query(User).filter_by(email=email).first()
    return user


async def create_user(body: UserModel, db: Session):
    """
    Створює нового користувача у базі даних.

    :param body: Дані користувача.
    :type body: UserModel
    :param db: Сесія бази даних.
    :type db: Session
    :return: Створений користувач.
    :rtype: User
    """
    user = User(**body.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


async def change_confirmed_email(email: str, db: Session) -> None:
    """
    Позначає email як підтверджений.

    :param email: Email користувача.
    :type email: str
    :param db: Сесія бази даних.
    :type db: Session
    :return: None
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar_url(email: str, url: str, db: Session) -> User:
    """
    Оновлює URL аватара користувача.

    :param email: Email користувача.
    :type email: str
    :param url: Новий URL аватара.
    :type url: str
    :param db: Сесія бази даних.
    :type db: Session
    :return: Оновлений користувач.
    :rtype: User
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    db.refresh(user)
    return user


async def update_user_password(email: str, hashed_password: str, db: Session):
    """
    Оновлює пароль користувача на новий хеш.

    :param email: Email користувача.
    :type email: str
    :param hashed_password: Хешований пароль.
    :type hashed_password: str
    :param db: Сесія бази даних.
    :type db: Session
    :return: Оновлений користувач або None, якщо не знайдено.
    :rtype: User | None
    """
    user = await get_user_by_email(email, db)
    if not user:
        return None
    user.password = hashed_password
    db.commit()
    db.refresh(user)
    return user
