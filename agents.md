# 🤖 ArbFinder Suite - AI Agents Architecture

## Overview

ArbFinder Suite uses a multi-agent system powered by CrewAI to automate various aspects of price arbitrage detection, data enrichment, and listing management. Each agent is a specialized AI worker designed to perform specific tasks with high autonomy and reliability.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Agent Orchestration Layer                    │
│                         (CrewAI Core)                            │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Input Layer │     │  Processing  │     │ Output Layer │
│              │     │    Agents    │     │              │
│ • Job Queue  │────▶│  (10 Types)  │────▶│ • Database   │
│ • Webhooks   │     │              │     │ • APIs       │
│ • Scheduler  │     │              │     │ • Storage    │
└──────────────┘     └──────────────┘     └──────────────┘
        │                     │                     │
        └─────────────────────┴─────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │   Monitoring &    │
                    │   Observability   │
                    │  (LangSmith/Fuse) │
                    └───────────────────┘
```

---

## 👥 Agent Types

### 1. 🕷️ Web Crawler Agent
**Role**: Data Extraction Specialist  
**Goal**: Extract structured data from e-commerce websites  
**Backstory**: Expert in web scraping with deep knowledge of HTML parsing and JavaScript rendering.

#### Capabilities
- Async concurrent crawling
- JavaScript rendering via Crawl4AI
- Rate limiting and politeness
- Proxy rotation support
- Retry logic with exponential backoff
- CSS selector-based extraction

#### Configuration
```yaml
web_crawler:
  role: "Data Extraction Specialist"
  goal: "Extract accurate product data from configured websites"
  tools:
    - crawl4ai_tool
    - beautifulsoup_parser
    - javascript_renderer
  max_iterations: 5
  max_rpm: 60
  memory: true
