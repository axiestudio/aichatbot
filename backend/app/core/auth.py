"""
Unified Authentication and Authorization System
Enterprise-grade multi-tenant authentication
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Union
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import jwt
import bcrypt
import logging

from .database import get_db
from .config import settings
from ..models.database import InstanceAdmin, SuperAdmin

logger = logging.getLogger(__name__)
security = HTTPBearer()


class UnifiedAuthService:
    """Unified authentication service for all user types"""
    
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = "HS256"
        self.admin_token_expire_hours = 8
        self.super_admin_token_expire_hours = 24
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt with enhanced security"""
        salt = bcrypt.gensalt(rounds=12)  # Higher rounds for better security
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    def create_access_token(self, data: Dict[str, Any], token_type: str = "admin") -> str:
        """Create JWT access token with appropriate expiration"""
        to_encode = data.copy()
        
        # Set expiration based on token type
        if token_type == "super_admin":
            expire = datetime.utcnow() + timedelta(hours=self.super_admin_token_expire_hours)
        else:
            expire = datetime.utcnow() + timedelta(hours=self.admin_token_expire_hours)
        
        to_encode.update({
            "exp": expire,
            "type": token_type,
            "iat": datetime.utcnow(),
            "iss": "chatbot-platform"
        })
        
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str, expected_type: str = None) -> Dict[str, Any]:
        """Verify JWT token with enhanced validation"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Validate token type
            if expected_type and payload.get("type") != expected_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid token type. Expected: {expected_type}"
                )
            
            # Validate issuer
            if payload.get("iss") != "chatbot-platform":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token issuer"
                )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError as e:
            logger.error(f"JWT verification error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    def authenticate_admin(self, db: Session, email: str, password: str, instance_id: str = None) -> Optional[InstanceAdmin]:
        """Authenticate instance admin with optional instance filtering"""
        try:
            query = db.query(InstanceAdmin).filter(
                InstanceAdmin.email == email,
                InstanceAdmin.is_active == True
            )
            
            if instance_id:
                query = query.filter(InstanceAdmin.instance_id == instance_id)
            
            admin = query.first()
            
            if not admin or not self.verify_password(password, admin.password_hash):
                return None
            
            # Update last login
            admin.last_login = datetime.utcnow()
            db.commit()
            
            return admin
            
        except Exception as e:
            logger.error(f"Admin authentication error: {e}")
            return None
    
    def authenticate_super_admin(self, db: Session, email: str, password: str) -> Optional[SuperAdmin]:
        """Authenticate super admin"""
        try:
            super_admin = db.query(SuperAdmin).filter(
                SuperAdmin.email == email,
                SuperAdmin.is_active == True
            ).first()
            
            if not super_admin or not self.verify_password(password, super_admin.password_hash):
                return None
            
            # Update last login
            super_admin.last_login = datetime.utcnow()
            db.commit()
            
            return super_admin
            
        except Exception as e:
            logger.error(f"Super admin authentication error: {e}")
            return None


# Global auth service instance
auth_service = UnifiedAuthService()

# Convenience functions for backward compatibility
def hash_password(password: str) -> str:
    return auth_service.hash_password(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return auth_service.verify_password(password, hashed_password)

def create_access_token(data: Dict[str, Any], token_type: str = "admin") -> str:
    return auth_service.create_access_token(data, token_type)


def get_current_admin_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> InstanceAdmin:
    """Get current authenticated instance admin"""
    payload = auth_service.verify_token(credentials.credentials, "admin")
    admin_id = payload.get("sub")
    
    if not admin_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    admin = db.query(InstanceAdmin).filter(
        InstanceAdmin.id == admin_id,
        InstanceAdmin.is_active == True
    ).first()
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin not found"
        )
    
    return admin


def get_current_super_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> SuperAdmin:
    """Get current authenticated super admin"""
    payload = auth_service.verify_token(credentials.credentials, "super_admin")
    super_admin_id = payload.get("sub")
    
    if not super_admin_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    super_admin = db.query(SuperAdmin).filter(
        SuperAdmin.id == super_admin_id,
        SuperAdmin.is_active == True
    ).first()
    
    if not super_admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Super admin not found"
        )
    
    return super_admin


def authenticate_admin(db: Session, email: str, password: str, instance_id: str = None) -> Optional[InstanceAdmin]:
    """Authenticate instance admin"""
    return auth_service.authenticate_admin(db, email, password, instance_id)


def authenticate_super_admin(db: Session, email: str, password: str) -> Optional[SuperAdmin]:
    """Authenticate super admin"""
    return auth_service.authenticate_super_admin(db, email, password)
