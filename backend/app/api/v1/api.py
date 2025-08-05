from fastapi import APIRouter
from app.api.v1.endpoints import chat, config, documents, admin_enhanced

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(config.router, prefix="/config", tags=["configuration"])
api_router.include_router(admin_enhanced.router, prefix="/admin", tags=["admin"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
