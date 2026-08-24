from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.db.database import get_db
from app.models.user import User
from app.models.campaign import Campaign, CampaignMember
from app.dependencies.auth import get_current_user
from app.schemas.campaign import CampaignCreate, CampaignResponse
from app.core.exceptions import (BadRequestException, ForbiddenException, NotFoundException)

router = APIRouter(
    prefix="/campaigns",
    tags=["Campaigns"]
)

@router.post("", response_model=CampaignResponse)
def create_campaign(campaign_in: CampaignCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_campaign = Campaign(
        name=campaign_in.name,
        description=campaign_in.description,
        owner_id=current_user.id,
        created_at=datetime.now(timezone.utc)
    )
    db.add(new_campaign)
    db.commit()
    db.refresh(new_campaign)

    new_campaign.owner = current_user

    return new_campaign

@router.get("", response_model=list[CampaignResponse])
def list_campaigns(db: Session = Depends(get_db), current_user: User = Depends(get_current_user), name: str | None = Query(None)):
    query = db.query(Campaign).filter(Campaign.owner_id == current_user.id)
    member_campaigns = (db.query(Campaign).join(CampaignMember).filter(CampaignMember.user_id == current_user.id))

    campaigns = query.union(member_campaigns)

    if name:
        campaigns = campaigns.filter(Campaign.name.ilike(f"%{name}%"))

    result = campaigns.all() 
    return result