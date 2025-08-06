import hashlib
import hmac
import time
import re
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
import logging
import ipaddress
from collections import defaultdict

from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import jwt

from app.core.config import settings
from app.middleware.error_handler import SecurityError, RateLimitError
from app.services.security_intelligence_service import security_intelligence_service

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)


class SecurityEnhancementMiddleware(BaseHTTPMiddleware):
    """Enhanced security middleware with multiple protection layers"""
    
    def __init__(self, app):
        super().__init__(app)
        self.security_monitor = SecurityMonitor()
        self.rate_limiter = AdvancedRateLimiter()
        self.input_validator = InputValidator()
        self.threat_detector = ThreatDetector()
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Apply security checks to all requests"""
        client_ip = self._get_client_ip(request)
        
        try:
            # 1. IP-based security checks
            await self._check_ip_security(client_ip, request)
            
            # 2. Rate limiting
            await self.rate_limiter.check_rate_limit(client_ip, request)
            
            # 3. Input validation and sanitization
            await self.input_validator.validate_request(request)
            
            # 4. Threat detection
            await self.threat_detector.analyze_request(request, client_ip)
            
            # 5. Security headers
            response = await call_next(request)
            self._add_security_headers(response)
            
            # 6. Log successful request
            await self.security_monitor.log_request(request, client_ip, "success")
            
            return response
            
        except (SecurityError, RateLimitError) as e:
            # Log security violation
            await self.security_monitor.log_security_event(
                request, client_ip, type(e).__name__, str(e)
            )
            raise
        except Exception as e:
            # Log unexpected error
            await self.security_monitor.log_security_event(
                request, client_ip, "UnexpectedError", str(e)
            )
            raise
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract real client IP address"""
        # Check for forwarded headers
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        if hasattr(request, "client") and request.client:
            return request.client.host
        
        return "unknown"
    
    async def _check_ip_security(self, client_ip: str, request: Request):
        """Check IP-based security rules"""
        # Check if IP is blocked
        if await self.security_monitor.is_ip_blocked(client_ip):
            raise SecurityError(
                "Access denied: IP address is blocked",
                threat_type="blocked_ip",
                details={"ip": client_ip}
            )
        
        # Check IP whitelist for admin endpoints
        if request.url.path.startswith("/admin/"):
            if not await self._is_ip_whitelisted(client_ip):
                raise SecurityError(
                    "Access denied: Admin access restricted",
                    threat_type="admin_access_violation",
                    details={"ip": client_ip, "path": request.url.path}
                )
    
    async def _is_ip_whitelisted(self, client_ip: str) -> bool:
        """Check if IP is whitelisted for admin access"""
        # In production, this would check against a database or config
        whitelist = getattr(settings, 'ADMIN_IP_WHITELIST', [])
        
        if not whitelist:
            return True  # No whitelist configured
        
        try:
            client_addr = ipaddress.ip_address(client_ip)
            for allowed in whitelist:
                if "/" in allowed:
                    # CIDR notation
                    if client_addr in ipaddress.ip_network(allowed):
                        return True
                else:
                    # Single IP
                    if client_addr == ipaddress.ip_address(allowed):
                        return True
        except ValueError:
            logger.warning(f"Invalid IP address format: {client_ip}")
        
        return False
    
    def _add_security_headers(self, response: Response):
        """Add security headers to response"""
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
        }
        
        for header, value in security_headers.items():
            response.headers[header] = value


