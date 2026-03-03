# 🤖 GitHub Copilot Instructions for ArbFinder Suite

## Overview
This document provides specific instructions and context for GitHub Copilot to generate better code suggestions for the ArbFinder Suite project.

---

## Project Context

### What is ArbFinder Suite?
ArbFinder Suite is a comprehensive price arbitrage detection platform that:
- Crawls e-commerce websites to find deals
- Uses AI agents to enrich and optimize listings
- Provides price analysis and profit calculations
- Enables multi-platform listing management
- Deployed on Cloudflare infrastructure

### Technology Stack
- **Backend**: Python 3.9+, FastAPI, PostgreSQL, CrewAI
- **Frontend**: Next.js 14, React 18, TypeScript, Tailwind CSS
- **Edge**: Cloudflare Workers, Pages, R2, D1, KV
- **AI**: OpenAI, OpenRouter, LangChain ecosystem
- **Storage**: PostgreSQL, MinIO, Redis
- **DevOps**: Docker, GitHub Actions, Pulumi

---

## Code Generation Guidelines

### Python Code

#### Imports Organization
```python
# Standard library imports
import os
import sys
from datetime import datetime
from typing import List, Dict, Optional

# Third-party imports
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Local imports
from backend.config import settings
from backend.utils import format_price
```

#### Type Hints
Always include type hints for function parameters and return values:
```python
def fetch_listings(
    source: str,
    limit: int = 100,
    offset: int = 0
) -> List[Dict[str, any]]:
    """Fetch listings from a specified source."""
    pass
```

#### Error Handling
Use proper exception handling with specific exception types:
```python
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
except requests.Timeout:
    logger.error(f"Timeout fetching {url}")
    raise HTTPException(status_code=504, detail="Request timeout")
except requests.HTTPError as e:
    logger.error(f"HTTP error: {e}")
    raise HTTPException(status_code=e.response.status_code)
```

#### Logging
Use structured logging with context:
```python
logger.info(
    "Listing created",
    extra={
        "listing_id": listing.id,
        "source": listing.source,
        "price": listing.price
    }
)
```

### TypeScript/React Code

#### Component Structure
```typescript
import { FC, useState, useEffect } from 'react';

interface ListingCardProps {
  listing: Listing;
  onSelect?: (listing: Listing) => void;
}

export const ListingCard: FC<ListingCardProps> = ({ 
  listing, 
  onSelect 
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  
  return (
    <div className="listing-card">
      {/* Component content */}
    </div>
  );
};
```

#### API Calls
```typescript
async function fetchListings(params: SearchParams): Promise<Listing[]> {
  try {
    const response = await fetch(`${API_BASE}/api/listings`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Failed to fetch listings:', error);
    throw error;
  }
}
```

### SQL Queries

#### Query Style
```sql
-- SELECT queries
SELECT 
    l.id,
    l.title,
    l.price,
    l.source
FROM listings l
INNER JOIN comps c ON c.key_title = l.title
WHERE l.price < (c.avg_price * 0.8)
    AND l.created_at > NOW() - INTERVAL '7 days'
ORDER BY l.price ASC
LIMIT 100;

-- INSERT queries
INSERT INTO listings (
    source,
    url,
    title,
    price,
    currency,
    created_at
) VALUES (
    'shopgoodwill',
    'https://...',
    'iPhone 12',
    599.99,
    'USD',
    NOW()
);
```

---

## Project-Specific Patterns

### Database Queries
When working with database queries, always:
- Use parameterized queries to prevent SQL injection
- Include proper error handling
- Add appropriate indexes
- Use transactions for related operations

```python
async def create_listing(listing_data: Dict) -> int:
    """Create a new listing in the database."""
    query = """
        INSERT INTO listings (source, url, title, price, currency)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id
    """
    try:
        result = await conn.fetchval(
            query,
            listing_data['source'],
            listing_data['url'],
            listing_data['title'],
            listing_data['price'],
            listing_data['currency']
        )
        return result
    except Exception as e:
        logger.error(f"Failed to create listing: {e}")
        raise
```

### API Endpoints
FastAPI endpoint pattern:
```python
@router.get("/listings", response_model=ListingResponse)
async def get_listings(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    source: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
) -> ListingResponse:
    """Get paginated list of listings."""
    query = select(Listing).limit(limit).offset(offset)
    
    if source:
        query = query.where(Listing.source == source)
    
    result = await db.execute(query)
    listings = result.scalars().all()
    
    return ListingResponse(
        success=True,
        data=listings,
        total=len(listings)
    )
```

