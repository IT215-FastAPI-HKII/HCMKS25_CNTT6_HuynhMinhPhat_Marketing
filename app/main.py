from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from app.db.database import engine, Base
from models.user import User
from models.campaign import Campaign, CampaignMember, CampaignTask

from app.core.exceptions import AppException
from app.routers.health import router as health_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Marketing Campaign Management API")

@app.get("/")
def root():
    return {"message": "Chào mừng đến với Marketing Campaign Management API!"}

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.message,
            "data": None,
            "error": exc.message,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "Internal server error",
            "data": None,
            "error": str(exc),
        },
    )

app.include_router(health_router)