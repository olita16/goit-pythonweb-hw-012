from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session
from src.repository.user import update_avatar_url
from src.services.upload_file import UploadFileService
from src.schemas.auth import User
from src.databases.models import Role, User as UserORM
from src.databases.connect import get_db

from src.services.auth import auth_service
from src.settings.config import settings
from src.services.roles import RoleAccess


router = APIRouter(prefix="/user", tags=["users"])

allowed_operation_update_avatar = RoleAccess([Role.admin])


@router.patch(
    "/avatar",
    response_model=User,
    dependencies=[Depends(allowed_operation_update_avatar)],
)
async def update_avatar_user(
    file: UploadFile = File(),
    user: UserORM = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Оновлює аватар користувача (доступно лише для адміністраторів).

    :param file: Завантажуваний файл зображення.
    :param user: Поточний автентифікований користувач.
    :param db: Сесія бази даних.
    :return: Користувач з оновленим URL аватарки.
    """
    avatar_url = UploadFileService(
        settings.CLOUDINARY_NAME,
        settings.CLOUDINARY_API_KEY,
        settings.CLOUDINARY_API_SECRET,
    ).upload_file(file, user.email)

    await update_avatar_url(user.email, avatar_url, db)
    user.avatar = avatar_url
    return user
