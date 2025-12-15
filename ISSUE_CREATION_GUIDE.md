# GitHub Issue and Project Creation Guide

This guide walks you through creating GitHub issues and projects from the TASKS.md file.

## 📋 Prerequisites

1. **GitHub CLI installed**: 
   ```bash
   # Check if gh is installed
   gh --version
   
   # If not installed, install it:
   # macOS
   brew install gh
   
   # Linux
   curl -sS https://webi.sh/gh | sh
   
   # Windows
   winget install GitHub.cli
   ```

2. **GitHub CLI authenticated**:
   ```bash
   # Login to GitHub
   gh auth login
   
   # Verify authentication
   gh auth status
   ```

3. **Repository access**:
   Ensure you have write access to the repository to create issues and projects.

## 🚀 Quick Start

### Option 1: Create Issues Only

Create a few test issues first:
```bash
# Test with dry-run (preview only)
python scripts/create_github_issues.py --dry-run --max-issues 5

# Create first 10 issues
python scripts/create_github_issues.py --max-issues 10

# Create all issues (136 tasks!)
python scripts/create_github_issues.py
```

### Option 2: Create Issues and Project

**Note**: GitHub Projects v2 API requires additional setup. We'll create the project manually through the UI and link issues via script or manually.

```bash
# Create issues
python scripts/create_github_issues.py

# Then manually create project and link issues (see below)
```

## 📝 Detailed Steps

### Step 1: Preview the Issues

Always start with a dry-run to see what will be created:

```bash
cd /home/runner/work/arbfinder-suite/arbfinder-suite
python scripts/create_github_issues.py --dry-run --max-issues 10
```

This will show you:
- Issue titles
- Labels that will be applied
- Number of issues that would be created

### Step 2: Create a Batch of Issues

Start with a small batch to ensure everything works:

```bash
# Create first 10 issues
python scripts/create_github_issues.py --max-issues 10
```

Check the created issues on GitHub:
```bash
gh issue list --limit 10
```

### Step 3: Review and Adjust

Review the created issues:
1. Check that labels are appropriate
2. Verify issue descriptions are clear
3. Make any manual adjustments needed

### Step 4: Create Remaining Issues

Once satisfied with the first batch:

```bash
# Create all remaining issues
python scripts/create_github_issues.py
```

**Note**: This creates 136 issues! Make sure this is what you want.

### Step 5: Create GitHub Project v2

#### Via GitHub Web UI (Recommended)

1. Go to repository on GitHub
2. Click "Projects" tab
3. Click "New project"
4. Choose "Board" template
5. Name it "ArbFinder Suite Roadmap"
6. Configure columns:
   - 📥 Backlog
   - 📝 Todo
   - 🏗️ In Progress
   - 👀 In Review
   - ✅ Done

#### Via GitHub CLI

```bash
# Create a new project
gh project create \
  --owner cbwinslow \
  --title "ArbFinder Suite Roadmap" \
  --body "Tracking development tasks for ArbFinder Suite"

# List projects to get the project number
gh project list --owner cbwinslow
```

### Step 6: Add Issues to Project

#### Bulk Add (Recommended)

```bash
# Get project number from previous step
PROJECT_NUMBER=1  # Replace with actual number

# Add all open issues to project
gh issue list --limit 200 --json number,url --jq '.[] | .url' | \
while read issue_url; do
  gh project item-add $PROJECT_NUMBER --owner cbwinslow --url "$issue_url"
  echo "Added: $issue_url"
done
```

#### Manual Add (For specific issues)

```bash
# Add specific issue to project
gh project item-add PROJECT_NUMBER \
  --owner cbwinslow \
  --url https://github.com/cbwinslow/arbfinder-suite/issues/123
```

#### Via Web UI

1. Open the project
2. Click "+" in a column
3. Search for issues
4. Click to add them

### Step 7: Configure Project Views

1. **Board View**: Already configured with columns
2. **Table View**: 
   - Add columns for Priority, Component, Effort
   - Enable sorting and filtering
3. **Roadmap View**:
   - Set up milestones
   - Configure date ranges

### Step 8: Set Up Custom Fields

Add custom fields to enhance tracking:

1. **Priority** (Single select)
   - Critical, High, Medium, Low

2. **Component** (Single select)
   - Backend, Frontend, TUI, CLI, API, Database, etc.

3. **Effort** (Single select)
   - S, M, L, XL

4. **Sprint** (Text)
   - Sprint number or version

