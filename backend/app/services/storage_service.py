"""
Storage Service
Handles file uploads to local storage or cloud (S3/R2)
"""
import os
import uuid
import aiofiles
from typing import Optional, Tuple
from pathlib import Path
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

class StorageService:
    """Unified storage service supporting local and cloud storage"""

    def __init__(self):
        self.storage_type = settings.STORAGE_TYPE
        self.upload_dir = Path(settings.UPLOAD_DIR)

        # Ensure upload directory exists
        self.upload_dir.mkdir(parents=True, exist_ok=True)

        # Initialize cloud storage if needed
        if self.storage_type in ["s3", "r2"]:
            self._init_s3()
        elif self.storage_type == "cloudinary":
            self._init_cloudinary()

    def _init_s3(self):
        """Initialize S3/R2 client"""
        try:
            import boto3
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.S3_ACCESS_KEY,
                aws_secret_access_key=settings.S3_SECRET_KEY,
                region_name=settings.S3_REGION,
                endpoint_url=f"https://{settings.S3_REGION}.r2.cloudflarestorage.com" if self.storage_type == "r2" else None
            )
            self.bucket_name = settings.S3_BUCKET
            logger.info(f"Initialized {self.storage_type.upper()} storage")
        except Exception as e:
            logger.error(f"Failed to initialize S3: {str(e)}")
            self.storage_type = "local"  # Fallback to local

    def _init_cloudinary(self):
        """Initialize Cloudinary"""
        try:
            import cloudinary
            import cloudinary.uploader

            cloudinary.config(
                cloud_name=settings.CLOUDINARY_CLOUD_NAME,
                api_key=settings.CLOUDINARY_API_KEY,
                api_secret=settings.CLOUDINARY_API_SECRET
            )
            self.cloudinary = cloudinary
            logger.info("Initialized Cloudinary storage")
        except Exception as e:
            logger.error(f"Failed to initialize Cloudinary: {str(e)}")
            self.storage_type = "local"

    async def upload(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: str = "image/png",
        folder: str = "stickers"
    ) -> Tuple[str, int]:
        """
        Upload file to storage

        Args:
            file_bytes: File content as bytes
            filename: Original filename
            content_type: MIME type
            folder: Subfolder to organize files

        Returns:
            Tuple of (public_url, file_size)
        """
        try:
            # Generate unique filename
            file_ext = Path(filename).suffix or ".png"
            unique_filename = f"{uuid.uuid4().hex}{file_ext}"

            file_size = len(file_bytes)

            if self.storage_type == "local":
                return await self._upload_local(file_bytes, unique_filename, folder, file_size)

            elif self.storage_type in ["s3", "r2"]:
                return await self._upload_s3(file_bytes, unique_filename, content_type, folder, file_size)

            elif self.storage_type == "cloudinary":
                return await self._upload_cloudinary(file_bytes, unique_filename, folder, file_size)

            else:
                raise ValueError(f"Unknown storage type: {self.storage_type}")

        except Exception as e:
            logger.error(f"Upload failed: {str(e)}")
            raise

    async def _upload_local(
        self,
        file_bytes: bytes,
        filename: str,
        folder: str,
        file_size: int
    ) -> Tuple[str, int]:
        """Upload to local filesystem"""
        # Create folder if needed
        folder_path = self.upload_dir / folder
        folder_path.mkdir(parents=True, exist_ok=True)

        # Write file
        file_path = folder_path / filename

        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_bytes)

        # Generate URL (in production, serve via CDN)
        public_url = f"/uploads/{folder}/{filename}"

        logger.info(f"Uploaded {filename} to local storage ({file_size} bytes)")

        return public_url, file_size

    async def _upload_s3(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: str,
        folder: str,
        file_size: int
    ) -> Tuple[str, int]:
        """Upload to S3/R2"""
        key = f"{folder}/{filename}"

        # Upload to S3
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=file_bytes,
            ContentType=content_type,
            ACL='public-read'  # Make publicly accessible
        )

        # Generate public URL
        public_url = f"https://{self.bucket_name}.s3.{settings.S3_REGION}.amazonaws.com/{key}"

        logger.info(f"Uploaded {filename} to S3 ({file_size} bytes)")

        return public_url, file_size

    async def _upload_cloudinary(
        self,
        file_bytes: bytes,
        filename: str,
        folder: str,
        file_size: int
    ) -> Tuple[str, int]:
        """Upload to Cloudinary"""
        result = self.cloudinary.uploader.upload(
            file_bytes,
            public_id=filename,
            folder=folder,
            resource_type="image"
        )

        public_url = result.get('secure_url')

        logger.info(f"Uploaded {filename} to Cloudinary ({file_size} bytes)")

        return public_url, file_size

    async def delete(self, file_url: str) -> bool:
        """
        Delete file from storage

        Args:
            file_url: URL or path of file to delete

        Returns:
            True if successful
        """
        try:
            if self.storage_type == "local":
                # Extract path from URL
                path_parts = file_url.split("/uploads/")
                if len(path_parts) == 2:
                    file_path = self.upload_dir / path_parts[1]
                    if file_path.exists():
                        file_path.unlink()
                        logger.info(f"Deleted local file: {file_url}")
                        return True

            elif self.storage_type in ["s3", "r2"]:
                # Extract key from URL
                key = file_url.split(f"{self.bucket_name}/")[-1]
                self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
                logger.info(f"Deleted S3 file: {file_url}")
                return True

            elif self.storage_type == "cloudinary":
                # Extract public_id
                public_id = file_url.split("/")[-1].split(".")[0]
                self.cloudinary.uploader.destroy(public_id)
                logger.info(f"Deleted Cloudinary file: {file_url}")
                return True

            return False

        except Exception as e:
            logger.error(f"Delete failed: {str(e)}")
            return False

    async def get_url(self, file_path: str, expires_in: int = 3600) -> str:
        """
        Get signed URL for private file

        Args:
            file_path: Path to file
            expires_in: URL expiration time in seconds

        Returns:
            Signed URL
        """
        if self.storage_type in ["s3", "r2"]:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': file_path},
                ExpiresIn=expires_in
            )
            return url

        # For local/cloudinary, just return the path
        return file_path

# Singleton instance
storage_service = StorageService()
