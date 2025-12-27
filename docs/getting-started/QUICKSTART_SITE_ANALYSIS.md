# Quick Start: Site Analysis System

Get started with the automated site analysis and integration system in 5 minutes.

## Prerequisites

```bash
pip install httpx beautifulsoup4 lxml pydantic
```

## Basic Usage

### 1. Investigate a Site

```bash
python backend/site_analysis_cli.py investigate shopgoodwill https://shopgoodwill.com
```

**Output:**
- `output/sites/shopgoodwill_investigation.json` - Full investigation report
- `output/sites/shopgoodwill_config.toml` - Site configuration
- `output/sites/shopgoodwill_schema.json` - Data schema

### 2. Generate Full Integration

```bash
python backend/site_analysis_cli.py analyze shopgoodwill https://shopgoodwill.com
```

**Output:**
- Python API client
- TypeScript API client
- Database schemas (SQL, Prisma, Pydantic, TypeScript)
- MCP server with OpenAI-compatible tools
- Postman collection
- Implementation guide

### 3. Use Generated Code

#### Python Client

```python
from shopgoodwill_api import ShopgoodwillClient

client = ShopgoodwillClient(base_url="https://shopgoodwill.com")
results = await client.get_listings(query="iPad Pro", limit=20)
```

#### MCP Server

```bash
export SHOPGOODWILL_BASE_URL="https://shopgoodwill.com"
python output/mcp_servers/shopgoodwill/server.py
```

## What Gets Analyzed?

✅ **Robots.txt** - Crawling rules, rate limits, allowed paths  
✅ **LLMs.txt** - AI-specific usage rules (if available)  
✅ **Terms of Service** - API permissions, scraping policy, restrictions  
✅ **API Endpoints** - Automatic discovery via multiple techniques  
✅ **Historical Data** - Wayback Machine availability (100k+ snapshots)  

## What Gets Generated?

### For Each Site:
- ✅ Python async API client
- ✅ TypeScript API client
- ✅ SQL database schema
- ✅ Prisma ORM schema
- ✅ Pydantic models
- ✅ TypeScript interfaces
- ✅ MCP server (OpenAI-compatible)
- ✅ Postman collection
- ✅ Implementation guide

## Advanced Examples

### Programmatic Use

```python
from agents.site_analysis_crew import SiteAnalysisCrew

crew = SiteAnalysisCrew(
    site_url="https://shopgoodwill.com",
    site_name="shopgoodwill"
)

results = await crew.analyze_site()

if results["status"] == "completed":
    print(f"Generated {len(results['artifacts'])} files")
```

### Historical Price Data

```python
from site_investigator import HistoricalDataFetcher

fetcher = HistoricalDataFetcher("https://shopgoodwill.com")

# Check availability
availability = await fetcher.check_availability()
print(f"Snapshots: {availability['snapshot_count']}")

# Get historical prices for an item
item_url = "https://shopgoodwill.com/item/12345"
price_history = await fetcher.get_historical_prices(item_url)
```

## Output Directory Structure

```
output/
├── sites/                      # Investigation reports
│   ├── shopgoodwill_investigation.json
│   ├── shopgoodwill_config.toml
│   └── shopgoodwill_schema.json
├── apis/                       # API clients
│   ├── shopgoodwill/
│   │   ├── shopgoodwill_api.py
│   │   ├── shopgoodwill_api.ts
│   │   ├── shopgoodwill_schema.sql
│   │   └── shopgoodwill_postman.json
├── schemas/                    # Data schemas
│   └── shopgoodwill/
│       ├── models.py           # Pydantic
│       ├── types.ts            # TypeScript
│       ├── schema.json         # JSON Schema
│       └── schema.prisma       # Prisma ORM
└── mcp_servers/               # MCP servers
    └── shopgoodwill/
        ├── server.py
        ├── tools.py
        ├── openai_tools.json
        └── README.md
```

## Tips & Best Practices

### 1. Start with Investigation
Run `investigate` first to understand the site's capabilities before generating code.

### 2. Respect Site Policies
The system automatically checks robots.txt and Terms of Service. Always follow the recommendations.

### 3. Use API When Available
If the site has a public API, use it instead of scraping for better reliability.

### 4. Rate Limiting
The generated clients include rate limiting. Configure based on the site's rules:

```python
client = ShopgoodwillClient(
    base_url="https://shopgoodwill.com",
    rate_limit={"requests": 60, "period": 60}  # 60 req/min
)
```

### 5. Historical Data
Use Wayback Machine for items that are no longer available:

```python
# Get snapshots from the last 5 years
snapshots = await fetcher.get_yearly_snapshots(item_url, years_back=5)
```

## Common Use Cases

### 1. Add a New Site to ArbFinder

```bash
# Analyze the site
python backend/site_analysis_cli.py analyze newsite https://newsite.com

# Review generated files
ls output/apis/newsite/

# Integrate with existing code
# Use generated client in your scrapers
```

### 2. Create MCP Server for AI Agents

```bash
# Generate MCP server
python backend/site_analysis_cli.py analyze mysite https://mysite.com

# Start the MCP server
cd output/mcp_servers/mysite
python server.py

# Use with OpenAI or other LLMs
```

### 3. Research Historical Pricing

```python
# For archived items
fetcher = HistoricalDataFetcher("https://shopgoodwill.com")
history = await fetcher.get_historical_prices(
    "https://shopgoodwill.com/item/old-item-123",
    from_date=datetime(2020, 1, 1),
    to_date=datetime(2024, 12, 31)
)
```

## Troubleshooting

### No API Endpoints Found
- Check if the site has a public API
- Review Terms of Service for restrictions
- Consider web scraping (if allowed) or manual export

### Import Errors
```bash
pip install httpx beautifulsoup4 lxml pydantic
```

### Rate Limit Errors
- Increase delays between requests
- Use the site's recommended crawl delay
- Implement exponential backoff

## Next Steps

1. **Read the full documentation**: [SITE_ANALYSIS.md](SITE_ANALYSIS.md)
2. **See working examples**: [examples/shopgoodwill_analysis.py](examples/shopgoodwill_analysis.py)
3. **Run the tests**: `pytest tests/test_site_analysis.py -v`
4. **Contribute**: Add new discovery techniques or agent capabilities

## Support

- 📖 Documentation: [SITE_ANALYSIS.md](SITE_ANALYSIS.md)
- 💻 Examples: [examples/](examples/)
- 🐛 Issues: [GitHub Issues](https://github.com/cbwinslow/arbfinder-suite/issues)
- 📧 Questions: Open a discussion on GitHub

---

**Ready to analyze your first site?**

```bash
python backend/site_analysis_cli.py investigate shopgoodwill https://shopgoodwill.com
```
