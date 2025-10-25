"""
Amazon Purchase Analytics System - Settings
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Amazon Purchase Analytics"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    POSTGRES_PASSWORD: Optional[str] = "postgres"
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/amazon_analytics"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # AI Provider Settings
    AI_PROVIDER: str = "gemini"  # gemini or openai
    
    # Gemini API (Google AI)
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.0-flash-exp"
    
    # OpenAI (alternative)
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    # File paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    UPLOAD_DIR: Path = DATA_DIR / "uploads"
    PROCESSED_DIR: Path = DATA_DIR / "processed"
    EXPORT_DIR: Path = DATA_DIR / "exports"
    CACHE_DIR: Path = DATA_DIR / "cache"
    
    # CSV Processing
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: list = [".csv"]
    
    # Analysis
    CATEGORY_CONFIDENCE_THRESHOLD: float = 0.7
    IMPULSE_BUY_THRESHOLD_DAYS: int = 7
    IMPULSE_BUY_COUNT: int = 3
    
    # External Integration
    NOTION_API_KEY: Optional[str] = None
    NOTION_DATABASE_ID: Optional[str] = None
    
    # Email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: Optional[str] = None
    EMAIL_TO: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"  # Allow extra fields from environment


# Create settings instance
settings = Settings()

# Ensure directories exist
for directory in [
    settings.UPLOAD_DIR,
    settings.PROCESSED_DIR,
    settings.EXPORT_DIR,
    settings.CACHE_DIR,
]:
    directory.mkdir(parents=True, exist_ok=True)

