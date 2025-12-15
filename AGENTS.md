# AI Agents Documentation

This document describes all AI agents in the ArbFinder Suite, their roles, capabilities, and integration details.

## Overview

ArbFinder Suite uses multiple AI agent frameworks to automate various tasks:

- **CrewAI:** Orchestrates multi-agent workflows for complex tasks
- **OpenRouter:** Provides access to multiple LLM models including free options
- **LangChain:** Manages agent memory, tools, and workflows
- **LangGraph:** Defines complex workflow graphs with state management

---

## Agent Architecture

```
┌─────────────────────────────────────────────────┐
│           Agent Orchestration Layer             │
│  (CrewAI + LangChain + LangGraph)              │
└─────────────────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
   ┌─────────┐  ┌─────────┐  ┌─────────┐
   │  Data   │  │ Market  │  │ Content │
   │ Agents  │  │ Agents  │  │ Agents  │
   └─────────┘  └─────────┘  └─────────┘
        │             │             │
        └─────────────┼─────────────┘
                      ▼
        ┌──────────────────────────┐
        │   OpenRouter API         │
        │   (Free Models)          │
        └──────────────────────────┘
```

---

## Agent Categories

### 1. Data Ingestion Agents

#### Web Crawler Agent
**Status:** ✅ Implemented  
**Framework:** CrewAI  
**Model:** OpenRouter free models

**Role:** Crawl target websites and extract structured data

**Capabilities:**
- Navigate multiple marketplace websites
- Extract product listings, prices, and images
- Handle pagination and infinite scroll
- Respect robots.txt and rate limits
- Retry failed requests with exponential backoff

**Tools:**
- `crawl4ai`: AI-powered web crawler
- `html_parser`: BeautifulSoup HTML parsing
- `price_extractor`: Custom price extraction logic

**Configuration:**
```yaml
agent: web_crawler
schedule: "0 */4 * * *"  # Every 4 hours
targets:
  - shopgoodwill.com
  - govdeals.com
  - governmentsurplus.com
max_pages: 100
timeout: 30s
```

**Example Usage:**
```python
from arbfinder.agents import WebCrawlerAgent

agent = WebCrawlerAgent(
    model="openrouter/free-model",
    max_pages=50
)

results = await agent.crawl(
    urls=["https://shopgoodwill.com/search/electronics"],
    extract_schema=ProductSchema
)
```

#### Data Validator Agent
**Status:** ✅ Implemented  
**Framework:** CrewAI  
**Model:** Rule-based + AI validation

**Role:** Validate and clean incoming data ensuring quality

**Capabilities:**
- Schema validation
- Data type checking
- Duplicate detection
- Data normalization
- Anomaly detection

**Tools:**
- `schema_validator`: Pydantic model validation
- `data_cleaner`: Data normalization functions
- `duplicate_checker`: Fuzzy matching for duplicates

**Validation Rules:**
- Price must be numeric and positive
- Title must be 10-200 characters
- URL must be valid and unique
- Timestamp must be recent (< 7 days old)
- Required fields: title, price, url, source

---

### 2. Market Research Agents

#### Market Researcher Agent
**Status:** 🚧 In Progress  
**Framework:** CrewAI  
**Model:** OpenRouter GPT-4-turbo (free tier)

**Role:** Analyze market trends and comparable prices

**Capabilities:**
- Collect comparable sales data
- Analyze price trends over time
- Identify seasonal patterns
- Calculate market demand indicators
- Generate price recommendations

**Tools:**
- `web_search`: Search for comparable listings
- `provider_scan`: Scan multiple marketplaces
- `price_aggregator`: Aggregate pricing data
- `trend_analyzer`: Time series analysis

**Example Analysis:**
```json
{
  "item": "RTX 3060 Graphics Card",
  "comps_found": 47,
  "avg_price": 289.50,
  "price_range": [210, 380],
  "trend": "stable",
  "confidence": 0.87,
  "recommendation": {
    "buy_below": 250,
    "sell_at": 295,
    "profit_margin": 18
  }
}
```

#### Price Specialist Agent
**Status:** 🚧 In Progress  
**Framework:** CrewAI  
**Model:** OpenRouter Claude-3-Sonnet (free tier)

**Role:** Calculate optimal pricing with fees and margins

**Capabilities:**
- Calculate platform fees (eBay, Mercari, etc.)
- Factor in shipping costs
- Apply condition multipliers
- Set competitive pricing
- Generate auto-offer thresholds