class SecurityMonitor:
    """Monitor and track security events"""
    
    def __init__(self):
        self.blocked_ips: Set[str] = set()
        self.security_events: List[Dict] = []
        self.failed_attempts: Dict[str, List[datetime]] = defaultdict(list)
        self.max_failed_attempts = 5
        self.block_duration = timedelta(hours=1)
    
    async def log_request(self, request: Request, client_ip: str, status: str):
        """Log request for security monitoring"""
        # In production, this would log to a security database
        pass
    
    async def log_security_event(
        self, 
        request: Request, 
        client_ip: str, 
        event_type: str, 
        details: str
    ):
        """Log security event"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "client_ip": client_ip,
            "event_type": event_type,
            "details": details,
            "path": request.url.path,
            "method": request.method,
            "user_agent": request.headers.get("user-agent", "Unknown")
        }
        
        self.security_events.append(event)
        logger.warning(f"Security event: {event_type} from {client_ip} - {details}")
        
        # Track failed attempts
        if event_type in ["AuthenticationError", "SecurityError"]:
            await self._track_failed_attempt(client_ip)
    
    async def _track_failed_attempt(self, client_ip: str):
        """Track failed authentication attempts"""
        now = datetime.utcnow()
        
        # Clean old attempts
        cutoff = now - timedelta(hours=1)
        self.failed_attempts[client_ip] = [
            attempt for attempt in self.failed_attempts[client_ip]
            if attempt > cutoff
        ]
        
        # Add new attempt
        self.failed_attempts[client_ip].append(now)
        
        # Check if should block IP
        if len(self.failed_attempts[client_ip]) >= self.max_failed_attempts:
            await self._block_ip(client_ip)
    
    async def _block_ip(self, client_ip: str):
        """Block an IP address"""
        self.blocked_ips.add(client_ip)
        logger.warning(f"IP address blocked due to repeated violations: {client_ip}")
        
        # In production, this would persist to database
        # and potentially notify administrators
    
    async def is_ip_blocked(self, client_ip: str) -> bool:
        """Check if IP is blocked"""
        return client_ip in self.blocked_ips
    
    def get_security_stats(self) -> Dict:
        """Get security statistics"""
        return {
            "blocked_ips": len(self.blocked_ips),
            "recent_events": len([
                e for e in self.security_events
                if datetime.fromisoformat(e["timestamp"]) > datetime.utcnow() - timedelta(hours=24)
            ]),
            "failed_attempts": sum(len(attempts) for attempts in self.failed_attempts.values())
        }


class AdvancedRateLimiter:
    """Advanced rate limiting with multiple strategies"""
    
    def __init__(self):
        self.request_counts: Dict[str, List[datetime]] = defaultdict(list)
        self.rate_limits = {
            "default": {"requests": 60, "window": 60},  # 60 requests per minute
            "auth": {"requests": 5, "window": 60},      # 5 auth attempts per minute
            "upload": {"requests": 10, "window": 300},   # 10 uploads per 5 minutes
            "admin": {"requests": 100, "window": 60}     # 100 admin requests per minute
        }
    
    async def check_rate_limit(self, client_ip: str, request: Request):
        """Check rate limits for request"""
        # Determine rate limit category
        category = self._get_rate_limit_category(request)
        limits = self.rate_limits.get(category, self.rate_limits["default"])
        
        # Clean old requests
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=limits["window"])
        
        key = f"{client_ip}:{category}"
        self.request_counts[key] = [
            req_time for req_time in self.request_counts[key]
            if req_time > cutoff
        ]
        
        # Check if limit exceeded
        if len(self.request_counts[key]) >= limits["requests"]:
            raise RateLimitError(
                f"Rate limit exceeded: {limits['requests']} requests per {limits['window']} seconds",
                retry_after=limits["window"]
            )
        
        # Add current request
        self.request_counts[key].append(now)
    
    def _get_rate_limit_category(self, request: Request) -> str:
        """Determine rate limit category for request"""
        path = request.url.path
        
        if path.startswith("/auth/") or path.startswith("/login"):
            return "auth"
        elif path.startswith("/admin/"):
            return "admin"
        elif "upload" in path or request.method == "POST":
            return "upload"
        else:
            return "default"


class InputValidator:
    """Validate and sanitize input data"""
    
    def __init__(self):
        # Dangerous patterns to detect
        self.sql_injection_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
            r"(--|#|/\*|\*/)",
            r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
            r"(\'\s*(OR|AND)\s*\'\w*\'\s*=\s*\'\w*)"
        ]
        
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>.*?</iframe>",
            r"<object[^>]*>.*?</object>"
        ]
        
        self.path_traversal_patterns = [
            r"\.\./",
            r"\.\.\\",
            r"%2e%2e%2f",
            r"%2e%2e%5c"
        ]
    
    async def validate_request(self, request: Request):
        """Validate request for security threats"""
        # Check URL path
        await self._validate_path(request.url.path)
        
        # Check query parameters
        for key, value in request.query_params.items():
            await self._validate_input(value, f"query_param_{key}")
        
        # Check headers for suspicious content
        await self._validate_headers(request.headers)
    
    async def _validate_path(self, path: str):
        """Validate URL path"""
        # Check for path traversal
        for pattern in self.path_traversal_patterns:
            if re.search(pattern, path, re.IGNORECASE):
                raise SecurityError(
                    "Path traversal attempt detected",
                    threat_type="path_traversal",
                    details={"path": path}
                )
    
    async def _validate_input(self, value: str, field_name: str):
        """Validate input value"""
        if not isinstance(value, str):
            return
        
        # Check for SQL injection
        for pattern in self.sql_injection_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                raise SecurityError(
                    f"SQL injection attempt detected in {field_name}",
                    threat_type="sql_injection",
                    details={"field": field_name, "pattern": pattern}
                )
        
        # Check for XSS
        for pattern in self.xss_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                raise SecurityError(
                    f"XSS attempt detected in {field_name}",
                    threat_type="xss",
                    details={"field": field_name, "pattern": pattern}
                )
    
    async def _validate_headers(self, headers):
        """Validate request headers"""
        suspicious_headers = ["x-forwarded-host", "x-original-url", "x-rewrite-url"]
        
        for header_name in suspicious_headers:
            if header_name in headers:
                logger.warning(f"Suspicious header detected: {header_name}")


class ThreatDetector:
    """Detect various types of threats and attacks"""
    
    def __init__(self):
        self.suspicious_user_agents = [
            "sqlmap", "nikto", "nmap", "masscan", "zap", "burp",
            "acunetix", "nessus", "openvas", "w3af"
        ]
        
        self.bot_patterns = [
            r"bot", r"crawler", r"spider", r"scraper",
            r"curl", r"wget", r"python-requests"
        ]
    
    async def analyze_request(self, request: Request, client_ip: str):
        """Analyze request for threats"""
        user_agent = request.headers.get("user-agent", "").lower()
        
        # Check for suspicious user agents
        for suspicious in self.suspicious_user_agents:
            if suspicious in user_agent:
                raise SecurityError(
                    f"Suspicious user agent detected: {suspicious}",
                    threat_type="suspicious_user_agent",
                    details={"user_agent": user_agent, "ip": client_ip}
                )
        
        # Check for bot activity on sensitive endpoints
        if request.url.path.startswith(("/admin/", "/api/v1/admin/")):
            for pattern in self.bot_patterns:
                if re.search(pattern, user_agent, re.IGNORECASE):
                    raise SecurityError(
                        "Bot access to sensitive endpoint detected",
                        threat_type="bot_access",
                        details={"user_agent": user_agent, "path": request.url.path}
                    )


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[str]:
    """Enhanced user authentication with security checks"""
    if not credentials:
        return None
    
    try:
        # Decode JWT token
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Check token expiration
        exp = payload.get("exp")
        if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Token expired")
        
        return username
        
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token with enhanced security"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password with timing attack protection"""
    import bcrypt
    
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception:
        # Use constant-time comparison to prevent timing attacks
        dummy_hash = bcrypt.hashpw(b"dummy", bcrypt.gensalt())
        bcrypt.checkpw(b"dummy", dummy_hash)
        return False


def hash_password(password: str) -> str:
    """Hash password securely"""
    import bcrypt
    
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')
