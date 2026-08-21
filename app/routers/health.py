from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.database import get_db
from app.core.exceptions import InternalServerErrorException

router = APIRouter(
    prefix="/health",
    tags=["Health Check"]
)


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {
            "success": True,
            "message": "Hệ thống và Database đang hoạt động bình thường",
            "data": {
                "status": "healthy",
                "database": "connected"
            },
            "error": None
        }
    except Exception as e:
        raise InternalServerErrorException(f"Lỗi kết nối Database: {str(e)}")