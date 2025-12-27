# Creating GitHub Issues from TASKS.md

This guide explains how to systematically create GitHub issues from the tasks documented in [TASKS.md](TASKS.md).

## 📋 Overview

The [TASKS.md](TASKS.md) file contains a comprehensive list of identified tasks, features, and improvements for ArbFinder Suite. This document provides a step-by-step guide to convert these tasks into well-structured GitHub issues.

## 🎯 Why Create Issues?

Creating GitHub issues from tasks provides several benefits:

1. **Tracking**: Track progress on individual tasks
2. **Organization**: Organize work into manageable units
3. **Collaboration**: Enable team collaboration and assignment
4. **Visibility**: Make work visible to contributors
5. **Planning**: Link issues to milestones and project boards
6. **Discussion**: Facilitate discussion around specific tasks

## 🚀 Quick Start

### Method 1: Manual Creation (Recommended for Start)

1. **Navigate to Issues**: Go to https://github.com/cbwinslow/arbfinder-suite/issues
2. **Click "New Issue"**: Select the appropriate template:
   - Bug Report (for issues marked as bugs)
   - Feature Request (for new features)
   - Task/Enhancement (for development tasks)
3. **Fill in Details**: Use information from TASKS.md
4. **Add Labels**: Apply appropriate labels
5. **Link to Project**: Add to "ArbFinder Suite Development" project

### Method 2: Using GitHub CLI

Install GitHub CLI and authenticate:

```bash
# Install gh CLI (if not already installed)
# macOS: brew install gh
# Linux: See https://cli.github.com/

# Authenticate
gh auth login

# Create an issue
gh issue create \
  --title "Add Reverb marketplace provider" \
  --body "Implement Reverb provider for both sold and live listings.

## Description
Reverb is a popular marketplace for musical instruments and gear.

## Acceptance Criteria
- [ ] Implement Reverb API integration
- [ ] Support sold listings
- [ ] Support live listings
- [ ] Add tests
- [ ] Update documentation

See TASKS.md for more details." \
  --label "enhancement,area: backend,priority: high" \
  --project "ArbFinder Suite Development"
```

### Method 3: Using Scripts

Create a script to batch-create issues (see example below).

## 📝 Issue Creation Template

When creating issues from TASKS.md, use this structure:

### Title Format
```
[Component] Brief description
```

Examples:
- `[Backend] Add Reverb marketplace provider`
- `[TUI] Implement search trigger functionality`
- `[Testing] Increase test coverage to 80%+`

### Description Format

```markdown
## Description
[Detailed description of the task]

## Motivation
[Why this task is important]

## Related Tasks
- Relates to #[issue_number]
- Depends on #[issue_number]

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Tests added
- [ ] Documentation updated

## Technical Notes
[Any implementation details or considerations]

## Resources
- [TASKS.md](TASKS.md)
- [Relevant documentation]
```

## 🏷️ Label Guidelines

Apply labels consistently:

### Required Labels

Every issue should have:
1. **Type**: `bug`, `enhancement`, `task`, or `documentation`
2. **Component**: `area: backend`, `area: frontend`, `area: tui`, etc.
3. **Priority**: `priority: high`, `priority: medium`, or `priority: low`

### Optional Labels

Add when applicable:
- `good first issue` - For beginner-friendly tasks
- `help wanted` - When seeking contributors
- `blocked` - When dependent on other work
- `breaking-change` - For breaking changes
- `security` - For security-related work

## 📊 Organizing Issues

### Priority Levels

#### High Priority
Create issues immediately for:
- Provider enhancements (Reverb, Mercari)
- Testing improvements (80%+ coverage)
- Critical TUI implementations
- Security issues

#### Medium Priority
Create over next 1-2 weeks:
- Feature enhancements
- AI integration
- API improvements
- Export/import features

#### Low Priority
Create as time permits:
- UI/UX improvements
- Platform expansion
- Nice-to-have features

### Milestones

Assign issues to milestones:

- **v0.5.0**: High-priority items, due in 2-3 months
- **v1.0.0**: Medium-priority items, due in 4-6 months
- **v2.0.0**: Long-term items, due in 6+ months
- **Backlog**: No immediate timeline

### Project Board

Add all issues to the project board:

1. **Backlog**: New issues not yet prioritized
2. **To Do**: Prioritized and ready to work on
3. **In Progress**: Currently being worked on
4. **In Review**: PRs under review
5. **Done**: Completed items

## 🤖 Batch Creation Script

Create multiple issues at once using this Python script:

