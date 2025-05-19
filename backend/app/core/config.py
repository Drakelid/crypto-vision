"""
Application configuration settings.
"""
from functools import lru_cache
from typing import List, Optional
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application
    PROJECT_NAME: str = "CryptoVision Dashboard"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    TESTING: bool = False  # Flag to indicate if we're in testing mode
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"  # Change in production
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    ALGORITHM: str = "HS256"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",  # React frontend
        "http://localhost:8000",  # FastAPI backend
    ]
    
    # Database
    POSTGRES_SERVER: str = "db"  # Matches the service name in docker-compose.yml
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "cryptovision"
    DATABASE_URL: Optional[str] = None  # Async database URL
    DATABASE_URI: Optional[str] = None  # Sync database URL (alias for SQLALCHEMY_DATABASE_URI)
    SQLALCHEMY_DATABASE_URI: Optional[str] = None  # Sync database URL
    ALEMBIC_DATABASE_URI: Optional[str] = None  # Sync database URL for Alembic
    
    # TimescaleDB settings
    ENABLE_TIMESCALEDB: bool = True  # Set to False to disable TimescaleDB features
    ENABLE_TIMESCALEDB_COMPRESSION: bool = False  # Set to True to enable TimescaleDB compression
    
    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    
    # Email settings
    SMTP_TLS: bool = True
    SMTP_PORT: int = 587
    SMTP_HOST: str = "smtp.example.com"
    SMTP_USER: str = "your-email@example.com"
    SMTP_PASSWORD: str = "your-email-password"
    EMAILS_FROM_EMAIL: str = "no-reply@cryptovision.app"
    EMAILS_FROM_NAME: str = "CryptoVision"
    
    # API Keys
    COINBASE_API_KEY: str = ""
    COINBASE_API_SECRET: str = ""
    BINANCE_API_KEY: str = ""
    BINANCE_API_SECRET: str = ""
    COINGECKO_API_KEY: str = "your-coin-gecko-api-key"
    ALPHA_VANTAGE_API_KEY: str = "your-alpha-vantage-api-key"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Model settings
    MODEL_DIR: str = "/app/models"
    DEFAULT_MODEL_NAME: str = "transformer"
    DEFAULT_MODEL_VERSION: str = "1.0.0"
    
    # Timezone
    TIMEZONE: str = "UTC"
    
    # Cryptocurrency Data
    SUPPORTED_CRYPTOS: List[str] = [
        "BTC/USDT", 
        "ETH/USDT", 
        "BNB/USDT", 
        "SOL/USDT", 
        "XRP/USDT",
        "ADA/USDT",
        "DOT/USDT"
    ]
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()

# Update database URLs if not set
if settings.DATABASE_URL is None:
    settings.DATABASE_URL = (
        f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@"
        f"{settings.POSTGRES_SERVER}/{settings.POSTGRES_DB}"
    )

if settings.SQLALCHEMY_DATABASE_URI is None:
    settings.SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@"
        f"{settings.POSTGRES_SERVER}/{settings.POSTGRES_DB}"
    )

if settings.ALEMBIC_DATABASE_URI is None:
    settings.ALEMBIC_DATABASE_URI = settings.SQLALCHEMY_DATABASE_URI

# Set DATABASE_URI to match SQLALCHEMY_DATABASE_URI for backward compatibility
settings.DATABASE_URI = settings.SQLALCHEMY_DATABASE_URI

# Print database URLs for debugging
print(f"DATABASE_URL: {settings.DATABASE_URL}")
print(f"SQLALCHEMY_DATABASE_URI: {settings.SQLALCHEMY_DATABASE_URI}")
print(f"ALEMBIC_DATABASE_URI: {settings.ALEMBIC_DATABASE_URI}")

# Ensure the database URL is set
if not settings.DATABASE_URL:
    raise ValueError("DATABASE_URL must be set")

# Ensure SQLAlchemy URL is set
if not settings.SQLALCHEMY_DATABASE_URI:
    raise ValueError("SQLALCHEMY_DATABASE_URI must be set")

# Ensure Alembic URL is set
if not settings.ALEMBIC_DATABASE_URI:
    raise ValueError("ALEMBIC_DATABASE_URI must be set")
