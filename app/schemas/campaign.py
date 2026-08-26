from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.user import UserResponse
from app.schemas.campaign_member import CampaignMemberResponse
from app.schemas.campaign_task import CampaignTaskResponse


class CampaignBase(BaseModel):
    name: str
    description: str | None = None


class CampaignCreate(CampaignBase):
    pass


class CampaignUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class CampaignResponse(CampaignBase):
    id: int
    owner_id: int
    created_at: datetime
    owner: UserResponse | None = None

    class Config:
        from_attributes = True

class AddMemberRequest(BaseModel):
    user_id: int = Field(..., gt=0)