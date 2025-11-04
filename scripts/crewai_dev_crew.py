#!/usr/bin/env python3
"""
CrewAI Development Crew - Automated Software Development
This script runs a crew of AI agents that specialize in software development.
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def run_development_crew(task: str, priority: str, output: str):
    """
    Run the CrewAI development crew to work on the given task.
    
    Args:
        task: The development task to work on
        priority: Priority level (low, medium, high, critical)
        output: Output file path for results
    """
    print(f"🤖 Starting CrewAI Development Crew...")
    print(f"📋 Task: {task}")
    print(f"⚡ Priority: {priority}")
    
    try:
        # Import CrewAI components
        from crewai import Agent, Task, Crew, Process
        
        # Define agents
        researcher = Agent(
            role='Code Researcher',
            goal='Analyze codebase and identify areas for improvement',
            backstory="""You are an expert code researcher with deep knowledge of software 
            architecture, design patterns, and best practices. You excel at identifying 
            code smells, performance bottlenecks, and areas for enhancement.""",
            verbose=True,
            allow_delegation=True
        )
        
        developer = Agent(
            role='Senior Software Developer',
            goal='Implement code improvements and new features',
            backstory="""You are a senior software developer with 10+ years of experience 
            in Python, JavaScript, and full-stack development. You write clean, efficient, 
            and well-documented code.""",
            verbose=True,
            allow_delegation=True
        )
        
        tester = Agent(
            role='Quality Assurance Engineer',
            goal='Write comprehensive tests and ensure code quality',
            backstory="""You are a meticulous QA engineer who believes in test-driven 
            development. You write comprehensive unit tests, integration tests, and 
            ensure high code coverage.""",
            verbose=True,
            allow_delegation=False
        )
        
        reviewer = Agent(
            role='Code Reviewer',
            goal='Review code changes and ensure quality standards',
            backstory="""You are a thorough code reviewer who ensures all code meets 
            quality standards, follows best practices, and is well-documented. You 
            provide constructive feedback and suggest improvements.""",
            verbose=True,
            allow_delegation=False
        )
        
        # Define tasks
        research_task = Task(
            description=f"""Analyze the codebase and create a detailed report on:
            1. Current code quality and areas for improvement
            2. Potential bugs or issues
            3. Performance optimization opportunities
            4. Best practices that should be applied
            
            Focus on: {task}""",
            agent=researcher,
            expected_output="A detailed research report with actionable recommendations"
        )
        
        development_task = Task(
            description=f"""Based on the research findings, implement improvements:
            1. Fix identified issues
            2. Refactor code following best practices
            3. Add necessary documentation
            4. Optimize performance where needed
            
            Task: {task}
            Priority: {priority}""",
            agent=developer,
            expected_output="Implemented code changes with documentation"
        )
        
        testing_task = Task(
            description="""Write comprehensive tests for all changes:
            1. Unit tests for new functionality
            2. Integration tests where applicable
            3. Update existing tests if needed
            4. Ensure coverage is above 80%""",
            agent=tester,
            expected_output="Complete test suite with high coverage"
        )
        
        review_task = Task(
            description="""Review all changes and provide feedback:
            1. Code quality assessment
            2. Test coverage review
            3. Documentation review
            4. Final recommendations""",
            agent=reviewer,
            expected_output="Detailed code review with approval or suggestions"
        )
        
        # Create crew
        crew = Crew(
            agents=[researcher, developer, tester, reviewer],
            tasks=[research_task, development_task, testing_task, review_task],
            process=Process.sequential,
            verbose=True
        )
        
        # Run the crew
        print("\n🚀 Executing development crew...")
        result = crew.kickoff()
        
        # Save results
        output_data = {
            "task": task,
            "priority": priority,
            "status": "completed",
            "result": str(result),
            "agents": ["researcher", "developer", "tester", "reviewer"]
        }
        
        with open(output, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"\n✅ Development crew completed successfully!")
        print(f"📄 Output saved to: {output}")
        
        return 0
        
    except ImportError as e:
        print(f"❌ Error: CrewAI not installed. Install with: pip install crewai")
        print(f"Details: {e}")
        
        # Create placeholder output
        output_data = {
            "task": task,
            "priority": priority,
            "status": "error",
            "error": "CrewAI not installed",
            "message": "Install crewai package to use this feature"
        }
        
        with open(output, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        return 1
        
    except Exception as e:
        print(f"❌ Error running development crew: {e}")
        
        # Create error output
        output_data = {
            "task": task,
            "priority": priority,
            "status": "error",
            "error": str(e)
        }
        
        with open(output, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        return 1


def main():
    parser = argparse.ArgumentParser(
        description='Run CrewAI development crew for automated software development'
    )
    parser.add_argument(
        '--task',
        type=str,
        required=True,
        help='Development task to work on'
    )
    parser.add_argument(
        '--priority',
        type=str,
        choices=['low', 'medium', 'high', 'critical'],
        default='medium',
        help='Task priority level'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='crew-output.json',
        help='Output file path'
    )
    
    args = parser.parse_args()
    
    return run_development_crew(args.task, args.priority, args.output)


if __name__ == '__main__':
    sys.exit(main())
