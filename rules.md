# 📜 ArbFinder Suite - Project Rules and Guidelines

## Overview
This document establishes the rules, conventions, and best practices for the ArbFinder Suite project. All contributors must follow these guidelines to maintain code quality, consistency, and project integrity.

---

## 1. Code Standards

### 1.1 Python Code Standards

#### Style Guide
- **Follow PEP 8**: All Python code must conform to PEP 8 style guide
- **Line Length**: Maximum 100 characters per line
- **Indentation**: 4 spaces (no tabs)
- **Quotes**: Use double quotes for strings by default
- **Imports**: Organize imports: stdlib, third-party, local

#### Code Formatting
```python
# Use black for automatic formatting
black backend/ --line-length 100

# Use isort for import sorting
isort backend/ --profile black

# Use flake8 for linting
flake8 backend/ --max-line-length=100
```

#### Type Hints
- **Required**: All function signatures must include type hints
- **Return Types**: Always specify return types
- **Optional**: Use `Optional[Type]` for nullable parameters

```python
# ✅ Good
def calculate_discount(price: float, percentage: float) -> float:
    return price * (percentage / 100)

# ❌ Bad
def calculate_discount(price, percentage):
    return price * (percentage / 100)
```

#### Docstrings
- **Format**: Use Google-style docstrings
- **Required**: All public functions, classes, and modules
- **Content**: Include description, args, returns, raises

```python
def fetch_listings(source: str, limit: int = 100) -> List[Dict]:
    """Fetch listings from a specified source.
    
    Args:
        source: The data source identifier
        limit: Maximum number of listings to fetch (default: 100)
        
    Returns:
        List of listing dictionaries
        
    Raises:
        ValueError: If source is invalid
        ConnectionError: If unable to connect to source
    """
    pass
```

### 1.2 JavaScript/TypeScript Standards

#### Style Guide
- **Follow Airbnb Style Guide**: Base for JavaScript conventions
- **Semicolons**: Required at end of statements
- **Quotes**: Single quotes for strings
- **Indentation**: 2 spaces

#### Code Formatting
```bash
# Use Prettier for formatting
prettier --write "**/*.{js,ts,jsx,tsx}"

# Use ESLint for linting
eslint "**/*.{js,ts,jsx,tsx}" --fix
```

#### Type Safety
- **TypeScript Required**: All new code must be TypeScript
- **Strict Mode**: Enable strict TypeScript checking
- **No `any`**: Avoid using `any` type unless absolutely necessary

```typescript
// ✅ Good
interface Listing {
  id: number;
  title: string;
  price: number;
}

function formatListing(listing: Listing): string {
  return `${listing.title}: $${listing.price}`;
}

// ❌ Bad
function formatListing(listing: any) {
  return `${listing.title}: $${listing.price}`;
}
```

### 1.3 SQL Standards

#### Query Style
- **Keywords**: UPPERCASE for SQL keywords
- **Identifiers**: lowercase_with_underscores
- **Indentation**: Align clauses vertically

```sql
-- ✅ Good
SELECT 
    l.id,
    l.title,
    l.price
FROM listings l
WHERE l.source = 'shopgoodwill'
    AND l.price > 100
ORDER BY l.price DESC
LIMIT 10;

-- ❌ Bad
select l.id,l.title,l.price from listings l where l.source='shopgoodwill' and l.price>100 order by l.price desc limit 10;
```

---

## 2. Git Workflow

### 2.1 Branch Naming
```
feature/short-description     # New features
bugfix/issue-number          # Bug fixes
hotfix/critical-issue        # Critical production fixes
docs/documentation-update    # Documentation changes
refactor/code-cleanup        # Code refactoring
test/test-improvements       # Test additions
```

### 2.2 Commit Messages
- **Format**: `<type>(<scope>): <subject>`
- **Types**: feat, fix, docs, style, refactor, test, chore
- **Subject**: Imperative mood, lowercase, no period
- **Body**: Explain what and why, not how

