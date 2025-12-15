# GitHub Projects V2 - Setup Guide

This document provides instructions for setting up and managing GitHub Projects V2 for ArbFinder Suite.

## 📋 Overview

GitHub Projects V2 is a powerful project management tool integrated with GitHub. It allows you to track issues, pull requests, and tasks in a flexible, customizable board view.

## 🚀 Creating the Project

### Step 1: Create a New Project

1. Navigate to your repository: `https://github.com/cbwinslow/arbfinder-suite`
2. Click on the **"Projects"** tab
3. Click **"New project"**
4. Choose **"Board"** or **"Table"** view (we recommend starting with Board)
5. Name it: **"ArbFinder Suite Development"**
6. Add a description: **"Main development board for tracking features, bugs, and tasks"**

### Step 2: Configure Project Views

Create multiple views for different purposes:

#### 1. Board View - Development Workflow
- **Columns**:
  - 📥 Backlog - Ideas and future tasks
  - 📋 To Do - Ready to be worked on
  - 🏗️ In Progress - Currently being worked on
  - 👀 In Review - Pull requests under review
  - ✅ Done - Completed items
  - 🚫 Blocked - Items waiting on dependencies

#### 2. Table View - All Items
- **Columns**:
  - Title
  - Status
  - Priority (High, Medium, Low)
  - Component (Backend, Frontend, CLI, TUI, etc.)
  - Assignees
  - Labels
  - Milestone
  - Created Date
  - Updated Date

#### 3. Priority View - What's Important
- **Columns**: Status
- **Grouping**: By Priority
- **Sorting**: By Priority (High → Low)
- **Filter**: Status not "Done"

#### 4. Component View - By Area
- **Columns**: Status
- **Grouping**: By Component
- **Filter**: Status not "Done"

#### 5. Roadmap View - Timeline
- **Layout**: Roadmap
- **Group by**: Milestone
- **Date field**: Target date

## 🏷️ Field Setup

### Custom Fields to Add

1. **Priority** (Single select)
   - 🔴 High
   - 🟡 Medium
   - 🟢 Low

2. **Component** (Single select)
   - Backend (Python)
   - Frontend (Next.js)
   - CLI (Python)
   - CLI (TypeScript)
   - TUI (Go)
   - TUI (Rich)
   - API
   - Database
   - Documentation
   - Infrastructure
   - Testing
   - CI/CD

3. **Type** (Single select)
   - 🐛 Bug
   - ✨ Feature
   - 🔧 Task
   - 📚 Documentation
   - 🎨 Enhancement
   - 🔒 Security
   - ⚡ Performance
   - 🧪 Testing

4. **Effort** (Single select)
   - XS (< 1 hour)
   - S (1-4 hours)
   - M (1-2 days)
   - L (3-5 days)
   - XL (1+ weeks)

5. **Target Date** (Date)
   - When you aim to complete the item

6. **Blocked By** (Text)
   - List blocking issues or PRs

## 📝 Using the Project Board

### Adding Items to the Project

#### From Issues
1. Create an issue using one of our templates
2. In the issue sidebar, click "Projects"
3. Select "ArbFinder Suite Development"
4. The issue appears in "Backlog" by default

#### From Pull Requests
1. PRs are automatically added when they reference an issue
2. Or manually add them via the PR sidebar

#### Quick Add
1. Click "+" at the bottom of any column
2. Type to search existing issues or create a draft
3. Convert draft to issue when ready

### Moving Items

#### Manual Movement
- Drag and drop between columns
- Use the dropdown menu on each card

#### Automated Movement (see AUTOMATION.md)
- Issues move to "In Progress" when assigned
- PRs move to "In Review" when opened
- Items move to "Done" when closed/merged

### Filtering and Searching

Use the search/filter bar to find items:

```
# Examples
is:open label:bug priority:high
component:"Backend (Python)" status:"To Do"
assignee:@me status:"In Progress"
milestone:v0.5.0
```

## 🎯 Workflow

### For Maintainers

1. **Triage New Issues**
   - Review issues in "Backlog"
   - Set priority, component, and effort
   - Add to milestone if applicable
   - Move to "To Do" when ready

2. **Planning**
   - Use Priority and Component views
   - Assign issues to developers
   - Set target dates for milestones

3. **Tracking Progress**
   - Check "In Progress" column daily
   - Identify blocked items
   - Review PRs in "In Review"

### For Contributors

