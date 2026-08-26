from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.dependencies.auth import get_current_user
from app.schemas.campaign_task import CampaignTaskResponse, CampaignTaskUpdate
from app.services import campaign_task_service

router = APIRouter(prefix="/campaign-tasks", tags=["Campaign Tasks"])

@router.get("/{id}", response_model=CampaignTaskResponse)
def get_campaign_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return campaign_task_service.get_campaign_task(db, task_id, current_user)

@router.patch("/{id}", response_model=CampaignTaskResponse)
def update_campaign_task(task_id: int, task_in: CampaignTaskUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return campaign_task_service.update_campaign_task(db, task_id, current_user, task_in)

@router.delete("/{id}")
def delete_campaign_task(campaign_id: int, task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task_title = campaign_task_service.delete_campaign_task(db, campaign_id, task_id, current_user)
    return {
        "success": True,
        "message": f"Nhiệm vụ '{task_title}' đã được xóa thành công",
        "data": None,
        "error": None,
    }