# AI-Powered Development Quick Start

This guide will help you get started with the AI-powered automation features in ArbFinder Suite.

## What Are These Features?

The ArbFinder Suite includes AI-powered workflows and scripts that can:
- **Analyze your code** and suggest improvements
- **Generate tests** automatically for uncovered code
- **Create documentation** from your code
- **Review pull requests** automatically
- **Improve CI/CD workflows** themselves
- **Run a crew of AI developers** to work on tasks

## Prerequisites

### Required
- Python 3.9 or higher
- pip package manager
- GitHub repository with Actions enabled

### Optional (for AI features)
- OpenAI API key (for full AI capabilities)
- GitHub Copilot (complementary tool)

## Quick Setup

### 1. Install Dependencies

```bash
# Install base dependencies
pip install -e ".[dev,test]"

# Install AI dependencies (optional)
pip install crewai openai langchain
```

### 2. Configure Secrets (Optional)

If you want to use AI features, add your OpenAI API key:

**GitHub (for Actions):**
1. Go to repository Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `OPENAI_API_KEY`
4. Value: Your OpenAI API key

**Local (for testing):**
```bash
export OPENAI_API_KEY=your-api-key-here
```

## Using AI Features

### Without OpenAI API Key

All scripts work in "placeholder mode" without an API key. They'll provide:
- Basic static analysis
- Template generation
- Structural improvements
- Rule-based suggestions

### With OpenAI API Key

With an API key, you get:
- AI-powered code analysis
- Intelligent test generation
- Context-aware documentation
- Advanced code suggestions
- CrewAI development crews

## Running Scripts Locally

### 1. Code Analysis

Analyze your code for improvements:

```bash
python scripts/ai_code_analyzer.py \
  --target backend \
  --output analysis-report.json
```

**Output:**
- JSON report with issues found
- Suggestions for improvements
- Statistics on code quality

**Example output:**
```
🔍 Analyzing code in: backend
✅ Analysis complete!
📊 Files analyzed: 5
⚠️  Issues found: 43
💡 Suggestions: 2
```

### 2. Generate Tests

Generate test templates for your code:

```bash
python scripts/ai_test_generator.py \
  --target backend \
  --output tests
```

**What it does:**
- Scans Python files
- Identifies functions without tests
- Generates pytest test templates
- Creates test files in output directory

### 3. Generate Documentation

Create API documentation:

```bash
python scripts/ai_doc_generator.py \
  --input backend \
  --output docs/api
```

**What it creates:**
- Markdown files for each module
- Function and class documentation
- Index of all modules
- API reference

### 4. Run Development Crew

Run a crew of AI agents on a task:

```bash
python scripts/crewai_dev_crew.py \
  --task "Improve error handling in API endpoints" \
  --priority high \
  --output crew-output.json
```

**The crew includes:**
- 🔍 Research Agent: Analyzes the codebase
- 💻 Developer Agent: Implements changes
- 🧪 Testing Agent: Writes tests
- 👀 Review Agent: Reviews everything

**Note:** This requires OpenAI API key.

## GitHub Actions Workflows

### Automatic Workflows

These run automatically:

1. **Daily (3 AM UTC)** - AI Code Improvement
   - Analyzes code
   - Auto-formats
   - Generates tests
   - Creates PR

2. **Weekly (Monday 9 AM UTC)** - CrewAI Development
   - Runs development crew
   - Implements improvements
   - Creates PR

3. **Weekly (Sunday Midnight UTC)** - Self-Improvement
   - Improves CI/CD itself
   - Optimizes workflows
   - Creates PR

### Manual Triggers

You can also trigger workflows manually:

1. Go to repository **Actions** tab
2. Select a workflow (e.g., "AI-Powered Code Improvement")
3. Click "Run workflow"
4. Select options if available
5. Click green "Run workflow" button

## Understanding the Results

### Pull Requests

AI workflows create PRs with:
- **Title**: 🤖 prefix indicates AI-generated
- **Labels**: `automated`, `ai-improvement`, `crewai`
- **Description**: Details what was changed
- **Artifacts**: Analysis reports and logs

### Review AI PRs

When reviewing AI-generated PRs:

1. **Check the description** - understand what was done
2. **Review changes carefully** - AI makes mistakes
3. **Run tests** - ensure nothing breaks
4. **Look at artifacts** - read analysis reports
5. **Approve or request changes**

### Artifacts

