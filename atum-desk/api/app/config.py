"""
ATUM DESK - FastAPI Application Configuration
"""
from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, PostgresDsn, RedisDsn


class Settings(BaseSettings):
    """Application settings loaded from environment"""
    
    # Application
    APP_NAME: str = "ATUM DESK"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False)
    ENVIRONMENT: str = Field(default="production")
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WEBSOCKET_PORT: int = 8001
    
    # Database
    DATABASE_URL: PostgresDsn = Field(
        default="postgresql+psycopg://atum:atum@localhost:5432/atum_desk"
    )
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Redis
    REDIS_URL: RedisDsn = Field(default="redis://localhost:6379/1")
    
    # Security
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 8  # 8 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_MIN_LENGTH: int = 8
    
    # JWT
    ALGORITHM: str = "HS256"
    
    # 2FA
    TOTP_ISSUER_NAME: str = "ATUM DESK"
    
    # File Upload
    UPLOAD_DIR: str = "/data/ATUM DESK/atum-desk/data/uploads"
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: List[str] = Field(
        default=[
            # Images
            "jpg", "jpeg", "png", "gif", "svg", "webp",
            # Documents
            "pdf", "doc", "docx", "txt", "rtf",
            # Spreadsheets
            "xls", "xlsx", "csv",
            # Archives
            "zip", "tar", "gz", "bz2", "7z",
            # Code
            "json", "xml", "yaml", "yml", "log"
        ]
    )
    
    # Email (SMTP)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_TLS: bool = True
    SMTP_FROM: str = "support@atum.desk"
    
    # Email (IMAP)
    IMAP_HOST: Optional[str] = None
    IMAP_PORT: int = 993
    IMAP_USER: Optional[str] = None
    IMAP_PASSWORD: Optional[str] = None
    IMAP_SSL: bool = True
    IMAP_FOLDER: str = "INBOX"
    EMAIL_POLL_INTERVAL: int = 60  # seconds
    
    # AI (Ollama)
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "ATUM-DESK-AI:latest"
    OLLAMA_EMBEDDING_MODEL: str = "nomic-embed-text:latest"
    OLLAMA_TIMEOUT: int = 30
    AI_ENABLED: bool = True
    # RAG Indexing: Disabled by default for stability. Enable via env var for Phase 3.
    # When enabled, tickets are indexed for semantic search via background task.
    RAG_INDEX_ON_TICKET_CREATE: bool = Field(default=False)
    
    # Rate Limiting
    RATE_LIMIT_LOGIN: int = 5  # attempts per 15 minutes
    RATE_LIMIT_API: int = 100  # requests per minute
    RATE_LIMIT_TICKET_CREATE: int = 10  # tickets per hour
    
    # SLA
    SLA_ENABLED: bool = True
    SLA_CHECK_INTERVAL_MINUTES: int = 5
    
    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = 30  # seconds
    WS_MAX_CONNECTIONS: int = 1000
    
    # Slack
    SLACK_WEBHOOK_URL: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Frontend URL (for CORS and emails)
    FRONTEND_URL: str = "https://localhost"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
