# Testing Guide

This document describes the comprehensive testing infrastructure for ArbFinder Suite.

## Overview

The project includes multiple layers of testing:
- **Unit Tests**: Python and TypeScript unit tests
- **Integration Tests**: API and database integration tests
- **Browser Tests**: Automated UI testing with Playwright
- **Security Tests**: Vulnerability scanning with Trivy
- **Coverage**: Code coverage reporting with Codecov

## Python Testing

### Test Structure

```
tests/
├── __init__.py
├── test_cli.py              # CLI command tests
├── test_api.py              # API endpoint tests
├── test_arb_finder.py       # Core functionality tests
├── test_config.py           # Configuration tests
├── test_utils.py            # Utility function tests
└── test_cloudflare_client.py # Cloud storage tests
```

### Running Python Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test file
pytest tests/test_api.py

# Run specific test
pytest tests/test_api.py::test_root_endpoint

# Run with verbose output
pytest -v

# Run tests matching pattern
pytest -k "test_api"
```

### Python Test Coverage

Current coverage: 15+ test cases covering:
- Database operations (CRUD)
- API endpoints (FastAPI)
- CLI commands and argument parsing
- Configuration management
- Cloud storage integration
- Utility functions

### Writing Python Tests

```python
import pytest
from fastapi.testclient import TestClient

def test_api_endpoint(client):
    """Test API endpoint with proper docstring."""
    response = client.get("/api/listings")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.fixture
def client():
    """Fixture for test client."""
    from backend.api.main import app
    return TestClient(app)
```

## TypeScript Testing

### Test Structure

```
packages/client/tests/
└── client.test.ts           # API client tests (22 tests)

frontend/__tests__/
└── page.test.tsx            # Component tests (10 tests)
```

### Running TypeScript Tests

```bash
# Client package tests
cd packages/client
npm test

# With coverage
npm test -- --coverage

# Watch mode
npm test -- --watch

# Frontend tests
cd frontend
npm test

# Update snapshots
npm test -- -u
```

### TypeScript Test Coverage

**Client Package** (22 tests):
- Constructor and configuration
- API endpoint methods (GET, POST)
- Search functionality
- Statistics and comparables
- Stripe checkout integration
- Error handling (network, timeout, 404, 500)

**Frontend** (10 tests):
- Component rendering
- Search and filter UI
- Loading states
- Empty states
- Navigation links

### Writing TypeScript Tests

```typescript
import { render, screen } from '@testing-library/react'
import { ArbFinderClient } from '../src/index'
import MockAdapter from 'axios-mock-adapter'

describe('ArbFinderClient', () => {
  let client: ArbFinderClient
  let mock: MockAdapter

  beforeEach(() => {
    client = new ArbFinderClient()
    mock = new MockAdapter((client as any).client)
  })

  it('should fetch listings', async () => {
    mock.onGet('/api/listings').reply(200, [])
    const data = await client.getListings()
    expect(data).toEqual([])
  })
})
```

## Browser Testing

### Playwright Tests

Automated browser testing using Playwright for:
- Homepage functionality
- Navigation and routing
- Search and filter features
- Form interactions
- Error handling

### Running Browser Tests

Browser tests are integrated into the development workflow and can be triggered with MCP server tools during development.

Example Playwright test flow:
```javascript
// Navigate to homepage
await page.goto('http://localhost:3000')

// Test search
await page.fill('input[placeholder="Search listings..."]', 'test query')
await page.click('button:has-text("Search")')

// Take screenshot
await page.screenshot({ path: 'test.png' })
```

## CI/CD Testing

### GitHub Actions Workflows

**.github/workflows/comprehensive-ci.yml**:
- Multi-version Python testing (3.9, 3.10, 3.11, 3.12)
- TypeScript package testing
- Frontend build verification
- Go TUI compilation
- Security scanning
- Code coverage

**.github/workflows/deploy-production.yml**:
- Pre-deployment testing
- Build verification
- Integration checks

### Security Testing

**Trivy Scanning**:
```bash
# Scan filesystem
trivy fs .

# Scan Docker image
trivy image arbfinder-suite:latest
```

**npm audit**:
```bash
# Audit frontend dependencies
cd frontend && npm audit

# Audit packages
cd packages/client && npm audit
```

## Test Data

### Fixtures

Test fixtures are defined in `conftest.py` for pytest and in individual test files for Jest.

Example pytest fixture:
```python
@pytest.fixture(scope="module")
def setup_test_db():
    """Setup temporary test database."""
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        db_path = tmp.name
    yield db_path
    os.remove(db_path)
```

### Mocking

**Python** - Use `pytest-mock` or `unittest.mock`:
```python
from unittest.mock import Mock, patch

@patch('backend.storage.cloudflare_client.boto3')
def test_upload(mock_boto3):
    mock_boto3.client.return_value = Mock()
    # Test code
```

**TypeScript** - Use `axios-mock-adapter`:
```typescript
import MockAdapter from 'axios-mock-adapter'

const mock = new MockAdapter(client)
mock.onGet('/api/listings').reply(200, mockData)
```

## Coverage Reports

### Python Coverage

Generate HTML coverage report:
```bash
pytest --cov=backend --cov-report=html
open htmlcov/index.html
```

### TypeScript Coverage

Generate coverage report:
```bash
cd packages/client
npm test -- --coverage
```

Coverage is automatically uploaded to Codecov in CI.

## Best Practices

### Testing Guidelines

1. **Write tests first** - TDD approach when possible
2. **Test one thing** - Each test should verify one behavior
3. **Use descriptive names** - Test names should describe what they test
4. **Avoid brittle tests** - Don't test implementation details
5. **Mock external dependencies** - Use mocks for APIs, databases, etc.
6. **Clean up resources** - Use fixtures and teardown properly
7. **Keep tests fast** - Mock slow operations
8. **Maintain high coverage** - Aim for 80%+ coverage

### Test Organization

- Group related tests in the same file
- Use describe/context blocks for organization
- Share setup code with fixtures
- Keep test files close to source code

### Continuous Testing

Run tests automatically:
```bash
# Python - watch mode with pytest-watch
ptw

# TypeScript - watch mode with Jest
npm test -- --watch
```

## Troubleshooting

### Common Issues

**Import errors**:
```bash
# Install package in development mode
pip install -e .
```

**Missing dependencies**:
```bash
# Install all test dependencies
pip install -r requirements-dev.lock
npm install
```

**Test database errors**:
```bash
# Clean test artifacts
rm -rf .pytest_cache htmlcov .coverage
```

**TypeScript type errors**:
```bash
# Rebuild types
npm run build
```

## Additional Resources

- [pytest documentation](https://docs.pytest.org/)
- [Jest documentation](https://jestjs.io/)
- [Testing Library](https://testing-library.com/)
- [Playwright documentation](https://playwright.dev/)
- [Coverage.py](https://coverage.readthedocs.io/)

## Contributing

When adding new features:
1. Write tests for new functionality
2. Ensure all tests pass: `pytest && npm test`
3. Check coverage hasn't decreased
4. Update this documentation if needed

See [CONTRIBUTING.md](CONTRIBUTING.md) for more details.
