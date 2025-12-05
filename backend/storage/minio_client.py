"""
MinIO client for object storage
"""

import logging
import os
from datetime import timedelta
from typing import BinaryIO, Optional

try:
    from minio import Minio
    from minio.error import S3Error

    MINIO_AVAILABLE = True
except ImportError:
    MINIO_AVAILABLE = False
    print("Warning: minio not installed. Install with: pip install minio")

logger = logging.getLogger(__name__)


class MinIOClient:
    """Client for MinIO object storage"""

    def __init__(
        self,
        endpoint: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        secure: bool = True,
    ):
        """Initialize MinIO client"""
        self.endpoint = endpoint or os.getenv("MINIO_ENDPOINT", "localhost:9000")
        self.access_key = access_key or os.getenv("MINIO_ACCESS_KEY", "")
        self.secret_key = secret_key or os.getenv("MINIO_SECRET_KEY", "")
        self.secure = secure

        if not MINIO_AVAILABLE:
            logger.warning("MinIO library not available")
            self.client = None
            return

        try:
            self.client = Minio(
                self.endpoint,
                access_key=self.access_key,
                secret_key=self.secret_key,
                secure=self.secure,
            )
            logger.info(f"MinIO client initialized: {self.endpoint}")
        except Exception as e:
            logger.error(f"Failed to initialize MinIO client: {e}")
            self.client = None

    def ensure_bucket(self, bucket_name: str) -> bool:
        """Ensure bucket exists, create if it doesn't"""
        if not self.client:
            return False

        try:
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)
                logger.info(f"Created bucket: {bucket_name}")
            return True
        except S3Error as e:
            logger.error(f"Error ensuring bucket {bucket_name}: {e}")
            return False

    def upload_file(
        self,
        bucket_name: str,
        object_name: str,
        file_data: BinaryIO,
        content_type: str = "application/octet-stream",
    ) -> Optional[str]:
        """Upload file to MinIO bucket"""
        if not self.client:
            return None

        try:
            self.ensure_bucket(bucket_name)

            # Get file size
            file_data.seek(0, 2)
            file_size = file_data.tell()
            file_data.seek(0)

            self.client.put_object(
                bucket_name,
                object_name,
                file_data,
                file_size,
                content_type=content_type,
            )

            # Generate URL
            url = f"{'https' if self.secure else 'http'}://{self.endpoint}/{bucket_name}/{object_name}"
            logger.info(f"Uploaded {object_name} to {bucket_name}")
            return url

        except S3Error as e:
            logger.error(f"Error uploading {object_name}: {e}")
            return None

    def get_presigned_url(
        self,
        bucket_name: str,
        object_name: str,
        expires: timedelta = timedelta(hours=1),
    ) -> Optional[str]:
        """Get presigned URL for object"""
        if not self.client:
            return None

        try:
            url = self.client.presigned_get_object(
                bucket_name,
                object_name,
                expires=expires,
            )
            return url
        except S3Error as e:
            logger.error(f"Error getting presigned URL: {e}")
            return None

    def delete_file(self, bucket_name: str, object_name: str) -> bool:
        """Delete file from bucket"""
        if not self.client:
            return False

        try:
            self.client.remove_object(bucket_name, object_name)
            logger.info(f"Deleted {object_name} from {bucket_name}")
            return True
        except S3Error as e:
            logger.error(f"Error deleting {object_name}: {e}")
            return False

    def list_objects(self, bucket_name: str, prefix: str = "") -> list:
        """List objects in bucket"""
        if not self.client:
            return []

        try:
            objects = self.client.list_objects(bucket_name, prefix=prefix)
            return [obj.object_name for obj in objects]
        except S3Error as e:
            logger.error(f"Error listing objects: {e}")
            return []
