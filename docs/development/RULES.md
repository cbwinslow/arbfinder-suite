# ArbFinder Suite - Development Rules and Standards

**Version**: 2.0  
**Last Updated**: 2025-12-15  
**Status**: Mandatory Compliance  

---

## Table of Contents

1. [Code Style and Formatting](#code-style-and-formatting)
2. [Architecture Principles](#architecture-principles)
3. [Git Workflow](#git-workflow)
4. [Testing Requirements](#testing-requirements)
5. [Security Rules](#security-rules)
6. [Documentation Standards](#documentation-standards)
7. [Performance Guidelines](#performance-guidelines)
8. [AI and Agents](#ai-and-agents)
9. [Code Review Process](#code-review-process)
10. [Deployment Rules](#deployment-rules)

---

## Code Style and Formatting

### Python Code (PEP 8)

#### Required Tools
- **black**: Code formatter (line length: 100)
- **flake8**: Linter
- **isort**: Import sorting
- **mypy**: Type checking

#### Configuration
```ini
# .flake8
[flake8]
max-line-length = 100
extend-ignore = E203, W503
exclude = .git,__pycache__,build,dist

# pyproject.toml
[tool.black]
line-length = 100
target-version = ['py39']

[tool.isort]
profile = "black"
line_length = 100

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
```

#### Style Rules

1. **Naming Conventions**
   ```python
   # Classes: PascalCase
   class ProductListing:
       pass
   
   # Functions/variables: snake_case
   def fetch_comparable_sales():
       listing_count = 10
   
   # Constants: UPPER_SNAKE_CASE
   MAX_RETRY_COUNT = 3
   API_TIMEOUT = 30
   
   # Private: Leading underscore
   def _internal_helper():
       pass
   ```

2. **Type Hints (Required)**
   ```python
   from typing import List, Optional, Dict, Any
   
   def analyze_price(
       listing_price: float,
       comparable_prices: List[float],
       confidence_threshold: float = 0.8
   ) -> Dict[str, Any]:
       """Analyze price with type hints."""
       pass
   ```

3. **Docstrings (Required for Public APIs)**
   ```python
   def calculate_profit_margin(cost: float, revenue: float) -> float:
       """Calculate profit margin percentage.
       
       Args:
           cost: Item cost including fees and shipping
           revenue: Total revenue from sale
           
       Returns:
           Profit margin as a percentage (0-100)
           
       Raises:
           ValueError: If cost or revenue is negative
           
       Example:
           >>> calculate_profit_margin(100.0, 150.0)
           33.33
       """
       if cost < 0 or revenue < 0:
           raise ValueError("Cost and revenue must be positive")
       return ((revenue - cost) / revenue) * 100
   ```

4. **Imports**
   ```python
   # Standard library
   import os
   import sys
   from typing import List, Dict
   
   # Third-party
   import httpx
   from fastapi import FastAPI, HTTPException
   
   # Local
   from backend.utils import get_database
   from backend.config import settings
   ```

5. **Error Handling**
   ```python
   # DO: Specific exceptions
   try:
       result = fetch_data()
   except httpx.HTTPError as e:
       logger.error(f"HTTP error: {e}")
       raise
   
   # DON'T: Bare except
   try:
       result = fetch_data()
   except:  # ❌ Never do this
       pass
   ```

---

### JavaScript/TypeScript Code

#### Required Tools
- **ESLint**: Linter
- **Prettier**: Code formatter
- **TypeScript**: Type checking (required)

#### Configuration
```json
// .eslintrc.json
{
  "extends": ["next/core-web-vitals", "prettier"],
  "rules": {
    "no-console": "warn",
    "no-unused-vars": "error",
    "@typescript-eslint/no-explicit-any": "warn"
  }
}

// .prettierrc
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2
}
```

#### Style Rules

1. **Naming Conventions**
   ```typescript
   // Interfaces/Types: PascalCase
   interface ProductListing {
     id: string;
     title: string;
   }
   
   // Functions/variables: camelCase
   const fetchListings = async () => {};
   let listingCount = 0;
   
   // Constants: UPPER_SNAKE_CASE
   const MAX_ITEMS = 100;
   const API_BASE_URL = 'https://api.example.com';
   
   // Components: PascalCase
   const ListingCard: React.FC<Props> = ({ listing }) => {};
   ```

2. **Type Annotations (Required)**
   ```typescript
   interface PriceAnalysis {
     currentPrice: number;
     marketValue: number;
     margin: number;
     confidence: number;
   }
   
   async function analyzePrice(
     listingId: string,
     options?: AnalysisOptions
   ): Promise<PriceAnalysis> {
     // Implementation
   }
   ```

3. **React Components**
   ```typescript
   // Functional components with TypeScript
   interface ListingCardProps {
     listing: Listing;
     onSelect?: (id: string) => void;
   }
   
   export const ListingCard: React.FC<ListingCardProps> = ({
     listing,
     onSelect
   }) => {
     return (
       <div className="listing-card">
         <h3>{listing.title}</h3>
         <p>${listing.price}</p>
       </div>
     );
   };
   ```

---

### YAML Configuration

```yaml
# Use 2 spaces for indentation
agents:
  web_crawler:
    role: "Web Crawler"
    # Comments should explain WHY, not WHAT
    temperature: 0.1  # Low temperature for consistency
    tools:
      - crawl4ai
      - html_parser
```

---

## Architecture Principles

### 1. Separation of Concerns

**DO**:
- Backend handles business logic
- Frontend handles presentation
- Database handles persistence
- Workers handle async tasks

**DON'T**:
- Mix business logic in UI components
- Perform complex calculations in templates
- Store application state in database

### 2. DRY (Don't Repeat Yourself)

**DO**:
```python
# Reusable function
def calculate_fees(price: float, platform: str) -> float:
    fee_rates = {
        'ebay': 0.129,
        'mercari': 0.10
    }
    return price * fee_rates.get(platform, 0)

# Use it multiple times
ebay_fees = calculate_fees(100, 'ebay')
mercari_fees = calculate_fees(100, 'mercari')
```

**DON'T**:
```python
# ❌ Duplicated logic
ebay_fees = 100 * 0.129
mercari_fees = 100 * 0.10
```

### 3. SOLID Principles

#### Single Responsibility
```python
# ❌ Bad: Class doing too much
class ListingManager:
    def fetch_data(self): pass
    def validate_data(self): pass
    def save_to_db(self): pass
    def send_email(self): pass

# ✅ Good: Separate concerns
class ListingFetcher:
    def fetch_data(self): pass

class ListingValidator:
    def validate_data(self): pass

class ListingRepository:
    def save_to_db(self): pass

class NotificationService:
    def send_email(self): pass
```

#### Dependency Inversion
```python
# ✅ Depend on abstractions
from abc import ABC, abstractmethod

class DataStore(ABC):
    @abstractmethod
    def save(self, data): pass

class D1Store(DataStore):
    def save(self, data):
        # D1 implementation
        pass

class PostgresStore(DataStore):
    def save(self, data):
        # PostgreSQL implementation
        pass

# Client depends on abstraction
class ListingService:
    def __init__(self, store: DataStore):
        self.store = store
```

### 4. Fail Fast

```python
def process_listing(listing: dict) -> None:
    # Validate early
    if not listing.get('title'):
        raise ValueError("Title is required")
    if not listing.get('price') or listing['price'] <= 0:
        raise ValueError("Price must be positive")
    
    # Continue processing
    _save_to_database(listing)
```

### 5. Defensive Programming

```python
def safe_divide(a: float, b: float) -> Optional[float]:
    """Safely divide two numbers."""
    if b == 0:
        logger.warning("Division by zero attempted")
        return None
    return a / b

# Always validate external inputs
def fetch_listing(listing_id: str) -> Optional[Listing]:
    if not isinstance(listing_id, str) or not listing_id:
        raise ValueError("Invalid listing_id")
    
    listing = db.query(Listing).filter_by(id=listing_id).first()
    if not listing:
        return None
    
    return listing
```

---

## Git Workflow

### Branch Naming

```
<type>/<description>

Types:
- feature/  - New features
- fix/      - Bug fixes
- docs/     - Documentation
- refactor/ - Code refactoring
- test/     - Test additions
- chore/    - Maintenance tasks

Examples:
feature/openrouter-integration
fix/crawler-timeout-error
docs/update-api-reference
refactor/extract-price-calculator
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]

Types:
- feat:     New feature
- fix:      Bug fix
- docs:     Documentation
- style:    Formatting
- refactor: Code refactoring
- test:     Tests
- chore:    Maintenance

Examples:
feat(crawler): add Mercari support
fix(api): handle missing price fields
docs(readme): update installation instructions
refactor(agents): extract common LLM client
test(pricing): add edge case tests
chore(deps): update dependencies
```

### Pull Request Rules

1. **Required**:
   - [ ] All tests pass
   - [ ] Code coverage doesn't decrease
   - [ ] Linters pass (no warnings)
   - [ ] Documentation updated
   - [ ] Changelog updated
   - [ ] At least 1 approval

2. **PR Description Template**:
   ```markdown
   ## Changes
   - List of changes
   
   ## Motivation
   Why this change is needed
   
   ## Testing
   How it was tested
   
   ## Screenshots (if UI change)
   Before/After images
   
   ## Checklist
   - [ ] Tests added
   - [ ] Documentation updated
   - [ ] Breaking changes noted
   ```

3. **Size Guidelines**:
   - Small: < 200 lines changed
   - Medium: 200-500 lines
   - Large: 500-1000 lines (avoid)
   - Huge: > 1000 lines (must justify)

### Protected Branches

- **main**: Production code
  - Requires PR approval
  - Must pass CI/CD
  - No direct pushes
  
- **develop**: Development code
  - Requires PR approval
  - Must pass tests

---

## Testing Requirements

### Coverage Requirements

- **Minimum**: 80% code coverage
- **Target**: 90% code coverage
- **Critical paths**: 100% coverage

### Test Types

#### 1. Unit Tests (Required)
```python
import pytest
from backend.pricing import calculate_profit_margin

def test_calculate_profit_margin():
    """Test profit margin calculation."""
    assert calculate_profit_margin(100, 150) == pytest.approx(33.33, 0.01)

def test_calculate_profit_margin_zero_cost():
    """Test with zero cost."""
    assert calculate_profit_margin(0, 150) == 100.0

def test_calculate_profit_margin_negative_raises():
    """Test negative values raise error."""
    with pytest.raises(ValueError):
        calculate_profit_margin(-100, 150)
```

#### 2. Integration Tests
```python
@pytest.mark.integration
async def test_crawler_integration(test_client):
    """Test full crawl workflow."""
    response = await test_client.post(
        "/api/crawl",
        json={"source": "shopgoodwill", "query": "iPad"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "listings" in data
    assert len(data["listings"]) > 0
```

#### 3. End-to-End Tests
```typescript
// e2e/listings.spec.ts
import { test, expect } from '@playwright/test';

test('search and view listing', async ({ page }) => {
  await page.goto('/');
  await page.fill('[data-testid="search-input"]', 'iPad');
  await page.click('[data-testid="search-button"]');
  
  await expect(page.locator('.listing-card')).toHaveCount(10, { timeout: 5000 });
  
  await page.click('.listing-card:first-child');
  await expect(page).toHaveURL(/\/listings\/\d+/);
});
```

### Test Organization

```
tests/
├── unit/
│   ├── test_crawler.py
│   ├── test_pricing.py
│   └── test_agents.py
├── integration/
│   ├── test_api.py
│   └── test_database.py
├── e2e/
│   ├── listings.spec.ts
│   └── search.spec.ts
└── conftest.py  # Shared fixtures
```

### Test Fixtures

```python
# conftest.py
import pytest
from backend.database import get_database

@pytest.fixture
def db():
    """Provide test database."""
    database = get_database(":memory:")
    database.create_all()
    yield database
    database.drop_all()

@pytest.fixture
def sample_listing():
    """Provide sample listing data."""
    return {
        "title": "iPad Pro 11-inch",
        "price": 299.99,
        "condition": "good",
        "source": "shopgoodwill"
    }
```

---

## Security Rules

### 1. Never Commit Secrets

```bash
# ❌ NEVER do this
API_KEY = "sk_live_abc123xyz"

# ✅ Always use environment variables
import os
API_KEY = os.getenv("API_KEY")

# ✅ Or use secret management
from cloudflare import get_secret
API_KEY = get_secret("API_KEY")
```

### 2. Input Validation

```python
from pydantic import BaseModel, validator

class ListingCreate(BaseModel):
    title: str
    price: float
    url: str
    
    @validator('title')
    def title_length(cls, v):
        if len(v) < 10 or len(v) > 200:
            raise ValueError("Title must be 10-200 characters")
        return v
    
    @validator('price')
    def price_positive(cls, v):
        if v <= 0:
            raise ValueError("Price must be positive")
        return v
    
    @validator('url')
    def url_valid(cls, v):
        if not v.startswith('http'):
            raise ValueError("URL must start with http/https")
        return v
```

### 3. SQL Injection Prevention

```python
# ✅ Use parameterized queries
cursor.execute(
    "SELECT * FROM listings WHERE id = ?",
    (listing_id,)
)

# ❌ NEVER use string formatting
cursor.execute(
    f"SELECT * FROM listings WHERE id = {listing_id}"  # ❌ DANGEROUS
)
```

### 4. XSS Prevention

```typescript
// ✅ React automatically escapes
<div>{listing.title}</div>

// ❌ Don't use dangerouslySetInnerHTML without sanitization
<div dangerouslySetInnerHTML={{ __html: listing.description }} />  // ❌

// ✅ Sanitize first
import DOMPurify from 'dompurify';
<div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(listing.description) }} />
```

### 5. Authentication

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

security = HTTPBearer()

def get_current_user(token: str = Depends(security)):
    """Verify JWT token."""
    try:
        payload = verify_token(token.credentials)
        return payload['user_id']
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )

# Use in routes
@app.get("/api/private")
def private_endpoint(user_id: str = Depends(get_current_user)):
    return {"user_id": user_id}
```

---

## Documentation Standards

### Code Documentation

```python
def fetch_comparable_sales(
    query: str,
    limit: int = 150,
    days: int = 90
) -> List[Dict[str, Any]]:
    """Fetch comparable sold listings from eBay.
    
    This function searches eBay's sold listings for items matching
    the query and returns structured data for price comparison.
    
    Args:
        query: Search query string
        limit: Maximum number of results to return (1-200)
        days: Number of days to look back (1-90)
        
    Returns:
        List of dictionaries containing listing data:
        - title: Product title
        - price: Sale price
        - date: Sale date
        - condition: Item condition
        
    Raises:
        ValueError: If limit or days are out of range
        HTTPError: If eBay API request fails
        
    Example:
        >>> comps = fetch_comparable_sales("iPad Pro", limit=50)
        >>> avg_price = sum(c['price'] for c in comps) / len(comps)
        
    Note:
        Results are cached for 24 hours to reduce API calls.
    """
    pass
```

### API Documentation

```python
from fastapi import FastAPI, Query
from pydantic import BaseModel

app = FastAPI(
    title="ArbFinder API",
    description="Price arbitrage discovery platform",
    version="2.0.0"
)

class ListingResponse(BaseModel):
    """Listing response model."""
    id: str
    title: str
    price: float
    
    class Config:
        schema_extra = {
            "example": {
                "id": "12345",
                "title": "iPad Pro 11-inch",
                "price": 299.99
            }
        }

@app.get(
    "/api/listings",
    response_model=List[ListingResponse],
    summary="Get listings",
    description="Retrieve product listings with pagination",
    tags=["listings"]
)
def get_listings(
    limit: int = Query(10, ge=1, le=100, description="Number of results"),
    offset: int = Query(0, ge=0, description="Pagination offset")
):
    """
    Get product listings.
    
    - **limit**: Number of results (1-100)
    - **offset**: Pagination offset
    
    Returns list of listings with id, title, and price.
    """
    pass
```

### README Files

Every directory should have a README.md:

```markdown
# Directory Name

Brief description of what's in this directory.

## Contents

- `file1.py`: Description
- `file2.py`: Description

## Usage

```python
from module import function
result = function()
```

## Testing

```bash
pytest tests/
```
```

---

## Performance Guidelines

### 1. Database Queries

```python
# ✅ Batch operations
db.bulk_insert_mappings(Listing, listings_data)

# ❌ Loop inserts
for listing in listings_data:
    db.add(Listing(**listing))  # Slow!

# ✅ Use indexes
CREATE INDEX idx_listings_price ON listings(price);
CREATE INDEX idx_listings_source ON listings(source);

# ✅ Limit query results
listings = db.query(Listing).limit(100).all()

# ✅ Use pagination
listings = db.query(Listing).offset(page * size).limit(size).all()
```

### 2. API Requests

```python
# ✅ Use async for I/O
import httpx

async def fetch_multiple(urls: List[str]) -> List[dict]:
    async with httpx.AsyncClient() as client:
        tasks = [client.get(url) for url in urls]
        responses = await asyncio.gather(*tasks)
        return [r.json() for r in responses]

# ✅ Cache results
from functools import lru_cache

@lru_cache(maxsize=1000)
def expensive_calculation(input: str) -> float:
    # Cached for same input
    pass
```

### 3. Frontend Performance

```typescript
// ✅ Lazy load components
const ListingDetail = lazy(() => import('./ListingDetail'));

// ✅ Memoize expensive computations
const expensiveValue = useMemo(() => {
  return computeExpensiveValue(data);
}, [data]);

// ✅ Debounce search
const debouncedSearch = useMemo(
  () => debounce((query) => performSearch(query), 300),
  []
);

// ✅ Virtual scrolling for large lists
import { FixedSizeList } from 'react-window';
```

---

## AI and Agents

### 1. LLM Usage

```python
# ✅ Use free models when possible
preferred_models = [
    "openrouter/meta-llama/llama-2-70b-chat",  # Free
    "openrouter/anthropic/claude-instant-v1",   # Cheap
    "openrouter/openai/gpt-4"                    # Expensive, fallback
]

# ✅ Set appropriate temperature
# Low (0.0-0.3): Factual, deterministic tasks
# Medium (0.4-0.7): Creative tasks
# High (0.8-1.0): Very creative, exploratory

# ✅ Limit token usage
response = llm.complete(
    prompt=prompt,
    max_tokens=500,  # Limit response length
    stop=["\n\n"]    # Stop at natural break
)

# ✅ Cache prompts
@lru_cache(maxsize=100)
def get_prompt_template(category: str) -> str:
    return load_template(category)
```

### 2. Agent Error Handling

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def execute_agent_task(agent, task):
    """Execute agent task with retry logic."""
    try:
        result = await agent.execute(task)
        return result
    except RateLimitError:
        logger.warning("Rate limit hit, waiting...")
        raise  # Retry
    except Exception as e:
        logger.error(f"Agent error: {e}")
        raise
```

---

## Code Review Process

### Reviewer Checklist

- [ ] Code follows style guide
- [ ] Tests are comprehensive
- [ ] No security vulnerabilities
- [ ] Performance considerations addressed
- [ ] Documentation is clear
- [ ] No TODOs or FIXMEs (unless tracked)
- [ ] Error handling is appropriate
- [ ] Logging is adequate
- [ ] Breaking changes are noted

### Review Comments

```
# ✅ Good comment
"Consider extracting this into a separate function for reusability."

# ✅ Good comment with suggestion
"This could cause a race condition. Consider using a lock:
```python
with threading.Lock():
    # protected code
```
"

# ❌ Bad comment
"This is bad."  # Not helpful

# ✅ Good approval
"LGTM! Nice use of type hints. Minor suggestion: add docstring."
```

---

## Deployment Rules

### Pre-Deployment Checklist

- [ ] All tests pass (unit, integration, e2e)
- [ ] Code coverage meets threshold
- [ ] Security scan passed
- [ ] Performance benchmarks met
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] Database migrations tested
- [ ] Rollback plan documented
- [ ] Monitoring alerts configured

### Environment Variables

```bash
# ✅ Document all environment variables
# .env.example
# API Keys (Required)
OPENROUTER_API_KEY=your-key-here
EBAY_APP_ID=your-app-id

# Database (Required)
DATABASE_URL=your-database-url

# Cloudflare (Required)
CLOUDFLARE_ACCOUNT_ID=your-account-id
CLOUDFLARE_API_TOKEN=your-token

# Optional
LOG_LEVEL=INFO
```

### Deployment Process

1. **Staging Deployment**
   - Deploy to staging environment
   - Run smoke tests
   - Verify functionality

2. **Production Deployment**
   - Create release tag
   - Deploy with Cloudflare Workers/Pages
   - Monitor error rates
   - Verify key metrics

3. **Rollback Plan**
   - Keep previous version ready
   - Know rollback commands
   - Monitor for issues

---

**Violation of these rules may result in PR rejection or code reversion.**

---

**End of Development Rules**
