"""
SQLAlchemy Database Models
Complete schema for StickerCraft
"""
from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime,
    ForeignKey, Text, Float, Enum as SQLEnum, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

def generate_uuid():
    """Generate UUID string"""
    return str(uuid.uuid4())

class User(Base):
    """User account"""
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, nullable=False, index=True)
    password_hash = Column(String, nullable=False)

    # Subscription & Credits
    tier = Column(String, default="free")  # free, creator, pro
    credits = Column(Integer, default=50)
    monthly_exports_used = Column(Integer, default=0)
    monthly_credits_used = Column(Integer, default=0)

    # Subscription Details
    stripe_customer_id = Column(String, nullable=True)
    stripe_subscription_id = Column(String, nullable=True)
    revenuecat_subscriber_id = Column(String, nullable=True)
    subscription_expires_at = Column(DateTime, nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    email_verified_at = Column(DateTime, nullable=True)

    # Preferences
    preferences = Column(JSON, default=dict)  # Theme, language, etc.

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)

    # Relationships
    stickers = relationship("Sticker", back_populates="user", cascade="all, delete-orphan")
    packs = relationship("Pack", back_populates="user", cascade="all, delete-orphan")
    generations = relationship("Generation", back_populates="user", cascade="all, delete-orphan")
    analytics_events = relationship("AnalyticsEvent", back_populates="user")

class Sticker(Base):
    """Generated sticker"""
    __tablename__ = "stickers"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

    # Image Data
    image_url = Column(String, nullable=False)
    thumbnail_url = Column(String)
    file_size = Column(Integer)  # bytes
    width = Column(Integer)
    height = Column(Integer)

    # Generation Info
    prompt = Column(Text)
    style = Column(String)  # cartoon, anime, realistic, etc.
    generation_type = Column(String)  # text_to_image, image_to_sticker, character

    # Metadata
    metadata = Column(JSON, default=dict)  # Store additional info

    # Stats
    export_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)

    # Status
    is_public = Column(Boolean, default=False)
    is_flagged = Column(Boolean, default=False)
    moderation_status = Column(String, default="pending")  # pending, approved, rejected

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="stickers")
    exports = relationship("Export", back_populates="sticker", cascade="all, delete-orphan")

class Pack(Base):
    """Sticker pack"""
    __tablename__ = "packs"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

    # Pack Details
    name = Column(String, nullable=False)
    description = Column(Text)
    platform = Column(String, nullable=False)  # whatsapp, telegram, signal, imessage
    tray_icon_url = Column(String)

    # Stickers (stored as JSON array of sticker IDs)
    sticker_ids = Column(JSON, default=list)

    # Publishing
    is_published = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    category = Column(String)  # festival, emotions, work, etc.

    # Marketplace
    is_marketplace_item = Column(Boolean, default=False)
    price = Column(Integer, default=0)  # in credits or currency
    download_count = Column(Integer, default=0)
    rating = Column(Float, default=0.0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="packs")

class Generation(Base):
    """AI generation job tracking"""
    __tablename__ = "generations"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

    # Job Details
    job_type = Column(String, nullable=False)  # text_to_image, image_to_sticker, etc.
    status = Column(String, default="pending")  # pending, processing, completed, failed

    # Input
    prompt = Column(Text)
    style = Column(String)
    input_data = Column(JSON, default=dict)  # Additional parameters

    # Output
    result_sticker_ids = Column(JSON, default=list)  # List of generated sticker IDs
    error_message = Column(Text, nullable=True)

    # Performance Metrics
    processing_time = Column(Float)  # seconds
    credits_used = Column(Integer, default=1)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="generations")

class Export(Base):
    """Sticker export tracking"""
    __tablename__ = "exports"

    id = Column(String, primary_key=True, default=generate_uuid)
    sticker_id = Column(String, ForeignKey("stickers.id"), nullable=False, index=True)

    # Export Details
    platform = Column(String, nullable=False)  # whatsapp, telegram, signal, imessage
    format = Column(String, nullable=False)  # webp, png, webm, apng
    file_url = Column(String, nullable=False)
    file_size = Column(Integer)  # bytes

    # Compliance
    is_compliant = Column(Boolean, default=True)
    warnings = Column(JSON, default=list)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    sticker = relationship("Sticker", back_populates="exports")

class Referral(Base):
    """Referral tracking"""
    __tablename__ = "referrals"

    id = Column(String, primary_key=True, default=generate_uuid)
    code = Column(String, unique=True, nullable=False, index=True)
    referrer_user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

    # Stats
    total_uses = Column(Integer, default=0)
    successful_signups = Column(Integer, default=0)
    subscription_conversions = Column(Integer, default=0)
    total_credits_earned = Column(Integer, default=0)

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    redemptions = relationship("ReferralRedemption", back_populates="referral")

class ReferralRedemption(Base):
    """Referral redemption tracking"""
    __tablename__ = "referral_redemptions"

    id = Column(String, primary_key=True, default=generate_uuid)
    referral_id = Column(String, ForeignKey("referrals.id"), nullable=False, index=True)
    referee_user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

    # Rewards
    referrer_credits_awarded = Column(Integer, default=0)
    referee_credits_awarded = Column(Integer, default=0)
    subscription_bonus_claimed = Column(Boolean, default=False)
    subscription_bonus_date = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    referral = relationship("Referral", back_populates="redemptions")

class AnalyticsEvent(Base):
    """Analytics event tracking"""
    __tablename__ = "analytics_events"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)

    # Event Details
    event_type = Column(String, nullable=False, index=True)  # page_view, sticker_created, export, etc.
    event_category = Column(String, index=True)  # engagement, conversion, revenue
    event_data = Column(JSON, default=dict)  # Additional data

    # Session
    session_id = Column(String, index=True)
    device_type = Column(String)  # mobile, tablet, desktop
    platform = Column(String)  # ios, android, web

    # Location (optional)
    country = Column(String)
    city = Column(String)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="analytics_events")

class ContentReport(Base):
    """Content moderation reports"""
    __tablename__ = "content_reports"

    id = Column(String, primary_key=True, default=generate_uuid)
    sticker_id = Column(String, ForeignKey("stickers.id"), nullable=False, index=True)
    reporter_user_id = Column(String, ForeignKey("users.id"), nullable=True)

    # Report Details
    report_type = Column(String, nullable=False)  # nsfw, spam, copyright, other
    description = Column(Text)

    # Moderation
    status = Column(String, default="pending")  # pending, reviewed, action_taken, dismissed
    moderator_notes = Column(Text)
    action_taken = Column(String)  # removed, warning, banned, none

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    reviewed_at = Column(DateTime, nullable=True)

class ApiKey(Base):
    """API keys for enterprise users"""
    __tablename__ = "api_keys"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

    # Key Details
    key = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)

    # Limits
    rate_limit = Column(Integer, default=60)  # requests per minute
    monthly_quota = Column(Integer, default=1000)
    current_usage = Column(Integer, default=0)

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
