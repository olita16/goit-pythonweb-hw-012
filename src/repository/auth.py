from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import UTC, datetime, timezone, timedelta

from src.settings.base import ALGORITHM, SECRET_KEY


class Hash:
    """
    Клас для хешування паролів та їх перевірки.
    """

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        """
        Перевіряє, чи відповідає plain_password хешу hashed_password.

        :param plain_password: Пароль у звичайному тексті.
        :param hashed_password: Хешований пароль для порівняння.
        :return: True, якщо паролі співпадають, інакше False.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Перевіряє, чи відповідає plain_password хешу hashed_password.

        :param plain_password: Пароль у звичайному тексті.
        :param hashed_password: Хешований пароль для порівняння.
        :return: True, якщо паролі співпадають, інакше False.
        """
        return self.pwd_context.hash(password)


async def create_access_token(data: dict, expires_delta=3600):
    """
    Перевіряє, чи відповідає plain_password хешу hashed_password.

    :param plain_password: Пароль у звичайному тексті.
    :param hashed_password: Хешований пароль для порівняння.
    :return: True, якщо паролі співпадають, інакше False.
    """

    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def create_email_token(data: dict):
    """
    Створює JWT токен для верифікації email з терміном дії 7 днів.

    :param data: Дані для кодування у токені.
    :return: Закодований JWT токен.
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=7)
    to_encode.update({"iat": datetime.now(UTC), "exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


async def get_email_from_token(token: str):
    """
    Декодує email з JWT токена.

    :param token: JWT токен.
    :return: Email, витягнутий з токена.
    :raises HTTPException: Якщо токен некоректний або прострочений.
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
