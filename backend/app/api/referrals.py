"""
Referral System API
Viral growth engine with rewards
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
import logging
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

# In-memory storage (replace with database)
referrals_db = {}
user_referrals = {}

class ReferralCode(BaseModel):
    code: str
    user_id: str
    uses: int = 0
    rewards_earned: int = 0
    created_at: str

class ReferralReward(BaseModel):
    type: str  # "signup", "subscription"
    credits: int
    description: str

class ReferralStats(BaseModel):
    total_referrals: int
    successful_signups: int
    subscription_conversions: int
    total_credits_earned: int
    referral_code: str

# Reward Configuration
REWARD_CONFIG = {
    "signup": {
        "referrer_credits": 20,
        "referee_credits": 20,
        "description": "Both get 20 credits when friend signs up"
    },
    "subscription": {
        "referrer_credits": 100,
        "description": "Get 100 credits when referral subscribes"
    }
}

@router.post("/generate")
async def generate_referral_code(user_id: str):
    """
    Generate unique referral code for user

    Each user gets a shareable code
    """
    try:
        # Check if user already has code
        existing_code = next(
            (code for code, data in referrals_db.items() if data["user_id"] == user_id),
            None
        )

        if existing_code:
            return {
                "code": existing_code,
                "url": f"https://stickercraft.app/signup?ref={existing_code}",
                "message": "Your existing referral code"
            }

        # Generate new code
        code = f"SC{str(uuid.uuid4())[:8].upper()}"

        referrals_db[code] = {
            "user_id": user_id,
            "uses": 0,
            "signups": [],
            "rewards_earned": 0,
            "created_at": datetime.utcnow().isoformat()
        }

        logger.info(f"Generated referral code {code} for user {user_id}")

        return {
            "code": code,
            "url": f"https://stickercraft.app/signup?ref={code}",
            "rewards": {
                "per_signup": REWARD_CONFIG["signup"]["referrer_credits"],
                "per_subscription": REWARD_CONFIG["subscription"]["referrer_credits"]
            },
            "message": "Share this link to earn credits!"
        }

    except Exception as e:
        logger.error(f"Error generating referral code: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/redeem/{code}")
async def redeem_referral_code(code: str, new_user_id: str):
    """
    Redeem referral code during signup

    Both referrer and referee get credits
    """
    try:
        # Validate code
        if code not in referrals_db:
            raise HTTPException(status_code=404, detail="Invalid referral code")

        referral = referrals_db[code]
        referrer_id = referral["user_id"]

        # Prevent self-referral
        if referrer_id == new_user_id:
            raise HTTPException(status_code=400, detail="Cannot use your own referral code")

        # Check if user already used a referral
        if new_user_id in user_referrals:
            raise HTTPException(status_code=400, detail="Already used a referral code")

        # Process referral
        signup_reward = REWARD_CONFIG["signup"]

        # Add credits to referrer
        referral["uses"] += 1
        referral["signups"].append({
            "user_id": new_user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "credits_earned": signup_reward["referrer_credits"]
        })
        referral["rewards_earned"] += signup_reward["referrer_credits"]

        # Track referee's referral usage
        user_referrals[new_user_id] = {
            "referred_by": referrer_id,
            "code": code,
            "credits_received": signup_reward["referee_credits"],
            "timestamp": datetime.utcnow().isoformat()
        }

        logger.info(f"Referral redeemed: {code} by user {new_user_id}")

        # TODO: Actually add credits to user accounts

        return {
            "success": True,
            "credits_earned": signup_reward["referee_credits"],
            "referrer_rewarded": signup_reward["referrer_credits"],
            "message": f"Welcome! You got {signup_reward['referee_credits']} bonus credits!"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error redeeming referral: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/subscription-bonus")
async def process_subscription_bonus(user_id: str):
    """
    Process referral bonus when referred user subscribes

    Referrer gets extra credits for successful conversion
    """
    try:
        # Check if user was referred
        if user_id not in user_referrals:
            return {"message": "User was not referred"}

        referral_info = user_referrals[user_id]

        # Check if bonus already claimed
        if referral_info.get("subscription_bonus_claimed", False):
            raise HTTPException(status_code=400, detail="Subscription bonus already claimed")

        referrer_id = referral_info["referred_by"]
        code = referral_info["code"]

        # Add bonus to referrer
        subscription_reward = REWARD_CONFIG["subscription"]
        referrals_db[code]["rewards_earned"] += subscription_reward["referrer_credits"]

        # Mark as claimed
        user_referrals[user_id]["subscription_bonus_claimed"] = True
        user_referrals[user_id]["subscription_bonus_date"] = datetime.utcnow().isoformat()

        logger.info(f"Subscription bonus credited to {referrer_id} for referral {user_id}")

        # TODO: Actually add credits to referrer account

        return {
            "success": True,
            "referrer_id": referrer_id,
            "bonus_credits": subscription_reward["referrer_credits"],
            "message": "Referrer rewarded for successful conversion!"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing subscription bonus: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/{user_id}")
async def get_referral_stats(user_id: str):
    """
    Get referral statistics for user

    Shows performance and earnings
    """
    try:
        # Find user's referral code
        code = next(
            (c for c, data in referrals_db.items() if data["user_id"] == user_id),
            None
        )

        if not code:
            return {
                "has_referral_code": False,
                "message": "Generate your referral code to start earning!"
            }

        referral = referrals_db[code]

        # Calculate stats
        subscription_conversions = sum(
            1 for signup in referral.get("signups", [])
            if user_referrals.get(signup["user_id"], {}).get("subscription_bonus_claimed", False)
        )

        return ReferralStats(
            total_referrals=referral["uses"],
            successful_signups=len(referral.get("signups", [])),
            subscription_conversions=subscription_conversions,
            total_credits_earned=referral["rewards_earned"],
            referral_code=code
        )

    except Exception as e:
        logger.error(f"Error fetching referral stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/leaderboard")
async def get_referral_leaderboard(limit: int = 10):
    """
    Get top referrers leaderboard

    Gamification element to encourage sharing
    """
    try:
        # Sort by rewards earned
        sorted_referrals = sorted(
            referrals_db.items(),
            key=lambda x: x[1]["rewards_earned"],
            reverse=True
        )[:limit]

        leaderboard = [
            {
                "rank": idx + 1,
                "user_id": data["user_id"][:8] + "...",  # Anonymize
                "referrals": data["uses"],
                "credits_earned": data["rewards_earned"]
            }
            for idx, (code, data) in enumerate(sorted_referrals)
        ]

        return {
            "leaderboard": leaderboard,
            "updated_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error fetching leaderboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rewards")
async def get_reward_info():
    """
    Get information about referral rewards

    Helps users understand the program
    """
    return {
        "rewards": [
            {
                "type": "signup",
                "referrer_gets": REWARD_CONFIG["signup"]["referrer_credits"],
                "referee_gets": REWARD_CONFIG["signup"]["referee_credits"],
                "description": "When your friend signs up"
            },
            {
                "type": "subscription",
                "referrer_gets": REWARD_CONFIG["subscription"]["referrer_credits"],
                "referee_gets": 0,
                "description": "When your friend subscribes to paid plan"
            }
        ],
        "total_possible": (
            REWARD_CONFIG["signup"]["referrer_credits"] +
            REWARD_CONFIG["subscription"]["referrer_credits"]
        ),
        "message": "Share with friends and earn credits together!"
    }
