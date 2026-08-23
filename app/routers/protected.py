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

@router.get("/me")
def read_current_user(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role if current_user.role else None,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at
    }