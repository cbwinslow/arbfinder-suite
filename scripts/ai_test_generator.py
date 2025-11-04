#!/usr/bin/env python3
"""
AI Test Generator - Automatically generate tests for uncovered code
"""

import argparse
import ast
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestGenerator:
    """Generate test cases for Python code"""
    
    def __init__(self, target_dir: str, output_dir: str):
        self.target_dir = Path(target_dir)
        self.output_dir = Path(output_dir)
        self.generated_tests = []
    
    def analyze_function(self, node: ast.FunctionDef, module_name: str) -> Dict[str, Any]:
        """Analyze a function and determine what tests are needed"""
        return {
            "name": node.name,
            "module": module_name,
            "line": node.lineno,
            "args": [arg.arg for arg in node.args.args],
            "has_docstring": ast.get_docstring(node) is not None
        }
    
    def generate_test_for_function(self, func_info: Dict[str, Any]) -> str:
        """Generate a test case for a function"""
        func_name = func_info["name"]
        module_name = func_info["module"]
        args = func_info["args"]
        
        # Remove 'self' from args if present
        test_args = [arg for arg in args if arg != 'self']
        
        # Generate test template with proper mocking
        test_code = f'''def test_{func_name}():
    """Test {func_name} function."""
    from {module_name} import {func_name}
    from unittest.mock import Mock, patch
    
    # TODO: Customize test parameters
'''
        
        if test_args:
            # Generate mock parameters
            for arg in test_args:
                test_code += f'    mock_{arg} = Mock()  # TODO: Set appropriate value\n'
            
            # Generate test with mocked args
            args_str = ", ".join(f"mock_{arg}" for arg in test_args)
            test_code += f'''    
    # Test with valid input
    result = {func_name}({args_str})
    assert result is not None  # TODO: Add proper assertion
'''
        else:
            # Function with no args
            test_code += f'''    
    # Test function call
    result = {func_name}()
    assert result is not None  # TODO: Add proper assertion
'''
        
        test_code += '''    
    # TODO: Add edge case tests
    # TODO: Add error handling tests
'''
        
        return test_code
    
    def generate_test_file(self, module_path: Path) -> str:
        """Generate a complete test file for a module"""
        try:
            with open(module_path, 'r') as f:
                content = f.read()
                tree = ast.parse(content)
            
            module_name = str(module_path.relative_to(self.target_dir)).replace('/', '.').replace('.py', '')
            module_name = f"backend.{module_name}" if not module_name.startswith('backend') else module_name
            
            functions = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                    func_info = self.analyze_function(node, module_name)
                    functions.append(func_info)
            
            if not functions:
                return ""
            
            # Generate test file content
            test_content = f'''"""
Generated tests for {module_name}
"""

import pytest
from unittest.mock import Mock, patch

'''
            
            for func_info in functions:
                test_content += "\n" + self.generate_test_for_function(func_info) + "\n"
            
            return test_content
            
        except Exception as e:
            print(f"Error generating tests for {module_path}: {e}")
            return ""
    
    def generate_tests(self) -> List[str]:
        """Generate tests for all modules in target directory"""
        generated_files = []
        
        for py_file in self.target_dir.rglob("*.py"):
            if "__pycache__" in str(py_file) or "__init__" in py_file.name:
                continue
            
            # Generate test content
            test_content = self.generate_test_file(py_file)
            
            if test_content:
                # Determine output path
                rel_path = py_file.relative_to(self.target_dir)
                test_filename = f"test_{rel_path.name}"
                output_path = self.output_dir / test_filename
                
                # Only create if it doesn't exist
                if not output_path.exists():
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(output_path, 'w') as f:
                        f.write(test_content)
                    
                    generated_files.append(str(output_path))
                    print(f"✅ Generated: {output_path}")
        
        return generated_files


def main():
    parser = argparse.ArgumentParser(description='AI Test Generator')
    parser.add_argument(
        '--target',
        type=str,
        default='backend',
        help='Target directory to generate tests for'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='tests',
        help='Output directory for generated tests'
    )
    
    args = parser.parse_args()
    
    print(f"🧪 Generating tests for: {args.target}")
    print(f"📁 Output directory: {args.output}")
    
    generator = TestGenerator(args.target, args.output)
    generated_files = generator.generate_tests()
    
    print(f"\n✅ Test generation complete!")
    print(f"📝 Generated {len(generated_files)} test files")
    
    for filepath in generated_files:
        print(f"  - {filepath}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
