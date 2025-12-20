"""
Site Analysis Crew
Coordinates all agents to perform comprehensive site analysis and setup
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from agents.api_analysis_agent import APIAnalysisAgent
from agents.mcp_server_agent import MCPServerAgent
from agents.schema_generator_agent import SchemaGeneratorAgent
from site_investigator import SiteInvestigator

logger = logging.getLogger(__name__)


class SiteAnalysisCrew:
    """
    Crew that coordinates all agents for site analysis

    Workflow:
    1. Site Investigation (robots.txt, ToS, API discovery, historical data)
    2. API Analysis (reverse engineering, function generation)
    3. Schema Generation (data models, database schemas)
    4. MCP Server Generation (OpenAI-compatible tools)
    """

    def __init__(
        self,
        site_url: str,
        site_name: str,
        output_dir: str = "output",
    ):
        """Initialize site analysis crew"""
        self.site_url = site_url
        self.site_name = site_name
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize investigator
        self.investigator = SiteInvestigator(
            site_url=site_url,
            site_name=site_name,
            output_dir=str(self.output_dir / "sites"),
        )

        # Initialize agents
        self.api_agent = APIAnalysisAgent(
            site_name=site_name,
            output_dir=str(self.output_dir / "apis"),
        )

        self.schema_agent = SchemaGeneratorAgent(
            site_name=site_name,
            output_dir=str(self.output_dir / "schemas"),
        )

        self.mcp_agent = MCPServerAgent(
            site_name=site_name,
            output_dir=str(self.output_dir / "mcp_servers"),
        )

    async def analyze_site(self) -> Dict[str, Any]:
        """
        Perform comprehensive site analysis

        Returns:
            Complete analysis results with all generated artifacts
        """
        logger.info(f"Starting site analysis workflow for {self.site_name}")

        results = {
            "site_name": self.site_name,
            "site_url": self.site_url,
            "status": "in_progress",
            "investigation": None,
            "api_analysis": None,
            "schemas": None,
            "mcp_server": None,
            "artifacts": [],
        }

        try:
            # Step 1: Site Investigation
            logger.info("Step 1: Investigating site...")
            investigation_report = await self.investigator.investigate()
            results["investigation"] = investigation_report.model_dump()

            # Check if we can proceed
            if not investigation_report.api_endpoints and not investigation_report.scraping_allowed:
                logger.warning(
                    "No API endpoints found and scraping not allowed. "
                    "Manual data export may be required."
                )
                results["status"] = "limited"
                return results

            # Step 2: API Analysis
            if investigation_report.api_endpoints:
                logger.info(
                    f"Step 2: Analyzing {len(investigation_report.api_endpoints)} API endpoints..."
                )
                api_results = self.api_agent.analyze_endpoints(investigation_report.api_endpoints)
                results["api_analysis"] = api_results
                results["artifacts"].extend(api_results.get("functions", {}).values())

            # Step 3: Schema Generation
            logger.info("Step 3: Generating schemas...")
            schema_results = self.schema_agent.generate_schemas(investigation_report.api_endpoints)
            results["schemas"] = schema_results
            results["artifacts"].extend(schema_results.values())

            # Step 4: MCP Server Generation
            logger.info("Step 4: Generating MCP server...")
            mcp_results = self.mcp_agent.generate_mcp_server(
                investigation_report.api_endpoints,
                {
                    "url": self.site_url,
                    "name": self.site_name,
                    "approach": investigation_report.recommended_approach,
                },
            )
            results["mcp_server"] = mcp_results
            results["artifacts"].extend(mcp_results.values())

            # Generate summary report
            summary = self._generate_summary(results)
            summary_file = self.output_dir / f"{self.site_name}_summary.json"
            with open(summary_file, "w") as f:
                json.dump(summary, f, indent=2)
            results["artifacts"].append(str(summary_file))

            # Generate implementation guide
            guide = self._generate_implementation_guide(results)
            guide_file = self.output_dir / f"{self.site_name}_implementation_guide.md"
            with open(guide_file, "w") as f:
                f.write(guide)
            results["artifacts"].append(str(guide_file))

            results["status"] = "completed"
            logger.info(
                f"Site analysis completed. Generated {len(results['artifacts'])} artifacts."
            )

        except Exception as e:
            logger.error(f"Error during site analysis: {e}", exc_info=True)
            results["status"] = "failed"
            results["error"] = str(e)

        return results

    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate analysis summary"""

        investigation = results.get("investigation", {})

        summary = {
            "site": self.site_name,
            "url": self.site_url,
            "analysis_complete": results["status"] == "completed",
            "recommended_approach": investigation.get("recommended_approach"),
            "capabilities": {
                "robots_allowed": investigation.get("robots_allowed", False),
                "api_available": bool(investigation.get("api_endpoints")),
                "api_endpoint_count": len(investigation.get("api_endpoints", [])),
                "scraping_allowed": investigation.get("scraping_allowed", False),
                "historical_data_available": investigation.get("wayback_available", False),
                "requires_authentication": investigation.get("requires_authentication", False),
            },
            "artifacts": {
                "python_client": results.get("api_analysis", {}).get("functions", {}).get("python"),
                "typescript_client": results.get("api_analysis", {})
                .get("functions", {})
                .get("typescript"),
                "schemas": results.get("schemas", {}),
                "mcp_server": results.get("mcp_server", {}),
            },
            "implementation_notes": investigation.get("implementation_notes", []),
        }

        return summary

    def _generate_implementation_guide(self, results: Dict[str, Any]) -> str:
        """Generate implementation guide"""

        investigation = results.get("investigation", {})

        lines = [
            f"# Implementation Guide: {self.site_name}",
            "",
            f"Site: {self.site_url}",
            f"Analysis Date: {investigation.get('investigation_date')}",
            "",
            "## Summary",
            "",
            f"Recommended Approach: **{investigation.get('recommended_approach')}**",
            "",
            "## Capabilities",
            "",
            f"- Robots.txt Allowed: {investigation.get('robots_allowed')}",
            f"- API Available: {bool(investigation.get('api_endpoints'))}",
            f"- API Endpoints Discovered: {len(investigation.get('api_endpoints', []))}",
            f"- Scraping Allowed: {investigation.get('scraping_allowed')}",
            f"- Historical Data (Wayback): {investigation.get('wayback_available')}",
            f"- Authentication Required: {investigation.get('requires_authentication')}",
            "",
            "## Implementation Notes",
            "",
        ]

        for note in investigation.get("implementation_notes", []):
            lines.append(f"- {note}")

        lines.extend(
            [
                "",
                "## Generated Artifacts",
                "",
                "### API Client Libraries",
                "",
            ]
        )

        if results.get("api_analysis"):
            api_funcs = results["api_analysis"].get("functions", {})
            if api_funcs.get("python"):
                lines.append(f"- Python: `{api_funcs['python']}`")
            if api_funcs.get("typescript"):
                lines.append(f"- TypeScript: `{api_funcs['typescript']}`")

        lines.extend(
            [
                "",
                "### Schemas",
                "",
            ]
        )

        if results.get("schemas"):
            for schema_type, path in results["schemas"].items():
                lines.append(f"- {schema_type}: `{path}`")

        lines.extend(
            [
                "",
                "### MCP Server",
                "",
            ]
        )

        if results.get("mcp_server"):
            for component, path in results["mcp_server"].items():
                lines.append(f"- {component}: `{path}`")

        lines.extend(
            [
                "",
                "## Quick Start",
                "",
                "### Using Python Client",
                "",
                "```python",
                f"from {self.site_name}_api import {self._to_class_name(self.site_name)}Client",
                "",
                f"client = {self._to_class_name(self.site_name)}Client(",
                f'    base_url="{self.site_url}",',
                "    api_key=os.getenv('API_KEY')  # If required",
                ")",
                "",
                "# Use the client",
                "# results = await client.get_listings()",
                "```",
                "",
                "### Using MCP Server",
                "",
                "```bash",
                "# Set environment variables",
                f'export {self.site_name.upper()}_BASE_URL="{self.site_url}"',
                f'export {self.site_name.upper()}_API_KEY="your-key"  # If required',
                "",
                "# Run MCP server",
                f"python output/mcp_servers/{self.site_name}/server.py",
                "```",
                "",
                "## Next Steps",
                "",
                "1. Review the generated code and customize as needed",
                "2. Test the API client with real requests",
                "3. Integrate the MCP server with your AI agents",
                "4. Set up data ingestion pipelines",
                "5. Configure rate limiting and error handling",
                "",
                "## Support",
                "",
                "For issues or questions, refer to the main project documentation.",
            ]
        )

        return "\n".join(lines)

    def _to_class_name(self, name: str) -> str:
        """Convert name to PascalCase"""
        return "".join(word.capitalize() for word in name.split("_"))


# Example usage for ShopGoodwill
async def analyze_shopgoodwill():
    """Analyze ShopGoodwill.com"""
    crew = SiteAnalysisCrew(
        site_url="https://shopgoodwill.com",
        site_name="shopgoodwill",
        output_dir="output",
    )

    results = await crew.analyze_site()

    print(f"\n{'=' * 80}")
    print(f"Site Analysis Complete: {results['site_name']}")
    print(f"{'=' * 80}")
    print(f"Status: {results['status']}")
    print(f"\nGenerated {len(results['artifacts'])} artifacts:")
    for artifact in results["artifacts"]:
        print(f"  - {artifact}")
    print(f"{'=' * 80}\n")

    return results


if __name__ == "__main__":
    asyncio.run(analyze_shopgoodwill())
