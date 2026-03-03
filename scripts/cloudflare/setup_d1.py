#!/usr/bin/env python3
"""
Setup Cloudflare D1 Database.

Creates and initializes D1 database for edge data storage.
"""

import sys
import subprocess
from pathlib import Path
from config import CloudflareConfig, get_default_config


class D1Setup:
    """Setup and manage D1 database."""
    
    def __init__(self, config: CloudflareConfig):
        self.config = config
    
    def check_wrangler(self) -> bool:
        """Check if Wrangler CLI is installed."""
        try:
            result = subprocess.run(
                ["wrangler", "--version"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"✅ Wrangler CLI found: {result.stdout.strip()}")
                return True
            else:
                print("❌ Wrangler CLI not found")
                return False
        except FileNotFoundError:
            print("❌ Wrangler CLI not installed")
            print("   Install with: npm install -g wrangler")
            return False
    
    def create_database(self) -> bool:
        """Create D1 database using Wrangler."""
        db_name = self.config.d1_database_name
        
        print(f"Creating D1 database: {db_name}")
        
        try:
            result = subprocess.run(
                ["wrangler", "d1", "create", db_name],
                capture_output=True,
                text=True
            )
            
            print(result.stdout)
            
            if result.returncode == 0:
                print(f"✅ Database '{db_name}' created successfully")
                return True
            elif "already exists" in result.stderr.lower():
                print(f"ℹ️  Database '{db_name}' already exists")
                return True
            else:
                print(f"❌ Failed to create database")
                print(result.stderr)
                return False
                
        except Exception as e:
            print(f"❌ Error creating database: {e}")
            return False
    
    def list_databases(self) -> bool:
        """List all D1 databases."""
        print("\nListing D1 databases:")
        
        try:
            result = subprocess.run(
                ["wrangler", "d1", "list"],
                capture_output=True,
                text=True
            )
            
            print(result.stdout)
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Error listing databases: {e}")
            return False
    
    def initialize_schema(self) -> bool:
        """Initialize database schema."""
        db_name = self.config.d1_database_name
        
        print(f"\nInitializing schema for '{db_name}'")
        
        # Example schema
        schema_sql = """
        -- Listings table for edge caching
        CREATE TABLE IF NOT EXISTS listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            url TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            price REAL NOT NULL,
            currency TEXT DEFAULT 'USD',
            condition TEXT,
            created_at INTEGER DEFAULT (strftime('%s', 'now')),
            updated_at INTEGER DEFAULT (strftime('%s', 'now'))
        );
        
        CREATE INDEX IF NOT EXISTS idx_listings_source ON listings(source);
        CREATE INDEX IF NOT EXISTS idx_listings_price ON listings(price);
        CREATE INDEX IF NOT EXISTS idx_listings_created_at ON listings(created_at);
        
        -- Cache metadata
        CREATE TABLE IF NOT EXISTS cache_meta (
            key TEXT PRIMARY KEY,
            value TEXT,
            expires_at INTEGER,
            created_at INTEGER DEFAULT (strftime('%s', 'now'))
        );
        """
        
        # Write schema to temp file
        schema_file = Path("/tmp/d1_schema.sql")
        schema_file.write_text(schema_sql)
        
        try:
            result = subprocess.run(
                ["wrangler", "d1", "execute", db_name, "--file", str(schema_file)],
                capture_output=True,
                text=True
            )
            
            print(result.stdout)
            
            if result.returncode == 0:
                print(f"✅ Schema initialized successfully")
                return True
            else:
                print(f"❌ Failed to initialize schema")
                print(result.stderr)
                return False
                
        except Exception as e:
            print(f"❌ Error initializing schema: {e}")
            return False
        finally:
            schema_file.unlink(missing_ok=True)
    
    def setup_all(self) -> bool:
        """Setup D1 database."""
        print("\n💾 Setting up D1 Database")
        print("="*60)
        
        # Check Wrangler
        if not self.check_wrangler():
            return False
        
        # Create database
        if not self.create_database():
            return False
        
        # Initialize schema
        if not self.initialize_schema():
            print("⚠️  Schema initialization failed, but database exists")
        
        # List databases
        self.list_databases()
        
        print("\n✅ D1 setup completed")
        print("\n📋 Configuration for wrangler.toml:")
        print("\n[[d1_databases]]")
        print(f'binding = "DB"')
        print(f'database_name = "{self.config.d1_database_name}"')
        print('database_id = "<copy from wrangler d1 list output>"')
        
        print("\n📋 Next Steps:")
        print("1. Copy database ID to wrangler.toml")
        print("2. Update Worker code to use D1 binding")
        print("3. Test database queries from Worker")
        print("4. Set up data synchronization from PostgreSQL")
        print("5. Monitor query performance in Workers Analytics")
        
        return True


def main():
    """Main entry point."""
    config = get_default_config()
    
    if not config.validate():
        print("❌ Configuration validation failed")
        sys.exit(1)
    
    d1_setup = D1Setup(config)
    success = d1_setup.setup_all()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
