#!/usr/bin/env python3
"""
Script to create GitHub issues from TASKS.md

This script parses TASKS.md and creates GitHub issues using the GitHub CLI.
It can also create a GitHub Project v2 and link the issues to it.

Usage:
    python scripts/create_github_issues.py --dry-run  # Preview what would be created
    python scripts/create_github_issues.py            # Actually create issues
    python scripts/create_github_issues.py --project  # Create issues and project
"""

import argparse
import re
import subprocess
import json
from typing import List, Dict, Tuple
from pathlib import Path


class TaskParser:
    """Parse TASKS.md and extract tasks"""
    
    def __init__(self, tasks_file: str = "TASKS.md"):
        self.tasks_file = Path(tasks_file)
        self.tasks = []
        
    def parse(self) -> List[Dict]:
        """Parse TASKS.md and return list of tasks"""
        if not self.tasks_file.exists():
            raise FileNotFoundError(f"Tasks file not found: {self.tasks_file}")
        
        content = self.tasks_file.read_text()
        self.tasks = self._extract_tasks(content)
        return self.tasks
    
    def _extract_tasks(self, content: str) -> List[Dict]:
        """Extract tasks from markdown content"""
        tasks = []
        current_section = None
        current_priority = None
        current_category = None
        
        lines = content.split('\n')
        
        for line in lines:
            # Detect priority sections
            if '🔴 High Priority' in line:
                current_priority = 'high'
            elif '🟡 Medium Priority' in line:
                current_priority = 'medium'
            elif '🟢 Low Priority' in line:
                current_priority = 'low'
            
            # Detect category sections (### headers)
            category_match = re.match(r'^### (.+)$', line)
            if category_match:
                current_category = category_match.group(1)
                continue
            
            # Extract tasks (lines starting with - [ ])
            task_match = re.match(r'^- \[ \] (.+)$', line)
            if task_match and current_priority and current_category:
                task_text = task_match.group(1)
                
                # Determine labels based on content and category
                labels = self._determine_labels(task_text, current_category, current_priority)
                
                # Create task dict
                task = {
                    'title': task_text,
                    'priority': current_priority,
                    'category': current_category,
                    'labels': labels,
                    'body': self._generate_task_body(task_text, current_category, current_priority)
                }
                
                tasks.append(task)
        
        return tasks
    
    def _determine_labels(self, task_text: str, category: str, priority: str) -> List[str]:
        """Determine appropriate labels for a task"""
        labels = ['enhancement']
        
        # Add priority label
        if priority == 'high':
            labels.append('priority: high')
        elif priority == 'medium':
            labels.append('priority: medium')
        elif priority == 'low':
            labels.append('priority: low')
        
        # Add component labels based on category
        category_lower = category.lower()
        if 'backend' in category_lower or 'api' in category_lower:
            labels.append('backend')
        if 'frontend' in category_lower or 'ui' in category_lower:
            labels.append('frontend')
        if 'security' in category_lower:
            labels.append('security')
        if 'documentation' in category_lower or 'docs' in category_lower:
            labels.append('documentation')
        if 'testing' in category_lower or 'test' in category_lower:
            labels.append('testing')
        if 'mobile' in category_lower:
            labels.append('mobile')
        if 'database' in category_lower or 'db' in category_lower:
            labels.append('database')
        if 'infrastructure' in category_lower or 'devops' in category_lower:
            labels.append('infrastructure')
        
        # Add specific labels based on task content
        task_lower = task_text.lower()
        if 'provider' in task_lower or 'reverb' in task_lower or 'mercari' in task_lower:
            labels.append('provider')
        if 'notification' in task_lower or 'email' in task_lower or 'sms' in task_lower:
            labels.append('notifications')
        if 'performance' in task_lower or 'optimize' in task_lower:
            labels.append('performance')
        if 'bug' in task_lower or 'fix' in task_lower:
            if 'enhancement' in labels:
                labels.remove('enhancement')
            labels.append('bug')
        
        return list(set(labels))  # Remove duplicates
    
    def _generate_task_body(self, task_text: str, category: str, priority: str) -> str:
        """Generate issue body for a task"""
        body = f"""## Task Description

{task_text}

## Category

{category}

## Priority

{priority.capitalize()}

## Context

This task is tracked in our project roadmap. See [TASKS.md](https://github.com/cbwinslow/arbfinder-suite/blob/main/TASKS.md) for the complete task list.

## Acceptance Criteria

- [ ] Implementation completed
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Code reviewed and approved

## Additional Notes

<!-- Add any additional context, requirements, or notes here -->
"""
        return body


