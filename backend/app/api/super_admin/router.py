"""
Super Admin API Router - Centralized routing for all super admin endpoints
"""

from fastapi import APIRouter

from . import auth, instances, analytics, billing

# Create main super admin router
super_admin_router = APIRouter(prefix="/super-admin", tags=["super-admin"])

# Include all sub-routers
super_admin_router.include_router(auth.router)
super_admin_router.include_router(instances.router)
super_admin_router.include_router(analytics.router)
super_admin_router.include_router(billing.router)

# Health check for super admin system
@super_admin_router.get("/health")
async def super_admin_health():
    """Super admin system health check"""
    return {
        "status": "healthy",
        "service": "super-admin",
        "version": "1.0.0",
        "features": [
            "Multi-tenant instance management",
            "Global analytics and monitoring",
            "Revenue and billing management",
            "Enterprise security"
        ]
    }
