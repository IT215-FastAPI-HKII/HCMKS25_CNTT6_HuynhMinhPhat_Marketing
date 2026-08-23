# app/core/deps.py
from fastapi import Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.core.config import settings
from app.core.exceptions import BadRequestException, NotFoundException, ForbiddenException

# Sử dụng HTTPBearer để lấy token từ header
reusable_oauth2 = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(reusable_oauth2), db: Session = Depends(get_db)) -> User:
    token = credentials.credentials

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise BadRequestException("Token không hợp lệ")
        
    except jwt.ExpiredSignatureError:
        raise ForbiddenException("Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại!")
    
    except jwt.PyJWTError:
        raise BadRequestException("Không thể xác thực thông tin đăng nhập!")

    user = db.query(User).filter(User.email == email).first()

    if user is None:
        raise NotFoundException("Người dùng không tồn tại trên hệ thống!")

    if not user.is_active:
        raise BadRequestException("Tài khoản này đã bị tạm khóa!")

    return user
