"""
Security and Authentication
JWT tokens, password hashing, API key validation
"""
from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from sqlalchemy.orm import Session
import secrets
import logging

from app.core.config import settings
from app.db.database import get_db
from app.db.models import User, ApiKey

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security schemes
security = HTTPBearer()
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token

    Args:
        data: Payload data (should include user_id)
        expires_delta: Optional expiration time

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow()
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt

def verify_token(token: str) -> Optional[Dict]:
    """
    Verify and decode JWT token

    Args:
        token: JWT token string

    Returns:
        Decoded payload or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError as e:
        logger.error(f"JWT verification failed: {str(e)}")
        return None

def generate_api_key() -> str:
    """Generate secure random API key"""
    return f"sk_{''.join(secrets.token_urlsafe(32))}"

# Dependencies for protected routes

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token

    Use in endpoints: current_user: User = Depends(get_current_user)
    """
    token = credentials.credentials
    payload = verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is inactive")

    # Update last login
    user.last_login_at = datetime.utcnow()
    db.commit()

    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user (verified account)"""
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified"
        )
    return current_user

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security, auto_error=False),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if authenticated, otherwise None
    Used for endpoints that work with or without auth
    """
    if not credentials:
        return None

    try:
        token = credentials.credentials
        payload = verify_token(token)

        if not payload:
            return None

        user_id = payload.get("user_id")
        user = db.query(User).filter(User.id == user_id).first()

        return user if user and user.is_active else None
    except Exception:
        return None

async def verify_api_key(
    api_key: Optional[str] = Security(api_key_header),
    db: Session = Depends(get_db)
) -> User:
    """
    Verify API key for enterprise users
    Alternative authentication method
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required"
        )

    # Find API key
    key_obj = db.query(ApiKey).filter(
        ApiKey.key == api_key,
        ApiKey.is_active == True
    ).first()

    if not key_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )

    # Check expiration
    if key_obj.expires_at and key_obj.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key expired"
        )

    # Check quota
    if key_obj.current_usage >= key_obj.monthly_quota:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="API key quota exceeded"
        )

    # Update usage
    key_obj.current_usage += 1
    key_obj.last_used_at = datetime.utcnow()
    db.commit()

    # Get user
    user = db.query(User).filter(User.id == key_obj.user_id).first()

    if not user or not user.is_active:
        raise HTTPException(status_code=403, detail="User account inactive")

    return user

# Tier-based access control

def require_tier(required_tier: str):
    """
    Decorator to require specific subscription tier

    Usage:
    @router.get("/premium-feature")
    async def premium(user: User = Depends(require_tier("pro"))):
        ...
    """
    async def tier_checker(user: User = Depends(get_current_user)) -> User:
        tier_hierarchy = {"free": 0, "creator": 1, "pro": 2}

        user_level = tier_hierarchy.get(user.tier, 0)
        required_level = tier_hierarchy.get(required_tier, 999)

        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"This feature requires {required_tier} tier subscription"
            )

        return user

    return tier_checker

# Credit deduction decorator

async def deduct_credits(
    user: User,
    amount: int,
    db: Session
) -> bool:
    """
    Deduct credits from user account

    Returns:
        True if successful, raises exception if insufficient
    """
    if user.credits < amount:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Insufficient credits. Required: {amount}, Available: {user.credits}"
        )

    user.credits -= amount
    user.monthly_credits_used += amount
    db.commit()

    logger.info(f"Deducted {amount} credits from user {user.id}. Remaining: {user.credits}")

    return True

async def check_rate_limit(user: User, action: str) -> bool:
    """
    Check if user has exceeded rate limit

    TODO: Implement with Redis for distributed rate limiting
    """
    # For now, just log
    logger.info(f"Rate limit check for user {user.id}, action {action}")
    return True
