# GitHub Copilot Instructions for ArbFinder Suite

This file provides context and guidelines for GitHub Copilot when working on the ArbFinder Suite project.

---

## Project Overview

**ArbFinder Suite** is a price arbitrage discovery platform that:
- Crawls liquidation and surplus websites for product listings
- Analyzes prices using AI and comparable sales data
- Generates optimized product listings
- Distributes listings across multiple marketplaces
- Provides analytics and deal notifications

**Tech Stack**:
- **Backend**: Python 3.9+, FastAPI, SQLAlchemy
- **Frontend**: Next.js 14+, React 18+, TypeScript, Tailwind CSS
- **Platform**: Cloudflare (Workers, Pages, D1, R2, KV)
- **AI**: OpenRouter API, CrewAI, LangChain
- **Database**: Cloudflare D1 (SQLite), PostgreSQL (optional)
- **Tools**: Go (TUI), Docker, pytest, Playwright

---

## Code Style Guidelines

### Python

- Follow **PEP 8** with **100-character line length**
- Use **type hints** for all function signatures
- Use **black** for formatting, **flake8** for linting
- Write **docstrings** for all public functions (Google style)
- Use **async/await** for I/O-bound operations
- Prefer **f-strings** over `.format()` or `%`

```python
async def fetch_comparable_sales(
    query: str,
    limit: int = 150,
    days: int = 90
) -> List[Dict[str, Any]]:
    """Fetch comparable sold listings from eBay.
    
    Args:
        query: Search query string
        limit: Maximum number of results
        days: Lookback period in days
        
    Returns:
        List of comparable sales data
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE}/search", params={...})
        return response.json()
```

### TypeScript/React

- Use **TypeScript** for all frontend code
- Use **functional components** with hooks
- Use **Tailwind CSS** for styling
- Prefer **const** over **let**
- Use **async/await** over promises
- Export types and interfaces

```typescript
interface ListingCardProps {
  listing: Listing;
  onSelect?: (id: string) => void;
}

export const ListingCard: React.FC<ListingCardProps> = ({ listing, onSelect }) => {
  const handleClick = () => {
    onSelect?.(listing.id);
  };

  return (
    <div className="rounded-lg border p-4 hover:shadow-lg transition-shadow">
      <h3 className="font-semibold text-lg">{listing.title}</h3>
      <p className="text-green-600">${listing.price}</p>
    </div>
  );
};
```

---

## Architecture Patterns

### Backend Structure

```
backend/
├── api/              # FastAPI routes
│   ├── main.py       # App initialization
│   ├── agents.py     # Agent endpoints
│   └── crawler.py    # Crawler endpoints
├── openrouter/       # OpenRouter SDK wrapper
│   ├── client.py     # API client
│   ├── models.py     # Model management
│   └── streaming.py  # Streaming support
├── agents/           # CrewAI agent definitions
├── crawler/          # Web crawling logic
├── utils.py          # Database utilities
└── config.py         # Configuration management
```

### API Design

- Use **RESTful** conventions
- Return **JSON** responses
- Use **Pydantic** models for validation
- Include **pagination** for lists
- Use **HTTP status codes** correctly

```python
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from typing import List

class ListingResponse(BaseModel):
    id: str
    title: str
    price: float

@app.get("/api/listings", response_model=List[ListingResponse])
async def get_listings(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    listings = await db.get_listings(limit=limit, offset=offset)
    return listings
```

### Database Patterns

- Use **async SQLAlchemy** for database operations
- Use **Pydantic** models for validation
- Use **migrations** for schema changes
- Add **indexes** for frequently queried columns

```python
from sqlalchemy import Column, Integer, String, Float, Index
from sqlalchemy.ext.asyncio import AsyncSession

class Listing(Base):
    __tablename__ = "listings"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False, index=True)
    price = Column(Float, nullable=False, index=True)
    source = Column(String(50), nullable=False, index=True)
    
    __table_args__ = (
        Index('idx_price_source', 'price', 'source'),
    )
```

---

## AI and Agent Guidelines

### OpenRouter Integration

- **Prefer free models** for simple tasks (llama-2, claude-instant)
- **Use paid models** sparingly for complex tasks (gpt-4, claude-2)
- **Cache LLM responses** to reduce costs
- **Set appropriate temperature**: low (0-0.3) for factual, high (0.7-1.0) for creative
- **Limit tokens** with `max_tokens` parameter

