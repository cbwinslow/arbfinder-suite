"""
Cloudflare R2 and Workers client
"""

import logging
import os
from typing import BinaryIO, Optional

import httpx

logger = logging.getLogger(__name__)


class CloudflareClient:
    """Client for Cloudflare R2 storage and Workers"""

    def __init__(
        self,
        account_id: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        bucket_name: Optional[str] = None,
    ):
        """Initialize Cloudflare client"""
        self.account_id = account_id or os.getenv("CLOUDFLARE_ACCOUNT_ID", "")
        self.access_key = access_key or os.getenv("CLOUDFLARE_R2_ACCESS_KEY", "")
        self.secret_key = secret_key or os.getenv("CLOUDFLARE_R2_SECRET_KEY", "")
        self.bucket_name = bucket_name or os.getenv("CLOUDFLARE_R2_BUCKET", "arbfinder")

        # R2 endpoint format: https://<account_id>.r2.cloudflarestorage.com
        self.endpoint = f"https://{self.account_id}.r2.cloudflarestorage.com"

        logger.info(f"Cloudflare client initialized for account: {self.account_id}")

    def upload_file(
        self,
        object_name: str,
        file_data: BinaryIO,
        content_type: str = "application/octet-stream",
    ) -> Optional[str]:
        """Upload file to Cloudflare R2 bucket using boto3 S3-compatible API"""
        try:
            if not all([self.account_id, self.access_key, self.secret_key]):
                logger.warning("Cloudflare R2 credentials not configured, skipping upload")
                return None

            # R2 is S3-compatible, use boto3
            try:
                import boto3
                from botocore.exceptions import ClientError
            except ImportError:
                logger.error("boto3 not installed. Install with: pip install boto3")
                return None

            # Create S3 client with R2 endpoint
            s3 = boto3.client(
                's3',
                endpoint_url=self.endpoint,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
            )

            # Upload file
            s3.upload_fileobj(
                file_data,
                self.bucket_name,
                object_name,
                ExtraArgs={'ContentType': content_type}
            )

            logger.info(f"Successfully uploaded {object_name} to Cloudflare R2")
            public_url = self.get_public_url(object_name)
            return public_url

        except Exception as e:
            logger.error(f"Error uploading to Cloudflare R2: {e}")
            return None

    def get_public_url(self, object_name: str) -> str:
        """Get public URL for object"""
        return f"https://{self.bucket_name}.{self.account_id}.r2.dev/{object_name}"

    def delete_file(self, object_name: str) -> bool:
        """Delete file from R2 bucket using boto3 S3-compatible API"""
        try:
            if not all([self.account_id, self.access_key, self.secret_key]):
                logger.warning("Cloudflare R2 credentials not configured, skipping delete")
                return False

            try:
                import boto3
                from botocore.exceptions import ClientError
            except ImportError:
                logger.error("boto3 not installed. Install with: pip install boto3")
                return False

            # Create S3 client with R2 endpoint
            s3 = boto3.client(
                's3',
                endpoint_url=self.endpoint,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
            )

            # Delete file
            s3.delete_object(Bucket=self.bucket_name, Key=object_name)
            logger.info(f"Successfully deleted {object_name} from Cloudflare R2")
            return True

        except Exception as e:
            logger.error(f"Error deleting from Cloudflare R2: {e}")
            return False

    async def invoke_worker(
        self,
        worker_name: str,
        payload: dict,
        worker_url: Optional[str] = None,
    ) -> Optional[dict]:
        """Invoke a Cloudflare Worker"""
        try:
            url = worker_url or f"https://{worker_name}.{self.account_id}.workers.dev"

            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"Error invoking Cloudflare Worker: {e}")
            return None
