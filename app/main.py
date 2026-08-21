from fastapi import FastAPI
from app.db.database import engine, Base
from app.models.user import User
from app.models.campaign import Campaign, CampaignMember, CampaignTask

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Marketing Campaign Management API")

@app.get("/")
def root():
    return {"message": "Chào mừng đến với Marketing Campaign Management API!"}