# app/founder/dependencies/role.py
from fastapi import Depends
from app.models.user import User
from app.dependencies.auth import get_current_user
from app.core.exceptions import ForbiddenException

class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)):
        user_role_name = current_user.role if current_user.role else None

        if user_role_name not in self.allowed_roles:
            raise ForbiddenException(f"Quyền truy cập bị từ chối! Yêu cầu một trong các quyền: {self.allowed_roles}")
        return current_user
