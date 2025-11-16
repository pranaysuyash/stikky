# Implementation Guide: Critical Features

Quick guide to implement the pending critical features.

## 1. Real AI Integration with FAL

### Setup FAL API
```bash
pip install fal-client
```

### Update `backend/app/services/ai_service.py`

Replace the placeholder in `generate_from_text` (line 50-70):

```python
import fal_client

async def generate_from_text(
    self,
    prompt: str,
    style: str = "cartoon",
    num_variants: int = 3
) -> List[Dict]:
    """Generate sticker images from text prompt using FAL AI"""
    try:
        # Enhance prompt with style
        enhanced_prompt = enhance_prompt_with_style(prompt, style)

        results = []

        for i in range(num_variants):
            # Call FAL API
            handler = fal_client.submit(
                "fal-ai/flux/schnell",
                arguments={
                    "prompt": enhanced_prompt,
                    "image_size": "square",
                    "num_inference_steps": 4,
                    "num_images": 1
                }
            )

            result = handler.get()

            # Extract image URL
            image_url = result["images"][0]["url"]

            # Download and process image
            async with httpx.AsyncClient() as client:
                img_response = await client.get(image_url)
                img_bytes = img_response.content

            # Remove background
            no_bg = await self.remove_background_bytes(img_bytes)

            # Add stroke
            with_stroke = await self.add_stroke(no_bg)

            # Optimize
            optimized = await self.optimize_for_sticker(with_stroke)

            # Upload to S3 and get URL
            final_url = await storage_service.upload(optimized, f"sticker_{i}.png")

            results.append({
                "id": f"gen_{uuid.uuid4()}",
                "image_url": final_url,
                "thumbnail_url": final_url,  # Or create thumbnail
                "prompt": enhanced_prompt
            })

        return results

    except Exception as e:
        logger.error(f"Error generating sticker: {str(e)}")
        raise
```

## 2. Database with SQLAlchemy

### Create Models

`backend/app/db/models.py`:

```python
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    tier = Column(String, default="free")
    credits = Column(Integer, default=50)
    monthly_exports_used = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    stickers = relationship("Sticker", back_populates="user")
    packs = relationship("Pack", back_populates="user")

class Sticker(Base):
    __tablename__ = "stickers"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"))
    image_url = Column(String, nullable=False)
    thumbnail_url = Column(String)
    prompt = Column(String)
    style = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="stickers")

class Pack(Base):
    __tablename__ = "packs"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    description = Column(String)
    platform = Column(String)
    tray_icon_url = Column(String)
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="packs")
```

### Database Connection

`backend/app/db/database.py`:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Migration

```bash
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## 3. JWT Authentication

### Install Dependencies
```bash
pip install python-jose[cryptography] passlib[bcrypt]
```

### Create Auth Service

`backend/app/core/security.py`:

```python
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

### Auth Dependency

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db = Depends(get_db)
):
    token = credentials.credentials
    payload = verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    user_id = payload.get("user_id")
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
```

## 4. S3 Storage Service

### Create Storage Service

`backend/app/services/storage_service.py`:

```python
import boto3
from app.core.config import settings
import uuid

class StorageService:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION
        )
        self.bucket = settings.S3_BUCKET

    async def upload(self, file_bytes: bytes, filename: str) -> str:
        """Upload file to S3 and return public URL"""
        try:
            # Generate unique filename
            key = f"stickers/{uuid.uuid4()}_{filename}"

            # Upload
            self.s3.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=file_bytes,
                ContentType='image/png'
            )

            # Return URL
            url = f"https://{self.bucket}.s3.{settings.S3_REGION}.amazonaws.com/{key}"
            return url

        except Exception as e:
            logger.error(f"S3 upload error: {str(e)}")
            raise

storage_service = StorageService()
```

## 5. Flutter API Client with Retrofit

### Setup
```yaml
# pubspec.yaml
dependencies:
  dio: ^5.4.0
  retrofit: ^4.0.3
  json_annotation: ^4.8.1

dev_dependencies:
  build_runner: ^2.4.7
  retrofit_generator: ^8.0.4
  json_serializable: ^6.7.1
```

### Create API Client

`frontend/lib/services/api_client.dart`:

```dart
import 'package:dio/dio.dart';
import 'package:retrofit/retrofit.dart';
import '../models/sticker_models.dart';

part 'api_client.g.dart';

@RestApi(baseUrl: "http://localhost:8000/api/v1")
abstract class ApiClient {
  factory ApiClient(Dio dio, {String baseUrl}) = _ApiClient;

  @POST("/stickers/generate/text")
  Future<GenerationResponse> generateFromText(@Body() TextToStickerRequest request);

  @POST("/stickers/generate/image")
  @MultiPart()
  Future<GenerationResponse> generateFromImage(
    @Part() File file,
    @Part() bool removeBackground,
    @Part() bool addStroke,
  );

