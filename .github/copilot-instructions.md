# GitHub Copilot Instructions for ArbFinder Suite

## Project Overview

ArbFinder Suite is a cloud-native price arbitrage finding and management system built on the Cloudflare platform. It uses AI agents (CrewAI, OpenRouter) for intelligent data processing, crawling (Crawl4AI), and listing optimization.

## Code Style and Conventions

### Python

- **Style Guide**: PEP 8 with Black formatting
- **Type Hints**: Use type hints for all function signatures
- **Docstrings**: Google-style docstrings for all public functions and classes
- **Line Length**: 100 characters (Black default)
- **Imports**: Organize with isort (stdlib, third-party, local)

```python
from typing import Optional, List, Dict, Any
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from backend.utils import get_database_connection


def process_listing(
    listing_data: Dict[str, Any],
    enrichment_level: str = "basic"
) -> Dict[str, Any]:
    """
    Process and enrich a single listing.
    
    Args:
        listing_data: Raw listing data from crawler
        enrichment_level: Level of enrichment (basic, standard, advanced)
        
    Returns:
        Enriched listing data with metadata
        
    Raises:
        ValueError: If listing_data is invalid
    """
    # Implementation
    pass
```

### TypeScript/JavaScript

- **Style Guide**: Airbnb TypeScript style guide
- **Formatting**: Prettier with 2-space indentation
- **Naming**: camelCase for variables/functions, PascalCase for classes/types
- **Async**: Prefer async/await over promises chains
- **Types**: Use TypeScript strict mode, avoid `any`

```typescript
interface ListingData {
  title: string;
  price: number;
  condition?: string;
  metadata?: Record<string, unknown>;
}

async function fetchListings(
  query: string,
  limit: number = 10
): Promise<ListingData[]> {
  const response = await fetch(`/api/listings/search?q=${encodeURIComponent(query)}&limit=${limit}`);
  
  if (!response.ok) {
    throw new Error(`Failed to fetch listings: ${response.statusText}`);
  }
  
  return response.json();
}
```

### Go (for TUI)

- **Style Guide**: Effective Go
- **Formatting**: gofmt
- **Naming**: mixedCase for variables, PascalCase for exported
- **Errors**: Return errors, don't panic
- **Comments**: Comment all exported functions

```go
// SearchPane represents the search interface pane
type SearchPane struct {
    query     string
    providers []string
    threshold float64
}

// UpdateQuery updates the search query
func (s *SearchPane) UpdateQuery(query string) error {
    if query == "" {
        return fmt.Errorf("query cannot be empty")
    }
    s.query = query
    return nil
}
```

## Architecture Patterns

### Backend API (FastAPI)

- **Structure**: Feature-based modules
- **Routing**: Use APIRouter for modular routes
- **Dependencies**: Use FastAPI dependency injection
- **Error Handling**: Custom exception handlers
- **Validation**: Pydantic models for all requests/responses

```python
# backend/api/routes/listings.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List

from backend.api.models import ListingResponse, ListingCreate
from backend.api.dependencies import get_db

router = APIRouter(prefix="/api/listings", tags=["listings"])

@router.get("/", response_model=List[ListingResponse])
async def get_listings(
    limit: int = 10,
    offset: int = 0,
    db = Depends(get_db)
):
    """Get paginated list of listings."""
    return await db.get_listings(limit=limit, offset=offset)
```

### Cloudflare Workers

- **Entry Point**: Single `fetch()` handler with routing
- **Environment**: Use `Env` interface for bindings
- **Responses**: Use `Response.json()` for consistency
- **Errors**: Return appropriate HTTP status codes
- **CORS**: Include CORS headers on all responses

```typescript
export interface Env {
  DB: D1Database;
  IMAGES: R2Bucket;
  CACHE: KVNamespace;
  API_BASE_URL: string;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    
    if (url.pathname === '/api/listings') {
      return handleListings(request, env);
    }
    
    return Response.json({ error: 'Not found' }, { status: 404 });
  }
};
```

### Frontend (Next.js)

- **Structure**: App Router (Next.js 13+)
- **Components**: Functional components with hooks
- **State**: Use React hooks, Context for global state
- **Styling**: Tailwind CSS utility classes
- **Data Fetching**: SWR or React Query for caching

```typescript
// frontend/app/listings/page.tsx
'use client';

import { useState } from 'react';
import useSWR from 'swr';

interface Listing {
  id: number;
  title: string;
  price: number;
}

export default function ListingsPage() {
  const [page, setPage] = useState(0);
  const { data, error } = useSWR<Listing[]>(
    `/api/listings?limit=10&offset=${page * 10}`,
    fetch
  );
  
  if (error) return <div>Failed to load</div>;
  if (!data) return <div>Loading...</div>;
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {data.map(listing => (
        <ListingCard key={listing.id} listing={listing} />
      ))}
    </div>
  );
}
```

## AI Agent Patterns

