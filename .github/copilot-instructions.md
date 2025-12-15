# GitHub Copilot Instructions for ArbFinder Suite

These instructions guide GitHub Copilot to provide context-aware suggestions specific to the ArbFinder Suite project.

---

## Project Context

ArbFinder Suite is a comprehensive price arbitrage discovery and listing management platform. The system:
- Crawls multiple marketplace websites for product listings
- Analyzes prices and identifies arbitrage opportunities
- Uses AI agents (CrewAI + OpenRouter) for automation
- Deployed on Cloudflare (Workers, Pages, D1, R2)
- Built with Python (FastAPI), TypeScript (Next.js), and Go (TUI)

---

## Code Style Guidelines

### Python
- Use type hints for all function signatures
- Follow PEP 8, format with Black (line length: 100)
- Use descriptive variable names (snake_case)
- Add docstrings to all public functions
- Prefer async/await for I/O operations

```python
async def fetch_listings(
    source: str,
    query: str,
    limit: int = 100
) -> List[Listing]:
    """Fetch listings from a marketplace source.
    
    Args:
        source: Marketplace source (e.g., 'ebay', 'mercari')
        query: Search query string
        limit: Maximum number of results
        
    Returns:
        List of Listing objects
        
    Raises:
        ValueError: If source is unsupported
        NetworkError: If request fails
    """
    pass
```

### TypeScript/JavaScript
- Use TypeScript for all new code
- Prefer functional components with hooks
- Use async/await over promises
- Type all function parameters and returns
- Use const for variables, avoid var

```typescript
interface ListingProps {
  listing: Listing;
  onSelect: (id: string) => void;
}

const ListingCard: React.FC<ListingProps> = ({ listing, onSelect }) => {
  const handleClick = useCallback(() => {
    onSelect(listing.id);
  }, [listing.id, onSelect]);
  
  return (
    <div onClick={handleClick}>
      {listing.title}
    </div>
  );
};
```

### Go
- Follow standard Go conventions
- Handle all errors explicitly
- Use descriptive variable names
- Keep functions focused and small
- Document exported functions

```go
// FetchListings retrieves listings from the database
func FetchListings(db *sql.DB, query string, limit int) ([]Listing, error) {
    rows, err := db.Query(
        "SELECT id, title, price FROM listings WHERE title LIKE ? LIMIT ?",
        "%"+query+"%",
        limit,
    )
    if err != nil {
        return nil, fmt.Errorf("query failed: %w", err)
    }
    defer rows.Close()
    
    // Parse results...
}
```

---

## Project Structure

```
arbfinder-suite/
├── backend/            # Python FastAPI backend
│   ├── api/           # API endpoints
│   ├── agents/        # AI agent definitions
│   ├── crawler/       # Web scraping logic
│   └── lib/           # Shared libraries
├── frontend/          # Next.js frontend
│   ├── app/           # App router pages
│   ├── components/    # React components
│   └── lib/           # Client utilities
├── cloudflare/        # Cloudflare Workers
│   └── src/           # Worker source code
├── tui/               # Go terminal UI
├── scripts/           # Automation scripts
│   └── cloudflare/    # Cloudflare setup scripts
└── tests/             # Test suite
```

---

## Common Patterns

### Database Queries

```python
# Use parameterized queries to prevent SQL injection
def get_listings(query: str) -> List[Listing]:
    cursor.execute(
        "SELECT * FROM listings WHERE title LIKE ?",
        (f"%{query}%",)
    )
    return [Listing(**row) for row in cursor.fetchall()]
```

### API Endpoints

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class ListingCreate(BaseModel):
    title: str
    price: float
    condition: str

@router.post("/listings", response_model=Listing)
async def create_listing(listing: ListingCreate):
    """Create a new listing"""
    try:
        result = await db.insert_listing(listing)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### Agent Tasks

```python
from arbfinder.agents import BaseAgent

class MetadataEnricherAgent(BaseAgent):
    """Enriches product metadata using AI"""
    
    async def execute(self, listing: Listing) -> Listing:
        """Fill in missing metadata for a listing"""
        prompt = self.build_prompt(listing)
        response = await self.llm.generate(prompt)
        metadata = self.parse_response(response)
        listing.metadata.update(metadata)
        return listing
```

### React Components

```typescript
'use client';

import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';

export function ListingList() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['listings'],
    queryFn: () => fetch('/api/listings').then(r => r.json())
  });
  
  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {data.map(listing => (
        <ListingCard key={listing.id} listing={listing} />
      ))}
    </div>
  );
}
```

---

## API Integration

### OpenRouter (AI Models)

```python
from arbfinder.lib.openrouter import OpenRouterClient

client = OpenRouterClient(api_key=os.getenv("OPENROUTER_API_KEY"))

response = await client.chat(
    model="anthropic/claude-3-haiku",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Extract product info from: ..."}
    ],
    temperature=0.3
)
```

### Cloudflare Workers

```typescript
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    
    if (url.pathname === '/api/listings') {
      const listings = await env.DB.prepare(
        "SELECT * FROM listings LIMIT 100"
      ).all();
      
      return Response.json(listings);
    }
    
    return new Response('Not Found', { status: 404 });
  }
};
```

---

## Testing Patterns

### Unit Tests (Python)