```

#### Inputs
- Target URL
- CSS selectors for data fields
- JavaScript rendering requirements
- Rate limit configuration

#### Outputs
```json
{
  "items": [
    {
      "title": "iPhone 12 Pro Max",
      "price": 599.99,
      "currency": "USD",
      "condition": "Good",
      "url": "https://...",
      "images": ["url1", "url2"]
    }
  ],
  "metadata": {
    "crawl_duration": 3.5,
    "items_found": 45,
    "success_rate": 0.98
  }
}
```

---

### 2. ✅ Data Validator Agent
**Role**: Quality Assurance Expert  
**Goal**: Ensure data quality and consistency  
**Backstory**: Meticulous quality engineer with expertise in data validation and cleansing.

#### Capabilities
- Schema validation
- Data type checking
- Range and boundary validation
- Duplicate detection
- Missing data identification
- Anomaly detection

#### Validation Rules
```python
VALIDATION_RULES = {
    'price': {
        'type': 'float',
        'min': 0.01,
        'max': 999999.99,
        'required': True
    },
    'title': {
        'type': 'string',
        'min_length': 3,
        'max_length': 500,
        'required': True
    },
    'url': {
        'type': 'url',
        'schemes': ['http', 'https'],
        'required': True
    }
}
```

#### Outputs
```json
{
  "status": "passed",
  "validated_items": 42,
  "failed_items": 3,
  "errors": [
    {
      "item_id": "xyz",
      "field": "price",
      "error": "Value out of range"
    }
  ]
}
```

---

### 3. 📊 Market Research Agent
**Role**: Pricing Analyst  
**Goal**: Analyze market trends and pricing patterns  
**Backstory**: Data scientist with expertise in market analysis and statistical modeling.

#### Capabilities
- Historical price analysis
- Trend detection
- Seasonal adjustment
- Market segmentation
- Competitor analysis
- Demand forecasting

#### Analysis Types
1. **Price Distribution Analysis**
   - Mean, median, mode
   - Standard deviation
   - Quartiles and percentiles

2. **Trend Analysis**
   - Linear regression
   - Moving averages
   - Exponential smoothing

3. **Anomaly Detection**
   - Z-score analysis
   - IQR-based outlier detection
   - Isolation forest algorithm

#### Outputs
```json
{
  "category": "Electronics > Phones",
  "statistics": {
    "avg_price": 450.25,
    "median_price": 425.00,
    "std_dev": 125.50,
    "sample_size": 1523
  },
  "trends": {
    "7_day_change": -5.2,
    "30_day_change": -12.8,
    "direction": "declining"
  },
  "recommendations": {
    "suggested_price": 425.00,
    "confidence": 0.87
  }
}
```

---

### 4. 💰 Price Specialist Agent
**Role**: Pricing Strategist  
**Goal**: Optimize pricing for maximum profit  
**Backstory**: Financial analyst with deep understanding of pricing psychology and arbitrage.

#### Capabilities
- Competitive pricing analysis
- Profit margin calculation
- Dynamic pricing strategies
- Discount threshold detection
- ROI estimation
- Breakeven analysis

#### Pricing Strategies
```python
PRICING_STRATEGIES = {
    'market_based': {
        'method': 'percentile',
        'percentile': 25,  # Price at 25th percentile
        'min_margin': 0.20
    },
    'cost_plus': {
        'method': 'markup',
        'markup': 1.50,  # 50% markup
        'min_margin': 0.15
    },
    'competitive': {
        'method': 'undercut',
        'undercut_pct': 0.05,  # 5% below competition
        'min_margin': 0.10
    }
}
```

#### Outputs
```json
{
  "item_id": "abc123",
  "current_price": 599.99,
  "market_price": 699.99,
  "recommended_price": 649.99,
  "estimated_profit": 125.50,
  "margin": 0.24,
  "discount_pct": 7.1,
  "strategy": "competitive",
  "confidence": 0.92
}
```

---

### 5. ✍️ Listing Writer Agent
**Role**: Content Creation Expert  
**Goal**: Create compelling, SEO-optimized product listings  
**Backstory**: Marketing copywriter with expertise in e-commerce and SEO.

#### Capabilities
- SEO keyword optimization
- Compelling headline generation
- Feature bullet point creation
- Product description writing
- Category classification
- Tag generation

#### Writing Templates
```python
TEMPLATES = {
    'electronics': {
        'headline': "{brand} {model} - {condition} - {key_feature}",
        'bullets': [
            "Brand: {brand}",
            "Model: {model}",
            "Condition: {condition}",
            "Includes: {included_items}",
            "Ships from: {location}"
        ]
    }
}
```

#### Outputs
```json
{
  "title": "Apple iPhone 12 Pro Max - Excellent - Unlocked 256GB",
  "description": "Experience the power of 5G with this pristine iPhone 12 Pro Max...",
  "bullets": [
    "• 256GB storage capacity",
    "• Unlocked for all carriers",
    "• Excellent cosmetic condition",
    "• Includes original box and accessories"
  ],
  "tags": ["iphone", "apple", "smartphone", "5g", "unlocked"],
  "category": "Electronics > Cell Phones > Smartphones",
  "seo_score": 85
}
```

---

### 6. 🖼️ Image Processor Agent
**Role**: Visual Content Specialist  
**Goal**: Optimize and enhance product images  
**Backstory**: Computer vision expert with skills in image processing and enhancement.

#### Capabilities
- Image compression and optimization
- Background removal
- Image enhancement (brightness, contrast)
- Watermark addition
- Format conversion
- Thumbnail generation
- Cloud upload (R2, MinIO)

#### Processing Pipeline
```
Original Image → Validation → Enhancement → Compression
                     ↓             ↓            ↓
                 Dimension    Background    Format
                   Check       Removal     Conversion
                     ↓             ↓            ↓
                 Thumbnail ← Watermark ← Cloud Upload
