"""
AI Generation Service
Handles text-to-image, image processing, and background removal
"""
import os
import asyncio
import httpx
from typing import Optional, List, Dict
import logging
from PIL import Image
import io

from app.core.config import settings

logger = logging.getLogger(__name__)

class AIService:
    """Service for AI-powered sticker generation"""

    def __init__(self):
        self.fal_key = settings.FAL_KEY
        self.replicate_token = settings.REPLICATE_API_TOKEN

    async def generate_from_text(
        self,
        prompt: str,
        style: str = "cartoon",
        num_variants: int = 3
    ) -> List[Dict]:
        """
        Generate sticker images from text prompt using FAL AI

        Args:
            prompt: Text description of desired sticker
            style: Visual style (cartoon, anime, realistic, etc.)
            num_variants: Number of variations to generate

        Returns:
            List of generated image URLs
        """
        try:
            # Style modifiers for prompt enhancement
            style_modifiers = {
                "cartoon": "cartoon style, simple, bold lines, vibrant colors",
                "anime": "anime style, expressive, detailed",
                "realistic": "photorealistic, detailed, high quality",
                "minimal": "minimalist, simple shapes, clean design",
                "doodle": "hand-drawn doodle style, sketchy, playful"
            }

            # Enhance prompt with style
            enhanced_prompt = f"{prompt}, {style_modifiers.get(style, '')}, sticker design, isolated on transparent background, no text"

            # For MVP, we'll use FAL's FLUX Schnell model
            # In production, replace with actual FAL API call
            logger.info(f"Generating sticker with prompt: {enhanced_prompt}")

            results = []
            for i in range(num_variants):
                # Placeholder for FAL API integration
                # TODO: Replace with actual FAL API call
                result = {
                    "id": f"gen_{i}_{hash(prompt) % 10000}",
                    "image_url": f"https://placeholder.com/512x512?text=Variant+{i+1}",
                    "thumbnail_url": f"https://placeholder.com/128x128?text=Variant+{i+1}",
                    "prompt": enhanced_prompt
                }
                results.append(result)

            logger.info(f"Successfully generated {len(results)} variants")
            return results

        except Exception as e:
            logger.error(f"Error generating sticker from text: {str(e)}")
            raise

    async def remove_background(self, image_path: str) -> bytes:
        """
        Remove background from image using rembg

        Args:
            image_path: Path to source image

        Returns:
            PNG bytes with transparent background
        """
        try:
            from rembg import remove

            logger.info(f"Removing background from {image_path}")

            # Read input image
            with open(image_path, 'rb') as f:
                input_data = f.read()

            # Remove background
            output_data = remove(input_data)

            logger.info("Background removed successfully")
            return output_data

        except Exception as e:
            logger.error(f"Error removing background: {str(e)}")
            raise

    async def add_stroke(
        self,
        image_bytes: bytes,
        stroke_width: int = 10,
        stroke_color: str = "#FFFFFF"
    ) -> bytes:
        """
        Add stroke/outline to sticker

        Args:
            image_bytes: Image data
            stroke_width: Width of stroke in pixels
            stroke_color: Hex color code

        Returns:
            Modified image bytes
        """
        try:
            from PIL import Image, ImageOps, ImageDraw
            import numpy as np

            # Load image
            img = Image.open(io.BytesIO(image_bytes))
            img = img.convert('RGBA')

            # Create stroke effect
            # This is a simplified version - can be enhanced with better edge detection
            alpha = img.split()[3]

            # Dilate the alpha channel to create stroke
            from PIL import ImageFilter
            dilated = alpha.filter(ImageFilter.MaxFilter(stroke_width * 2 + 1))

            # Create stroke layer
            stroke_layer = Image.new('RGBA', img.size, stroke_color)
            stroke_layer.putalpha(dilated)

            # Composite original image over stroke
            result = Image.alpha_composite(stroke_layer, img)

            # Convert to bytes
            output = io.BytesIO()
            result.save(output, format='PNG')
            output.seek(0)

            logger.info("Stroke added successfully")
            return output.read()

        except Exception as e:
            logger.error(f"Error adding stroke: {str(e)}")
            raise

    async def create_character(
        self,
        character_description: str,
        expression: str = "neutral",
        style: str = "cartoon"
    ) -> Dict:
        """
        Create character sticker with specific expression

        Args:
            character_description: Description of character
            expression: Emotion/expression (happy, sad, angry, etc.)
            style: Visual style

        Returns:
            Generated character image data
        """
        try:
            # Enhance prompt with expression
            prompt = f"{character_description}, {expression} expression, {style} style, sticker, isolated"

            results = await self.generate_from_text(prompt, style, num_variants=1)

            if results:
                return results[0]

            raise ValueError("Character generation failed")

        except Exception as e:
            logger.error(f"Error creating character: {str(e)}")
            raise

    async def optimize_for_sticker(
        self,
        image_bytes: bytes,
        target_size: int = 512
    ) -> bytes:
        """
        Optimize image for sticker format
        - Resize to target dimensions
        - Ensure transparent background
        - Optimize file size

        Args:
            image_bytes: Source image data
            target_size: Target dimension (square)

        Returns:
            Optimized image bytes
        """
        try:
            # Load image
            img = Image.open(io.BytesIO(image_bytes))
            img = img.convert('RGBA')

            # Calculate resize dimensions (maintain aspect ratio, fit in square)
            width, height = img.size
            if width > height:
                new_width = target_size
                new_height = int(height * (target_size / width))
            else:
                new_height = target_size
                new_width = int(width * (target_size / height))

            # Resize with high-quality resampling
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Create square canvas with transparent background
            canvas = Image.new('RGBA', (target_size, target_size), (0, 0, 0, 0))

            # Center the image on canvas
            x_offset = (target_size - new_width) // 2
            y_offset = (target_size - new_height) // 2
            canvas.paste(img, (x_offset, y_offset), img)

            # Convert to bytes
            output = io.BytesIO()
            canvas.save(output, format='PNG', optimize=True)
            output.seek(0)

            logger.info(f"Image optimized to {target_size}x{target_size}")
            return output.read()

        except Exception as e:
            logger.error(f"Error optimizing image: {str(e)}")
            raise

# Singleton instance
ai_service = AIService()
