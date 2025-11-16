"""
Sticker Data Models
Pydantic models for sticker creation and export
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Literal
from enum import Enum

class PlatformType(str, Enum):
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    SIGNAL = "signal"
    IMESSAGE = "imessage"

class StickerType(str, Enum):
    STATIC = "static"
    ANIMATED = "animated"

class GenerationType(str, Enum):
    TEXT_TO_IMAGE = "text_to_image"
    IMAGE_TO_STICKER = "image_to_sticker"
    CHARACTER_MAKER = "character_maker"

class StylePreset(str, Enum):
    CARTOON = "cartoon"
    ANIME = "anime"
    REALISTIC = "realistic"
    MINIMAL = "minimal"
    DOODLE = "doodle"

# Request Models
class TextToStickerRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=200)
    style: StylePreset = StylePreset.CARTOON
    num_variants: int = Field(default=3, ge=1, le=4)

    @validator('prompt')
    def validate_prompt(cls, v):
        if len(v.strip()) == 0:
            raise ValueError('Prompt cannot be empty')
        return v.strip()

class ImageToStickerRequest(BaseModel):
    image_url: Optional[str] = None
    remove_background: bool = True
    add_stroke: bool = True
    stroke_width: int = Field(default=10, ge=6, le=14)
    stroke_color: str = "#FFFFFF"

class CharacterMakerRequest(BaseModel):
    character_name: str = Field(..., min_length=1, max_length=50)
    base_description: str = Field(..., min_length=10, max_length=200)
    expression: str = Field(default="neutral")
    style: StylePreset = StylePreset.CARTOON

class TextLayer(BaseModel):
    text: str = Field(..., max_length=50)
    font_size: int = Field(default=48, ge=20, le=72)
    color: str = "#000000"
    position_x: float = Field(default=0.5, ge=0, le=1)  # Normalized 0-1
    position_y: float = Field(default=0.5, ge=0, le=1)
    rotation: int = Field(default=0, ge=-180, le=180)

class StickerEditRequest(BaseModel):
    sticker_id: str
    text_layers: List[TextLayer] = []
    stroke_width: Optional[int] = Field(None, ge=6, le=14)
    stroke_color: Optional[str] = None
    background_color: Optional[str] = None

class ExportRequest(BaseModel):
    sticker_id: str
    platforms: List[PlatformType] = Field(..., min_items=1)
    sticker_type: StickerType = StickerType.STATIC
    fps: Optional[int] = Field(12, ge=4, le=30)
    duration: Optional[float] = Field(3.0, ge=1.0, le=3.0)

# Response Models
class StickerGeneration(BaseModel):
    id: str
    type: GenerationType
    status: Literal["pending", "processing", "completed", "failed"]
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    error: Optional[str] = None
    created_at: str

class StickerVariant(BaseModel):
    id: str
    image_url: str
    thumbnail_url: str

class GenerationResponse(BaseModel):
    job_id: str
    status: str
    variants: List[StickerVariant] = []
    message: str

class PlatformExport(BaseModel):
    platform: PlatformType
    format: str
    file_url: str
    file_size: int
    dimensions: str
    compliant: bool
    warnings: List[str] = []

class ExportResponse(BaseModel):
    sticker_id: str
    exports: List[PlatformExport]
    total_size: int
    message: str

class CreditBalance(BaseModel):
    user_id: str
    credits: int
    tier: Literal["free", "creator", "pro"]
    monthly_exports_used: int
    monthly_exports_limit: int
    credits_used_this_month: int

# Sticker Pack Models
class StickerPack(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    tray_icon_url: Optional[str] = None
    sticker_ids: List[str] = []
    platform: PlatformType
    is_published: bool = False
    created_at: str
    updated_at: str

class CreatePackRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    platform: PlatformType
    sticker_ids: List[str] = Field(..., min_items=3, max_items=30)
