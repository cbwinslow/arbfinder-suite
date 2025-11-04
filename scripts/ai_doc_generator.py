#!/usr/bin/env python3
"""
AI Documentation Generator - Automatically generate API documentation
"""

import argparse
import ast
import os
import sys
from pathlib import Path
from typing import Dict, List, Any

sys.path.insert(0, str(Path(__file__).parent.parent))


class DocGenerator:
    """Generate documentation from Python code"""
    
    def __init__(self, input_dir: str, output_dir: str):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
    
    def extract_function_info(self, node: ast.FunctionDef) -> Dict[str, Any]:
        """Extract information from a function definition"""
        return {
            "name": node.name,
            "docstring": ast.get_docstring(node) or "No documentation available",
            "args": [(arg.arg, self.get_type_annotation(arg.annotation)) 
                     for arg in node.args.args],
            "returns": self.get_type_annotation(node.returns),
            "line": node.lineno
        }
    
    def extract_class_info(self, node: ast.ClassDef) -> Dict[str, Any]:
        """Extract information from a class definition"""
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append(self.extract_function_info(item))
        
        return {
            "name": node.name,
            "docstring": ast.get_docstring(node) or "No documentation available",
            "methods": methods,
            "line": node.lineno
        }
    
    def get_type_annotation(self, annotation) -> str:
        """Get string representation of type annotation"""
        if annotation is None:
            return "Any"
        if isinstance(annotation, ast.Name):
            return annotation.id
        if isinstance(annotation, ast.Constant):
            return str(annotation.value)
        return "Any"
    
    def parse_module(self, filepath: Path) -> Dict[str, Any]:
        """Parse a Python module and extract documentation"""
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                tree = ast.parse(content)
            
            module_doc = ast.get_docstring(tree) or "No module documentation"
            
            functions = []
            classes = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                    # Only top-level functions
                    if isinstance(node, ast.FunctionDef):
                        functions.append(self.extract_function_info(node))
                elif isinstance(node, ast.ClassDef):
                    classes.append(self.extract_class_info(node))
            
            return {
                "module": str(filepath.relative_to(self.input_dir)),
                "docstring": module_doc,
                "functions": functions,
                "classes": classes
            }
            
        except Exception as e:
            print(f"Error parsing {filepath}: {e}")
            return None
    
    def generate_markdown(self, module_info: Dict[str, Any]) -> str:
        """Generate markdown documentation from module info"""
        md = f"# {module_info['module']}\n\n"
        md += f"{module_info['docstring']}\n\n"
        
        if module_info['classes']:
            md += "## Classes\n\n"
            for cls in module_info['classes']:
                md += f"### {cls['name']}\n\n"
                md += f"{cls['docstring']}\n\n"
                
                if cls['methods']:
                    md += "#### Methods\n\n"
                    for method in cls['methods']:
                        args_str = ", ".join(f"{arg[0]}: {arg[1]}" for arg in method['args'])
                        md += f"##### `{method['name']}({args_str}) -> {method['returns']}`\n\n"
                        md += f"{method['docstring']}\n\n"
        
        if module_info['functions']:
            md += "## Functions\n\n"
            for func in module_info['functions']:
                args_str = ", ".join(f"{arg[0]}: {arg[1]}" for arg in func['args'])
                md += f"### `{func['name']}({args_str}) -> {func['returns']}`\n\n"
                md += f"{func['docstring']}\n\n"
        
        return md
    
    def generate_docs(self):
        """Generate documentation for all modules"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        generated_docs = []
        
        for py_file in self.input_dir.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            
            module_info = self.parse_module(py_file)
            if module_info:
                # Generate markdown
                markdown = self.generate_markdown(module_info)
                
                # Write to file
                output_file = self.output_dir / f"{module_info['module'].replace('/', '_').replace('.py', '.md')}"
                with open(output_file, 'w') as f:
                    f.write(markdown)
                
                generated_docs.append(str(output_file))
                print(f"✅ Generated: {output_file}")
        
        # Generate index
        self.generate_index(generated_docs)
        
        return generated_docs
    
    def generate_index(self, doc_files: List[str]):
        """Generate an index of all documentation"""
        index_path = self.output_dir / "README.md"
        
        with open(index_path, 'w') as f:
            f.write("# API Documentation\n\n")
            f.write("## Modules\n\n")
            
            for doc_file in sorted(doc_files):
                name = Path(doc_file).stem
                f.write(f"- [{name}]({Path(doc_file).name})\n")
        
        print(f"✅ Generated index: {index_path}")


def main():
    parser = argparse.ArgumentParser(description='AI Documentation Generator')
    parser.add_argument(
        '--input',
        type=str,
        default='backend',
        help='Input directory to generate docs from'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='docs/api',
        help='Output directory for documentation'
    )
    
    args = parser.parse_args()
    
    print(f"📚 Generating documentation for: {args.input}")
    print(f"📁 Output directory: {args.output}")
    
    generator = DocGenerator(args.input, args.output)
    generated_docs = generator.generate_docs()
    
    print(f"\n✅ Documentation generation complete!")
    print(f"📝 Generated {len(generated_docs)} documentation files")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
