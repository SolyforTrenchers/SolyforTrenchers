"""
Configuration - Environment variables and settings
Loads configuration from .env file
"""

import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Soly"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False)
    ENVIRONMENT: str = Field(default="production")
    
    # API
    API_HOST: str = Field(default="0.0.0.0")
    API_PORT: int = Field(default=8000)
    CORS_ORIGINS: List[str] = Field(default=["*"])
    
    # Solana
    SOLANA_RPC_URL: str = Field(default="https://api.mainnet-beta.solana.com")
    SOLANA_WS_URL: str = Field(default="wss://api.mainnet-beta.solana.com")
    SOLANA_NETWORK: str = Field(default="mainnet-beta")
    
    # Twitter/X API
    TWITTER_API_KEY: str = Field(default="")
    TWITTER_API_SECRET: str = Field(default="")
    TWITTER_ACCESS_TOKEN: str = Field(default="")
    TWITTER_ACCESS_TOKEN_SECRET: str = Field(default="")
    TWITTER_BEARER_TOKEN: str = Field(default="")
    
    # AI/ML
    OPENAI_API_KEY: str = Field(default="")
    ANTHROPIC_API_KEY: str = Field(default="")
    AI_MODEL: str = Field(default="gpt-4-turbo-preview")
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql://user:password@localhost:5432/soly"
    )
    DATABASE_POOL_SIZE: int = Field(default=10)
    DATABASE_MAX_OVERFLOW: int = Field(default=20)
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    REDIS_CACHE_TTL: int = Field(default=300)  # 5 minutes
    
    # Monitoring
    SENTRY_DSN: str = Field(default="")
    LOG_LEVEL: str = Field(default="INFO")
    
    # Features
    ENABLE_TWITTER_BOT: bool = Field(default=True)
    ENABLE_BLOCKCHAIN_MONITOR: bool = Field(default=True)
    ENABLE_AI_ANALYSIS: bool = Field(default=True)
    
    # Rate Limiting
    MAX_TWEETS_PER_DAY: int = Field(default=50)
    MIN_TWEET_INTERVAL_MINUTES: int = Field(default=15)
    API_RATE_LIMIT: int = Field(default=100)  # requests per minute
    
    # Alert Thresholds
    RUG_RISK_THRESHOLD: float = Field(default=70.0)  # Risk score 0-100
    WHALE_TRANSACTION_THRESHOLD_SOL: float = Field(default=1000.0)
    PRICE_CHANGE_ALERT_THRESHOLD_PCT: float = Field(default=50.0)
    
    # DEX Programs (Solana program IDs)
    RAYDIUM_PROGRAM_ID: str = "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8"
    ORCA_PROGRAM_ID: str = "9W959DqEETiGZocYWCQPaJ6sBmUzgfxXfqGeTEdp3aQP"
    JUPITER_PROGRAM_ID: str = "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()


# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": settings.LOG_LEVEL,
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "detailed",
            "filename": "logs/soly.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        },
    },
    "loggers": {
        "": {
            "level": settings.LOG_LEVEL,
            "handlers": ["console", "file"],
        },
        "uvicorn": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
    },
}
