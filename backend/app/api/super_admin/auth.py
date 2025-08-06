"""
Super Admin Authentication API
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Dict, Any
import uuid

from ...core.database import get_db
from ...core.auth import auth_service, get_current_super_admin
from ...models.database import SuperAdmin

router = APIRouter(prefix="/auth", tags=["super-admin-auth"])


class SuperAdminLogin(BaseModel):
    email: EmailStr
    password: str


class SuperAdminCreate(BaseModel):
    email: EmailStr
    name: str
    password: str
    can_create_instances: bool = True
    can_delete_instances: bool = True
    can_manage_billing: bool = True
    can_view_all_analytics: bool = True


class SuperAdminResponse(BaseModel):
    id: str
    email: str
    name: str
    can_create_instances: bool
    can_delete_instances: bool
    can_manage_billing: bool
    can_view_all_analytics: bool
    is_active: bool
    last_login: str = None
    created_at: str
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    super_admin: SuperAdminResponse


@router.post("/login", response_model=TokenResponse)
async def login_super_admin(
    login_data: SuperAdminLogin,
    db: Session = Depends(get_db)
):
    """Super admin login"""
    super_admin = auth_service.authenticate_super_admin(
        db, login_data.email, login_data.password
    )

    if not super_admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Create access token
    access_token = auth_service.create_access_token(
        data={"sub": super_admin.id, "email": super_admin.email},
        token_type="super_admin"
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        super_admin=SuperAdminResponse.from_orm(super_admin)
    )


@router.post("/create-super-admin", response_model=SuperAdminResponse)
async def create_super_admin(
    super_admin_data: SuperAdminCreate,
    db: Session = Depends(get_db),
    current_super_admin: SuperAdmin = Depends(get_current_super_admin)
):
    """Create new super admin (requires existing super admin)"""
    
    # Check if email already exists
    existing = db.query(SuperAdmin).filter(SuperAdmin.email == super_admin_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new super admin
    new_super_admin = SuperAdmin(
        id=str(uuid.uuid4()),
        email=super_admin_data.email,
        name=super_admin_data.name,
        password_hash=super_admin_auth.hash_password(super_admin_data.password),
        can_create_instances=super_admin_data.can_create_instances,
        can_delete_instances=super_admin_data.can_delete_instances,
        can_manage_billing=super_admin_data.can_manage_billing,
        can_view_all_analytics=super_admin_data.can_view_all_analytics
    )
    
    db.add(new_super_admin)
    db.commit()
    db.refresh(new_super_admin)
    
    return SuperAdminResponse.from_orm(new_super_admin)


@router.get("/me", response_model=SuperAdminResponse)
async def get_current_super_admin_info(
    current_super_admin: SuperAdmin = Depends(get_current_super_admin)
):
    """Get current super admin information"""
    return SuperAdminResponse.from_orm(current_super_admin)


@router.post("/logout")
async def logout_super_admin(
    current_super_admin: SuperAdmin = Depends(get_current_super_admin)
):
    """Super admin logout"""
    # In a real implementation, you might want to blacklist the token
    return {"message": "Successfully logged out"}


@router.post("/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    current_super_admin: SuperAdmin = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Change super admin password"""
    
    # Verify old password
    if not super_admin_auth.verify_password(old_password, current_super_admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid current password"
        )
    
    # Update password
    current_super_admin.password_hash = super_admin_auth.hash_password(new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}


@router.post("/setup-first-super-admin", response_model=SuperAdminResponse)
async def setup_first_super_admin(
    super_admin_data: SuperAdminCreate,
    db: Session = Depends(get_db)
):
    """Setup the first super admin (only works if no super admins exist)"""

    # Check if any super admins exist
    existing_count = db.query(SuperAdmin).count()
    if existing_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Super admin already exists. Use regular creation endpoint."
        )

    # Create first super admin
    first_super_admin = SuperAdmin(
        id=str(uuid.uuid4()),
        email=super_admin_data.email,
        name=super_admin_data.name,
        password_hash=auth_service.hash_password(super_admin_data.password),
        can_create_instances=True,
        can_delete_instances=True,
        can_manage_billing=True,
        can_view_all_analytics=True
    )

    db.add(first_super_admin)
    db.commit()
    db.refresh(first_super_admin)

    return SuperAdminResponse.from_orm(first_super_admin)


@router.post("/setup-railway-admin", response_model=SuperAdminResponse)
async def setup_railway_admin(
    db: Session = Depends(get_db)
):
    """Setup Railway super admin with predefined credentials"""

    # Check if Railway admin already exists
    existing_admin = db.query(SuperAdmin).filter(
        SuperAdmin.email == "stefan@axiestudio.se"
    ).first()

    if existing_admin:
        return SuperAdminResponse.from_orm(existing_admin)

    # Create Railway super admin
    railway_admin = SuperAdmin(
        id=str(uuid.uuid4()),
        email="stefan@axiestudio.se",
        name="Stefan - Railway Super Admin",
        password_hash=auth_service.hash_password("STEfanjohn!12"),
        can_create_instances=True,
        can_delete_instances=True,
        can_manage_billing=True,
        can_view_all_analytics=True
    )

    db.add(railway_admin)
    db.commit()
    db.refresh(railway_admin)

    return SuperAdminResponse.from_orm(railway_admin)
