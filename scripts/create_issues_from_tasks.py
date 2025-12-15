#!/usr/bin/env python3
"""
Create GitHub issues from TASKS.md

This script parses TASKS.md and creates GitHub issues for tasks that don't
already have issues created.

Requirements:
    - GitHub CLI (gh) installed and authenticated
    - TASKS.md file in the repository root

Usage:
    python scripts/create_issues_from_tasks.py [--dry-run] [--limit N]

Options:
    --dry-run   Show what would be created without actually creating issues
    --limit N   Limit to creating N issues (useful for testing)
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path


def parse_tasks_file(file_path):
    """Parse TASKS.md and extract task information."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    tasks = []
    current_section = None
    current_priority = None
    
    # Regular expressions
    section_pattern = r'^##\s+(.+?)(?:\s+\((.+?)\))?$'
    task_pattern = r'^-\s+\[\s*\]\s+\*\*(.+?)\*\*(?:\s+\(#(\d+)\))?'
    field_pattern = r'^\s+-\s+(.+?):\s+(.+)$'
    
    lines = content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check for section headers
        section_match = re.match(section_pattern, line)
        if section_match:
            current_section = section_match.group(1).strip()
            current_priority = section_match.group(2) or 'MEDIUM'
            i += 1
            continue
        
        # Check for priority markers in section names
        if '🔴' in line or 'HIGH PRIORITY' in line.upper():
            current_priority = 'HIGH'
        elif '🟡' in line or 'MEDIUM PRIORITY' in line.upper():
            current_priority = 'MEDIUM'
        elif '🟢' in line or 'LOW PRIORITY' in line.upper():
            current_priority = 'LOW'
        
        # Check for task items
        task_match = re.match(task_pattern, line)
        if task_match:
            task_title = task_match.group(1).strip()
            existing_issue = task_match.group(2)
            
            if existing_issue:
                # Skip tasks that already have issues
                i += 1
                continue
            
            # Parse task details
            task = {
                'title': task_title,
                'section': current_section,
                'priority': current_priority,
                'component': None,
                'estimated': None,
                'description': None,
                'acceptance': [],
                'technical': None,
                'dependencies': None,
            }
            
            # Look ahead for task details
            i += 1
            while i < len(lines):
                line = lines[i]
                
                # Stop at next task or section
                if re.match(section_pattern, line) or re.match(task_pattern, line):
                    break
                
                # Parse field
                field_match = re.match(field_pattern, line)
                if field_match:
                    field_name = field_match.group(1).strip()
                    field_value = field_match.group(2).strip()
                    
                    if field_name == 'Component':
                        task['component'] = field_value
                    elif field_name == 'Estimated' or field_name == 'Estimate':
                        task['estimated'] = field_value
                    elif field_name == 'Description':
                        task['description'] = field_value
                    elif field_name == 'Acceptance':
                        task['acceptance'].append(field_value)
                    elif field_name == 'Technical':
                        task['technical'] = field_value
                    elif field_name == 'Dependencies':
                        task['dependencies'] = field_value
                
                i += 1
            
            if task['component']:  # Only add if we found component info
                tasks.append(task)
            continue
        
        i += 1
    
    return tasks


def map_priority(priority):
    """Map priority to GitHub label."""
    priority = priority.upper()
    if 'HIGH' in priority or 'CRITICAL' in priority:
        return 'priority: high'
    elif 'LOW' in priority:
        return 'priority: low'
    else:
        return 'priority: medium'


def map_component(component):
    """Map component to GitHub label."""
    component_map = {
        'Testing': 'component: testing',
        'Backend/API': 'component: backend',
        'Frontend/UI': 'component: frontend',
        'CLI': 'component: cli',
        'TUI (Bubbletea)': 'component: tui',
        'TUI': 'component: tui',
        'TypeScript SDK': 'component: sdk',
        'Docker/Deployment': 'component: docker',
        'Documentation': 'component: docs',
        'Infrastructure': 'component: infra',
        'CI/CD': 'component: ci',
        'Mobile': 'component: mobile',
        'Browser Extension': 'component: extension',
        'Desktop': 'component: desktop',
    }
    return component_map.get(component, 'component: backend')


