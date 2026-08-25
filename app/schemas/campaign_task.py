from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from app.schemas.user import UserResponse

class TaskStatus(str, Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


class TaskPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class CampaignTaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: datetime | None = None


class CampaignTaskCreate(CampaignTaskBase):
    assignee_id: int | None = None


class CampaignTaskUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
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