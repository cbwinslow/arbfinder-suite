"""
Main site investigation orchestrator
Coordinates analysis of website structure, API endpoints, and data access
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

import httpx
from pydantic import BaseModel

from .robots_analyzer import RobotsAnalyzer
from .terms_analyzer import TermsAnalyzer
from .api_discoverer import APIDiscoverer
from .historical_data import HistoricalDataFetcher

logger = logging.getLogger(__name__)


class SiteInvestigationReport(BaseModel):
    """Complete site investigation report"""

    site_name: str
    site_url: str
    investigation_date: str
    
    # Robots.txt analysis
    robots_allowed: bool
    robots_crawl_delay: Optional[int] = None
    robots_rules: Dict[str, Any] = {}
    
    # Terms of Service
    terms_url: Optional[str] = None
    api_allowed: bool = False
    scraping_allowed: bool = False
    rate_limits: Dict[str, Any] = {}
    restrictions: List[str] = []
    
    # API Discovery
    api_endpoints: List[Dict[str, Any]] = []
    api_documentation_url: Optional[str] = None
    requires_authentication: bool = False
    
    # Historical data capabilities
    wayback_available: bool = False
    historical_snapshots: int = 0
    historical_date_range: Optional[Dict[str, str]] = None
    
    # Recommendations
    recommended_approach: str = ""
    implementation_notes: List[str] = []
    
    # Generated artifacts
    config_file: Optional[str] = None
    schema_file: Optional[str] = None


class SiteInvestigator:
    """Main site investigation orchestrator"""

    def __init__(
        self,
        site_url: str,
        site_name: str,
        output_dir: str = "config/sites",
    ):
        """Initialize site investigator"""
        self.site_url = site_url.rstrip("/")
        self.site_name = site_name
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize analyzers
        self.robots_analyzer = RobotsAnalyzer(site_url)
        self.terms_analyzer = TermsAnalyzer(site_url, site_name)
        self.api_discoverer = APIDiscoverer(site_url)
        self.historical_fetcher = HistoricalDataFetcher(site_url)

    async def investigate(self) -> SiteInvestigationReport:
        """
        Perform comprehensive site investigation
        
        Returns:
            SiteInvestigationReport with all findings
        """
        logger.info(f"Starting investigation of {self.site_name} ({self.site_url})")
        
        # Run all analyses in parallel
        robots_result, terms_result, api_result, historical_result = await asyncio.gather(
            self.robots_analyzer.analyze(),
            self.terms_analyzer.analyze(),
            self.api_discoverer.discover(),
            self.historical_fetcher.check_availability(),
            return_exceptions=True,
        )
        
        # Handle any exceptions
        if isinstance(robots_result, Exception):
            logger.error(f"Robots analysis failed: {robots_result}")
            robots_result = {}
        if isinstance(terms_result, Exception):
            logger.error(f"Terms analysis failed: {terms_result}")
            terms_result = {}
        if isinstance(api_result, Exception):
            logger.error(f"API discovery failed: {api_result}")
            api_result = {}
        if isinstance(historical_result, Exception):
            logger.error(f"Historical data check failed: {historical_result}")
            historical_result = {}
        
        # Build comprehensive report
        report = SiteInvestigationReport(
            site_name=self.site_name,
            site_url=self.site_url,
            investigation_date=datetime.utcnow().isoformat(),
            robots_allowed=robots_result.get("allowed", True),
            robots_crawl_delay=robots_result.get("crawl_delay"),
            robots_rules=robots_result.get("rules", {}),
            terms_url=terms_result.get("terms_url"),
            api_allowed=terms_result.get("api_allowed", False),
            scraping_allowed=terms_result.get("scraping_allowed", False),
            rate_limits=terms_result.get("rate_limits", {}),
            restrictions=terms_result.get("restrictions", []),
            api_endpoints=api_result.get("endpoints", []),
            api_documentation_url=api_result.get("documentation_url"),
            requires_authentication=api_result.get("requires_auth", False),
            wayback_available=historical_result.get("available", False),
            historical_snapshots=historical_result.get("snapshot_count", 0),
            historical_date_range=historical_result.get("date_range"),
        )
        
        # Generate recommendations
        report.recommended_approach = self._determine_approach(report)
        report.implementation_notes = self._generate_implementation_notes(report)
        
        # Save report and generate configuration files
        await self._save_report(report)
        
        logger.info(f"Investigation complete. Report saved to {self.output_dir}")
        
        return report

    def _determine_approach(self, report: SiteInvestigationReport) -> str:
        """Determine the recommended data collection approach"""
        
        if report.api_endpoints and report.api_allowed:
            return "API_PREFERRED"
        elif report.scraping_allowed and report.robots_allowed:
            return "WEB_SCRAPING"
        elif report.wayback_available:
            return "HISTORICAL_ONLY"
        else:
            return "MANUAL_EXPORT"

    def _generate_implementation_notes(
        self, report: SiteInvestigationReport
    ) -> List[str]:
        """Generate implementation notes based on findings"""
        notes = []
        
        if report.robots_crawl_delay:
            notes.append(
                f"Respect crawl delay of {report.robots_crawl_delay} seconds"
            )
        
        if report.rate_limits:
            for key, value in report.rate_limits.items():
                notes.append(f"Rate limit: {key} = {value}")
        
        if report.requires_authentication:
            notes.append("API authentication required - obtain API key")
        
        if not report.scraping_allowed:
            notes.append(
                "Terms of Service prohibit scraping - use official API or manual export"
            )
        
        if report.restrictions:
            notes.extend([f"Restriction: {r}" for r in report.restrictions])
        
        return notes

    async def _save_report(self, report: SiteInvestigationReport) -> None:
        """Save investigation report and generate config files"""
        
        # Save JSON report
        report_path = self.output_dir / f"{self.site_name}_investigation.json"
        with open(report_path, "w") as f:
            json.dump(report.model_dump(), f, indent=2)
        
        # Generate site-specific configuration
        config_path = self.output_dir / f"{self.site_name}_config.toml"
        await self._generate_site_config(report, config_path)
        report.config_file = str(config_path)
        
        # Generate schema file
        schema_path = self.output_dir / f"{self.site_name}_schema.json"
        await self._generate_schema(report, schema_path)
        report.schema_file = str(schema_path)

    async def _generate_site_config(
        self, report: SiteInvestigationReport, output_path: Path
    ) -> None:
        """Generate TOML configuration file for the site"""
        
        config_lines = [
            f"# Configuration for {report.site_name}",
            f"# Generated: {report.investigation_date}",
            f"# Investigation Report: {report.site_name}_investigation.json",
            "",
            "[site]",
            f'name = "{report.site_name}"',
            f'url = "{report.site_url}"',
            f'approach = "{report.recommended_approach}"',
            "",
            "[crawler]",
            f"enabled = {str(report.robots_allowed).lower()}",
        ]
        
        if report.robots_crawl_delay:
            config_lines.append(
                f"crawl_delay = {report.robots_crawl_delay}"
            )
        
        config_lines.extend(
            [
                "",
                "[api]",
                f"enabled = {str(report.api_allowed).lower()}",
                f"requires_auth = {str(report.requires_authentication).lower()}",
            ]
        )
        
        if report.api_documentation_url:
            config_lines.append(
                f'documentation_url = "{report.api_documentation_url}"'
            )
        
        if report.api_endpoints:
            config_lines.extend(["", "# Discovered API endpoints", "[[endpoints]]"])
            for endpoint in report.api_endpoints[:5]:  # Include first 5
                config_lines.append(f"# {endpoint.get('path', 'unknown')}")
        
        config_lines.extend(
            [
                "",
                "[historical]",
                f"wayback_available = {str(report.wayback_available).lower()}",
                f"snapshot_count = {report.historical_snapshots}",
            ]
        )
        
        with open(output_path, "w") as f:
            f.write("\n".join(config_lines))

    async def _generate_schema(
        self, report: SiteInvestigationReport, output_path: Path
    ) -> None:
        """Generate JSON schema file for the site's data structure"""
        
        schema = {
            "site": report.site_name,
            "version": "1.0",
            "generated": report.investigation_date,
            "endpoints": report.api_endpoints,
            "data_structure": {
                "listing": {
                    "id": "string",
                    "title": "string",
                    "price": "number",
                    "currency": "string",
                    "url": "string",
                    "image_url": "string",
                    "condition": "string",
                    "description": "string",
                    "timestamp": "datetime",
                },
            },
            "functions": {
                "get_listings": {
                    "description": "Fetch current listings",
                    "parameters": {
                        "query": "string",
                        "category": "string",
                        "limit": "number",
                    },
                    "returns": "array[listing]",
                },
                "get_item_details": {
                    "description": "Get detailed information about a specific item",
                    "parameters": {"item_id": "string"},
                    "returns": "listing",
                },
            },
        }
        
        with open(output_path, "w") as f:
            json.dump(schema, f, indent=2)


# Example usage
async def investigate_shopgoodwill():
    """Investigate ShopGoodwill.com"""
    investigator = SiteInvestigator(
        site_url="https://shopgoodwill.com",
        site_name="shopgoodwill",
    )
    
    report = await investigator.investigate()
    
    print(f"\n{'=' * 60}")
    print(f"Investigation Report: {report.site_name}")
    print(f"{'=' * 60}")
    print(f"Robots Allowed: {report.robots_allowed}")
    print(f"API Allowed: {report.api_allowed}")
    print(f"Scraping Allowed: {report.scraping_allowed}")
    print(f"API Endpoints Found: {len(report.api_endpoints)}")
    print(f"Historical Data: {report.wayback_available}")
    print(f"\nRecommended Approach: {report.recommended_approach}")
    print(f"\nImplementation Notes:")
    for note in report.implementation_notes:
        print(f"  - {note}")
    print(f"{'=' * 60}\n")
    
    return report


if __name__ == "__main__":
    asyncio.run(investigate_shopgoodwill())
