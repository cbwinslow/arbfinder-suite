# GitHub Automation Guide

This document describes the automation setup for ArbFinder Suite, including GitHub Actions integration with Projects V2, issue management, and workflow automation.

## 📋 Overview

ArbFinder Suite uses GitHub's built-in automation features and GitHub Actions to streamline development workflows, manage issues, and maintain the project board.

## 🤖 Project Board Automation

### Built-in Project Automations

GitHub Projects V2 includes built-in automations that you can enable:

#### 1. Auto-add Items

**When**: Issues or PRs are created or updated
**Action**: Automatically add them to the project

To enable:
1. Go to Project Settings
2. Click "Workflows"
3. Enable "Auto-add to project"
4. Configure filters (e.g., repository, labels)

Example filters:
```
# Add all issues and PRs
is:issue is:pr

# Add only bugs and features
is:issue label:bug,enhancement

# Add from specific repository
repo:cbwinslow/arbfinder-suite
```

#### 2. Auto-close Items

**When**: Issue or PR is closed
**Action**: Move to "Done" column

To enable:
1. Project Settings → Workflows
2. Enable "Item closed"
3. Select target status: "Done"

#### 3. Auto-archive Items

**When**: Item has been in "Done" for X days
**Action**: Archive the item

To enable:
1. Project Settings → Workflows
2. Enable "Auto-archive items"
3. Set days (e.g., 30 days)

### Custom Project Workflows

#### Status Transitions

**Workflow**: Update status based on PR state

```yaml
# .github/workflows/project-automation.yml
name: Project Board Automation

on:
  pull_request:
    types: [opened, ready_for_review, review_requested]
  issues:
    types: [assigned, labeled]

jobs:
  update-project:
    runs-on: ubuntu-latest
    steps:
      - name: Move PR to In Review
        if: github.event_name == 'pull_request' && github.event.action == 'opened'
        uses: actions/add-to-project@v0.5.0
        with:
          project-url: https://github.com/users/cbwinslow/projects/1
          github-token: ${{ secrets.PROJECT_TOKEN }}
          labeled: in-review
          
      - name: Move assigned issues to In Progress
        if: github.event_name == 'issues' && github.event.action == 'assigned'
        uses: actions/add-to-project@v0.5.0
        with:
          project-url: https://github.com/users/cbwinslow/projects/1
          github-token: ${{ secrets.PROJECT_TOKEN }}
          labeled: in-progress
```

**Note**: This requires a `PROJECT_TOKEN` secret with project write permissions.

## 🏷️ Label Automation

### Auto-labeling Issues

**Workflow**: Automatically label issues based on content

```yaml
# .github/workflows/auto-label.yml
name: Auto Label Issues

on:
  issues:
    types: [opened, edited]

jobs:
  label:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/labeler@v4
        with:
          repo-token: ${{ secrets.GITHUB_TOKEN }}
          configuration-path: .github/labeler.yml
```

**Configuration** (`.github/labeler.yml`):

```yaml
# Label based on file paths in PRs
'area: backend':
  - backend/**/*
  - '**/*.py'

'area: frontend':
  - frontend/**/*
  - '**/*.tsx'
  - '**/*.jsx'

'area: tui':
  - tui/**/*
  - '**/*.go'

'area: documentation':
  - '**/*.md'
  - docs/**/*

# Label based on size
'size: XS':
  - changed-files: 1-10

'size: S':
  - changed-files: 11-50

'size: M':
  - changed-files: 51-150

'size: L':
  - changed-files: 151-500

'size: XL':
  - changed-files: 501-*
```

### Label Management

Common labels for the project:

```yaml
# Type labels
- name: bug
  color: 'd73a4a'
  description: Something isn't working

- name: enhancement
  color: 'a2eeef'
  description: New feature or request

- name: documentation
  color: '0075ca'
  description: Improvements or additions to documentation

- name: task
  color: '1d76db'
  description: Development task

# Priority labels
- name: 'priority: high'
  color: 'b60205'
  description: High priority

- name: 'priority: medium'
  color: 'fbca04'
  description: Medium priority

- name: 'priority: low'
  color: '0e8a16'
  description: Low priority

# Area labels
- name: 'area: backend'
  color: 'c2e0c6'
  description: Backend (Python)

- name: 'area: frontend'
  color: 'c2e0c6'
  description: Frontend (Next.js)

- name: 'area: tui'
  color: 'c2e0c6'
  description: TUI (Go/Rich)

# Status labels
- name: 'status: blocked'
  color: 'b60205'
  description: Blocked by another issue

- name: 'status: help-wanted'
  color: '008672'
  description: Extra attention needed

- name: 'good first issue'
  color: '7057ff'
  description: Good for newcomers
```

## 🔔 Notifications

### Slack/Discord Integration

**Workflow**: Send notifications for important events

