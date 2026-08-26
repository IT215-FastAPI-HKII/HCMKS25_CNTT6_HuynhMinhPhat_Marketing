
from fastapi import APIRouter, Depends, status
from app.models.user import User
from app.dependencies.auth import get_current_user
from app.dependencies.role import RoleChecker
from app.db.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/admin", summary="Thông tin ẩn [ADMIN]", status_code=status.HTTP_200_OK)
def get_admin(current_user: User = Depends(RoleChecker(["ADMIN"]))):
    return {
        "status": "success",
        "message": f"Chào mừng Admin {current_user.full_name}!",
        "secret_data": "Hello tôi là super admin đây :>!"
    }

@router.get("/me", summary="Thông tin người dùng hiện tại", status_code=status.HTTP_200_OK)
def read_current_user(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role if current_user.role else None,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at
    }

@router.get("", summary="Lấy danh sách người dùng [ADMIN]", status_code=status.HTTP_200_OK)
def list_users(db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["ADMIN"])), name: str | None = None, email: str | None = None, is_active: bool | None = None):
    search = db.query(User)
    if name:
        search = search.filter(User.full_name.ilike(f"%{name}%"))
    if email:
        search = search.filter(User.email.ilike(f"%{email}%"))
    if is_active is not None:
        search = search.filter(User.is_active == is_active)

    users = search.all()
    result = []
    for u in users:
        result.append({
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role if u.role else None,
            "is_active": u.is_active,
            "created_at": u.created_at
        })
    return result

