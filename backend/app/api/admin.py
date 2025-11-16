"""
Admin Panel API
Content moderation, user management, analytics dashboard
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from app.db.database import get_db
from app.db.models import (
    User, Sticker, Pack, Generation, ContentReport,
    AnalyticsEvent, Referral
)
from app.core.security import get_current_user, require_tier
from app.services.analytics_service import analytics_service

router = APIRouter()
logger = logging.getLogger(__name__)

# Admin role check (in production, use proper RBAC)
async def require_admin(current_user: User = Depends(get_current_user)):
    """Require admin role"""
    # For MVP, check if email is in admin list
    # In production, use proper role-based access control
    admin_emails = ["admin@stickercraft.com", "pranay@stickercraft.com"]

    if current_user.email not in admin_emails:
        raise HTTPException(status_code=403, detail="Admin access required")

    return current_user

@router.get("/dashboard")
async def get_admin_dashboard(
    days: int = Query(30, ge=1, le=365),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Admin dashboard with key metrics

    Returns comprehensive overview for product management
    """
    try:
        # Get product metrics
        metrics = await analytics_service.get_product_metrics(db, days)

        # Get funnel metrics
        funnel = await analytics_service.get_funnel_metrics(db)

        # Revenue metrics (mock for MVP)
        revenue_metrics = {
            "mrr": 50000,  # Monthly Recurring Revenue (₹)
            "arr": 600000,  # Annual Recurring Revenue
            "arpu": 250,  # Average Revenue Per User
            "ltv": 3000  # Lifetime Value
        }

        # Recent signups
        recent_signups = db.query(User).order_by(
            desc(User.created_at)
        ).limit(10).all()

        # Top creators
        top_creators = db.query(
            User.id,
            User.username,
            User.email,
            func.count(Sticker.id).label('sticker_count')
        ).join(Sticker).group_by(
            User.id
        ).order_by(desc('sticker_count')).limit(10).all()

        # Pending content reports
        pending_reports = db.query(func.count(ContentReport.id)).filter(
            ContentReport.status == "pending"
        ).scalar()

        return {
            "overview": metrics,
            "funnel": funnel,
            "revenue": revenue_metrics,
            "recent_signups": [
                {
                    "id": u.id,
                    "email": u.email,
                    "username": u.username,
                    "tier": u.tier,
                    "created_at": u.created_at.isoformat()
                }
                for u in recent_signups
            ],
            "top_creators": [
                {
                    "id": c[0],
                    "username": c[1],
                    "email": c[2],
                    "sticker_count": c[3]
                }
                for c in top_creators
            ],
            "moderation": {
                "pending_reports": pending_reports
            }
        }

    except Exception as e:
        logger.error(f"Error getting admin dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users")
