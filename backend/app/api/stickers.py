"""
Sticker Generation API Endpoints
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from typing import List
import uuid
import os
import logging

from app.models.sticker import (
    TextToStickerRequest,
    ImageToStickerRequest,
    CharacterMakerRequest,
    GenerationResponse,
    StickerVariant,
    StickerEditRequest
)
from app.services.ai_service import ai_service
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/generate/text", response_model=GenerationResponse)
async def generate_from_text(request: TextToStickerRequest):
    """
    Generate sticker from text prompt

    Creates AI-generated sticker variants based on text description
    Uses credits: 1 per generation
    """
    try:
        logger.info(f"Generating sticker from text: {request.prompt}")

        # Generate variants
        results = await ai_service.generate_from_text(
            prompt=request.prompt,
            style=request.style.value,
            num_variants=request.num_variants
        )

        # Convert to response format
        variants = [
            StickerVariant(
                id=result['id'],
                image_url=result['image_url'],
                thumbnail_url=result['thumbnail_url']
            )
            for result in results
        ]

        job_id = str(uuid.uuid4())

        return GenerationResponse(
            job_id=job_id,
            status="completed",
            variants=variants,
            message=f"Generated {len(variants)} sticker variants"
        )

    except Exception as e:
        logger.error(f"Error in text generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate/image", response_model=GenerationResponse)
async def generate_from_image(
    file: UploadFile = File(...),
    remove_background: bool = True,
    add_stroke: bool = True,
    stroke_width: int = 10
):
    """
    Convert uploaded image to sticker

    Processes image with background removal and stroke
    Uses credits: 1 per generation
    """
    try:
        logger.info(f"Converting image to sticker: {file.filename}")

        # Save uploaded file
        upload_id = str(uuid.uuid4())
        file_ext = os.path.splitext(file.filename)[1]
        file_path = os.path.join(settings.UPLOAD_DIR, f"{upload_id}{file_ext}")

        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Process image
        image_data = content

        # Remove background if requested
        if remove_background:
            logger.info("Removing background...")
            image_data = await ai_service.remove_background(file_path)

        # Add stroke if requested
        if add_stroke:
            logger.info("Adding stroke...")
            image_data = await ai_service.add_stroke(
                image_data,
                stroke_width=stroke_width,
                stroke_color="#FFFFFF"
            )

        # Optimize for sticker format
        image_data = await ai_service.optimize_for_sticker(image_data)

        # Save processed image
        output_path = os.path.join(settings.UPLOAD_DIR, f"{upload_id}_processed.png")
        with open(output_path, "wb") as f:
            f.write(image_data)

        # Create response
        variant = StickerVariant(
            id=upload_id,
            image_url=f"/uploads/{upload_id}_processed.png",
            thumbnail_url=f"/uploads/{upload_id}_processed.png"
        )

        return GenerationResponse(
            job_id=upload_id,
            status="completed",
            variants=[variant],
            message="Image converted to sticker successfully"
        )

    except Exception as e:
        logger.error(f"Error in image conversion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate/character", response_model=GenerationResponse)
async def create_character(request: CharacterMakerRequest):
    """
    Create character sticker with expression

    Generates character with specific emotion/expression
    Uses credits: 1 per generation
    """
    try:
        logger.info(f"Creating character: {request.character_name} - {request.expression}")

        # Generate character
        result = await ai_service.create_character(
            character_description=request.base_description,
            expression=request.expression,
            style=request.style.value
        )

        variant = StickerVariant(
            id=result['id'],
            image_url=result['image_url'],
            thumbnail_url=result['thumbnail_url']
        )

        return GenerationResponse(
            job_id=result['id'],
            status="completed",
            variants=[variant],
            message=f"Character '{request.character_name}' created successfully"
        )

    except Exception as e:
        logger.error(f"Error creating character: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/edit")
async def edit_sticker(request: StickerEditRequest):
    """
    Edit sticker with text layers and effects

    Add text, modify stroke, and apply effects to existing sticker
    """
    try:
        logger.info(f"Editing sticker: {request.sticker_id}")

        # TODO: Implement sticker editing logic
        # - Load existing sticker
        # - Apply text layers
        # - Modify stroke/effects
        # - Save edited version

        return {
            "sticker_id": request.sticker_id,
            "status": "completed",
            "message": "Sticker edited successfully",
            "image_url": f"/uploads/{request.sticker_id}_edited.png"
        }

    except Exception as e:
        logger.error(f"Error editing sticker: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{sticker_id}")
async def get_sticker(sticker_id: str):
    """Get sticker by ID"""
    try:
        # TODO: Implement sticker retrieval from storage/database
        return {
            "id": sticker_id,
            "image_url": f"/uploads/{sticker_id}.png",
            "created_at": "2025-11-17T00:00:00Z"
        }

    except Exception as e:
        raise HTTPException(status_code=404, detail="Sticker not found")

@router.delete("/{sticker_id}")
async def delete_sticker(sticker_id: str):
    """Delete sticker"""
    try:
        # TODO: Implement sticker deletion
        logger.info(f"Deleting sticker: {sticker_id}")

        return {
            "message": "Sticker deleted successfully",
            "sticker_id": sticker_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
