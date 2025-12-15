# Useful Prompts for ArbFinder Suite Development

This document contains a collection of proven prompts for various AI tools to help with ArbFinder Suite development.

---

## Table of Contents

1. [Code Generation Prompts](#code-generation-prompts)
2. [Code Review Prompts](#code-review-prompts)
3. [Documentation Prompts](#documentation-prompts)
4. [Testing Prompts](#testing-prompts)
5. [Debugging Prompts](#debugging-prompts)
6. [Architecture Prompts](#architecture-prompts)
7. [Refactoring Prompts](#refactoring-prompts)

---

## Code Generation Prompts

### API Endpoint Creation

```
Create a FastAPI endpoint for [FEATURE] that:
- Accepts [PARAMETERS] as input
- Validates input using Pydantic models
- Queries D1 database for [DATA]
- Returns paginated results
- Includes error handling for common cases
- Has appropriate type hints
- Follows the project's error response format
- Includes docstring with example usage

Use the existing patterns from backend/api/routes/listings.py as reference.
```

### React Component Creation

```
Create a Next.js React component for [FEATURE] that:
- Uses TypeScript with proper types
- Follows the project's component structure
- Uses Tailwind CSS for styling
- Implements loading and error states
- Is responsive (mobile, tablet, desktop)
- Uses SWR for data fetching if applicable
- Includes accessibility attributes
- Has proper prop types documented

Style: [Minimal/Modern/Professional]
Reference: frontend/components/ui/ for UI patterns
```

### CrewAI Agent Creation

```
Create a CrewAI agent for [TASK] that:
- Has a clear role and goal
- Uses appropriate tools: [LIST TOOLS]
- Integrates with OpenRouter using [MODEL]
- Returns structured JSON output
- Includes error handling
- Logs execution to LangFuse
- Has a backstory that defines its expertise
- Includes example input/output

Reference: backend/api/agents.py and crew/crewai.yaml
```

### Database Migration

```
Create a D1 database migration that:
- Adds/modifies table: [TABLE_NAME]
- Includes these columns: [COLUMNS with types]
- Has appropriate indexes for: [QUERIES]
- Includes foreign key constraints where needed
- Has a rollback/down migration
- Includes comments explaining the schema
- Follows SQLite best practices

Reference: database/cloudflare_schema.sql
```

---

## Code Review Prompts

### General Code Review

```
Review this code for:
1. Adherence to project conventions (see .github/copilot-instructions.md)
2. Security vulnerabilities
3. Performance issues
4. Error handling completeness
5. Type safety
6. Code duplication
7. Test coverage needs
8. Documentation completeness

Provide specific, actionable feedback with examples.

Code:
[PASTE CODE]
```

### Security Review

```
Perform a security review of this code, checking for:
- SQL injection vulnerabilities
- XSS vulnerabilities
- Insecure data handling
- Missing input validation
- Exposed secrets or API keys
- Weak authentication/authorization
- Missing rate limiting
- Insecure dependencies
- CORS misconfiguration
- Missing security headers

Provide severity levels (Critical/High/Medium/Low) and remediation steps.

Code:
[PASTE CODE]
```

### Performance Review

```
Analyze this code for performance issues:
- Database query efficiency (N+1 problems, missing indexes)
- Unnecessary API calls
- Blocking operations
- Memory leaks
- Inefficient algorithms
- Missing caching opportunities
- Large payload sizes
- Unoptimized loops

Suggest specific optimizations with estimated impact.

Code:
[PASTE CODE]
```

---

## Documentation Prompts

### API Documentation

```
Generate OpenAPI/Swagger documentation for this endpoint:

[PASTE ENDPOINT CODE]

Include:
- Clear description
- Request/response examples
- Error responses with codes
- Parameter descriptions
- Security requirements
- Rate limiting info
```

### Code Documentation

```
Generate comprehensive documentation for this function/class:

[PASTE CODE]

Include:
- Purpose and overview
- Parameters with types and descriptions
- Return value with type
- Exceptions that may be raised
- Usage examples
- Related functions/classes
- Performance considerations if applicable

Style: Google docstring format for Python, JSDoc for TypeScript
```

### README Section

```
Write a README section for [FEATURE] that includes:
- Overview of the feature
- Why it's useful
- How to use it (with examples)
- Configuration options
- Common issues and solutions
- Links to related documentation

Target audience: [Developers/Users/Both]
Tone: [Technical/Friendly/Professional]
```

---

## Testing Prompts

### Unit Test Generation

```
Generate comprehensive unit tests for this function/class:

[PASTE CODE]

Requirements:
- Use pytest for Python or Jest for TypeScript
- Test happy path and edge cases
- Test error conditions
- Mock external dependencies
- Aim for 90%+ coverage
- Include docstrings explaining what each test verifies
- Follow AAA pattern (Arrange, Act, Assert)

Reference: tests/ directory for existing test patterns
```

### Integration Test Generation

```
Create integration tests for this workflow:

Workflow: [DESCRIBE WORKFLOW]
Components involved: [LIST COMPONENTS]

Requirements:
- Test end-to-end flow
- Use test database/fixtures
- Clean up after tests
- Test success and failure scenarios
- Verify data consistency
- Test concurrent operations if applicable

Framework: pytest for Python, Playwright for E2E
```

### Test Data Generation

```
Generate realistic test data for [ENTITY]:

Schema: [PASTE SCHEMA/MODEL]

Requirements:
- Create [N] test records
- Include edge cases (empty strings, nulls, max values, etc.)
- Realistic values that look like production data
- Valid and invalid data for validation testing
- Data in multiple formats (JSON, Python dict, SQL INSERT)
```

---

## Debugging Prompts

### Error Analysis

```
Analyze this error and provide debugging guidance:

Error message:
[PASTE ERROR]

Stack trace:
[PASTE STACK TRACE]

Context:
- What I was trying to do: [DESCRIPTION]
- Environment: [Development/Staging/Production]
- Recent changes: [DESCRIPTION]

Provide:
1. Root cause analysis
2. Step-by-step debugging approach
3. Potential fixes with code examples
4. How to prevent this in the future
```

### Performance Debugging

```
This code is slower than expected. Help me identify the bottleneck:

Code:
[PASTE CODE]

Observations:
- Expected time: [X]
- Actual time: [Y]
- Input size: [DESCRIPTION]
- Environment: [DESCRIPTION]

Suggest:
1. Where to add profiling/logging
2. Likely bottlenecks
3. How to measure performance
4. Optimization strategies
```

### Database Query Optimization

```
Optimize this slow database query:

Query:
[PASTE SQL]

Context:
- Table sizes: [DESCRIPTION]
- Current indexes: [LIST]
- Execution time: [X]ms
- Query frequency: [HIGH/MEDIUM/LOW]

Provide:
1. EXPLAIN analysis
2. Suggested indexes
3. Query rewrite if needed
4. Expected performance improvement
```

---

## Architecture Prompts

### System Design

```
Design a system for [FEATURE] that:

Requirements:
- [LIST REQUIREMENTS]

Constraints:
- Must use Cloudflare Workers
- Must integrate with existing D1 database
- Must handle [X] requests/second
- Budget: [X]/month

Provide:
1. High-level architecture diagram (ASCII art)
2. Component breakdown
3. Data flow
4. Technology choices with justification
5. Scalability considerations
6. Cost estimates
```

### API Design

```
Design a RESTful API for [RESOURCE]:

Operations needed:
- [LIST OPERATIONS]

Requirements:
- RESTful conventions
- Proper HTTP status codes
- Pagination for list endpoints
- Filtering and sorting
- Error responses
- Rate limiting strategy
- Versioning strategy

Provide:
1. Endpoint URLs
2. Request/response formats
3. Authentication approach
4. Example curl commands
```

### Database Schema Design

```
Design a database schema for [FEATURE]:

Entities:
- [LIST ENTITIES with attributes]

Requirements:
- SQLite/D1 compatibility
- Efficient querying for [USE CASES]
- Data integrity
- Scalable to [X] records

Provide:
1. CREATE TABLE statements
2. Indexes needed
3. Relationships (foreign keys)
4. Constraints
5. Example queries
```

---

## Refactoring Prompts

### Code Refactoring

```
Refactor this code to improve [readability/performance/maintainability]:

[PASTE CODE]

Requirements:
- Maintain exact same functionality
- Improve [SPECIFIC ASPECT]
- Follow project conventions
- Add comments explaining changes
- Ensure backward compatibility if it's a public API

Explain the improvements made.
```

### Extract Function

```
Refactor this code by extracting reusable functions:

[PASTE CODE]

Identify:
- Repeated logic that can be extracted
- Appropriate function names
- Function signatures with types
- Where to place the functions
- Update call sites

Maintain current behavior exactly.
```

### Simplify Complex Logic

```
Simplify this complex conditional/logic:

[PASTE CODE]

Make it more readable by:
- Reducing nesting
- Using early returns
- Extracting conditions to well-named variables
- Breaking into smaller functions if needed
- Adding comments for remaining complexity

Maintain exact same behavior.
```

---

## Prompt Templates

### General Template

```
Context:
- Project: ArbFinder Suite (price arbitrage finder)
- Tech stack: Python/FastAPI, Next.js, Cloudflare, AI agents
- See .github/copilot-instructions.md for conventions

Task: [DESCRIBE TASK]

Requirements:
- [LIST REQUIREMENTS]

Constraints:
- [LIST CONSTRAINTS]

Expected output:
- [DESCRIBE OUTPUT]

Reference:
- [RELEVANT FILES/DOCS]
```

### Code Modification Template

```
File: [FILE_PATH]

Current code:
[PASTE CODE]

Desired change:
[DESCRIBE CHANGE]

Requirements:
- Maintain backward compatibility: [YES/NO]
- Update tests: [YES/NO]
- Update documentation: [YES/NO]
- Follow project conventions: [YES - see .github/copilot-instructions.md]

Provide:
1. Modified code
2. Explanation of changes
3. Any necessary test updates
4. Migration steps if needed
```

---

## Tips for Using These Prompts

1. **Be Specific**: Replace placeholders like [FEATURE] with actual details
2. **Provide Context**: Reference relevant files and documentation
3. **Include Examples**: Show existing patterns to follow
4. **Set Constraints**: Mention technical constraints upfront
5. **Iterate**: Refine prompts based on results
6. **Save Working Prompts**: Add successful variations back to this file

---

## Model-Specific Variations

See [MODEL_PROMPTS.md](MODEL_PROMPTS.md) for prompts optimized for specific models (GPT-4, Claude, Llama, etc.).

---

**Last Updated**: 2025-12-15  
**Maintained By**: Development Team  
**Contributions Welcome**: Add your successful prompts via PR!
