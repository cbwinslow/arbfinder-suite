# Leveraging GitHub Features for ArbFinder Suite

This document explains how to use GitHub's features effectively for managing the ArbFinder Suite project.

## 📋 Table of Contents

- [Issues](#issues)
- [Projects](#projects)
- [Discussions](#discussions)
- [Pull Requests](#pull-requests)
- [Actions](#actions)
- [Security](#security)
- [Releases](#releases)
- [Wiki](#wiki)

## 🐛 Issues

### Creating Issues

Issues are tracked using our custom templates:
- **Bug Report**: Report bugs or unexpected behavior
- **Feature Request**: Suggest new features or enhancements
- **Documentation**: Report documentation issues
- **Provider Request**: Request new marketplace provider support

**Quick Links:**
- [Create Bug Report](../../issues/new?template=bug_report.yml)
- [Create Feature Request](../../issues/new?template=feature_request.yml)
- [View All Issues](../../issues)

### Issue Labels

We use a comprehensive labeling system:

#### Component Labels
- `backend` - Python backend code
- `frontend` - Next.js frontend code
- `tui` - Terminal UI (Go)
- `cli` - Command-line interface
- `api` - REST API endpoints
- `database` - Database-related issues
- `docker` - Docker and containerization
- `documentation` - Documentation updates

#### Type Labels
- `bug` - Something isn't working
- `enhancement` - New feature or request
- `security` - Security vulnerability
- `performance` - Performance improvement
- `testing` - Test-related issues
- `provider` - Marketplace provider

#### Priority Labels
- `priority: critical` - Requires immediate attention
- `priority: high` - Important, should be addressed soon
- `priority: medium` - Normal priority
- `priority: low` - Nice to have

#### Status Labels
- `needs-triage` - Needs review by maintainers
- `in progress` - Currently being worked on
- `blocked` - Blocked by another issue or dependency
- `help wanted` - Looking for contributors
- `good first issue` - Good for newcomers
- `wontfix` - Will not be implemented
- `duplicate` - Duplicate of another issue
- `stale` - Inactive for extended period

### Linking Issues

Link issues to show relationships:
- `Closes #123` - Automatically closes issue when PR is merged
- `Fixes #123` - Same as above
- `Related to #123` - Shows relationship without auto-closing
- `Depends on #123` - Shows dependency
- `Blocks #123` - Shows that this issue blocks another

### Issue Templates

Located in `.github/ISSUE_TEMPLATE/`:
- `bug_report.yml` - Structured bug reporting
- `feature_request.yml` - Feature suggestions
- `documentation.yml` - Documentation improvements
- `provider_request.yml` - New provider requests
- `config.yml` - Template configuration

## 📊 Projects

### GitHub Projects v2

We use GitHub Projects v2 for project management with multiple views:

#### Board View
- **Backlog**: Unstarted tasks
- **Todo**: Ready to start
- **In Progress**: Currently being worked on
- **In Review**: Under code review
- **Done**: Completed tasks

#### Table View
Sortable and filterable table with:
- Priority
- Assignees
- Labels
- Due dates
- Custom fields

#### Roadmap View
Timeline visualization showing:
- Milestones
- Release planning
- Dependencies

### Custom Fields

Our projects include custom fields:
- **Priority**: Critical, High, Medium, Low
- **Component**: Backend, Frontend, TUI, CLI, etc.
- **Effort**: S, M, L, XL
- **Sprint**: Sprint number or version
- **Status**: Custom workflow status

### Creating a Project

```bash
# Using GitHub CLI
gh project create --owner cbwinslow --title "ArbFinder v0.5.0" --format board
```

### Adding Issues to Projects

```bash
# Add issue to project
gh project item-add PROJECT_NUMBER --owner cbwinslow --url ISSUE_URL
```

## 💬 Discussions

Use GitHub Discussions for:

### Categories
1. **Q&A** - Ask and answer questions
2. **Ideas** - Share and discuss new ideas
3. **Show and Tell** - Share what you've built
4. **General** - General discussion
5. **Announcements** - Project announcements

### Discussion Templates

Located in `.github/DISCUSSION_TEMPLATE/`:
- `q-and-a.yml` - Questions template
- `ideas.yml` - Ideas template
- `show-and-tell.yml` - Show and tell template

### Best Practices
- Search before creating new discussions
- Use appropriate categories
- Be respectful and constructive
- Follow the Code of Conduct

## 🔀 Pull Requests

### PR Template

Our PR template includes:
- Description
- Type of change
- Related issues
- Testing performed
- Screenshots (if applicable)
- Checklist

### PR Review Process

1. **Create PR** using the template
2. **Automated checks** run (CI/CD)
3. **Code review** by maintainers
4. **Address feedback** if needed
5. **Approval** by maintainer(s)
6. **Merge** into main branch

### PR Labels

- `work in progress` - Not ready for review
- `ready for review` - Ready for maintainer review
- `changes requested` - Reviewer requested changes
- `approved` - Approved and ready to merge

### Branch Naming

Use descriptive branch names:
- `feature/provider-reverb` - New features
- `fix/api-cors-issue` - Bug fixes
- `docs/update-quickstart` - Documentation
- `refactor/split-providers` - Refactoring
- `test/api-endpoints` - Testing

## ⚙️ Actions

### Automated Workflows

Located in `.github/workflows/`:

#### Issue Management
- `issue-labeler.yml` - Auto-labels issues based on content
- `stale-issues.yml` - Marks and closes stale issues/PRs
- `greetings.yml` - Welcomes first-time contributors

#### CI/CD
- Existing CI workflows continue to run
- Tests, linting, and builds automated

### Running Actions

Actions run automatically on:
- Push to branches
- Pull request creation/update
- Issue creation/update
- Scheduled cron jobs

View action runs: [Actions Tab](../../actions)

## 🔒 Security

### Security Policy

See [SECURITY.md](../SECURITY.md) for:
- Supported versions
- Reporting vulnerabilities
- Disclosure policy
- Security best practices

### Security Features

1. **Dependabot** - Automatic dependency updates
2. **CodeQL** - Security analysis
3. **Secret Scanning** - Detects committed secrets
4. **Security Advisories** - Private vulnerability reporting

### Reporting Security Issues

**Never report security issues in public issues!**

Use:
- [Security Advisories](../../security/advisories/new)
- Private vulnerability reporting
- Email to maintainers

## 🚀 Releases

### Creating Releases

1. Update `CHANGELOG.md`
2. Tag the version: `git tag -a v0.5.0 -m "Release v0.5.0"`
3. Push tags: `git push --tags`
4. Create release on GitHub with release notes

### Release Notes

Include:
- New features
- Bug fixes
- Breaking changes
- Upgrade instructions
- Contributors

### Versioning

We follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

Example: `v0.4.0` → `v0.5.0` (minor) or `v1.0.0` (major)

## 📚 Wiki

Use the GitHub Wiki for:
- Extended documentation
- Tutorials and guides
- FAQs
- API examples
- Architecture documentation
- Troubleshooting guides

**Access**: [Wiki Tab](../../wiki)

## 🎯 Quick Reference

### Common Commands

```bash
# List issues
gh issue list

# Create issue
gh issue create --title "Bug: API error" --body "Description" --label bug

# View issue
gh issue view 123

# Create PR
gh pr create --title "Fix API bug" --body "Fixes #123"

# Review PR
gh pr review 456 --approve

# Merge PR
gh pr merge 456

# Create project
gh project create --title "Sprint 1" --owner cbwinslow

# Create release
gh release create v0.5.0 --title "v0.5.0" --notes "Release notes"
```

### Useful Links

- [GitHub CLI Documentation](https://cli.github.com/manual/)
- [GitHub Projects Documentation](https://docs.github.com/en/issues/planning-and-tracking-with-projects)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Markdown Guide](https://guides.github.com/features/mastering-markdown/)

## 📝 Tips and Tricks

### Issue Management
- Use task lists in issues to track progress: `- [ ] Task`
- Reference commits in issues: `Fixed in abc123`
- Mention users with `@username`
- Use keywords in commits to auto-close issues: `Fixes #123`

### Project Management
- Use milestones to group related issues
- Set due dates for time-sensitive work
- Use projects for sprint planning
- Filter by labels for focused views

### Collaboration
- Request reviews from specific people
- Use draft PRs for work in progress
- Enable auto-merge for approved PRs
- Use GitHub Codespaces for quick testing

### Automation
- Set up Dependabot for dependency updates
- Use Actions for CI/CD automation
- Configure branch protection rules
- Enable required status checks

## 🎉 Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for detailed contribution guidelines.

---

**Last Updated**: 2025-12-15
