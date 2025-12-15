# Project Management Guide

This guide explains how to use GitHub Projects v2 for managing ArbFinder Suite development.

## 📋 Overview

GitHub Projects v2 provides powerful project management capabilities with:
- Multiple views (Board, Table, Roadmap)
- Custom fields and automation
- Integration with issues and pull requests
- Milestone tracking

## 🎯 Our Project Structure

### Project Views

#### 1. Board View
The kanban-style board with columns:
- **📥 Backlog** - Prioritized tasks not yet started
- **📝 Todo** - Ready to be picked up
- **🏗️ In Progress** - Currently being worked on
- **👀 In Review** - Pull requests under review
- **✅ Done** - Completed work

#### 2. Table View
Spreadsheet-style view with sortable/filterable columns:
- Title
- Status
- Priority
- Component
- Assignee
- Labels
- Milestone
- Effort estimate

#### 3. Roadmap View
Timeline visualization showing:
- Milestones and releases
- Sprint planning
- Dependencies
- Due dates

### Custom Fields

We use custom fields to enhance project tracking:

#### Priority (Single Select)
- 🔴 Critical
- 🟠 High
- 🟡 Medium
- 🟢 Low

#### Component (Single Select)
- Backend
- Frontend
- TUI
- CLI
- API
- Database
- Infrastructure
- Documentation
- Multiple

#### Effort (Single Select)
- S (Small) - < 1 day
- M (Medium) - 1-3 days
- L (Large) - 3-5 days
- XL (Extra Large) - > 5 days

#### Sprint (Text)
- Sprint number or version (e.g., "Sprint 1", "v0.5.0")

#### Status (Single Select)
- Not Started
- In Progress
- Blocked
- In Review
- Done
- Won't Do

## 🚀 Getting Started

### Creating a Project

Using GitHub CLI:
```bash
# Create a new project
gh project create --owner cbwinslow --title "ArbFinder v0.5.0" --format board

# List all projects
gh project list --owner cbwinslow
```

Using GitHub Web UI:
1. Go to repository
2. Click "Projects" tab
3. Click "New project"
4. Choose template or start from scratch
5. Configure views and fields

### Adding Issues to Project

Using GitHub CLI:
```bash
# Add a single issue
gh project item-add PROJECT_NUMBER --owner cbwinslow --url ISSUE_URL

# Add multiple issues
for issue in $(gh issue list --limit 50 --json url -q '.[].url'); do
  gh project item-add PROJECT_NUMBER --owner cbwinslow --url "$issue"
done
```

Using GitHub Web UI:
1. Open the project
2. Click "+" in a column
3. Search for issue
4. Click to add

Using the automation script:
```bash
# Create issues and add to project
python scripts/create_github_issues.py --project
```

## 📊 Workflows and Best Practices

### Issue Lifecycle

```
Backlog → Todo → In Progress → In Review → Done
```

1. **Backlog**: New issues are triaged and prioritized
2. **Todo**: Issues are ready to be worked on with clear requirements
3. **In Progress**: Developer assigns issue to themselves and moves to this column
4. **In Review**: PR created and awaiting review
5. **Done**: PR merged and issue closed

### Sprint Planning

#### Before Sprint
1. Review backlog
2. Prioritize issues for next sprint
3. Move selected issues to "Todo"
4. Assign effort estimates
5. Set sprint field (e.g., "Sprint 1")

#### During Sprint
1. Developers pick issues from "Todo"
2. Move to "In Progress"
3. Create PR when ready
4. Move to "In Review"
5. After merge, automatically moves to "Done"

#### After Sprint
1. Review completed work
2. Close sprint
3. Move unfinished work back to backlog or next sprint
4. Sprint retrospective

### Milestone Management

Create milestones for major releases:

```bash
# Create milestone
gh api repos/cbwinslow/arbfinder-suite/milestones \
  -f title="v0.5.0 - Enhanced Providers" \
  -f description="Add Reverb and Mercari providers" \
  -f due_on="2026-03-31T00:00:00Z"
```

Link issues to milestones:
```bash
# Add issue to milestone
gh issue edit 123 --milestone "v0.5.0"
```

### Priority Management

#### Critical Priority
- Production bugs
- Security vulnerabilities
- Data loss issues
- Complete feature failures

**Actions**: 
- Immediate attention
- Daily updates
- May require hotfix release

#### High Priority
- Important features for upcoming release
- Performance issues affecting users
- Significant bugs

**Actions**:
- Should be in current sprint
- Regular updates
- Part of normal release cycle

