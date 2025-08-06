from fastapi import APIRouter
from app.api.v1.endpoints import chat, config, documents, admin_enhanced, monitoring, websocket, errors, files, search
from app.api.v1.endpoints.advanced_analytics import router as advanced_analytics_router
from app.api.v1.endpoints.intelligence_apis import router as intelligence_router

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(config.router, prefix="/config", tags=["configuration"])
api_router.include_router(admin_enhanced.router, prefix="/admin", tags=["admin"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])
api_router.include_router(websocket.router, prefix="/realtime", tags=["websocket"])
api_router.include_router(errors.router, prefix="/errors", tags=["errors"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(advanced_analytics_router, prefix="/advanced", tags=["advanced_analytics"])
api_router.include_router(intelligence_router, prefix="/ai", tags=["intelligence"])
