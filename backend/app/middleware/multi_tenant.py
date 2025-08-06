"""
Multi-Tenant Middleware for Instance Isolation
Enterprise-grade tenant isolation and routing
"""

import logging
from typing import Optional
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.database import ChatInstance

logger = logging.getLogger(__name__)


class MultiTenantMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle multi-tenant routing and instance isolation
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.tenant_cache = {}  # Simple in-memory cache for tenant lookups
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request with tenant context"""
        
        # Skip tenant resolution for certain paths
        if self._should_skip_tenant_resolution(request.url.path):
            return await call_next(request)
        
        # Extract tenant information
        tenant_info = await self._resolve_tenant(request)
        
        if tenant_info:
            # Add tenant context to request state
            request.state.tenant_id = tenant_info["id"]
            request.state.tenant_subdomain = tenant_info["subdomain"]
            request.state.tenant_active = tenant_info["is_active"]
            
            # Check if tenant is active
            if not tenant_info["is_active"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Instance is currently inactive"
                )
        
        # Process request
        response = await call_next(request)
        
        # Add tenant headers to response
        if tenant_info:
            response.headers["X-Tenant-ID"] = tenant_info["id"]
            response.headers["X-Tenant-Subdomain"] = tenant_info["subdomain"]
        
        return response
    
    def _should_skip_tenant_resolution(self, path: str) -> bool:
        """Check if tenant resolution should be skipped for this path"""
        skip_paths = [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/api/v1/super-admin",
            "/api/v1/monitoring",
            "/api/v1/errors"
        ]
        
        return any(path.startswith(skip_path) for skip_path in skip_paths)
    
    async def _resolve_tenant(self, request: Request) -> Optional[dict]:
        """Resolve tenant from request"""
        
        # Method 1: Extract from subdomain
        host = request.headers.get("host", "")
        if "." in host:
            subdomain = host.split(".")[0]
            if subdomain and subdomain != "www":
                return await self._get_tenant_by_subdomain(subdomain)
        
        # Method 2: Extract from custom header (for API calls)
        tenant_header = request.headers.get("X-Tenant-ID")
        if tenant_header:
            return await self._get_tenant_by_id(tenant_header)
        
        # Method 3: Extract from path parameter (for embedded widgets)
        path_parts = request.url.path.split("/")
        if len(path_parts) > 3 and path_parts[1] == "chat":
            potential_tenant = path_parts[2]
            return await self._get_tenant_by_subdomain(potential_tenant)
        
        # Method 4: Default tenant for development/testing
        if request.headers.get("host", "").startswith("localhost"):
            return await self._get_default_tenant()
        
        return None
    
    async def _get_tenant_by_subdomain(self, subdomain: str) -> Optional[dict]:
        """Get tenant information by subdomain"""
        
        # Check cache first
        cache_key = f"subdomain:{subdomain}"
        if cache_key in self.tenant_cache:
            return self.tenant_cache[cache_key]
        
        # Query database
        try:
            # Get database session (simplified - in production use dependency injection)
            db = next(get_db())
            
            instance = db.query(ChatInstance).filter(
                ChatInstance.subdomain == subdomain
            ).first()
            
            if instance:
                tenant_info = {
                    "id": instance.id,
                    "subdomain": instance.subdomain,
                    "name": instance.name,
                    "is_active": instance.is_active,
                    "plan_type": instance.plan_type
                }
                
                # Cache for 5 minutes
                self.tenant_cache[cache_key] = tenant_info
                return tenant_info
            
        except Exception as e:
            logger.error(f"Error resolving tenant by subdomain {subdomain}: {e}")
        
        return None
    
    async def _get_tenant_by_id(self, tenant_id: str) -> Optional[dict]:
        """Get tenant information by ID"""
        
        # Check cache first
        cache_key = f"id:{tenant_id}"
        if cache_key in self.tenant_cache:
            return self.tenant_cache[cache_key]
        
        # Query database
        try:
            db = next(get_db())
            
            instance = db.query(ChatInstance).filter(
                ChatInstance.id == tenant_id
            ).first()
            
            if instance:
                tenant_info = {
                    "id": instance.id,
                    "subdomain": instance.subdomain,
                    "name": instance.name,
                    "is_active": instance.is_active,
                    "plan_type": instance.plan_type
                }
                
                # Cache for 5 minutes
                self.tenant_cache[cache_key] = tenant_info
                return tenant_info
            
        except Exception as e:
            logger.error(f"Error resolving tenant by ID {tenant_id}: {e}")
        
        return None
    
    async def _get_default_tenant(self) -> Optional[dict]:
        """Get default tenant for development"""
        return {
            "id": "default",
            "subdomain": "default",
            "name": "Default Instance",
            "is_active": True,
            "plan_type": "free"
        }


def get_current_tenant(request: Request) -> Optional[dict]:
    """Helper function to get current tenant from request state"""
    if hasattr(request.state, "tenant_id"):
        return {
            "id": request.state.tenant_id,
            "subdomain": request.state.tenant_subdomain,
            "is_active": request.state.tenant_active
        }
    return None


def require_tenant(request: Request) -> dict:
    """Helper function that requires a tenant context"""
    tenant = get_current_tenant(request)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant context required"
        )
    return tenant
