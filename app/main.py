from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from app.db.database import engine, Base
from app.models.user import User
from app.models.campaign import Campaign, CampaignMember, CampaignTask
from app.core.exceptions import AppException, app_exception_handler, general_exception_handler
from app.routers.health import router as health_router
from app.routers.auth import router as auth_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Marketing Campaign Management API")

@app.get("/")
def root():
    return {"message": "Chào mừng đến với Marketing Campaign Management API!"}

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

app.include_router(health_router)
app.include_router(auth_router)