### CrewAI Agents

- **Configuration**: Define in `crew/crewai.yaml`
- **Tools**: Create reusable tool functions
- **Memory**: Use agent memory for context
- **Output**: Return structured data (JSON)

```python
# backend/api/agents.py
from crewai import Agent, Task
from backend.integrations.openrouter import get_openrouter_llm

def create_metadata_enricher() -> Agent:
    """Create metadata enrichment agent."""
    return Agent(
        role="Metadata Enricher",
        goal="Fill missing product metadata using AI",
        backstory="Expert at extracting product information from text",
        llm=get_openrouter_llm(model="meta-llama/llama-3.1-8b-instruct:free"),
        tools=[extract_brand_tool, classify_category_tool],
        verbose=True
    )

def enrich_metadata_task(product_data: dict) -> Task:
    """Create metadata enrichment task."""
    return Task(
        description=f"Enrich metadata for product: {product_data['title']}",
        agent=create_metadata_enricher(),
        expected_output="JSON object with enriched metadata"
    )
```

### OpenRouter Integration

- **Client**: Use singleton pattern for client
- **Models**: Prefer free models for routine tasks
- **Fallbacks**: Implement fallback to alternative models
- **Caching**: Cache responses when appropriate
- **Streaming**: Use streaming for real-time UIs

```python
# backend/integrations/openrouter/client.py
from typing import Optional, AsyncIterator
import os
import httpx

class OpenRouterClient:
    """OpenRouter API client."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1"
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": os.getenv("OPENROUTER_APP_URL", ""),
                "X-Title": os.getenv("OPENROUTER_APP_NAME", "ArbFinder Suite")
            }
        )
    
    async def complete(
        self,
        model: str,
        prompt: str,
        **kwargs
    ) -> dict:
        """Get completion from model."""
        response = await self.client.post(
            f"{self.base_url}/chat/completions",
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                **kwargs
            }
        )
        response.raise_for_status()
        return response.json()
    
    async def stream(
        self,
        model: str,
        prompt: str,
        **kwargs
    ) -> AsyncIterator[dict]:
        """Stream completion from model."""
        async with self.client.stream(
            "POST",
            f"{self.base_url}/chat/completions",
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": True,
                **kwargs
            }
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    yield json.loads(line[6:])
```

## Database Patterns

### D1 (SQLite)

- **Queries**: Use prepared statements
- **Transactions**: Use for multi-statement operations
- **Indexes**: Index frequently queried columns
- **JSON**: Use JSON columns for flexible data

```typescript
// Query D1 from Worker
async function getListings(env: Env, limit: number = 10): Promise<Listing[]> {
  const result = await env.DB.prepare(
    'SELECT * FROM listings ORDER BY created_at DESC LIMIT ?'
  ).bind(limit).all();
  
  return result.results as Listing[];
}

// With transaction
async function createListingWithComps(
  env: Env,
  listing: Listing,
  comps: Comp[]
): Promise<void> {
  const stmt = env.DB.prepare('BEGIN TRANSACTION');
  await stmt.run();
  
  try {
    // Insert listing
    await env.DB.prepare(
      'INSERT INTO listings (title, price, metadata) VALUES (?, ?, ?)'
    ).bind(listing.title, listing.price, JSON.stringify(listing.metadata)).run();
    
    // Insert comps
    for (const comp of comps) {
      await env.DB.prepare(
        'INSERT INTO comps (listing_id, price, date) VALUES (?, ?, ?)'
      ).bind(listing.id, comp.price, comp.date).run();
    }
    
    await env.DB.prepare('COMMIT').run();
  } catch (error) {
    await env.DB.prepare('ROLLBACK').run();
    throw error;
  }
}
```

## Testing Patterns

### Python Tests (pytest)

```python
# tests/test_agents.py
import pytest
from backend.api.agents import create_metadata_enricher

@pytest.fixture
def sample_product():
    return {
        "title": "Dell Laptop",
        "price": 500.00
    }

@pytest.mark.asyncio
async def test_metadata_enrichment(sample_product):
    """Test metadata enrichment agent."""
    agent = create_metadata_enricher()
    result = await agent.enrich(sample_product)
    
    assert "brand" in result
    assert result["brand"] == "Dell"
    assert "category" in result
```

### TypeScript Tests (Jest)

```typescript
// tests/openrouter.test.ts
import { OpenRouterClient } from '../backend/integrations/openrouter';

describe('OpenRouterClient', () => {
  let client: OpenRouterClient;
  
  beforeEach(() => {
    client = new OpenRouterClient(process.env.TEST_API_KEY);
  });
  
  it('should fetch free models', async () => {
    const models = await client.getFreeModels();
    expect(models).toBeInstanceOf(Array);
    expect(models.length).toBeGreaterThan(0);
  });
  
  it('should complete prompts', async () => {
    const result = await client.complete(
      'meta-llama/llama-3.1-8b-instruct:free',
      'Say hello'
    );
    expect(result.choices[0].message.content).toBeTruthy();
  });
});
```

