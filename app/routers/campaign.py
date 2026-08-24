from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.db.database import get_db
from app.models.user import User
from app.models.campaign import Campaign
from app.dependencies.auth import get_current_user
from app.schemas.campaign import CampaignCreate, CampaignResponse

router = APIRouter(
    prefix="/campaigns",
    tags=["Campaigns"]
)

@router.post("", response_model=CampaignResponse)
def create_campaign(
    campaign_in: CampaignCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
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