### AI Agent Tasks
When creating agent tasks, follow this pattern:
```python
async def create_agent_job(
    agent_type: str,
    input_data: Dict,
    priority: str = "normal"
) -> AgentJob:
    """Create a new agent job."""
    job = AgentJob(
        agent_type=agent_type,
        status="queued",
        input=input_data,
        priority=priority,
        created_at=datetime.now()
    )
    
    await db.add(job)
    await db.commit()
    
    # Trigger agent execution asynchronously
    background_tasks.add_task(execute_agent, job.id)
    
    return job
```

### Cloudflare Workers
Worker pattern:
```typescript
export default {
  async fetch(
    request: Request,
    env: Env,
    ctx: ExecutionContext
  ): Promise<Response> {
    const url = new URL(request.url);
    
    try {
      // Route handling
      if (url.pathname === '/api/health') {
        return new Response(
          JSON.stringify({ status: 'ok' }),
          { headers: { 'Content-Type': 'application/json' } }
        );
      }
      
      return new Response('Not Found', { status: 404 });
    } catch (error) {
      return new Response(
        JSON.stringify({ error: error.message }),
        { status: 500 }
      );
    }
  },
};
```

---

## Common Patterns

### Configuration Management
```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Application settings."""
    database_url: str
    api_key: str
    environment: str = "development"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

### Price Normalization
```python
def normalize_price(price_str: str) -> float:
    """Normalize price string to float."""
    # Remove currency symbols
    price = re.sub(r'[$£€¥]', '', price_str)
    # Handle European format (comma as decimal)
    price = price.replace(',', '.')
    # Remove thousands separators
    price = re.sub(r'\.(?=\d{3})', '', price)
    return float(price)
```

### Error Response Format
```python
class ErrorResponse(BaseModel):
    """Standard error response format."""
    success: bool = False
    error: Dict[str, any]
    data: None = None

def create_error_response(
    code: str,
    message: str,
    details: Optional[Dict] = None
) -> ErrorResponse:
    """Create standardized error response."""
    return ErrorResponse(
        error={
            "code": code,
            "message": message,
            "details": details or {}
        }
    )
```

### Caching Pattern
```python
from functools import lru_cache
from datetime import datetime, timedelta

# In-memory cache
_cache = {}
_cache_timestamps = {}

def get_cached(key: str, ttl_seconds: int = 300) -> Optional[any]:
    """Get cached value if not expired."""
    if key in _cache:
        timestamp = _cache_timestamps.get(key)
        if timestamp and (datetime.now() - timestamp).seconds < ttl_seconds:
            return _cache[key]
    return None

def set_cached(key: str, value: any) -> None:
    """Set cached value with timestamp."""
    _cache[key] = value
    _cache_timestamps[key] = datetime.now()
```

---

## Testing Patterns

### Unit Test
```python
import pytest
from backend.utils import normalize_price

def test_normalize_price_usd():
    """Test USD price normalization."""
    assert normalize_price("$1,234.56") == 1234.56

def test_normalize_price_eur():
    """Test EUR price normalization."""
    assert normalize_price("€1.234,56") == 1234.56

@pytest.mark.asyncio
async def test_create_listing():
    """Test listing creation."""
    listing_data = {
        "source": "test",
        "title": "Test Item",
        "price": 99.99
    }
    result = await create_listing(listing_data)
    assert result > 0
```

### Integration Test
```python
from fastapi.testclient import TestClient

