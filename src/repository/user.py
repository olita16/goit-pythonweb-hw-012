from sqlalchemy.orm import Session
from src.databases.models import User
from src.schemas.auth import UserModel


async def get_user_by_email(email: str, db: Session):
    """
    Повертає користувача за email.

    :param email: Email користувача.
    :param db: Сесія бази даних.
    :return: Об'єкт користувача або None, якщо не знайдено.
    """
    user = db.query(User).filter_by(email=email).first()
    return user


async def create_user(body: UserModel, db: Session):
    """
    Створює нового користувача в базі даних.

    :param body: Дані нового користувача.
    :param db: Сесія бази даних.
    :return: Об'єкт створеного користувача.
    """
    user = User(**body.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


async def change_confirmed_email(email: str, db: Session) -> None:
    """
    Встановлюж email як підтверджений.

    :param email: Email користувача.
    :param db: Сесія бази даних.
    :return: None
    """

    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar_url(email: str, url: str, db: Session) -> User:
    """
    Оновлює URL аватарки користувача.

    :param email: Email користувача.
    :param url: Новий URL аватарки.
    :param db: Сесія бази даних.
    :return: Оновлений об'єкт користувача.
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    db.refresh(user)
    return user


async def update_user_password(email: str, hashed_password: str, db: Session):
    """
    Оновлює пароль користувача.

    :param email: Email користувача.
    :param hashed_password: Хешований новий пароль.
    :param db: Сесія бази даних.
    :return: Оновлений об'єкт користувача або None, якщо не знайдено.
    """
    user = await get_user_by_email(email, db)
    if not user:
        return None
    user.password = hashed_password
    db.commit()
    db.refresh(user)
    return user
