import secrets
import warnings
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List


def generate_secret_key() -> str:
    """Generate a secure random secret key with warning"""
    key = secrets.token_urlsafe(32)
    warnings.warn(
        "SECRET_KEY not set in environment. Using auto-generated key. "
        "This is not suitable for production!",
        RuntimeWarning
    )
    return key


class Settings(BaseSettings):
    """Application settings"""

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_PREFIX: str = "/api"

    # Database
    DATABASE_URL: str = "postgresql://trader:password@localhost:5432/trading_journal"

    # Demo mode (no Kafka, use asyncio Queue)
    DEMO_MODE: bool = True

    # ML Models
    NLP_MODEL_NAME: str = "ProsusAI/finbert"
    USE_GPU: bool = False

    # Security - Set SECRET_KEY via environment variable in production
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    JWT_ISSUER: str = "smart-trading-journal"
    JWT_AUDIENCE: str = "smart-trading-journal-api"

    # CORS - Configure these for production
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="allow"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Generate secret key if not provided
        if not self.SECRET_KEY:
            object.__setattr__(self, 'SECRET_KEY', generate_secret_key())


settings = Settings()
