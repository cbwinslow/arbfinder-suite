"""
Cloudflare Configuration Management.

Centralized configuration for all Cloudflare setup scripts.
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
import json


# Global API key placeholder - should be set via environment variable
CLOUDFLARE_API_KEY = os.getenv("CLOUDFLARE_API_KEY", "")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN", "")
CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID", "")
CLOUDFLARE_ZONE_ID = os.getenv("CLOUDFLARE_ZONE_ID", "")
CLOUDFLARE_EMAIL = os.getenv("CLOUDFLARE_EMAIL", "")


@dataclass
class CloudflareConfig:
    """Cloudflare configuration settings."""
    
    # Authentication
    api_key: str = field(default_factory=lambda: CLOUDFLARE_API_KEY)
    api_token: str = field(default_factory=lambda: CLOUDFLARE_API_TOKEN)
    account_id: str = field(default_factory=lambda: CLOUDFLARE_ACCOUNT_ID)
    zone_id: str = field(default_factory=lambda: CLOUDFLARE_ZONE_ID)
    email: str = field(default_factory=lambda: CLOUDFLARE_EMAIL)
    
    # Project settings
    project_name: str = "arbfinder"
    environment: str = "production"
    
    # Workers configuration
    worker_name: str = "arbfinder-worker"
    worker_subdomain: str = "arbfinder"
    
    # Pages configuration
    pages_project: str = "arbfinder-pages"
    pages_domain: str = "arbfinder.pages.dev"
    
    # R2 configuration
    r2_bucket_images: str = "arbfinder-images"
    r2_bucket_data: str = "arbfinder-data"
    
    # D1 configuration
    d1_database_name: str = "arbfinder-d1"
    
    # KV configuration
    kv_namespace_cache: str = "arbfinder-cache"
    kv_namespace_config: str = "arbfinder-config"
    
    # WAF configuration
    waf_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_period: int = 60
    
    # Observability
    enable_logging: bool = True
    log_retention_days: int = 30
    
    def validate(self) -> bool:
        """Validate required configuration."""
        required = [
            ("API Token", self.api_token),
            ("Account ID", self.account_id),
        ]
        
        missing = [name for name, value in required if not value]
        
        if missing:
            print(f"❌ Missing required configuration: {', '.join(missing)}")
            return False
        
        print("✅ Configuration validated successfully")
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "project_name": self.project_name,
            "environment": self.environment,
            "worker_name": self.worker_name,
            "pages_project": self.pages_project,
            "r2_bucket_images": self.r2_bucket_images,
            "r2_bucket_data": self.r2_bucket_data,
            "d1_database_name": self.d1_database_name,
            "kv_namespace_cache": self.kv_namespace_cache,
            "kv_namespace_config": self.kv_namespace_config,
        }
    
    def save_to_file(self, filepath: str) -> None:
        """Save configuration to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
        print(f"✅ Configuration saved to {filepath}")
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'CloudflareConfig':
        """Load configuration from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls(**data)


def get_default_config() -> CloudflareConfig:
    """Get default configuration instance."""
    return CloudflareConfig()


def check_environment() -> bool:
    """Check if environment variables are set."""
    required_vars = [
        "CLOUDFLARE_API_TOKEN",
        "CLOUDFLARE_ACCOUNT_ID",
    ]
    
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print("❌ Missing environment variables:")
        for var in missing:
            print(f"  - {var}")
        print("\nSet these variables:")
        print("  export CLOUDFLARE_API_TOKEN='your_token_here'")
        print("  export CLOUDFLARE_ACCOUNT_ID='your_account_id_here'")
        return False
    
    print("✅ All required environment variables are set")
    return True


def get_api_headers(config: CloudflareConfig) -> Dict[str, str]:
    """Get API headers for Cloudflare requests."""
    headers = {
        "Content-Type": "application/json",
    }
    
    if config.api_token:
        headers["Authorization"] = f"Bearer {config.api_token}"
    elif config.api_key and config.email:
        headers["X-Auth-Key"] = config.api_key
        headers["X-Auth-Email"] = config.email
    
    return headers


# Example configuration for different environments
ENVIRONMENTS = {
    "development": {
        "environment": "development",
        "worker_name": "arbfinder-worker-dev",
        "pages_project": "arbfinder-pages-dev",
        "r2_bucket_images": "arbfinder-images-dev",
        "r2_bucket_data": "arbfinder-data-dev",
        "d1_database_name": "arbfinder-d1-dev",
    },
    "staging": {
        "environment": "staging",
        "worker_name": "arbfinder-worker-staging",
        "pages_project": "arbfinder-pages-staging",
        "r2_bucket_images": "arbfinder-images-staging",
        "r2_bucket_data": "arbfinder-data-staging",
        "d1_database_name": "arbfinder-d1-staging",
    },
    "production": {
        "environment": "production",
        "worker_name": "arbfinder-worker",
        "pages_project": "arbfinder-pages",
        "r2_bucket_images": "arbfinder-images",
        "r2_bucket_data": "arbfinder-data",
        "d1_database_name": "arbfinder-d1",
    },
}


def get_config_for_environment(env: str = "production") -> CloudflareConfig:
    """Get configuration for specific environment."""
    if env not in ENVIRONMENTS:
        raise ValueError(f"Unknown environment: {env}")
    
    config = CloudflareConfig()
    config_dict = ENVIRONMENTS[env]
    
    for key, value in config_dict.items():
        setattr(config, key, value)
    
    return config


if __name__ == "__main__":
    # Test configuration
    print("Testing Cloudflare Configuration...")
    print()
    
    if check_environment():
        config = get_default_config()
        if config.validate():
            print("\nConfiguration:")
            print(json.dumps(config.to_dict(), indent=2))
    else:
        print("\n⚠️  Set environment variables before running Cloudflare setup scripts.")