```python
from backend.openrouter import OpenRouterClient

client = OpenRouterClient()

# Simple task - use free model
response = await client.complete(
    prompt="Extract price from: 'iPad Pro - $299.99'",
    model="openrouter/meta-llama/llama-2-70b-chat",
    temperature=0.1,
    max_tokens=50
)

# Complex task - use better model
response = await client.complete(
    prompt="Write compelling product description for...",
    model="openrouter/anthropic/claude-2",
    temperature=0.7,
    max_tokens=500
)
```

### CrewAI Agents

- Each agent should have **one clear responsibility**
- Use **appropriate tools** for each agent
- Configure **LLM models** based on task complexity
- Implement **error handling** and **retries**

```python
from crewai import Agent, Task, Crew

market_researcher = Agent(
    role="Market Researcher",
    goal="Analyze market prices and trends",
    tools=[ebay_search_tool, price_calculator_tool],
    llm="openrouter/anthropic/claude-instant-v1",
    temperature=0.3,
    verbose=True
)

research_task = Task(
    description="Research market prices for iPad Pro 11-inch",
    agent=market_researcher,
    expected_output="Market analysis with average price and confidence"
)
```

---

## Cloudflare Platform

### Workers

- Keep workers **stateless**
- Use **environment bindings** for secrets
- Use **KV** for caching
- Use **D1** for edge data
- Use **R2** for object storage

```typescript
// cloudflare/src/index.ts
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    // Access D1 database
    const listings = await env.DB.prepare(
      'SELECT * FROM listings LIMIT 10'
    ).all();
    
    // Access KV cache
    const cached = await env.CACHE.get('key');
    
    return new Response(JSON.stringify(listings.results));
  }
};
```

### Pages

- Use **Next.js** for frontend
- Enable **edge runtime** where possible
- Use **ISR** for dynamic content
- Connect to **Workers** API

---

## Testing Guidelines

### Unit Tests

- Test **all public functions**
- Use **pytest** for Python tests
- Use **Jest** for TypeScript tests
- Mock **external dependencies**
- Aim for **80%+ coverage**

```python
import pytest
from backend.pricing import calculate_profit_margin

def test_calculate_profit_margin():
    assert calculate_profit_margin(100, 150) == pytest.approx(33.33, 0.01)

def test_calculate_profit_margin_invalid_input():
    with pytest.raises(ValueError):
        calculate_profit_margin(-100, 150)

@pytest.mark.asyncio
async def test_fetch_listings(mock_db):
    listings = await fetch_listings(limit=10)
    assert len(listings) == 10
```

### Integration Tests

- Test **API endpoints** end-to-end
- Test **database operations**
- Test **agent workflows**

```python
@pytest.mark.integration
async def test_crawl_endpoint(test_client):
    response = await test_client.post(
        "/api/crawl",
        json={"source": "shopgoodwill", "query": "iPad"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "listings" in data
```

---

## Common Patterns

### Error Handling

```python
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

async def fetch_data(url: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"HTTP error fetching {url}: {e}")
        raise HTTPException(status_code=502, detail="External service error")
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

### Async Operations

```python
import asyncio
from typing import List

async def fetch_multiple_sources(queries: List[str]) -> List[dict]:
    """Fetch from multiple sources concurrently."""
    tasks = [fetch_from_source(q) for q in queries]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filter out exceptions
    return [r for r in results if not isinstance(r, Exception)]
```

### Caching

```python
from functools import lru_cache
import time

@lru_cache(maxsize=1000)
def expensive_calculation(input: str) -> float:
    """Cache expensive calculations."""
    # Calculation here
    return result

# With TTL using external cache
async def get_comparable_prices(query: str) -> dict:
    # Try cache first
    cached = await kv_store.get(f"comps:{query}")
    if cached:
        return cached
    
    # Fetch if not cached
    data = await fetch_comparables(query)
    
    # Cache for 24 hours
    await kv_store.put(f"comps:{query}", data, ttl=86400)
    return data
```

---

## Security Best Practices

### Never Hardcode Secrets

```python
import os

# ✅ Good - use environment variables
API_KEY = os.getenv("OPENROUTER_API_KEY")

# ❌ Bad - hardcoded secret
API_KEY = "sk_live_abc123xyz"
```

### Validate All Inputs

```python
from pydantic import BaseModel, validator

class ListingCreate(BaseModel):
    title: str
    price: float
    
    @validator('title')
    def title_not_empty(cls, v):
        if not v or len(v) < 10:
            raise ValueError("Title must be at least 10 characters")
        return v
    
    @validator('price')
    def price_positive(cls, v):
        if v <= 0:
            raise ValueError("Price must be positive")
        return v