def test_get_listings_endpoint(client: TestClient):
    """Test listings endpoint."""
    response = client.get("/api/listings?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) <= 10
```

---

## Naming Conventions

### Python
- **Functions**: `lowercase_with_underscores`
- **Classes**: `PascalCase`
- **Constants**: `UPPERCASE_WITH_UNDERSCORES`
- **Private**: `_leading_underscore`
- **Modules**: `lowercase_with_underscores.py`

### TypeScript
- **Functions**: `camelCase`
- **Classes**: `PascalCase`
- **Interfaces**: `PascalCase` (prefix with 'I' optional)
- **Components**: `PascalCase`
- **Files**: `camelCase.ts` or `PascalCase.tsx` for components

### Database
- **Tables**: `lowercase_plural` (e.g., `listings`, `agent_jobs`)
- **Columns**: `lowercase_with_underscores`
- **Indexes**: `idx_table_column`
- **Foreign Keys**: `fk_table_column`

---

## Security Patterns

### Input Validation
```python
from pydantic import BaseModel, validator, Field

class ListingCreate(BaseModel):
    source: str = Field(..., min_length=1, max_length=100)
    title: str = Field(..., min_length=3, max_length=500)
    price: float = Field(..., gt=0, lt=1000000)
    
    @validator('source')
    def validate_source(cls, v):
        allowed_sources = ['shopgoodwill', 'govdeals', 'governmentsurplus']
        if v not in allowed_sources:
            raise ValueError(f'Invalid source: {v}')
        return v
```

### API Authentication
```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    """Verify API key."""
    if api_key != settings.api_key:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key"
        )
    return api_key
```

---

## Performance Patterns

### Async Operations
```python
import asyncio

async def fetch_multiple_sources(sources: List[str]) -> List[Dict]:
    """Fetch from multiple sources concurrently."""
    tasks = [fetch_source(source) for source in sources]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return [r for r in results if not isinstance(r, Exception)]
```

### Database Query Optimization
```python
# Use SELECT only needed columns
query = select(Listing.id, Listing.title, Listing.price)

# Use joins instead of multiple queries
query = (
    select(Listing, Comp)
    .join(Comp, Listing.title == Comp.key_title)
)

# Use indexes for WHERE clauses
# CREATE INDEX idx_listings_created_at ON listings(created_at);
query = query.where(Listing.created_at > cutoff_date)
```

---

## Documentation Patterns

### Function Docstrings
```python
def calculate_profit(
    buy_price: float,
    sell_price: float,
    fees_pct: float = 0.13
) -> float:
    """Calculate profit after fees.
    
    Args:
        buy_price: Purchase price of item
        sell_price: Selling price of item
        fees_pct: Platform fees as percentage (default: 0.13 = 13%)
        
    Returns:
        Net profit after fees
        
    Example:
        >>> calculate_profit(100, 150, 0.13)
        30.50
    """
    fees = sell_price * fees_pct
    return sell_price - buy_price - fees
```

### Component Documentation
```typescript
/**
 * ListingCard component displays a single listing with image, title, and price.
 * 
 * @param {Listing} listing - The listing data to display
 * @param {Function} onSelect - Callback when listing is selected
 * 
 * @example
 * <ListingCard 
 *   listing={listing}
 *   onSelect={(listing) => console.log(listing)}
 * />
 */
```

---

## Context-Specific Hints

When generating code for:

### **Crawler**: 
- Always implement rate limiting
- Handle connection errors gracefully
- Respect robots.txt
- Use retry logic with exponential backoff

### **AI Agents**:
- Track token usage
- Implement timeouts
- Log all inputs and outputs
- Handle API errors

### **API Endpoints**:
- Validate all inputs
- Use appropriate HTTP status codes
- Implement pagination for lists
- Add OpenAPI documentation

### **Database Operations**:
- Use transactions for related operations
- Handle unique constraint violations
- Implement soft deletes
- Add proper indexes

### **Frontend Components**:
- Make components responsive
- Handle loading states
- Show error messages
- Add loading skeletons

---

## Example Completions

### Generate API Endpoint
**Prompt**: Create an API endpoint to search listings

**Expected Generation**:
```python
@router.get("/listings/search", response_model=SearchResponse)
async def search_listings(
    q: str = Query(..., min_length=3),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
) -> SearchResponse:
    """Search listings by title or description."""
    search_term = f"%{q}%"
    query = (
        select(Listing)
        .where(
            or_(
                Listing.title.ilike(search_term),
                Listing.description.ilike(search_term)
            )
        )
        .limit(limit)
    )
    
    result = await db.execute(query)
    listings = result.scalars().all()
    
    return SearchResponse(
        success=True,
        data=listings,
        total=len(listings)
    )
```

---

**Last Updated**: 2024-12-15  
**For**: GitHub Copilot AI Assistant  
**Project**: ArbFinder Suite

**Note**: These instructions help Copilot generate code that follows project conventions and best practices.