```

#### Outputs
```json
{
  "original_url": "https://source.com/image.jpg",
  "processed_urls": {
    "full": "https://cdn.arbfinder.com/abc123-full.jpg",
    "thumbnail": "https://cdn.arbfinder.com/abc123-thumb.jpg",
    "square": "https://cdn.arbfinder.com/abc123-square.jpg"
  },
  "metadata": {
    "original_size": 2048576,
    "compressed_size": 256000,
    "compression_ratio": 0.875,
    "format": "webp",
    "dimensions": "1200x800"
  }
}
```

---

### 7. 🏷️ Metadata Enricher Agent
**Role**: Data Enhancement Specialist  
**Goal**: Fill missing metadata using AI inference  
**Backstory**: Machine learning engineer specializing in data enrichment and NLP.

#### Capabilities
- Brand extraction from titles
- Model number identification
- Condition inference from descriptions
- Specification parsing
- Category classification
- Missing field prediction

#### Enrichment Methods
```python
ENRICHMENT_METHODS = {
    'brand': 'nlp_entity_extraction',
    'model': 'regex_pattern_matching',
    'condition': 'keyword_classification',
    'category': 'ml_classification_model',
    'specs': 'structured_data_extraction'
}
```

#### Outputs
```json
{
  "item_id": "xyz789",
  "enriched_fields": {
    "brand": {
      "value": "Sony",
      "confidence": 0.95,
      "method": "nlp_entity_extraction"
    },
    "model": {
      "value": "WH-1000XM4",
      "confidence": 0.92,
      "method": "regex_pattern"
    },
    "category": {
      "value": "Electronics > Audio > Headphones",
      "confidence": 0.88,
      "method": "ml_classification"
    }
  }
}
```

---

### 8. 🎯 Title Enhancer Agent
**Role**: SEO Optimization Expert  
**Goal**: Optimize product titles for search visibility  
**Backstory**: SEO specialist with expertise in e-commerce title optimization.

#### Capabilities
- Keyword optimization
- Character limit compliance
- Brand/model prominence
- Condition clarity
- Feature highlighting
- A/B testing support

#### Enhancement Rules
```python
TITLE_RULES = {
    'max_length': 80,
    'required_elements': ['brand', 'model', 'condition'],
    'optional_elements': ['color', 'size', 'key_feature'],
    'capitalization': 'title_case',
    'separator': ' - '
}
```

#### Outputs
```json
{
  "original_title": "sony headphones good condition",
  "enhanced_title": "Sony WH-1000XM4 Wireless Headphones - Excellent - Noise Canceling",
  "improvements": [
    "Added model number",
    "Capitalized properly",
    "Added key feature",
    "Improved condition description"
  ],
  "seo_score": {
    "before": 35,
    "after": 88,
    "improvement": 53
  }
}
```

---

### 9. 🔄 Cross-Lister Agent
**Role**: Multi-Platform Distribution Expert  
**Goal**: Publish listings across multiple marketplaces  
**Backstory**: E-commerce automation specialist with API integration expertise.

#### Capabilities
- Multi-platform posting
- Platform-specific formatting
- Inventory synchronization
- Price adjustment per platform
- Order management
- Performance tracking

#### Supported Platforms
- eBay
- Facebook Marketplace
- Mercari
- Poshmark
- Craigslist
- OfferUp
- Custom platforms via API

#### Outputs
```json
{
  "item_id": "local_123",
  "posted_to": [
    {
      "platform": "ebay",
      "listing_id": "eb_456789",
      "url": "https://ebay.com/itm/456789",
      "status": "active",
      "price": 449.99
    },
    {
      "platform": "mercari",
      "listing_id": "m_123456",
      "url": "https://mercari.com/us/item/123456",
      "status": "active",
      "price": 439.99
    }
  ],
  "sync_enabled": true
}
```

---

### 10. 🎖️ Quality Monitor Agent
**Role**: Compliance and Standards Enforcer  
**Goal**: Ensure all listings meet platform guidelines  
**Backstory**: Quality assurance specialist with deep knowledge of marketplace policies.

#### Capabilities
- Policy compliance checking
- Prohibited item detection
- Image quality validation
- Description completeness check
- Review monitoring
- Performance tracking

#### Compliance Checks
```python
COMPLIANCE_CHECKS = {
    'prohibited_items': [
        'weapons', 'drugs', 'counterfeit',
        'alcohol', 'tobacco', 'adult_content'
    ],
    'required_fields': [
        'title', 'description', 'price',
        'images', 'condition', 'category'
    ],
    'image_requirements': {
        'min_resolution': '600x600',
        'min_count': 1,
        'max_count': 12,
        'formats': ['jpg', 'jpeg', 'png', 'webp']
    }
}
```

#### Outputs
```json
{
  "listing_id": "abc123",
  "compliance_status": "passed",
  "checks_performed": 15,
  "checks_passed": 15,
  "warnings": [],
  "recommendations": [
    "Add more images for better conversion",
    "Consider adding shipping cost details"
  ],
  "approval_status": "approved"
}
```

---

## 🔄 Agent Workflows

### Workflow 1: New Listing Creation
```
Crawler Agent → Validator Agent → Enricher Agent
      ↓                                    ↓
