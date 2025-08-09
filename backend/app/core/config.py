from pydantic_settings import BaseSettings
from typing import List, Optional
import os
import json

# Import enterprise settings
try:
    from app.core.enterprise_config import enterprise_settings
    ENTERPRISE_CONFIG_AVAILABLE = True
except ImportError:
    ENTERPRISE_CONFIG_AVAILABLE = False
    enterprise_settings = None


def safe_getenv_list(key: str, default: str = "") -> List[str]:
    """Safely get environment variable as list, avoiding JSON parsing issues"""
    value = os.getenv(key, default)
    if not value or value.strip() == "":
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def safe_getenv_bool(key: str, default: str = "false") -> bool:
    """Safely get environment variable as boolean"""
    return os.getenv(key, default).lower() == "true"


def safe_getenv_int(key: str, default: str = "0") -> int:
    """Safely get environment variable as integer"""
    try:
        return int(os.getenv(key, default))
    except (ValueError, TypeError):
        return int(default)


class Settings(BaseSettings):
    """Application settings"""
    
    # FastAPI Configuration (Production-Optimized)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "prod-chatbot-secret-key-2024-digital-ocean-deployment-secure")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    # Railway-specific configuration
    RAILWAY_ENVIRONMENT: Optional[str] = os.getenv("RAILWAY_ENVIRONMENT")
    RAILWAY_PROJECT_ID: Optional[str] = os.getenv("RAILWAY_PROJECT_ID")
    RAILWAY_SERVICE_ID: Optional[str] = os.getenv("RAILWAY_SERVICE_ID")

    # Security Configuration
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "CHANGE-THIS-JWT-SECRET-MINIMUM-32-CHARACTERS")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # Admin Configuration
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "CHANGE-THIS-ADMIN-PASSWORD")
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "admin@localhost")
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/chatbot_db")
    
    # Supabase Configuration
    SUPABASE_URL: Optional[str] = None
    SUPABASE_ANON_KEY: Optional[str] = None
    SUPABASE_SERVICE_KEY: Optional[str] = None
    
    # AI Provider Configuration
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")

    # Distributed Tracing
    JAEGER_ENDPOINT: Optional[str] = os.getenv("JAEGER_ENDPOINT")
    JAEGER_HOST: str = os.getenv("JAEGER_HOST", "localhost")
    JAEGER_PORT: int = int(os.getenv("JAEGER_PORT", "6831"))
    ENABLE_TRACING: bool = os.getenv("ENABLE_TRACING", "true").lower() == "true"

    # Performance & Monitoring
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "true").lower() == "true"

    # Cache Configuration
    CACHE_NAMESPACE: str = os.getenv("CACHE_NAMESPACE", "chatbot")
    CACHE_DEFAULT_TTL: int = int(os.getenv("CACHE_DEFAULT_TTL", "300"))

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = safe_getenv_bool("RATE_LIMIT_ENABLED", "true")

    @property
    def RATE_LIMIT_WHITELIST(self) -> List[str]:
        return safe_getenv_list("RATE_LIMIT_WHITELIST", "")

    # Performance Monitoring
    PERFORMANCE_MONITORING_ENABLED: bool = os.getenv("PERFORMANCE_MONITORING_ENABLED", "true").lower() == "true"
    PERFORMANCE_RETENTION_HOURS: int = int(os.getenv("PERFORMANCE_RETENTION_HOURS", "24"))

    # Health Checks
    HEALTH_CHECK_ENABLED: bool = os.getenv("HEALTH_CHECK_ENABLED", "true").lower() == "true"
    HEALTH_CHECK_INTERVAL: int = int(os.getenv("HEALTH_CHECK_INTERVAL", "30"))

    # Error Tracking
    ERROR_TRACKING_ENABLED: bool = os.getenv("ERROR_TRACKING_ENABLED", "true").lower() == "true"
    ERROR_RETENTION_HOURS: int = int(os.getenv("ERROR_RETENTION_HOURS", "168"))

    # Security
    SECURITY_HEADERS_ENABLED: bool = safe_getenv_bool("SECURITY_HEADERS_ENABLED", "true")

    # CORS Origins - handle as string and split manually to avoid JSON parsing issues
    @property
    def CORS_ORIGINS(self) -> List[str]:
        origins = safe_getenv_list("CORS_ORIGINS", "*")
        return origins if origins else ["*"]

    # Production Settings
    WORKERS: int = int(os.getenv("WORKERS", "1"))
    MAX_CONNECTIONS: int = int(os.getenv("MAX_CONNECTIONS", "1000"))
    KEEPALIVE_TIMEOUT: int = int(os.getenv("KEEPALIVE_TIMEOUT", "5"))
    ENABLE_CACHING: bool = os.getenv("ENABLE_CACHING", "true").lower() == "true"
    ENABLE_CIRCUIT_BREAKER: bool = os.getenv("ENABLE_CIRCUIT_BREAKER", "true").lower() == "true"
    
    # CORS Configuration
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173")

    @property
    def ALLOWED_HOSTS(self) -> List[str]:
        return safe_getenv_list("ALLOWED_HOSTS", "*")

    # Rate Limiting & Security
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    RATE_LIMIT_BURST: int = int(os.getenv("RATE_LIMIT_BURST", "20"))
    MAX_REQUEST_SIZE: int = int(os.getenv("MAX_REQUEST_SIZE", "104857600"))  # 100MB

    # Security Headers
    SECURITY_HEADERS_ENABLED: bool = os.getenv("SECURITY_HEADERS_ENABLED", "true").lower() == "true"
    CSRF_PROTECTION_ENABLED: bool = os.getenv("CSRF_PROTECTION_ENABLED", "true").lower() == "true"

    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        """Parse CORS origins from environment variable"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    # File Upload Configuration
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", str(10 * 1024 * 1024)))  # 10MB default
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB total
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".docx", ".doc", ".txt", ".md", ".html", ".csv", ".xlsx", ".json", ".jpg", ".jpeg", ".png", ".gif", ".webp", ".mp3", ".wav", ".ogg"]

    # Security Scanning Configuration
    ENABLE_VIRUS_SCANNING: bool = os.getenv("ENABLE_VIRUS_SCANNING", "true").lower() == "true"
    CLAMAV_HOST: str = os.getenv("CLAMAV_HOST", "localhost")
    CLAMAV_PORT: int = int(os.getenv("CLAMAV_PORT", "3310"))
    QUARANTINE_DIR: str = os.getenv("QUARANTINE_DIR", "./quarantine")

    # WebSocket Configuration
    WS_HEARTBEAT_INTERVAL: int = int(os.getenv("WS_HEARTBEAT_INTERVAL", "30"))
    WS_MAX_CONNECTIONS: int = int(os.getenv("WS_MAX_CONNECTIONS", "1000"))
    WS_MESSAGE_RATE_LIMIT: int = int(os.getenv("WS_MESSAGE_RATE_LIMIT", "60"))  # messages per minute

    # Storage Configuration
    STORAGE_TYPE: str = "local"  # local, s3, minio, azure
    STORAGE_PATH: str = "./storage"

    # AWS S3 Configuration
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET: Optional[str] = None

    # MinIO Configuration
    MINIO_ENDPOINT: Optional[str] = None
    MINIO_ACCESS_KEY: Optional[str] = None
    MINIO_SECRET_KEY: Optional[str] = None
    MINIO_BUCKET: Optional[str] = None
    MINIO_SECURE: bool = True

    # Azure Storage Configuration
    AZURE_ACCOUNT_NAME: Optional[str] = None
    AZURE_ACCOUNT_KEY: Optional[str] = None
    AZURE_CONTAINER: Optional[str] = None

    # RAG Configuration
    DEFAULT_MAX_CONTEXT_LENGTH: int = 2000
    DEFAULT_SEARCH_LIMIT: int = 5
    DEFAULT_TEMPERATURE: float = 0.7
    DEFAULT_MAX_TOKENS: int = 1000
    DEFAULT_CHUNK_SIZE: int = 1000
    DEFAULT_CHUNK_OVERLAP: int = 200
    MAX_CONTEXT_LENGTH: int = 4000
    SIMILARITY_THRESHOLD: float = 0.7

    # Embedding Configuration
    EMBEDDING_PROVIDER: str = "sentence_transformers"  # sentence_transformers, openai
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-ada-002"
    EMBEDDING_DIMENSION: int = 384

    # Security Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "jwt-secret-key-change-in-production-minimum-32-characters")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
    ALGORITHM: str = "HS256"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # Rate Limiting Configuration
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seconds

    # Error Tracking Configuration
    ENABLE_ERROR_TRACKING: bool = os.getenv("ENABLE_ERROR_TRACKING", "true").lower() == "true"
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")
    ERROR_RETENTION_DAYS: int = int(os.getenv("ERROR_RETENTION_DAYS", "30"))

    # Monitoring Configuration
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    SENTRY_DSN: Optional[str] = None

    # Background Tasks Configuration
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Cache Configuration
    CACHE_TTL: int = 3600  # 1 hour
    CACHE_MAX_SIZE: int = 1000
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