## Common Patterns to Use

### Error Handling

```python
# Python: Use custom exceptions
class ArbFinderError(Exception):
    """Base exception for ArbFinder."""
    pass

class CrawlerError(ArbFinderError):
    """Crawler-related errors."""
    pass

# Catch and handle gracefully
try:
    listings = await crawler.crawl(url)
except CrawlerError as e:
    logger.error(f"Crawler failed: {e}")
    return {"error": str(e), "listings": []}
```

```typescript
// TypeScript: Use Result type or throw
type Result<T, E = Error> = 
  | { ok: true; value: T }
  | { ok: false; error: E };

async function fetchData(): Promise<Result<Data>> {
  try {
    const response = await fetch('/api/data');
    const data = await response.json();
    return { ok: true, value: data };
  } catch (error) {
    return { ok: false, error: error as Error };
  }
}
```

### Logging

```python
# Python: Use structlog
import structlog

logger = structlog.get_logger()

logger.info(
    "listing_created",
    listing_id=listing.id,
    title=listing.title,
    price=listing.price
)
```

```typescript
// TypeScript: Console with context
function log(level: string, message: string, context?: object) {
  console.log(JSON.stringify({
    level,
    message,
    timestamp: new Date().toISOString(),
    ...context
  }));
}

log('info', 'Listing created', { listingId: 123, title: 'Dell Laptop' });
```

### Configuration

```python
# Python: Use pydantic settings
from pydantic import BaseSettings

class Settings(BaseSettings):
    openrouter_api_key: str
    database_url: str = "sqlite:///arbfinder.db"
    debug: bool = False
    
    class Config:
        env_file = ".env"

settings = Settings()
```

## Security Best Practices

1. **Never commit secrets**: Use environment variables
2. **Validate all input**: Use Pydantic/Zod for validation
3. **Sanitize output**: Escape HTML, validate JSON
4. **Use HTTPS only**: No plain HTTP in production
5. **Implement rate limiting**: Prevent abuse
6. **Log security events**: Track auth failures, unusual activity

## Performance Optimization

1. **Database**: Use indexes, limit query results, cache frequent queries
2. **API**: Implement pagination, use compression, cache responses
3. **Frontend**: Code splitting, lazy loading, image optimization
4. **Workers**: Minimize CPU time, use KV for caching, batch operations

## Documentation

- **Code Comments**: Explain why, not what
- **Docstrings**: All public APIs
- **README**: Update when adding features
- **CHANGELOG**: Document all changes
- **API Docs**: Keep OpenAPI spec updated

## Git Commit Messages

Use conventional commits:

```
feat: add metadata enrichment agent
fix: resolve D1 connection timeout
docs: update Cloudflare setup guide
test: add tests for OpenRouter client
chore: update dependencies
refactor: simplify crawler error handling
perf: optimize database queries
```

## Code Review Checklist

Before submitting PR, verify:

- [ ] All tests pass
- [ ] Code follows style guide
- [ ] Documentation updated
- [ ] No secrets committed
- [ ] Error handling in place
- [ ] Logging added for debugging
- [ ] Performance considered
- [ ] Security reviewed

## Useful Commands

```bash
# Python
black backend/          # Format
flake8 backend/        # Lint
mypy backend/          # Type check
pytest                 # Test

# TypeScript
npm run format         # Format
npm run lint          # Lint
npm run type-check    # Type check
npm test              # Test

# Cloudflare
wrangler dev          # Local development
wrangler deploy       # Deploy
wrangler tail         # View logs

# Git
git commit -m "feat: ..."  # Commit with convention
git push origin <branch>   # Push changes
```

## When to Ask for Help

Ask a human when:

- Security concerns arise
- Architecture decisions needed
- External API integration unclear
- Performance issues encountered
- Breaking changes required

## Project-Specific Context

### Important Files

- `backend/arb_finder.py`: Core arbitrage finder logic
- `backend/api/main.py`: FastAPI application
- `cloudflare/src/index.ts`: Worker entry point
- `crew/crewai.yaml`: Agent configuration
- `frontend/app/page.tsx`: Main UI component

### Common Tasks

**Add a new agent**:
1. Define in `crew/crewai.yaml`
2. Implement in `backend/api/agents.py`
3. Add tests in `tests/test_agents.py`
4. Document in `docs/AGENTS.md`

**Add a new API endpoint**:
1. Create route in `backend/api/routes/`
2. Add Pydantic models in `backend/api/models.py`
3. Update OpenAPI docs
4. Add tests
5. Update frontend client

**Deploy changes**:
1. Run tests: `pytest && npm test`
2. Commit: `git commit -m "..."`
3. Push: `git push`
4. Deploy: `wrangler deploy`

Remember: Prioritize code clarity, maintainability, and security over cleverness!