```bash
# ✅ Good
feat(crawler): add support for Mercari website
fix(api): resolve pagination offset error
docs(readme): update installation instructions

# ❌ Bad
updated some stuff
fixed bug
WIP
```

### 2.3 Pull Requests

#### Requirements
- **Title**: Clear, descriptive title
- **Description**: What, why, and how
- **Tests**: Include tests for new features
- **Documentation**: Update relevant docs
- **Review**: Minimum 1 approval required

#### PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests passed
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added to complex code
- [ ] Documentation updated
- [ ] No new warnings generated
```

---

## 3. Testing Standards

### 3.1 Test Coverage
- **Minimum**: 80% code coverage
- **Critical Paths**: 100% coverage for critical functionality
- **New Code**: All new code must have tests

### 3.2 Test Organization
```
tests/
├── unit/           # Unit tests (isolated functions)
├── integration/    # Integration tests (multiple components)
├── e2e/           # End-to-end tests (full workflows)
└── fixtures/      # Test data and fixtures
```

### 3.3 Test Naming
```python
def test_<function>_<scenario>_<expected_result>():
    """Test that describes what is being tested."""
    pass

# Examples
def test_calculate_discount_with_valid_inputs_returns_correct_value():
    pass

def test_fetch_listings_with_invalid_source_raises_value_error():
    pass
```

### 3.4 Test Structure
```python
def test_example():
    # Arrange: Set up test data and dependencies
    price = 100.0
    discount_pct = 20.0
    
    # Act: Execute the function being tested
    result = calculate_discount(price, discount_pct)
    
    # Assert: Verify the expected outcome
    assert result == 20.0
```

---

## 4. Security Rules

### 4.1 Secrets Management
- **No Hardcoded Secrets**: Never commit API keys, passwords, or tokens
- **Environment Variables**: Use .env files for configuration
- **Git Ignore**: Ensure .env files are in .gitignore
- **Secret Rotation**: Rotate secrets regularly

```python
# ✅ Good
api_key = os.getenv("OPENROUTER_API_KEY")

# ❌ Bad
api_key = "sk-or-v1-abc123..."
```

### 4.2 Input Validation
- **Always Validate**: Validate all user inputs
- **Sanitize**: Sanitize inputs before use
- **Parameterize**: Use parameterized queries for SQL

```python
# ✅ Good
def get_listing(listing_id: int) -> Dict:
    if not isinstance(listing_id, int) or listing_id < 1:
        raise ValueError("Invalid listing ID")
    query = "SELECT * FROM listings WHERE id = ?"
    return execute_query(query, (listing_id,))

# ❌ Bad
def get_listing(listing_id):
    query = f"SELECT * FROM listings WHERE id = {listing_id}"
    return execute_query(query)
```

### 4.3 Dependencies
- **Keep Updated**: Regularly update dependencies
- **Security Scans**: Run security scans before deployment
- **Review Changes**: Review dependency changes in PRs

---

## 5. Documentation Rules

### 5.1 Required Documentation
- **README.md**: Project overview and quick start
- **CONTRIBUTING.md**: How to contribute
- **CHANGELOG.md**: Version history
- **API Docs**: Complete API documentation
- **Code Comments**: Complex logic must be commented

### 5.2 Documentation Standards
- **Markdown**: Use Markdown for all documentation
- **Clear Language**: Write in clear, concise English
- **Code Examples**: Include working code examples
- **Keep Updated**: Update docs with code changes

### 5.3 README Structure
```markdown
# Project Title
Brief description

## Features
Key features list

## Installation
Step-by-step installation

## Usage
Basic usage examples

## API Reference
Link to API docs

## Contributing
Link to CONTRIBUTING.md

## License
License information
```

---

## 6. API Design Rules

### 6.1 RESTful Principles
- **Resources**: Use nouns for endpoints
- **Methods**: Use appropriate HTTP methods
- **Status Codes**: Return correct HTTP status codes
- **Versioning**: Version APIs (/api/v1/)

```python
# ✅ Good
GET    /api/v1/listings        # List listings
GET    /api/v1/listings/:id    # Get single listing
POST   /api/v1/listings        # Create listing
PUT    /api/v1/listings/:id    # Update listing
DELETE /api/v1/listings/:id    # Delete listing

