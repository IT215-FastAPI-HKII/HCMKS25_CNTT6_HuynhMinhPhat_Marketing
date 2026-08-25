from sqlalchemy.orm import Session
from app.models.campaign import Campaign, CampaignMember, CampaignTask
from app.models.user import User
from app.core.exceptions import NotFoundException, ForbiddenException, BadRequestException

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

def update_campaign_task(db: Session, task_id: int, current_user: User, task_in):
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

    if task_in.title is not None:
        if task_in.title.strip() == "":
            raise BadRequestException("Tiêu đề không được để trống")
        task.title = task_in.title.strip()

    if task_in.description is not None:
        task.description = task_in.description

    if task_in.status is not None:
        task.status = task_in.status

    if task_in.priority is not None:
        task.priority = task_in.priority

    if task_in.due_date is not None:
        task.due_date = task_in.due_date

    if task_in.assignee_id is not None:
        assignee_id = task_in.assignee_id

        if assignee_id > 0:
            assignee = (db.query(User).filter(User.id == assignee_id).first())
            if not assignee:
                raise NotFoundException("Assignee không tồn tại")

            is_assignee_owner = campaign.owner_id == assignee_id
            is_assignee_member = (db.query(CampaignMember).filter(CampaignMember.campaign_id == campaign.id, CampaignMember.user_id == assignee_id).first() is not None)

            if not (is_assignee_owner or is_assignee_member):
                raise BadRequestException("Người được giao công việc không thuộc chiến dịch này")

            task.assignee_id = assignee_id
        else:
            task.assignee_id = None

    db.commit()
    db.refresh(task)
    return task

def delete_campaign_task(db: Session, task_id: int, current_user: User):
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

    if campaign.owner_id != current_user.id:
        raise ForbiddenException("Chỉ OWNER mới có quyền xóa đầu việc")

    db.delete(task)
    db.commit()

    return {
        "status": "success",
        "message": f"Đầu việc '{task.title}' đã được xóa thành công"
    }