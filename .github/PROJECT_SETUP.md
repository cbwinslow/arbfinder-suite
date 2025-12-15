# GitHub Project v2 Setup Guide

This guide explains how to set up and use GitHub Projects (v2) for managing the ArbFinder Suite project.

## Overview

GitHub Projects v2 is a flexible, spreadsheet-like project management tool that integrates deeply with GitHub issues and pull requests. This guide will help you set up a project board for ArbFinder Suite.

## Creating a New Project

### Step 1: Create the Project

1. Go to your GitHub profile or organization page
2. Click on the **"Projects"** tab
3. Click **"New project"**
4. Choose a template:
   - **"Board"** - Kanban-style board (recommended)
   - **"Table"** - Spreadsheet view
   - **"Roadmap"** - Timeline view
5. Name it: **"ArbFinder Suite Development"**
6. Add a description: **"Task and feature tracking for ArbFinder Suite"**
7. Click **"Create"**

### Step 2: Configure Views

#### Board View (Default)

1. Create columns (called "fields" in v2):
   - **📋 Backlog** - New and planned items
   - **🚧 In Progress** - Currently being worked on
   - **👀 In Review** - Awaiting code review
   - **✅ Done** - Completed items
   - **❌ Closed** - Won't fix or duplicate

2. Customize the Status field:
   - Click the **"..."** menu on Status
   - Edit options to match your columns
   - Set colors for each status

#### Table View

1. Click **"+ New view"**
2. Select **"Table"** layout
3. Add columns:
   - Status
   - Priority
   - Assignees
   - Labels
   - Milestone
   - Estimate (custom field)
   - Component (custom field)

#### Roadmap View

1. Click **"+ New view"**
2. Select **"Roadmap"** layout
3. Configure date fields:
   - Start date
   - Target date
4. Group by: Milestone or Quarter

### Step 3: Add Custom Fields

Custom fields help organize and track additional information:

1. **Priority** (Single select)
   - 🔴 High
   - 🟡 Medium
   - 🟢 Low

2. **Component** (Single select)
   - Backend/API
   - Frontend/UI
   - CLI
   - TUI (Bubbletea)
   - TypeScript SDK
   - Docker/Deployment
   - Documentation
   - Testing
   - Infrastructure

3. **Estimate** (Number)
   - Story points or hours
   - Range: 0-40

4. **Type** (Single select)
   - Feature
   - Bug
   - Task
   - Documentation
   - Refactoring

5. **Sprint** (Iteration field)
   - Duration: 2 weeks
   - Start date: Your preference

## Adding Issues to the Project

### Manual Method

1. Open an issue
2. Click the gear icon next to **"Projects"** in the sidebar
3. Select your project
4. Issue appears in the project board

### Automated Method (Recommended)

Use the GitHub Actions workflow (see `.github/workflows/project-management.yml`):

```yaml
- name: Add issue to project
  uses: actions/add-to-project@v0.5.0
  with:
    project-url: https://github.com/users/YOUR_USERNAME/projects/1
    github-token: ${{ secrets.PROJECT_TOKEN }}
```

**Setup Steps**:

1. Create a Personal Access Token (PAT):
   - Go to **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
   - Click **"Generate new token (classic)"**
   - Name it: "Project Automation"
   - Select scopes: `repo`, `project`
   - Generate and copy the token

2. Add token as a repository secret:
   - Go to repository **Settings** → **Secrets and variables** → **Actions**
   - Click **"New repository secret"**
   - Name: `PROJECT_TOKEN`
   - Value: Your PAT
   - Click **"Add secret"**

3. The workflow will now automatically add new issues and PRs to the project

## Project Automation

### Built-in Automation

GitHub Projects v2 has built-in automation:

1. **Auto-add items**:
   - Click **"..."** → **"Workflows"**
   - Enable **"Auto-add to project"**
   - Configure: Add items when they match filters (e.g., specific labels)

2. **Auto-move items**:
   - Enable **"Item closed"** workflow
   - Action: Move to "Done" when issue is closed
   
3. **Auto-archive items**:
   - Enable **"Auto-archive items"**
   - Action: Archive items 7 days after closure

### Custom Automation (GitHub Actions)

The `project-management.yml` workflow provides:

- ✅ Auto-add issues to project when opened
- ✅ Auto-add PRs to project when opened
- ✅ Auto-triage with labels
- ✅ Priority assignment based on keywords
- ✅ Stale issue marking
- ✅ First-time contributor welcome
- ✅ Related issue linking

## Using the Project Board

### Daily Workflow

1. **Start of day**:
   - Review "Backlog" column
   - Move items to "In Progress"
   - Assign yourself to items

2. **During work**:
   - Update status as you progress
   - Add comments to issues
   - Link PRs to issues

3. **End of day**:
   - Update item status
   - Add notes on blockers
   - Plan next day's work

### Sprint Planning

1. **Create a new iteration**:
   - Click **"Sprint"** field
   - Create new iteration (2 weeks)
   - Name it: "Sprint X"

2. **Select items**:
   - Filter by priority and estimate
   - Assign items to current sprint
   - Balance workload across team

