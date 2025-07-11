import pickle
import redis

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from src.repository.user import get_user_by_email
from src.db.connect import get_db
from src.db.models import Role

from src.settings.base import ALGORITHM, SECRET_KEY


class Auth:
    """
    Сервіс аутентифікації користувачів.

    Підтримує валідацію JWT токенів та кешування користувачів у Redis.
    """

    r = redis.Redis(host="redis", port=6379, db=0)

    async def get_current_user(
        self,
        token: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
        db: Session = Depends(get_db),
    ):
        """
        Отримує поточного користувача на основі JWT токена.

        Перевіряє валідність токена, декодує його, отримує email та роль користувача.
        Якщо користувач є в кеші Redis — використовує його, інакше отримує з БД і кешує.

        :param token: HTTP авторизаційні дані (Bearer токен).
        :param db: Сесія бази даних.
        :return: Об'єкт користувача.
        :raises HTTPException: Якщо токен невалідний або користувач не знайдений.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
            print("Payload from token:", payload)
            email = payload.get("sub")
            role_str = payload.get("roles")
            if email is None or role_str is None:
                print("Missing sub or roles in token")
                raise credentials_exception
        except JWTError as e:
            print("JWT error:", e)
            raise credentials_exception

        cached_user = self.r.get(f"user:{email}")

        if cached_user is None:
            user = await get_user_by_email(email, db)
            if user is None:
                raise credentials_exception
            self.r.set(f"user:{email}", pickle.dumps(user))
            self.r.expire(f"user:{email}", 900)
        else:
            user = pickle.loads(cached_user)

        try:
            user.roles = Role(role_str)
        except ValueError:
            raise credentials_exception

        return user


auth_service = Auth()
