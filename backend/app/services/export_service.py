"""
Platform Export Service
Handles conversion and optimization for different messaging platforms
"""
import io
import logging
from typing import Dict, List, Tuple
from PIL import Image
import os

from app.core.config import settings
from app.models.sticker import PlatformType, StickerType

logger = logging.getLogger(__name__)

class ExportService:
    """Service for exporting stickers to different platforms"""

    def __init__(self):
        self.platform_specs = {
            PlatformType.WHATSAPP: {
                'static': {
                    'format': 'WEBP',
                    'size_limit': settings.WHATSAPP_STATIC_LIMIT,
                    'dimensions': (512, 512),
                    'requires_tray': True
                },
                'animated': {
                    'format': 'WEBP',
                    'size_limit': settings.WHATSAPP_ANIMATED_LIMIT,
                    'dimensions': (512, 512),
                    'max_duration': 3,
                    'requires_tray': True
                }
            },
            PlatformType.TELEGRAM: {
                'static': {
                    'format': 'WEBP',
                    'size_limit': settings.TELEGRAM_STATIC_LIMIT,
                    'dimensions': (512, 512),
                },
                'animated': {
                    'format': 'WEBM',
                    'size_limit': settings.TELEGRAM_ANIMATED_LIMIT,
                    'dimensions': (512, 512),
                    'max_duration': 3,
                    'fps': 30
                }
            },
            PlatformType.SIGNAL: {
                'static': {
                    'format': 'WEBP',
                    'size_limit': settings.WHATSAPP_STATIC_LIMIT,
                    'dimensions': (512, 512),
                },
                'animated': {
                    'format': 'WEBP',
                    'size_limit': settings.WHATSAPP_ANIMATED_LIMIT,
                    'dimensions': (512, 512),
                    'max_duration': 3
                }
            },
            PlatformType.IMESSAGE: {
                'static': {
                    'format': 'PNG',
                    'dimensions': (512, 512),
                    'size_limit': settings.IMESSAGE_WARNING_LIMIT
                },
                'animated': {
                    'format': 'APNG',
                    'dimensions': (512, 512),
                    'size_limit': settings.IMESSAGE_WARNING_LIMIT
                }
            }
        }

    async def export_static(
        self,
        image_bytes: bytes,
        platform: PlatformType
    ) -> Tuple[bytes, Dict]:
        """
        Export static sticker for specific platform

        Args:
            image_bytes: Source image data (PNG with transparency)
            platform: Target platform

        Returns:
            Tuple of (converted image bytes, metadata dict)
        """
        try:
            specs = self.platform_specs[platform]['static']

            # Load image
            img = Image.open(io.BytesIO(image_bytes))
            img = img.convert('RGBA')

            # Ensure correct dimensions
            target_width, target_height = specs['dimensions']
            if img.size != (target_width, target_height):
                img = self._resize_with_padding(img, target_width, target_height)

            # Add white stroke for WhatsApp/Signal
            if platform in [PlatformType.WHATSAPP, PlatformType.SIGNAL]:
                img = self._add_white_stroke(img)

            # Convert to target format
            output = io.BytesIO()

            if specs['format'] == 'WEBP':
                # Try high quality first, reduce if over limit
                quality = 90
                while quality > 10:
                    output = io.BytesIO()
                    img.save(output, format='WEBP', quality=quality, method=6)
                    if output.tell() <= specs['size_limit']:
                        break
                    quality -= 10

                output.seek(0)

            elif specs['format'] == 'PNG':
                img.save(output, format='PNG', optimize=True)
                output.seek(0)

            file_size = output.tell()
            output.seek(0)

            # Check compliance
            compliant = file_size <= specs['size_limit']
            warnings = []

            if not compliant:
                warnings.append(f"File size {file_size} exceeds limit {specs['size_limit']}")

            if platform == PlatformType.IMESSAGE and file_size > specs['size_limit']:
                warnings.append(f"Large file size ({file_size} bytes) may impact performance")

            metadata = {
                'format': specs['format'],
                'file_size': file_size,
                'dimensions': f"{target_width}x{target_height}",
                'compliant': compliant,
                'warnings': warnings
            }

            logger.info(f"Exported static sticker for {platform.value}: {metadata}")
            return output.read(), metadata

        except Exception as e:
            logger.error(f"Error exporting static sticker: {str(e)}")
            raise

    async def export_animated(
        self,
        frames: List[bytes],
        platform: PlatformType,
        fps: int = 12,
        duration: float = 3.0
    ) -> Tuple[bytes, Dict]:
        """
        Export animated sticker for specific platform

        Args:
            frames: List of frame image bytes
            platform: Target platform
            fps: Frames per second
            duration: Total duration in seconds

        Returns:
            Tuple of (converted video/animation bytes, metadata dict)
        """
        try:
            specs = self.platform_specs[platform]['animated']

            # For WEBP animation (WhatsApp, Signal)
            if specs['format'] == 'WEBP':
                return await self._create_animated_webp(frames, specs, fps, duration)

            # For WEBM (Telegram)
            elif specs['format'] == 'WEBM':
                return await self._create_webm(frames, specs, fps, duration)

            # For APNG (iMessage)
            elif specs['format'] == 'APNG':
                return await self._create_apng(frames, specs, fps, duration)

            raise ValueError(f"Unsupported animation format: {specs['format']}")

        except Exception as e:
            logger.error(f"Error exporting animated sticker: {str(e)}")
            raise

    async def create_tray_icon(self, image_bytes: bytes) -> bytes:
        """
        Create tray icon for WhatsApp sticker pack

        Args:
            image_bytes: Source image

        Returns:
            96x96 PNG image bytes
        """
        try:
            img = Image.open(io.BytesIO(image_bytes))
            img = img.convert('RGBA')

            # Resize to 96x96
            img = img.resize((96, 96), Image.Resampling.LANCZOS)

            output = io.BytesIO()
            img.save(output, format='PNG', optimize=True)
            output.seek(0)

            return output.read()

        except Exception as e:
            logger.error(f"Error creating tray icon: {str(e)}")
            raise

    def _resize_with_padding(
        self,
        img: Image.Image,
        target_width: int,
        target_height: int
    ) -> Image.Image:
        """Resize image to fit dimensions with transparent padding"""
        # Calculate scaling to fit within target dimensions
        width_ratio = target_width / img.width
        height_ratio = target_height / img.height
        scale = min(width_ratio, height_ratio)

        # Resize maintaining aspect ratio
        new_width = int(img.width * scale)
        new_height = int(img.height * scale)
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Create transparent canvas
        canvas = Image.new('RGBA', (target_width, target_height), (0, 0, 0, 0))

        # Center image on canvas
        x_offset = (target_width - new_width) // 2
        y_offset = (target_height - new_height) // 2
        canvas.paste(img, (x_offset, y_offset), img)

        return canvas

    def _add_white_stroke(self, img: Image.Image, width: int = 10) -> Image.Image:
        """Add white stroke around sticker"""
        from PIL import ImageFilter

        # Get alpha channel
        alpha = img.split()[3]

        # Dilate alpha to create stroke
        dilated = alpha.filter(ImageFilter.MaxFilter(width * 2 + 1))

        # Create white stroke layer
        stroke = Image.new('RGBA', img.size, (255, 255, 255, 255))
        stroke.putalpha(dilated)

        # Composite original over stroke
        result = Image.alpha_composite(stroke, img)

        return result

    async def _create_animated_webp(
        self,
        frames: List[bytes],
        specs: Dict,
        fps: int,
        duration: float
    ) -> Tuple[bytes, Dict]:
        """Create animated WebP from frames"""
        try:
            images = [Image.open(io.BytesIO(frame)).convert('RGBA') for frame in frames]

            # Calculate frame duration in milliseconds
            frame_duration = int(1000 / fps)

            output = io.BytesIO()
            images[0].save(
                output,
                format='WEBP',
                save_all=True,
                append_images=images[1:],
                duration=frame_duration,
                loop=0,
                quality=80,
                method=6
            )
            output.seek(0)

            file_size = output.tell()
            output.seek(0)

            metadata = {
                'format': 'WEBP',
                'file_size': file_size,
                'dimensions': f"{specs['dimensions'][0]}x{specs['dimensions'][1]}",
                'fps': fps,
                'frame_count': len(frames),
                'compliant': file_size <= specs['size_limit'],
                'warnings': [] if file_size <= specs['size_limit'] else [f"Size {file_size} exceeds limit"]
            }

            return output.read(), metadata

        except Exception as e:
            logger.error(f"Error creating animated WebP: {str(e)}")
            raise

    async def _create_webm(
        self,
        frames: List[bytes],
        specs: Dict,
        fps: int,
        duration: float
    ) -> Tuple[bytes, Dict]:
        """Create WebM video for Telegram"""
        # Note: This requires ffmpeg-python
        # For MVP, return placeholder
        logger.warning("WEBM creation not yet implemented - placeholder")

        metadata = {
            'format': 'WEBM',
            'file_size': 0,
            'dimensions': f"{specs['dimensions'][0]}x{specs['dimensions'][1]}",
            'fps': fps,
            'compliant': False,
            'warnings': ['WEBM export not yet implemented']
        }

        return b'', metadata

    async def _create_apng(
        self,
        frames: List[bytes],
        specs: Dict,
        fps: int,
        duration: float
    ) -> Tuple[bytes, Dict]:
        """Create APNG for iMessage"""
        # Note: This requires apng library
        # For MVP, return placeholder
        logger.warning("APNG creation not yet implemented - placeholder")

        metadata = {
            'format': 'APNG',
            'file_size': 0,
            'dimensions': f"{specs['dimensions'][0]}x{specs['dimensions'][1]}",
            'fps': fps,
            'compliant': False,
            'warnings': ['APNG export not yet implemented']
        }

        return b'', metadata

# Singleton instance
export_service = ExportService()
