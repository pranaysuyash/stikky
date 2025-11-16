# StickerCraft: AI-Powered Cross-Platform Sticker Creator

**Version 1.0** | Built with Flutter & FastAPI

## Overview
StickerCraft is a playful, AI-first mobile app that enables users to create custom stickers for WhatsApp, Telegram, Signal, and iMessage with zero design skills. Turn photos, text prompts, and selfies into platform-compliant stickers in seconds using generative AI.

## Features
- 🎨 **AI-Powered Generation**: Text-to-sticker and photo-to-sticker with background removal
- 🎭 **Character Maker**: Create recurring characters with pose control
- ✨ **Smart Editor**: Real-time layers, strokes, and effects
- 📱 **Multi-Platform Export**: Auto-optimized for WhatsApp, Telegram, Signal, and iMessage
- 💰 **Flexible Monetization**: Credit-based system with subscription tiers
- 🌏 **Regional Focus**: India-first with Hinglish templates and festival packs

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Queue**: Redis for async job processing
- **AI**: FAL/Replicate APIs for generation
- **Storage**: Cloudflare R2 / AWS S3
- **Deployment**: Google Cloud Run

### Frontend
- **Framework**: Flutter (Dart 3.0+)
- **State Management**: Riverpod
- **UI**: Material Design 3 with custom theme
- **Payments**: RevenueCat + Stripe

## Project Structure
```
stikky/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── core/        # Config, security
│   │   ├── models/      # Data models
│   │   ├── services/    # Business logic
│   │   └── utils/       # Helpers
│   ├── requirements.txt
│   └── main.py
├── frontend/            # Flutter app
│   ├── lib/
│   │   ├── screens/    # UI screens
│   │   ├── widgets/    # Reusable widgets
│   │   ├── services/   # API clients
│   │   └── models/     # Data models
│   └── pubspec.yaml
├── docker/             # Docker configs
└── docs/              # Documentation
```

## Quick Start

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Setup
```bash
cd frontend
flutter pub get
flutter run
```

### Docker Setup
```bash
docker-compose up -d
```

## Environment Variables

Create `.env` file in backend/:
```env
# AI Services
FAL_KEY=your_fal_api_key
REPLICATE_API_TOKEN=your_replicate_token

# Storage
S3_BUCKET=your_bucket_name
S3_ACCESS_KEY=your_access_key
S3_SECRET_KEY=your_secret_key

# Redis
REDIS_URL=redis://localhost:6379

# Payments
STRIPE_SECRET_KEY=your_stripe_key
REVENUECAT_API_KEY=your_revenuecat_key
```

## Platform Export Specifications

| Platform | Format | Size Limit | Dimensions |
|----------|--------|------------|------------|
| WhatsApp | WebP | ≤100KB (static), ≤500KB (animated) | 512x512 |
| Telegram | WebP/WEBM | ≤512KB (static), ≤256KB (animated) | 512x512 |
| Signal | WebP | Same as WhatsApp | 512x512 |
| iMessage | PNG/APNG | ~1MB (warning) | Flexible |

## Pricing Tiers

- **Free**: 30 static exports/month, basic styles
- **Creator** (₹199/mo): Unlimited static, 200 AI credits, 50 animated exports
- **Pro** (₹499/mo): 1,000 AI credits, LoRA blending, marketplace access

## Development Roadmap

### Phase 1: MVP (Current)
- [x] Project setup
- [ ] AI generation pipeline
- [ ] Platform export system
- [ ] Basic Flutter UI
- [ ] Payment integration

### Phase 2: Scale
- [ ] GPU optimization
- [ ] Marketplace
- [ ] Advanced animations
- [ ] Regional templates

## Contributing
Contributions are welcome! Please read our contributing guidelines first.

## License
Proprietary - All rights reserved

## Contact
For questions: [Your Contact Info]

---
*Built for Pranay | November 2025*
