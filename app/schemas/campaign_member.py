from datetime import datetime
from pydantic import BaseModel
from app.schemas.user import UserResponse


class CampaignMemberBase(BaseModel):
    role: str = "MEMBER"


class CampaignMemberCreate(CampaignMemberBase):
    user_id: int


class CampaignMemberUpdate(BaseModel):
    role: str | None = None


class CampaignMemberResponse(CampaignMemberBase):
    campaign_id: int
    user_id: int
    joined_at: datetime
    user: UserResponse | None = None

    class Config:
        from_attributes = True