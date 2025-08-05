from functools import lru_cache
from typing import Optional
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from app.core.config import settings
from app.services.enhanced_chat_service import EnhancedChatService
from app.services.enhanced_rag_service import EnhancedRAGService
from app.services.chat_monitoring_service import ChatMonitoringService
from app.services.config_service import ConfigService
from app.services.document_service import DocumentService
from app.services.embedding_service import EmbeddingService
from app.services.file_processor import FileProcessor
from app.services.storage_service import StorageService

# Security
security = HTTPBearer(auto_error=False)


# Authentication and Authorization
async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[str]:
    """Get current user from JWT token (optional)"""
    if not credentials:
        return None

    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except jwt.PyJWTError:
        return None


async def get_current_admin_user(
    current_user: Optional[str] = Depends(get_current_user)
) -> str:
    """Get current admin user (required)"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # In production, check if user has admin role
    # For now, we'll check if it's the admin username
    if current_user != settings.ADMIN_USERNAME:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    return current_user


# Service Dependencies
@lru_cache()
def get_enhanced_chat_service() -> EnhancedChatService:
    """Get enhanced chat service instance"""
    return EnhancedChatService()


@lru_cache()
def get_enhanced_rag_service() -> EnhancedRAGService:
    """Get enhanced RAG service instance"""
    return EnhancedRAGService()


@lru_cache()
def get_chat_monitoring_service() -> ChatMonitoringService:
    """Get chat monitoring service instance"""
    return ChatMonitoringService()


@lru_cache()
def get_config_service() -> ConfigService:
    """Get configuration service instance"""
    return ConfigService()


@lru_cache()
def get_analytics_service() -> AnalyticsService:
    """Get analytics service instance"""
    return AnalyticsService()


@lru_cache()
def get_document_service() -> DocumentService:
    """Get document service instance"""
    return DocumentService()


@lru_cache()
def get_embedding_service() -> EmbeddingService:
    """Get embedding service instance"""
    return EmbeddingService()


@lru_cache()
def get_file_processor() -> FileProcessor:
    """Get file processor instance"""
    return FileProcessor()


@lru_cache()
def get_storage_service() -> StorageService:
    """Get storage service instance"""
    return StorageService()
