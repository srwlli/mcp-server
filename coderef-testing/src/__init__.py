"""coderef-testing: Universal MCP server for test orchestration and reporting."""

__version__ = "1.0.0"
__author__ = "willh"
__license__ = "MIT"

from src.models import (
    TestFramework,
    TestResult,
    TestSummary,
    UnifiedTestResults,
)

__all__ = [
    "TestFramework",
    "TestResult",
    "TestSummary",
    "UnifiedTestResults",
]
