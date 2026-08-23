from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.core.exceptions import BadRequestException
from app.core.security import hash_password

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
