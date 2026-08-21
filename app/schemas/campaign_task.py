from datetime import datetime
from pydantic import BaseModel
from app.schemas.user import UserResponse


class CampaignTaskBase(BaseModel):
    title: str
    description: str | None = None
    status: str = "TODO"
    priority: str = "MEDIUM"
    due_date: datetime | None = None


class CampaignTaskCreate(CampaignTaskBase):
    assignee_id: int | None = None


class CampaignTaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    priority: str | None = None
    due_date: datetime | None = None
    assignee_id: int | None = None


class CampaignTaskResponse(CampaignTaskBase):
    id: int
    campaign_id: int
    assignee_id: int | None = None
    created_at: datetime
    assignee: UserResponse | None = None

    class Config:
        from_attributes = True