5. **Status** (Single select)
   - Not Started, In Progress, Blocked, In Review, Done

## 🔧 Advanced Usage

### Filtering Issues Before Creation

Edit `TASKS.md` to include only specific tasks, then run:

```bash
python scripts/create_github_issues.py --tasks-file TASKS_FILTERED.md
```

### Creating Issues for Specific Categories

Extract specific sections from TASKS.md:

```bash
# Create a filtered version with only high priority tasks
grep -A 50 "🔴 High Priority" TASKS.md > TASKS_HIGH_PRIORITY.md

# Create issues from filtered file
python scripts/create_github_issues.py --tasks-file TASKS_HIGH_PRIORITY.md
```

### Updating Existing Issues

If you need to update existing issues in bulk:

```bash
# List all issues
gh issue list --limit 200 --json number,title

# Update specific issues
gh issue edit 123 --add-label "priority: high"
gh issue edit 123 --milestone "v0.5.0"
```

### Organizing with Milestones

Create milestones for major releases:

```bash
# Create milestone
gh api repos/cbwinslow/arbfinder-suite/milestones \
  -f title="v0.5.0 - Enhanced Providers" \
  -f description="Add Reverb and Mercari providers" \
  -f due_on="2026-03-31T00:00:00Z"

# Assign issues to milestone
gh issue edit 123 --milestone "v0.5.0"
```

## 📊 Post-Creation Tasks

### 1. Triage and Prioritize

Review all created issues:
```bash
gh issue list --label "needs-triage" --limit 100
```

For each issue:
- Verify labels are correct
- Add priority if not set
- Assign to milestone if applicable
- Add to project if not already added

### 2. Set Up Automation

The workflow files already created will:
- Auto-label new issues
- Welcome first-time contributors
- Mark stale issues
- Auto-close old stale issues

### 3. Create Milestones

Based on TASKS.md milestones:
- v0.5.0 - Enhanced Providers (Q1 2026)
- v0.6.0 - Notifications & Alerts (Q2 2026)
- v0.7.0 - Mobile Apps (Q3 2026)
- v1.0.0 - Production Ready (Q4 2026)

### 4. Assign Issues

Distribute work:
```bash
# Assign issue to user
gh issue edit 123 --add-assignee username

# Assign multiple issues
for issue in 123 124 125; do
  gh issue edit $issue --add-assignee username
done
```

## 🎯 Best Practices

### Issue Creation
- Start with a small batch (10-20 issues)
- Review and adjust before creating all
- Use dry-run mode liberally
- Keep TASKS.md up to date

### Project Management
- Use projects for sprint planning
- Keep board columns up to date
- Review backlog regularly
- Update issue statuses promptly

### Labels
- Use consistent label schemes
- Don't over-label (3-5 labels per issue)
- Create label taxonomy documentation
- Use automation for common labels

### Milestones
- Align with release schedule
- Don't overcommit
- Review milestone progress weekly
- Close milestones when complete

## 🐛 Troubleshooting

### Issue: gh command not found
```bash
# Install GitHub CLI
curl -sS https://webi.sh/gh | sh
```

### Issue: Authentication failed
```bash
# Re-authenticate
gh auth logout
gh auth login
```

### Issue: Permission denied
- Ensure you have write access to repository
- Check that you're authenticated as correct user
- Verify organization permissions

### Issue: Too many issues created
- You can bulk close issues if needed:
```bash
# Close multiple issues (BE CAREFUL!)
for issue in {100..136}; do
  gh issue close $issue
done
```

### Issue: Project not accessible
- Ensure project is public or you have access
- Verify project number is correct
- Check organization settings

## 📚 Additional Resources

- [GitHub CLI Manual](https://cli.github.com/manual/)
- [GitHub Projects Docs](https://docs.github.com/en/issues/planning-and-tracking-with-projects)
- [GitHub Issues Docs](https://docs.github.com/en/issues)
- [TASKS.md](TASKS.md) - Source task list
- [PROJECT_MANAGEMENT.md](PROJECT_MANAGEMENT.md) - Project management guide
- [GITHUB_FEATURES.md](GITHUB_FEATURES.md) - GitHub features guide

## 🤝 Getting Help

- Open a [Discussion](https://github.com/cbwinslow/arbfinder-suite/discussions)
- Check existing [Issues](https://github.com/cbwinslow/arbfinder-suite/issues)
- Review [Contributing Guide](CONTRIBUTING.md)

---

**Last Updated**: 2025-12-15