**Pricing Formula:**
```python
target_price = (
    base_price 
    * condition_multiplier 
    * market_demand_factor
    + shipping_cost
    + platform_fee
    + desired_margin
)
```

**Fee Structure:**
```yaml
platforms:
  ebay:
    insertion_fee: 0.35
    final_value_fee: 0.129  # 12.9%
    payment_processing: 0.029  # 2.9% + $0.30
  mercari:
    selling_fee: 0.10  # 10%
    payment_processing: 0.029
  reverb:
    selling_fee: 0.05  # 5%
    payment_processing: 0.029
```

---

### 3. Content Creation Agents

#### Listing Writer Agent
**Status:** 📋 Planned  
**Framework:** CrewAI  
**Model:** OpenRouter GPT-3.5-turbo (free tier)

**Role:** Generate SEO-optimized product listings

**Capabilities:**
- Write compelling product titles
- Generate detailed descriptions
- Add relevant keywords
- Include condition notes
- Optimize for platform search

**Templates:**
```yaml
title_template: |
  {brand} {model} {category} - {condition} - {key_features}

description_template: |
  ## Product Details
  {detailed_description}
  
  ## Condition
  {condition_notes}
  
  ## Specifications
  {specifications}
  
  ## Shipping & Returns
  {shipping_info}
```

**SEO Optimization:**
- Keyword density: 2-3%
- Title length: 60-80 characters
- Description length: 200-500 words
- Include long-tail keywords
- Use bullet points for readability

#### Image Processor Agent
**Status:** ✅ Implemented  
**Framework:** Custom + Cloudflare Workers  
**Model:** N/A (Image processing)

**Role:** Process and optimize product images

**Capabilities:**
- Resize and compress images
- Generate thumbnails
- Remove backgrounds (optional)
- Add watermarks
- Upload to R2 storage

**Image Pipeline:**
1. Download original image
2. Validate format and size
3. Generate multiple sizes (thumbnail, medium, large)
4. Compress with quality optimization
5. Upload to R2 bucket
6. Generate CDN URLs
7. Store metadata in database

**Configuration:**
```yaml
image_processing:
  formats: [jpg, png, webp]
  sizes:
    thumbnail: 200x200
    medium: 800x800
    large: 1600x1600
  quality: 85
  max_file_size: 5MB
  compression: true
```

---

### 4. Metadata Enrichment Agents

#### Metadata Enricher Agent
**Status:** 🚧 In Progress  
**Framework:** CrewAI + LangChain  
**Model:** OpenRouter Mixtral-8x7B (free tier)

**Role:** Fill missing metadata using AI

**Capabilities:**
- Extract category from title/description
- Identify brand and model
- Extract specifications
- Generate tags
- Classify item type

**Enrichment Process:**
```python
# Input
{
  "title": "Gaming Laptop - i7, 16GB RAM, RTX 3060",
  "price": 899.99
}

# Output
{
  "title": "Gaming Laptop - i7, 16GB RAM, RTX 3060",
  "price": 899.99,
  "category": "Electronics > Computers > Laptops",
  "brand": "Unknown",
  "specifications": {
    "processor": "Intel Core i7",
    "ram": "16GB",
    "gpu": "NVIDIA RTX 3060"
  },
  "tags": ["gaming", "laptop", "nvidia", "intel"],
  "condition_estimated": "Used - Good"
}
```

#### Title Enhancer Agent
**Status:** 📋 Planned  
**Framework:** CrewAI  
**Model:** OpenRouter GPT-3.5-turbo (free tier)

**Role:** Improve and standardize product titles

**Capabilities:**
- Remove unnecessary words
- Fix capitalization
- Add missing details
- Follow platform conventions
- Maintain brand consistency

**Enhancement Examples:**
```yaml
before: "laptop gaming GREAT DEAL!!!! i7"
after: "Gaming Laptop - Intel Core i7 - High Performance"

before: "iphone 12 - blue - 128 gb - unlocked"
after: "Apple iPhone 12 128GB Unlocked - Blue - Excellent Condition"

before: "Graphics Card RTX"
after: "NVIDIA GeForce RTX 3060 Graphics Card - 12GB GDDR6"
```

---

### 5. Cross-Listing and Distribution

#### Crosslister Agent
**Status:** 📋 Planned  
**Framework:** CrewAI  
**Model:** Rule-based automation

**Role:** Distribute listings across multiple platforms

**Capabilities:**
- Format for different platforms
- Handle platform-specific requirements
- Manage listing inventory
- Sync updates across platforms
- Handle delisting

