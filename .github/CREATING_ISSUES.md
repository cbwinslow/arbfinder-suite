# Creating Issues from TASKS.md

This guide shows how to convert tasks from [TASKS.md](../TASKS.md) into GitHub issues.

## Quick Start

### Using GitHub Web Interface

1. Go to [New Issue](https://github.com/cbwinslow/arbfinder-suite/issues/new/choose)
2. Select **"Task"** template
3. Fill in the fields from the task in TASKS.md
4. Submit the issue

### Using GitHub CLI

```bash
# Install GitHub CLI if not already installed
# https://cli.github.com/

# Authenticate
gh auth login

# Create issue from template
gh issue create \
  --title "[Task]: Increase test coverage to 50%+" \
  --label "task,priority: high,component: testing" \
  --body "See TASKS.md for details"
```

## Converting Tasks to Issues

### Example: High Priority Testing Task

From TASKS.md:
```markdown
### 🔴 Increase Test Coverage
- [ ] **Increase test coverage to 50%+** (Current: 23%)
  - Component: Testing
  - Estimated: XL (2-3 days)
  - Description: Add tests for arb_finder.py core functionality, utils.py database operations, and watch.py monitoring
  - Acceptance: Test coverage reaches 50%+ across all modules
```

Convert to GitHub Issue:

**Title**: `[Task]: Increase test coverage to 50%+`

**Task Description**:
```
Add comprehensive tests to increase overall test coverage from 23% to 50%+.

Focus on:
- arb_finder.py core functionality
- utils.py database operations
- watch.py monitoring functionality
```

**Component**: Testing

**Task Type**: Testing

**Acceptance Criteria**:
```
- [ ] Test coverage reaches 50%+ overall
- [ ] arb_finder.py has adequate test coverage
- [ ] utils.py database operations are tested
- [ ] watch.py monitoring functionality is tested
- [ ] Coverage report is generated and documented
```

**Estimated Complexity**: XL - More than 2 days

**Technical Notes**:
```
Current coverage: 23%
Target coverage: 50%+

Use pytest for testing.
Configure coverage in pyproject.toml.
Run: pytest --cov=backend --cov-report=html
```

**Labels**: `task`, `priority: high`, `component: testing`, `complexity: xl`

**Milestone**: v0.5.0

---

### Example: Medium Priority Feature

From TASKS.md:
```markdown
### 🟡 Email notifications for deals
- [ ] **Email notifications for deals**
  - Component: Backend/API
  - Estimated: M (4-8 hours)
  - Description: Send email alerts when deals meet user criteria
  - Acceptance: Users can configure email alerts for deal notifications
  - Technical: Integrate email service (SendGrid, AWS SES, etc.)
```

Convert to GitHub Issue:

**Title**: `[Task]: Add email notifications for deals`

**Task Description**:
```
Implement email notification system to alert users when deals matching their criteria are found.

Users should be able to:
- Configure email notification preferences
- Set deal criteria (price threshold, keywords, etc.)
- Receive formatted email alerts with deal details
```

**Component**: Backend/API

**Task Type**: Feature Implementation

**Acceptance Criteria**:
```
- [ ] Email notification system implemented
- [ ] User preferences for email notifications stored
- [ ] Notification triggers configured based on deal criteria
- [ ] Email templates created for deal alerts
- [ ] Emails sent successfully when deals match criteria
- [ ] Configuration documented
```

**Estimated Complexity**: M - 4-8 hours

**Dependencies**: None

**Technical Notes**:
```
Consider email service options:
- SendGrid (recommended for simplicity)
- AWS SES (cost-effective at scale)
- Mailgun (alternative)

Implementation:
- Add email service configuration to config
- Create email templates (HTML + plain text)
- Implement notification logic in watch.py
- Add user email preferences to database
- Test with real email service
```

**Labels**: `task`, `priority: medium`, `component: backend`, `complexity: m`

**Milestone**: v0.8.0

---

## Batch Issue Creation

### Using GitHub CLI Script

Create a script to batch-create issues:

```bash
#!/bin/bash
# create_issues.sh

# Test Coverage Task
gh issue create \
  --title "[Task]: Increase test coverage to 50%+" \
  --label "task,priority: high,component: testing,complexity: xl" \
  --milestone "v0.5.0" \
  --body "$(cat <<EOF
Add comprehensive tests to increase overall test coverage from 23% to 50%+.

**Focus on:**
- arb_finder.py core functionality
- utils.py database operations
- watch.py monitoring functionality

**Acceptance Criteria:**
- [ ] Test coverage reaches 50%+ overall
- [ ] arb_finder.py has adequate test coverage
- [ ] utils.py database operations are tested
- [ ] watch.py monitoring functionality is tested
- [ ] Coverage report is generated and documented

**Current coverage**: 23%
**Target coverage**: 50%+
EOF
)"

# Add Reverb Provider
gh issue create \
  --title "[Task]: Add Reverb marketplace provider" \
  --label "task,priority: high,component: backend,complexity: l" \
  --milestone "v0.6.0" \
  --body "$(cat <<EOF
Implement Reverb marketplace crawler for musical instruments.

**Features needed:**
- Search live listings on Reverb
- Fetch sold comparables
- Parse item details (title, price, condition)
- Store in database

**Acceptance Criteria:**
- [ ] Can search Reverb for live listings
- [ ] Can fetch sold comparables from Reverb
- [ ] Data properly parsed and stored
- [ ] Error handling implemented
- [ ] Rate limiting respected
- [ ] Tests added

**Technical Notes:**
- Follow existing provider pattern in arb_finder.py
- Respect robots.txt and ToS
- Use session with retry logic
EOF
)"

# Continue for other tasks...
```

Make executable and run:
```bash
chmod +x create_issues.sh
./create_issues.sh
```

### Using Python Script

```python
#!/usr/bin/env python3
# create_issues.py

import subprocess
import json

tasks = [
    {
        "title": "[Task]: Increase test coverage to 50%+",
        "labels": ["task", "priority: high", "component: testing", "complexity: xl"],
        "milestone": "v0.5.0",
        "body": """Add comprehensive tests to increase overall test coverage from 23% to 50%+.

**Focus on:**
- arb_finder.py core functionality
- utils.py database operations
- watch.py monitoring functionality

**Acceptance Criteria:**
- [ ] Test coverage reaches 50%+ overall
- [ ] arb_finder.py has adequate test coverage
- [ ] utils.py database operations are tested
- [ ] watch.py monitoring functionality is tested
- [ ] Coverage report is generated and documented
"""
    },
    # Add more tasks...
]

for task in tasks:
    cmd = [
        "gh", "issue", "create",
        "--title", task["title"],
        "--label", ",".join(task["labels"]),
        "--milestone", task["milestone"],
        "--body", task["body"]
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✓ Created: {task['title']}")
    else:
        print(f"✗ Failed: {task['title']}")
        print(f"  Error: {result.stderr}")
```

Run:
```bash
python3 create_issues.py
```

## Issue Creation Checklist

When creating an issue from TASKS.md:

- [ ] Use the appropriate template (Task, Feature, Bug)
- [ ] Copy the task title
- [ ] Include full description
- [ ] Add acceptance criteria as checkboxes
- [ ] Set component label
- [ ] Set priority label
- [ ] Set complexity label
- [ ] Add milestone if applicable
- [ ] Include technical notes
- [ ] Link dependencies (other issues)
- [ ] Assign to someone if known

## Priority Mapping

Map TASKS.md priority to GitHub labels:

| TASKS.md | GitHub Label |
|----------|--------------|
| 🔴 High Priority | `priority: high` |
| 🟡 Medium Priority | `priority: medium` |
| 🟢 Low Priority | `priority: low` |

## Component Mapping

| TASKS.md Component | GitHub Label |
|-------------------|--------------|
| Testing | `component: testing` |
| Backend/API | `component: backend` |
| Frontend/UI | `component: frontend` |
| CLI | `component: cli` |
| TUI | `component: tui` |
| TypeScript SDK | `component: sdk` |
| Docker/Deployment | `component: docker` |
| Documentation | `component: docs` |
| Infrastructure | `component: infra` |
| CI/CD | `component: ci` |

## Complexity Mapping

| TASKS.md Estimate | GitHub Label |
|------------------|--------------|
| XS (<1 hour) | `complexity: xs` |
| S (1-4 hours) | `complexity: s` |
| M (4-8 hours) | `complexity: m` |
| L (1-2 days) | `complexity: l` |
| XL (2+ days) | `complexity: xl` |

## Tips

### Good Issue Titles

✅ **Good**: `[Task]: Add email notifications for deals`
✅ **Good**: `[Task]: Increase test coverage to 50%+`
✅ **Good**: `[Task]: Implement Reverb marketplace provider`

❌ **Bad**: `Testing`
❌ **Bad**: `Fix stuff`
❌ **Bad**: `Work on notifications`

### Good Issue Descriptions

Include:
- Clear description of what needs to be done
- Why it's important
- Acceptance criteria (checkboxes)
- Technical notes or resources
- Dependencies or blockers

### Linking Issues

Use keywords to link issues:
- `Depends on #123`
- `Blocks #456`
- `Related to #789`
- `Part of #012` (for epics)

### Assigning Work

- Self-assign when you start work
- Use "In Progress" status in project board
- Update issue with progress comments
- Close when complete

## After Creating Issues

1. **Add to Project Board**: Issues should auto-add via workflow
2. **Prioritize in Backlog**: Drag to appropriate position
3. **Assign to Milestone**: Group by release version
4. **Link Related Issues**: Use keywords in comments
5. **Update TASKS.md**: Mark as created with issue number

Example update in TASKS.md:
```markdown
- [ ] **Increase test coverage to 50%+** (#123)
  - Component: Testing
  - Estimated: XL (2-3 days)
  - GitHub Issue: #123
```

## Resources

- [TASKS.md](../TASKS.md) - Full task list
- [Issue Templates](.github/ISSUE_TEMPLATE/) - Templates for creating issues
- [Labels Guide](LABELS.md) - Label definitions and usage
- [Project Setup](PROJECT_SETUP.md) - Project board configuration
- [GitHub CLI Docs](https://cli.github.com/manual/gh_issue_create) - CLI reference

---

**Last Updated**: December 2024

Questions? Open a discussion or ask a maintainer.
