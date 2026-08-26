from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from app.db.database import engine, Base
from app.models.user import User
from app.models.campaign import Campaign, CampaignMember, CampaignTask
from app.core.exceptions import AppException, app_exception_handler, general_exception_handler, db_integrity_exception_handler
from app.routers.health import router as health_router
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.campaign import router as campaign_router
from app.routers.campaign_task import router as campaign_task_router
from sqlalchemy.exc import IntegrityError

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Marketing Campaign Management API")

@app.get("/", summary="Test Connect", status_code=status.HTTP_200_OK)
def root():
    return {"message": "Chào mừng đến với Marketing Campaign Management API!"}

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)
app.add_exception_handler(IntegrityError, db_integrity_exception_handler)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(campaign_router)
app.include_router(campaign_task_router)