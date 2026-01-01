#!/usr/bin/env python3
"""
Quick test runner for coderef-context → coderef-workflow integration tests.

Usage:
    python run_integration_tests.py              # Run all tests
    python run_integration_tests.py --verbose    # Detailed output
    python run_integration_tests.py --class TestDataFlowIntoPlanning  # Specific class
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Run integration tests with pytest."""

    # Ensure we're in the right directory
    coderef_context_dir = Path(__file__).parent
    test_file = coderef_context_dir / "tests" / "test_workflow_integration.py"

    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        return 1

    # Build pytest command
    cmd = ["python", "-m", "pytest", str(test_file)]

    # Add command line arguments
    if "--verbose" in sys.argv or "-v" in sys.argv:
        cmd.extend(["-v", "--tb=long"])
    else:
        cmd.append("-v")

    # Add specific test class if provided
    if "--class" in sys.argv:
        idx = sys.argv.index("--class")
        if idx + 1 < len(sys.argv):
            test_class = sys.argv[idx + 1]
            cmd[2] = f"{cmd[2]}::{test_class}"

    # Print command
    print(f"Running: {' '.join(cmd)}")
    print("-" * 80)

    # Run tests
    result = subprocess.run(cmd, cwd=coderef_context_dir)

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
