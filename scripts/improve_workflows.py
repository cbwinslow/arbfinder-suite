#!/usr/bin/env python3
"""
Workflow Improvement Script - Analyzes and improves GitHub Actions workflows
"""

import argparse
import sys
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def analyze_workflow(filepath: Path) -> dict:
    """Analyze a workflow file and suggest improvements"""
    improvements = []
    
    try:
        with open(filepath, 'r') as f:
            workflow = yaml.safe_load(f)
        
        # Check for outdated actions
        content = filepath.read_text()
        if 'actions/checkout@v3' in content:
            improvements.append({
                'type': 'outdated_action',
                'message': 'Update to actions/checkout@v4',
                'line': content.split('\n').index('  - uses: actions/checkout@v3') + 1
            })
        
        # Check for missing caching
        if 'actions/setup-python@' in content and 'cache:' not in content:
            improvements.append({
                'type': 'missing_cache',
                'message': 'Add pip caching to speed up workflow',
                'suggestion': "Add 'cache: pip' to setup-python step"
            })
        
        # Check for missing concurrency
        if 'concurrency' not in workflow:
            improvements.append({
                'type': 'missing_concurrency',
                'message': 'Add concurrency control to cancel outdated runs',
                'suggestion': 'Add concurrency group at workflow level'
            })
        
        return {
            'file': str(filepath.name),
            'improvements': improvements,
            'score': max(0, 100 - (len(improvements) * 10))
        }
        
    except Exception as e:
        return {
            'file': str(filepath.name),
            'error': str(e),
            'score': 0
        }


def improve_workflow(input_file: Path, output_file: Path) -> bool:
    """Apply improvements to a workflow file"""
    try:
        with open(input_file, 'r') as f:
            content = f.read()
        
        # Apply improvements
        improved = content
        
        # Update checkout action
        improved = improved.replace('actions/checkout@v3', 'actions/checkout@v4')
        
        # Add caching if missing
        if 'actions/setup-python@' in improved and 'cache:' not in improved:
            improved = improved.replace(
                'uses: actions/setup-python@v5',
                'uses: actions/setup-python@v5\n        with:\n          cache: pip'
            )
        
        # Write improved version
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            f.write(improved)
        
        return True
        
    except Exception as e:
        print(f"Error improving {input_file}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Improve GitHub Actions workflows')
    parser.add_argument('--input', type=str, required=True, help='Input directory')
    parser.add_argument('--output', type=str, required=True, help='Output directory')
    
    args = parser.parse_args()
    
    input_dir = Path(args.input)
    output_dir = Path(args.output)
    
    print(f"🔍 Analyzing workflows in: {input_dir}")
    
    workflow_files = list(input_dir.glob('*.yml'))
    
    if not workflow_files:
        print(f"❌ No workflow files found in {input_dir}")
        return 1
    
    analyses = []
    improved_count = 0
    
    for workflow_file in workflow_files:
        print(f"\n📋 Analyzing: {workflow_file.name}")
        
        # Analyze
        analysis = analyze_workflow(workflow_file)
        analyses.append(analysis)
        
        print(f"   Score: {analysis['score']}/100")
        if 'improvements' in analysis and analysis['improvements']:
            print(f"   Improvements suggested: {len(analysis['improvements'])}")
            for imp in analysis['improvements']:
                print(f"   - {imp['message']}")
        
        # Improve
        output_file = output_dir / workflow_file.name
        if improve_workflow(workflow_file, output_file):
            improved_count += 1
            print(f"   ✅ Improved version saved to: {output_file}")
    
    print(f"\n✅ Analysis complete!")
    print(f"📊 Analyzed {len(workflow_files)} workflows")
    print(f"🔧 Improved {improved_count} workflows")
    
    # Calculate average score
    avg_score = sum(a['score'] for a in analyses) / len(analyses)
    print(f"📈 Average workflow quality score: {avg_score:.1f}/100")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
