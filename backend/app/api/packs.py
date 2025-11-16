"""
Sticker Pack API Endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import List
import uuid
import logging
from datetime import datetime

from app.models.sticker import (
    CreatePackRequest,
    StickerPack
)

router = APIRouter()
logger = logging.getLogger(__name__)

# In-memory storage for MVP (replace with database)
packs_db = {}

@router.post("/", response_model=StickerPack)
async def create_pack(request: CreatePackRequest):
    """
    Create new sticker pack

    Requires minimum 3 stickers for WhatsApp/Telegram
    """
    try:
        logger.info(f"Creating pack: {request.name}")

        pack_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        pack = StickerPack(
            id=pack_id,
            name=request.name,
            description=request.description,
            sticker_ids=request.sticker_ids,
            platform=request.platform,
            is_published=False,
            created_at=now,
            updated_at=now
        )

        packs_db[pack_id] = pack

        logger.info(f"Pack created: {pack_id}")
        return pack

    except Exception as e:
        logger.error(f"Error creating pack: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{pack_id}", response_model=StickerPack)
async def get_pack(pack_id: str):
    """Get sticker pack by ID"""
    pack = packs_db.get(pack_id)

    if not pack:
        raise HTTPException(status_code=404, detail="Pack not found")

    return pack

@router.get("/", response_model=List[StickerPack])
async def list_packs(platform: str = None, limit: int = 20, offset: int = 0):
    """
    List sticker packs

    Optionally filter by platform
    """
    all_packs = list(packs_db.values())

    if platform:
        all_packs = [p for p in all_packs if p.platform.value == platform]

    # Pagination
    packs = all_packs[offset:offset + limit]

    return packs

@router.put("/{pack_id}/publish")
async def publish_pack(pack_id: str):
    """
    Publish sticker pack

    Makes pack available for export to platform
    """
    pack = packs_db.get(pack_id)

    if not pack:
        raise HTTPException(status_code=404, detail="Pack not found")

    pack.is_published = True
    pack.updated_at = datetime.utcnow().isoformat()

    return {
        "pack_id": pack_id,
        "is_published": True,
        "message": "Pack published successfully"
    }

@router.delete("/{pack_id}")
async def delete_pack(pack_id: str):
    """Delete sticker pack"""
    if pack_id not in packs_db:
        raise HTTPException(status_code=404, detail="Pack not found")

    del packs_db[pack_id]

    return {
        "pack_id": pack_id,
        "message": "Pack deleted successfully"
    }

@router.post("/{pack_id}/stickers")
async def add_sticker_to_pack(pack_id: str, sticker_id: str):
    """Add sticker to existing pack"""
    pack = packs_db.get(pack_id)

    if not pack:
        raise HTTPException(status_code=404, detail="Pack not found")

    if sticker_id in pack.sticker_ids:
        raise HTTPException(status_code=400, detail="Sticker already in pack")

    if len(pack.sticker_ids) >= 30:
        raise HTTPException(status_code=400, detail="Pack is full (max 30 stickers)")

    pack.sticker_ids.append(sticker_id)
    pack.updated_at = datetime.utcnow().isoformat()

    return {
        "pack_id": pack_id,
        "sticker_count": len(pack.sticker_ids),
        "message": "Sticker added to pack"
    }

@router.delete("/{pack_id}/stickers/{sticker_id}")
async def remove_sticker_from_pack(pack_id: str, sticker_id: str):
    """Remove sticker from pack"""
    pack = packs_db.get(pack_id)

    if not pack:
        raise HTTPException(status_code=404, detail="Pack not found")

    if sticker_id not in pack.sticker_ids:
        raise HTTPException(status_code=404, detail="Sticker not in pack")

    pack.sticker_ids.remove(sticker_id)
    pack.updated_at = datetime.utcnow().isoformat()

    return {
        "pack_id": pack_id,
        "sticker_count": len(pack.sticker_ids),
        "message": "Sticker removed from pack"
    }
