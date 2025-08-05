from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
import re
from typing import Optional
from app.utils.auth import verify_token

security = HTTPBearer(auto_error=False)

# Security headers middleware
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    
    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    
    # Add HSTS in production
    if not request.url.hostname in ["localhost", "127.0.0.1"]:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    return response

# Input validation middleware
async def input_validation_middleware(request: Request, call_next):
    # Check for suspicious patterns in URL
    suspicious_patterns = [
        r'\.\./',  # Path traversal
        r'<script',  # XSS
        r'javascript:',  # XSS
        r'data:',  # Data URLs
        r'vbscript:',  # VBScript
        r'onload=',  # Event handlers
        r'onerror=',  # Event handlers
    ]
    
    url_path = str(request.url.path).lower()
    for pattern in suspicious_patterns:
        if re.search(pattern, url_path, re.IGNORECASE):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Invalid request"}
            )
    
    # Check request size
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > 10 * 1024 * 1024:  # 10MB limit
        return JSONResponse(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            content={"detail": "Request too large"}
        )
    
    return await call_next(request)

# Authentication dependency
async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = None):
    if not credentials:
        return None
    
    try:
        payload = verify_token(credentials.credentials)
        return payload.get("sub")
    except HTTPException:
        return None

# Admin authentication dependency
async def require_admin(credentials: HTTPAuthorizationCredentials = security):
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = verify_token(credentials.credentials)
        if payload.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        return payload.get("sub")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
