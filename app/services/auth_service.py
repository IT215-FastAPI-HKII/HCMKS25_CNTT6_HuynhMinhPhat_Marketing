from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, TokenResponse, UserLogin
from app.core.exceptions import BadRequestException
from app.core.security import hash_password, verify_password, create_access_token

def register_user(db: Session, payload: UserCreate) -> UserResponse:
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise BadRequestException("Email đã tồn tại")

    hashed_pw = hash_password(payload.password)

    new_user = User(
        email=payload.email,
        password_hash=hashed_pw,
        full_name=payload.full_name,
        role=payload.role,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserResponse.model_validate(new_user)

def login_user(db: Session, payload: UserLogin) -> TokenResponse:
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise BadRequestException("Email không tồn tại hoặc không đúng")

    if not verify_password(payload.password, user.password_hash):
        raise BadRequestException("Sai mật khẩu")
    
    token_data = {
        "sub": str(user.email),
        "email": user.email,
        "role": user.role
    }
    access_token = create_access_token(token_data)

    return TokenResponse(access_token= access_token, token_type= "bearer")