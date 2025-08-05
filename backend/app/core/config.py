from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # FastAPI Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "CHANGE-THIS-IN-PRODUCTION-MINIMUM-32-CHARACTERS")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Security Configuration
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "CHANGE-THIS-JWT-SECRET-MINIMUM-32-CHARACTERS")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # Admin Configuration
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "CHANGE-THIS-ADMIN-PASSWORD")
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "admin@localhost")
    
    # Database Configuration
    DATABASE_URL: Optional[str] = None
    
    # Supabase Configuration
    SUPABASE_URL: Optional[str] = None
    SUPABASE_ANON_KEY: Optional[str] = None
    SUPABASE_SERVICE_KEY: Optional[str] = None
    
    # AI Provider Configuration
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379"
    
    # CORS Configuration
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173")
    ALLOWED_HOSTS: List[str] = os.getenv("ALLOWED_HOSTS", "*").split(",")

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
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".docx", ".doc", ".txt", ".md", ".html", ".csv", ".xlsx", ".json"]

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
    JWT_SECRET_KEY: str = "jwt-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

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