```python
#!/usr/bin/env python3
"""
Script to create GitHub issues from TASKS.md
Requires: pip install PyGithub
"""

import os
from github import Github

# Configuration
REPO_NAME = "cbwinslow/arbfinder-suite"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Initialize GitHub client
g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

# High priority tasks to create
high_priority_tasks = [
    {
        "title": "[Backend] Add Reverb marketplace provider",
        "body": """## Description
Implement Reverb API integration for both sold and live listings.

## Motivation
Reverb is a major marketplace for musical instruments and gear, providing valuable price data.

## Acceptance Criteria
- [ ] Implement Reverb API client
- [ ] Support sold listings search
- [ ] Support live listings search
- [ ] Add error handling and rate limiting
- [ ] Add unit tests
- [ ] Update documentation

## Resources
- Reverb API: https://reverb.com/page/api
- TASKS.md entry for Reverb provider
""",
        "labels": ["enhancement", "area: backend", "priority: high"],
    },
    {
        "title": "[Backend] Add Mercari marketplace provider",
        "body": """## Description
Implement Mercari scraper for both sold and live listings.

## Motivation
Mercari is a popular peer-to-peer marketplace with valuable pricing data.

## Acceptance Criteria
- [ ] Implement Mercari scraper
- [ ] Support sold listings search
- [ ] Support live listings search
- [ ] Respect robots.txt and rate limits
- [ ] Add unit tests
- [ ] Update documentation

## Technical Notes
- May need to use headless browser for JavaScript-heavy pages
- Be respectful of ToS

## Resources
- TASKS.md entry for Mercari provider
""",
        "labels": ["enhancement", "area: backend", "priority: high"],
    },
    {
        "title": "[Testing] Increase test coverage to 80%+",
        "body": """## Description
Improve test coverage across the codebase to reach 80% or higher.

## Motivation
Higher test coverage improves code quality and reduces bugs.

## Current Coverage
- Check current coverage with: `pytest --cov=backend --cov-report=html`

## Acceptance Criteria
- [ ] Backend coverage >= 80%
- [ ] Frontend coverage >= 70%
- [ ] Add integration tests
- [ ] Add E2E tests
- [ ] Update CI to enforce coverage thresholds

## Resources
- TASKS.md testing section
""",
        "labels": ["testing", "area: testing", "priority: high"],
    },
    # Add more tasks here...
]

# Create issues
for task in high_priority_tasks:
    try:
        issue = repo.create_issue(
            title=task["title"],
            body=task["body"],
            labels=task["labels"]
        )
        print(f"✅ Created issue #{issue.number}: {task['title']}")
    except Exception as e:
        print(f"❌ Failed to create issue '{task['title']}': {e}")

print("\n🎉 Done creating issues!")
```

### Running the Script

```bash
# Set your GitHub token
export GITHUB_TOKEN="your_github_token_here"

# Install dependencies
pip install PyGithub

# Run the script
python create_issues.py
```

## 📅 Recommended Creation Schedule

### Week 1: High Priority
- [ ] Create all high-priority issues from TASKS.md
- [ ] Assign to appropriate milestones
- [ ] Add to project board

### Week 2: Medium Priority
- [ ] Create medium-priority feature issues
- [ ] Create medium-priority enhancement issues

### Week 3: TUI and Testing
- [ ] Create all TUI implementation issues
- [ ] Create testing-related issues

### Week 4: Documentation and Low Priority
- [ ] Create documentation issues
- [ ] Create low-priority enhancement issues

## ✅ Post-Creation Checklist

After creating issues:

- [ ] All issues have appropriate labels
- [ ] Issues are added to project board
- [ ] High-priority issues assigned to milestones
- [ ] Related issues are linked
- [ ] Good first issues are marked
- [ ] Project board views are updated
- [ ] TASKS.md is updated with issue numbers

## 🔄 Keeping TASKS.md Updated

As issues are created, update TASKS.md:

1. Replace `[#TBD]` with actual issue number: `[#123]`
2. Add links: `[#123](https://github.com/cbwinslow/arbfinder-suite/issues/123)`
3. Update status when issues are completed
4. Remove items that are no longer relevant

Example:
```markdown
## Before
- [ ] Add Reverb marketplace provider [#TBD]

## After
- [ ] Add Reverb marketplace provider [#123](https://github.com/cbwinslow/arbfinder-suite/issues/123)
```

## 🤝 Collaboration Tips

### For Maintainers
1. Review and triage new issues weekly
2. Assign issues to appropriate team members
3. Update project board status
4. Link related issues
5. Add issues to milestones

### For Contributors
1. Comment on issues you want to work on
2. Wait for assignment before starting
3. Link your PR to the issue
4. Update issue status in comments
5. Ask questions early

## 📚 Resources

- [GitHub Issues Documentation](https://docs.github.com/en/issues)
- [GitHub CLI](https://cli.github.com/)
- [PyGithub Library](https://pygithub.readthedocs.io/)
- [TASKS.md](TASKS.md)
- [PROJECT_BOARD.md](PROJECT_BOARD.md)
- [CONTRIBUTING.md](../../CONTRIBUTING.md)

## 🆘 Need Help?

If you have questions about creating issues:
- Check [SUPPORT.md](SUPPORT.md)
- Ask in [GitHub Discussions](https://github.com/cbwinslow/arbfinder-suite/discussions)
- Tag maintainers in a comment

---

**Remember**: Good issues lead to good code! Take time to write clear, detailed issue descriptions.
