#!/usr/bin/env python3
"""
AI Code Analyzer - Automated code analysis and improvement suggestions
"""

import argparse
import ast
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class CodeAnalyzer:
    """Analyze code and suggest improvements"""
    
    def __init__(self, target_dir: str = "backend"):
        self.target_dir = Path(target_dir)
        self.issues = []
        self.suggestions = []
    
    def analyze_file(self, filepath: Path) -> Dict[str, Any]:
        """Analyze a single Python file"""
        issues = []
        
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                tree = ast.parse(content)
            
            # Check for common issues
            for node in ast.walk(tree):
                # Check for long functions
                if isinstance(node, ast.FunctionDef):
                    if len(node.body) > 50:
                        issues.append({
                            "type": "long_function",
                            "line": node.lineno,
                            "function": node.name,
                            "message": f"Function '{node.name}' is too long ({len(node.body)} lines)"
                        })
                
                # Check for missing docstrings
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    if not ast.get_docstring(node):
                        issues.append({
                            "type": "missing_docstring",
                            "line": node.lineno,
                            "name": node.name,
                            "message": f"Missing docstring for {type(node).__name__} '{node.name}'"
                        })
                
                # Check for broad exception catching
                if isinstance(node, ast.ExceptHandler):
                    if node.type is None or (isinstance(node.type, ast.Name) and node.type.id == 'Exception'):
                        issues.append({
                            "type": "broad_exception",
                            "line": node.lineno,
                            "message": "Catching broad exception - be more specific"
                        })
        
        except SyntaxError as e:
            issues.append({
                "type": "parse_error",
                "message": f"Syntax error: {e}"
            })
        except UnicodeDecodeError as e:
            issues.append({
                "type": "parse_error",
                "message": f"Encoding error: {e}"
            })
        except Exception as e:
            issues.append({
                "type": "parse_error",
                "message": f"Failed to parse file: {e}"
            })
        
        return {
            "file": str(filepath),
            "issues": issues
        }
    
    def analyze_directory(self) -> List[Dict[str, Any]]:
        """Analyze all Python files in directory"""
        results = []
        
        for py_file in self.target_dir.rglob("*.py"):
            if "__pycache__" not in str(py_file):
                result = self.analyze_file(py_file)
                if result["issues"]:
                    results.append(result)
        
        return results
    
    def generate_suggestions(self, results: List[Dict[str, Any]]) -> List[str]:
        """Generate improvement suggestions based on analysis"""
        suggestions = []
        
        issue_counts = {}
        for result in results:
            for issue in result["issues"]:
                issue_type = issue["type"]
                issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
        
        if issue_counts.get("missing_docstring", 0) > 5:
            suggestions.append(
                "Add docstrings to functions and classes to improve code documentation"
            )
        
        if issue_counts.get("long_function", 0) > 0:
            suggestions.append(
                "Refactor long functions into smaller, more manageable pieces"
            )
        
        if issue_counts.get("broad_exception", 0) > 0:
            suggestions.append(
                "Use specific exception types instead of catching broad exceptions"
            )
        
        return suggestions


def main():
    parser = argparse.ArgumentParser(description='AI Code Analyzer')
    parser.add_argument(
        '--target',
        type=str,
        default='backend',
        help='Target directory to analyze'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='analysis-report.json',
        help='Output file path'
    )
    
    args = parser.parse_args()
    
    print(f"🔍 Analyzing code in: {args.target}")
    
    analyzer = CodeAnalyzer(args.target)
    results = analyzer.analyze_directory()
    suggestions = analyzer.generate_suggestions(results)
    
    # Calculate statistics
    total_files = len(results)
    total_issues = sum(len(r["issues"]) for r in results)
    
    report = {
        "summary": {
            "files_analyzed": total_files,
            "total_issues": total_issues,
            "suggestions_count": len(suggestions)
        },
        "files": results,
        "suggestions": suggestions,
        "status": "completed"
    }
    
    # Save report
    with open(args.output, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✅ Analysis complete!")
    print(f"📊 Files analyzed: {total_files}")
    print(f"⚠️  Issues found: {total_issues}")
    print(f"💡 Suggestions: {len(suggestions)}")
    print(f"📄 Report saved to: {args.output}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
