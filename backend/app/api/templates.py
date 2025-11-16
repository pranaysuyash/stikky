"""
Smart Templates and Festival Pack API Endpoints
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
import uuid
import logging

from app.core.templates import (
    Festival,
    MoodCategory,
    get_hinglish_templates,
    get_festival_pack,
    get_prompt_suggestions,
    enhance_prompt_with_style
)
from app.services.ai_service import ai_service
from app.models.sticker import (
    StylePreset,
    GenerationResponse,
    StickerVariant,
    CreatePackRequest
)

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/hinglish/{category}")
async def get_hinglish_prompts(category: MoodCategory):
    """
    Get Hinglish smart prompts for a mood category

    Returns curated prompts in Hinglish for Indian users
    """
    try:
        templates = get_hinglish_templates(category)

        return {
            "category": category.value,
            "count": len(templates),
            "templates": templates
        }

    except Exception as e:
        logger.error(f"Error fetching Hinglish templates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/autocomplete")
async def autocomplete_prompt(q: str):
    """
    Get prompt autocomplete suggestions

    Smart suggestions based on partial input
    Example: "angry c" → ["angry cat...", "angry chef..."]
    """
    try:
        if len(q) < 2:
            return {"suggestions": []}

        suggestions = get_prompt_suggestions(q)

        return {
            "query": q,
            "suggestions": suggestions
        }

    except Exception as e:
        logger.error(f"Error in autocomplete: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/festival/{festival}/generate")
async def generate_festival_pack(
    festival: Festival,
    style: StylePreset = StylePreset.CARTOON,
    background_tasks: BackgroundTasks = None
):
    """
    Auto-generate complete festival sticker pack

    Creates 10 themed stickers for the festival in one go
    High-value feature for Indian market!

    Returns immediately with job_id, processes in background
    """
    try:
        logger.info(f"Generating {festival.value} pack in {style.value} style")

        # Get festival prompts
        prompts = get_festival_pack(festival)

        if not prompts:
            raise HTTPException(status_code=404, detail="Festival not found")

        job_id = str(uuid.uuid4())

        # For MVP, return placeholder
        # In production, use Celery to batch process
        variants = []
        for i, prompt in enumerate(prompts[:10]):  # Limit to 10
            enhanced = enhance_prompt_with_style(prompt, style.value)
            variant = StickerVariant(
                id=f"{job_id}_sticker_{i}",
                image_url=f"https://placeholder.com/512x512?text={festival.value}+{i+1}",
                thumbnail_url=f"https://placeholder.com/128x128?text={festival.value}+{i+1}"
            )
            variants.append(variant)

        # TODO: In production, queue this as background task
        # background_tasks.add_task(batch_generate_stickers, prompts, style)

        return {
            "job_id": job_id,
            "festival": festival.value,
            "style": style.value,
            "status": "processing",
            "sticker_count": len(variants),
            "variants": variants,
            "message": f"Generating {festival.value} festival pack with {len(variants)} stickers",
            "estimated_time": "2-3 minutes"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating festival pack: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/festivals")
async def list_festivals():
    """
    List all available festival packs

    Returns festivals with preview info
    """
    festivals_info = [
        {
            "id": Festival.DIWALI.value,
            "name": "Diwali",
            "description": "Festival of Lights - Diyas, rangoli, sweets, crackers",
            "sticker_count": 10,
            "popular": True
        },
        {
            "id": Festival.HOLI.value,
            "name": "Holi",
            "description": "Festival of Colors - Gulal, pichkari, colors, celebration",
            "sticker_count": 10,
            "popular": True
        },
        {
            "id": Festival.EID.value,
            "name": "Eid",
            "description": "Islamic Festival - Moon, lanterns, biryani, celebration",
            "sticker_count": 10,
            "popular": True
        },
        {
            "id": Festival.CHRISTMAS.value,
            "name": "Christmas",
            "description": "Christmas - Tree, Santa, gifts, celebration",
            "sticker_count": 10,
            "popular": True
        },
        {
            "id": Festival.NEW_YEAR.value,
            "name": "New Year",
            "description": "New Year - Fireworks, countdown, celebration, fresh start",
            "sticker_count": 10,
            "popular": True
        },
        {
            "id": Festival.RAKSHA_BANDHAN.value,
            "name": "Raksha Bandhan",
            "description": "Sibling Bond - Rakhi, sweets, brother-sister love",
            "sticker_count": 10,
            "popular": False
        },
        {
            "id": Festival.GANESH_CHATURTHI.value,
            "name": "Ganesh Chaturthi",
            "description": "Ganesh Festival - Idol, modak, visarjan, celebration",
            "sticker_count": 10,
            "popular": False
        },
        {
            "id": Festival.NAVRATRI.value,
            "name": "Navratri",
            "description": "Garba Festival - Dandiya, dance, colors, celebration",
            "sticker_count": 10,
            "popular": False
        },
        {
            "id": Festival.DURGA_PUJA.value,
            "name": "Durga Puja",
            "description": "Durga Worship - Pandal, idol, dhak, Bengali celebration",
            "sticker_count": 10,
            "popular": False
        },
        {
            "id": Festival.PONGAL.value,
            "name": "Pongal",
            "description": "Harvest Festival - Pongal pot, cow, kolam, Tamil tradition",
            "sticker_count": 10,
            "popular": False
        }
    ]

    return {
        "festivals": festivals_info,
        "total": len(festivals_info)
    }

@router.get("/categories")
async def list_mood_categories():
    """
    List all Hinglish mood categories

    Returns categories with sample prompts
    """
    categories = [
        {
            "id": "work",
            "name": "Work & Office",
            "emoji": "💼",
            "sample_prompts": get_hinglish_templates(MoodCategory.WORK)[:3]
        },
        {
            "id": "celebration",
            "name": "Celebration",
            "emoji": "🎉",
            "sample_prompts": get_hinglish_templates(MoodCategory.CELEBRATION)[:3]
        },
        {
            "id": "emotions",
            "name": "Emotions",
            "emoji": "😊",
            "sample_prompts": get_hinglish_templates(MoodCategory.EMOTIONS)[:3]
        },
        {
            "id": "food",
            "name": "Food & Drink",
            "emoji": "🍛",
            "sample_prompts": get_hinglish_templates(MoodCategory.FOOD)[:3]
        },
        {
            "id": "daily_life",
            "name": "Daily Life",
            "emoji": "🏠",
            "sample_prompts": get_hinglish_templates(MoodCategory.DAILY_LIFE)[:3]
        },
        {
            "id": "humor",
            "name": "Desi Humor",
            "emoji": "😂",
            "sample_prompts": get_hinglish_templates(MoodCategory.HUMOR)[:3]
        }
    ]

    return {
        "categories": categories,
        "total": len(categories)
    }