# ❌ Bad
GET /api/getListings
POST /api/createNewListing
GET /api/listing-by-id?id=123
```

### 6.2 Response Format
```json
{
  "success": true,
  "data": {
    "items": [...],
    "total": 100,
    "page": 1,
    "per_page": 10
  },
  "error": null
}
```

### 6.3 Error Handling
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "INVALID_INPUT",
    "message": "Price must be a positive number",
    "details": {
      "field": "price",
      "value": -10
    }
  }
}
```

---

## 7. Performance Rules

### 7.1 Database Queries
- **Indexing**: Create indexes for frequently queried columns
- **Pagination**: Always paginate large result sets
- **N+1 Queries**: Avoid N+1 query problems
- **Query Optimization**: Profile and optimize slow queries

### 7.2 API Performance
- **Caching**: Implement caching for expensive operations
- **Rate Limiting**: Enforce rate limits to prevent abuse
- **Compression**: Use gzip compression for responses
- **CDN**: Serve static assets via CDN

### 7.3 Frontend Performance
- **Bundle Size**: Keep bundle size under 200KB gzipped
- **Code Splitting**: Use code splitting for routes
- **Lazy Loading**: Lazy load images and components
- **Memoization**: Memoize expensive computations

---

## 8. Deployment Rules

### 8.1 Environment Separation
- **Development**: Local development environment
- **Staging**: Pre-production testing environment
- **Production**: Live production environment

### 8.2 Deployment Checklist
- [ ] All tests passing
- [ ] Code reviewed and approved
- [ ] Security scan completed
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] Monitoring configured
- [ ] Rollback plan prepared

### 8.3 Zero-Downtime Deployment
- **Blue-Green**: Use blue-green deployment strategy
- **Health Checks**: Implement health check endpoints
- **Gradual Rollout**: Roll out to subset of users first
- **Monitoring**: Monitor metrics during deployment

---

## 9. Monitoring and Observability

### 9.1 Logging
- **Structured Logging**: Use structured JSON logging
- **Log Levels**: Use appropriate log levels
- **No Secrets**: Never log sensitive information
- **Context**: Include relevant context in logs

```python
# ✅ Good
logger.info("User logged in", extra={
    "user_id": 123,
    "ip_address": "192.168.1.1",
    "timestamp": datetime.now().isoformat()
})

# ❌ Bad
print(f"User {user_id} logged in with password {password}")
```

### 9.2 Metrics
- **Key Metrics**: Track request rate, error rate, latency
- **Business Metrics**: Track business-specific metrics
- **Alerts**: Set up alerts for anomalies
- **Dashboards**: Create monitoring dashboards

### 9.3 Tracing
- **Distributed Tracing**: Implement tracing for microservices
- **Correlation IDs**: Use correlation IDs for request tracking
- **Performance**: Track performance of critical paths

---

## 10. Code Review Guidelines

### 10.1 What to Review
- **Correctness**: Does the code work as intended?
- **Design**: Is the design sound and maintainable?
- **Complexity**: Is the code unnecessarily complex?
- **Tests**: Are tests adequate and meaningful?
- **Security**: Are there security vulnerabilities?
- **Performance**: Are there performance issues?
- **Documentation**: Is documentation clear and complete?

### 10.2 Review Etiquette
- **Be Respectful**: Critique code, not people
- **Be Constructive**: Suggest improvements
- **Be Specific**: Provide specific feedback
- **Be Timely**: Review PRs within 24 hours
- **Be Thorough**: Don't rubber-stamp reviews

### 10.3 Approval Criteria
- [ ] Code follows style guidelines
- [ ] Tests are comprehensive and passing
- [ ] Documentation is updated
- [ ] No security vulnerabilities
- [ ] No performance regressions
- [ ] Changes are backwards compatible (or breaking changes documented)

---

