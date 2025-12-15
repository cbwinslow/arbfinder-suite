# AI Automation Scripts

This directory contains AI-powered automation scripts for software development tasks.

## Scripts Overview

### CrewAI Development Crew (`crewai_dev_crew.py`)
Runs a crew of AI agents specialized in software development:
- **Research Agent**: Analyzes codebase and identifies improvements
- **Developer Agent**: Implements code changes
- **Tester Agent**: Writes comprehensive tests
- **Reviewer Agent**: Reviews all changes

**Usage:**
```bash
python scripts/crewai_dev_crew.py \
  --task "Improve error handling" \
  --priority high \
  --output crew-output.json
```

### AI Code Analyzer (`ai_code_analyzer.py`)
Analyzes code and suggests improvements:
- Detects long functions
- Finds missing docstrings
- Identifies broad exception handling
- Suggests refactoring opportunities

**Usage:**
```bash
python scripts/ai_code_analyzer.py \
  --target backend \
  --output analysis-report.json
```

### AI Test Generator (`ai_test_generator.py`)
Automatically generates test cases for uncovered code:
- Analyzes existing code
- Generates test templates
- Creates pytest-compatible tests

**Usage:**
```bash
python scripts/ai_test_generator.py \
  --target backend \
  --output tests
```

### AI Documentation Generator (`ai_doc_generator.py`)
Generates API documentation from code:
- Extracts docstrings
- Creates markdown documentation
- Generates index of all modules

**Usage:**
```bash
python scripts/ai_doc_generator.py \
  --input backend \
  --output docs/api
```

### Research Agent (`research_agent.py`)
Researches best practices and generates recommendations:
- Code quality improvements
- Testing strategies
- Performance optimizations
- Security best practices

**Usage:**
```bash
python scripts/research_agent.py \
  --topic "code improvements" \
  --output research-report.md
```

### Implementation Agent (`implementation_agent.py`)
Implements code improvements based on research findings.

**Usage:**
```bash
python scripts/implementation_agent.py \
  --research research-report.md \
  --target backend
```

### Testing Agent (`testing_agent.py`)
Generates comprehensive tests to achieve coverage targets.

**Usage:**
```bash
python scripts/testing_agent.py \
  --source backend \
  --output tests \
  --coverage-target 80
```

### Review Agent (`review_agent.py`)
Reviews code changes and provides detailed feedback.

**Usage:**
```bash
python scripts/review_agent.py \
  --target backend \
  --output review-report.md
```

### Workflow Improvement Script (`improve_workflows.py`)
Analyzes and improves GitHub Actions workflows:
- Updates outdated actions
- Adds caching
- Adds concurrency controls

**Usage:**
```bash
python scripts/improve_workflows.py \
  --input .github/workflows \
  --output .github/workflows-improved
```

### GitHub Issue Creator (`create_github_issues.py`)
Creates GitHub issues and projects from TASKS.md:
- Parses TASKS.md to extract tasks
- Creates properly labeled issues
- Optionally creates GitHub Project v2
- Supports dry-run mode for preview

**Usage:**
```bash
# Preview what would be created
python scripts/create_github_issues.py --dry-run

# Create first 10 issues
python scripts/create_github_issues.py --max-issues 10

# Create all issues and a project
python scripts/create_github_issues.py --project

# Specify custom repo and tasks file
python scripts/create_github_issues.py --repo owner/repo --tasks-file path/to/tasks.md
```

**Options:**
- `--dry-run` - Preview without creating
- `--project` - Create GitHub Project v2 and link issues
- `--max-issues N` - Limit number of issues to create
- `--repo OWNER/REPO` - Specify repository
- `--tasks-file PATH` - Path to tasks file (default: TASKS.md)

## Requirements

These scripts require the following packages:
```bash
pip install crewai openai langchain
```

Some scripts work without AI integration and will provide placeholder functionality.

## Environment Variables

For AI-powered features, set:
```bash
export OPENAI_API_KEY=your-api-key
```

## Integration with GitHub Actions

These scripts are automatically run by various GitHub Actions workflows:
- `ai-code-improvement.yml` - Daily code improvements
- `crewai-development.yml` - Weekly development tasks
- `self-improvement.yml` - Weekly CI/CD improvements

## Contributing

To add a new automation script:
1. Create the script in this directory
2. Make it executable: `chmod +x scripts/your_script.py`
3. Add documentation to this README
4. Create a corresponding GitHub Actions workflow if needed

## License

MIT