Price Specialist ← Market Research ← Title Enhancer
      ↓                                    ↓
Listing Writer ← Image Processor → Quality Monitor
      ↓                                    ↓
Cross-Lister Agent → Marketplace(s)
```

### Workflow 2: Batch Processing
```
Job Queue → [Parallel Execution]
              ├→ Agent 1 (Items 1-100)
              ├→ Agent 2 (Items 101-200)
              ├→ Agent 3 (Items 201-300)
              └→ Agent N (Items N...)
                    ↓
           Aggregation & Storage
```

### Workflow 3: Scheduled Maintenance
```
Cron Trigger → Quality Monitor → [Check All Listings]
                                        ↓
                                  [Flag Issues]
                                        ↓
                           ┌────────────┴────────────┐
                           ↓                         ↓
                    [Auto-Fix Minor]          [Alert Major]
                           ↓                         ↓
                    [Update Listings]         [Create Tasks]
```

---

## 📊 Monitoring & Observability

### Metrics Tracked
- **Performance**: Execution time, throughput, success rate
- **Quality**: Accuracy, completeness, error rate
- **Cost**: Token usage, API calls, compute time
- **Business**: Revenue impact, listing velocity, conversion rates

### Integration with Observability Tools

#### LangSmith
```python
from langsmith import Client

client = Client(api_key=os.getenv("LANGSMITH_API_KEY"))

@traceable(project_name="arbfinder")
def execute_agent_task(agent_type, input_data):
    # Automatically traces all LLM calls
    agent = get_agent(agent_type)
    result = agent.execute(input_data)
    return result
```

#### LangFuse
```python
from langfuse import Langfuse

langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY")
)

# Track agent performance
langfuse.track(
    name="agent_execution",
    input=input_data,
    output=result,
    metadata={
        "agent_type": "metadata_enricher",
        "duration": 2.5,
        "tokens_used": 450
    }
)
```

### Dashboard Metrics
```
┌────────────────────────────────────────────────────┐
│  Agent Performance Dashboard                       │
├────────────────────────────────────────────────────┤
│  Agent Type       │ Jobs  │ Success │ Avg Time    │
│  Web Crawler      │ 1,250 │  98.4%  │ 3.2s       │
│  Validator        │ 1,250 │  99.8%  │ 0.5s       │
│  Enricher         │ 1,100 │  92.1%  │ 2.8s       │
│  Price Specialist │   980 │  96.7%  │ 1.5s       │
│  Listing Writer   │   950 │  98.9%  │ 4.2s       │
└────────────────────────────────────────────────────┘
```

---

## 🔧 Configuration

### CrewAI Configuration File
```yaml
# crew/crewai.yaml
agents:
  web_crawler:
    role: "Data Extraction Specialist"
    goal: "Extract accurate product data"
    backstory: "Expert web scraper with 10+ years experience"
    tools:
      - crawl4ai
      - beautifulsoup
    max_iterations: 5
    max_rpm: 60
    memory: true
    verbose: true
    
  data_validator:
    role: "Quality Assurance Expert"
    goal: "Ensure data quality"
    backstory: "Meticulous QA engineer"
    tools:
      - pydantic_validator
      - schema_checker
    max_iterations: 3
    max_rpm: 100

