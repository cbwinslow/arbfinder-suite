# Project Rules and Conventions

This document defines the rules, conventions, and best practices for the ArbFinder Suite project.

---

## Table of Contents

1. [Code Style](#code-style)
2. [Git Workflow](#git-workflow)
3. [Testing Requirements](#testing-requirements)
4. [Documentation Standards](#documentation-standards)
5. [Security Guidelines](#security-guidelines)
6. [Performance Standards](#performance-standards)
7. [API Design](#api-design)
8. [Error Handling](#error-handling)
9. [Logging](#logging)
10. [Deployment](#deployment)

---

## Code Style

### Python

#### General Rules
- Follow PEP 8 style guide
- Use Black for code formatting (line length: 100)
- Use type hints for all function signatures
- Maximum function length: 50 lines
- Maximum file length: 500 lines

#### Naming Conventions
```python
# Classes: PascalCase
class WebCrawlerAgent:
    pass

# Functions/methods: snake_case
def fetch_listings():
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRY_COUNT = 3

# Private members: leading underscore
def _internal_helper():
    pass

# Variables: snake_case
user_count = 0
```

#### Documentation
```python
def calculate_price(
    base_price: float,
    condition: str,
    fees: dict
) -> float:
    """Calculate final price including fees and condition.
    
    Args:
        base_price: Original price in USD
        condition: Item condition (new, used, refurbished)
        fees: Dictionary of applicable fees
        
    Returns:
        Final calculated price
        
    Raises:
        ValueError: If base_price is negative
        
    Example:
        >>> calculate_price(100.0, "used", {"platform": 0.10})
        110.0
    """
    pass
```

#### Imports
```python
# Standard library first
import os
import sys
from typing import List, Dict

# Third-party packages
import httpx
from fastapi import FastAPI

# Local imports
from arbfinder.utils import normalize_price
from arbfinder.agents import WebCrawlerAgent
```

### TypeScript/JavaScript

#### General Rules
- Follow Airbnb JavaScript Style Guide
- Use ESLint with recommended rules
- Use Prettier for formatting
- Prefer const over let, avoid var
- Use async/await over promises

#### Naming Conventions
```typescript
// Interfaces: PascalCase with 'I' prefix
interface IListing {
  id: string;
  title: string;
}

// Types: PascalCase
type Status = 'pending' | 'active' | 'sold';

// Functions: camelCase
function fetchListings(): Promise<Listing[]> {
  return [];
}

// Constants: UPPER_SNAKE_CASE
const MAX_RETRIES = 3;

// Variables: camelCase
let userCount = 0;
```

#### Documentation
```typescript
/**
 * Calculate price with fees and adjustments
 * @param basePrice - Original price in USD
 * @param condition - Item condition
 * @param fees - Platform and shipping fees
 * @returns Final calculated price
 * @throws {Error} If basePrice is negative
 * @example
 * ```typescript
 * calculatePrice(100, 'used', { platform: 0.10 })
 * // => 110.0
 * ```
 */
function calculatePrice(
  basePrice: number,
  condition: string,
  fees: Record<string, number>
): number {
  // Implementation
}
```

### Go

#### General Rules
- Follow Go standard style (gofmt)
- Use golangci-lint for linting
- Keep functions small and focused
- Document exported functions
- Handle all errors explicitly

#### Naming Conventions
```go
// Exported: PascalCase
type Listing struct {
    ID    string
    Title string
}

// Unexported: camelCase
type internalState struct {
    count int
}

// Constants: PascalCase
const MaxRetries = 3

// Functions: PascalCase (exported), camelCase (private)
func FetchListings() ([]Listing, error) {
    return nil, nil
}
```

---

## Git Workflow

### Branch Naming

```
main              - Production-ready code
develop           - Integration branch
feature/<name>    - New features
bugfix/<name>     - Bug fixes
hotfix/<name>     - Urgent production fixes
release/<version> - Release preparation
```

### Commit Messages

Follow Conventional Commits specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style changes
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `ci`: CI/CD changes

**Examples:**
```bash
feat(api): add listing search endpoint

fix(crawler): handle rate limit errors gracefully

docs(readme): update installation instructions

refactor(agents): simplify agent orchestration logic

perf(database): optimize listing query with indexes
```

### Pull Request Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/add-search-filters
   ```

2. **Make Changes and Commit**
   ```bash
   git add .
   git commit -m "feat(search): add price range filter"
   ```

3. **Push to Remote**
   ```bash
   git push origin feature/add-search-filters
   ```

4. **Create Pull Request**
   - Descriptive title
   - Detailed description
   - Link related issues
   - Request reviewers

5. **Code Review**
   - Address all comments
   - Pass all CI checks
   - Get approvals

6. **Merge**
   - Squash and merge for feature branches
   - Merge commit for releases
   - Delete branch after merge

### Pre-commit Hooks

Required hooks:
- Code formatting (Black, Prettier)
- Linting (Flake8, ESLint)
- Type checking (mypy, TypeScript)
- Tests (pytest, jest)
- Security scan (bandit)

Install with:
```bash
pre-commit install
```

---

## Testing Requirements

### Coverage Requirements

- Minimum 80% code coverage
- 100% coverage for critical paths
- All public APIs must be tested

### Test Structure

```python
# test_pricing.py
import pytest
from arbfinder.pricing import calculate_price

class TestPriceCalculation:
    """Test suite for price calculation"""
    
    def test_basic_calculation(self):
        """Test basic price calculation"""
        result = calculate_price(100.0, "new", {})
        assert result == 100.0
    
    def test_with_fees(self):
        """Test calculation with platform fees"""
        result = calculate_price(100.0, "new", {"platform": 0.10})
        assert result == 110.0
    
    @pytest.mark.parametrize("condition,expected", [
        ("new", 100.0),
        ("used", 80.0),
        ("refurbished", 90.0),
    ])
    def test_condition_multipliers(self, condition, expected):
        """Test different condition multipliers"""
        result = calculate_price(100.0, condition, {})
        assert result == expected
```

### Test Types

#### Unit Tests
- Test individual functions
- Mock external dependencies
- Fast execution (< 1s each)
- No database or network calls

#### Integration Tests
- Test component interactions
- Use test database
- Can make network calls
- Slower execution (< 10s each)

#### End-to-End Tests
- Test complete workflows
- Use staging environment
- Real services (where safe)
- Slowest execution (< 60s each)

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=arbfinder --cov-report=html

# Run specific test file
pytest tests/test_pricing.py

# Run specific test
pytest tests/test_pricing.py::TestPriceCalculation::test_basic_calculation

# Run integration tests only
pytest -m integration

# Run with verbose output
pytest -v
```

---

## Documentation Standards

### Code Documentation

- All public APIs must be documented
- Include examples in docstrings
- Document parameters and return values
- Explain complex algorithms
- Add inline comments for tricky code

### README Files

Each module/package should have a README with:
- Purpose and overview
- Installation instructions
- Usage examples
- API reference
- Configuration options
- Troubleshooting

### API Documentation

- Use OpenAPI/Swagger for REST APIs
- Auto-generate from code annotations
- Include request/response examples
- Document error codes
- Provide authentication guide

### Changelog

Follow Keep a Changelog format:

```markdown
# Changelog

## [Unreleased]

## [0.4.0] - 2024-12-15

### Added
- Enhanced CLI with subcommands
- TypeScript SDK package
- Docker support

### Changed
- Improved performance of listing queries
- Updated dependencies

### Fixed
- Race condition in crawler
- Memory leak in image processor

### Deprecated
- Old CLI interface (will be removed in 1.0)

### Removed
- Legacy API v1 endpoints

### Security
- Fixed SQL injection vulnerability
```

---

## Security Guidelines

### Authentication

- Never store passwords in plain text
- Use bcrypt for password hashing
- Implement rate limiting on auth endpoints
- Support MFA for admin accounts
- Invalidate sessions on logout

### API Keys

```python
# ❌ DON'T
API_KEY = "sk-1234567890"

# ✅ DO
import os
API_KEY = os.environ.get("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY environment variable required")
```

### Input Validation

```python
# ❌ DON'T
def search(query: str):
    sql = f"SELECT * FROM listings WHERE title LIKE '%{query}%'"
    
# ✅ DO
def search(query: str):
    # Validate input
    if len(query) > 100:
        raise ValueError("Query too long")
    
    # Use parameterized queries
    sql = "SELECT * FROM listings WHERE title LIKE ?"
    cursor.execute(sql, (f"%{query}%",))
```

### Secrets Management

- Use environment variables
- Never commit secrets to Git
- Use .env.example for templates
- Rotate keys regularly
- Use secret management service in production

### OWASP Top 10

Must protect against:
1. Injection attacks
2. Broken authentication
3. Sensitive data exposure
4. XML external entities
5. Broken access control
6. Security misconfiguration
7. Cross-site scripting (XSS)
8. Insecure deserialization
9. Using components with known vulnerabilities
10. Insufficient logging and monitoring

---

## Performance Standards

### Response Time Targets

| Operation | Target | Maximum |
|-----------|--------|---------|
| API request | < 100ms | 200ms |
| Page load | < 1s | 2s |
| Search query | < 200ms | 500ms |
| Database query | < 50ms | 100ms |
| Worker execution | < 25ms | 50ms |

### Optimization Rules

1. **Database**
   - Add indexes for commonly queried fields
   - Use connection pooling
   - Implement query caching
   - Avoid N+1 queries

2. **API**
   - Implement response caching
   - Use pagination for large results
   - Enable compression (gzip/brotli)
   - Batch related requests

3. **Frontend**
   - Code splitting
   - Lazy loading
   - Image optimization
   - Minimize bundle size
   - Use CDN for static assets

4. **Workers**
   - Minimize cold start time
   - Optimize bundle size
   - Use streaming where possible
   - Implement caching

### Monitoring

Required metrics:
- Request latency (p50, p95, p99)
- Error rate
- Throughput (requests/second)
- Database query time
- Memory usage
- CPU usage

---

## API Design

### RESTful Principles

- Use HTTP methods correctly (GET, POST, PUT, DELETE)
- Use plural nouns for resources (/listings, /agents)
- Use HTTP status codes appropriately
- Version your API (/api/v1/, /api/v2/)
- Support pagination and filtering

### URL Structure

```
Good:
GET    /api/v1/listings              - Get all listings
GET    /api/v1/listings/{id}         - Get specific listing
POST   /api/v1/listings              - Create listing
PUT    /api/v1/listings/{id}         - Update listing
DELETE /api/v1/listings/{id}         - Delete listing
GET    /api/v1/listings/{id}/comps   - Get comps for listing

Bad:
GET    /api/v1/getListings
POST   /api/v1/listing/create
GET    /api/v1/listings/{id}/get
```

### Response Format

```json
{
  "success": true,
  "data": {
    "id": "123",
    "title": "RTX 3060",
    "price": 299.99
  },
  "meta": {
    "timestamp": "2024-12-15T10:30:00Z",
    "version": "1.0"
  }
}
```

### Error Format

```json
{
  "success": false,
  "error": {
    "code": "INVALID_INPUT",
    "message": "Price must be a positive number",
    "field": "price"
  },
  "meta": {
    "timestamp": "2024-12-15T10:30:00Z",
    "request_id": "abc123"
  }
}
```

---

## Error Handling

### Python

```python
# ❌ DON'T - Bare except
try:
    result = risky_operation()
except:
    pass

# ✅ DO - Specific exceptions
try:
    result = risky_operation()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
    raise
except NetworkError as e:
    logger.warning(f"Network error: {e}")
    return None
finally:
    cleanup()
```

### TypeScript

```typescript
// ✅ DO - Proper error handling
async function fetchData(): Promise<Data | null> {
  try {
    const response = await api.get('/data');
    return response.data;
  } catch (error) {
    if (error instanceof NetworkError) {
      logger.error('Network error:', error);
      // Retry logic
    } else if (error instanceof ValidationError) {
      logger.warn('Validation error:', error);
      // Handle validation
    } else {
      logger.error('Unexpected error:', error);
      throw error;
    }
    return null;
  }
}
```

### Custom Exceptions

```python
class ArbFinderError(Exception):
    """Base exception for ArbFinder"""
    pass

class CrawlerError(ArbFinderError):
    """Crawler-specific errors"""
    pass

class PricingError(ArbFinderError):
    """Pricing calculation errors"""
    pass
```

---

## Logging

### Log Levels

- **DEBUG:** Detailed information for debugging
- **INFO:** General informational messages
- **WARNING:** Warning messages for potentially harmful situations
- **ERROR:** Error messages for serious problems
- **CRITICAL:** Critical messages for system failures

### Log Format

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.info("Application started")
logger.error("Failed to process listing", extra={"listing_id": "123"})
```

### What to Log

**DO log:**
- Application start/stop
- Important state changes
- Errors and exceptions
- Performance metrics
- Security events

**DON'T log:**
- Passwords or API keys
- PII (personally identifiable information)
- Credit card numbers
- Excessive debug info in production

---

## Deployment

### Environment Variables

Required for all environments:
```bash
# Application
APP_ENV=production
APP_VERSION=0.4.0
LOG_LEVEL=info

# Database
DATABASE_URL=postgresql://user:pass@host/db

# External Services
OPENROUTER_API_KEY=sk-or-...
CLOUDFLARE_API_TOKEN=...
```

### Deployment Checklist

- [ ] All tests passing
- [ ] Code reviewed and approved
- [ ] Documentation updated
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] Security scan passed
- [ ] Performance benchmarks met
- [ ] Monitoring configured
- [ ] Rollback plan documented
- [ ] Stakeholders notified

### Rollback Procedure

1. Identify the issue
2. Stop incoming traffic
3. Revert to previous version
4. Verify functionality
5. Resume traffic
6. Post-mortem analysis

---

Last Updated: 2024-12-15  
Version: 1.0
