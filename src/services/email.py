from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.repository.auth import create_email_token
from src.settings.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS,
    TEMPLATE_FOLDER=Path(__file__).parent / "templates",
)
"""
Конфігурація для FastAPI-Mail, яка використовує налаштування з конфігураційного файлу.
Папка з HTML-шаблонами для листів знаходиться в "templates" поряд з цим файлом.
"""


async def send_email(email: EmailStr, username: str, host: str):
    """
    Відправляє лист підтвердження електронної пошти користувачу.

    Створює токен підтвердження і відправляє лист з посиланням на підтвердження.

    :param email: Email отримувача.
    :param username: Ім'я користувача для персоналізації листа.
    :param host: Базова URL-адреса сервера для формування посилання.
    """
    try:
        token_verification = create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email",
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "token": token_verification,
            },
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="verify_email.html")
    except ConnectionErrors as err:
        print(err)


async def send_reset_password_email(email: EmailStr, host: str):
    """
    Відправляє лист для скидання пароля.

    Генерує токен для скидання пароля та відправляє лист із відповідним посиланням.

    :param email: Email отримувача.
    :param host: Базова URL-адреса сервера для формування посилання.
    """
    try:
        token = create_email_token({"sub": email})
        message = MessageSchema(
            subject="Reset your password",
            recipients=[email],
            template_body={"host": host, "token": token},
            subtype=MessageType.html,
        )
        fm = FastMail(conf)
        await fm.send_message(message, template_name="reset_password.html")
    except ConnectionErrors as err:
        print(err)
