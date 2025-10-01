# Contributing to ArbFinder Suite

Thank you for your interest in contributing to ArbFinder Suite! This document provides guidelines and information for contributors.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/arbfinder-suite.git`
3. Create a new branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test thoroughly
6. Submit a pull request

## Development Setup

### Backend Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt

# Install development dependencies
pip install flake8 mypy black isort pytest
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

## Code Style

### Python

- Follow PEP 8 guidelines
- Use type hints for function parameters and return values
- Add docstrings to all functions and classes
- Keep functions focused and under 50 lines when possible
- Use meaningful variable names

Example:
```python
def search_listings(query: str, limit: int = 100) -> List[Listing]:
    """
    Search for listings matching the query.
    
    Args:
        query: Search term
        limit: Maximum number of results
    
    Returns:
        List of matching listings
    """
    # Implementation
```

### TypeScript/React

- Use TypeScript for type safety
- Follow React best practices and hooks patterns
- Use functional components
- Keep components small and focused
- Use meaningful prop and state names

## Testing

### Backend Tests

```bash
# Run tests (when available)
pytest backend/tests/

# Check types
mypy backend/

# Lint code
flake8 backend/
```

### Frontend Tests

```bash
cd frontend
npm test
npm run lint
```

## Adding New Features

### New Providers

To add a new marketplace provider:

1. Create a new class in `backend/arb_finder.py` that extends `Provider`
2. Implement the `search()` method
3. Add the provider to the providers dict in `run_arbfinder()`
4. Update documentation

Example:
```python
class NewMarketplaceLive(Provider):
    name = "newmarketplace"
    
    async def search(self, query: str, limit: int = 40):
        # Implementation
        return items
```

### New API Endpoints

To add new API endpoints:

1. Add the endpoint function to `backend/api/main.py`
2. Use appropriate HTTP methods (GET, POST, etc.)
3. Add input validation with Pydantic models
4. Document with docstrings
5. Update README with endpoint info

Example:
```python
@app.get("/api/your-endpoint")
def your_endpoint(param: str = Query(...)) -> Dict[str, Any]:
    """Endpoint description."""
    # Implementation
    return {"result": "data"}
```

### New UI Components

To add new UI components:

1. Create component in `frontend/app/` or `frontend/components/`
2. Use TypeScript for type safety
3. Follow existing styling patterns (Tailwind CSS)
4. Ensure responsive design
5. Add loading states and error handling

## Commit Messages

Use clear, descriptive commit messages:

- `feat: Add Reverb provider for sold listings`
- `fix: Correct price parsing in GovDeals provider`
- `docs: Update README with new CLI options`
- `style: Format code with black`
- `refactor: Simplify database connection logic`
- `test: Add tests for config module`

## Pull Request Process

1. Update documentation if needed
2. Add tests for new features
3. Ensure all tests pass
4. Update CHANGELOG.md
5. Request review from maintainers

### PR Checklist

- [ ] Code follows style guidelines
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
- [ ] Commit messages are clear
- [ ] Branch is up to date with main

## Areas for Contribution

We welcome contributions in these areas:

### High Priority
- Additional marketplace providers (Reverb, Mercari, etc.)
- Email/SMS notifications
- Price history tracking
- Export to additional formats (PDF, Excel)
- Mobile app development

### Medium Priority
- Dark/light mode toggle
- Improved error handling
- Performance optimizations
- Additional test coverage
- Docker containerization

### Nice to Have
- Browser extension
- Desktop app (Electron)
- Advanced analytics
- Machine learning price prediction
- Multi-language support

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for questions or ideas
- Check existing issues before creating new ones

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the code, not the person
- Help others learn and grow

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Git commit history

Thank you for making ArbFinder Suite better! 🎉