**Supported Platforms:**
- eBay (via API)
- Mercari (via CSV export)
- Reverb (via API)
- Amazon (via SP-API)
- Facebook Marketplace (manual export)

**Example Workflow:**
```yaml
workflow:
  - create_master_listing
  - generate_platform_variants:
      - ebay:
          category: "Electronics > Computer Components"
          format: "Buy It Now"
          shipping: "Calculated"
      - mercari:
          category: "Electronics"
          shipping_included: true
      - reverb:
          category: "Guitars & Basses"
          make_an_offer: true
  - publish_to_platforms
  - monitor_status
```

---

### 6. Monitoring and Quality Control

#### Quality Monitor Agent
**Status:** 📋 Planned  
**Framework:** LangChain  
**Model:** OpenRouter free models

**Role:** Monitor data quality and detect anomalies

**Capabilities:**
- Track data quality metrics
- Detect price anomalies
- Flag suspicious listings
- Monitor agent performance
- Generate quality reports

**Monitored Metrics:**
```yaml
data_quality:
  completeness: 95%  # Fields filled
  accuracy: 98%      # Validated correct
  consistency: 92%   # Matches schema
  timeliness: 99%    # Updated recently
  uniqueness: 100%   # No duplicates

agent_performance:
  success_rate: 94%
  avg_latency: 2.3s
  error_rate: 0.06
  throughput: 150/min
```

**Anomaly Detection:**
- Price outliers (>3 standard deviations)
- Suspicious patterns (duplicate IDs, bot-like behavior)
- Data drift (schema changes, new values)
- Performance degradation (latency spikes, errors)

---

## Agent Orchestration

### Workflow: Data Ingestion Pipeline

```python
from arbfinder.agents import workflow

@workflow.define("ingest_data")
async def ingest_data_workflow(search_query: str):
    # Step 1: Crawl websites
    crawler = agents.get("web_crawler")
    raw_data = await crawler.execute(query=search_query)
    
    # Step 2: Validate data
    validator = agents.get("data_validator")
    validated = await validator.execute(data=raw_data)
    
    # Step 3: Enrich metadata
    enricher = agents.get("metadata_enricher")
    enriched = await enricher.execute(data=validated)
    
    # Step 4: Process images
    image_proc = agents.get("image_processor")
    final = await image_proc.execute(data=enriched)
    
    return final
```

### Workflow: Listing Creation Pipeline

```python
@workflow.define("create_listing")
async def create_listing_workflow(item_id: str):
    # Step 1: Research market
    researcher = agents.get("market_researcher")
    market_data = await researcher.execute(item_id=item_id)
    
    # Step 2: Calculate pricing
    pricer = agents.get("price_specialist")
    pricing = await pricer.execute(market_data=market_data)
    
    # Step 3: Write listing
    writer = agents.get("listing_writer")
    listing = await writer.execute(
        item_id=item_id,
        pricing=pricing
    )
    
    # Step 4: Crosslist
    crosslister = agents.get("crosslister")
    result = await crosslister.execute(listing=listing)
    
    return result
```

---

## Agent Configuration

### Environment Variables

```bash
# OpenRouter API
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# LangChain
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2_pt_...
LANGCHAIN_PROJECT=arbfinder-suite

# LangSmith
LANGSMITH_API_KEY=lsv2_sk_...

# LangFuse
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com

# CrewAI
CREWAI_TELEMETRY=false
```

### Model Selection

```yaml
# config/agents/models.yaml
default_model: "openrouter/auto"  # Auto-select best free model

model_preferences:
  web_crawler: "openrouter/free"
  data_validator: "local/rules"  # No LLM needed
  market_researcher: "openrouter/gpt-3.5-turbo"
  price_specialist: "openrouter/claude-3-haiku"
  listing_writer: "openrouter/mixtral-8x7b"
  metadata_enricher: "openrouter/mistral-7b"

fallback_models:
  - "openrouter/gpt-3.5-turbo"
  - "openrouter/claude-3-haiku"
  - "openrouter/mixtral-8x7b"
```

---

## Agent API Reference

### Base Agent Interface

```python
from arbfinder.agents.base import BaseAgent

class CustomAgent(BaseAgent):
    """Base class for all agents"""
    
    def __init__(
        self,
        name: str,
        role: str,
        model: str,
        tools: List[str],
        **kwargs
    ):
        super().__init__(name, role, model, tools, **kwargs)
    
    async def execute(self, **inputs) -> Dict[str, Any]:
        """Execute agent task"""
        raise NotImplementedError
    
    async def validate_inputs(self, inputs: Dict) -> bool:
        """Validate input parameters"""
        return True
    
    async def format_output(self, result: Any) -> Dict:
        """Format output for consistency"""
        return {"result": result}
```