```yaml
# .github/workflows/notifications.yml
name: Notifications

on:
  issues:
    types: [opened, closed]
  pull_request:
    types: [opened, closed, ready_for_review]
  release:
    types: [published]

jobs:
  notify:
    runs-on: ubuntu-latest
    steps:
      - name: Send Slack notification
        uses: slackapi/slack-github-action@v1
        with:
          webhook-url: ${{ secrets.SLACK_WEBHOOK_URL }}
          payload: |
            {
              "text": "New ${{ github.event_name }}: ${{ github.event.issue.title || github.event.pull_request.title }}",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "*${{ github.event_name }}*: <${{ github.event.issue.html_url || github.event.pull_request.html_url }}|${{ github.event.issue.title || github.event.pull_request.title }}>"
                  }
                }
              ]
            }
```

### Email Digests

GitHub provides built-in email notifications. Configure in your GitHub settings:
1. Go to Settings → Notifications
2. Choose notification frequency
3. Select which events to receive

## 🔄 Issue Management

### Stale Issue Management

**Workflow**: Close inactive issues automatically

```yaml
# .github/workflows/stale.yml
name: Mark Stale Issues

on:
  schedule:
    - cron: '0 0 * * *' # Daily at midnight

jobs:
  stale:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/stale@v8
        with:
          repo-token: ${{ secrets.GITHUB_TOKEN }}
          stale-issue-message: |
            This issue has been automatically marked as stale because it has not had 
            recent activity. It will be closed if no further activity occurs within 7 days.
            If this issue is still relevant, please comment to keep it open.
          stale-pr-message: |
            This PR has been automatically marked as stale because it has not had 
            recent activity. It will be closed if no further activity occurs within 7 days.
          close-issue-message: |
            This issue was automatically closed due to inactivity. 
            If you believe this issue is still relevant, please reopen it.
          close-pr-message: |
            This PR was automatically closed due to inactivity.
          days-before-stale: 60
          days-before-close: 7
          stale-issue-label: 'stale'
          stale-pr-label: 'stale'
          exempt-issue-labels: 'pinned,security,roadmap'
          exempt-pr-labels: 'pinned,security'
```

### Issue Triage

**Workflow**: Request more information from issue reporters

```yaml
# .github/workflows/issue-triage.yml
name: Issue Triage

on:
  issues:
    types: [opened]

jobs:
  triage:
    runs-on: ubuntu-latest
    steps:
      - name: Check if issue has label
        id: check-label
        uses: actions/github-script@v6
        with:
          script: |
            const issue = context.payload.issue;
            return issue.labels.length === 0;
            
      - name: Add needs-triage label
        if: steps.check-label.outputs.result == 'true'
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.addLabels({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              labels: ['needs-triage']
            });
```

## 🧪 Testing Automation

### Run Tests on Issue Comment

**Workflow**: Trigger tests when maintainer comments

```yaml
# .github/workflows/test-on-comment.yml
name: Test on Comment

on:
  issue_comment:
    types: [created]

jobs:
  test:
    if: |
      github.event.issue.pull_request &&
      contains(github.event.comment.body, '/test')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          pip install -e ".[test]"
          pytest
      - name: Comment result
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: '✅ Tests passed!'
            });
```

## 📦 Release Automation

### Auto-generate Release Notes

**Workflow**: Generate release notes from PRs and issues

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
          
      - name: Generate Release Notes
        id: release-notes
        uses: release-drafter/release-drafter@v5
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          
      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          body: ${{ steps.release-notes.outputs.body }}
          draft: false
          prerelease: false
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**Configuration** (`.github/release-drafter.yml`):

```yaml
name-template: 'v$RESOLVED_VERSION'
tag-template: 'v$RESOLVED_VERSION'

categories:
  - title: '🚀 Features'
    labels:
      - 'enhancement'
      - 'feature'
  - title: '🐛 Bug Fixes'
    labels:
      - 'bug'
      - 'fix'
  - title: '🧪 Testing'
    labels:
      - 'test'
      - 'testing'
  - title: '📚 Documentation'
    labels:
      - 'documentation'
  - title: '🔧 Maintenance'
    labels:
      - 'maintenance'
      - 'refactor'
      - 'chore'

change-template: '- $TITLE @$AUTHOR (#$NUMBER)'

version-resolver:
  major:
    labels:
      - 'major'
      - 'breaking'
  minor:
    labels:
      - 'minor'
      - 'enhancement'
  patch:
    labels:
      - 'patch'
      - 'bug'
      - 'fix'
  default: patch

template: |
  ## What's Changed
  
  $CHANGES
  
  ## Contributors
  
  $CONTRIBUTORS
```

## 🔐 Security Automation

### Dependency Updates

**Workflow**: Auto-update dependencies with Dependabot