```

### Use Parameterized Queries

```python
# ✅ Good - parameterized
cursor.execute("SELECT * FROM listings WHERE id = ?", (listing_id,))

# ❌ Bad - SQL injection risk
cursor.execute(f"SELECT * FROM listings WHERE id = {listing_id}")
```

---

## Performance Tips

### Database Optimization

```python
# ✅ Batch inserts
db.bulk_insert_mappings(Listing, listings)

# ❌ Loop inserts (slow)
for listing in listings:
    db.add(Listing(**listing))

# ✅ Use pagination
listings = db.query(Listing).offset(page * size).limit(size).all()

# ✅ Select specific columns
listings = db.query(Listing.id, Listing.title, Listing.price).all()
```

### API Optimization

```python
# ✅ Concurrent requests
async def fetch_all_comps(queries: List[str]):
    tasks = [fetch_comps(q) for q in queries]
    return await asyncio.gather(*tasks)

# ❌ Sequential requests (slow)
def fetch_all_comps(queries: List[str]):
    results = []
    for q in queries:
        results.append(fetch_comps(q))
    return results
```

---

## Documentation

### Docstrings

Use Google-style docstrings for Python:

```python
def calculate_fees(price: float, platform: str) -> float:
    """Calculate marketplace fees for a given price.
    
    Args:
        price: Item price in USD
        platform: Marketplace name ('ebay', 'mercari', etc.)
        
    Returns:
        Total fees as a dollar amount
        
    Raises:
        ValueError: If platform is not supported
        
    Example:
        >>> calculate_fees(100.0, 'ebay')
        12.90
    """
    pass
```

### Code Comments

```python
# Comment WHY, not WHAT
# Use low temperature for deterministic extraction
temperature = 0.1

# Avoid obvious comments
# Set price to 100  # ❌ Obvious
price = 100
```

---

## Project-Specific Context

### Important Modules

- **backend/arb_finder.py**: Main crawler logic
- **backend/api/main.py**: FastAPI app
- **backend/openrouter/**: OpenRouter SDK wrapper (create this)
- **crew/crewai.yaml**: Agent configuration
- **cloudflare/src/index.ts**: Cloudflare Worker

### Key Concepts

- **Listing**: Product from crawled source
- **Comparable**: Sold listing for price comparison
- **Deal**: Listing meeting profit threshold
- **Margin**: Profit percentage after fees
- **Agent**: AI agent performing specific tasks

### External APIs

- **OpenRouter**: LLM access (`openrouter.ai`)
- **eBay Finding API**: Sold listings search
- **Cloudflare API**: Platform management

### Configuration Files

- `.env`: Environment variables (not committed)
- `config.example.json`: Configuration template
- `crew/crewai.yaml`: Agent definitions
- `wrangler.toml`: Cloudflare Workers config

---

## Common Tasks

### Adding a New API Endpoint

```python
# backend/api/main.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/api/deals")
async def get_deals(threshold: float = 20.0):
    """Get deals meeting profit threshold."""
    deals = await db.query(Listing).filter(
        Listing.margin_pct >= threshold
    ).all()
    return deals

app.include_router(router)
```

### Adding a New Agent

```yaml
# crew/crewai.yaml
agents:
  new_agent:
    role: "Agent Role"
    goal: "Agent goal"
    tools: [tool1, tool2]
    llm: "openrouter/anthropic/claude-instant-v1"
    temperature: 0.5
```

### Adding a New Frontend Component

```typescript
// frontend/components/NewComponent.tsx
import React from 'react';

interface Props {
  data: SomeType;
}

export const NewComponent: React.FC<Props> = ({ data }) => {
  return (
    <div className="container">
      {/* Component JSX */}
    </div>
  );
};
```

---

## Questions to Ask

When generating code, consider:

1. **Does this follow the project's code style?**
2. **Are there appropriate error handlers?**
3. **Is this performant for large datasets?**
4. **Are there security implications?**
5. **Does this need tests?**
6. **Is this properly documented?**
7. **Does this respect rate limits?**
8. **Is this cost-effective (for AI operations)?**

---

## Resources

- **Documentation**: See `/docs` directory
- **Examples**: See `docs/EXAMPLES.md`
- **Tasks**: See `TASKS.md` for planned work
- **Features**: See `FEATURES.md` for capabilities
- **Rules**: See `RULES.md` for standards

---

**When in doubt, prioritize:**
1. **Correctness** over speed
2. **Security** over convenience
3. **Maintainability** over cleverness
4. **Cost-efficiency** (especially for AI calls)

---

**End of Copilot Instructions**