Workflows upload artifacts you can download:
- `analysis-report.json` - Code analysis results
- `crew-output.json` - CrewAI crew results
- `coverage-report` - Coverage HTML reports
- `test-results` - Test execution results

## Best Practices

### DO ✅

- **Review AI suggestions** carefully before accepting
- **Test locally** before pushing
- **Start small** - test on non-critical code first
- **Monitor costs** - OpenAI API usage has costs
- **Combine with human review** - AI assists, doesn't replace

### DON'T ❌

- **Blindly accept** AI-generated code
- **Skip testing** AI changes
- **Use in production** without review
- **Share API keys** in code or commits
- **Expect perfection** - AI makes mistakes

## Troubleshooting

### "Module not found" errors

```bash
# Make sure you're in the right directory
cd /path/to/arbfinder-suite

# Reinstall dependencies
pip install -e ".[dev,test]"
```

### "OpenAI API key not found"

```bash
# Set the environment variable
export OPENAI_API_KEY=your-key

# Or run without AI features (placeholder mode)
# Scripts will still work with basic functionality
```

### Workflows not running

1. Check you have Actions enabled in repository settings
2. Verify secrets are configured (if using AI)
3. Check workflow files syntax (YAML)
4. Review workflow run logs for errors

### High API costs

If OpenAI costs are too high:

1. **Reduce frequency** - change cron schedules
2. **Use smaller models** - modify scripts to use gpt-3.5-turbo
3. **Disable AI workflows** - comment out cron triggers
4. **Run manually only** - trigger workflows when needed

## Examples

### Example 1: Analyze and Fix Code

```bash
# 1. Analyze code
python scripts/ai_code_analyzer.py --target backend --output /tmp/analysis.json

# 2. Review analysis
cat /tmp/analysis.json

# 3. Generate tests for uncovered code
python scripts/ai_test_generator.py --target backend --output tests

# 4. Run tests
pytest tests/ -v

# 5. Commit improvements
git add tests/
git commit -m "Add generated tests"
```

### Example 2: Improve Documentation

```bash
# 1. Generate docs
python scripts/ai_doc_generator.py --input backend --output docs/api

# 2. Review generated docs
ls docs/api/

# 3. Commit docs
git add docs/api/
git commit -m "Add API documentation"
```

### Example 3: Run Development Task

```bash
# 1. Run CrewAI crew (requires API key)
python scripts/crewai_dev_crew.py \
  --task "Add input validation to all API endpoints" \
  --priority high \
  --output crew-result.json

# 2. Review results
cat crew-result.json

# 3. Test changes
pytest tests/ -v

# 4. Commit if good
git commit -am "Add input validation per CrewAI suggestions"
```

## Learning More

- **Full documentation**: See `docs/CI_CD_AUTOMATION.md`
- **Script documentation**: See `scripts/README.md`
- **Workflow files**: Check `.github/workflows/` directory
- **Examples**: Browse existing PRs with 🤖 prefix

## Getting Help

If you need help:

1. Check the troubleshooting section above
2. Review workflow logs in GitHub Actions
3. Read script help: `python scripts/script_name.py --help`
4. Open an issue on GitHub
5. Check OpenAI API documentation

## What's Next?

After getting comfortable with basic features:

1. **Customize agents** - modify agent behaviors in scripts
2. **Add new workflows** - create specialized workflows
3. **Tune parameters** - adjust thresholds and settings
4. **Integrate with tools** - connect to Slack, Discord, etc.
5. **Contribute back** - share improvements with community

## Cost Considerations

### Free Tier
- GitHub Actions: 2000 minutes/month (free tier)
- AI features work without API key (limited)

### Paid Usage
- OpenAI API: ~$0.002 per 1K tokens (GPT-3.5)
- GitHub Actions: $0.008/minute (over free tier)

**Estimated monthly costs (with AI):**
- Small project (<100 files): ~$5-10/month
- Medium project (100-500 files): ~$10-30/month
- Large project (500+ files): ~$30-100/month

## Security Notes

⚠️ **Important:**
- Never commit API keys to code
- Use GitHub Secrets for sensitive data
- Review AI-generated code for security issues
- AI can introduce vulnerabilities
- Always run security scans after AI changes

## Conclusion

The AI-powered features are tools to **assist** development, not replace developers. Use them to:
- Save time on repetitive tasks
- Catch issues early
- Improve code quality
- Increase test coverage
- Maintain documentation

Start small, review carefully, and gradually increase usage as you become comfortable with the tools.

Happy automating! 🤖
