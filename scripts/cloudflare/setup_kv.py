#!/usr/bin/env python3
"""
Setup Cloudflare KV Namespaces.

Creates KV namespaces for caching and configuration storage.
"""

import sys
import requests
from typing import Dict, Any, List, Optional
from config import CloudflareConfig, get_default_config, get_api_headers


class KVSetup:
    """Setup and manage KV namespaces."""
    
    def __init__(self, config: CloudflareConfig):
        self.config = config
        self.base_url = f"https://api.cloudflare.com/client/v4/accounts/{config.account_id}"
        self.headers = get_api_headers(config)
    
    def create_namespace(self, namespace_name: str) -> Optional[str]:
        """Create a KV namespace."""
        url = f"{self.base_url}/storage/kv/namespaces"
        
        payload = {
            "title": namespace_name
        }
        
        print(f"Creating KV namespace: {namespace_name}")
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                namespace_id = data.get("result", {}).get("id")
                print(f"✅ Namespace '{namespace_name}' created")
                print(f"   ID: {namespace_id}")
                return namespace_id
            else:
                print(f"❌ Failed to create namespace: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating namespace: {e}")
            return None
    
    def list_namespaces(self) -> List[Dict[str, Any]]:
        """List all KV namespaces."""
        url = f"{self.base_url}/storage/kv/namespaces"
        
        try:
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                namespaces = data.get("result", [])
                return namespaces
            else:
                print(f"❌ Failed to list namespaces: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error listing namespaces: {e}")
            return []
    
    def find_namespace_by_title(self, title: str) -> Optional[str]:
        """Find namespace ID by title."""
        namespaces = self.list_namespaces()
        for ns in namespaces:
            if ns.get("title") == title:
                return ns.get("id")
        return None
    
    def write_example_key(self, namespace_id: str, key: str, value: str) -> bool:
        """Write an example key to namespace."""
        url = f"{self.base_url}/storage/kv/namespaces/{namespace_id}/values/{key}"
        
        try:
            response = requests.put(url, headers=self.headers, data=value)
            
            if response.status_code == 200:
                print(f"   ✅ Example key '{key}' written")
                return True
            else:
                print(f"   ❌ Failed to write key: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error writing key: {e}")
            return False
    
    def setup_all(self) -> bool:
        """Setup all KV namespaces."""
        print("\n🗄️  Setting up KV Namespaces")
        print("="*60)
        
        namespaces = {
            self.config.kv_namespace_cache: "Cache for frequent data",
            self.config.kv_namespace_config: "Configuration storage",
        }
        
        namespace_ids = {}
        success = True
        
        for namespace_name, description in namespaces.items():
            print(f"\n{description}:")
            
            # Check if exists
            existing_id = self.find_namespace_by_title(namespace_name)
            
            if existing_id:
                print(f"ℹ️  Namespace '{namespace_name}' already exists")
                print(f"   ID: {existing_id}")
                namespace_ids[namespace_name] = existing_id
            else:
                namespace_id = self.create_namespace(namespace_name)
                if namespace_id:
                    namespace_ids[namespace_name] = namespace_id
                    
                    # Write example key
                    if namespace_name == self.config.kv_namespace_cache:
                        self.write_example_key(
                            namespace_id,
                            "test_key",
                            "test_value"
                        )
                else:
                    success = False
        
        # List all namespaces
        print("\nCurrent KV Namespaces:")
        existing_namespaces = self.list_namespaces()
        for ns in existing_namespaces:
            print(f"  - {ns.get('title')} ({ns.get('id')})")
        
        if success:
            print("\n✅ KV setup completed successfully")
            print("\n📋 Configuration for wrangler.toml:")
            print("\n[[kv_namespaces]]")
            print(f'binding = "CACHE"')
            print(f'id = "{namespace_ids.get(self.config.kv_namespace_cache, "YOUR_NAMESPACE_ID")}"')
            print()
            print("[[kv_namespaces]]")
            print(f'binding = "CONFIG"')
            print(f'id = "{namespace_ids.get(self.config.kv_namespace_config, "YOUR_NAMESPACE_ID")}"')
            
            print("\n📋 Next Steps:")
            print("1. Copy namespace IDs to wrangler.toml")
            print("2. Update Worker bindings to use KV namespaces")
            print("3. Implement cache invalidation strategy")
            print("4. Monitor KV storage usage in dashboard")
        else:
            print("\n❌ KV setup encountered errors")
        
        return success


def main():
    """Main entry point."""
    config = get_default_config()
    
    if not config.validate():
        print("❌ Configuration validation failed")
        sys.exit(1)
    
    kv_setup = KVSetup(config)
    success = kv_setup.setup_all()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
