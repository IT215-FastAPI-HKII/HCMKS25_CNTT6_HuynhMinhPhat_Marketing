from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.models.user import User
from app.models.campaign import Campaign, CampaignMember, CampaignTask
from app.core.exceptions import NotFoundException, ForbiddenException, BadRequestException
from app.schemas.campaign_task import TaskStatus, TaskPriority

def create_campaign(db: Session, current_user: User, name: str, description: str | None):
    if not name or name.strip() == "":
        raise BadRequestException("Tên chiến dịch không được để trống")
    if len(name) > 100:
        raise BadRequestException("Tên chiến dịch không được vượt quá 100 ký tự")

    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise NotFoundException("User không tồn tại")

    new_campaign = Campaign(
        name=name,
        description=description,
        owner_id=current_user.id,
        created_at=datetime.now(timezone.utc)
    )
    db.add(new_campaign)
    db.commit()
    db.refresh(new_campaign)

    new_campaign.owner = current_user

    return new_campaign


def list_campaigns(db: Session, current_user: User, name: str | None):
    query = db.query(Campaign).filter(Campaign.owner_id == current_user.id)
    member_campaigns = db.query(Campaign).join(CampaignMember).filter(CampaignMember.user_id == current_user.id)
    campaigns = query.union(member_campaigns)
    if name:
        campaigns = campaigns.filter(Campaign.name.ilike(f"%{name}%"))

    result = campaigns.all()

    return result


def get_campaign(db: Session, campaign_id: int, current_user: User):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise NotFoundException("Chiến dịch không tồn tại")

    is_owner = campaign.owner_id == current_user.id
    is_member = db.query(CampaignMember).filter(CampaignMember.campaign_id == campaign_id, CampaignMember.user_id == current_user.id).first() is not None

    if not (is_owner or is_member):
        raise ForbiddenException("Bạn không phải thành viên của chiến dịch này")

    campaign.owner = campaign.owner
    return campaign

def replace_campaign(db: Session, campaign_id: int, current_user: User, name: str, description: str | None):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise NotFoundException("Chiến dịch không tồn tại")
    if campaign.owner_id != current_user.id:
        raise ForbiddenException("Chỉ OWNER mới có quyền sửa chiến dịch")

    if not name or name.strip() == "":
        raise BadRequestException("Tên chiến dịch không được để trống")
    if len(name) > 100:
        raise BadRequestException("Tên chiến dịch không được vượt quá 100 ký tự")

    campaign.name = name
    campaign.description = description
    db.commit()
    db.refresh(campaign)

    return campaign

def update_campaign_partial(db: Session, campaign_id: int, current_user: User, name: str | None, description: str | None):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise NotFoundException("Chiến dịch không tồn tại")
    if campaign.owner_id != current_user.id:
        raise ForbiddenException("Chỉ OWNER mới có quyền sửa chiến dịch")

    if name is not None:
        campaign.name = name
    if description is not None:
        campaign.description = description

    db.commit()
    db.refresh(campaign)
    return campaign

def delete_campaign(db: Session, campaign_id: int, current_user: User):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise NotFoundException("Chiến dịch không tồn tại")
    if campaign.owner_id != current_user.id:
        raise ForbiddenException("Chỉ OWNER mới có quyền xóa chiến dịch")

    db.delete(campaign)
    db.commit()
    return {
        "status": "success", 
        "message": f"Chiến dịch '{campaign.name}' đã được xóa thành công"
    }

def add_member(db: Session, campaign_id: int, current_user: User, user_id: int):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise NotFoundException("Chiến dịch không tồn tại")
    if campaign.owner_id != current_user.id:
        raise ForbiddenException("Chỉ OWNER mới có quyền thêm thành viên")
    
    if user_id == campaign.owner_id:
        raise BadRequestException("Chủ sở hữu chiến dịch đã tự động có quyền, không thể thêm làm Member!")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundException("User không tồn tại trên hệ thống!")

    existing_member = db.query(CampaignMember).filter(CampaignMember.campaign_id == campaign_id, CampaignMember.user_id == user_id).first()
    if existing_member:
        raise BadRequestException("User này đã là thành viên của chiến dịch")

    new_member = CampaignMember(
        campaign_id=campaign_id, 
        user_id=user_id, 
        role="MEMBER"
    )

    db.add(new_member)
    db.commit()
    db.refresh(user)

    return user

def remove_member(db: Session, campaign_id: int, current_user: User, user_id: int):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise NotFoundException("Chiến dịch không tồn tại")
    if campaign.owner_id != current_user.id:
        raise ForbiddenException("Chỉ OWNER mới có quyền xóa thành viên")

    member = db.query(CampaignMember).filter(CampaignMember.campaign_id == campaign_id, CampaignMember.user_id == user_id).first()
    if not member:
        raise NotFoundException("Thành viên không tồn tại trong chiến dịch")
    if user_id == campaign.owner_id:
        raise BadRequestException("Không thể xóa OWNER cuối cùng của chiến dịch")

    db.delete(member)
    db.commit()
    return {
        "status": "success", 
        "message": f"User {user_id} đã được xóa khỏi chiến dịch '{campaign.name}'"
    }

def list_members(db: Session, campaign_id: int, current_user: User):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise NotFoundException("Chiến dịch không tồn tại")

    is_owner = campaign.owner_id == current_user.id
    is_member = db.query(CampaignMember).filter(CampaignMember.campaign_id == campaign_id, CampaignMember.user_id == current_user.id).first() is not None

    if not (is_owner or is_member):
        raise ForbiddenException("Bạn không phải thành viên của chiến dịch này")

    members = db.query(CampaignMember).filter(CampaignMember.campaign_id == campaign_id).all()

    return members


def create_campaign_task(db: Session, campaign_id: int, current_user: User, title: str, description: str | None, status: TaskStatus, priority: TaskPriority, due_date: datetime | None, assignee_id: int | None):
    
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise NotFoundException("Chiến dịch không tồn tại")

    is_owner = campaign.owner_id == current_user.id
    is_member = db.query(CampaignMember).filter(CampaignMember.campaign_id == campaign_id, CampaignMember.user_id == current_user.id).first() is not None
    if not (is_owner or is_member):
        raise ForbiddenException("Bạn không phải thành viên của chiến dịch này")

    if assignee_id and assignee_id > 0:
        assignee = db.query(User).filter(User.id == assignee_id).first()
        if not assignee:
            raise NotFoundException("Assignee không tồn tại")

        is_assignee_owner = campaign.owner_id == assignee_id
        is_assignee_member = (db.query(CampaignMember).filter(CampaignMember.campaign_id == campaign_id, CampaignMember.user_id == assignee_id).first() is not None)

        if not (is_assignee_owner or is_assignee_member):
            raise BadRequestException("Người được giao công việc không thuộc chiến dịch này")
    else:
        assignee_id = None

    new_task = CampaignTask(
        campaign_id=campaign_id,
        title=title.strip(),
        description=description,
        status=status,
        priority=priority,
        due_date=due_date,
        assignee_id=assignee_id,
        created_at=datetime.now(timezone.utc)
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task
