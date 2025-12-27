"""
pytest configuration and fixtures for coderef-context tests
"""

import asyncio
import pytest
import os
from pathlib import Path


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_project_path():
    """Return path to @coderef/core CLI source (actual code to analyze).

    Note: coderef-context/src is empty, so we use the actual @coderef/core
    CLI project which has real TypeScript source code for analysis.
    """
    return r"C:\Users\willh\Desktop\projects\coderef-system\packages\cli"


@pytest.fixture
def cli_path():
    """Return the coderef CLI path."""
    default_path = os.path.expandvars(
        r"C:\Users\willh\Desktop\projects\coderef-system\packages\cli"
    )
    return os.environ.get("CODEREF_CLI_PATH", default_path)


@pytest.fixture
def cli_exists(cli_path):
    """Check if CLI exists at expected path."""
    cli_bin = os.path.join(cli_path, "dist", "cli.js")
    return os.path.exists(cli_bin)


class MockTestResults:
    """Helper class for mock test results."""

    @staticmethod
    def scan_result():
        """Mock coderef_scan result."""
        return {
            "success": True,
            "elements_found": 5,
            "elements": [
                {"name": "Server", "type": "class", "file": "server.py", "line": 47},
                {"name": "list_tools", "type": "function", "file": "server.py", "line": 59},
                {"name": "call_tool", "type": "function", "file": "server.py", "line": 312},
                {"name": "handle_coderef_scan", "type": "function", "file": "server.py", "line": 347},
                {"name": "handle_coderef_query", "type": "function", "file": "server.py", "line": 410},
            ]
        }

    @staticmethod
    def query_result():
        """Mock coderef_query result."""
        return {
            "success": True,
            "query_type": "imports",
            "target": "Server",
            "results": [
                {"file": "server.py", "line": 48, "type": "import"},
                {"file": "server.py", "line": 49, "type": "reference"},
            ]
        }

    @staticmethod
    def impact_result():
        """Mock coderef_impact result."""
        return {
            "success": True,
            "element": "Server",
            "operation": "modify",
            "impact": {
                "affected_files": 3,
                "risk_level": "MEDIUM",
                "ripple_effects": [
                    {"file": "server.py", "impact": "direct modification"},
                    {"file": "handler1.py", "impact": "indirect"},
                    {"file": "handler2.py", "impact": "indirect"},
                ]
            }
        }


@pytest.fixture
def mock_results():
    """Provide mock test results."""
    return MockTestResults()
