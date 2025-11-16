"""
User and Authentication Models
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: str
    tier: Literal["free", "creator", "pro"] = "free"
    credits: int = 50
    monthly_exports_used: int = 0
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User

class TokenData(BaseModel):
    user_id: Optional[str] = None

# Subscription Models
class SubscriptionTier(BaseModel):
    name: Literal["free", "creator", "pro"]
    price: int
    credits_per_month: int
    static_exports: Optional[int] = None
    animated_exports: Optional[int] = None
    features: list[str]

class UserSubscription(BaseModel):
    user_id: str
    tier: Literal["free", "creator", "pro"]
    stripe_subscription_id: Optional[str] = None
    revenuecat_subscriber_id: Optional[str] = None
    expires_at: Optional[datetime] = None
    auto_renew: bool = True
    created_at: datetime
    updated_at: datetime
