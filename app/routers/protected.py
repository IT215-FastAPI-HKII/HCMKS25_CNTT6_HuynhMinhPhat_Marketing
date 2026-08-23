# app/routers/protected_routes.py
from fastapi import APIRouter, Depends
from app.models.user import User
from app.dependencies.auth import get_current_user
from app.dependencies.role import RoleChecker

router = APIRouter(
    prefix="/protected",
    tags=["Protected Routes"]
)

@router.get("/admin")
def get_admin(current_user: User = Depends(RoleChecker(["ADMIN"]))):
    return {
        "status": "success",
        "message": f"Chào mừng Admin {current_user.full_name}!",
        "secret_data": "Hello tôi là super admin đây :>!"
    }
