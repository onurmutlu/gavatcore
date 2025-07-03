#!/usr/bin/env python3
"""
🧪 GAVATCore Test Setup & Automation Script 🧪

Production-grade test infrastructure for GAVATCore backend project.
Provides complete validation pipeline with single command execution.

Usage:
    python setup_tests.py                    # Run all tests
    python setup_tests.py --install          # Install test dependencies only
    python setup_tests.py --lint             # Run linting only
    python setup_tests.py --test             # Run tests only
    python setup_tests.py --all              # Full validation pipeline
    python setup_tests.py --ci               # CI-optimized run (no interactive)

Author: GAVATCore Team
Version: 1.0.0
"""

import sys
import os
import subprocess
import argparse
import time
from pathlib import Path
from typing import List, Optional, Tuple
import json

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.panel import Panel
    from rich.table import Table
    from rich import print as rprint
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    console = None

# Global configuration
REQUIRED_PYTHON_VERSION = (3, 9)
PROJECT_ROOT = Path(__file__).parent
REQUIREMENTS_TEST = PROJECT_ROOT / "requirements_test.txt"
COVERAGE_MIN_THRESHOLD = 80
HTML_COVERAGE_DIR = PROJECT_ROOT / "htmlcov"


class TestRunner:
    """Main test runner class for GAVATCore project."""
    
    def __init__(self, verbose: bool = True, ci_mode: bool = False):
        self.verbose = verbose
        self.ci_mode = ci_mode
        self.console = Console() if RICH_AVAILABLE else None
        self.start_time = time.time()
        self.results = {
            "python_check": False,
            "dependencies": False,
            "mypy": False,
            "pytest": False,
            "coverage": 0
        }
    
    def log(self, message: str, level: str = "info") -> None:
        """Log messages with appropriate formatting."""
        if self.console and not self.ci_mode:
            if level == "success":
                rprint(f"[bold green]✅ {message}[/bold green]")
            elif level == "error":
                rprint(f"[bold red]❌ {message}[/bold red]")
            elif level == "warning":
                rprint(f"[bold yellow]⚠️ {message}[/bold yellow]")
            elif level == "info":
                rprint(f"[bold blue]ℹ️ {message}[/bold blue]")
            else:
                rprint(message)
        else:
            prefix = {
                "success": "✅",
                "error": "❌", 
                "warning": "⚠️",
                "info": "ℹ️"
            }.get(level, "")
            print(f"{prefix} {message}")
    
    def check_python_version(self) -> bool:
        """Check if Python version meets requirements."""
        current_version = sys.version_info[:2]
        
        if current_version >= REQUIRED_PYTHON_VERSION:
            self.log(f"Python {'.'.join(map(str, current_version))} ✓", "success")
            self.results["python_check"] = True
            return True
        else:
            self.log(
                f"Python {'.'.join(map(str, REQUIRED_PYTHON_VERSION))}+ required, "
                f"found {'.'.join(map(str, current_version))}", 
                "error"
            )
            return False
    
    def run_command(self, cmd: List[str], description: str) -> Tuple[bool, str]:
        """Run subprocess command with proper error handling."""
        try:
            if self.verbose and not self.ci_mode:
                self.log(f"Running: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                cwd=PROJECT_ROOT
            )
            
            if result.returncode == 0:
                self.log(f"{description} ✓", "success")
                return True, result.stdout
            else:
                self.log(f"{description} failed", "error")
                if self.verbose:
                    self.log(f"Error output: {result.stderr}")
                return False, result.stderr
                
        except FileNotFoundError:
            self.log(f"Command not found: {cmd[0]}", "error")
            return False, f"Command not found: {cmd[0]}"
        except Exception as e:
            self.log(f"Unexpected error: {e}", "error")
            return False, str(e)
    
    def install_dependencies(self) -> bool:
        """Install test dependencies from requirements_test.txt."""
        if not REQUIREMENTS_TEST.exists():
            self.log(f"Requirements file not found: {REQUIREMENTS_TEST}", "error")
            return False
        
        self.log("Installing test dependencies...")
        success, output = self.run_command(
            [sys.executable, "-m", "pip", "install", "-r", str(REQUIREMENTS_TEST)],
            "Dependencies installation"
        )
        
        if success:
            self.results["dependencies"] = True
        
        return success
    
    def run_mypy(self) -> bool:
        """Run mypy static type checking."""
        self.log("Running mypy static analysis...")
        
        # Check if mypy config exists
        mypy_config = PROJECT_ROOT / "mypy.ini"
        cmd = [sys.executable, "-m", "mypy", "."]
        
        if mypy_config.exists():
            cmd.extend(["--config-file", str(mypy_config)])
        
        success, output = self.run_command(cmd, "MyPy static analysis")
        
        if success:
            self.results["mypy"] = True
        
        return success
    
    def run_pytest(self) -> bool:
        """Run pytest with coverage reporting."""
        self.log("Running pytest with coverage...")
        
        cmd = [
            sys.executable, "-m", "pytest",
            "--cov=.",
            "--cov-report=term-missing",
            "--cov-report=html",
            "--cov-report=json",
            "-v"
        ]
        
        if self.ci_mode:
            cmd.append("--tb=short")
        
        success, output = self.run_command(cmd, "Pytest execution")
        
        if success:
            self.results["pytest"] = True
            # Extract coverage percentage
            self._extract_coverage(output)
        
        return success
    
    def _extract_coverage(self, pytest_output: str) -> None:
        """Extract coverage percentage from pytest output."""
        try:
            # Try to read from coverage.json if available
            coverage_json = PROJECT_ROOT / "coverage.json"
            if coverage_json.exists():
                with open(coverage_json) as f:
                    data = json.load(f)
                    self.results["coverage"] = round(data["totals"]["percent_covered"], 1)
            else:
                # Fallback to parsing output
                for line in pytest_output.split('\n'):
                    if 'TOTAL' in line and '%' in line:
                        try:
                            coverage_str = line.split('%')[0].split()[-1]
                            self.results["coverage"] = float(coverage_str)
                            break
                        except (ValueError, IndexError):
                            continue
        except Exception as e:
            self.log(f"Could not extract coverage: {e}", "warning")
    
    def generate_report(self) -> None:
        """Generate final test report."""
        duration = time.time() - self.start_time
        
        if self.console and not self.ci_mode:
            # Rich formatted report
            table = Table(title="🧪 GAVATCore Test Results")
            table.add_column("Component", style="cyan", no_wrap=True)
            table.add_column("Status", style="bold")
            table.add_column("Details", style="green")
            
            # Add results to table
            table.add_row(
                "Python Version", 
                "✅ PASS" if self.results["python_check"] else "❌ FAIL",
                f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            )
            
            table.add_row(
                "Dependencies",
                "✅ PASS" if self.results["dependencies"] else "❌ FAIL", 
                "All packages installed" if self.results["dependencies"] else "Installation failed"
            )
            
            table.add_row(
                "MyPy Analysis",
                "✅ PASS" if self.results["mypy"] else "❌ FAIL",
                "No type errors" if self.results["mypy"] else "Type errors found"
            )
            
            table.add_row(
                "Pytest Tests",
                "✅ PASS" if self.results["pytest"] else "❌ FAIL",
                f"Coverage: {self.results['coverage']}%" if self.results["pytest"] else "Tests failed"
            )
            
            self.console.print(table)
            
            # Coverage status
            coverage = self.results["coverage"]
            if coverage >= COVERAGE_MIN_THRESHOLD:
                self.console.print(f"[bold green]🎯 Coverage target achieved: {coverage}%[/bold green]")
            else:
                self.console.print(f"[bold yellow]📊 Coverage below target: {coverage}% (target: {COVERAGE_MIN_THRESHOLD}%)[/bold yellow]")
            
            # Duration
            self.console.print(f"[bold cyan]⏱️ Total execution time: {duration:.2f} seconds[/bold cyan]")
            
        else:
            # Simple text report for CI
            print("\n" + "="*50)
            print("GAVATCore Test Results")
            print("="*50)
            print(f"Python Version: {'PASS' if self.results['python_check'] else 'FAIL'}")
            print(f"Dependencies: {'PASS' if self.results['dependencies'] else 'FAIL'}")
            print(f"MyPy Analysis: {'PASS' if self.results['mypy'] else 'FAIL'}")
            print(f"Pytest Tests: {'PASS' if self.results['pytest'] else 'FAIL'}")
            print(f"Coverage: {self.results['coverage']}%")
            print(f"Duration: {duration:.2f} seconds")
            print("="*50)
    
    def run_all(self) -> bool:
        """Run complete test pipeline."""
        if self.console and not self.ci_mode:
            self.console.print(Panel.fit(
                "[bold blue]🚀 GAVATCore Test Pipeline Starting[/bold blue]\n"
                f"[cyan]Project: {PROJECT_ROOT}[/cyan]",
                title="Test Setup"
            ))
        
        steps = [
            ("Python Version Check", self.check_python_version),
            ("Install Dependencies", self.install_dependencies),
            ("MyPy Analysis", self.run_mypy),
            ("Pytest Execution", self.run_pytest)
        ]
        
        all_passed = True
        
        for step_name, step_func in steps:
            if self.console and not self.ci_mode:
                with self.console.status(f"[bold green]{step_name}..."):
                    success = step_func()
            else:
                self.log(f"Running {step_name}...")
                success = step_func()
            
            if not success:
                all_passed = False
                if step_name == "Python Version Check":
                    break  # Critical failure
        
        self.generate_report()
        return all_passed


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="GAVATCore Test Setup & Automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python setup_tests.py                    # Run all tests
  python setup_tests.py --install          # Install dependencies only  
  python setup_tests.py --lint             # Run linting only
  python setup_tests.py --test             # Run tests only
  python setup_tests.py --ci               # CI mode (non-interactive)
        """
    )
    
    parser.add_argument("--install", action="store_true", 
                       help="Install test dependencies only")
    parser.add_argument("--lint", action="store_true",
                       help="Run mypy linting only") 
    parser.add_argument("--test", action="store_true",
                       help="Run pytest tests only")
    parser.add_argument("--all", action="store_true",
                       help="Run complete validation pipeline")
    parser.add_argument("--ci", action="store_true",
                       help="CI mode (non-interactive, machine readable)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    
    args = parser.parse_args()
    
    # Initialize test runner
    runner = TestRunner(verbose=args.verbose, ci_mode=args.ci)
    
    # Determine what to run
    if args.install:
        success = runner.check_python_version() and runner.install_dependencies()
    elif args.lint:
        success = runner.check_python_version() and runner.run_mypy()
    elif args.test:
        success = runner.check_python_version() and runner.run_pytest()
    elif args.all or len(sys.argv) == 1:
        success = runner.run_all()
    else:
        parser.print_help()
        return 0
    
    # Exit with appropriate code for CI systems
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main()) 