  @POST("/exports/export")
  Future<ExportResponse> exportSticker(@Body() ExportRequest request);

  @GET("/templates/festivals")
  Future<FestivalsResponse> getFestivals();

  @GET("/templates/autocomplete")
  Future<AutocompleteResponse> autocomplete(@Query("q") String query);

  @POST("/referrals/generate")
  Future<ReferralCodeResponse> generateReferralCode(@Body() Map<String, String> body);
}
```

### Generate Code
```bash
flutter pub run build_runner build
```

### Use in App

```dart
// lib/services/api_service.dart
import 'package:dio/dio.dart';
import 'api_client.dart';

class ApiService {
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;

  late ApiClient _client;

  ApiService._internal() {
    final dio = Dio();
    dio.options.headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };

    // Add interceptor for auth token
    dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) {
        final token = getStoredToken(); // Implement this
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        return handler.next(options);
      },
    ));

    _client = ApiClient(dio);
  }

  ApiClient get client => _client;
}
```

## 6. RevenueCat Integration

### Flutter Setup

```dart
// lib/services/payment_service.dart
import 'package:purchases_flutter/purchases_flutter.dart';

class PaymentService {
  static Future<void> initialize() async {
    await Purchases.configure(
      PurchasesConfiguration("your_revenuecat_api_key")
    );
  }

  static Future<Offerings?> getOfferings() async {
    try {
      return await Purchases.getOfferings();
    } catch (e) {
      print('Error getting offerings: $e');
      return null;
    }
  }

  static Future<bool> purchasePackage(Package package) async {
    try {
      await Purchases.purchasePackage(package);
      return true;
    } catch (e) {
      print('Purchase error: $e');
      return false;
    }
  }

  static Future<CustomerInfo> getCustomerInfo() async {
    return await Purchases.getCustomerInfo();
  }

  static Future<void> restorePurchases() async {
    await Purchases.restorePurchases();
  }
}
```

## 7. Celery for Async Tasks

### Setup

```python
# backend/app/core/celery.py
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "stickercraft",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)
```

### Create Task

```python
# backend/app/tasks/sticker_tasks.py
from app.core.celery import celery_app
from app.services.ai_service import ai_service

@celery_app.task
def generate_sticker_task(prompt: str, style: str, user_id: str):
    """Background task for sticker generation"""
    result = ai_service.generate_from_text(prompt, style)
    # Save to database
    # Send notification to user
    return result

@celery_app.task
def batch_generate_festival_pack(festival: str, style: str, user_id: str):
    """Generate complete festival pack in background"""
    from app.core.templates import get_festival_pack

    prompts = get_festival_pack(festival)
    stickers = []

    for prompt in prompts:
        sticker = ai_service.generate_from_text(prompt, style, num_variants=1)
        stickers.append(sticker)

    # Create pack in database
    # Notify user
    return stickers
```

### Usage

```python
from app.tasks.sticker_tasks import generate_sticker_task

# In API endpoint
@router.post("/stickers/generate/async")
async def generate_async(request: TextToStickerRequest):
    task = generate_sticker_task.delay(
        request.prompt,
        request.style,
        current_user.id
    )

    return {
        "task_id": task.id,
        "status": "processing"
    }

@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    task = generate_sticker_task.AsyncResult(task_id)

    return {
        "task_id": task_id,
        "status": task.status,
        "result": task.result if task.ready() else None
    }
```

### Run Worker

```bash
celery -A app.core.celery worker --loglevel=info
```

## 8. WEBM Video Export for Telegram

```python
# backend/app/services/video_service.py
import ffmpeg
import tempfile
from PIL import Image

async def create_webm(frames: List[bytes], fps: int = 30) -> bytes:
    """Create WEBM video from frames"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Save frames as images
        for i, frame_bytes in enumerate(frames):
            img = Image.open(io.BytesIO(frame_bytes))
            img.save(f"{tmpdir}/frame_{i:04d}.png")

        # Use ffmpeg to create WEBM
        output_path = f"{tmpdir}/output.webm"

        (
            ffmpeg
            .input(f"{tmpdir}/frame_%04d.png", framerate=fps)
            .output(
                output_path,
                vcodec='libvpx-vp9',
                pix_fmt='yuva420p',
                **{'b:v': '0', 'crf': '30'}
            )
            .run(overwrite_output=True)
        )

        # Read output
        with open(output_path, 'rb') as f:
            return f.read()
```

## Next Steps

1. Implement these in order of priority
2. Test each feature individually
3. Write tests as you go
4. Update documentation
5. Deploy incrementally

## Quick Test Checklist

- [ ] AI generation works with real API
- [ ] Database stores user data correctly
- [ ] JWT auth protects endpoints
- [ ] File upload works to S3
- [ ] Flutter app connects to backend
- [ ] Payments work in test mode
- [ ] Celery processes tasks
- [ ] Video export creates valid WEBM
- [ ] All tests pass
- [ ] App works on real device
