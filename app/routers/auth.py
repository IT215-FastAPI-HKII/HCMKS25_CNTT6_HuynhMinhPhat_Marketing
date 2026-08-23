from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserResponse, TokenResponse, UserLogin
from app.services.auth_service import register_user, login_user
from app.db.database import get_db

router = APIRouter(
    prefix="/auth", 
    tags=["Auth"]
)

@router.post("/register", response_model=UserResponse)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    return register_user(db, payload)

@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    return login_user(db, payload)
