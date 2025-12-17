## Site Analysis & Integration Workflow

A comprehensive system for analyzing websites, discovering APIs, and automatically generating integration code, MCP servers, and data schemas.

## Overview

This workflow automates the process of integrating new websites into the ArbFinder suite by:

1. **Investigating** the site's structure, policies, and capabilities
2. **Discovering** API endpoints through multiple techniques
3. **Analyzing** discovered endpoints and reverse engineering their structure
4. **Generating** client libraries, schemas, and MCP servers
5. **Creating** OpenAI-compatible tools for AI agents

## Features

### 🔍 Site Investigation
- **Robots.txt Analysis**: Checks crawling permissions, rate limits, and allowed paths
- **LLMs.txt Support**: Detects AI-specific rules and restrictions
- **Terms of Service Analysis**: Identifies usage policies, API permissions, and restrictions
- **API Discovery**: Multiple techniques to discover API endpoints
- **Historical Data**: Wayback Machine integration for historical price data

### 🤖 AI Agent Crew
- **API Reverse Engineer**: Expert in analyzing and documenting APIs
- **MCP Server Architect**: Creates Model Context Protocol servers
- **Schema Designer**: Generates data models and database schemas
- **Site Investigator**: Coordinates the investigation workflow

### 📦 Generated Artifacts

For each analyzed site, the system generates:

- **Python API Client**: Async client with type hints
- **TypeScript API Client**: Full TypeScript client with interfaces
- **SQL Schema**: Database schema for storing API responses
- **Prisma Schema**: ORM schema for database access
- **Pydantic Models**: Python data validation models
- **TypeScript Interfaces**: Type-safe interfaces
- **MCP Server**: OpenAI-compatible tool server
- **Postman Collection**: API testing collection
- **Implementation Guide**: Step-by-step integration instructions

## Installation

```bash
# Install dependencies
pip install -e ".[dev]"

# Additional dependencies for site analysis
pip install httpx beautifulsoup4 lxml
```

## Quick Start

### 1. Investigate a Site (ShopGoodwill Example)

```bash
# Simple investigation
python backend/site_analysis_cli.py investigate shopgoodwill https://shopgoodwill.com

# Full analysis with code generation
python backend/site_analysis_cli.py analyze shopgoodwill https://shopgoodwill.com
```

### 2. Review Generated Artifacts

```bash
# List analyzed sites
python backend/site_analysis_cli.py list

# Check output directory
ls -R output/
```

### 3. Use Generated Code

#### Python Client

```python
from shopgoodwill_api import ShopgoodwillClient

client = ShopgoodwillClient(
    base_url="https://shopgoodwill.com",
    api_key=os.getenv("SHOPGOODWILL_API_KEY")
)

# Fetch listings
results = await client.get_listings(query="iPad", limit=20)
```

#### TypeScript Client

```typescript
import { ShopgoodwillClient } from './shopgoodwill_api';

const client = new ShopgoodwillClient(
  'https://shopgoodwill.com',
  process.env.SHOPGOODWILL_API_KEY
);

// Fetch listings
const results = await client.getListings({ query: 'iPad', limit: 20 });
```

#### MCP Server

```bash
# Set environment variables
export SHOPGOODWILL_BASE_URL="https://shopgoodwill.com"
export SHOPGOODWILL_API_KEY="your-api-key"

# Run MCP server
python output/mcp_servers/shopgoodwill/server.py
```

## Architecture

```
Site Analysis Workflow
├── Site Investigation
│   ├── Robots.txt Analyzer
│   ├── Terms of Service Analyzer
│   ├── API Discoverer
│   └── Historical Data Fetcher
├── API Analysis Agent
│   ├── Endpoint Categorization
│   ├── Python Client Generation
│   ├── TypeScript Client Generation
│   └── Postman Collection Generation
├── Schema Generator Agent
│   ├── Pydantic Models
│   ├── TypeScript Interfaces
│   ├── SQL Schema
│   └── Prisma Schema
└── MCP Server Agent
    ├── Server Code Generation
    ├── Tool Definitions
    └── OpenAI Schema Generation
```

## Directory Structure

