# AI Agents Architecture
# ArbFinder Suite

**Version**: 1.0  
**Date**: 2025-12-15  
**Status**: Active Development

---

## Table of Contents

1. [Overview](#overview)
2. [Agent Framework](#agent-framework)
3. [Agent Catalog](#agent-catalog)
4. [OpenRouter Integration](#openrouter-integration)
5. [LangChain Integration](#langchain-integration)
6. [Observability](#observability)
7. [Deployment](#deployment)

---

## Overview

### Purpose

The ArbFinder Suite uses AI agents to automate complex tasks that would otherwise require manual human effort. Agents handle data enrichment, content generation, quality control, and workflow orchestration.

### Agent Framework Stack

```
┌─────────────────────────────────────────────────────────┐
│                    Application Layer                     │
│  ┌───────────────┐  ┌───────────────┐  ┌─────────────┐│
│  │   Backend     │  │   Frontend    │  │   Workers   ││
│  │     API       │  │      UI       │  │  (Scheduled) ││
│  └───────┬───────┘  └───────────────┘  └──────┬──────┘│
└──────────┼──────────────────────────────────────┼──────┘
           │                                       │
┌──────────┼───────────────────────────────────────┼──────┐
│          │      Agent Orchestration Layer         │     │
│  ┌───────▼──────┐                      ┌─────────▼────┐│
│  │   CrewAI     │◄─────────────────────┤  LangChain   ││
│  │  Framework   │                      │   Chains     ││
│  └───────┬──────┘                      └──────┬───────┘│
└──────────┼─────────────────────────────────────┼───────┘
           │                                      │
┌──────────┼──────────────────────────────────────┼───────┐
│          │         LLM Access Layer              │      │
│  ┌───────▼──────────────────────────────────────▼────┐ │
│  │              OpenRouter API                        │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐        │ │
│  │  │  GPT-4   │  │  Claude  │  │  Gemini  │  ...   │ │
│  │  └──────────┘  └──────────┘  └──────────┘        │ │
│  └───────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────┘
           │
┌──────────▼────────────────────────────────────────────┐
│              Observability Layer                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │LangFuse  │  │LangSmith │  │ Custom   │           │
│  │ Tracing  │  │ Monitor  │  │  Logs    │           │
│  └──────────┘  └──────────┘  └──────────┘           │
└────────────────────────────────────────────────────────┘
```

### Key Technologies

- **CrewAI**: Agent orchestration and workflow management
- **OpenRouter**: Multi-provider LLM access with unified API
- **LangChain**: Agent chains and prompt management
- **LangFuse**: Observability and tracing
- **LangSmith**: Monitoring and debugging
- **Crawl4AI**: AI-powered web crawling

---

## Agent Framework

### CrewAI Configuration

CrewAI manages our agents and their interactions. Configuration is defined in `crew/crewai.yaml`.

**Core Concepts**:

1. **Agents**: Individual AI workers with specific roles
2. **Tasks**: Work items assigned to agents
3. **Processes**: Workflows combining multiple agents
4. **Tools**: Functions agents can use to accomplish tasks
5. **Workers**: Background processes running agents on schedule

### Agent Lifecycle

```
┌──────────────┐
│  Initialize  │ ← Load configuration, connect to LLM
└──────┬───────┘
       │
┌──────▼───────┐
│   Assign     │ ← Receive task with input data
│    Task      │
└──────┬───────┘
       │
┌──────▼───────┐
│   Execute    │ ← Use tools, call LLM, process data
│    Task      │
└──────┬───────┘
       │
┌──────▼───────┐
│   Return     │ ← Return output, log metrics
│   Result     │
└──────┬───────┘
       │
┌──────▼───────┐
│  Finalize    │ ← Cleanup, persist state
└──────────────┘
```

### Agent Communication

Agents communicate through:
1. **Task Queues**: Async task assignment via database queue
2. **Shared Context**: Access to shared data store (D1)
3. **Event Bus**: Real-time events for coordination
4. **API Endpoints**: HTTP endpoints for external triggers

---

## Agent Catalog

### Data Ingestion Agents

#### 1. Web Crawler Agent

**Role**: Web Crawler Agent  
**Goal**: Crawl target websites and extract price data, images, and metadata efficiently  
**Tools**: Crawl4AI, HTML Parser, Price Extractor  
**Model**: Free models via OpenRouter (e.g., `meta-llama/llama-3.1-8b-instruct`)

**Responsibilities**:
- Execute scheduled crawls of configured marketplaces
- Extract structured data from HTML
- Handle pagination and infinite scroll
- Respect robots.txt and rate limits
- Store raw data for validation

**Input**:
```python
{
  "target_urls": ["https://shopgoodwill.com/search?query=laptop"],
  "extraction_schema": {
    "title": "string",
    "price": "number",
    "image_url": "string",
    "condition": "string"
  },
  "max_pages": 10
}
```

**Output**:
```python
{
  "items": [
    {
      "title": "Dell Latitude Laptop",
      "price": 150.00,
      "image_url": "https://...",
      "condition": "Used",
      "source_url": "https://...",
      "crawled_at": "2025-12-15T10:30:00Z"
    }
  ],
  "stats": {
    "pages_crawled": 5,
    "items_found": 47,
    "errors": 0
  }
}
```

**Triggers**:
- Scheduled: Every 4 hours (configurable)
- Manual: User-initiated search
- Event: New watch request created

**Configuration**:
```yaml
crawler_agent:
  model: "meta-llama/llama-3.1-8b-instruct:free"
  temperature: 0.1  # Low for deterministic extraction
  max_tokens: 2000
  timeout: 120  # seconds
  retry_attempts: 3
```

---

#### 2. Data Validator Agent

**Role**: Data Validation Agent  
**Goal**: Validate and clean incoming data ensuring quality and consistency  
**Tools**: Schema Validator, Data Cleaner, Duplicate Checker  
**Model**: Free models via OpenRouter

**Responsibilities**:
- Validate data against schema
- Detect and remove duplicates
- Normalize formats (prices, dates, etc.)
- Flag anomalies for review
- Enrich with data quality scores

**Input**: Raw crawled data

**Output**: Validated, cleaned data with quality scores

**Triggers**:
- After crawler completes
- Scheduled: Every 20 minutes for queued items

---

### Market Research Agents

#### 3. Market Researcher Agent

**Role**: Market Researcher  
**Goal**: Collect comparable prices and analyze market trends  
**Tools**: Web Search, Provider Scan, Price Aggregator  
**Model**: GPT-4 or Claude (via OpenRouter)

**Responsibilities**:
- Search for comparable sold items
- Aggregate pricing data
- Identify price trends
- Calculate market velocity
- Assess demand levels

**Input**:
```python
{
  "product": {
    "title": "Apple MacBook Pro 16\" M1",
    "category": "electronics/computers",
    "condition": "good"
  },
  "lookback_days": 90,
  "min_comparables": 10
}
```

**Output**:
```python
{
  "comparables": [
    {
      "sold_price": 1250.00,
      "sold_date": "2025-12-10",
      "platform": "ebay",
      "condition": "good"
    }
  ],
  "analysis": {
    "avg_price": 1275.00,
    "median_price": 1250.00,
    "std_dev": 125.50,
    "trend": "stable",
    "confidence": 0.92
  }
}
```

---

#### 4. Price Specialist Agent

**Role**: Price Specialist  
**Goal**: Compute optimal pricing based on comps and fees  
**Tools**: Fee Calculator, Statistics Engine  
**Model**: GPT-4 (reasoning tasks)

**Responsibilities**:
- Calculate recommended list price
- Determine minimum acceptable price
- Factor in platform fees
- Account for condition adjustments
- Provide ROI estimates

**Input**: Market research data + target platform

**Output**: Pricing recommendations with justification

---

### Content Creation Agents

#### 5. Listing Writer Agent

**Role**: Listing Specialist  
**Goal**: Draft SEO-optimized titles and descriptions  
**Tools**: Template Library, SEO Optimizer, Content Generator  
**Model**: GPT-4 or Claude (creative tasks)

**Responsibilities**:
- Generate compelling titles
- Write detailed descriptions
- Add condition notes
- Include shipping details
- Optimize for platform search

**Input**:
```python
{
  "product": {
    "title": "Dell Latitude 5420",
    "category": "laptops",
    "specs": {...},
    "condition": "good",
    "defects": ["minor scratches on lid"]
  },
  "target_platform": "ebay",
  "style": "professional"
}
```

**Output**:
```python
{
  "title": "Dell Latitude 5420 14\" Laptop i5 16GB RAM 256GB SSD Win11 Pro - Good",
  "description": "...",
  "bullets": [
    "Intel Core i5 11th Gen Processor",
    "16GB DDR4 RAM, 256GB NVMe SSD",
    "..."
  ],
  "seo_keywords": ["dell laptop", "latitude 5420", "business laptop"]
}
```

**Triggers**:
- User creates new listing
- Batch processing command

---

#### 6. Image Processor Agent

**Role**: Image Processing Agent  
**Goal**: Process, optimize, and store images with metadata  
**Tools**: Image Optimizer, Bucket Uploader, Thumbnail Generator  
**Model**: Vision models via OpenRouter (for image analysis)

**Responsibilities**:
- Download images from source URLs
- Optimize for web (compress, resize)
- Generate thumbnails (multiple sizes)
- Upload to R2 storage
- Extract visual features (color, quality)
- Generate alt text for accessibility

**Input**: Image URLs or file uploads

**Output**: Processed image URLs, metadata, alt text

**Triggers**:
- New listings with images
- Scheduled: Every 10 minutes for queue

---

### Metadata Enrichment Agents

#### 7. Metadata Enricher Agent

**Role**: Metadata Enrichment Agent  
**Goal**: Fill missing metadata using AI  
**Tools**: OpenRouter API, Metadata Database, Category Classifier  
**Model**: GPT-4 or free alternatives

**Responsibilities**:
- Identify product category
- Extract brand and model
- Determine specifications
- Add relevant tags
- Fill missing fields

**Input**: Raw product data with missing fields

**Output**: Complete product metadata with confidence scores

**Triggers**:
- Scheduled: Every 15 minutes
- Manual: Bulk enrichment command

---

#### 8. Title Enhancer Agent

**Role**: Title Enhancement Agent  
**Goal**: Improve and standardize product titles  
**Tools**: NLP Processor, Title Templates, Brand Database  
**Model**: GPT-4 or Claude

**Responsibilities**:
- Standardize title format
- Add missing keywords
- Fix spelling/grammar
- Ensure brand/model accuracy
- Optimize for search

---

### Distribution Agents

#### 9. Cross-listing Agent

**Role**: Cross-listing Operator  
**Goal**: Prepare listings for multiple platforms  
**Tools**: CSV Exporter, Platform APIs, Batch Processor  
**Model**: GPT-4 (for platform-specific adaptations)

**Responsibilities**:
- Generate platform-specific formats
- Adapt content for each platform
- Handle character limits
- Map categories correctly
- Export in required formats

---

### Quality Control Agents

#### 10. Quality Monitor Agent

**Role**: Quality Monitor  
**Goal**: Monitor data quality and detect anomalies  
**Tools**: Anomaly Detector, Quality Metrics, Alert System  
**Model**: GPT-4 (anomaly detection)

**Responsibilities**:
- Score data quality
- Detect anomalies
- Flag suspicious data
- Generate quality reports
- Trigger alerts

---

## OpenRouter Integration

### Why OpenRouter?

OpenRouter provides:
1. **Unified API**: Single API for multiple LLM providers
2. **Free Models**: Access to free open-source models
3. **Fallback Handling**: Automatic fallback to alternative models
4. **Cost Optimization**: Route to cheapest suitable model
5. **Monitoring**: Built-in usage tracking

### Configuration

**Environment Variables**:
```bash
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_APP_NAME=ArbFinder-Suite
OPENROUTER_APP_URL=https://arbfinder.com
```

**Client Initialization**:
```python
from backend.integrations.openrouter import OpenRouterClient

client = OpenRouterClient(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    app_name="ArbFinder-Suite"
)
```

### Free Models

**Recommended Free Models**:
- `meta-llama/llama-3.1-8b-instruct:free` - General purpose
- `mistralai/mistral-7b-instruct:free` - Fast, efficient
- `google/gemma-2-9b-it:free` - Google's open model
- `qwen/qwen-2-7b-instruct:free` - Multilingual

**Fetching Available Models**:
```python
from scripts.openrouter import list_free_models

# Get list of free models
free_models = list_free_models.fetch()

# Filter by capability
reasoning_models = [m for m in free_models if m['capabilities']['reasoning'] > 0.8]
```

### Model Selection Strategy

```python
def select_model(task_type: str, priority: str = "cost") -> str:
    """
    Select appropriate model based on task type and priority.
    
    Args:
        task_type: Type of task (extraction, generation, reasoning, etc.)
        priority: Selection priority (cost, speed, quality)
    
    Returns:
        Model identifier
    """
    model_map = {
        "extraction": {
            "cost": "meta-llama/llama-3.1-8b-instruct:free",
            "speed": "mistralai/mistral-7b-instruct:free",
            "quality": "openai/gpt-4-turbo"
        },
        "generation": {
            "cost": "meta-llama/llama-3.1-8b-instruct:free",
            "speed": "meta-llama/llama-3.1-8b-instruct:free",
            "quality": "anthropic/claude-3.5-sonnet"
        },
        "reasoning": {
            "cost": "qwen/qwen-2-7b-instruct:free",
            "speed": "mistralai/mistral-7b-instruct:free",
            "quality": "openai/gpt-4"
        }
    }
    
    return model_map.get(task_type, {}).get(priority, "meta-llama/llama-3.1-8b-instruct:free")
```

### Streaming Responses

```python
async def stream_completion(prompt: str, model: str):
    """Stream responses for real-time UI updates."""
    async for chunk in client.stream(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=True
    ):
        yield chunk.choices[0].delta.content
```

### Code Completion

```python
def complete_code(code_context: str, cursor_position: int) -> str:
    """Get code completion suggestions."""
    response = client.complete(
        model="openai/gpt-4-turbo",
        prompt=code_context,
        max_tokens=100,
        temperature=0.2,  # Low for deterministic completion
        stop=["\n\n", "def ", "class "]
    )
    return response.choices[0].text
```

---

## LangChain Integration

### LangChain Components

1. **Chains**: Sequential agent operations
2. **Memory**: Conversation history and context
3. **Tools**: External functions agents can call
4. **Agents**: Decision-making entities
5. **Prompts**: Template management

### Example Chain

```python
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from backend.integrations.openrouter import get_langchain_llm

# Create LLM instance
llm = get_langchain_llm(model="meta-llama/llama-3.1-8b-instruct:free")

# Define prompt template
template = """
Extract product information from the following text:

Text: {text}

Extract:
- Brand
- Model
- Condition
- Price

Return as JSON.
"""

prompt = PromptTemplate(template=template, input_variables=["text"])

# Create chain
chain = LLMChain(llm=llm, prompt=prompt)

# Execute
result = chain.run(text="Dell Latitude 5420 laptop in good condition for $500")
```

### LangGraph Workflow

```python
from langgraph.graph import StateGraph
from langchain.schema import HumanMessage

# Define workflow states
class WorkflowState:
    product_data: dict
    enriched_data: dict
    pricing_data: dict
    listing_content: dict

# Create graph
workflow = StateGraph(WorkflowState)

# Add nodes
workflow.add_node("extract", extract_metadata_agent)
workflow.add_node("price", calculate_pricing_agent)
workflow.add_node("generate", generate_listing_agent)

# Add edges
workflow.add_edge("extract", "price")
workflow.add_edge("price", "generate")

# Compile
app = workflow.compile()

# Execute
result = app.invoke({"product_data": raw_data})
```

---

## Observability

### LangFuse Integration

**Tracing Agent Execution**:

```python
from langfuse import Langfuse

langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY")
)

# Trace agent execution
@langfuse.observe()
def enrich_metadata(product_data: dict) -> dict:
    """Enrich product metadata with AI."""
    trace = langfuse.trace(
        name="metadata_enrichment",
        metadata={"product_id": product_data.get("id")}
    )
    
    with trace.span(name="llm_call") as span:
        result = agent.run(product_data)
        span.end(output=result)
    
    return result
```

**View Traces**: https://cloud.langfuse.com/

### LangSmith Integration

**Monitoring Agent Performance**:

```python
from langsmith import Client

client = Client(api_key=os.getenv("LANGSMITH_API_KEY"))

# Log run
client.create_run(
    name="Metadata Enrichment",
    run_type="chain",
    inputs={"product": product_data},
    outputs={"enriched": enriched_data},
    project_name="arbfinder-agents"
)
```

### Custom Metrics

**Track Agent Performance**:

```python
from backend.integrations.observability import AgentMetrics

metrics = AgentMetrics()

@metrics.track_execution
async def execute_agent(agent_name: str, input_data: dict):
    start_time = time.time()
    
    try:
        result = await agent.run(input_data)
        
        metrics.record(
            agent=agent_name,
            duration=time.time() - start_time,
            status="success",
            tokens_used=result.get("tokens", 0),
            cost=result.get("cost", 0.0)
        )
        
        return result
    except Exception as e:
        metrics.record(
            agent=agent_name,
            duration=time.time() - start_time,
            status="error",
            error=str(e)
        )
        raise
```

---

## Deployment

### Local Development

```bash
# Install dependencies
pip install -e ".[dev]"

# Set environment variables
export OPENROUTER_API_KEY=your-key
export LANGFUSE_PUBLIC_KEY=your-key
export LANGFUSE_SECRET_KEY=your-key

# Run agent locally
python -m backend.api.agents run metadata_enricher \
    --input '{"title": "Dell Laptop"}'
```

### Cloudflare Workers

**Deploy Agent Worker**:

```bash
# Build and deploy
cd cloudflare
npm run deploy

# The worker will trigger agents via Cron:
# - Every 15 min: Metadata enrichment
# - Every 10 min: Image processing
# - Every 4 hours: Scheduled crawls
```

**Worker Configuration** (`wrangler.toml`):

```toml
[triggers]
crons = [
  "*/15 * * * *",  # Metadata worker
  "*/10 * * * *",  # Image worker
  "0 */4 * * *"    # Crawler worker
]

[vars]
OPENROUTER_API_KEY = ""  # Set via secrets

[[d1_databases]]
binding = "DB"
database_name = "arbfinder"
database_id = "..."

[[r2_buckets]]
binding = "IMAGES"
bucket_name = "arbfinder-images"
```

### Monitoring

**Health Checks**:
```bash
# Check agent status
curl https://api.arbfinder.com/agents/health

# View agent metrics
curl https://api.arbfinder.com/agents/metrics
```

**Logs**:
```bash
# Tail worker logs
wrangler tail

# View specific agent logs
wrangler tail --filter agent=metadata_enricher
```

---

## Best Practices

### 1. Prompt Engineering

- Use specific, clear instructions
- Include examples in prompts
- Request structured output (JSON)
- Set appropriate temperature
- Limit max tokens for cost control

### 2. Error Handling

- Implement retry logic with exponential backoff
- Fallback to simpler models on errors
- Log all failures with context
- Alert on sustained failures

### 3. Cost Management

- Use free models for routine tasks
- Reserve premium models for complex tasks
- Cache results when possible
- Monitor token usage closely

### 4. Performance

- Batch process items when possible
- Use async operations
- Implement timeouts
- Cache frequently accessed data

### 5. Quality Assurance

- Validate agent outputs
- Track confidence scores
- Human review for low-confidence results
- A/B test prompt variations

---

## Future Enhancements

1. **Multi-Agent Collaboration**: Agents that work together on complex tasks
2. **Learning from Feedback**: Improve prompts based on user corrections
3. **Custom Fine-tuned Models**: Train models on domain-specific data
4. **Voice Interface**: Voice-activated agent interactions
5. **Autonomous Workflows**: Fully automated end-to-end processes

---

**Last Updated**: 2025-12-15  
**Maintained By**: AI Team  
**Related Docs**: [SRS](SRS.md), [OpenRouter Integration](OPENROUTER_INTEGRATION.md), [Observability](OBSERVABILITY.md)
