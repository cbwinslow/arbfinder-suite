# CI/CD & Automation Documentation

## Overview

This project includes a comprehensive CI/CD pipeline with AI-powered automation features. The workflows are designed to improve code quality, increase test coverage, and enable self-improvement capabilities.

## GitHub Actions Workflows

### Core CI/CD Workflows

#### 1. Enhanced CI/CD Pipeline (`ci-enhanced.yml`)
**Trigger:** Push to main/develop, Pull Requests  
**Purpose:** Comprehensive testing and quality checks

**Jobs:**
- **lint-python**: Black, isort, Flake8, MyPy, Pylint
- **lint-frontend**: ESLint, Prettier
- **test-python**: Pytest across Python 3.9-3.12 with coverage
- **test-analysis-cli**: Analysis CLI functionality tests
- **test-frontend**: Build and test frontend
- **security-scan**: Safety, Bandit for Python; npm audit for Node
- **validate-database-schema**: PostgreSQL schema validation
- **docker-build**: Docker image build and test
- **check-docs**: Markdown link checking
- **integration-tests**: Full stack integration tests

#### 2. Code Review Automation (`code-review.yml`)
**Trigger:** Pull Request events  
**Purpose:** Automated code review and quality metrics

**Jobs:**
- **automated-review**: Code complexity analysis with Radon
- **pr-size-check**: PR size labeling and warnings
- **coverage-check**: Test coverage threshold validation
- **breaking-changes**: Detection of potential breaking changes
- **docs-check**: Documentation update suggestions
- **auto-assign**: Auto-assign reviewers based on changed files

#### 3. Security Scanning (`security-scan.yml`)
**Trigger:** Push, PRs, Daily schedule, Manual  
**Purpose:** Comprehensive security vulnerability detection

**Jobs:**
- **codeql-analysis**: GitHub CodeQL for Python and JavaScript
- **dependency-review**: Dependency vulnerability scanning
- **snyk-scan**: Snyk security scanning (requires SNYK_TOKEN)
- **python-security-scan**: Safety, Bandit, pip-audit
- **semgrep-scan**: Semgrep SAST scanning
- **secret-scan**: TruffleHog and GitLeaks secret detection
- **container-scan**: Trivy and Grype container scanning
- **sql-security-check**: SQL injection pattern detection
- **license-check**: License compliance validation

#### 4. Deployment Pipeline (`deployment.yml`)
**Trigger:** Version tags (v*.*.*), Manual  
**Purpose:** Automated deployment to staging and production

**Jobs:**
- **build-and-push**: Docker image build and push to GHCR
- **deploy-staging**: Deploy to staging environment
- **deploy-production**: Deploy to production environment
- **database-migration**: Run database migrations
- **create-rollback**: Generate rollback plans
- **post-deployment-tests**: Integration and load tests
- **notify-deployment**: Deployment status notifications

### AI-Powered Workflows

#### 5. AI Code Improvement (`ai-code-improvement.yml`)
**Trigger:** Daily at 3 AM UTC, Manual  
**Purpose:** AI-powered code analysis and automatic improvements

**Jobs:**
- **ai-code-analysis**: Analyze code with AI (using `ai_code_analyzer.py`)
- **auto-format**: Automatic code formatting (black, isort, autoflake)
- **generate-tests**: Generate missing tests with AI
- **generate-docs**: Generate documentation from code
- **create-improvement-pr**: Create PR with all improvements

**Required Secrets:**
- `OPENAI_API_KEY` (optional, works without AI)

#### 6. CrewAI Development (`crewai-development.yml`)
**Trigger:** Weekly on Monday at 9 AM UTC, Manual  
**Purpose:** Run AI development crew for code improvements

**Jobs:**
- **crewai-development**: Main crew orchestration
- **research-agent**: Analyze codebase and best practices
- **implementation-agent**: Apply code improvements
- **testing-agent**: Generate comprehensive tests
- **review-agent**: Review all changes
- **create-development-pr**: Create PR with crew improvements

