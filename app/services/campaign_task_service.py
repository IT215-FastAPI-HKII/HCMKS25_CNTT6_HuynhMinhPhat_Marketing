from sqlalchemy.orm import Session
from app.models.campaign import Campaign, CampaignMember, CampaignTask
from app.models.user import User
from app.core.exceptions import NotFoundException, ForbiddenException

def get_campaign_task(db: Session, task_id: int, current_user: User):
    task = db.query(CampaignTask).filter(CampaignTask.id == task_id).first()
    if not task:
        raise NotFoundException("Đầu việc không tồn tại")

    campaign = db.query(Campaign).filter(Campaign.id == task.campaign_id).first()
    if not campaign:
        raise NotFoundException("Chiến dịch không tồn tại")

    is_owner = campaign.owner_id == current_user.id
    is_member = db.query(CampaignMember).filter(CampaignMember.campaign_id == campaign.id, CampaignMember.user_id == current_user.id).first() is not None

    if not (is_owner or is_member):
        raise ForbiddenException("Bạn không phải thành viên của chiến dịch này")
    
    return task
