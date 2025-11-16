# StickerCraft Deployment Guide

## Development Setup

### Prerequisites
- Python 3.11+
- Flutter SDK 3.0+
- Docker & Docker Compose
- Redis
- PostgreSQL (optional, SQLite works for dev)

### Backend Setup

1. **Clone and navigate to backend**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and settings
   ```

5. **Run development server**
   ```bash
   uvicorn main:app --reload
   ```

   API will be available at `http://localhost:8000`
   Docs at `http://localhost:8000/api/docs`

### Frontend Setup

1. **Navigate to frontend**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   flutter pub get
   ```

3. **Run on device/emulator**
   ```bash
   flutter run
   ```

### Docker Development

Run entire stack with Docker Compose:

```bash
docker-compose up -d
```

This starts:
- Backend API on port 8000
- Redis on port 6379
- PostgreSQL on port 5432
- Celery worker for async tasks

## Production Deployment

### Google Cloud Run (Recommended)

#### Backend Deployment

1. **Build container**
   ```bash
   cd backend
   docker build -t stickercraft-api .
   ```

2. **Tag for GCR**
   ```bash
   docker tag stickercraft-api gcr.io/YOUR_PROJECT/stickercraft-api
   ```

3. **Push to Google Container Registry**
   ```bash
   docker push gcr.io/YOUR_PROJECT/stickercraft-api
   ```

4. **Deploy to Cloud Run**
   ```bash
   gcloud run deploy stickercraft-api \
     --image gcr.io/YOUR_PROJECT/stickercraft-api \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --memory 2Gi \
     --cpu 2 \
     --min-instances 1 \
     --max-instances 10 \
     --set-env-vars "REDIS_URL=redis://..." \
     --set-env-vars "FAL_KEY=..." \
     --set-env-vars "STRIPE_SECRET_KEY=..."
   ```

5. **Set up Cloud SQL (PostgreSQL)**
   ```bash
   gcloud sql instances create stickercraft-db \
     --database-version=POSTGRES_14 \
     --cpu=2 \
     --memory=4GB \
     --region=us-central1
   ```

6. **Configure Redis**
   - Use Google Cloud Memorystore for Redis
   - Or external Redis provider (Upstash, Redis Cloud)

#### Frontend Deployment

1. **Build Flutter web**
   ```bash
   cd frontend
   flutter build web
   ```

2. **Deploy to Firebase Hosting**
   ```bash
   firebase init hosting
   firebase deploy
   ```

3. **Or deploy to Cloudflare Pages**
   - Connect GitHub repo
   - Set build command: `flutter build web`
   - Set output directory: `build/web`

### AWS Deployment

#### Backend on ECS

1. **Create ECR repository**
   ```bash
   aws ecr create-repository --repository-name stickercraft-api
   ```

2. **Build and push**
   ```bash
   docker build -t stickercraft-api .
   docker tag stickercraft-api:latest AWS_ACCOUNT.dkr.ecr.REGION.amazonaws.com/stickercraft-api:latest
   docker push AWS_ACCOUNT.dkr.ecr.REGION.amazonaws.com/stickercraft-api:latest
   ```

3. **Create ECS task definition and service**
   - Use Fargate for serverless container orchestration
   - Configure environment variables
   - Set up load balancer

4. **Configure RDS for PostgreSQL**

5. **Set up ElastiCache for Redis**

### Environment Variables (Production)

Required environment variables:

```bash
# Core
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=<generate-strong-key>

# AI Services
FAL_KEY=<your-fal-key>
REPLICATE_API_TOKEN=<your-token>

# Storage (use S3/R2 in production)
STORAGE_TYPE=s3
S3_BUCKET=stickercraft-assets
S3_ACCESS_KEY=<access-key>
S3_SECRET_KEY=<secret-key>
S3_REGION=us-east-1

# Database
DATABASE_URL=postgresql://user:pass@host:5432/stickercraft

# Redis
REDIS_URL=redis://host:6379

# Payments
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
REVENUECAT_API_KEY=<key>

# CORS
ALLOWED_ORIGINS=https://stickercraft.app,https://www.stickercraft.app
```

### Security Checklist

- [ ] Change SECRET_KEY to strong random value
- [ ] Set DEBUG=False in production
- [ ] Configure HTTPS/SSL certificates
- [ ] Set up CORS properly with allowed origins
- [ ] Enable rate limiting
- [ ] Set up API authentication/authorization
- [ ] Configure secure database passwords
- [ ] Enable Redis password/ACL
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy
- [ ] Enable DDoS protection (Cloudflare)
- [ ] Set up error tracking (Sentry)

### Monitoring & Logging

#### Recommended Tools

1. **Application Monitoring**
   - Sentry for error tracking
   - New Relic or DataDog for APM

2. **Logging**
   - Google Cloud Logging (GCP)
   - CloudWatch (AWS)
   - Structured JSON logging

3. **Uptime Monitoring**
   - UptimeRobot
   - Pingdom

#### Health Checks

API provides health endpoint:
```
GET /health
```

Configure monitoring to check this endpoint every 30s.

### Scaling Considerations

1. **Horizontal Scaling**
   - Cloud Run auto-scales based on traffic
   - Set min/max instances appropriately

2. **Database**
   - Use connection pooling
   - Configure read replicas for heavy read workloads

3. **Redis**
   - Use cluster mode for high availability
   - Configure persistence (AOF/RDB)

4. **Storage**
   - Use CDN (Cloudflare/CloudFront) for asset delivery
   - Configure object lifecycle policies

5. **Queue Workers**
   - Run multiple Celery workers
   - Monitor queue depth
   - Auto-scale based on queue size

### Cost Optimization

1. **Compute**
   - Use auto-scaling to match demand
   - Set appropriate min instances (0 or 1)
   - Use spot instances for workers (AWS)

2. **Storage**
   - Configure object expiration policies
   - Use cheaper storage tiers for old assets
   - Compress images/videos

3. **AI API Costs**
   - Cache common generations
   - Implement rate limiting
   - Monitor per-user usage

4. **Database**
   - Right-size instance
   - Archive old data
   - Use connection pooling

### Backup Strategy

1. **Database**
   - Automated daily backups
   - Point-in-time recovery enabled
   - Test restore procedure monthly

2. **User Assets**
   - Replicate to multiple regions
   - Versioning enabled
   - 30-day retention policy

3. **Configuration**
   - Store configs in version control
   - Use secret management (GCP Secret Manager, AWS Secrets Manager)

### CI/CD Pipeline

Example GitHub Actions workflow:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build and push Docker image
        run: |
          docker build -t gcr.io/$PROJECT/stickercraft-api .
          docker push gcr.io/$PROJECT/stickercraft-api

      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy stickercraft-api \
            --image gcr.io/$PROJECT/stickercraft-api \
            --region us-central1
```

## Mobile App Distribution

### iOS

1. **Configure signing**
   - Create App ID in Apple Developer Portal
   - Configure provisioning profiles
   - Set up RevenueCat for IAP

2. **Build for App Store**
   ```bash
   flutter build ios --release
   ```

3. **Submit via Xcode or Fastlane**

### Android

1. **Configure signing**
   - Generate keystore
   - Configure in `android/key.properties`

2. **Build AAB**
   ```bash
   flutter build appbundle --release
   ```

3. **Submit to Google Play Console**

### Code Push Updates

Consider using:
- Shorebird for Flutter (OTA updates)
- Firebase App Distribution for beta testing
