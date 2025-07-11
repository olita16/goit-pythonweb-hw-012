# from pydantic import EmailStr
# from pydantic_settings import BaseSettings, SettingsConfigDict


# class Settings(BaseSettings):
#     MAIL_USERNAME: str
#     MAIL_PASSWORD: str
#     MAIL_FROM: EmailStr
#     MAIL_PORT: int
#     MAIL_SERVER: str
#     MAIL_FROM_NAME: str
#     MAIL_STARTTLS: bool
#     MAIL_SSL_TLS: bool
#     USE_CREDENTIALS: bool
#     VALIDATE_CERTS: bool

#     CLOUDINARY_NAME: str
#     CLOUDINARY_API_KEY: str
#     CLOUDINARY_API_SECRET: str

#     SECRET_KEY: str
#     ALGORITHM: str
#     DB_URL: str


#     model_config = SettingsConfigDict(
#         extra="ignore",
#         env_file=".env",
#         env_file_encoding="utf-8",
#         case_sensitive=True,
#     )


# settings = Settings()

import os
from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: EmailStr
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool
    MAIL_SSL_TLS: bool
    USE_CREDENTIALS: bool
    VALIDATE_CERTS: bool

    CLOUDINARY_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str

    SECRET_KEY: str
    ALGORITHM: str
    DB_URL: str

    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=os.getenv("ENV_FILE", ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

settings = Settings()
