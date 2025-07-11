from fastapi import APIRouter, Depends, HTTPException, Request, status, BackgroundTasks
from sqlalchemy.orm import Session
from src.db.connect import get_db
from src.schemas.auth import User, UserModelRegister, UserModel
from src.repository.auth import (
    Hash,
    create_access_token,
    get_email_from_token,
    create_email_token
)
from src.repository.user import create_user, get_user_by_email, change_confirmed_email, update_user_password
from src.services.email import send_email, send_reset_password_email
from src.services.auth import auth_service
from src.services.limiter import limiter

from src.schemas.auth import RequestResetPassword, ResetPassword, ResetPasswordWithToken
from jose import JWTError


router = APIRouter(prefix="/auth", tags=["auth"])

hash_handler = Hash()


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(
    body: UserModelRegister,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Реєструє нового користувача.

    :param body: Дані для реєстрації користувача.
    :type body: UserModelRegister
    :param background_tasks: Фонові задачі для відправки email.
    :type background_tasks: BackgroundTasks
    :param request: HTTP-запит.
    :type request: Request
    :param db: Сесія бази даних.
    :type db: Session
    :raises HTTPException: Якщо акаунт з таким email вже існує (409 Conflict).
    :return: Створений користувач.
    :rtype: User
    """
    user = await get_user_by_email(body.email, db)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Account already exists"
        )
    body.password = hash_handler.get_password_hash(body.password)
    new_user = await create_user(body, db)
    background_tasks.add_task(
        send_email, new_user.email, new_user.first_name, str(request.base_url)
    )
    return new_user


@router.post("/login", status_code=status.HTTP_201_CREATED)
async def login(body: UserModel, db: Session = Depends(get_db)):
    """
    Авторизує користувача та видає JWT токен.

    :param body: Дані для авторизації (email та пароль).
    :type body: UserModel
    :param db: Сесія бази даних.
    :type db: Session
    :raises HTTPException: Якщо email або пароль невірні (401 Unauthorized).
    :raises HTTPException: Якщо email не підтверджений.
    :return: JWT токен доступу та тип токена.
    :rtype: dict
    """
    user = await get_user_by_email(body.email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email"
        )

    if not hash_handler.verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
        )

    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed"
        )

    access_token = await create_access_token(data={"sub": user.email, "roles": user.roles.value})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    Підтверджує email користувача за токеном.

    :param token: Токен підтвердження email.
    :type token: str
    :param db: Сесія бази даних.
    :type db: Session
    :raises HTTPException: Якщо користувач не знайдений або токен невалідний (400 Bad Request).
    :return: Повідомлення про статус підтвердження.
    :rtype: dict
    """
    email = await get_email_from_token(token)

    user = await get_user_by_email(email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await change_confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.get("/me")
@limiter.limit("5/minute")
async def get_current_user_info(
    request: Request, user: User = Depends(auth_service.get_current_user)
):
    """
    Повертає інформацію про поточного авторизованого користувача.

    :param request: HTTP-запит.
    :type request: Request
    :param user: Поточний авторизований користувач.
    :type user: User
    :return: Email, ID та статус підтвердження користувача.
    :rtype: dict
    """
    return {"email": user.email, "id": user.id, "confirmed": user.confirmed}


@router.post("/request-reset-password", status_code=status.HTTP_200_OK)
async def request_reset_password(
    body: RequestResetPassword,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Запит на відновлення пароля. Якщо email існує, відправляє лист із посиланням на зміну пароля.

    :param body: Дані для запиту скидання пароля (email).
    :type body: RequestResetPassword
    :param background_tasks: Фонові задачі для відправки email.
    :type background_tasks: BackgroundTasks
    :param request: HTTP-запит.
    :type request: Request
    :param db: Сесія бази даних.
    :type db: Session
    :return: Повідомлення про те, що посилання на скидання пароля надіслано (якщо email існує).
    :rtype: dict
    """
    user = await get_user_by_email(body.email, db)
    if user:
        token = create_email_token({"sub": user.email})
        reset_link = f"{request.base_url}auth/reset-password?token={token}"
        background_tasks.add_task(
            send_reset_password_email, user.email, reset_link
        )

    return {"message": "If the email exists, a reset link was sent"}


@router.post("/reset-password/{token}")
async def reset_password(
    token: str,
    body: ResetPassword,
    db: Session = Depends(get_db),
):
    """
    Скидає пароль користувача за допомогою токена.

    :param token: Токен для скидання пароля.
    :type token: str
    :param body: Новий пароль.
    :type body: ResetPassword
    :param db: Сесія бази даних.
    :type db: Session
    :raises HTTPException: Якщо токен невалідний або користувач не знайдений (400 Bad Request).
    :return: Повідомлення про успішне скидання пароля.
    :rtype: dict
    """
    try:
        email = await get_email_from_token(token)
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = await get_user_by_email(email, db)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    hashed_password = hash_handler.get_password_hash(body.password)
    await update_user_password(email, hashed_password, db)

    return {"message": "Password has been reset successfully"}
