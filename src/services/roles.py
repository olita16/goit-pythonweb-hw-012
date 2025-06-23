from typing import List
from fastapi import Depends, HTTPException, status, Request

from src.databases.models import User, Role
from src.services.auth import auth_service


class RoleAccess:
    """
    Клас для перевірки прав доступу користувача за ролями.
    """

    def __init__(self, allowed_roles: List[Role]):
        """
        Ініціалізує RoleAccess зі списком дозволених ролей.

        :param allowed_roles: Список ролей, яким дозволено доступ.
        """
        self.allowed_roles = allowed_roles

    async def __call__(
        self,
        request: Request,
        current_user: User = Depends(auth_service.get_current_user),
    ):
        """
        Перевіряє, чи має поточний користувач дозвіл виконувати дію.

        :param request: HTTP-запит.
        :param current_user: Поточний автентифікований користувач.
        :raises HTTPException: Якщо роль користувача не дозволена.
        :return: None
        """
        if current_user.roles not in self.allowed_roles:
            print("Allowed_roles", self.allowed_roles)
            print(" User roles", current_user.roles)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation forbidden, you don't have access",
            )