**CrewAI Agents:**
1. **Research Agent**: Analyzes code quality, identifies issues
2. **Implementation Agent**: Implements improvements
3. **Testing Agent**: Writes tests to achieve 80%+ coverage
4. **Review Agent**: Reviews changes and provides feedback

**Required Secrets:**
- `OPENAI_API_KEY` (required for CrewAI)

#### 7. Enhanced Test Coverage (`test-coverage.yml`)
**Trigger:** Push to main/develop, PRs, Nightly, Manual  
**Purpose:** Comprehensive testing with coverage tracking

**Jobs:**
- **unit-tests**: Unit tests across Python versions with coverage
- **integration-tests**: Integration tests with PostgreSQL
- **e2e-tests**: End-to-end tests with Playwright
- **performance-tests**: Performance benchmarks
- **load-tests**: Load testing with Locust
- **coverage-report**: Combined coverage report
- **test-summary**: Test results summary

**Coverage Threshold:** 80%

#### 8. Self-Improving CI/CD (`self-improvement.yml`)
**Trigger:** Weekly on Sunday, Manual  
**Purpose:** Analyze and improve CI/CD workflows themselves

**Jobs:**
- **analyze-workflows**: Analyze workflow files for issues
- **generate-improvements**: Generate improved workflow versions
- **improve-scripts**: Auto-improve automation scripts
- **optimize-tests**: Optimize test suite performance
- **update-documentation**: Check and update documentation
- **create-improvement-pr**: Create PR with self-improvements

### Additional Workflows

#### 9. Dependency Management (`dependency-management.yml`)
**Trigger:** Weekly, Manual  
**Purpose:** Automated dependency updates

#### 10. Documentation (`documentation.yml`)
**Trigger:** Push to docs, Manual  
**Purpose:** Documentation building and deployment

#### 11. Penetration Testing (`penetration-testing.yml`)
**Trigger:** Weekly, Manual  
**Purpose:** Security penetration testing

## Automation Scripts

All scripts are located in the `scripts/` directory and are executable.

### AI-Powered Scripts

#### `crewai_dev_crew.py`
Main CrewAI orchestration script.

```bash
python scripts/crewai_dev_crew.py \
  --task "Improve error handling" \
  --priority high \
  --output crew-output.json
```

#### `ai_code_analyzer.py`
Analyzes code and suggests improvements.

```bash
python scripts/ai_code_analyzer.py \
  --target backend \
  --output analysis-report.json
```

**Detects:**
- Long functions (>50 lines)
- Missing docstrings
- Broad exception handling
- Parse errors

#### `ai_test_generator.py`
Generates test templates for uncovered code.

```bash
python scripts/ai_test_generator.py \
  --target backend \
  --output tests
```

#### `ai_doc_generator.py`
Generates markdown documentation from code.

```bash
python scripts/ai_doc_generator.py \
  --input backend \
  --output docs/api
```

### Agent Scripts

#### `research_agent.py`
Researches best practices and generates recommendations.

```bash
python scripts/research_agent.py \
  --topic "code improvements" \
  --output research-report.md
```

#### `implementation_agent.py`
Implements improvements based on research.

```bash
python scripts/implementation_agent.py \
  --research research-report.md \
  --target backend
```

#### `testing_agent.py`
Generates comprehensive tests.

```bash
python scripts/testing_agent.py \
  --source backend \
  --output tests \
  --coverage-target 80
```

#### `review_agent.py`
Reviews code and generates report.

```bash
python scripts/review_agent.py \
  --target backend \
  --output review-report.md
```

### Infrastructure Scripts

#### `improve_workflows.py`
Analyzes and improves GitHub Actions workflows.

```bash
python scripts/improve_workflows.py \
  --input .github/workflows \
  --output .github/workflows-improved
```

**Improvements:**
- Updates outdated actions
- Adds caching
- Adds concurrency controls

## Setup Instructions

### 1. Required Secrets

Add these secrets to your GitHub repository:

