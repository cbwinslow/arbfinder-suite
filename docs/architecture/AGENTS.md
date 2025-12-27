# ArbFinder Suite - AI Agents Documentation

**Version**: 2.0  
**Last Updated**: 2025-12-15  
**Framework**: CrewAI + OpenRouter + LangChain  

---

## Table of Contents

1. [Overview](#overview)
2. [Agent Architecture](#agent-architecture)
3. [Configured Agents](#configured-agents)
4. [Agent Workflows](#agent-workflows)
5. [Tools and Capabilities](#tools-and-capabilities)
6. [Configuration Guide](#configuration-guide)
7. [Best Practices](#best-practices)
8. [Monitoring and Observability](#monitoring-and-observability)

---

## Overview

ArbFinder Suite employs a multi-agent AI system built on CrewAI, LangChain, and OpenRouter to automate complex workflows including web crawling, data validation, price analysis, content generation, and cross-platform listing distribution.

### Agent System Goals

- **Automation**: Reduce manual work through intelligent agents
- **Accuracy**: Maintain high data quality and analysis precision
- **Scalability**: Process thousands of items efficiently
- **Cost-Effectiveness**: Utilize free AI models when possible
- **Observability**: Track agent performance and costs

### Technology Stack

- **CrewAI**: Multi-agent orchestration framework
- **OpenRouter**: Universal LLM access (100+ models)
- **LangChain**: Agent toolkit and orchestration
- **LangSmith**: Execution tracing and debugging
- **LangFuse**: Cost analytics and monitoring
- **Cloudflare Workers**: Scheduled agent execution

---

## Agent Architecture

### System Design

```
┌─────────────────────────────────────────────────────────────┐
│                    ArbFinder Agent System                    │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Data        │    │  Analysis    │    │  Distribution│
│  Ingestion   │    │  Agents      │    │  Agents      │
│  Agents      │    │              │    │              │
└──────────────┘    └──────────────┘    └──────────────┘
    │                    │                    │
    ├─ Crawler          ├─ Researcher        ├─ Crosslister
    ├─ Validator        ├─ Pricer           └─ Notifier
    ├─ Enricher         └─ Analyzer
    └─ Processor
```

### Agent Communication

Agents communicate through:
1. **Shared Database**: Cloudflare D1 for persistent state
2. **Message Queues**: Cloudflare Queues for async tasks
3. **KV Store**: Temporary data and coordination
4. **Direct Handoffs**: CrewAI task delegation

### Agent Lifecycle

```
┌─────────┐     ┌─────────┐     ┌──────────┐     ┌─────────┐
│ Trigger │────▶│ Execute │────▶│ Validate │────▶│ Complete│
└─────────┘     └─────────┘     └──────────┘     └─────────┘
                     │                                  │
                     │                                  │
                     ▼                                  ▼
                ┌─────────┐                       ┌─────────┐
                │  Error  │                       │  Log    │
                │ Handler │                       │ Metrics │
                └─────────┘                       └─────────┘
```

---

## Configured Agents

### 1. Web Crawler Agent

**Role**: Web Crawler and Data Extraction Specialist  
**Goal**: Efficiently crawl target websites and extract structured product data  
**Status**: ✅ Active

#### Responsibilities
- Navigate target websites from configuration
- Extract product listings (title, price, condition, images)
- Handle pagination automatically
- Respect robots.txt and rate limits
- Store raw data for validation

#### Tools
- `crawl4ai`: AI-enhanced web crawler
- `html_parser`: BeautifulSoup and lxml
- `price_extractor`: Custom price parsing
- `image_downloader`: Async image fetching
- `duplicate_detector`: Content hashing

#### Configuration
```yaml
web_crawler:
  role: "Web Crawler Agent"
  goal: "Crawl target websites and extract price data efficiently"
  tools: [crawl4ai, html_parser, price_extractor]
  llm: "openrouter/anthropic/claude-instant-v1"
  temperature: 0.1  # Low temperature for consistency
  max_iterations: 10
  memory: true
  verbose: true
```

#### Performance Metrics
- **Pages/Minute**: 50+
- **Success Rate**: 98%+
- **Error Handling**: Automatic retry with exponential backoff
- **Resource Usage**: <50MB memory per instance

#### Example Task
```python
crawler_task = Task(
    description="Crawl ShopGoodwill for electronics under $100",
    agent=web_crawler,
    expected_output="List of product listings with structured data",
    tools=[crawl4ai, html_parser],
    context=[crawler_config]
)
```

---

### 2. Data Validator Agent

**Role**: Data Quality Assurance Specialist  
**Goal**: Ensure all ingested data meets quality standards  
**Status**: ✅ Active

#### Responsibilities
- Validate data completeness
- Check data types and formats
- Normalize prices and currencies
- Flag suspicious or anomalous data
- Clean and standardize text fields

#### Tools
- `schema_validator`: Pydantic models
- `data_cleaner`: Text normalization
- `duplicate_checker`: Fuzzy matching
- `anomaly_detector`: Statistical outlier detection
- `image_validator`: Image format and size checks

#### Configuration
```yaml
data_validator:
  role: "Data Validation Agent"
  goal: "Validate and clean data ensuring quality and consistency"
  tools: [schema_validator, data_cleaner, duplicate_checker]
  llm: "openrouter/meta-llama/llama-2-70b-chat"
  temperature: 0.0  # Deterministic validation
  quality_threshold: 0.85
```

#### Validation Rules
1. **Required Fields**: title, price, url, source
2. **Price Range**: $0.01 - $1,000,000
3. **Title Length**: 10-200 characters
4. **Image Count**: 1-20 images
5. **URL Format**: Valid HTTP/HTTPS URL
6. **Duplicate Check**: Hash-based deduplication

#### Example Output
```json
{
  "valid": true,
  "quality_score": 0.92,
  "issues": [],
  "cleaned_data": {
    "title": "Apple iPad Pro 11-inch 2021 128GB WiFi",
    "price": 299.99,
    "currency": "USD",
    "condition": "Good"
  }
}
```

---

### 3. Market Researcher Agent

**Role**: Market Research and Trend Analysis Specialist  
**Goal**: Collect comparable sales and analyze market trends  
**Status**: ✅ Active

#### Responsibilities
- Fetch eBay sold listings (comparables)
- Calculate market statistics (avg, median, percentiles)
- Analyze price trends over time
- Identify seasonal patterns
- Provide confidence scores

#### Tools
- `ebay_api`: eBay Finding API
- `web_search`: General web search
- `statistics_engine`: NumPy/Pandas analytics
- `trend_analyzer`: Time-series analysis
- `comparable_cache`: KV-based caching

#### Configuration
```yaml
market_researcher:
  role: "Market Researcher"
  goal: "Collect comps and analyze pricing trends accurately"
  tools: [ebay_api, web_search, statistics_engine]
  llm: "openrouter/openai/gpt-3.5-turbo"
  temperature: 0.3
  comp_limit: 150
  lookback_days: 90
```

#### Analysis Output
```json
{
  "item": "iPad Pro 11-inch 2021",
  "comparable_count": 47,
  "avg_price": 550.00,
  "median_price": 525.00,
  "p25": 475.00,
  "p75": 600.00,
  "trend": "stable",
  "confidence": 0.92,
  "updated_at": "2025-12-15T10:30:00Z"
}
```

---

### 4. Price Specialist Agent

**Role**: Pricing Strategy and Optimization Specialist  
**Goal**: Calculate optimal prices accounting for all costs and fees  
**Status**: ✅ Active

#### Responsibilities
- Calculate target list price
- Account for marketplace fees (eBay, Mercari, etc.)
- Factor in shipping costs
- Compute profit margins
- Recommend pricing strategies

#### Tools
- `fee_calculator`: Platform-specific fee calculators
- `shipping_estimator`: USPS/FedEx/UPS rate APIs
- `profit_optimizer`: Margin optimization algorithms
- `pricing_rules`: Category-specific rules
- `competitor_pricer`: Competitive pricing analysis

#### Configuration
```yaml
price_specialist:
  role: "Price Specialist"
  goal: "Compute optimal prices maximizing profit while remaining competitive"
  tools: [fee_calculator, shipping_estimator, profit_optimizer]
  llm: "openrouter/anthropic/claude-2"
  temperature: 0.2
  target_margin_pct: 30.0
  min_margin_pct: 15.0
```

#### Fee Calculations

**eBay Fees**:
- Final value fee: 12.9% of sale price
- Payment processing: 2.9% + $0.30
- Store subscription: Variable
- Promoted listings: Optional 2-20%

**Mercari Fees**:
- Service fee: 10% of sale price
- Payment processing: 2.9% + $0.30
- Seller protection: Included

#### Example Calculation
```python
{
  "item_cost": 299.99,
  "target_price": 550.00,
  "fees": {
    "ebay_fvf": 70.95,  # 12.9%
    "payment": 16.25,   # 2.9% + $0.30
    "shipping": 15.00
  },
  "total_fees": 102.20,
  "profit": 147.81,
  "margin_pct": 26.9,
  "recommendation": "List at $550, auto-accept $500+"
}
```

---

### 5. Listing Writer Agent

**Role**: Content Creation and SEO Specialist  
**Goal**: Create compelling, optimized product listings  
**Status**: ✅ Active

#### Responsibilities
- Generate SEO-optimized titles
- Write persuasive product descriptions
- Extract and highlight key features
- Include condition notes
- Adapt content for different platforms

#### Tools
- `template_library`: Category-specific templates
- `seo_optimizer`: Keyword research and optimization
- `content_generator`: LLM-based text generation
- `feature_extractor`: NLP feature identification
- `platform_formatter`: Platform-specific formatting

#### Configuration
```yaml
listing_writer:
  role: "Listing Specialist"
  goal: "Draft SEO-optimized listings that convert browsers to buyers"
  tools: [template_library, seo_optimizer, content_generator]
  llm: "openrouter/anthropic/claude-instant-v1"
  temperature: 0.7
  max_tokens: 500
  style: "professional"
```

#### Title Generation

**Best Practices**:
- Lead with brand name
- Include specific model
- Add key specs (size, capacity, year)
- Mention condition
- Use power words (Excellent, Fast, New)
- Stay within character limits (80 for eBay)

**Example**:
```
Bad:  "Nice iPad"
Good: "Apple iPad Pro 11" 2021 128GB WiFi Excellent Condition + Accessories"
```

#### Description Template
```markdown
## Product Details
- Brand: Apple
- Model: iPad Pro 11-inch (3rd Gen)
- Year: 2021
- Storage: 128GB
- Connectivity: WiFi Only
- Condition: Excellent

## Description
This iPad Pro is in excellent condition with minimal signs of use. 
Screen is pristine with no scratches. Battery health at 95%.

## What's Included
- iPad Pro 11-inch
- Original charging cable
- USB-C power adapter
- Original box

## Shipping
Ships within 1 business day via USPS Priority Mail with tracking.

## Returns
30-day returns accepted. Buyer pays return shipping.
```

---

### 6. Image Processor Agent

**Role**: Image Optimization and Management Specialist  
**Goal**: Process, optimize, and store product images  
**Status**: 🚧 In Development

#### Responsibilities
- Download images from source URLs
- Optimize image size and quality
- Generate thumbnails (multiple sizes)
- Apply watermarks (optional)
- Upload to Cloudflare R2
- Extract image metadata

#### Tools
- `image_downloader`: Async HTTP image fetching
- `image_optimizer`: PIL/Pillow optimization
- `thumbnail_generator`: Multi-size thumbnail creation
- `watermark_applicator`: Image composition
- `bucket_uploader`: R2/S3 upload
- `image_analyzer`: Computer vision (future)

#### Configuration
```yaml
image_processor:
  role: "Image Processing Agent"
  goal: "Optimize and store images efficiently with proper metadata"
  tools: [image_optimizer, thumbnail_generator, bucket_uploader]
  llm: "openrouter/google/gemini-pro"  # Good for vision
  max_size_mb: 5
  thumbnail_sizes: [100, 300, 600, 1200]
  watermark: false
```

#### Image Specifications

**Original Images**:
- Format: JPEG, PNG, WebP
- Max size: 5MB
- Max dimensions: 4096x4096
- Quality: 85% JPEG compression

**Thumbnails**:
- 100x100: List view
- 300x300: Grid view
- 600x600: Detail view
- 1200x1200: Full-screen view

---

### 7. Metadata Enricher Agent

**Role**: Data Enhancement and Classification Specialist  
**Goal**: Fill missing metadata using AI and external sources  
**Status**: 🚧 In Development

#### Responsibilities
- Identify missing metadata fields
- Extract information from titles/descriptions
- Classify products into categories
- Look up brand information
- Standardize attributes
- Add tags and keywords

#### Tools
- `llm_extractor`: LLM-based metadata extraction
- `category_classifier`: ML-based categorization
- `brand_database`: Brand name lookup
- `attribute_normalizer`: Standardization rules
- `tag_generator`: Keyword tagging

#### Configuration
```yaml
metadata_enricher:
  role: "Metadata Enrichment Agent"
  goal: "Fill missing metadata using AI and maintain data completeness"
  tools: [llm_extractor, category_classifier, brand_database]
  llm: "openrouter/openai/gpt-4-turbo"
  temperature: 0.4
  confidence_threshold: 0.8
```

#### Metadata Fields
- Category (Electronics > Computers > Tablets)
- Brand (Apple, Samsung, etc.)
- Model (iPad Pro 11-inch)
- Year (2021)
- Specifications (128GB, WiFi)
- Color (Space Gray)
- Condition (Excellent)
- Tags (tablet, apple, ipad, portable)

---

### 8. Title Enhancer Agent

**Role**: Title Optimization Specialist  
**Goal**: Improve and standardize product titles for searchability  
**Status**: 🚧 In Development

#### Responsibilities
- Analyze existing titles
- Identify missing keywords
- Standardize format and structure
- Optimize for search engines
- Ensure platform compliance
- A/B testing recommendations

#### Tools
- `nlp_processor`: spaCy or NLTK
- `keyword_analyzer`: SEO keyword research
- `title_templates`: Category-specific patterns
- `competitor_analyzer`: Competitor title analysis
- `ab_tester`: Title performance tracking

#### Configuration
```yaml
title_enhancer:
  role: "Title Enhancement Agent"
  goal: "Optimize titles for maximum searchability and conversion"
  tools: [nlp_processor, keyword_analyzer, title_templates]
  llm: "openrouter/anthropic/claude-2"
  temperature: 0.5
  max_length: 80
```

---

### 9. Cross-listing Operator Agent

**Role**: Multi-Platform Distribution Specialist  
**Goal**: Prepare and distribute listings across marketplaces  
**Status**: 🔜 Planned

#### Responsibilities
- Format listings per platform requirements
- Generate CSV exports for bulk uploads
- Call platform APIs (eBay, Mercari, Poshmark)
- Handle category mapping
- Manage inventory sync
- Track listing status

#### Tools
- `platform_api`: Marketplace API clients
- `csv_exporter`: CSV generation
- `category_mapper`: Cross-platform category mapping
- `batch_processor`: Bulk operation handling
- `inventory_sync`: Stock level management

#### Configuration
```yaml
crosslister:
  role: "Cross-listing Operator"
  goal: "Distribute listings efficiently across multiple platforms"
  tools: [platform_api, csv_exporter, batch_processor]
  platforms: [ebay, mercari, poshmark]
  batch_size: 50
  retry_count: 3
```

---

### 10. Quality Monitor Agent

**Role**: Quality Assurance and Anomaly Detection Specialist  
**Goal**: Maintain high data quality and detect issues  
**Status**: 🔜 Planned

#### Responsibilities
- Monitor data quality metrics
- Detect anomalies and outliers
- Flag suspicious listings
- Track agent performance
- Generate quality reports
- Trigger alerts for issues

#### Tools
- `anomaly_detector`: Statistical analysis
- `quality_metrics`: Custom quality scoring
- `alert_system`: Notification service
- `report_generator`: Automated reporting
- `drift_detector`: Data drift monitoring

#### Configuration
```yaml
quality_monitor:
  role: "Quality Monitor Agent"
  goal: "Ensure data quality and detect anomalies proactively"
  tools: [anomaly_detector, quality_metrics, alert_system]
  schedule: "*/30 * * * *"  # Every 30 minutes
  alert_threshold: 0.05  # Alert if >5% failures
```

---

## Agent Workflows

### Workflow 1: Data Ingestion

**Purpose**: Crawl websites and ingest product data

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  1. Crawl   │────▶│ 2. Validate │────▶│  3. Enrich  │
│   Website   │     │    Data     │     │  Metadata   │
└─────────────┘     └─────────────┘     └─────────────┘
       │                    │                    │
       │                    │                    │
       ▼                    ▼                    ▼
  Crawler Agent      Validator Agent      Enricher Agent
       │                    │                    │
       └────────────────────┴────────────────────┘
                           │
                           ▼
                   ┌──────────────┐
                   │  4. Process  │
                   │    Images    │
                   └──────────────┘
                           │
                           ▼
                   Image Processor
                           │
                           ▼
                   ┌──────────────┐
                   │   5. Store   │
                   │   in D1/R2   │
                   └──────────────┘
```

**Execution**:
```python
from crewai import Crew, Process

ingestion_crew = Crew(
    agents=[web_crawler, data_validator, metadata_enricher, image_processor],
    tasks=[crawl_task, validate_task, enrich_task, process_images_task],
    process=Process.sequential,
    verbose=True
)

result = ingestion_crew.kickoff()
```

---

### Workflow 2: Listing Creation

**Purpose**: Create optimized listings for marketplaces

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ 1. Research │────▶│  2. Price   │────▶│  3. Write   │
│   Market    │     │   Analysis  │     │   Listing   │
└─────────────┘     └─────────────┘     └─────────────┘
       │                    │                    │
       │                    │                    │
       ▼                    ▼                    ▼
  Researcher Agent    Price Specialist    Listing Writer
       │                    │                    │
       └────────────────────┴────────────────────┘
                           │
                           ▼
                   ┌──────────────┐
                   │ 4. Crosslist │
                   │   Platforms  │
                   └──────────────┘
                           │
                           ▼
                  Crosslister Agent
```

**Execution**:
```python
listing_crew = Crew(
    agents=[market_researcher, price_specialist, listing_writer, crosslister],
    tasks=[research_task, pricing_task, writing_task, crosslist_task],
    process=Process.sequential,
    memory=True,
    verbose=True
)

result = listing_crew.kickoff(inputs={"item_id": "12345"})
```

---

### Workflow 3: Metadata Enrichment

**Purpose**: Fill missing metadata for existing items

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  1. Detect  │────▶│  2. Extract │────▶│  3. Enhance │
│   Missing   │     │  Metadata   │     │   Titles    │
└─────────────┘     └─────────────┘     └─────────────┘
       │                    │                    │
       │                    │                    │
       ▼                    ▼                    ▼
  Quality Monitor     Metadata Enricher    Title Enhancer
       │                    │                    │
       └────────────────────┴────────────────────┘
                           │
                           ▼
                   ┌──────────────┐
                   │  4. Validate │
                   │    Quality   │
                   └──────────────┘
                           │
                           ▼
                  Quality Monitor
```

**Scheduled Execution**:
```python
# Runs every 15 minutes via Cloudflare Cron Trigger
@worker.scheduled("*/15 * * * *")
async def enrich_metadata():
    enrichment_crew = Crew(
        agents=[quality_monitor, metadata_enricher, title_enhancer],
        tasks=[detect_task, extract_task, enhance_task, validate_task],
        process=Process.sequential
    )
    await enrichment_crew.kickoff()
```

---

## Tools and Capabilities

### Web Scraping Tools

#### crawl4ai
- AI-enhanced web crawler
- JavaScript rendering support
- Anti-bot detection bypass
- Proxy rotation support
- Session management

#### html_parser
- BeautifulSoup4 for HTML parsing
- lxml for fast XML/HTML processing
- CSS selector support
- XPath queries
- Schema.org microdata extraction

#### price_extractor
- Regular expression patterns
- Currency detection and normalization
- Multiple price format support
- Shipping cost extraction
- Tax calculation awareness

---

### Data Processing Tools

#### schema_validator
- Pydantic model validation
- Type checking and coercion
- Custom validation rules
- Error collection and reporting
- JSON schema support

#### data_cleaner
- Text normalization (Unicode, whitespace)
- HTML entity decoding
- Special character handling
- Duplicate space removal
- Case normalization

#### duplicate_checker
- Content hashing (SHA256)
- Fuzzy string matching (RapidFuzz)
- Image similarity (perceptual hashing)
- Configurable similarity threshold
- Batch deduplication

---

### AI/LLM Tools

#### OpenRouter Client
- Access to 100+ models
- Automatic model fallback
- Cost tracking per request
- Rate limit handling
- Streaming support

#### LangChain Tools
- Agents and chains
- Memory management (conversation, summary)
- Tool calling
- Prompt templates
- Output parsers

---

### External APIs

#### eBay Finding API
- Sold listings search
- Active listings search
- Category browsing
- Advanced filtering
- Rate limit: 5000 calls/day

#### Payment APIs
- Stripe (primary)
- PayPal (future)
- Square (future)

#### Notification APIs
- SendGrid (email)
- Twilio (SMS)
- Firebase (push notifications)

---

## Configuration Guide

### Environment Variables

```bash
# OpenRouter API
OPENROUTER_API_KEY=your-key-here
OPENROUTER_MODEL_PREFERENCE=free  # free, cheap, best

# eBay API
EBAY_APP_ID=your-ebay-app-id
EBAY_CERT_ID=your-ebay-cert-id

# Cloudflare
CLOUDFLARE_ACCOUNT_ID=your-account-id
CLOUDFLARE_API_TOKEN=your-api-token

# Database
DATABASE_URL=your-d1-or-postgres-url

# Observability
LANGSMITH_API_KEY=your-langsmith-key
LANGFUSE_PUBLIC_KEY=your-langfuse-public-key
LANGFUSE_SECRET_KEY=your-langfuse-secret-key
```

### CrewAI Configuration

```yaml
# crew/crewai.yaml
project: arbfinder

agents:
  web_crawler:
    role: "Web Crawler Agent"
    goal: "Crawl websites efficiently and extract structured data"
    tools: [crawl4ai, html_parser]
    llm: "openrouter/anthropic/claude-instant-v1"
    temperature: 0.1
    max_iterations: 10
    verbose: true

workers:
  crawler_worker:
    agent: web_crawler
    schedule: "0 */4 * * *"  # Every 4 hours
    task: "Run scheduled crawls"
    max_runtime: 3600  # 1 hour timeout

processes:
  ingest_data:
    - task: crawl_sites
      agent: web_crawler
    - task: validate_data
      agent: data_validator
    - task: enrich_metadata
      agent: metadata_enricher
```

### LangChain Integration

```python
from langchain.agents import initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain_openrouter import ChatOpenRouter

# Initialize LLM via OpenRouter
llm = ChatOpenRouter(
    model="anthropic/claude-instant-v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0.7
)

# Create memory for conversation
memory = ConversationBufferMemory()

# Initialize agent with tools
agent = initialize_agent(
    tools=[ebay_search_tool, price_calculator_tool],
    llm=llm,
    memory=memory,
    agent="conversational-react-description",
    verbose=True
)

# Execute agent task
result = agent.run("Find comparable prices for iPad Pro 11-inch")
```

---

## Best Practices

### Agent Development

1. **Single Responsibility**: Each agent should have one clear purpose
2. **Idempotency**: Agent operations should be safely repeatable
3. **Error Handling**: Always handle errors gracefully with retries
4. **Logging**: Log all agent actions for debugging
5. **Testing**: Unit test each agent independently

### Performance Optimization

1. **Caching**: Cache LLM responses for duplicate queries
2. **Batching**: Process multiple items together when possible
3. **Async Operations**: Use async/await for I/O-bound tasks
4. **Resource Limits**: Set memory and timeout limits
5. **Cost Management**: Use free models for simple tasks

### Security

1. **API Key Security**: Never hardcode API keys
2. **Input Validation**: Validate all inputs before processing
3. **Rate Limiting**: Respect third-party API rate limits
4. **Data Privacy**: Don't log sensitive user data
5. **Access Control**: Implement RBAC for agent operations

---

## Monitoring and Observability

### LangSmith Integration

```python
from langsmith import Client

client = Client(api_key=os.getenv("LANGSMITH_API_KEY"))

# Trace agent execution
with client.trace(
    name="price_analysis",
    tags=["agent", "market_researcher"]
) as tracer:
    result = market_researcher.execute(task)
    tracer.log_output(result)
```

### LangFuse Integration

```python
from langfuse import Langfuse

langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY")
)

# Track LLM costs
trace = langfuse.trace(name="listing_generation")
generation = trace.generation(
    name="write_description",
    model="openrouter/anthropic/claude-instant-v1",
    input=prompt,
    output=result,
    usage={"tokens": 500, "cost": 0.001}
)
```

### Metrics to Track

- **Agent Execution Time**: How long each agent takes
- **Success Rate**: Percentage of successful completions
- **Error Rate**: Failures per agent
- **LLM Costs**: Spending per agent/task
- **Token Usage**: Input/output tokens per model
- **Cache Hit Rate**: How often cached responses are used
- **Queue Depth**: Backlog of pending tasks

### Alerting Rules

```yaml
alerts:
  - name: High Error Rate
    condition: error_rate > 0.05  # >5%
    window: 5m
    action: notify_slack

  - name: High LLM Costs
    condition: hourly_cost > 10.00  # $10/hour
    action: notify_email

  - name: Agent Timeout
    condition: execution_time > 3600  # 1 hour
    action: kill_and_notify
```

---

**End of Agents Documentation**
