#!/usr/bin/env python3
"""
Site Analysis CLI
Command-line tool for analyzing websites and generating integration code
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from agents.site_analysis_crew import SiteAnalysisCrew
from site_investigator import SiteInvestigator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def investigate_site(args):
    """Run site investigation only"""
    logger.info(f"Investigating {args.site_name} at {args.url}")

    investigator = SiteInvestigator(
        site_url=args.url,
        site_name=args.site_name,
        output_dir=args.output_dir,
    )

    report = await investigator.investigate()

    print(f"\n{'=' * 80}")
    print(f"Investigation Report: {report.site_name}")
    print(f"{'=' * 80}")
    print(f"Robots Allowed: {report.robots_allowed}")
    print(f"API Allowed: {report.api_allowed}")
    print(f"Scraping Allowed: {report.scraping_allowed}")
    print(f"API Endpoints Found: {len(report.api_endpoints)}")
    print(f"Historical Data Available: {report.wayback_available}")
    print(f"\nRecommended Approach: {report.recommended_approach}")
    print(f"\nImplementation Notes:")
    for note in report.implementation_notes:
        print(f"  - {note}")
    print(f"\nConfiguration saved to: {report.config_file}")
    print(f"Schema saved to: {report.schema_file}")
    print(f"{'=' * 80}\n")


async def analyze_site(args):
    """Run full site analysis with all agents"""
    logger.info(f"Analyzing {args.site_name} at {args.url}")

    crew = SiteAnalysisCrew(
        site_url=args.url,
        site_name=args.site_name,
        output_dir=args.output_dir,
    )

    results = await crew.analyze_site()

    print(f"\n{'=' * 80}")
    print(f"Site Analysis Complete: {results['site_name']}")
    print(f"{'=' * 80}")
    print(f"Status: {results['status']}")

    if results["status"] == "completed":
        print(f"\n✓ Investigation completed")
        if results.get("api_analysis"):
            print(f"✓ API analysis completed")
        if results.get("schemas"):
            print(f"✓ Schemas generated")
        if results.get("mcp_server"):
            print(f"✓ MCP server generated")

        print(f"\nGenerated {len(results['artifacts'])} artifacts:")
        for artifact in results["artifacts"]:
            print(f"  - {artifact}")
    elif results["status"] == "failed":
        print(f"\n✗ Analysis failed: {results.get('error')}")

    print(f"{'=' * 80}\n")


async def list_sites(args):
    """List analyzed sites"""
    output_dir = Path(args.output_dir)
    sites_dir = output_dir / "sites"

    if not sites_dir.exists():
        print("No sites analyzed yet.")
        return

    print(f"\n{'=' * 80}")
    print("Analyzed Sites")
    print(f"{'=' * 80}")

    for investigation_file in sites_dir.glob("*_investigation.json"):
        import json

        with open(investigation_file) as f:
            data = json.load(f)

        print(f"\n{data['site_name']}")
        print(f"  URL: {data['site_url']}")
        print(f"  Approach: {data['recommended_approach']}")
        print(f"  API Endpoints: {len(data['api_endpoints'])}")
        print(f"  Date: {data['investigation_date']}")

    print(f"\n{'=' * 80}\n")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Site Analysis Tool - Analyze websites and generate integration code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Investigate ShopGoodwill
  %(prog)s investigate shopgoodwill https://shopgoodwill.com
  
  # Full analysis (investigation + code generation)
  %(prog)s analyze shopgoodwill https://shopgoodwill.com
  
  # List analyzed sites
  %(prog)s list
        """,
    )

    parser.add_argument(
        "--output-dir",
        default="output",
        help="Output directory for generated files (default: output)",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Investigate command
    investigate_parser = subparsers.add_parser(
        "investigate",
        help="Investigate a website (robots.txt, ToS, API discovery)",
    )
    investigate_parser.add_argument("site_name", help="Site identifier (e.g., shopgoodwill)")
    investigate_parser.add_argument("url", help="Site URL")

    # Analyze command
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Full site analysis (investigation + code generation)",
    )
    analyze_parser.add_argument("site_name", help="Site identifier (e.g., shopgoodwill)")
    analyze_parser.add_argument("url", help="Site URL")

    # List command
    list_parser = subparsers.add_parser(
        "list",
        help="List analyzed sites",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Run the appropriate command
    if args.command == "investigate":
        asyncio.run(investigate_site(args))
    elif args.command == "analyze":
        asyncio.run(analyze_site(args))
    elif args.command == "list":
        asyncio.run(list_sites(args))


if __name__ == "__main__":
    main()
