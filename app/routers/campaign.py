from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.db.database import get_db
from app.models.user import User
from app.models.campaign import Campaign, CampaignMember
from app.dependencies.auth import get_current_user
from app.schemas.campaign import CampaignCreate, CampaignResponse, CampaignUpdate, CampaignMemberResponse
from app.core.exceptions import NotFoundException, ForbiddenException, BadRequestException
from app.schemas.user import UserResponse

router = APIRouter(
    prefix="/campaigns",
    tags=["Campaigns"]
)

@router.post("", response_model=CampaignResponse)
def create_campaign(campaign_in: CampaignCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not campaign_in.name or campaign_in.name.strip() == "":
        raise BadRequestException("Tên chiến dịch không được để trống")
    if len(campaign_in.name) > 100:
        raise BadRequestException("Tên chiến dịch không được vượt quá 100 ký tự")

    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise NotFoundException("User không tồn tại")
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

@router.get("/{id}", response_model=CampaignResponse)
def get_campaign(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    campaign = db.query(Campaign).filter(Campaign.id == id).first()
    if not campaign:
        raise NotFoundException("Chiến dịch không tồn tại")

    is_owner = campaign.owner_id == current_user.id
    is_member = (db.query(CampaignMember).filter(CampaignMember.campaign_id == id, CampaignMember.user_id == current_user.id).first() is not None)

    if not (is_owner or is_member):
        raise ForbiddenException("Bạn không phải thành viên của chiến dịch này")

    return campaign

@router.put("/{id}", response_model=CampaignResponse)
def replace_campaign(id: int, campaign_in: CampaignCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    campaign = db.query(Campaign).filter(Campaign.id == id).first()
    if not campaign:
        raise NotFoundException("Chiến dịch không tồn tại")

    if campaign.owner_id != current_user.id:
        raise ForbiddenException("Chỉ OWNER mới có quyền sửa chiến dịch")
    
    if not campaign_in.name or campaign_in.name.strip() == "":
        raise BadRequestException("Tên chiến dịch không được để trống")
    
    if len(campaign_in.name) > 100:
        raise BadRequestException("Tên chiến dịch không được vượt quá 100 ký tự")

    campaign.name = campaign_in.name
    campaign.description = campaign_in.description

    db.commit()
    db.refresh(campaign)
    return campaign

@router.patch("/{id}", response_model=CampaignResponse)
def update_campaign_partial(id: int, campaign_in: CampaignUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    campaign = db.query(Campaign).filter(Campaign.id == id).first()
    if not campaign:
        raise NotFoundException("Chiến dịch không tồn tại")

    if campaign.owner_id != current_user.id:
        raise ForbiddenException("Chỉ OWNER mới có quyền sửa chiến dịch")
    
    if campaign_in.name is not None:
        campaign.name = campaign_in.name

    if campaign_in.description is not None:
        campaign.description = campaign_in.description

    db.commit()
    db.refresh(campaign)
    return campaign

@router.delete("/{id}")
def delete_campaign(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    campaign = db.query(Campaign).filter(Campaign.id == id).first()
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

@router.post("/{id}/members", response_model=UserResponse)
def add_member_to_campaign(id: int, user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    campaign = db.query(Campaign).filter(Campaign.id == id).first()
    if not campaign:
        raise NotFoundException("Chiến dịch không tồn tại")

    if campaign.owner_id != current_user.id:
        raise ForbiddenException("Chỉ OWNER mới có quyền thêm thành viên")

    if user_id == campaign.owner_id:
        raise BadRequestException("Chủ sở hữu chiến dịch đã tự động có quyền, không thể thêm làm Member!")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundException("User không tồn tại trên hệ thống!")

    existing_member = (db.query(CampaignMember).filter(CampaignMember.campaign_id == id, CampaignMember.user_id == user_id).first())
    if existing_member:
        raise BadRequestException("User này đã là thành viên của chiến dịch")

    new_member = CampaignMember(
        campaign_id=id,
        user_id=user_id,
        role="MEMBER"
    )
    db.add(new_member)
    db.commit()
    db.refresh(user)

    return user

@router.delete("/{id}/members/{user_id}")
def remove_member_from_campaign(id: int, user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    campaign = db.query(Campaign).filter(Campaign.id == id).first()
    if not campaign:
        raise NotFoundException("Chiến dịch không tồn tại")

    if campaign.owner_id != current_user.id:
        raise ForbiddenException("Chỉ OWNER mới có quyền xóa thành viên")

    member = (db.query(CampaignMember).filter(CampaignMember.campaign_id == id, CampaignMember.user_id == user_id).first())
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

@router.get("/{id}/members", response_model=list[CampaignMemberResponse])
def list_campaign_members(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    campaign = db.query(Campaign).filter(Campaign.id == id).first()
    if not campaign:
        raise NotFoundException("Chiến dịch không tồn tại")

    is_owner = campaign.owner_id == current_user.id
    is_member = (db.query(CampaignMember).filter(CampaignMember.campaign_id == id, CampaignMember.user_id == current_user.id).first() is not None)

    if not (is_owner or is_member):
        raise ForbiddenException("Bạn không phải thành viên của chiến dịch này")

    members = (db.query(CampaignMember).filter(CampaignMember.campaign_id == id).all())

    return members