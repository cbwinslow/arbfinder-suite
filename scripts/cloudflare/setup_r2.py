#!/usr/bin/env python3
"""
Setup Cloudflare R2 Storage Buckets.

Creates and configures R2 buckets for image and data storage.
"""

import sys
import requests
from typing import Dict, Any, List
from config import CloudflareConfig, get_default_config, get_api_headers


class R2Setup:
    """Setup and manage R2 storage buckets."""
    
    def __init__(self, config: CloudflareConfig):
        self.config = config
        self.base_url = f"https://api.cloudflare.com/client/v4/accounts/{config.account_id}"
        self.headers = get_api_headers(config)
    
    def create_bucket(self, bucket_name: str) -> bool:
        """Create an R2 bucket."""
        url = f"{self.base_url}/r2/buckets"
        
        payload = {
            "name": bucket_name
        }
        
        print(f"Creating R2 bucket: {bucket_name}")
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                print(f"✅ Bucket '{bucket_name}' created successfully")
                return True
            elif response.status_code == 409:
                print(f"ℹ️  Bucket '{bucket_name}' already exists")
                return True
            else:
                print(f"❌ Failed to create bucket: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error creating bucket: {e}")
            return False
    
    def list_buckets(self) -> List[Dict[str, Any]]:
        """List all R2 buckets."""
        url = f"{self.base_url}/r2/buckets"
        
        try:
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                buckets = data.get("result", {}).get("buckets", [])
                return buckets
            else:
                print(f"❌ Failed to list buckets: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error listing buckets: {e}")
            return []
    
    def configure_cors(self, bucket_name: str) -> bool:
        """Configure CORS for bucket."""
        # Note: CORS configuration via API may not be available
        # This might need to be done via Wrangler or dashboard
        print(f"ℹ️  CORS configuration for bucket '{bucket_name}'")
        print("   Configure CORS in Cloudflare dashboard if needed:")
        print("   - Allow origins: https://yourdomain.com")
        print("   - Allow methods: GET, PUT, POST, DELETE")
        print("   - Allow headers: Content-Type, Content-Length")
        return True
    
    def setup_lifecycle_rules(self, bucket_name: str) -> bool:
        """Setup lifecycle rules for bucket."""
        print(f"ℹ️  Lifecycle rules for bucket '{bucket_name}'")
        print("   Configure in dashboard for automatic cleanup:")
        print("   - Delete incomplete multipart uploads after 7 days")
        print("   - Archive old versions after 30 days")
        return True
    
    def setup_all(self) -> bool:
        """Setup all R2 buckets."""
        print("\n🪣 Setting up R2 Storage Buckets")
        print("="*60)
        
        buckets = [
            self.config.r2_bucket_images,
            self.config.r2_bucket_data,
        ]
        
        success = True
        
        for bucket_name in buckets:
            if not self.create_bucket(bucket_name):
                success = False
            else:
                self.configure_cors(bucket_name)
                self.setup_lifecycle_rules(bucket_name)
            print()
        
        # List all buckets
        print("Current R2 Buckets:")
        existing_buckets = self.list_buckets()
        for bucket in existing_buckets:
            print(f"  - {bucket.get('name')}")
        
        if success:
            print("\n✅ R2 setup completed successfully")
            print("\n📋 Next Steps:")
            print("1. Note bucket names for wrangler.toml configuration")
            print("2. Generate R2 access keys in Cloudflare dashboard")
            print("3. Configure CORS if needed for web uploads")
            print("4. Set up lifecycle policies for cost optimization")
        else:
            print("\n❌ R2 setup encountered errors")
        
        return success


def main():
    """Main entry point."""
    config = get_default_config()
    
    if not config.validate():
        print("❌ Configuration validation failed")
        sys.exit(1)
    
    r2_setup = R2Setup(config)
    success = r2_setup.setup_all()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
