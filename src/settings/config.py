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

#     model_config = SettingsConfigDict(
#         extra="ignore",
#         env_file=".env",
#         env_file_encoding="utf-8",
#         case_sensitive=True,
#     )


# settings = Settings()



from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_PORT: int
    POSTGRES_HOST: str

    DB_URL: str | None = None  # optional, згенеруємо через валідатор

    @validator("DB_URL", pre=True, always=True)
    def assemble_db_url(cls, v, values):
        if v is not None:
            return v
        return (
            f"postgresql+asyncpg://{values['POSTGRES_USER']}:"
            f"{values['POSTGRES_PASSWORD']}@{values['POSTGRES_HOST']}:"
            f"{values['POSTGRES_PORT']}/{values['POSTGRES_DB']}"
        )

    # інші поля

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

    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()
