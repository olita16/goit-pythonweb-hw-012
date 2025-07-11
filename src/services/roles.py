from typing import List
from fastapi import Depends, HTTPException, status, Request

from src.db.models import User, Role
from src.services.auth import auth_service


class RoleAccess:
    """
    Депенденсі для перевірки доступу користувача за роллю.

    Перевіряє, чи має поточний користувач одну з дозволених ролей.
    Викликається як FastAPI dependency.

    Args:
        allowed_roles (List[Role]): Список ролей, які мають доступ.
    """

    def __init__(self, allowed_roles: List[Role]):
        self.allowed_roles = allowed_roles

    async def __call__(
        self,
        request: Request,
        current_user: User = Depends(auth_service.get_current_user),
    ):
        """
        Перевіряє роль користувача і кидає HTTP 403, якщо доступ заборонений.

        Args:
            request (Request): Об’єкт запиту FastAPI.
            current_user (User): Поточний користувач, отриманий через депенденсі.

        Raises:
            HTTPException: Якщо роль користувача не в allowed_roles, викликається 403 Forbidden.
        """
        if current_user.roles not in self.allowed_roles:
            print("Allowed_roles:", self.allowed_roles)
            print("User roles:", current_user.roles)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation forbidden, you don't have access",
            )