tasks:
  crawl_website:
    description: "Crawl {url} and extract product data"
    agent: web_crawler
    expected_output: "List of product dictionaries"
    
  validate_data:
    description: "Validate extracted data"
    agent: data_validator
    expected_output: "Validation report with passed/failed items"
```

### Environment Variables
```bash
# OpenAI/OpenRouter
OPENAI_API_KEY=sk-...
OPENROUTER_API_KEY=sk-or-...

# Observability
LANGSMITH_API_KEY=ls-...
LANGFUSE_PUBLIC_KEY=pk-...
LANGFUSE_SECRET_KEY=sk-...

# Database
DATABASE_URL=postgresql://...

# Agent Configuration
MAX_CONCURRENT_AGENTS=5
AGENT_TIMEOUT_SECONDS=300
ENABLE_AGENT_MEMORY=true
```

---

## 🚀 Usage Examples

### Starting an Agent Job
```python
from backend.api.agents import create_agent_job

job = create_agent_job({
    'agent_type': 'metadata_enricher',
    'input_data': {
        'listing_ids': [123, 456, 789],
        'batch_size': 50
    },
    'priority': 'high'
})

# Job created with ID: job_abc123
```

### Monitoring Job Progress
```python
from backend.api.agents import get_job_status

status = get_job_status('job_abc123')
print(f"Status: {status['status']}")
print(f"Progress: {status['progress']}%")
print(f"ETA: {status['estimated_completion']}")
```

### Retrieving Job Results
```python
from backend.api.agents import get_job_results

results = get_job_results('job_abc123')
print(f"Processed: {results['items_processed']}")
print(f"Success: {results['success_count']}")
print(f"Failed: {results['failed_count']}")
```

---

## 🧪 Testing Agents

### Unit Tests
```python
# tests/test_agents.py
def test_metadata_enricher():
    agent = MetadataEnricherAgent()
    result = agent.enrich({
        'title': 'Sony WH1000XM4 Headphones'
    })
    assert result['brand'] == 'Sony'
    assert result['model'] == 'WH-1000XM4'
    assert result['category'].startswith('Electronics')
```

### Integration Tests
```python
def test_full_workflow():
    # Create crawl job
    crawl_job = create_agent_job({
        'agent_type': 'web_crawler',
        'input_data': {'url': 'https://test.com'}
    })
    
    # Wait for completion
    wait_for_completion(crawl_job['id'])
    
    # Verify results
    results = get_job_results(crawl_job['id'])
    assert results['status'] == 'completed'
    assert results['items_found'] > 0
```

---

## 📚 Best Practices

### 1. Error Handling
- Always implement retry logic
- Log all errors with context
- Gracefully degrade on failures
- Alert on critical errors

### 2. Performance
- Batch operations when possible
- Use async/await for I/O operations
- Implement caching for expensive calls
- Monitor and optimize token usage

### 3. Cost Management
- Use cheaper models for simple tasks
- Implement token limits
- Cache LLM responses
- Monitor spending per agent

### 4. Security
- Validate all inputs
- Sanitize outputs
- Use environment variables for secrets
- Implement rate limiting

### 5. Observability
- Log all agent actions
- Track performance metrics
- Monitor error rates
- Set up alerting

---

## 🔮 Future Enhancements

### Planned Features
- [ ] Multi-language support
- [ ] Voice-based agent control
- [ ] Autonomous learning from feedback
- [ ] Advanced scheduling algorithms
- [ ] Custom agent creation UI
- [ ] Agent marketplace
- [ ] Real-time collaboration between agents
- [ ] Predictive task allocation

### Research Areas
- Reinforcement learning for agent improvement
- Multi-agent negotiation protocols
- Self-healing agent systems
- Federated learning across agents

---

**Last Updated**: 2024-12-15  
**Version**: 1.0.0  
**Maintainer**: AI Team