```
OPENAI_API_KEY      # For AI-powered features (optional)
SNYK_TOKEN          # For Snyk security scanning (optional)
CODECOV_TOKEN       # For Codecov integration (optional)
DATABASE_URL        # For deployment (required for production)
STRIPE_SECRET_KEY   # For payment features (optional)
```

### 2. Install Dependencies

For AI features:
```bash
pip install crewai openai langchain
```

For all development:
```bash
pip install -e ".[dev,test]"
```

### 3. Environment Variables

Create `.env` file:
```bash
OPENAI_API_KEY=your-api-key-here
ARBF_DB=/path/to/database.db
```

### 4. Run Locally

Test scripts locally before workflows run them:

```bash
# Test code analyzer
python scripts/ai_code_analyzer.py --target backend --output /tmp/analysis.json

# Test test generator
python scripts/ai_test_generator.py --target backend --output tests

# Test doc generator
python scripts/ai_doc_generator.py --input backend --output docs/api
```

## Workflow Scheduling

- **Daily (3 AM UTC)**: AI Code Improvement
- **Nightly (Midnight UTC)**: Enhanced Test Coverage
- **Weekly Monday (9 AM UTC)**: CrewAI Development
- **Weekly Sunday (Midnight UTC)**: Self-Improvement
- **Weekly (2 AM UTC)**: Security Scanning
- **Weekly**: Dependency Management, Penetration Testing

## Coverage Goals

- **Current**: 24%
- **Target**: 80%
- **Threshold in CI**: 80%

Coverage is tracked across:
- Unit tests
- Integration tests
- E2E tests
- All Python versions (3.9, 3.10, 3.11, 3.12)

## Best Practices

### For Contributors

1. **Before Committing:**
   - Run `make test` to run tests locally
   - Run `make lint` to check code quality
   - Run `make format` to auto-format code

2. **Pull Requests:**
   - Keep PRs small (<1000 lines)
   - Ensure all tests pass
   - Maintain or improve coverage
   - Add tests for new features

3. **AI Features:**
   - Test locally before pushing
   - Review AI-generated code carefully
   - Don't blindly accept AI suggestions

### For Maintainers

1. **Security:**
   - Review Dependabot PRs promptly
   - Check security scan results weekly
   - Rotate secrets regularly

2. **Performance:**
   - Monitor workflow execution times
   - Optimize slow tests
   - Use caching effectively

3. **Costs:**
   - Monitor GitHub Actions minutes
   - Review AI API usage (OpenAI costs)
   - Optimize workflow triggers

## Troubleshooting

### Workflows Failing

1. **Check workflow logs** in GitHub Actions tab
2. **Verify secrets** are configured correctly
3. **Test scripts locally** to reproduce issues
4. **Check for rate limiting** if using external APIs

### AI Features Not Working

1. **Verify OPENAI_API_KEY** is set
2. **Check API quotas** and billing
3. **Test without AI** - scripts work in placeholder mode
4. **Review CrewAI logs** for detailed error messages

### Tests Failing

1. **Run tests locally**: `pytest tests/ -v`
2. **Check database** initialization
3. **Verify dependencies** are installed
4. **Check Python version** compatibility

## Monitoring

### GitHub Actions

- View all workflows: Repository → Actions tab
- Monitor success rates
- Check execution times
- Review artifact sizes

### Coverage Reports

- Codecov dashboard (if configured)
- Coverage HTML reports in artifacts
- PR comments with coverage changes

### Security Alerts

- Security tab in GitHub
- Dependabot alerts
- CodeQL findings
- Secret scanning alerts

## Future Enhancements

- [ ] Add more AI agents for specialized tasks
- [ ] Implement cost tracking for AI API usage
- [ ] Add workflow optimization suggestions
- [ ] Create dashboard for CI/CD metrics
- [ ] Add more E2E test scenarios
- [ ] Implement canary deployments
- [ ] Add A/B testing infrastructure
- [ ] Create mobile app testing workflows

## Contributing

To add new workflows or scripts:

1. Create the workflow/script
2. Test locally
3. Add documentation here
4. Submit PR with tests
5. Update this README

## License

MIT License - See LICENSE file for details