1. **Pick a Task**
   - Browse "To Do" column
   - Filter by "good first issue" label
   - Check effort estimation

2. **Start Working**
   - Assign yourself to the issue
   - Move to "In Progress"
   - Create a branch

3. **Submit Work**
   - Create a PR linking to the issue
   - PR automatically moves to "In Review"
   - Address review feedback

4. **Complete**
   - Once merged, item moves to "Done"

## 📊 Milestones

Create milestones for version releases:

### Example Milestones

- **v0.5.0** - Q1 2024
  - New provider integrations
  - Enhanced AI features
  - Performance improvements

- **v1.0.0** - Q2 2024
  - OAuth authentication
  - Multi-user support
  - Production-ready features

- **v2.0.0** - Future
  - Mobile apps
  - Advanced analytics
  - Enterprise features

### Milestone Usage
1. Create milestone in repository settings
2. Set due date
3. Add description with goals
4. Assign issues to milestone
5. Track progress in Roadmap view

## 🔄 Integration with Issues

### Linking Issues to Project Items

Issues and PRs can be linked in several ways:

```markdown
# In issue/PR description
Fixes #123
Closes #456
Relates to #789
Depends on #012
Blocks #345
```

### Issue Templates Integration

Our issue templates automatically suggest:
- Component selection (becomes project field)
- Priority level (becomes project field)
- Type of issue (becomes project field)

## 📈 Metrics and Insights

### Built-in Insights

GitHub Projects V2 provides insights:
1. Click "Insights" in project menu
2. Create charts for:
   - Items by status
   - Items by component
   - Items by priority
   - Velocity (items completed over time)
   - Burn-down charts

### Useful Charts

1. **Velocity Chart**
   - X-axis: Week
   - Y-axis: Count
   - Group by: Status = Done

2. **Component Distribution**
   - Chart type: Pie
   - Group by: Component
   - Filter: Status != Done

3. **Priority Breakdown**
   - Chart type: Bar
   - Group by: Priority
   - Filter: Status != Done

## 🤖 Automation

See [AUTOMATION.md](AUTOMATION.md) for details on:
- Auto-adding issues to project
- Status transitions
- Label management
- Notifications

## 🎨 Customization

### Custom Workflows

You can create custom workflows for your team:

1. **Bug Triage Workflow**
   - New bugs → Backlog
   - Validated bugs → To Do
   - Critical bugs → In Progress (assigned immediately)

2. **Feature Development Workflow**
   - Idea → Backlog
   - Approved → To Do
   - Design → In Progress
   - Implementation → In Progress
   - Testing → In Review
   - Released → Done

3. **Documentation Workflow**
   - Identified gap → To Do
   - Writing → In Progress
   - Review → In Review
   - Published → Done

## 💡 Best Practices

### For Effective Project Management

1. **Keep Status Updated**
   - Move cards as work progresses
   - Don't let items get stale

2. **Use Labels Consistently**
   - Apply relevant labels to all issues
   - Keep label list manageable

3. **Write Clear Titles**
   - Use action verbs
   - Be specific and concise
   - Example: "Add Reverb provider for sold listings"

4. **Link Related Items**
   - Use "Relates to", "Blocks", "Depends on"
   - Helps understand dependencies

5. **Regular Grooming**
   - Review backlog weekly
   - Close stale issues
   - Update priorities

6. **Set Realistic Targets**
   - Don't overcommit milestones
   - Leave buffer for unexpected work

## 📚 Resources

- [GitHub Projects V2 Documentation](https://docs.github.com/en/issues/planning-and-tracking-with-projects)
- [Best Practices Guide](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/best-practices-for-projects)
- [GitHub Projects Changelog](https://github.com/orgs/community/discussions/categories/projects)

## 🆘 Common Issues

### Issue: Items not appearing
**Solution**: Make sure the issue/PR is added to the project via the sidebar

### Issue: Can't change custom field
**Solution**: You may not have write access. Contact a maintainer.

### Issue: Automation not working
**Solution**: Check workflow permissions in repository settings

### Issue: Lost items
**Solution**: Use "Clear all filters" to show all items

## 📞 Getting Help

If you have questions about the project board:
- Open a discussion in [GitHub Discussions](https://github.com/cbwinslow/arbfinder-suite/discussions)
- Tag maintainers in the project

---

**Next Steps**: See [AUTOMATION.md](AUTOMATION.md) for setting up automated workflows with the project board.