3. **During sprint**:
   - Daily standup using the board
   - Update progress regularly
   - Move completed items to "Done"

4. **Sprint retrospective**:
   - Review completed items
   - Identify bottlenecks
   - Plan improvements

### Milestone Planning

1. **Create milestones** in Issues:
   - Go to **Issues** → **Milestones**
   - Click **"New milestone"**
   - Name: "v0.5.0 - Testing & Quality"
   - Due date: Q1 2025
   - Description: Major goals

2. **Assign issues** to milestones:
   - Open issue
   - Select milestone in sidebar
   - Issue appears in milestone view

3. **Track progress**:
   - Use Roadmap view
   - Group by milestone
   - Visualize timeline

## Labels Strategy

Recommended labels for ArbFinder Suite:

### Type Labels
- `bug` - Something isn't working
- `enhancement` - New feature or request
- `task` - Project task
- `documentation` - Documentation improvement

### Priority Labels
- `priority: high` - Urgent, blocking
- `priority: medium` - Important, not blocking
- `priority: low` - Nice to have

### Component Labels
- `component: backend` - Backend/API changes
- `component: frontend` - Frontend/UI changes
- `component: cli` - CLI changes
- `component: tui` - TUI changes
- `component: sdk` - TypeScript SDK changes

### Status Labels
- `needs-triage` - Needs initial review
- `needs-info` - Waiting for more information
- `in-progress` - Currently being worked on
- `blocked` - Blocked by dependencies
- `ready-for-review` - Ready for code review

### Special Labels
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention needed
- `duplicate` - Already exists
- `wontfix` - Won't be fixed
- `security` - Security issue

## Filters and Saved Views

### Useful Filters

1. **My work**:
   ```
   assignee:@me is:open
   ```

2. **High priority bugs**:
   ```
   is:open label:"priority: high" label:bug
   ```

3. **Good first issues**:
   ```
   is:open label:"good first issue"
   ```

4. **This sprint**:
   ```
   is:open sprint:@current
   ```

5. **Blocked items**:
   ```
   is:open label:blocked
   ```

### Creating Saved Views

1. Apply filters to your view
2. Click **"Save changes"**
3. Name the view (e.g., "High Priority")
4. View appears in left sidebar

## Reporting and Insights

### Built-in Insights

1. Click **"Insights"** tab in project
2. View charts:
   - Burn down chart
   - Velocity
   - Items by status
   - Items by assignee

### Custom Insights

1. **Create custom chart**:
   - Click **"New chart"**
   - Select chart type (bar, line, pie)
   - Configure X and Y axes
   - Apply filters

2. **Example charts**:
   - Issues by component
   - Issues by priority
   - Issues closed per week
   - Estimated vs actual time

## Best Practices

### Do's ✅

- ✅ Keep board updated daily
- ✅ Use consistent labels
- ✅ Link PRs to issues
- ✅ Add estimates to tasks
- ✅ Write clear issue descriptions
- ✅ Close completed items promptly
- ✅ Use milestones for releases
- ✅ Archive old items regularly

### Don'ts ❌

- ❌ Don't leave stale items in "In Progress"
- ❌ Don't skip writing acceptance criteria
- ❌ Don't create duplicate issues
- ❌ Don't leave issues unassigned for long
- ❌ Don't forget to update status
- ❌ Don't ignore blocked items

## Integration with Workflow

### Issue → PR → Merge Flow

1. **Create issue** from template
2. Issue **auto-added** to project (via workflow)
3. **Assign** yourself and move to "In Progress"
4. **Create branch** from issue
5. **Make changes** and commit
6. **Create PR** linking to issue (#123)
7. PR **auto-added** to project
8. Request **review**, PR moves to "In Review"
9. **Merge PR**, issue moves to "Done"
10. Issue **auto-closes** (with "Fixes #123" in PR)
11. Item **auto-archives** after 7 days

### Connecting Multiple Repositories

If you have multiple repos (e.g., mobile app, extension):

1. Go to project settings
2. Click **"Manage access"**
3. Add other repositories
4. Issues from all repos appear in project

## Troubleshooting

### Issues Not Auto-Adding

- Check that `PROJECT_TOKEN` secret is set
- Verify token has `project` scope
- Check workflow runs in Actions tab
- Update project URL in workflow file

### Automation Not Working

- Enable built-in workflows in project settings
- Check workflow permissions in repository settings
- Verify Actions are enabled for repository

### Can't Find Project

- Projects are per user/organization
- Check you're looking in the right place
- Project must be created first

## Resources

- [GitHub Projects Documentation](https://docs.github.com/en/issues/planning-and-tracking-with-projects)
- [GitHub Actions for Projects](https://github.com/actions/add-to-project)
- [Project Automation](https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project)

## Maintenance

### Weekly Tasks
- Review and triage new issues
- Update item statuses
- Archive completed items
- Plan next sprint

### Monthly Tasks
- Review insights and metrics
- Update roadmap
- Clean up stale items
- Update documentation

---

**Last Updated**: December 2024

For questions or issues with project setup, open a discussion on GitHub.