#### Medium Priority
- Nice-to-have features
- Minor bugs
- Refactoring tasks

**Actions**:
- Planned for future sprints
- Updates as needed

#### Low Priority
- Future enhancements
- Documentation improvements
- Nice-to-have optimizations

**Actions**:
- Backlog
- Consider for future releases

## 🤖 Automation

### Automated Workflows

We use GitHub Actions to automate project management:

#### Auto-move Issues
- New issues → Backlog
- Issues assigned → Todo
- PR opened → In Review
- PR merged → Done
- Issue closed → Done

#### Auto-label
- Issues automatically labeled based on content
- Labels sync with project fields

#### Stale Management
- Mark stale issues after 60 days
- Close after 7 days of being stale
- Exempt "pinned" and "in progress" issues

### Custom Automations

Create custom automations in project settings:

**Example: Auto-assign to sprint**
```
When: Issue moved to "In Progress"
Then: Set sprint to "Current Sprint"
```

**Example: Set priority based on labels**
```
When: Label "priority: high" added
Then: Set Priority to "High"
```

## 📈 Tracking Progress

### Velocity Tracking

Track team velocity by:
1. Count story points (effort) completed per sprint
2. Calculate average velocity
3. Use for future sprint planning

### Burndown Charts

Monitor sprint progress:
1. Plot remaining work vs. time
2. Identify blockers early
3. Adjust scope if needed

### Metrics to Track

- **Cycle Time**: Time from "In Progress" to "Done"
- **Lead Time**: Time from "Backlog" to "Done"
- **Throughput**: Issues completed per sprint
- **Work in Progress**: Number of issues "In Progress"

## 🎯 Tips and Tricks

### Filtering

Use filters to focus on specific work:

```
# High priority backend issues
is:issue is:open label:backend label:"priority: high"

# Current sprint issues
is:issue project:@cbwinslow/1 sprint:"Sprint 1"

# My assigned issues
is:issue is:open assignee:@me
```

### Saved Views

Create saved views for common filters:
- "My Work" - Issues assigned to you
- "This Sprint" - Current sprint issues
- "High Priority" - Critical and high priority
- "Backend" - All backend issues
- "Blocked" - Blocked issues needing attention

### Keyboard Shortcuts

- `c` - Create new issue
- `e` - Edit item
- `/` - Focus search
- `x` - Select item
- `Cmd/Ctrl + Enter` - Save changes

### Bulk Operations

Select multiple items to:
- Change status
- Update priority
- Assign to sprint
- Add labels
- Close/archive

## 🔗 Integration with Other Tools

### Slack Integration

Get notifications in Slack:
1. Install GitHub app in Slack
2. Configure channel subscriptions
3. Receive updates on issues, PRs, reviews

### IDEs

Many IDEs support GitHub integration:
- VS Code: GitHub Pull Requests extension
- JetBrains: GitHub integration built-in
- View and manage issues from your IDE

### CLI Tools

```bash
# Quick issue creation
alias gh-issue='gh issue create --web'

# List my issues
alias my-issues='gh issue list --assignee @me'

# View project
alias project='gh project view PROJECT_NUMBER --owner cbwinslow'
```

## 📚 Resources

### Documentation
- [GitHub Projects Documentation](https://docs.github.com/en/issues/planning-and-tracking-with-projects)
- [GitHub CLI Manual](https://cli.github.com/manual/)
- [Our Contributing Guide](CONTRIBUTING.md)
- [Our GitHub Features Guide](GITHUB_FEATURES.md)

### Templates

We provide templates for:
- Sprint planning
- Release checklist
- Retrospective
- Bug triage

### Example Projects

View our example projects:
- [ArbFinder Roadmap](../../projects/1) - Long-term planning
- [Current Sprint](../../projects/2) - Active sprint
- [Bug Tracking](../../projects/3) - Bug management

## 🤝 Contributing to Project Management

Help improve our project management:
1. Suggest process improvements
2. Create useful views and filters
3. Document best practices
4. Share automation ideas

Open an issue or discussion to share your ideas!

## 📝 Changelog

### 2025-12-15
- Initial project management setup
- Created TASKS.md with comprehensive task list
- Set up issue templates and workflows
- Created automation for issue management

---

**Need Help?**
- Check [GITHUB_FEATURES.md](GITHUB_FEATURES.md) for GitHub feature guide
- Open a [Discussion](../../discussions) for questions
- Review [Contributing Guide](CONTRIBUTING.md) for more details

**Last Updated**: 2025-12-15
