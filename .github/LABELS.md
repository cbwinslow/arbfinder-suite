# GitHub Labels Guide

This document defines the labeling strategy for ArbFinder Suite issues and pull requests.

## Label Categories

### Type Labels (What)

These indicate the type of work:

| Label | Color | Description | Usage |
|-------|-------|-------------|-------|
| `bug` | #d73a4a | Something isn't working | Bug reports and fixes |
| `enhancement` | #a2eeef | New feature or request | Feature requests |
| `task` | #0075ca | Project task | Development tasks |
| `documentation` | #0075ca | Documentation improvement | Doc updates and fixes |
| `refactoring` | #fbca04 | Code refactoring | Code improvement without feature changes |
| `performance` | #fbca04 | Performance improvement | Speed/efficiency improvements |
| `security` | #d73a4a | Security issue | Security vulnerabilities and fixes |

### Priority Labels (When)

These indicate urgency:

| Label | Color | Description | When to Use |
|-------|-------|-------------|-------------|
| `priority: critical` | #b60205 | Urgent, production issue | Security issues, prod down, data loss |
| `priority: high` | #d93f0b | Important, blocking | Blocks releases, major bugs |
| `priority: medium` | #fbca04 | Important, not blocking | Important features, non-critical bugs |
| `priority: low` | #0e8a16 | Nice to have | Minor improvements, cosmetic issues |

### Component Labels (Where)

These indicate which part of the codebase:

| Label | Color | Description | Usage |
|-------|-------|-------------|-------|
| `component: backend` | #1d76db | Backend/API changes | Python backend, API endpoints |
| `component: frontend` | #1d76db | Frontend/UI changes | React, Next.js, UI components |
| `component: cli` | #1d76db | CLI changes | Python CLI tool |
| `component: tui` | #1d76db | TUI changes | Go Bubbletea TUI |
| `component: sdk` | #1d76db | TypeScript SDK changes | @arbfinder/client package |
| `component: docker` | #1d76db | Docker/deployment | Docker, docker-compose |
| `component: docs` | #1d76db | Documentation | Markdown files, docs/ |
| `component: tests` | #1d76db | Testing | Test files, test infrastructure |
| `component: ci` | #1d76db | CI/CD | GitHub Actions workflows |
| `component: infra` | #1d76db | Infrastructure | Deployment, cloud, config |

### Status Labels (State)

These indicate the current state:

| Label | Color | Description | When to Use |
|-------|-------|-------------|-------------|
| `needs-triage` | #ffffff | Needs initial review | Auto-applied to new issues |
| `needs-info` | #d876e3 | Waiting for information | Missing details from reporter |
| `needs-review` | #0e8a16 | Ready for code review | PR ready for review |
| `in-progress` | #fbca04 | Being worked on | Actively being developed |
| `blocked` | #d73a4a | Blocked by dependency | Can't proceed until something else is done |
| `duplicate` | #cfd3d7 | Already exists | Duplicate of another issue |
| `wontfix` | #ffffff | Won't be fixed | Out of scope or won't implement |
| `invalid` | #e4e669 | Not valid | Not a real issue |
| `stale` | #ededed | Inactive for 60+ days | Auto-applied by stale bot |

### Difficulty Labels (Complexity)

These help new contributors:

| Label | Color | Description | Estimate |
|-------|-------|-------------|----------|
| `good first issue` | #7057ff | Good for newcomers | XS-S, well-documented |
| `help wanted` | #008672 | Extra attention needed | Any size, could use help |
| `complexity: xs` | #c2e0c6 | Very simple | < 1 hour |
| `complexity: s` | #c2e0c6 | Simple | 1-4 hours |
| `complexity: m` | #fef2c0 | Medium | 4-8 hours |
| `complexity: l` | #f9d0c4 | Large | 1-2 days |
| `complexity: xl` | #d73a4a | Very large | 2+ days |

### Special Labels

| Label | Color | Description | Usage |
|-------|-------|-------------|-------|
| `breaking change` | #b60205 | Breaking API changes | Major version changes |
| `dependencies` | #0366d6 | Dependency updates | Renovate/Dependabot PRs |
| `question` | #d876e3 | Question | Questions (use Discussions instead) |
| `pinned` | #0075ca | Pinned issue | Important, don't mark stale |
| `epic` | #3e4b9e | Epic/large feature | Groups multiple issues |
| `technical debt` | #fbca04 | Tech debt | Code that needs refactoring |

## Labeling Guidelines

### When Creating Issues

1. **Auto-applied labels**: Bug/feature/task templates auto-apply labels
2. **Add priority**: Assess urgency and add priority label
3. **Add component**: Identify affected component(s)
4. **Add complexity**: Estimate effort (optional but helpful)
5. **Add special labels**: If applicable (breaking change, technical debt, etc.)

### When Creating PRs

