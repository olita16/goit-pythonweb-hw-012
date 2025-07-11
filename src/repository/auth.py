from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import UTC, datetime, timezone, timedelta

from src.settings.base import ALGORITHM, SECRET_KEY


class Hash:
    """
    Клас для хешування та перевірки паролів.
    """

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        """
        Перевіряє відповідність хешованого пароля оригіналу.

        :param plain_password: Незахешований пароль.
        :type plain_password: str
        :param hashed_password: Хешований пароль.
        :type hashed_password: str
        :return: True, якщо паролі збігаються, інакше False.
        :rtype: bool
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Генерує хеш з переданого пароля.

        :param password: Пароль, який потрібно захешувати.
        :type password: str
        :return: Хешований пароль.
        :rtype: str
        """
        return self.pwd_context.hash(password)


async def create_access_token(data: dict, expires_delta=3600):
    """
    Створює JWT токен доступу.

    :param data: Дані, які потрібно закодувати в токен.
    :type data: dict
    :param expires_delta: Тривалість життя токена у секундах. За замовчуванням — 3600 секунд (1 година).
    :type expires_delta: int
    :return: Згенерований токен.
    :rtype: str
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def create_email_token(data: dict):
    """
    Створює JWT токен для підтвердження електронної пошти.

    :param data: Дані, які потрібно закодувати в токен.
    :type data: dict
    :return: Згенерований email-токен.
    :rtype: str
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=7)
    to_encode.update({"iat": datetime.now(UTC), "exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


async def get_email_from_token(token: str):
    """
    Отримує email з JWT токена.

    :param token: JWT токен.
    :type token: str
    :raises HTTPException: Якщо токен недійсний або не може бути розкодуваний.
    :return: Email, отриманий з токена.
    :rtype: str
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload["sub"]
        return email
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid token for email verification",
        )
