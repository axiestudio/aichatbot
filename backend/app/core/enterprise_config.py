"""
Enterprise Configuration Management
Netflix/Google-style configuration with environment-specific settings
"""

import os
from typing import Dict, Any, List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from enum import Enum


class Environment(str, Enum):
    """Environment types"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(str, Enum):
    """Log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class EnterpriseSettings(BaseSettings):
    """
    Enterprise-grade configuration settings
    """
    
    # Application Settings
    APP_NAME: str = Field(default="AI Chatbot Platform", env="APP_NAME")
    APP_VERSION: str = Field(default="2.0.0", env="APP_VERSION")
    ENVIRONMENT: Environment = Field(default=Environment.DEVELOPMENT, env="ENVIRONMENT")
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # Server Settings
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    WORKERS: int = Field(default=1, env="WORKERS")
    
    # Database Settings
    DATABASE_URL: str = Field(env="DATABASE_URL")
    DATABASE_POOL_SIZE: int = Field(default=20, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=30, env="DATABASE_MAX_OVERFLOW")
    DATABASE_POOL_TIMEOUT: int = Field(default=30, env="DATABASE_POOL_TIMEOUT")
    DATABASE_POOL_RECYCLE: int = Field(default=3600, env="DATABASE_POOL_RECYCLE")
    
    # Redis/Cache Settings
    REDIS_URL: Optional[str] = Field(default=None, env="REDIS_URL")
    CACHE_TTL: int = Field(default=300, env="CACHE_TTL")
    CACHE_MAX_SIZE: int = Field(default=10000, env="CACHE_MAX_SIZE")
    
    # Security Settings
    SECRET_KEY: str = Field(env="SECRET_KEY")
    JWT_SECRET_KEY: str = Field(env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    JWT_EXPIRATION_HOURS: int = Field(default=24, env="JWT_EXPIRATION_HOURS")
    
    # CORS Settings
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        env="ALLOWED_ORIGINS"
    )
    ALLOWED_HOSTS: List[str] = Field(
        default=["localhost", "127.0.0.1"],
        env="ALLOWED_HOSTS"
    )
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(default=60, env="RATE_LIMIT_WINDOW")
    RATE_LIMIT_BURST: int = Field(default=20, env="RATE_LIMIT_BURST")
    
    # File Upload Settings
    MAX_FILE_SIZE_MB: int = Field(default=50, env="MAX_FILE_SIZE_MB")
    UPLOAD_DIR: str = Field(default="uploads", env="UPLOAD_DIR")
    ALLOWED_FILE_TYPES: List[str] = Field(
        default=["pdf", "txt", "docx", "md", "csv"],
        env="ALLOWED_FILE_TYPES"
    )
    
    # AI Provider Settings
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    DEFAULT_AI_PROVIDER: str = Field(default="openai", env="DEFAULT_AI_PROVIDER")
    DEFAULT_AI_MODEL: str = Field(default="gpt-3.5-turbo", env="DEFAULT_AI_MODEL")
    AI_REQUEST_TIMEOUT: int = Field(default=30, env="AI_REQUEST_TIMEOUT")
    AI_MAX_RETRIES: int = Field(default=3, env="AI_MAX_RETRIES")
    
    # Observability Settings
    ENABLE_TRACING: bool = Field(default=True, env="ENABLE_TRACING")
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")
    ENABLE_LOGGING: bool = Field(default=True, env="ENABLE_LOGGING")
    LOG_LEVEL: LogLevel = Field(default=LogLevel.INFO, env="LOG_LEVEL")
    
    # Distributed Tracing
    JAEGER_ENDPOINT: Optional[str] = Field(default=None, env="JAEGER_ENDPOINT")
    JAEGER_HOST: str = Field(default="localhost", env="JAEGER_HOST")
    JAEGER_PORT: int = Field(default=6831, env="JAEGER_PORT")
    TRACE_SAMPLING_RATE: float = Field(default=0.1, env="TRACE_SAMPLING_RATE")
    
    # Metrics and Monitoring
    PROMETHEUS_ENABLED: bool = Field(default=True, env="PROMETHEUS_ENABLED")
    METRICS_PORT: int = Field(default=9090, env="METRICS_PORT")
    HEALTH_CHECK_INTERVAL: int = Field(default=30, env="HEALTH_CHECK_INTERVAL")
    
    # Event Streaming
    ENABLE_EVENT_STREAMING: bool = Field(default=True, env="ENABLE_EVENT_STREAMING")
    EVENT_STREAM_MAX_SIZE: int = Field(default=100000, env="EVENT_STREAM_MAX_SIZE")
    EVENT_RETENTION_HOURS: int = Field(default=24, env="EVENT_RETENTION_HOURS")
    
    # Chaos Engineering
    ENABLE_CHAOS_ENGINEERING: bool = Field(default=False, env="ENABLE_CHAOS_ENGINEERING")
    CHAOS_SAFETY_MODE: bool = Field(default=True, env="CHAOS_SAFETY_MODE")
    CHAOS_EXPERIMENT_PROBABILITY: float = Field(default=0.01, env="CHAOS_EXPERIMENT_PROBABILITY")
    
    # Zero Trust Security
    ENABLE_ZERO_TRUST: bool = Field(default=True, env="ENABLE_ZERO_TRUST")
    SECURITY_THREAT_THRESHOLD: float = Field(default=0.7, env="SECURITY_THREAT_THRESHOLD")
    SECURITY_BLOCK_THRESHOLD: float = Field(default=0.9, env="SECURITY_BLOCK_THRESHOLD")
    DEVICE_FINGERPRINTING: bool = Field(default=True, env="DEVICE_FINGERPRINTING")
    BEHAVIORAL_ANALYSIS: bool = Field(default=True, env="BEHAVIORAL_ANALYSIS")
    
    # WebSocket Settings
    MAX_WEBSOCKET_CONNECTIONS: int = Field(default=1000, env="MAX_WEBSOCKET_CONNECTIONS")
    WEBSOCKET_HEARTBEAT_INTERVAL: int = Field(default=30, env="WEBSOCKET_HEARTBEAT_INTERVAL")
    WEBSOCKET_TIMEOUT: int = Field(default=300, env="WEBSOCKET_TIMEOUT")
    
    # Auto-scaling Settings
    ENABLE_AUTO_SCALING: bool = Field(default=False, env="ENABLE_AUTO_SCALING")
    MIN_INSTANCES: int = Field(default=1, env="MIN_INSTANCES")
    MAX_INSTANCES: int = Field(default=10, env="MAX_INSTANCES")
    SCALE_UP_THRESHOLD: float = Field(default=0.8, env="SCALE_UP_THRESHOLD")
    SCALE_DOWN_THRESHOLD: float = Field(default=0.3, env="SCALE_DOWN_THRESHOLD")
    
    # External Services
    WEBHOOK_URL: Optional[str] = Field(default=None, env="WEBHOOK_URL")
    SLACK_WEBHOOK_URL: Optional[str] = Field(default=None, env="SLACK_WEBHOOK_URL")
    EMAIL_SMTP_HOST: Optional[str] = Field(default=None, env="EMAIL_SMTP_HOST")
    EMAIL_SMTP_PORT: int = Field(default=587, env="EMAIL_SMTP_PORT")
    EMAIL_USERNAME: Optional[str] = Field(default=None, env="EMAIL_USERNAME")
    EMAIL_PASSWORD: Optional[str] = Field(default=None, env="EMAIL_PASSWORD")
    
    # Admin Settings
    ADMIN_USERNAME: str = Field(env="ADMIN_USERNAME")
    ADMIN_PASSWORD: str = Field(env="ADMIN_PASSWORD")
    SUPER_ADMIN_ENABLED: bool = Field(default=True, env="SUPER_ADMIN_ENABLED")
    
    # Feature Flags
    ENABLE_RAG: bool = Field(default=True, env="ENABLE_RAG")
    ENABLE_DOCUMENT_UPLOAD: bool = Field(default=True, env="ENABLE_DOCUMENT_UPLOAD")
    ENABLE_MULTI_TENANT: bool = Field(default=True, env="ENABLE_MULTI_TENANT")
    ENABLE_ANALYTICS: bool = Field(default=True, env="ENABLE_ANALYTICS")
    ENABLE_CACHING: bool = Field(default=True, env="ENABLE_CACHING")
    
    # Performance Settings
    REQUEST_TIMEOUT: int = Field(default=30, env="REQUEST_TIMEOUT")
    RESPONSE_TIMEOUT: int = Field(default=60, env="RESPONSE_TIMEOUT")
    MAX_CONCURRENT_REQUESTS: int = Field(default=100, env="MAX_CONCURRENT_REQUESTS")
    
    # Backup and Recovery
    BACKUP_ENABLED: bool = Field(default=True, env="BACKUP_ENABLED")
    BACKUP_INTERVAL_HOURS: int = Field(default=24, env="BACKUP_INTERVAL_HOURS")
    BACKUP_RETENTION_DAYS: int = Field(default=30, env="BACKUP_RETENTION_DAYS")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        
    def get_environment_config(self) -> Dict[str, Any]:
        """Get environment-specific configuration"""
        base_config = {
            "app_name": self.APP_NAME,
            "version": self.APP_VERSION,
            "environment": self.ENVIRONMENT.value,
            "debug": self.DEBUG
        }
        
        if self.ENVIRONMENT == Environment.PRODUCTION:
            return {
                **base_config,
                "log_level": LogLevel.INFO,
                "enable_chaos_engineering": False,
                "chaos_safety_mode": True,
                "debug": False,
                "trace_sampling_rate": 0.01,  # Lower sampling in production
                "rate_limit_requests": 1000,  # Higher limits in production
                "max_concurrent_requests": 500
            }
        elif self.ENVIRONMENT == Environment.STAGING:
            return {
                **base_config,
                "log_level": LogLevel.DEBUG,
                "enable_chaos_engineering": True,
                "chaos_safety_mode": True,
                "trace_sampling_rate": 0.1,
                "rate_limit_requests": 500
            }
        else:  # Development
            return {
                **base_config,
                "log_level": LogLevel.DEBUG,
                "enable_chaos_engineering": True,
                "chaos_safety_mode": True,
                "debug": True,
                "trace_sampling_rate": 1.0,  # Full tracing in development
                "rate_limit_requests": 100
            }
            
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration"""
        return {
            "enable_zero_trust": self.ENABLE_ZERO_TRUST,
            "threat_threshold": self.SECURITY_THREAT_THRESHOLD,
            "block_threshold": self.SECURITY_BLOCK_THRESHOLD,
            "device_fingerprinting": self.DEVICE_FINGERPRINTING,
            "behavioral_analysis": self.BEHAVIORAL_ANALYSIS,
            "jwt_expiration_hours": self.JWT_EXPIRATION_HOURS,
            "rate_limiting": {
                "requests": self.RATE_LIMIT_REQUESTS,
                "window": self.RATE_LIMIT_WINDOW,
                "burst": self.RATE_LIMIT_BURST
            }
        }
        
    def get_observability_config(self) -> Dict[str, Any]:
        """Get observability configuration"""
        return {
            "enable_tracing": self.ENABLE_TRACING,
            "enable_metrics": self.ENABLE_METRICS,
            "enable_logging": self.ENABLE_LOGGING,
            "log_level": self.LOG_LEVEL.value,
            "jaeger": {
                "endpoint": self.JAEGER_ENDPOINT,
                "host": self.JAEGER_HOST,
                "port": self.JAEGER_PORT,
                "sampling_rate": self.TRACE_SAMPLING_RATE
            },
            "prometheus": {
                "enabled": self.PROMETHEUS_ENABLED,
                "port": self.METRICS_PORT
            },
            "event_streaming": {
                "enabled": self.ENABLE_EVENT_STREAMING,
                "max_size": self.EVENT_STREAM_MAX_SIZE,
                "retention_hours": self.EVENT_RETENTION_HOURS
            }
        }
        
    def get_ai_config(self) -> Dict[str, Any]:
        """Get AI configuration"""
        return {
            "default_provider": self.DEFAULT_AI_PROVIDER,
            "default_model": self.DEFAULT_AI_MODEL,
            "request_timeout": self.AI_REQUEST_TIMEOUT,
            "max_retries": self.AI_MAX_RETRIES,
            "providers": {
                "openai": {
                    "api_key": self.OPENAI_API_KEY,
                    "enabled": bool(self.OPENAI_API_KEY)
                },
                "anthropic": {
                    "api_key": self.ANTHROPIC_API_KEY,
                    "enabled": bool(self.ANTHROPIC_API_KEY)
                }
            }
        }


# Global enterprise settings instance
enterprise_settings = EnterpriseSettings()
