"""
API Routes
"""
from fastapi import APIRouter

from app.api import stickers, users, exports, packs

router = APIRouter()

# Include sub-routers
router.include_router(stickers.router, prefix="/stickers", tags=["stickers"])
router.include_router(exports.router, prefix="/exports", tags=["exports"])
router.include_router(packs.router, prefix="/packs", tags=["packs"])
router.include_router(users.router, prefix="/users", tags=["users"])