```yaml
# .github/dependabot.yml
version: 2
updates:
  # Python dependencies
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
      - "python"
    reviewers:
      - "cbwinslow"
    commit-message:
      prefix: "deps"
      
  # JavaScript dependencies
  - package-ecosystem: "npm"
    directory: "/frontend"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
      - "javascript"
    reviewers:
      - "cbwinslow"
    commit-message:
      prefix: "deps"
      
  # Go dependencies
  - package-ecosystem: "gomod"
    directory: "/tui"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
      - "go"
    reviewers:
      - "cbwinslow"
    commit-message:
      prefix: "deps"
      
  # GitHub Actions
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
      - "github-actions"
    commit-message:
      prefix: "ci"
```

### Security Scanning

**Workflow**: Scan for security issues

```yaml
# .github/workflows/security.yml
name: Security Scan

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 0 * * 0' # Weekly on Sunday

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run Bandit (Python)
        run: |
          pip install bandit
          bandit -r backend/ -f json -o bandit-report.json
          
      - name: Run npm audit
        working-directory: ./frontend
        run: npm audit --audit-level=moderate
        
      - name: Run Trivy (Container scanning)
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'
          
      - name: Upload results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'
```

## 📊 Metrics and Reports

### Generate Project Reports

**Workflow**: Create weekly project reports

```yaml
# .github/workflows/weekly-report.yml
name: Weekly Report

on:
  schedule:
    - cron: '0 9 * * 1' # Monday at 9 AM

jobs:
  report:
    runs-on: ubuntu-latest
    steps:
      - name: Generate Report
        uses: actions/github-script@v6
        with:
          script: |
            const since = new Date();
            since.setDate(since.getDate() - 7);
            
            // Get issues created last week
            const { data: issues } = await github.rest.issues.listForRepo({
              owner: context.repo.owner,
              repo: context.repo.repo,
              since: since.toISOString(),
              state: 'all'
            });
            
            // Get PRs merged last week
            const { data: prs } = await github.rest.pulls.list({
              owner: context.repo.owner,
              repo: context.repo.repo,
              state: 'closed',
              sort: 'updated',
              direction: 'desc'
            });
            
            const mergedPRs = prs.filter(pr => 
              pr.merged_at && new Date(pr.merged_at) > since
            );
            
            // Create report issue
            const report = `
            ## Weekly Project Report
            
            ### Summary
            - Issues opened: ${issues.filter(i => !i.pull_request).length}
            - Issues closed: ${issues.filter(i => !i.pull_request && i.state === 'closed').length}
            - PRs merged: ${mergedPRs.length}
            
            ### New Issues
            ${issues.filter(i => !i.pull_request).map(i => `- ${i.title} #${i.number}`).join('\n')}
            
            ### Merged PRs
            ${mergedPRs.map(pr => `- ${pr.title} #${pr.number}`).join('\n')}
            `;
            
            await github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: `Weekly Report - ${new Date().toISOString().split('T')[0]}`,
              body: report,
              labels: ['report', 'weekly']
            });
```

## 🎯 Best Practices

### Automation Guidelines

1. **Keep It Simple**: Start with basic automations, add complexity as needed
2. **Test Thoroughly**: Test workflows in a development environment first
3. **Monitor Performance**: Ensure automations don't slow down development
4. **Document Everything**: Keep this file updated with new automations
5. **Use Secrets Safely**: Never expose tokens or keys in workflow files
6. **Be Mindful of Costs**: GitHub Actions has usage limits

### Common Pitfalls

- **Over-automation**: Don't automate everything, some tasks need human judgment
- **Token Permissions**: Ensure tokens have correct scopes
- **Rate Limits**: Be careful with API-heavy automations
- **Notification Fatigue**: Don't spam team members with too many notifications

## 🔧 Setup Instructions

### Required Secrets

Add these secrets in repository settings:

```
GITHUB_TOKEN - Automatically provided by GitHub
PROJECT_TOKEN - Personal access token for project access (classic token with repo and project scopes)
SLACK_WEBHOOK_URL - Optional, for Slack notifications
```

### Enabling Workflows

1. Workflows are enabled by default
2. For new workflows, create `.yml` files in `.github/workflows/`
3. Commit and push to trigger
4. Check Actions tab to monitor

## 📚 Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Projects Automation](https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project)
- [Awesome GitHub Actions](https://github.com/sdras/awesome-actions)

## 🆘 Troubleshooting

### Workflow Not Running
- Check if workflow file is in `.github/workflows/`
- Verify YAML syntax
- Check workflow permissions in repository settings
- Review workflow run logs in Actions tab

### Project Automation Not Working
- Verify project URL in workflow
- Check PROJECT_TOKEN permissions
- Ensure items are linked to project

### Labels Not Applied
- Verify labeler configuration
- Check if paths match correctly
- Review workflow logs

---

**Next Steps**: 
- Review existing workflows in `.github/workflows/`
- Enable desired project automations
- Set up required secrets
- Test automations in a development branch
