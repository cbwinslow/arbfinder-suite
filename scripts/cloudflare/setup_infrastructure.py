#!/usr/bin/env python3
"""
Cloudflare Infrastructure Setup Orchestrator.

This script orchestrates the setup of all Cloudflare services for ArbFinder Suite:
- Workers
- Pages
- R2 Storage
- D1 Database
- KV Namespaces
- WAF Configuration
- Observability

Usage:
    python setup_infrastructure.py [--environment dev|staging|prod] [--dry-run]
"""

import argparse
import sys
import subprocess
from pathlib import Path
from typing import List, Tuple, Optional
import time

from config import (
    CloudflareConfig,
    check_environment,
    get_config_for_environment
)


class InfrastructureOrchestrator:
    """Orchestrate Cloudflare infrastructure setup."""
    
    def __init__(self, config: CloudflareConfig, dry_run: bool = False):
        self.config = config
        self.dry_run = dry_run
        self.results: List[Tuple[str, bool, str]] = []
    
    def run_script(self, script_name: str, description: str) -> bool:
        """Run a setup script and track results."""
        print(f"\n{'='*60}")
        print(f"🔧 {description}")
        print(f"{'='*60}")
        
        if self.dry_run:
            print(f"[DRY RUN] Would execute: python {script_name}")
            self.results.append((description, True, "Skipped (dry run)"))
            return True
        
        script_path = Path(__file__).parent / script_name
        
        if not script_path.exists():
            print(f"❌ Script not found: {script_path}")
            self.results.append((description, False, "Script not found"))
            return False
        
        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            print(result.stdout)
            
            if result.returncode == 0:
                print(f"✅ {description} completed successfully")
                self.results.append((description, True, "Success"))
                return True
            else:
                print(f"❌ {description} failed")
                print(result.stderr)
                self.results.append((description, False, result.stderr[:100]))
                return False
                
        except subprocess.TimeoutExpired:
            print(f"❌ {description} timed out")
            self.results.append((description, False, "Timeout"))
            return False
        except Exception as e:
            print(f"❌ {description} error: {e}")
            self.results.append((description, False, str(e)[:100]))
            return False
    
    def setup_all(self) -> bool:
        """Run complete infrastructure setup."""
        print("\n🚀 Starting Cloudflare Infrastructure Setup")
        print(f"Environment: {self.config.environment}")
        print(f"Project: {self.config.project_name}")
        
        if self.dry_run:
            print("\n⚠️  DRY RUN MODE - No actual changes will be made\n")
        
        start_time = time.time()
        
        # Setup sequence
        steps = [
            ("setup_kv.py", "Setting up KV Namespaces"),
            ("setup_r2.py", "Setting up R2 Storage Buckets"),
            ("setup_d1.py", "Setting up D1 Database"),
            ("setup_workers.py", "Deploying Cloudflare Workers"),
            ("setup_pages.py", "Setting up Cloudflare Pages"),
            ("configure_waf.py", "Configuring Web Application Firewall"),
            ("setup_observability.py", "Setting up Observability and Logging"),
        ]
        
        for script, description in steps:
            success = self.run_script(script, description)
            if not success and not self.dry_run:
                print(f"\n⚠️  Setup step failed: {description}")
                print("Do you want to continue? (y/n): ", end="")
                response = input().lower()
                if response != 'y':
                    print("\n❌ Setup aborted by user")
                    return False
            time.sleep(1)  # Brief pause between steps
        
        # Print summary
        duration = time.time() - start_time
        self.print_summary(duration)
        
        # Return overall success
        return all(success for _, success, _ in self.results)
    
    def print_summary(self, duration: float) -> None:
        """Print setup summary."""
        print("\n" + "="*60)
        print("📊 SETUP SUMMARY")
        print("="*60)
        
        for description, success, message in self.results:
            status = "✅" if success else "❌"
            print(f"{status} {description}")
            if not success:
                print(f"   Error: {message}")
        
        success_count = sum(1 for _, success, _ in self.results if success)
        total_count = len(self.results)
        
        print(f"\nCompleted: {success_count}/{total_count} steps")
        print(f"Duration: {duration:.2f} seconds")
        
        if success_count == total_count:
            print("\n🎉 Infrastructure setup completed successfully!")
            self.print_next_steps()
        else:
            print("\n⚠️  Some steps failed. Check the logs above for details.")
    
    def print_next_steps(self) -> None:
        """Print next steps after successful setup."""
        print("\n" + "="*60)
        print("📋 NEXT STEPS")
        print("="*60)
        
        print("\n1. Verify Deployments:")
        print(f"   - Workers: https://{self.config.worker_subdomain}.workers.dev")
        print(f"   - Pages: https://{self.config.pages_domain}")
        
        print("\n2. Configure Environment Variables:")
        print("   - Update .env with Cloudflare resource IDs")
        print("   - Set up secrets in Workers and Pages dashboards")
        
        print("\n3. Test Services:")
        print("   - Test Worker health endpoint")
        print("   - Test image upload to R2")
        print("   - Verify D1 database connectivity")
        
        print("\n4. Monitor:")
        print("   - Check Cloudflare Analytics dashboard")
        print("   - Review Worker logs")
        print("   - Monitor R2 storage usage")
        
        print("\n5. Documentation:")
        print("   - Update docs/CLOUDFLARE_SETUP.md with deployment details")
        print("   - Document any custom configurations")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Set up Cloudflare infrastructure for ArbFinder Suite"
    )
    parser.add_argument(
        "--environment",
        "-e",
        choices=["development", "staging", "production"],
        default="production",
        help="Deployment environment (default: production)"
    )
    parser.add_argument(
        "--dry-run",
        "-d",
        action="store_true",
        help="Preview actions without making changes"
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip environment validation"
    )
    
    args = parser.parse_args()
    
    print("="*60)
    print("🌐 ArbFinder Suite - Cloudflare Infrastructure Setup")
    print("="*60)
    
    # Check environment variables
    if not args.skip_validation and not check_environment():
        print("\n❌ Environment validation failed")
        print("\nSet required environment variables:")
        print("  export CLOUDFLARE_API_TOKEN='your_token_here'")
        print("  export CLOUDFLARE_ACCOUNT_ID='your_account_id_here'")
        sys.exit(1)
    
    # Get configuration for environment
    try:
        config = get_config_for_environment(args.environment)
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    
    # Validate configuration
    if not args.skip_validation and not config.validate():
        print("\n❌ Configuration validation failed")
        sys.exit(1)
    
    # Run orchestrator
    orchestrator = InfrastructureOrchestrator(config, dry_run=args.dry_run)
    success = orchestrator.setup_all()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