1. **Link to issue**: Reference issue number (#123)
2. **Add component labels**: Same as the issue
3. **Add type**: bug, enhancement, refactoring, etc.
4. **Add status**: Usually `needs-review` when ready

### Label Combinations

#### High Priority Bug
```
bug
priority: high
component: backend
needs-triage
```

#### Good First Issue
```
enhancement
good first issue
complexity: s
component: docs
priority: low
```

#### Blocked Task
```
task
blocked
in-progress
priority: medium
component: frontend
```

## Automation Rules

### Auto-Applied Labels

1. **New Issues**:
   - Bug template → `bug`, `needs-triage`
   - Feature template → `enhancement`, `needs-triage`
   - Task template → `task`
   - Documentation template → `documentation`

2. **Keywords in Title/Body**:
   - "security", "vulnerability" → `security`, `priority: high`
   - "urgent", "critical" → `priority: critical`
   - "breaking" → `breaking change`

3. **Stale Issues**:
   - No activity for 60 days → `stale`
   - Closed 7 days after marked stale

4. **Renovate PRs**:
   - Auto → `dependencies`

### Label-Triggered Actions

1. **`needs-triage`**: Maintainers review and remove after triage
2. **`stale`**: Auto-close after 7 days if no activity
3. **`pinned`**: Exempt from stale marking
4. **`security`**: High priority, immediate attention

## Using Labels Effectively

### For Issue Authors

```markdown
Good example:
- Clear title: "Fix CSV export error when column contains quotes"
- Labels: bug, priority: medium, component: backend
- Component identified, priority set

Bad example:
- Vague title: "Export doesn't work"
- Labels: None
- No context, no labels
```

### For Maintainers

**Triage Process**:
1. Review `needs-triage` issues daily
2. Add priority label
3. Add component label(s)
4. Add complexity if clear
5. Remove `needs-triage`
6. Assign to milestone if applicable

**Review Process**:
1. Check `needs-review` PRs
2. Review code
3. Add comments if needed → `needs-changes`
4. Approve → `approved`
5. Merge → Auto-closes issue

### For Contributors

**Finding Issues**:
```
# Good first issues
label:"good first issue" is:open

# Help wanted
label:"help wanted" is:open

# By component
label:"component: frontend" is:open

# By priority
label:"priority: high" is:open
```

## Label Management

### Creating Labels

Via GitHub UI:
1. Go to **Issues** → **Labels**
2. Click **New label**
3. Enter name, description, color
4. Click **Create label**

Via GitHub CLI:
```bash
gh label create "priority: medium" \
  --description "Important, not blocking" \
  --color "fbca04"
```

### Bulk Label Operations

Via GitHub CLI:
```bash
# Add label to multiple issues
gh issue list --label "bug" | awk '{print $1}' | \
  xargs -I {} gh issue edit {} --add-label "priority: high"

# Remove label
gh issue edit 123 --remove-label "needs-triage"
```

### Label Sync

Use `github-label-sync` to sync labels across repos:

```bash
npm install -g github-label-sync

github-label-sync \
  --access-token $GITHUB_TOKEN \
  cbwinslow/arbfinder-suite \
  labels.json
```

## Best Practices

### Do's ✅

- ✅ Apply labels when creating issues
- ✅ Use consistent label naming
- ✅ Keep label count reasonable (< 50 total)
- ✅ Document label meanings (this file!)
- ✅ Review and update labels regularly
- ✅ Use automation for common patterns

### Don'ts ❌

- ❌ Create duplicate labels
- ❌ Use too many labels (keep to 3-5 per issue)
- ❌ Create labels without description
- ❌ Use confusing label names
- ❌ Leave issues unlabeled
- ❌ Create labels for one-time use

## Examples

### Example 1: Critical Security Bug

```
Title: SQL injection vulnerability in search endpoint
Labels:
  - bug
  - security
  - priority: critical
  - component: backend
  - complexity: s
```

### Example 2: New Feature Request

```
Title: Add export to Excel format
Labels:
  - enhancement
  - priority: medium
  - component: backend
  - complexity: m
  - help wanted
```

### Example 3: Documentation Task

```
Title: Add API examples to documentation
Labels:
  - task
  - documentation
  - good first issue
  - priority: low
  - component: docs
  - complexity: xs
```

### Example 4: Technical Debt

```
Title: Refactor database connection pooling
Labels:
  - refactoring
  - technical debt
  - priority: medium
  - component: backend
  - complexity: l
```

## Reporting

### Label Statistics

Track label usage:
```bash
# Count issues by label
gh issue list --label "bug" --state all --json number | jq '. | length'

# Issues by priority
gh issue list --state open --json labels | \
  jq -r '.[].labels[].name' | grep "priority:" | sort | uniq -c
```

### Label Analytics

View in GitHub Insights:
1. Go to **Insights** → **Issues**
2. Filter by labels
3. View trends over time

---

## Maintenance

### Monthly Review

- Review all labels for consistency
- Merge duplicate labels
- Remove unused labels
- Update descriptions
- Sync labels if using multiple repos

### Yearly Review

- Audit entire label system
- Get team feedback
- Update color scheme if needed
- Document changes

---

**Last Updated**: December 2024

For questions about labels, open a discussion or ask a maintainer.