```
backend/
├── site_investigator/
│   ├── investigator.py          # Main orchestrator
│   ├── robots_analyzer.py       # Robots.txt parser
│   ├── terms_analyzer.py        # ToS analyzer
│   ├── api_discoverer.py        # API discovery
│   └── historical_data.py       # Wayback Machine integration
├── agents/
│   ├── site_analysis_crew.py    # Crew coordinator
│   ├── api_analysis_agent.py    # API analysis
│   ├── schema_generator_agent.py # Schema generation
│   └── mcp_server_agent.py      # MCP server generation
└── site_analysis_cli.py         # CLI tool

output/
├── sites/                        # Investigation reports
│   ├── {site}_investigation.json
│   ├── {site}_config.toml
│   └── {site}_schema.json
├── apis/                         # API clients
│   ├── {site}_api.py
│   ├── {site}_api.ts
│   ├── {site}_schema.sql
│   └── {site}_postman.json
├── schemas/                      # Data schemas
│   ├── models.py
│   ├── types.ts
│   ├── schema.json
│   └── schema.prisma
└── mcp_servers/                  # MCP servers
    └── {site}/
        ├── server.py
        ├── tools.py
        ├── openai_tools.json
        └── README.md
```

## Site Investigation Process

### 1. Robots.txt Analysis

```python
from site_investigator import RobotsAnalyzer

analyzer = RobotsAnalyzer("https://shopgoodwill.com")
results = await analyzer.analyze()

# Check if crawling is allowed
if results['allowed']:
    crawl_delay = analyzer.get_recommended_delay(results)
    print(f"Crawl delay: {crawl_delay} seconds")
```

### 2. Terms of Service Analysis

```python
from site_investigator import TermsAnalyzer

analyzer = TermsAnalyzer("https://shopgoodwill.com", "shopgoodwill")
results = await analyzer.analyze()

print(f"API Allowed: {results['api_allowed']}")
print(f"Scraping Allowed: {results['scraping_allowed']}")
print(f"Commercial Use: {results['commercial_use_allowed']}")
```

### 3. API Discovery

```python
from site_investigator import APIDiscoverer

discoverer = APIDiscoverer("https://shopgoodwill.com")
results = await discoverer.discover()

print(f"Found {len(results['endpoints'])} endpoints")
for endpoint in results['endpoints']:
    print(f"  {endpoint['method']} {endpoint['path']}")
```

### 4. Historical Data

```python
from site_investigator import HistoricalDataFetcher

fetcher = HistoricalDataFetcher("https://shopgoodwill.com")
results = await fetcher.check_availability()

if results['available']:
    print(f"Snapshots available: {results['snapshot_count']}")
    
    # Get historical prices
    item_url = "https://shopgoodwill.com/item/12345"
    history = await fetcher.get_historical_prices(item_url)
```

## API Discovery Techniques

The system uses multiple techniques to discover API endpoints:

1. **Documentation Discovery**: Scans for Swagger/OpenAPI specs, API docs
2. **Network Analysis**: Analyzes JavaScript for API calls
3. **Sitemap Parsing**: Checks sitemap.xml for API-like paths
4. **Common Patterns**: Tests common API URL patterns
5. **Link Following**: Follows links to find API documentation

## MCP Server Integration

### Using with OpenAI

```python
import openai
import json

# Load tool definitions
with open("output/mcp_servers/shopgoodwill/openai_tools.json") as f:
    tools = json.load(f)

# Use with OpenAI API
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "Find iPad deals on ShopGoodwill"}
    ],
    tools=tools,
    tool_choice="auto"
)
```

### Using with LangChain

```python
from langchain.agents import initialize_agent
from langchain.tools import Tool

# Create tools from MCP server
tools = [
    Tool(
        name="search_listings",
        func=lambda query: mcp_client.search_listings(query),
        description="Search for items on ShopGoodwill"
    )
]

agent = initialize_agent(tools, llm, agent="zero-shot-react-description")
```

## CrewAI Integration

The site analysis agents are integrated into the CrewAI configuration:

```yaml
agents:
  site_investigator:
    role: "Website Investigation Specialist"
    goal: "Investigate websites to understand structure, policies, and capabilities"
    tools: [robots_analyzer, terms_parser, api_discoverer]
  
  api_reverse_engineer:
    role: "API Reverse Engineering Specialist"
    goal: "Analyze and document API endpoints"
    tools: [postman, endpoint_discoverer, function_generator]
  
  mcp_server_architect:
    role: "MCP Server Architect"
    goal: "Generate MCP servers with OpenAI-compatible tools"
    tools: [mcp_generator, openai_schema_builder]
  
  schema_designer:
    role: "Schema Design Specialist"
    goal: "Create comprehensive data schemas"
    tools: [schema_generator, type_inferrer]
```

