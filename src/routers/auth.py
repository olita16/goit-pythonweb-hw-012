from fastapi import APIRouter, Depends, HTTPException, Request, status, BackgroundTasks
from sqlalchemy.orm import Session
from src.databases.connect import get_db
from src.schemas.auth import (
    User,
    UserModelRegister,
    UserModel,
    RequestResetPassword,
    ResetPassword,
)
from src.repository.auth import (
    Hash,
    create_access_token,
    create_email_token,
    get_email_from_token,
)
from src.repository.user import (
    create_user,
    get_user_by_email,
    change_confirmed_email,
    update_user_password,
)
from src.services.email import send_email, send_reset_password_email
from src.services.auth import auth_service
from src.services.limiter import limiter


router = APIRouter(prefix="/auth", tags=["auth"])

hash_handler = Hash()


@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=User)
async def signup(
    body: UserModelRegister,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Реєструє нового користувача.

    :param body: Дані для реєстрації користувача.
    :param background_tasks: Об'єкт для фонових задач.
    :param request: HTTP-запит.
    :param db: Сесія бази даних.
    :raises HTTPException: Якщо акаунт з таким email вже існує.
    :return: Зареєстрований користувач.
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
    Авторизує користувача.

    :param body: ПОшта та пароль.
    :param db: Сесія бази даних.
    :raises HTTPException: Якщо пошта або пароль некоректні, або пошта не підтверджено.
    :return: JWT токен доступу.
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

    access_token = await create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    Підтверджує пошту користувача за токеном.

    :param token: Токен верифікації.
    :param db: Сесія бази даних.
    :raises HTTPException: Якщо токен некоректний або користувача не знайдено.
    :return: Повідомлення про статус підтвердження.
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
    Обмеження кількості запитів маршрут /me
    :param request: HTTP-запит, використовується для відстеження IP/ідентифікатора користувача.
    :param user: Поточний автентифікований користувач.
    :return: Email, ID та статус підтвердження користувача.
    """
    return {"email": user.email, "id": user.id, "confirmed": user.confirmed}


@router.post("/request-reset-password")
async def request_reset_password(
    body: RequestResetPassword,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Надсилає лист для скидання пароля, якщо email існує.

    :param body: Email користувача.
    :param background_tasks: Об'єкт для фонових задач.
    :param request: HTTP-запит.
    :param db: Сесія бази даних.
    :return: Повідомлення або токен для скидання пароля.
    """
    user = await get_user_by_email(body.email, db)
    if user:
        background_tasks.add_task(
            send_reset_password_email, user.email, str(request.base_url)
        )
        token = create_email_token({"sub": user.email})
        return {"reset_token": token}
    return {"message": "If the email exists, a reset link was sent"}


@router.post("/reset-password/{token}")
async def reset_password(
    token: str,
    body: ResetPassword,
    db: Session = Depends(get_db),
):
    """
    Скидає пароль користувача за токеном.

    :param token: Токен для скидання пароля.
    :param body: Новий пароль.
    :param db: Сесія бази даних.
    :raises HTTPException: Якщо токен недійсний або користувача не знайдено.
    :return: Повідомлення про успішне скидання.
    """
    email = await get_email_from_token(token)
    user = await get_user_by_email(email, db)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid token or user not found")

    hashed_password = hash_handler.get_password_hash(body.password)
    await update_user_password(email, hashed_password, db)
    return {"message": "Password has been reset successfully"}
