"""
Analytics and Event Tracking Service
Track user behavior, conversions, and product metrics
"""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
import logging

from app.db.models import AnalyticsEvent, User, Sticker, Generation, Export
from app.db.database import get_db

logger = logging.getLogger(__name__)

class AnalyticsService:
    """Service for tracking and analyzing user behavior"""

    @staticmethod
    async def track_event(
        db: Session,
        event_type: str,
        user_id: Optional[str] = None,
        event_category: str = "engagement",
        event_data: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        device_type: Optional[str] = None,
        platform: Optional[str] = None
    ):
        """
        Track analytics event

        Event Types:
        - page_view
        - sticker_created
        - sticker_exported
        - pack_created
        - referral_shared
        - subscription_started
        - subscription_canceled
        - feature_used
        """
        try:
            event = AnalyticsEvent(
                user_id=user_id,
                event_type=event_type,
                event_category=event_category,
                event_data=event_data or {},
                session_id=session_id,
                device_type=device_type,
                platform=platform
            )

            db.add(event)
            db.commit()

            logger.info(f"Tracked event: {event_type} for user {user_id}")

        except Exception as e:
            logger.error(f"Failed to track event: {str(e)}")
            db.rollback()

    @staticmethod
    async def get_user_stats(db: Session, user_id: str) -> Dict:
        """Get comprehensive stats for a user"""
        try:
            user = db.query(User).filter(User.id == user_id).first()

            if not user:
                return {}

            # Count stickers
            total_stickers = db.query(func.count(Sticker.id)).filter(
                Sticker.user_id == user_id
            ).scalar()

            # Count exports
            total_exports = db.query(func.count(Export.id)).filter(
                Sticker.user_id == user_id,
                Export.sticker_id == Sticker.id
            ).scalar()

            # Count generations
            total_generations = db.query(func.count(Generation.id)).filter(
                Generation.user_id == user_id
            ).scalar()

            # Average generation time
            avg_generation_time = db.query(func.avg(Generation.processing_time)).filter(
                Generation.user_id == user_id,
                Generation.status == "completed"
            ).scalar() or 0

            # Most used style
            most_used_style = db.query(
                Sticker.style,
                func.count(Sticker.id).label('count')
            ).filter(
                Sticker.user_id == user_id
            ).group_by(Sticker.style).order_by(func.count(Sticker.id).desc()).first()

            # Days since signup
            days_active = (datetime.utcnow() - user.created_at).days

            return {
                "user_id": user_id,
                "tier": user.tier,
                "total_stickers": total_stickers,
                "total_exports": total_exports,
                "total_generations": total_generations,
                "avg_generation_time": round(avg_generation_time, 2) if avg_generation_time else 0,
                "most_used_style": most_used_style[0] if most_used_style else None,
                "credits_remaining": user.credits,
                "credits_used_this_month": user.monthly_credits_used,
                "exports_this_month": user.monthly_exports_used,
                "days_active": days_active,
                "created_at": user.created_at.isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to get user stats: {str(e)}")
            return {}

    @staticmethod
    async def get_product_metrics(db: Session, days: int = 30) -> Dict:
        """
        Get product-level metrics for PM dashboard

        Key metrics:
        - DAU/MAU (Daily/Monthly Active Users)
        - Activation rate
        - Retention (D1, D7, D30)
        - Conversion rate (free to paid)
        - ARPU (Average Revenue Per User)
        - Viral coefficient
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            # Total users
            total_users = db.query(func.count(User.id)).scalar()

            # Active users (created sticker in last X days)
            active_users = db.query(func.count(func.distinct(Sticker.user_id))).filter(
                Sticker.created_at >= cutoff_date
            ).scalar()

            # New signups
            new_signups = db.query(func.count(User.id)).filter(
                User.created_at >= cutoff_date
            ).scalar()

            # Activated users (created at least 1 sticker)
            activated_users = db.query(func.count(func.distinct(Sticker.user_id))).scalar()
            activation_rate = (activated_users / total_users * 100) if total_users > 0 else 0

            # Paid users
            paid_users = db.query(func.count(User.id)).filter(
                User.tier.in_(["creator", "pro"])
            ).scalar()
            conversion_rate = (paid_users / total_users * 100) if total_users > 0 else 0

            # Total stickers created
            total_stickers = db.query(func.count(Sticker.id)).filter(
                Sticker.created_at >= cutoff_date
            ).scalar()

            # Total exports
            total_exports = db.query(func.count(Export.id)).filter(
                Export.created_at >= cutoff_date
            ).scalar()

            # Average stickers per user
            avg_stickers_per_user = (total_stickers / active_users) if active_users > 0 else 0

            # Most popular style
            popular_style = db.query(
                Sticker.style,
                func.count(Sticker.id).label('count')
            ).filter(
                Sticker.created_at >= cutoff_date
            ).group_by(Sticker.style).order_by(func.count(Sticker.id).desc()).first()

            # Most popular platform
            popular_platform = db.query(
                Export.platform,
                func.count(Export.id).label('count')
            ).filter(
                Export.created_at >= cutoff_date
            ).group_by(Export.platform).order_by(func.count(Export.id).desc()).first()

            return {
                "period_days": days,
                "total_users": total_users,
                "active_users": active_users,
                "new_signups": new_signups,
                "activation_rate": round(activation_rate, 2),
                "paid_users": paid_users,
                "conversion_rate": round(conversion_rate, 2),
                "total_stickers_created": total_stickers,
                "total_exports": total_exports,
                "avg_stickers_per_user": round(avg_stickers_per_user, 2),
                "most_popular_style": popular_style[0] if popular_style else None,
                "most_popular_platform": popular_platform[0] if popular_platform else None,
                "generated_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to get product metrics: {str(e)}")
            return {}

    @staticmethod
    async def get_funnel_metrics(db: Session) -> Dict:
        """
        Calculate conversion funnel metrics

        Funnel:
        1. Signup
        2. First sticker created (Activation)
        3. First export
        4. Pack created
        5. Subscription started
        """
        try:
            # Total signups
            total_signups = db.query(func.count(User.id)).scalar()

            # Users who created sticker
            created_sticker = db.query(func.count(func.distinct(Sticker.user_id))).scalar()

            # Users who exported
            exported = db.query(func.count(func.distinct(Sticker.user_id))).join(
                Export, Sticker.id == Export.sticker_id
            ).scalar()

            # Paid users
            subscribed = db.query(func.count(User.id)).filter(
                User.tier.in_(["creator", "pro"])
            ).scalar()

            # Calculate conversion rates
            activation_rate = (created_sticker / total_signups * 100) if total_signups > 0 else 0
            export_rate = (exported / created_sticker * 100) if created_sticker > 0 else 0
            subscription_rate = (subscribed / exported * 100) if exported > 0 else 0

            return {
                "funnel": [
                    {"stage": "signup", "count": total_signups, "conversion_rate": 100},
                    {"stage": "activated", "count": created_sticker, "conversion_rate": round(activation_rate, 2)},
                    {"stage": "exported", "count": exported, "conversion_rate": round(export_rate, 2)},
                    {"stage": "subscribed", "count": subscribed, "conversion_rate": round(subscription_rate, 2)}
                ],
                "overall_conversion": round((subscribed / total_signups * 100) if total_signups > 0 else 0, 2)
            }

        except Exception as e:
            logger.error(f"Failed to get funnel metrics: {str(e)}")
            return {}

    @staticmethod
    async def get_retention_cohort(db: Session, cohort_date: datetime) -> Dict:
        """
        Calculate retention for a specific cohort

        Args:
            cohort_date: Date to start cohort (e.g., first day of month)

        Returns:
            Retention rates for D1, D7, D30
        """
        try:
            # Get users who signed up on cohort_date
            cohort_users = db.query(User.id).filter(
                func.date(User.created_at) == cohort_date.date()
            ).all()

            cohort_user_ids = [u[0] for u in cohort_users]
            cohort_size = len(cohort_user_ids)

            if cohort_size == 0:
                return {"cohort_size": 0, "retention": {}}

            # Day 1 retention
            d1_active = db.query(func.count(func.distinct(Sticker.user_id))).filter(
                Sticker.user_id.in_(cohort_user_ids),
                func.date(Sticker.created_at) == (cohort_date + timedelta(days=1)).date()
            ).scalar()

            # Day 7 retention
            d7_active = db.query(func.count(func.distinct(Sticker.user_id))).filter(
                Sticker.user_id.in_(cohort_user_ids),
                Sticker.created_at >= cohort_date + timedelta(days=7),
                Sticker.created_at < cohort_date + timedelta(days=8)
            ).scalar()

            # Day 30 retention
            d30_active = db.query(func.count(func.distinct(Sticker.user_id))).filter(
                Sticker.user_id.in_(cohort_user_ids),
                Sticker.created_at >= cohort_date + timedelta(days=30),
                Sticker.created_at < cohort_date + timedelta(days=31)
            ).scalar()

            return {
                "cohort_date": cohort_date.date().isoformat(),
                "cohort_size": cohort_size,
                "retention": {
                    "d1": round((d1_active / cohort_size * 100), 2),
                    "d7": round((d7_active / cohort_size * 100), 2),
                    "d30": round((d30_active / cohort_size * 100), 2)
                }
            }

        except Exception as e:
            logger.error(f"Failed to calculate retention: {str(e)}")
            return {}

# Singleton
analytics_service = AnalyticsService()
