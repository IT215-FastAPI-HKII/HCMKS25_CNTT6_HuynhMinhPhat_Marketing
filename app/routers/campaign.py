from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.dependencies.auth import get_current_user
from app.schemas.campaign import CampaignCreate, CampaignResponse, CampaignUpdate, CampaignMemberResponse, AddMemberRequest
from app.schemas.user import UserResponse
from app.services import campaign_service
from app.schemas.campaign_task import CampaignTaskCreate, CampaignTaskResponse
from typing import Optional

router = APIRouter(
    prefix="/campaigns",
    tags=["Campaigns"]
)

@router.post("", response_model=CampaignResponse)
def create_campaign(campaign_in: CampaignCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return campaign_service.create_campaign(db, current_user, campaign_in.name, campaign_in.description)

@router.get("", response_model=list[CampaignResponse])
def list_campaigns(db: Session = Depends(get_db), current_user: User = Depends(get_current_user), name: str | None = Query(None)):
    return campaign_service.list_campaigns(db, current_user, name)

@router.get("/{id}", response_model=CampaignResponse)
def get_campaign(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return campaign_service.get_campaign(db, id, current_user)

@router.put("/{id}", response_model=CampaignResponse)
def replace_campaign(id: int, campaign_in: CampaignCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return campaign_service.replace_campaign(db, id, current_user, campaign_in.name, campaign_in.description)

@router.patch("/{id}", response_model=CampaignResponse)
def update_campaign_partial(id: int, campaign_in: CampaignUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return campaign_service.update_campaign_partial(db, id, current_user, campaign_in.name, campaign_in.description)

@router.delete("/{id}")
def delete_campaign(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return campaign_service.delete_campaign(db, id, current_user)

@router.post("/{id}/members", response_model=UserResponse)
def add_member_to_campaign(id: int, payload: AddMemberRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return campaign_service.add_member(db, id, current_user, payload.user_id)

@router.delete("/{id}/members/{user_id}")
def remove_member_from_campaign(id: int, user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return campaign_service.remove_member(db, id, current_user, user_id)

@router.get("/{id}/members", response_model=list[CampaignMemberResponse])
def list_campaign_members(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return campaign_service.list_members(db, id, current_user)

@router.post("/{id}/campaign-tasks", response_model=CampaignTaskResponse)
def create_campaign_task(id: int, task_in: CampaignTaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return campaign_service.create_campaign_task(db, id, current_user, task_in.title, task_in.description, task_in.status, task_in.priority, task_in.due_date, task_in.assignee_id)

@router.get("/campaigns/{id}/campaign-tasks", response_model=list[CampaignTaskResponse])
def get_campaign_tasks(campaign_id: int, status: Optional[str] = Query(None), priority: Optional[str] = Query(None), assignee_id: Optional[int] = Query(None), title: Optional[str] = Query(None), limit: int = Query(10, ge=1), offset: int = Query(0, ge=0), sort_by: str = Query("created_at"), sort_order: str = Query("asc"), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return campaign_service.list_campaign_tasks(db=db, campaign_id=campaign_id, current_user=current_user, status=status, priority=priority, assignee_id=assignee_id, title=title, limit=limit, offset=offset, sort_by=sort_by, sort_order=sort_order)