### Agent Registry

```python
from arbfinder.agents import registry

# Register agent
@registry.register("custom_agent")
class CustomAgent(BaseAgent):
    pass

# Get agent instance
agent = registry.get("custom_agent")

# List all agents
all_agents = registry.list()

# Check if agent exists
exists = registry.has("custom_agent")
```

### Agent Execution

```python
from arbfinder.agents import execute_agent

# Synchronous execution
result = execute_agent(
    "web_crawler",
    query="RTX 3060",
    max_pages=10
)

# Asynchronous execution
result = await execute_agent_async(
    "web_crawler",
    query="RTX 3060",
    max_pages=10
)

# Batch execution
results = await execute_agents_batch([
    ("web_crawler", {"query": "RTX 3060"}),
    ("web_crawler", {"query": "iPad Pro"}),
    ("web_crawler", {"query": "MacBook"})
])
```

---

## Monitoring and Observability

### LangSmith Integration

All agent executions are automatically traced:

```python
from langsmith import Client

client = Client()

# Get traces for a specific agent
traces = client.list_runs(
    project_name="arbfinder-suite",
    filter='eq(name, "web_crawler")'
)

# Get performance metrics
metrics = client.get_run_stats(
    project_name="arbfinder-suite"
)
```

### LangFuse Dashboard

Access metrics at: `https://cloud.langfuse.com`

**Available Metrics:**
- Agent execution count
- Average latency per agent
- Success/failure rates
- Token usage and costs
- Error logs and traces

### Custom Metrics

```python
from arbfinder.agents.metrics import track_metric

@track_metric("agent_execution")
async def execute_with_metrics(agent_name: str, **inputs):
    start = time.time()
    try:
        result = await execute_agent_async(agent_name, **inputs)
        track_metric("agent_success", agent_name=agent_name)
        return result
    except Exception as e:
        track_metric("agent_error", agent_name=agent_name, error=str(e))
        raise
    finally:
        duration = time.time() - start
        track_metric("agent_latency", agent_name=agent_name, duration=duration)
```

---

## Best Practices

### 1. Agent Design
- Keep agents focused on single responsibility
- Use composition over inheritance
- Implement proper error handling
- Add comprehensive logging
- Document expected inputs/outputs

### 2. Model Selection
- Use free models for non-critical tasks
- Fall back to cheaper models on quota limits
- Cache responses when possible
- Batch requests to reduce API calls
- Monitor token usage and costs

### 3. Performance
- Implement async execution
- Use connection pooling
- Cache frequently accessed data
- Set appropriate timeouts
- Implement circuit breakers

### 4. Testing
- Unit test agent logic
- Integration test workflows
- Mock external API calls
- Test error scenarios
- Load test under production load

### 5. Security
- Never log API keys
- Validate all inputs
- Sanitize outputs
- Rate limit API calls
- Implement authentication

---

## Troubleshooting

### Common Issues

**Issue: Agent timeouts**
```python
# Solution: Increase timeout
agent = WebCrawlerAgent(timeout=60)  # seconds
```

**Issue: Rate limit errors**
```python
# Solution: Implement backoff
from tenacity import retry, wait_exponential

@retry(wait=wait_exponential(multiplier=1, min=4, max=10))
async def call_with_retry():
    return await agent.execute()
```

**Issue: Memory leaks**
```python
# Solution: Clean up resources
async with agent:
    result = await agent.execute()
# Resources automatically cleaned up
```

---

## Roadmap

### Q1 2025
- ✅ CrewAI agent framework
- ✅ OpenRouter integration
- 🚧 LangChain integration
- 📋 LangSmith tracing

### Q2 2025
- 📋 LangGraph workflows
- 📋 Advanced agent memory
- 📋 Multi-agent collaboration
- 📋 Custom agent marketplace

### Q3 2025
- 📋 Fine-tuned models
- 📋 Agent performance optimization
- 📋 Real-time agent monitoring
- 📋 Agent A/B testing

### Q4 2025
- 📋 Agent marketplace
- 📋 Community agents
- 📋 Enterprise features
- 📋 Advanced analytics

---

Last Updated: 2024-12-15  
Version: 1.0