## 11. Issue and Project Management

### 11.1 Issue Creation
- **Title**: Clear, descriptive title
- **Description**: Detailed description of issue
- **Reproduction**: Steps to reproduce (for bugs)
- **Labels**: Appropriate labels (bug, feature, etc.)
- **Priority**: Priority level (P0, P1, P2, P3)

### 11.2 Issue Labels
```
Type:
- bug: Something isn't working
- feature: New feature request
- enhancement: Improvement to existing feature
- documentation: Documentation improvements
- question: Question about the project

Priority:
- P0: Critical, blocks deployment
- P1: High priority, major impact
- P2: Medium priority, moderate impact
- P3: Low priority, minor impact

Status:
- in-progress: Currently being worked on
- blocked: Waiting on dependencies
- review: In code review
- testing: Being tested
```

### 11.3 Task Management
- **Daily Standup**: Brief daily updates
- **Sprint Planning**: Plan work in 2-week sprints
- **Retrospectives**: Reflect on process improvements
- **Task Assignment**: Clear ownership of tasks

---

## 12. Communication Guidelines

### 12.1 Channels
- **GitHub Issues**: Bug reports, feature requests
- **GitHub Discussions**: General discussions, questions
- **Pull Requests**: Code reviews, technical discussions
- **Email**: Sensitive or private matters

### 12.2 Response Times
- **Critical Issues**: < 2 hours
- **High Priority**: < 24 hours
- **Normal Priority**: < 48 hours
- **Low Priority**: < 1 week

### 12.3 Communication Best Practices
- **Be Clear**: Write clear, unambiguous messages
- **Be Concise**: Respect others' time
- **Be Professional**: Maintain professional tone
- **Be Inclusive**: Use inclusive language
- **Be Responsive**: Respond in a timely manner

---

## 13. Third-Party Integrations

### 13.1 API Usage
- **Rate Limits**: Respect rate limits
- **Terms of Service**: Follow ToS and usage policies
- **Error Handling**: Handle API errors gracefully
- **Monitoring**: Monitor API usage and costs

### 13.2 Web Scraping Ethics
- **robots.txt**: Respect robots.txt directives
- **Rate Limiting**: Don't overwhelm servers
- **User-Agent**: Use descriptive user-agent strings
- **ToS Compliance**: Comply with website terms of service

---

## 14. License and Legal

### 14.1 Code License
- **License**: MIT License
- **Attribution**: Maintain attribution in source files
- **Third-Party**: Track third-party licenses

### 14.2 Contributor Agreement
- **Original Work**: Contributors certify code is original work
- **License Agreement**: Contributors agree to MIT license
- **Rights**: Contributors retain copyright to their contributions

---

## 15. Violations and Enforcement

### 15.1 Violation Handling
1. **First Offense**: Friendly reminder
2. **Second Offense**: Formal warning
3. **Third Offense**: Temporary ban
4. **Repeated Violations**: Permanent ban

### 15.2 Reporting Violations
- **How**: Email project maintainers
- **What**: Describe the violation with evidence
- **Confidentiality**: Reports handled confidentially

---

## Appendix: Quick Reference

### Code Formatting Commands
```bash
# Python
black backend/ --line-length 100
isort backend/ --profile black
flake8 backend/ --max-line-length=100
mypy backend/

# JavaScript/TypeScript
prettier --write "**/*.{js,ts,jsx,tsx}"
eslint "**/*.{js,ts,jsx,tsx}" --fix

# SQL
sqlfluff lint database/
```

### Pre-commit Hook
```bash
# Install pre-commit
pip install pre-commit
pre-commit install

# Run on all files
pre-commit run --all-files
```

### Testing Commands
```bash
# Python
pytest tests/ --cov=backend --cov-report=html

# JavaScript
npm test
npm run test:coverage
```

---

**Version**: 1.0  
**Last Updated**: 2024-12-15  
**Maintained By**: Project Maintainers

**Note**: These rules are living documents and may be updated as the project evolves. Contributors are expected to stay current with the latest version.
