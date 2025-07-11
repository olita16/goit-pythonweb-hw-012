from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session
from src.repository.user import update_avatar_url
from src.services.upload_file import UploadFileService
from src.schemas.auth import User
from src.db.models import User as UserORM
from src.db.connect import get_db
from src.db.models import Role
from src.services.roles import RoleAccess
from src.services.auth import auth_service
from src.settings.config import settings


router = APIRouter(prefix="/user", tags=["users"])


@router.patch(
    "/avatar",
    response_model=User,
    dependencies=[Depends(RoleAccess([Role.admin]))]
)
async def update_avatar_user(
    file: UploadFile = File(),
    user: UserORM = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Оновлює аватар користувача.

    Цей ендпоінт дозволяє користувачам з роллю admin завантажити новий аватар.
    Файл завантажується через UploadFile, після чого відбувається завантаження у хмарне сховище
    (Cloudinary) та оновлення URL аватара у базі даних.

    :param file: Файл аватара, що завантажується.
    :param user: Поточний авторизований користувач (повинен мати роль admin).
    :param db: Сесія бази даних.
    :return: Оновлена інформація про користувача, включно з новим URL аватара.
    :rtype: User
    """
    avatar_url = UploadFileService(
        settings.CLOUDINARY_NAME,
        settings.CLOUDINARY_API_KEY,
        settings.CLOUDINARY_API_SECRET,
    ).upload_file(file, user.email)

    await update_avatar_url(user.email, avatar_url, db)
    user.avatar = avatar_url
    return user
