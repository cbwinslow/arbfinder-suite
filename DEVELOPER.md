# Developer Guide

## Architecture Overview

ArbFinder Suite is a full-stack application for finding arbitrage opportunities across multiple marketplaces.

### Components

```
┌─────────────────┐
│   Frontend      │  Next.js + TypeScript + Tailwind
│   (Port 3000)   │
└────────┬────────┘
         │
         │ HTTP/REST
         │
┌────────▼────────┐
│   Backend API   │  FastAPI + Python
│   (Port 8080)   │
└────────┬────────┘
         │
         │ SQLite
         │
┌────────▼────────┐
│   Database      │  SQLite3
│                 │
└─────────────────┘
```

### Backend Structure

```
backend/
├── __init__.py           # Package initialization
├── arb_finder.py         # Core arbitrage finder logic
├── cli.py                # Enhanced CLI with subcommands
├── config.py             # Configuration management
├── tui.py                # Rich terminal UI
├── utils.py              # Database utilities
├── watch.py              # Watch mode implementation
└── api/
    ├── __init__.py
    └── main.py           # FastAPI application
```

### Frontend Structure

```
frontend/
├── app/
│   ├── layout.tsx        # Root layout
│   ├── page.tsx          # Home page
│   └── comps/
│       └── page.tsx      # Comps viewer
├── public/               # Static assets
└── package.json
```

### TypeScript Packages

```
packages/
├── client/               # API client library
│   ├── src/
│   │   └── index.ts
│   └── package.json
└── cli/                  # TypeScript CLI
    ├── src/
    │   └── cli.ts
    └── package.json
```

## Development Setup

### Prerequisites

- Python 3.9+
- Node.js 18+
- npm or yarn

### Initial Setup

```bash
# Clone repository
git clone https://github.com/cbwinslow/arbfinder-suite.git
cd arbfinder-suite

# Install Python dependencies
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev,test]"

# Install pre-commit hooks
pre-commit install

# Install frontend dependencies
cd frontend
npm install
cd ..

# Install TypeScript packages (optional)
cd packages/client
npm install
npm run build
cd ../cli
npm install
npm link ../client
npm run build
cd ../..
```

## Running Tests

### Python Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=arbfinder --cov-report=html

# Run specific test file
pytest tests/test_config.py

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_cli.py::test_version
```

### Frontend Tests

```bash
cd frontend
npm test
```

## Code Style

### Python

We use:
- **Black** for code formatting (line length: 100)
- **flake8** for linting
- **mypy** for type checking

```bash
# Format code
black backend/

# Lint code
flake8 backend/

# Type check
mypy backend/
```

### TypeScript

We use:
- **Prettier** for code formatting
- **ESLint** for linting

```bash
cd frontend
npm run lint
```

## Making Changes

### Workflow

1. Create a new branch from `main`
2. Make your changes
3. Write/update tests
4. Run linters and tests
5. Commit with descriptive messages
6. Push and create a pull request

### Commit Messages

Follow conventional commits:

```
feat: Add new feature
fix: Fix bug
docs: Update documentation
style: Format code
refactor: Refactor code
test: Add tests
chore: Update dependencies
```

## Database Schema

### Listings Table

```sql
CREATE TABLE listings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source TEXT,
  url TEXT UNIQUE,
  title TEXT,
  price REAL,
  currency TEXT,
  condition TEXT,
  ts REAL,
  meta_json TEXT
);
```

### Comps Table

```sql
CREATE TABLE comps (
  key_title TEXT PRIMARY KEY,
  avg_price REAL,
  median_price REAL,
  count INTEGER,
  ts REAL
);
```

## API Development

### Adding New Endpoints

1. Define the endpoint in `backend/api/main.py`
2. Add Pydantic models for request/response
3. Implement the handler function
4. Add to API documentation
5. Update TypeScript client if needed

Example:

```python
from fastapi import Query
from pydantic import BaseModel

class NewRequest(BaseModel):
    field: str

@app.post("/api/new-endpoint")
def new_endpoint(data: NewRequest):
    # Implementation
    return {"result": "success"}
```

### Update TypeScript Client

```typescript
// In packages/client/src/index.ts
async newEndpoint(data: NewRequest): Promise<NewResponse> {
  const response = await this.client.post('/api/new-endpoint', data);
  return response.data;
}
```

## CLI Development

### Adding New Commands

1. Add subparser in `backend/cli.py`
2. Implement handler function
3. Add to help text
4. Update documentation

Example:

```python
# Add subparser
new_parser = subparsers.add_parser(
    "newcommand",
    help="Description",
)
new_parser.add_argument("--option", help="Option help")

# Add handler
def handle_newcommand(args):
    # Implementation
    return 0

# In main()
elif args.command == "newcommand":
    return handle_newcommand(args)
```

## Debugging

### Python

Use the VS Code debugger with the provided launch configurations:

- **Python: ArbFinder CLI** - Debug CLI commands
- **Python: API Server** - Debug API server
- **Python: Current File** - Debug current file
- **Python: Pytest** - Debug tests

Or use `pdb`:

```python
import pdb; pdb.set_trace()
```

### Frontend

Use browser DevTools or VS Code debugger:

```bash
cd frontend
npm run dev
# Open http://localhost:3000
# Use browser DevTools
```

## Performance

### Backend

- Use async/await for I/O operations
- Implement pagination for large datasets
- Use database indexes
- Cache frequently accessed data

### Frontend

- Use React.memo for expensive components
- Implement virtual scrolling for long lists
- Use Next.js image optimization
- Minimize bundle size

## Deployment

### Docker

```bash
# Build image
docker build -t arbfinder-suite .

# Run container
docker run -p 8080:8080 -p 3000:3000 \
  -v arbfinder-data:/data \
  arbfinder-suite
```

### Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Troubleshooting

### Common Issues

**Import errors:**
```bash
# Reinstall package in development mode
pip install -e .
```

**Database locked:**
```bash
# Ensure no other processes are using the database
rm ~/.arb_finder.sqlite3  # WARNING: Deletes data
```

**Node modules issues:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Rich Documentation](https://rich.readthedocs.io/)
- [Pytest Documentation](https://docs.pytest.org/)

## Getting Help

- Open an issue on GitHub
- Check existing documentation
- Review test files for examples