def map_complexity(estimated):
    """Map estimate to complexity label."""
    if not estimated:
        return None
    
    estimated = estimated.upper()
    if 'XL' in estimated or '2+ DAYS' in estimated or 'WEEKS' in estimated:
        return 'complexity: xl'
    elif 'L' in estimated or '1-2 DAYS' in estimated:
        return 'complexity: l'
    elif 'M' in estimated or '4-8 HOURS' in estimated:
        return 'complexity: m'
    elif 'S' in estimated or '1-4 HOURS' in estimated:
        return 'complexity: s'
    elif 'XS' in estimated or '<1 HOUR' in estimated:
        return 'complexity: xs'
    return None


def create_issue_body(task):
    """Generate issue body from task data."""
    body_parts = []
    
    # Description
    if task['description']:
        body_parts.append(task['description'])
        body_parts.append('')
    
    # Acceptance criteria
    if task['acceptance']:
        body_parts.append('**Acceptance Criteria:**')
        for criterion in task['acceptance']:
            body_parts.append(f'- [ ] {criterion}')
        body_parts.append('')
    
    # Technical notes
    if task['technical']:
        body_parts.append('**Technical Notes:**')
        body_parts.append(task['technical'])
        body_parts.append('')
    
    # Dependencies
    if task['dependencies']:
        body_parts.append('**Dependencies:**')
        body_parts.append(task['dependencies'])
        body_parts.append('')
    
    # Section reference
    body_parts.append(f'_From TASKS.md: {task["section"]}_')
    
    return '\n'.join(body_parts)


def create_github_issue(task, dry_run=False):
    """Create a GitHub issue using gh CLI."""
    title = f"[Task]: {task['title']}"
    
    # Build labels
    labels = ['task']
    labels.append(map_priority(task['priority']))
    if task['component']:
        labels.append(map_component(task['component']))
    complexity = map_complexity(task['estimated'])
    if complexity:
        labels.append(complexity)
    
    label_str = ','.join(labels)
    body = create_issue_body(task)
    
    if dry_run:
        print(f"\n{'='*60}")
        print(f"WOULD CREATE ISSUE:")
        print(f"Title: {title}")
        print(f"Labels: {label_str}")
        print(f"Body:\n{body}")
        print(f"{'='*60}")
        return True
    
    # Create issue using gh CLI
    cmd = [
        'gh', 'issue', 'create',
        '--title', title,
        '--label', label_str,
        '--body', body
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        issue_url = result.stdout.strip()
        print(f"✓ Created: {title}")
        print(f"  URL: {issue_url}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to create: {title}")
        print(f"  Error: {e.stderr}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Create GitHub issues from TASKS.md'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be created without actually creating issues'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of issues to create'
    )
    args = parser.parse_args()
    
    # Check for gh CLI
    try:
        subprocess.run(['gh', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: GitHub CLI (gh) is not installed or not in PATH")
        print("Install from: https://cli.github.com/")
        sys.exit(1)
    
    # Find TASKS.md
    tasks_file = Path('TASKS.md')
    if not tasks_file.exists():
        tasks_file = Path(__file__).parent.parent / 'TASKS.md'
    
    if not tasks_file.exists():
        print("Error: TASKS.md not found")
        sys.exit(1)
    
    print(f"Parsing {tasks_file}...")
    tasks = parse_tasks_file(tasks_file)
    print(f"Found {len(tasks)} tasks without existing issues")
    
    if not tasks:
        print("No tasks to create issues for!")
        return
    
    if args.limit:
        tasks = tasks[:args.limit]
        print(f"Limiting to {args.limit} issues")
    
    if args.dry_run:
        print("\n=== DRY RUN MODE ===")
    else:
        print("\nCreating issues...")
    
    created = 0
    for task in tasks:
        if create_github_issue(task, dry_run=args.dry_run):
            created += 1
    
    print(f"\n{'Would create' if args.dry_run else 'Created'} {created} issue(s)")


if __name__ == '__main__':
    main()