class IssueCreator:
    """Create GitHub issues using GitHub CLI"""
    
    def __init__(self, repo: str = "cbwinslow/arbfinder-suite", dry_run: bool = False):
        self.repo = repo
        self.dry_run = dry_run
        self.created_issues = []
        
    def create_issue(self, task: Dict) -> Tuple[bool, str]:
        """Create a single GitHub issue"""
        title = task['title']
        body = task['body']
        labels = ','.join(task['labels'])
        
        if self.dry_run:
            print(f"[DRY RUN] Would create issue:")
            print(f"  Title: {title}")
            print(f"  Labels: {labels}")
            return True, "dry-run"
        
        try:
            # Create issue using gh CLI
            cmd = [
                'gh', 'issue', 'create',
                '--repo', self.repo,
                '--title', title,
                '--body', body,
                '--label', labels
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            issue_url = result.stdout.strip()
            
            print(f"✓ Created issue: {title}")
            print(f"  URL: {issue_url}")
            
            self.created_issues.append({
                'title': title,
                'url': issue_url,
                'labels': task['labels']
            })
            
            return True, issue_url
            
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to create issue: {title}")
            print(f"  Error: {e.stderr}")
            return False, str(e)
    
    def create_all_issues(self, tasks: List[Dict], max_issues: int = None) -> int:
        """Create all issues from task list"""
        count = 0
        
        if max_issues:
            tasks = tasks[:max_issues]
        
        print(f"\nCreating {len(tasks)} issues...\n")
        
        for task in tasks:
            success, _ = self.create_issue(task)
            if success:
                count += 1
        
        print(f"\n{'[DRY RUN] ' if self.dry_run else ''}Created {count} issues successfully")
        return count


class ProjectCreator:
    """Create and manage GitHub Projects v2"""
    
    def __init__(self, repo: str = "cbwinslow/arbfinder-suite", dry_run: bool = False):
        self.repo = repo
        self.owner = repo.split('/')[0]
        self.dry_run = dry_run
        
    def create_project(self, title: str, description: str = "") -> Tuple[bool, str]:
        """Create a new GitHub Project v2"""
        if self.dry_run:
            print(f"[DRY RUN] Would create project: {title}")
            return True, "dry-run-project"
        
        try:
            cmd = [
                'gh', 'project', 'create',
                '--owner', self.owner,
                '--title', title,
                '--format', 'json'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            project_data = json.loads(result.stdout)
            project_url = project_data.get('url', '')
            
            print(f"✓ Created project: {title}")
            print(f"  URL: {project_url}")
            
            return True, project_url
            
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to create project: {title}")
            print(f"  Error: {e.stderr}")
            return False, str(e)
    
    def add_issue_to_project(self, project_number: int, issue_url: str) -> bool:
        """Add an issue to a project"""
        if self.dry_run:
            return True
        
        try:
            cmd = [
                'gh', 'project', 'item-add',
                str(project_number),
                '--owner', self.owner,
                '--url', issue_url
            ]
            
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            return True
            
        except subprocess.CalledProcessError:
            return False


def main():
    parser = argparse.ArgumentParser(
        description='Create GitHub issues from TASKS.md'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview what would be created without actually creating'
    )
    parser.add_argument(
        '--project',
        action='store_true',
        help='Also create a GitHub Project v2 and link issues'
    )
    parser.add_argument(
        '--max-issues',
        type=int,
        help='Maximum number of issues to create (for testing)'
    )
    parser.add_argument(
        '--repo',
        default='cbwinslow/arbfinder-suite',
        help='GitHub repository (default: cbwinslow/arbfinder-suite)'
    )
    parser.add_argument(
        '--tasks-file',
        default='TASKS.md',
        help='Path to tasks file (default: TASKS.md)'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("GitHub Issue Creator")
    print("=" * 60)
    
    if args.dry_run:
        print("\n⚠️  DRY RUN MODE - No issues will be created\n")
    
    # Parse tasks
    print(f"\nParsing {args.tasks_file}...")
    task_parser = TaskParser(args.tasks_file)
    tasks = task_parser.parse()
    print(f"Found {len(tasks)} tasks")
    
    # Create issues
    issue_creator = IssueCreator(repo=args.repo, dry_run=args.dry_run)
    issue_creator.create_all_issues(tasks, max_issues=args.max_issues)
    
    # Create project if requested
    if args.project and not args.dry_run:
        print("\n" + "=" * 60)
        print("Project Creation")
        print("=" * 60)
        print("\nNote: The --project flag is not yet fully implemented.")
        print("Please create the project manually and link issues using:")
        print("\n1. Create project via GitHub UI or CLI:")
        print("   gh project create --owner cbwinslow --title 'ArbFinder Suite Roadmap'")
        print("\n2. Add issues to project:")
        print("   See ISSUE_CREATION_GUIDE.md for detailed instructions")
        print("\nAlternatively, use the bulk add command from the guide.")
    
    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == '__main__':
    main()
