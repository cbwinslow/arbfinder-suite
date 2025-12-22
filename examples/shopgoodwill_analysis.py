#!/usr/bin/env python3
"""
Example: Analyzing ShopGoodwill.com

This example demonstrates how to use the site analysis system to investigate
ShopGoodwill.com and generate all necessary integration code.
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from agents.site_analysis_crew import SiteAnalysisCrew
from site_investigator import SiteInvestigator


async def investigate_only():
    """
    Example 1: Just investigate the site without generating code
    
    This is useful when you want to:
    - Check if the site has an API
    - Review Terms of Service
    - See what data is available
    - Decide on the best integration approach
    """
    print("\n" + "=" * 80)
    print("Example 1: Site Investigation Only")
    print("=" * 80 + "\n")
    
    investigator = SiteInvestigator(
        site_url="https://shopgoodwill.com",
        site_name="shopgoodwill",
        output_dir="output/sites",
    )
    
    report = await investigator.investigate()
    
    print(f"\n✓ Investigation Complete!")
    print(f"\nKey Findings:")
    print(f"  - Robots.txt allows crawling: {report.robots_allowed}")
    print(f"  - API available: {bool(report.api_endpoints)}")
    print(f"  - API endpoints found: {len(report.api_endpoints)}")
    print(f"  - Scraping allowed: {report.scraping_allowed}")
    print(f"  - Historical data available: {report.wayback_available}")
    print(f"  - Recommended approach: {report.recommended_approach}")
    
    if report.implementation_notes:
        print(f"\n  Implementation Notes:")
        for note in report.implementation_notes:
            print(f"    - {note}")
    
    print(f"\n  Generated Files:")
    print(f"    - Config: {report.config_file}")
    print(f"    - Schema: {report.schema_file}")
    
    return report


async def full_analysis():
    """
    Example 2: Complete site analysis with code generation
    
    This generates everything needed to integrate the site:
    - Python and TypeScript API clients
    - Database schemas (SQL, Prisma, Pydantic, TypeScript)
    - MCP server with OpenAI-compatible tools
    - Postman collection for API testing
    - Implementation guide
    """
    print("\n" + "=" * 80)
    print("Example 2: Full Site Analysis with Code Generation")
    print("=" * 80 + "\n")
    
    crew = SiteAnalysisCrew(
        site_url="https://shopgoodwill.com",
        site_name="shopgoodwill",
        output_dir="output",
    )
    
    print("Starting comprehensive analysis...")
    print("This will:")
    print("  1. Investigate the site (robots.txt, ToS, APIs)")
    print("  2. Analyze discovered API endpoints")
    print("  3. Generate Python and TypeScript clients")
    print("  4. Create database schemas")
    print("  5. Build an MCP server for AI agents")
    print("  6. Generate Postman collection")
    print("")
    
    results = await crew.analyze_site()
    
    if results["status"] == "completed":
        print(f"\n✓ Analysis Complete!")
        print(f"\nGenerated {len(results['artifacts'])} artifacts:")
        
        # Group artifacts by type
        api_files = [f for f in results["artifacts"] if "/apis/" in f]
        schema_files = [f for f in results["artifacts"] if "/schemas/" in f]
        mcp_files = [f for f in results["artifacts"] if "/mcp_servers/" in f]
        other_files = [
            f
            for f in results["artifacts"]
            if f not in api_files + schema_files + mcp_files
        ]
        
        if api_files:
            print(f"\n  API Clients:")
            for f in api_files:
                print(f"    - {Path(f).name}")
        
        if schema_files:
            print(f"\n  Schemas:")
            for f in schema_files:
                print(f"    - {Path(f).name}")
        
        if mcp_files:
            print(f"\n  MCP Server:")
            for f in mcp_files:
                print(f"    - {Path(f).name}")
        
        if other_files:
            print(f"\n  Documentation:")
            for f in other_files:
                print(f"    - {Path(f).name}")
        
        print(f"\n  All files saved in: output/")
        
    elif results["status"] == "failed":
        print(f"\n✗ Analysis failed: {results.get('error')}")
    
    return results


async def using_generated_client():
    """
    Example 3: Using the generated Python client
    
    After running full_analysis(), you can use the generated client:
    """
    print("\n" + "=" * 80)
    print("Example 3: Using Generated Client")
    print("=" * 80 + "\n")
    
    print("After running the analysis, you can use the generated client like this:")
    print("")
    print("```python")
    print("from shopgoodwill_api import ShopgoodwillClient")
    print("")
    print("# Initialize client")
    print('client = ShopgoodwillClient(')
    print('    base_url="https://shopgoodwill.com",')
    print('    api_key=os.getenv("SHOPGOODWILL_API_KEY")  # If required')
    print(")")
    print("")
    print("# Fetch listings")
    print('results = await client.get_listings(query="iPad Pro", limit=20)')
    print("")
    print("# Process results")
    print("for item in results['items']:")
    print("    print(f\"{item['title']}: ${item['price']}\")")
    print("")
    print("# Clean up")
    print("await client.close()")
    print("```")


async def using_mcp_server():
    """
    Example 4: Using the generated MCP server
    
    The MCP server allows AI agents to interact with the site's API
    """
    print("\n" + "=" * 80)
    print("Example 4: Using the MCP Server")
    print("=" * 80 + "\n")
    
    print("The generated MCP server can be used with AI agents:")
    print("")
    print("1. Start the MCP server:")
    print("   ```bash")
    print("   export SHOPGOODWILL_BASE_URL=https://shopgoodwill.com")
    print("   export SHOPGOODWILL_API_KEY=your-key  # If required")
    print("   python output/mcp_servers/shopgoodwill/server.py")
    print("   ```")
    print("")
    print("2. Use with OpenAI:")
    print("   ```python")
    print("   import openai")
    print("   import json")
    print("   ")
    print("   # Load tool definitions")
    print('   with open("output/mcp_servers/shopgoodwill/openai_tools.json") as f:')
    print("       tools = json.load(f)")
    print("   ")
    print("   # Use with OpenAI API")
    print("   response = openai.ChatCompletion.create(")
    print('       model="gpt-4",')
    print("       messages=[")
    print('           {"role": "user", "content": "Find iPad deals"}')
    print("       ],")
    print("       tools=tools,")
    print("   )")
    print("   ```")


async def main():
    """Run all examples"""
    print("\n" + "=" * 80)
    print("ShopGoodwill.com Analysis Examples")
    print("=" * 80)
    
    # Example 1: Investigation only
    # await investigate_only()
    
    # Example 2: Full analysis (uncomment to run)
    # await full_analysis()
    
    # Example 3 & 4: Usage examples (just print code)
    await using_generated_client()
    await using_mcp_server()
    
    print("\n" + "=" * 80)
    print("To run the actual analysis, uncomment the examples in main()")
    print("Note: The full analysis may take 1-2 minutes to complete")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