async def list_all_users(
    skip: int = 0,
    limit: int = 50,
    tier: Optional[str] = None,
    search: Optional[str] = None,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    List all users with filters

    For user management and support
    """
    try:
        query = db.query(User)

        # Filter by tier
        if tier:
            query = query.filter(User.tier == tier)

        # Search by email or username
        if search:
            query = query.filter(
                (User.email.ilike(f"%{search}%")) |
                (User.username.ilike(f"%{search}%"))
            )

        # Paginate
        total = query.count()
        users = query.order_by(desc(User.created_at)).offset(skip).limit(limit).all()

        return {
            "total": total,
            "users": [
                {
                    "id": u.id,
                    "email": u.email,
                    "username": u.username,
                    "tier": u.tier,
                    "credits": u.credits,
                    "is_active": u.is_active,
                    "is_verified": u.is_verified,
                    "created_at": u.created_at.isoformat(),
                    "last_login_at": u.last_login_at.isoformat() if u.last_login_at else None
                }
                for u in users
            ]
        }

    except Exception as e:
        logger.error(f"Error listing users: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/users/{user_id}/credits")
async def adjust_user_credits(
    user_id: str,
    amount: int,
    reason: str,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Manually adjust user credits

    For support and compensation
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        old_credits = user.credits
        user.credits += amount

        # Prevent negative credits
        if user.credits < 0:
            user.credits = 0

        db.commit()

        logger.info(f"Admin {admin.email} adjusted credits for {user.email}: {old_credits} -> {user.credits} (reason: {reason})")

        return {
            "user_id": user_id,
            "old_credits": old_credits,
            "new_credits": user.credits,
            "adjustment": amount,
            "reason": reason
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adjusting credits: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/users/{user_id}/tier")
async def change_user_tier(
    user_id: str,
    new_tier: str,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Change user subscription tier manually"""
    try:
        if new_tier not in ["free", "creator", "pro"]:
            raise HTTPException(status_code=400, detail="Invalid tier")

        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        old_tier = user.tier
        user.tier = new_tier
        db.commit()

        logger.info(f"Admin {admin.email} changed tier for {user.email}: {old_tier} -> {new_tier}")

        return {
            "user_id": user_id,
            "old_tier": old_tier,
            "new_tier": new_tier
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing tier: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/content/flagged")
async def get_flagged_content(
    status: str = "pending",
    skip: int = 0,
    limit: int = 50,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get flagged content for moderation

    Review reported stickers
    """
    try:
        query = db.query(ContentReport).filter(
            ContentReport.status == status
        )

        total = query.count()
        reports = query.order_by(desc(ContentReport.created_at)).offset(skip).limit(limit).all()

        return {
            "total": total,
            "reports": [
                {
                    "id": r.id,
                    "sticker_id": r.sticker_id,
                    "report_type": r.report_type,
                    "description": r.description,
                    "status": r.status,
                    "created_at": r.created_at.isoformat()
                }
                for r in reports
            ]
        }

    except Exception as e:
        logger.error(f"Error getting flagged content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/content/reports/{report_id}/moderate")
async def moderate_content(
    report_id: str,
    action: str,  # approve, remove, warn
    notes: str,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Take moderation action on reported content
    """
    try:
        report = db.query(ContentReport).filter(ContentReport.id == report_id).first()

        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        # Update report
        report.status = "reviewed"
        report.action_taken = action
        report.moderator_notes = notes
        report.reviewed_at = datetime.utcnow()

        # Take action on sticker
        if action == "remove":
            sticker = db.query(Sticker).filter(Sticker.id == report.sticker_id).first()
            if sticker:
                sticker.is_flagged = True
                sticker.moderation_status = "rejected"

        db.commit()

        logger.info(f"Admin {admin.email} moderated report {report_id}: {action}")

        return {
            "report_id": report_id,
            "action": action,
            "notes": notes
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error moderating content: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/retention")
async def get_retention_analysis(
    cohort_date: Optional[str] = None,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get retention cohort analysis

    Critical metric for product health
    """
    try:
        if cohort_date:
            date = datetime.fromisoformat(cohort_date)
        else:
            # Default to 30 days ago
            date = datetime.utcnow() - timedelta(days=30)

        retention = await analytics_service.get_retention_cohort(db, date)

        return retention

    except Exception as e:
        logger.error(f"Error getting retention: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/growth")
async def get_growth_metrics(
    days: int = 90,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get growth metrics over time

    Daily/weekly signups, activations, revenue
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Daily signups
        daily_signups = db.query(
            func.date(User.created_at).label('date'),
            func.count(User.id).label('count')
        ).filter(
            User.created_at >= cutoff_date
        ).group_by(func.date(User.created_at)).all()

        # Daily activations (first sticker created)
        daily_activations = db.query(
            func.date(Sticker.created_at).label('date'),
            func.count(func.distinct(Sticker.user_id)).label('count')
        ).filter(
            Sticker.created_at >= cutoff_date
        ).group_by(func.date(Sticker.created_at)).all()

        return {
            "period_days": days,
            "signups": [
                {"date": s[0].isoformat(), "count": s[1]}
                for s in daily_signups
            ],
            "activations": [
                {"date": a[0].isoformat(), "count": a[1]}
                for a in daily_activations
            ]
        }

    except Exception as e:
        logger.error(f"Error getting growth metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/referrals/leaderboard")
async def get_referral_leaderboard_admin(
    limit: int = 50,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get detailed referral leaderboard

    Track viral growth performance
    """
    try:
        referrals = db.query(
            Referral,
            User.email,
            User.username
        ).join(User, Referral.referrer_user_id == User.id).order_by(
            desc(Referral.total_credits_earned)
        ).limit(limit).all()

        return {
            "leaderboard": [
                {
                    "rank": idx + 1,
                    "code": r[0].code,
                    "referrer_email": r[1],
                    "referrer_username": r[2],
                    "total_uses": r[0].total_uses,
                    "signups": r[0].successful_signups,
                    "conversions": r[0].subscription_conversions,
                    "credits_earned": r[0].total_credits_earned
                }
                for idx, r in enumerate(referrals)
            ]
        }

    except Exception as e:
        logger.error(f"Error getting referral leaderboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