```python
import pytest
from arbfinder.pricing import calculate_price

def test_calculate_price_basic():
    """Test basic price calculation"""
    result = calculate_price(base_price=100.0, fees={})
    assert result == 100.0

def test_calculate_price_with_fees():
    """Test price calculation with platform fees"""
    result = calculate_price(
        base_price=100.0,
        fees={"platform": 0.10}
    )
    assert result == 110.0

@pytest.mark.asyncio
async def test_fetch_listings():
    """Test async listing fetch"""
    listings = await fetch_listings("ebay", "RTX 3060")
    assert len(listings) > 0
    assert all(isinstance(l, Listing) for l in listings)
```

### Integration Tests (TypeScript)

```typescript
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ListingCard } from './ListingCard';

describe('ListingCard', () => {
  it('renders listing title', () => {
    const listing = {
      id: '1',
      title: 'Test Product',
      price: 99.99
    };
    
    render(<ListingCard listing={listing} />);
    expect(screen.getByText('Test Product')).toBeInTheDocument();
  });
});
```

---

## Environment Variables

Always use environment variables for sensitive data:

```python
import os
from dotenv import load_dotenv

load_dotenv()

# Required environment variables
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

# Validate required variables
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY is required")
```

---

## Error Handling

Always handle errors gracefully:

```python
from typing import Optional
import logging

logger = logging.getLogger(__name__)

async def fetch_with_retry(url: str, max_retries: int = 3) -> Optional[dict]:
    """Fetch data with automatic retry on failure"""
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=30.0)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                logger.error(f"All retries failed for {url}")
                return None
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

---

## Performance Considerations

### Database Indexing

```sql
-- Add indexes for commonly queried fields
CREATE INDEX IF NOT EXISTS idx_listings_price ON listings(price);
CREATE INDEX IF NOT EXISTS idx_listings_source ON listings(source);
CREATE INDEX IF NOT EXISTS idx_listings_ts ON listings(ts);
CREATE INDEX IF NOT EXISTS idx_listings_title_fts ON listings 
  USING gin(to_tsvector('english', title));
```

### Caching

```python
from functools import lru_cache
import asyncio

# Sync cache
@lru_cache(maxsize=128)
def get_fee_structure(platform: str) -> dict:
    """Get platform fee structure (cached)"""
    return load_fee_structure(platform)

# Async cache with TTL
from aiocache import cached

@cached(ttl=3600)  # 1 hour
async def get_market_data(item_id: str) -> dict:
    """Get market data (cached for 1 hour)"""
    return await fetch_market_data(item_id)
```

---

## Security Best Practices

### Input Validation

```python
from pydantic import BaseModel, validator

class SearchQuery(BaseModel):
    query: str
    limit: int = 100
    
    @validator('query')
    def validate_query(cls, v):
        if len(v) < 2:
            raise ValueError('Query must be at least 2 characters')
        if len(v) > 200:
            raise ValueError('Query too long')
        return v
    
    @validator('limit')
    def validate_limit(cls, v):
        if v < 1 or v > 1000:
            raise ValueError('Limit must be between 1 and 1000')
        return v
```

### Authentication

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Verify JWT token"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
```

---

## Useful Snippets

### Async Context Manager

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def database_connection():
    """Async context manager for database connections"""
    conn = await create_connection()
    try:
        yield conn
    finally:
        await conn.close()

# Usage
async with database_connection() as conn:
    results = await conn.fetch("SELECT * FROM listings")
```

### Retry Decorator

```python
from functools import wraps
import asyncio

def retry_on_exception(max_attempts=3, delay=1.0):
    """Decorator to retry function on exception"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    await asyncio.sleep(delay * (2 ** attempt))
        return wrapper
    return decorator
```

---

## Documentation

Always document:
- Function purpose and behavior
- Parameters and return types
- Possible exceptions
- Usage examples
- Edge cases and limitations

Use this format:

```python
def complex_function(param1: str, param2: int) -> Optional[dict]:
    """
    Brief one-line description.
    
    Longer description explaining the function's behavior,
    its use cases, and any important details.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value, including None case
        
    Raises:
        ValueError: When param2 is negative
        NetworkError: When external API call fails
        
    Example:
        >>> result = complex_function("test", 42)
        >>> print(result['key'])
        'value'
        
    Note:
        Any important notes or warnings about usage.
    """
    pass
```

---

## Common Libraries

### Python
- `fastapi` - API framework
- `httpx` - Async HTTP client
- `pydantic` - Data validation
- `rich` - Terminal formatting
- `crewai` - AI agent framework
- `langchain` - LLM orchestration

### TypeScript
- `next` - React framework
- `@tanstack/react-query` - Data fetching
- `tailwindcss` - Styling
- `zod` - Schema validation
- `lucide-react` - Icons

### Go
- `bubbletea` - TUI framework
- `lipgloss` - Terminal styling
- `database/sql` - Database access

---

## Additional Resources

- [README.md](../README.md) - Project overview
- [DEVELOPER.md](../DEVELOPER.md) - Development guide
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines
- [RULES.md](../RULES.md) - Code style and conventions
- [AGENTS.md](../AGENTS.md) - AI agent documentation
- [API Documentation](https://api.arbfinder.com/docs) - REST API reference

---

Last Updated: 2024-12-15  
Version: 1.0