## ShopGoodwill-Specific Features

### Investigation Results

When analyzing ShopGoodwill, the system will:

1. Check robots.txt for crawling rules
2. Analyze Terms of Service for API/scraping permissions
3. Discover available API endpoints
4. Check Wayback Machine for historical data (100k+ snapshots)
5. Generate site-specific configuration

### Generated Configuration

```toml
# config/sites/shopgoodwill_config.toml
[site]
name = "shopgoodwill"
url = "https://shopgoodwill.com"
approach = "API_PREFERRED"  # or WEB_SCRAPING, HISTORICAL_ONLY, MANUAL_EXPORT

[crawler]
enabled = true
crawl_delay = 2  # seconds

[api]
enabled = true
requires_auth = false

[historical]
wayback_available = true
snapshot_count = 123456
```

## Best Practices

### 1. Respect Site Policies

- Always check robots.txt before crawling
- Honor rate limits and crawl delays
- Review Terms of Service for restrictions
- Use API endpoints when available

### 2. Error Handling

```python
try:
    results = await crew.analyze_site()
except Exception as e:
    logger.error(f"Analysis failed: {e}")
    # Fallback to manual configuration
```

### 3. Rate Limiting

```python
# Built-in rate limiting
client = ShopgoodwillClient(
    base_url="https://shopgoodwill.com",
    rate_limit={"requests": 60, "period": 60}  # 60 req/min
)
```

### 4. Caching

```python
# Cache investigation results
results = await crew.analyze_site()
with open("cache/shopgoodwill.json", "w") as f:
    json.dump(results, f)
```

## Troubleshooting

### No API Endpoints Found

If no endpoints are discovered:

1. Check if the site has public APIs
2. Review the Terms of Service
3. Consider web scraping (if allowed)
4. Use manual data export

### Authentication Required

For sites requiring authentication:

1. Register for an API key
2. Set environment variable: `{SITE}_API_KEY`
3. Update generated code with auth logic

### Rate Limit Errors

If you hit rate limits:

1. Increase delays between requests
2. Implement exponential backoff
3. Use caching aggressively
4. Consider using proxies (ethically)

## Examples

### Complete Workflow

```python
from agents.site_analysis_crew import SiteAnalysisCrew

# Analyze site
crew = SiteAnalysisCrew(
    site_url="https://shopgoodwill.com",
    site_name="shopgoodwill"
)

results = await crew.analyze_site()

# Use generated client
from shopgoodwill_api import ShopgoodwillClient

client = ShopgoodwillClient(base_url=results['investigation']['site_url'])
items = await client.get_listings(query="iPad Pro")

# Store in database using generated schema
# (use generated SQL or Prisma schema)
```

### Adding a New Site

```bash
# 1. Investigate the site
python backend/site_analysis_cli.py analyze newsite https://newsite.com

# 2. Review generated files
ls output/sites/newsite/

# 3. Customize as needed
vim output/apis/newsite/newsite_api.py

# 4. Test the integration
python -c "
from newsite_api import NewsiteClient
client = NewsiteClient('https://newsite.com')
# Test API calls
"

# 5. Deploy MCP server
python output/mcp_servers/newsite/server.py
```

## Contributing

To add new analysis features:

1. Extend analyzers in `backend/site_investigator/`
2. Add new agent capabilities in `backend/agents/`
3. Update CrewAI configuration in `crew/crewai.yaml`
4. Add tests in `tests/`

## Future Enhancements

- [ ] Browser automation for JavaScript-heavy sites
- [ ] GraphQL endpoint discovery
- [ ] WebSocket support detection
- [ ] Authentication flow automation
- [ ] API versioning detection
- [ ] Rate limit detection from headers
- [ ] Auto-retry with exponential backoff
- [ ] Proxy rotation support
- [ ] Compliance monitoring
- [ ] Cost estimation for API usage

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
- GitHub Issues: https://github.com/cbwinslow/arbfinder-suite/issues
- Documentation: https://github.com/cbwinslow/arbfinder-suite/docs
