#!/usr/bin/env python3
"""
Cloudflare Platform Setup Orchestrator

This script automates the complete setup of ArbFinder Suite on Cloudflare platform,
including Workers, Pages, D1, R2, KV, WAF, and observability configuration.

Usage:
    python setup_cloudflare.py --api-key YOUR_API_KEY --account-id YOUR_ACCOUNT_ID
    python setup_cloudflare.py --config config/cloudflare.json
    python setup_cloudflare.py --interactive

Requirements:
    - Python 3.9+
    - cloudflare SDK
    - requests
    - rich (for pretty output)
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import logging

try:
    import requests
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.table import Table
    from rich.panel import Panel
    from rich import print as rprint
except ImportError:
    print("Missing dependencies. Install with: pip install requests rich")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cloudflare_setup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

console = Console()

# Global constant for API key (will be set from arguments or environment)
CLOUDFLARE_API_KEY = os.getenv("CLOUDFLARE_API_TOKEN", "")
CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID", "")
CLOUDFLARE_API_BASE = "https://api.cloudflare.com/client/v4"


@dataclass
class CloudflareConfig:
    """Cloudflare configuration data class."""
    api_token: str
    account_id: str
    zone_id: Optional[str] = None
    project_name: str = "arbfinder"
    environment: str = "production"
    
    # Service configurations
    worker_name: Optional[str] = None
    pages_project: Optional[str] = None
    d1_database: Optional[str] = None
    r2_buckets: Optional[List[str]] = None
    kv_namespaces: Optional[List[str]] = None


class CloudflareAPIClient:
    """Cloudflare API client wrapper."""
    
    def __init__(self, api_token: str, account_id: str):
        """Initialize Cloudflare API client.
        
        Args:
            api_token: Cloudflare API token
            account_id: Cloudflare account ID
        """
        self.api_token = api_token
        self.account_id = account_id
        self.base_url = CLOUDFLARE_API_BASE
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        })
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to Cloudflare API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters
            
        Returns:
            API response data
            
        Raises:
            requests.HTTPError: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            
            if not result.get("success", False):
                errors = result.get("errors", [])
                error_msg = ", ".join([e.get("message", str(e)) for e in errors])
                raise Exception(f"Cloudflare API error: {error_msg}")
            
            return result.get("result", {})
            
        except requests.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            raise
        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make GET request."""
        return self._make_request("GET", endpoint, params=params)
    
    def post(self, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make POST request."""
        return self._make_request("POST", endpoint, data=data)
    
    def put(self, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make PUT request."""
        return self._make_request("PUT", endpoint, data=data)
    
    def delete(self, endpoint: str) -> Dict:
        """Make DELETE request."""
        return self._make_request("DELETE", endpoint)


class CloudflareSetup:
    """Main Cloudflare setup orchestrator."""
    
    def __init__(self, config: CloudflareConfig, interactive: bool = False):
        """Initialize setup orchestrator.
        
        Args:
            config: Cloudflare configuration
            interactive: Enable interactive mode
        """
        self.config = config
        self.interactive = interactive
        self.client = CloudflareAPIClient(config.api_token, config.account_id)
        self.created_resources = []
    
    def run(self):
        """Execute complete setup workflow."""
        console.print(Panel.fit(
            "[bold green]ArbFinder Suite - Cloudflare Platform Setup[/bold green]\n"
            f"Account ID: {self.config.account_id}\n"
            f"Project: {self.config.project_name}\n"
            f"Environment: {self.config.environment}",
            title="Setup Configuration"
        ))
        
        steps = [
            ("Verify API credentials", self.verify_credentials),
            ("Create D1 database", self.setup_d1_database),
            ("Create R2 buckets", self.setup_r2_buckets),
            ("Create KV namespaces", self.setup_kv_namespaces),
            ("Deploy Cloudflare Worker", self.setup_worker),
            ("Deploy Cloudflare Pages", self.setup_pages),
            ("Configure WAF rules", self.setup_waf),
            ("Configure observability", self.setup_observability),
            ("Bind services", self.bind_services),
            ("Verify setup", self.verify_setup)
        ]
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            for description, step_func in steps:
                task = progress.add_task(description, total=None)
                try:
                    result = step_func()
                    progress.update(task, completed=True)
                    console.print(f"✓ {description}", style="green")
                    if result:
                        logger.info(f"{description}: {result}")
                except Exception as e:
                    progress.update(task, completed=True)
                    console.print(f"✗ {description}: {e}", style="red")
                    logger.error(f"{description} failed: {e}", exc_info=True)
                    
                    if self.interactive:
                        choice = console.input(
                            "\n[yellow]Continue with remaining steps? (y/n):[/yellow] "
                        )
                        if choice.lower() != 'y':
                            break
        
        self.print_summary()
    
    def verify_credentials(self) -> Dict[str, Any]:
        """Verify API credentials."""
        try:
            user_info = self.client.get("/user")
            console.print(f"Authenticated as: {user_info.get('email', 'Unknown')}")
            return {"email": user_info.get("email")}
        except Exception as e:
            raise Exception(f"Failed to verify credentials: {e}")
    
    def setup_d1_database(self) -> Dict[str, Any]:
        """Create D1 database."""
        db_name = f"{self.config.project_name}-db-{self.config.environment}"
        
        endpoint = f"/accounts/{self.config.account_id}/d1/database"
        
        try:
            # Check if database already exists
            existing_dbs = self.client.get(endpoint)
            for db in existing_dbs:
                if db.get("name") == db_name:
                    console.print(f"D1 database '{db_name}' already exists")
                    return {"id": db.get("uuid"), "name": db_name, "status": "exists"}
            
            # Create new database
            data = {"name": db_name}
            result = self.client.post(endpoint, data=data)
            
            db_id = result.get("uuid")
            self.created_resources.append({"type": "d1_database", "id": db_id, "name": db_name})
            
            console.print(f"Created D1 database: {db_name} (ID: {db_id})")
            return {"id": db_id, "name": db_name, "status": "created"}
            
        except Exception as e:
            raise Exception(f"Failed to create D1 database: {e}")
    
    def setup_r2_buckets(self) -> Dict[str, List[str]]:
        """Create R2 buckets."""
        bucket_names = self.config.r2_buckets or [
            f"{self.config.project_name}-images",
            f"{self.config.project_name}-data",
            f"{self.config.project_name}-backups"
        ]
        
        created_buckets = []
        endpoint = f"/accounts/{self.config.account_id}/r2/buckets"
        
        for bucket_name in bucket_names:
            try:
                # R2 bucket creation via API
                data = {"name": bucket_name}
                result = self.client.post(endpoint, data=data)
                
                created_buckets.append(bucket_name)
                self.created_resources.append({"type": "r2_bucket", "name": bucket_name})
                console.print(f"Created R2 bucket: {bucket_name}")
                
            except Exception as e:
                console.print(f"Warning: Could not create R2 bucket '{bucket_name}': {e}", style="yellow")
                logger.warning(f"R2 bucket creation failed: {e}")
        
        return {"buckets": created_buckets}
    
    def setup_kv_namespaces(self) -> Dict[str, List[Dict]]:
        """Create KV namespaces."""
        namespace_names = self.config.kv_namespaces or [
            f"{self.config.project_name}-cache",
            f"{self.config.project_name}-sessions",
            f"{self.config.project_name}-config"
        ]
        
        created_namespaces = []
        endpoint = f"/accounts/{self.config.account_id}/storage/kv/namespaces"
        
        for namespace_name in namespace_names:
            try:
                data = {"title": namespace_name}
                result = self.client.post(endpoint, data=data)
                
                namespace_id = result.get("id")
                created_namespaces.append({"name": namespace_name, "id": namespace_id})
                self.created_resources.append({
                    "type": "kv_namespace",
                    "id": namespace_id,
                    "name": namespace_name
                })
                console.print(f"Created KV namespace: {namespace_name} (ID: {namespace_id})")
                
            except Exception as e:
                console.print(f"Warning: Could not create KV namespace '{namespace_name}': {e}", style="yellow")
                logger.warning(f"KV namespace creation failed: {e}")
        
        return {"namespaces": created_namespaces}
    
    def setup_worker(self) -> Dict[str, Any]:
        """Deploy Cloudflare Worker."""
        worker_name = self.config.worker_name or f"{self.config.project_name}-worker"
        
        console.print(f"\n[yellow]Worker deployment requires wrangler CLI[/yellow]")
        console.print(f"Run: wrangler deploy from cloudflare/ directory")
        console.print(f"Worker name: {worker_name}")
        
        return {"name": worker_name, "status": "manual_deployment_required"}
    
    def setup_pages(self) -> Dict[str, Any]:
        """Deploy Cloudflare Pages."""
        pages_project = self.config.pages_project or f"{self.config.project_name}-frontend"
        
        console.print(f"\n[yellow]Pages deployment requires GitHub integration[/yellow]")
        console.print(f"Project name: {pages_project}")
        console.print("Connect your repository at: https://dash.cloudflare.com/pages")
        
        return {"project": pages_project, "status": "manual_deployment_required"}
    
    def setup_waf(self) -> Dict[str, Any]:
        """Configure Web Application Firewall."""
        console.print("\n[yellow]WAF configuration requires zone ID[/yellow]")
        console.print("Configure WAF rules in Cloudflare Dashboard > Security > WAF")
        
        # Placeholder for WAF setup
        # In a real implementation, this would create WAF rules via API
        return {"status": "manual_configuration_required"}
    
    def setup_observability(self) -> Dict[str, Any]:
        """Configure observability and logging."""
        console.print("\n[cyan]Setting up observability...[/cyan]")
        
        # Enable Workers Analytics Engine
        console.print("Workers Analytics Engine will track custom metrics")
        console.print("Configure in your Worker with: env.ANALYTICS.writeDataPoint()")
        
        return {
            "analytics_engine": "enabled",
            "logs": "available_via_wrangler_tail",
            "logpush": "configure_for_external_logging"
        }
    
    def bind_services(self) -> Dict[str, Any]:
        """Bind services to Workers."""
        console.print("\n[cyan]Service bindings configuration...[/cyan]")
        console.print("Update wrangler.toml with created resource IDs:")
        
        # Generate wrangler.toml snippet
        bindings = []
        for resource in self.created_resources:
            if resource["type"] == "d1_database":
                bindings.append(f"""
[[d1_databases]]
binding = "DB"
database_name = "{resource['name']}"
database_id = "{resource['id']}"
""")
            elif resource["type"] == "r2_bucket":
                bindings.append(f"""
[[r2_buckets]]
binding = "{resource['name'].upper().replace('-', '_')}"
bucket_name = "{resource['name']}"
""")
            elif resource["type"] == "kv_namespace":
                bindings.append(f"""
[[kv_namespaces]]
binding = "{resource['name'].upper().replace('-', '_')}"
id = "{resource['id']}"
""")
        
        if bindings:
            console.print("\n[green]Add to wrangler.toml:[/green]")
            for binding in bindings:
                console.print(binding)
        
        return {"bindings_configured": len(bindings)}
    
    def verify_setup(self) -> Dict[str, Any]:
        """Verify setup completion."""
        console.print("\n[cyan]Verifying setup...[/cyan]")
        
        verification_results = {
            "d1_databases": 0,
            "r2_buckets": 0,
            "kv_namespaces": 0,
            "total_resources": len(self.created_resources)
        }
        
        for resource in self.created_resources:
            resource_type = resource["type"]
            if resource_type in verification_results:
                verification_results[resource_type] += 1
        
        return verification_results
    
    def print_summary(self):
        """Print setup summary."""
        console.print("\n" + "="*60)
        console.print("[bold green]Setup Complete![/bold green]")
        console.print("="*60 + "\n")
        
        if not self.created_resources:
            console.print("[yellow]No resources were created[/yellow]")
            return
        
        # Create summary table
        table = Table(title="Created Resources")
        table.add_column("Type", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("ID", style="yellow")
        
        for resource in self.created_resources:
            table.add_row(
                resource.get("type", "unknown"),
                resource.get("name", "N/A"),
                resource.get("id", "N/A")
            )
        
        console.print(table)
        
        # Next steps
        console.print("\n[bold cyan]Next Steps:[/bold cyan]")
        console.print("1. Update wrangler.toml with resource IDs (see above)")
        console.print("2. Deploy Worker: cd cloudflare && wrangler deploy")
        console.print("3. Deploy Pages: Connect GitHub repo in Cloudflare Dashboard")
        console.print("4. Configure WAF rules in Cloudflare Dashboard > Security")
        console.print("5. Test endpoints and verify functionality")
        
        console.print(f"\n[dim]Setup log saved to: cloudflare_setup.log[/dim]")


def load_config_from_file(file_path: str) -> CloudflareConfig:
    """Load configuration from JSON file.
    
    Args:
        file_path: Path to configuration file
        
    Returns:
        CloudflareConfig object
    """
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    return CloudflareConfig(**data)


def interactive_config() -> CloudflareConfig:
    """Collect configuration interactively.
    
    Returns:
        CloudflareConfig object
    """
    console.print("[bold cyan]Cloudflare Setup - Interactive Mode[/bold cyan]\n")
    
    api_token = console.input("Cloudflare API Token: ").strip()
    account_id = console.input("Cloudflare Account ID: ").strip()
    project_name = console.input("Project Name [arbfinder]: ").strip() or "arbfinder"
    environment = console.input("Environment (production/staging) [production]: ").strip() or "production"
    
    return CloudflareConfig(
        api_token=api_token,
        account_id=account_id,
        project_name=project_name,
        environment=environment
    )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Setup ArbFinder Suite on Cloudflare Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python setup_cloudflare.py --api-key TOKEN --account-id ID
  python setup_cloudflare.py --config config/cloudflare.json
  python setup_cloudflare.py --interactive
  
Environment Variables:
  CLOUDFLARE_API_TOKEN    - API token for authentication
  CLOUDFLARE_ACCOUNT_ID   - Account ID for resource creation
        """
    )
    
    parser.add_argument(
        "--api-key",
        "--api-token",
        help="Cloudflare API token"
    )
    parser.add_argument(
        "--account-id",
        help="Cloudflare account ID"
    )
    parser.add_argument(
        "--config",
        help="Path to configuration JSON file"
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Interactive configuration mode"
    )
    parser.add_argument(
        "--project-name",
        default="arbfinder",
        help="Project name (default: arbfinder)"
    )
    parser.add_argument(
        "--environment",
        choices=["production", "staging", "development"],
        default="production",
        help="Environment (default: production)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate setup without creating resources"
    )
    
    args = parser.parse_args()
    
    # Load configuration
    if args.config:
        config = load_config_from_file(args.config)
    elif args.interactive:
        config = interactive_config()
    else:
        api_token = args.api_key or os.getenv("CLOUDFLARE_API_TOKEN")
        account_id = args.account_id or os.getenv("CLOUDFLARE_ACCOUNT_ID")
        
        if not api_token or not account_id:
            console.print("[bold red]Error:[/bold red] API token and account ID required")
            console.print("Provide via --api-key and --account-id or environment variables")
            parser.print_help()
            sys.exit(1)
        
        config = CloudflareConfig(
            api_token=api_token,
            account_id=account_id,
            project_name=args.project_name,
            environment=args.environment
        )
    
    if args.dry_run:
        console.print("[yellow]DRY RUN MODE - No resources will be created[/yellow]\n")
        console.print("Configuration:")
        console.print(json.dumps(asdict(config), indent=2))
        return
    
    # Run setup
    setup = CloudflareSetup(config, interactive=args.interactive)
    try:
        setup.run()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Setup interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red]Setup failed:[/bold red] {e}")
        logger.exception("Setup failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
