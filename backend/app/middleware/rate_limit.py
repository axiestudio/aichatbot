import time
from typing import Dict, Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import asyncio
from collections import defaultdict, deque

class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, deque] = defaultdict(deque)
        
    def is_allowed(self, identifier: str) -> bool:
        now = time.time()
        minute_ago = now - 60
        
        # Clean old requests
        while self.requests[identifier] and self.requests[identifier][0] < minute_ago:
            self.requests[identifier].popleft()
            
        # Check if under limit
        if len(self.requests[identifier]) >= self.requests_per_minute:
            return False
            
        # Add current request
        self.requests[identifier].append(now)
        return True
        
    def get_reset_time(self, identifier: str) -> Optional[int]:
        if not self.requests[identifier]:
            return None
        return int(self.requests[identifier][0] + 60)

# Global rate limiter instance
rate_limiter = RateLimiter()

async def rate_limit_middleware(request: Request, call_next):
    # Get client IP
    client_ip = request.client.host if request.client else "unknown"
    
    # Check rate limit
    if not rate_limiter.is_allowed(client_ip):
        reset_time = rate_limiter.get_reset_time(client_ip)
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "detail": "Rate limit exceeded",
                "reset_time": reset_time
            },
            headers={
                "X-RateLimit-Limit": str(rate_limiter.requests_per_minute),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(reset_time) if reset_time else ""
            }
        )
    
    # Process request
    response = await call_next(request)
    
    # Add rate limit headers
    remaining = max(0, rate_limiter.requests_per_minute - len(rate_limiter.requests[client_ip]))
    response.headers["X-RateLimit-Limit"] = str(rate_limiter.requests_per_minute)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    
    return response
