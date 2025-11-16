"""
User Management API Endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict
import uuid
import logging
from datetime import datetime

from app.models.user import (
    UserCreate,
    UserLogin,
    User,
    Token,
    CreditBalance
)
from app.models.sticker import CreditBalance as StickerCreditBalance
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

# In-memory storage for MVP (replace with database)
users_db = {}
credits_db = {}

@router.post("/register", response_model=Token)
async def register(user_data: UserCreate):
    """
    Register new user

    Creates account with free tier (50 credits)
    """
    try:
        # Check if email exists
        if any(u.email == user_data.email for u in users_db.values()):
            raise HTTPException(status_code=400, detail="Email already registered")

        user_id = str(uuid.uuid4())
        now = datetime.utcnow()

        user = User(
            id=user_id,
            email=user_data.email,
            username=user_data.username,
            tier="free",
            credits=settings.FREE_TIER_CREDITS,
            monthly_exports_used=0,
            is_active=True,
            created_at=now,
            updated_at=now
        )

        users_db[user_id] = user

        # Initialize credits
        credits_db[user_id] = {
            "credits": settings.FREE_TIER_CREDITS,
            "tier": "free",
            "monthly_exports_used": 0,
            "monthly_exports_limit": settings.FREE_TIER_STATIC_EXPORTS,
            "credits_used_this_month": 0
        }

        # TODO: Generate actual JWT token
        access_token = f"token_{user_id}"

        logger.info(f"User registered: {user.email}")

        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """
    User login

    Returns JWT token for authentication
    """
    try:
        # Find user by email
        user = next(
            (u for u in users_db.values() if u.email == credentials.email),
            None
        )

        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # TODO: Verify password hash

        # TODO: Generate actual JWT token
        access_token = f"token_{user.id}"

        logger.info(f"User logged in: {user.email}")

        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/me", response_model=User)
async def get_current_user():
    """Get current user profile"""
    # TODO: Get from JWT token
    # For MVP, return first user or demo user
    if users_db:
        return list(users_db.values())[0]

    # Return demo user
    return User(
        id="demo",
        email="demo@stickercraft.com",
        username="demo_user",
        tier="free",
        credits=50,
        monthly_exports_used=0,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

@router.get("/credits", response_model=StickerCreditBalance)
async def get_credits():
    """
    Get user credit balance and usage
    """
    try:
        # TODO: Get from JWT token
        user_id = "demo"

        credits = credits_db.get(user_id, {
            "credits": 50,
            "tier": "free",
            "monthly_exports_used": 0,
            "monthly_exports_limit": 30,
            "credits_used_this_month": 0
        })

        return StickerCreditBalance(
            user_id=user_id,
            credits=credits["credits"],
            tier=credits["tier"],
            monthly_exports_used=credits["monthly_exports_used"],
            monthly_exports_limit=credits["monthly_exports_limit"],
            credits_used_this_month=credits["credits_used_this_month"]
        )

    except Exception as e:
        logger.error(f"Error getting credits: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/credits/deduct")
async def deduct_credits(amount: int = 1):
    """
    Deduct credits from user balance

    Used internally by generation endpoints
    """
    try:
        # TODO: Get from JWT token
        user_id = "demo"

        if user_id not in credits_db:
            raise HTTPException(status_code=404, detail="User credits not found")

        credits = credits_db[user_id]

        if credits["credits"] < amount:
            raise HTTPException(status_code=402, detail="Insufficient credits")

        credits["credits"] -= amount
        credits["credits_used_this_month"] += amount

        # Update user
        if user_id in users_db:
            users_db[user_id].credits = credits["credits"]

        return {
            "remaining_credits": credits["credits"],
            "deducted": amount,
            "message": f"Deducted {amount} credit(s)"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deducting credits: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tiers")
async def get_subscription_tiers():
    """
    Get available subscription tiers
    """
    return {
        "tiers": [
            {
                "name": "free",
                "price": 0,
                "credits_per_month": 50,
                "static_exports": 30,
                "animated_exports": 0,
                "features": [
                    "30 static exports/month",
                    "Basic styles",
                    "1 active pack"
                ]
            },
            {
                "name": "creator",
                "price": 199,
                "credits_per_month": 200,
                "static_exports": None,  # Unlimited
                "animated_exports": 50,
                "features": [
                    "Unlimited static exports",
                    "200 AI credits/month",
                    "50 animated exports/month",
                    "Custom fonts"
                ]
            },
            {
                "name": "pro",
                "price": 499,
                "credits_per_month": 1000,
                "static_exports": None,  # Unlimited
                "animated_exports": None,  # Unlimited
                "features": [
                    "1,000 AI credits/month",
                    "LoRA blending sliders",
                    "Marketplace seller access",
                    "Priority queue"
                ]
            }
        ]
    }
