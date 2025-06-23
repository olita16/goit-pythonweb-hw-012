import pickle
import redis


from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from src.repository.user import get_user_by_email
from src.databases.connect import get_db
from src.databases.models import User as UserORM
from src.settings.base import ALGORITHM, SECRET_KEY


class Auth:
    """
    Клас для автентифікації користувачів через JWT та кешування з Redis.
    """

    r = redis.Redis(host="redis", port=6379, db=0)

    async def get_current_user(
        self,
        token: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
        db: Session = Depends(get_db),
    ):
        """
        Отримує поточного користувача за JWT токеном. Перевіряє токен, витягує email,
        шукає користувача в Redis або базі даних. Кешує користувача на 15 хвилин.

        :param token: JWT токен авторизації.
        :param db: Сесія бази даних.
        :raises HTTPException: Якщо токен недійсний або користувача не знайдено.
        :return: Об'єкт користувача (UserORM).
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
            print("Payload from token:", payload)
            email = payload["sub"]
            if email is None:
                print("No sub in token")
                raise credentials_exception
        except JWTError as e:
            print("JWT error:", e)
            raise credentials_exception

        # user: User = db.query(User).filter(User.email == email).first()
        cache_key = f"user:{email}"
        cached_user = self.r.get(cache_key)

        if cached_user:
            user: UserORM = pickle.loads(cached_user)

            fresh_user = await get_user_by_email(email, db)
            if not fresh_user:
                raise credentials_exception

            if fresh_user.roles != user.roles:
                user = fresh_user
                self.r.set(cache_key, pickle.dumps(user))
                self.r.expire(cache_key, 900)
        else:
            user = await get_user_by_email(email, db)
            if not user:
                raise credentials_exception
            self.r.set(cache_key, pickle.dumps(user))
            self.r.expire(cache_key, 900)

        return user


auth_service = Auth()
