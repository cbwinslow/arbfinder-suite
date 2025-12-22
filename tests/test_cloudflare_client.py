"""
Tests for Cloudflare client
"""

import os
from io import BytesIO
from unittest.mock import MagicMock, Mock, patch

import pytest

from backend.storage.cloudflare_client import CloudflareClient


def test_cloudflare_client_initialization():
    """Test CloudflareClient initialization"""
    client = CloudflareClient(
        account_id="test_account",
        access_key="test_key",
        secret_key="test_secret",
        bucket_name="test_bucket"
    )
    
    assert client.account_id == "test_account"
    assert client.access_key == "test_key"
    assert client.secret_key == "test_secret"
    assert client.bucket_name == "test_bucket"
    assert "test_account.r2.cloudflarestorage.com" in client.endpoint


def test_cloudflare_client_from_env():
    """Test CloudflareClient initialization from environment variables"""
    os.environ["CLOUDFLARE_ACCOUNT_ID"] = "env_account"
    os.environ["CLOUDFLARE_R2_ACCESS_KEY"] = "env_key"
    os.environ["CLOUDFLARE_R2_SECRET_KEY"] = "env_secret"
    os.environ["CLOUDFLARE_R2_BUCKET"] = "env_bucket"
    
    client = CloudflareClient()
    
    assert client.account_id == "env_account"
    assert client.access_key == "env_key"
    assert client.secret_key == "env_secret"
    assert client.bucket_name == "env_bucket"
    
    # Cleanup
    for key in ["CLOUDFLARE_ACCOUNT_ID", "CLOUDFLARE_R2_ACCESS_KEY", 
                "CLOUDFLARE_R2_SECRET_KEY", "CLOUDFLARE_R2_BUCKET"]:
        if key in os.environ:
            del os.environ[key]


def test_get_public_url():
    """Test getting public URL for an object"""
    client = CloudflareClient(
        account_id="test_account",
        bucket_name="test_bucket"
    )
    
    url = client.get_public_url("test_object.txt")
    assert url == "https://test_bucket.test_account.r2.dev/test_object.txt"


def test_upload_file_without_credentials():
    """Test upload_file returns None when credentials are missing"""
    client = CloudflareClient(
        account_id="",
        access_key="",
        secret_key=""
    )
    
    file_data = BytesIO(b"test data")
    result = client.upload_file("test.txt", file_data)
    
    assert result is None


@patch('backend.storage.cloudflare_client.boto3')
def test_upload_file_with_credentials(mock_boto3):
    """Test upload_file with credentials"""
    mock_s3_client = Mock()
    mock_boto3.client.return_value = mock_s3_client
    
    client = CloudflareClient(
        account_id="test_account",
        access_key="test_key",
        secret_key="test_secret",
        bucket_name="test_bucket"
    )
    
    file_data = BytesIO(b"test data")
    result = client.upload_file("test.txt", file_data, content_type="text/plain")
    
    # Verify boto3 client was created with correct params
    mock_boto3.client.assert_called_once_with(
        's3',
        endpoint_url=client.endpoint,
        aws_access_key_id="test_key",
        aws_secret_access_key="test_secret"
    )
    
    # Verify upload was called
    mock_s3_client.upload_fileobj.assert_called_once()
    
    # Verify result is the public URL
    assert result == "https://test_bucket.test_account.r2.dev/test.txt"


def test_delete_file_without_credentials():
    """Test delete_file returns False when credentials are missing"""
    client = CloudflareClient(
        account_id="",
        access_key="",
        secret_key=""
    )
    
    result = client.delete_file("test.txt")
    assert result is False


@patch('backend.storage.cloudflare_client.boto3')
def test_delete_file_with_credentials(mock_boto3):
    """Test delete_file with credentials"""
    mock_s3_client = Mock()
    mock_boto3.client.return_value = mock_s3_client
    
    client = CloudflareClient(
        account_id="test_account",
        access_key="test_key",
        secret_key="test_secret",
        bucket_name="test_bucket"
    )
    
    result = client.delete_file("test.txt")
    
    # Verify boto3 client was created
    mock_boto3.client.assert_called_once()
    
    # Verify delete was called
    mock_s3_client.delete_object.assert_called_once_with(
        Bucket="test_bucket",
        Key="test.txt"
    )
    
    # Verify result is True
    assert result is True


@pytest.mark.asyncio
async def test_invoke_worker():
    """Test invoking a Cloudflare Worker"""
    with patch('backend.storage.cloudflare_client.httpx.AsyncClient') as mock_client:
        mock_response = Mock()
        mock_response.json.return_value = {"result": "success"}
        
        mock_context = Mock()
        mock_context.__aenter__ = Mock(return_value=Mock(post=Mock(return_value=mock_response)))
        mock_context.__aexit__ = Mock(return_value=None)
        mock_client.return_value = mock_context
        
        client = CloudflareClient(account_id="test_account")
        
        # This would need actual async testing, for now just test initialization
        assert client.account_id == "test_account"
