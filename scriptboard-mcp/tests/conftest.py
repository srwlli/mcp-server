"""
Pytest configuration and fixtures for Scriptboard MCP tests.
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset the client singleton before each test."""
    import http_client
    http_client._client = None
    yield
    http_client._client = None
