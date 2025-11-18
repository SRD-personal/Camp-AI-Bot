"""
Application configuration management using Pydantic Settings
"""
from typing import List, Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    APP_NAME: str = "KIT CampusAI"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_VERSION: str = "v1"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 0

    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Google OAuth
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str

    # Google Gemini
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-pro"
    GEMINI_EMBEDDING_MODEL: str = "models/embedding-001"

    # Vector Database
    PGVECTOR_DIMENSION: int = 768
    SIMILARITY_THRESHOLD: float = 0.5

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000

    # File Upload
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_FILE_TYPES: str = ".pdf,.docx,.txt"
    UPLOAD_DIR: str = "uploads"

    # Web Scraping
    KIT_WEBSITE_URL: str = "https://kitcbe.com"
    SCRAPE_MAX_PAGES: int = 500
    SCRAPE_TIMEOUT_SECONDS: int = 30
    USER_AGENT: str = "KIT-CampusAI/1.0"

    # Guardrails
    MAX_QUERY_LENGTH: int = 2000
    ENABLE_INPUT_GUARDRAILS: bool = True
    ENABLE_OUTPUT_GUARDRAILS: bool = True

    # Logging
    LOG_LEVEL: str = "INFO"
    SENTRY_DSN: Optional[str] = None

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8080"
    CORS_ALLOW_CREDENTIALS: bool = True

    # Redis
    REDIS_URL: Optional[str] = "redis://localhost:6379/0"

    # WebSocket
    SOCKETIO_CORS_ORIGINS: str = "*"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

    @field_validator('DATABASE_URL', mode='before')
    @classmethod
    def convert_database_url_to_async(cls, v: str) -> str:
        """Convert standard PostgreSQL URL to asyncpg format for async operations"""
        if isinstance(v, str) and v.startswith('postgresql://') and '+asyncpg' not in v:
            return v.replace('postgresql://', 'postgresql+asyncpg://')
        return v

    @field_validator('CORS_ORIGINS')
    @classmethod
    def parse_cors_origins(cls, v: str) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v

    @property
    def allowed_file_extensions(self) -> List[str]:
        """Get list of allowed file extensions"""
        return [ext.strip() for ext in self.ALLOWED_FILE_TYPES.split(',')]

    @property
    def max_file_size_bytes(self) -> int:
        """Get max file size in bytes"""
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL for Alembic (removes +asyncpg if present)"""
        url = self.DATABASE_URL
        # Remove +asyncpg for sync operations (Alembic migrations)
        if '+asyncpg' in url:
            return url.replace('+asyncpg', '')
        # If URL is plain postgresql://, it's already sync-compatible
        return url


# Global settings instance
settings = Settings()
