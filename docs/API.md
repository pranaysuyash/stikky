# StickerCraft API Documentation

Base URL: `http://localhost:8000/api/v1`

## Authentication

Currently using simple token-based authentication. Include in headers:
```
Authorization: Bearer {token}
```

## Endpoints

### Stickers

#### Generate from Text
```http
POST /stickers/generate/text
Content-Type: application/json

{
  "prompt": "angry cat with coffee cup, cartoon style",
  "style": "cartoon",
  "num_variants": 3
}
```

**Response:**
```json
{
  "job_id": "uuid",
  "status": "completed",
  "variants": [
    {
      "id": "variant_id",
      "image_url": "https://...",
      "thumbnail_url": "https://..."
    }
  ],
  "message": "Generated 3 sticker variants"
}
```

#### Generate from Image
```http
POST /stickers/generate/image
Content-Type: multipart/form-data

file: <binary>
remove_background: true
add_stroke: true
stroke_width: 10
```

#### Create Character
```http
POST /stickers/generate/character
Content-Type: application/json

{
  "character_name": "My Avatar",
  "base_description": "friendly robot with blue eyes",
  "expression": "happy",
  "style": "cartoon"
}
```

#### Edit Sticker
```http
POST /stickers/edit
Content-Type: application/json

{
  "sticker_id": "uuid",
  "text_layers": [
    {
      "text": "Hello!",
      "font_size": 48,
      "color": "#000000",
      "position_x": 0.5,
      "position_y": 0.8,
      "rotation": 0
    }
  ],
  "stroke_width": 12,
  "stroke_color": "#FFFFFF"
}
```

### Exports

#### Export to Platforms
```http
POST /exports/export
Content-Type: application/json

{
  "sticker_id": "uuid",
  "platforms": ["whatsapp", "telegram", "signal"],
  "sticker_type": "static",
  "fps": 12,
  "duration": 3.0
}
```

**Response:**
```json
{
  "sticker_id": "uuid",
  "exports": [
    {
      "platform": "whatsapp",
      "format": "WEBP",
      "file_url": "/uploads/...",
      "file_size": 98304,
      "dimensions": "512x512",
      "compliant": true,
      "warnings": []
    }
  ],
  "total_size": 294912,
  "message": "Successfully exported to 3 platform(s)"
}
```

#### Create Tray Icon
```http
POST /exports/tray-icon?sticker_id=uuid
```

#### Get Platform Specs
```http
GET /exports/specs/{platform}
```

Platforms: `whatsapp`, `telegram`, `signal`, `imessage`

### Packs

#### Create Pack
```http
POST /packs/
Content-Type: application/json

{
  "name": "My Awesome Pack",
  "description": "Collection of cool stickers",
  "platform": "whatsapp",
  "sticker_ids": ["uuid1", "uuid2", "uuid3"]
}
```

#### List Packs
```http
GET /packs/?platform=whatsapp&limit=20&offset=0
```

#### Get Pack
```http
GET /packs/{pack_id}
```

#### Publish Pack
```http
PUT /packs/{pack_id}/publish
```

#### Add Sticker to Pack
```http
POST /packs/{pack_id}/stickers?sticker_id=uuid
```

### Users

#### Register
```http
POST /users/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "cooluser",
  "password": "securepassword123"
}
```

#### Login
```http
POST /users/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

#### Get Profile
```http
GET /users/me
```

#### Get Credits
```http
GET /users/credits
```

**Response:**
```json
{
  "user_id": "uuid",
  "credits": 50,
  "tier": "free",
  "monthly_exports_used": 5,
  "monthly_exports_limit": 30,
  "credits_used_this_month": 10
}
```

#### Get Subscription Tiers
```http
GET /users/tiers
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid credentials"
}
```

### 402 Payment Required
```json
{
  "detail": "Insufficient credits"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Style Presets

Available styles for sticker generation:
- `cartoon` - Cartoon style with bold lines and vibrant colors
- `anime` - Anime/manga style
- `realistic` - Photorealistic rendering
- `minimal` - Minimalist, simple shapes
- `doodle` - Hand-drawn, sketchy style

## Platform Specifications

### WhatsApp
- **Static**: WebP, 512x512, ≤100KB
- **Animated**: WebP, 512x512, ≤500KB, ≤3s
- **Tray Icon**: 96x96 PNG required
- **Pack Size**: 3-30 stickers

### Telegram
- **Static**: WebP, 512x512, ≤512KB
- **Animated**: WEBM VP9, 512x512, ≤256KB, ≤3s, 30fps
- **Pack Size**: Unlimited

### Signal
- **Static**: WebP, 512x512, ≤100KB
- **Animated**: WebP, 512x512, ≤500KB, ≤3s
- Same as WhatsApp specs

### iMessage
- **Static**: PNG, flexible size
- **Animated**: APNG
- **Size Warning**: >1MB may impact performance

## Rate Limits

- **Free Tier**: 60 requests/minute
- **Creator Tier**: 120 requests/minute
- **Pro Tier**: 300 requests/minute

## Credits System

### Credit Costs
- Text-to-sticker generation: 1 credit
- Image-to-sticker conversion: 1 credit
- Character creation: 1 credit
- Animated export: 1 credit per platform
- Static export: No credit cost (counted in monthly limit)

### Monthly Limits
- **Free**: 30 static exports, 50 AI credits
- **Creator**: Unlimited static, 200 AI credits, 50 animated
- **Pro**: Unlimited everything, 1000 AI credits
