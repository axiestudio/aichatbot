"""
Super Admin Instance Management API - Industry Leading Multi-Tenancy
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, validator
from typing import List, Dict, Any, Optional
import uuid
import secrets
import string

from ...core.database import get_db
from ...core.auth import get_current_super_admin, hash_password
from ...models.database import SuperAdmin, ChatInstance, InstanceAdmin, ApiConfiguration, RagInstruction

router = APIRouter(prefix="/instances", tags=["super-admin-instances"])


class InstanceCreate(BaseModel):
    name: str
    subdomain: str
    owner_email: EmailStr
    owner_name: str
    description: str = ""
    plan_type: str = "free"
    max_monthly_messages: int = 1000
    primary_color: str = "#3b82f6"
    secondary_color: str = "#e5e7eb"
    
    @validator('subdomain')
    def validate_subdomain(cls, v):
        if not v.isalnum() or len(v) < 3 or len(v) > 20:
            raise ValueError('Subdomain must be 3-20 alphanumeric characters')
        return v.lower()
    
    @validator('plan_type')
    def validate_plan_type(cls, v):
        if v not in ['free', 'pro', 'enterprise']:
            raise ValueError('Plan type must be free, pro, or enterprise')
        return v


class InstanceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    max_monthly_messages: Optional[int] = None
    plan_type: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    domain: Optional[str] = None


class InstanceResponse(BaseModel):
    id: str
    name: str
    subdomain: str
    domain: Optional[str]
    description: str
    owner_email: str
    owner_name: str
    is_active: bool
    max_monthly_messages: int
    current_monthly_messages: int
    plan_type: str
    primary_color: str
    secondary_color: str
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class InstanceStatsResponse(BaseModel):
    total_instances: int
    active_instances: int
    inactive_instances: int
    total_monthly_messages: int
    instances_by_plan: Dict[str, int]
    recent_instances: List[InstanceResponse]


class InstanceAdminCreate(BaseModel):
    email: EmailStr
    name: str
    role: str = "admin"
    
    @validator('role')
    def validate_role(cls, v):
        if v not in ['admin', 'viewer']:
            raise ValueError('Role must be admin or viewer')
        return v


@router.post("/", response_model=InstanceResponse)
async def create_instance(
    instance_data: InstanceCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_super_admin: SuperAdmin = Depends(get_current_super_admin)
):
    """Create new chat instance with full setup"""
    
    if not current_super_admin.can_create_instances:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: cannot create instances"
        )
    
    # Check if subdomain is available
    existing = db.query(ChatInstance).filter(ChatInstance.subdomain == instance_data.subdomain).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subdomain already taken"
        )
    
    # Create instance
    instance = ChatInstance(
        id=str(uuid.uuid4()),
        name=instance_data.name,
        subdomain=instance_data.subdomain,
        description=instance_data.description,
        owner_email=instance_data.owner_email,
        owner_name=instance_data.owner_name,
        max_monthly_messages=instance_data.max_monthly_messages,
        plan_type=instance_data.plan_type,
        primary_color=instance_data.primary_color,
        secondary_color=instance_data.secondary_color
    )
    
    db.add(instance)
    db.commit()
    db.refresh(instance)
    
    # Create default admin user for the instance
    background_tasks.add_task(setup_instance_defaults, instance.id, instance_data.owner_email, instance_data.owner_name, db)
    
    return InstanceResponse.from_orm(instance)


@router.get("/", response_model=List[InstanceResponse])
async def get_all_instances(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    db: Session = Depends(get_db),
    current_super_admin: SuperAdmin = Depends(get_current_super_admin)
):
    """Get all chat instances"""
    
    query = db.query(ChatInstance)
    
    if active_only:
        query = query.filter(ChatInstance.is_active == True)
    
    instances = query.offset(skip).limit(limit).all()
    return [InstanceResponse.from_orm(instance) for instance in instances]


@router.get("/stats", response_model=InstanceStatsResponse)
async def get_instance_stats(
    db: Session = Depends(get_db),
    current_super_admin: SuperAdmin = Depends(get_current_super_admin)
):
    """Get comprehensive instance statistics"""
    
    if not current_super_admin.can_view_all_analytics:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: cannot view analytics"
        )
    
    total_instances = db.query(ChatInstance).count()
    active_instances = db.query(ChatInstance).filter(ChatInstance.is_active == True).count()
    inactive_instances = total_instances - active_instances
    
    # Calculate total monthly messages
    total_monthly_messages = db.query(ChatInstance).with_entities(
        db.func.sum(ChatInstance.current_monthly_messages)
    ).scalar() or 0
    
    # Instances by plan
    plan_counts = db.query(ChatInstance.plan_type, db.func.count(ChatInstance.id)).group_by(ChatInstance.plan_type).all()
    instances_by_plan = {plan: count for plan, count in plan_counts}
    
    # Recent instances
    recent_instances = db.query(ChatInstance).order_by(ChatInstance.created_at.desc()).limit(5).all()
    
    return InstanceStatsResponse(
        total_instances=total_instances,
        active_instances=active_instances,
        inactive_instances=inactive_instances,
        total_monthly_messages=total_monthly_messages,
        instances_by_plan=instances_by_plan,
        recent_instances=[InstanceResponse.from_orm(instance) for instance in recent_instances]
    )


@router.get("/{instance_id}", response_model=InstanceResponse)
async def get_instance(
    instance_id: str,
    db: Session = Depends(get_db),
    current_super_admin: SuperAdmin = Depends(get_current_super_admin)
):
    """Get specific instance details"""
    
    instance = db.query(ChatInstance).filter(ChatInstance.id == instance_id).first()
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    return InstanceResponse.from_orm(instance)


@router.put("/{instance_id}", response_model=InstanceResponse)
async def update_instance(
    instance_id: str,
    instance_update: InstanceUpdate,
    db: Session = Depends(get_db),
    current_super_admin: SuperAdmin = Depends(get_current_super_admin)
):
    """Update instance configuration"""
    
    instance = db.query(ChatInstance).filter(ChatInstance.id == instance_id).first()
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    # Update fields
    update_data = instance_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(instance, field, value)
    
    db.commit()
    db.refresh(instance)
    
    return InstanceResponse.from_orm(instance)


@router.delete("/{instance_id}")
async def delete_instance(
    instance_id: str,
    db: Session = Depends(get_db),
    current_super_admin: SuperAdmin = Depends(get_current_super_admin)
):
    """Delete instance and all associated data"""
    
    if not current_super_admin.can_delete_instances:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: cannot delete instances"
        )
    
    instance = db.query(ChatInstance).filter(ChatInstance.id == instance_id).first()
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    # Delete associated data
    db.query(InstanceAdmin).filter(InstanceAdmin.instance_id == instance_id).delete()
    db.query(ApiConfiguration).filter(ApiConfiguration.instance_id == instance_id).delete()
    db.query(RagInstruction).filter(RagInstruction.instance_id == instance_id).delete()
    
    # Delete instance
    db.delete(instance)
    db.commit()
    
    return {"message": "Instance deleted successfully"}


def setup_instance_defaults(instance_id: str, owner_email: str, owner_name: str, db: Session):
    """Setup default configurations for new instance"""
    
    # Generate random password for admin
    password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))

    # Create instance admin
    admin = InstanceAdmin(
        id=str(uuid.uuid4()),
        instance_id=instance_id,
        email=owner_email,
        name=owner_name,
        password_hash=hash_password(password),
        role="admin"
    )
    
    db.add(admin)
    db.commit()
    
    # TODO: Send welcome email with login credentials
    # TODO: Create default API configuration
    # TODO: Create default RAG instructions
