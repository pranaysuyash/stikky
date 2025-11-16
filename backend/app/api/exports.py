"""
Platform Export API Endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import List
import logging
import os

from app.models.sticker import (
    ExportRequest,
    ExportResponse,
    PlatformExport,
    PlatformType
)
from app.services.export_service import export_service
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/export", response_model=ExportResponse)
async def export_sticker(request: ExportRequest):
    """
    Export sticker to specified platforms

    Converts sticker to platform-specific formats with optimization
    Uses credits for animated exports
    """
    try:
        logger.info(f"Exporting sticker {request.sticker_id} to platforms: {request.platforms}")

        # Load sticker image
        # TODO: Get from storage/database
        sticker_path = os.path.join(settings.UPLOAD_DIR, f"{request.sticker_id}.png")

        if not os.path.exists(sticker_path):
            raise HTTPException(status_code=404, detail="Sticker not found")

        with open(sticker_path, "rb") as f:
            image_bytes = f.read()

        exports = []
        total_size = 0

        # Export to each platform
        for platform in request.platforms:
            try:
                if request.sticker_type.value == "static":
                    export_data, metadata = await export_service.export_static(
                        image_bytes,
                        platform
                    )
                else:
                    # For animated, we'd need frames
                    # Placeholder for now
                    logger.warning(f"Animated export not fully implemented for {platform.value}")
                    continue

                # Save exported file
                ext = metadata['format'].lower()
                export_filename = f"{request.sticker_id}_{platform.value}.{ext}"
                export_path = os.path.join(settings.UPLOAD_DIR, export_filename)

                with open(export_path, "wb") as f:
                    f.write(export_data)

                platform_export = PlatformExport(
                    platform=platform,
                    format=metadata['format'],
                    file_url=f"/uploads/{export_filename}",
                    file_size=metadata['file_size'],
                    dimensions=metadata['dimensions'],
                    compliant=metadata['compliant'],
                    warnings=metadata['warnings']
                )

                exports.append(platform_export)
                total_size += metadata['file_size']

            except Exception as e:
                logger.error(f"Error exporting to {platform.value}: {str(e)}")
                # Continue with other platforms

        if not exports:
            raise HTTPException(status_code=500, detail="Failed to export to any platform")

        return ExportResponse(
            sticker_id=request.sticker_id,
            exports=exports,
            total_size=total_size,
            message=f"Successfully exported to {len(exports)} platform(s)"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in export: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tray-icon")
async def create_tray_icon(sticker_id: str):
    """
    Create tray icon for WhatsApp pack

    Generates 96x96 icon from sticker
    """
    try:
        logger.info(f"Creating tray icon for sticker {sticker_id}")

        # Load sticker
        sticker_path = os.path.join(settings.UPLOAD_DIR, f"{sticker_id}.png")

        if not os.path.exists(sticker_path):
            raise HTTPException(status_code=404, detail="Sticker not found")

        with open(sticker_path, "rb") as f:
            image_bytes = f.read()

        # Create tray icon
        tray_data = await export_service.create_tray_icon(image_bytes)

        # Save tray icon
        tray_filename = f"{sticker_id}_tray.png"
        tray_path = os.path.join(settings.UPLOAD_DIR, tray_filename)

        with open(tray_path, "wb") as f:
            f.write(tray_data)

        return {
            "sticker_id": sticker_id,
            "tray_icon_url": f"/uploads/{tray_filename}",
            "size": len(tray_data),
            "message": "Tray icon created successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating tray icon: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/specs/{platform}")
async def get_platform_specs(platform: PlatformType):
    """
    Get export specifications for platform

    Returns format requirements and limits
    """
    try:
        specs = export_service.platform_specs.get(platform)

        if not specs:
            raise HTTPException(status_code=404, detail="Platform not found")

        return {
            "platform": platform.value,
            "specifications": specs
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
