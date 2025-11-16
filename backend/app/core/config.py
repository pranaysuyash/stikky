"""
Application Configuration
Centralized settings management using Pydantic
"""
from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Project Info
    PROJECT_NAME: str = "StickerCraft API"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost",
    ]

    # AI Services
    FAL_KEY: str = ""
    REPLICATE_API_TOKEN: str = ""

    # Default AI Models
    TEXT_TO_IMAGE_MODEL: str = "fal-ai/flux/schnell"
    BACKGROUND_REMOVAL_MODEL: str = "rembg"

    # Storage
    STORAGE_TYPE: str = "local"  # local, s3, r2, cloudinary
    S3_BUCKET: str = ""
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""
    S3_REGION: str = "us-east-1"
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    # Local Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_DB: int = 0

    # Database
    DATABASE_URL: str = "sqlite:///./stikkercraft.db"

    # Payments
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    REVENUECAT_API_KEY: str = ""

    # Free Tier Limits
    FREE_TIER_STATIC_EXPORTS: int = 30
    FREE_TIER_CREDITS: int = 50

    # Subscription Tiers
    CREATOR_TIER_PRICE: int = 199  # INR
    CREATOR_TIER_CREDITS: int = 200
    PRO_TIER_PRICE: int = 499  # INR
    PRO_TIER_CREDITS: int = 1000

    # Platform Export Limits (bytes)
    WHATSAPP_STATIC_LIMIT: int = 100 * 1024  # 100KB
    WHATSAPP_ANIMATED_LIMIT: int = 500 * 1024  # 500KB
    TELEGRAM_STATIC_LIMIT: int = 512 * 1024  # 512KB
    TELEGRAM_ANIMATED_LIMIT: int = 256 * 1024  # 256KB
    IMESSAGE_WARNING_LIMIT: int = 1024 * 1024  # 1MB

    # Sticker Dimensions
    STICKER_SIZE: int = 512  # 512x512
    TRAY_ICON_SIZE: int = 96  # 96x96

    # Animation Limits
    MAX_ANIMATION_DURATION: int = 3  # seconds
    DEFAULT_FPS: int = 12
    MAX_FPS: int = 30

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = True

# Initialize settings
settings = Settings()

# Create upload directory if it doesn't exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
