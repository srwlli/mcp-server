"""
Mock fixtures for MCP client testing.

This module provides reusable mock objects and fixtures for testing
coderef-context integration across all test categories.
"""

import json
from unittest.mock import Mock, MagicMock, AsyncMock, patch
from typing import Dict, Any, List


class MockMCPResponse:
    """Mock response from MCP server."""

    def __init__(self, tool_name: str, result: Dict[str, Any], message_id: int = 1):
        self.tool_name = tool_name
        self.result = result
        self.message_id = message_id

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-RPC 2.0 response format."""
        return {
            "jsonrpc": "2.0",
            "id": self.message_id,
            "result": self.result
        }


class MockCoderefScanResponse:
    """Mock response for coderef_scan tool."""

    @staticmethod
    def with_components(component_count: int = 5) -> Dict[str, Any]:
        """Generate mock scan response with N components."""
        components = [
            {
                "type": "function",
                "name": f"function_{i}",
                "file": f"src/module_{i}.py",
                "line": 10 + i * 10
            }
            for i in range(component_count)
        ]
        return {
            "inventory": {
                "components": components,
                "total_files": component_count,
                "total_components": component_count
            }
        }

    @staticmethod
    def empty() -> Dict[str, Any]:
        """Generate empty scan response."""
        return {
            "inventory": {
                "components": [],
                "total_files": 0,
                "total_components": 0
            }
        }


class MockCoderefQueryResponse:
    """Mock response for coderef_query tool."""

    @staticmethod
    def with_dependencies(dependency_count: int = 3) -> Dict[str, Any]:
        """Generate mock query response with N dependencies."""
        dependencies = [
            {
                "type": "function_call",
                "source": f"module_{i}",
                "target": "auth_service",
                "file": f"src/module_{i}.py"
            }
            for i in range(dependency_count)
        ]
        return {
            "relationships": dependencies,
            "total_dependencies": dependency_count
        }

    @staticmethod
    def empty() -> Dict[str, Any]:
        """Generate empty query response."""
        return {
            "relationships": [],
            "total_dependencies": 0
        }


class MockCoderefPatternsResponse:
    """Mock response for coderef_patterns tool."""

    @staticmethod
    def with_patterns(pattern_count: int = 2) -> Dict[str, Any]:
        """Generate mock patterns response with N patterns."""
        patterns = [
            {
                "name": f"decorator_pattern_{i}",
                "count": 5 + i,
                "files": [f"src/file_{j}.py" for j in range(3)]
            }
            for i in range(pattern_count)
        ]
        return {
            "patterns": patterns,
            "total_patterns": pattern_count
        }

    @staticmethod
    def empty() -> Dict[str, Any]:
        """Generate empty patterns response."""
        return {
            "patterns": [],
            "total_patterns": 0
        }


class MockCoderefCoverageResponse:
    """Mock response for coderef_coverage tool."""

    @staticmethod
    def high_coverage() -> Dict[str, Any]:
        """Generate mock coverage response with 85% coverage."""
        return {
            "coverage": {
                "overall_percent": 85.0,
                "files": [
                    {"name": "src/auth.py", "coverage_percent": 90.0},
                    {"name": "src/db.py", "coverage_percent": 80.0}
                ]
            }
        }

    @staticmethod
    def low_coverage() -> Dict[str, Any]:
        """Generate mock coverage response with 45% coverage."""
        return {
            "coverage": {
                "overall_percent": 45.0,
                "files": [
                    {"name": "src/utils.py", "coverage_percent": 30.0},
                    {"name": "src/legacy.py", "coverage_percent": 60.0}
                ]
            }
        }


class MockMCPClient:
    """Mock MCP client for testing."""

    def __init__(self):
        self.call_history: List[Dict[str, Any]] = []
        self.response_map: Dict[str, Dict[str, Any]] = {}
        self.message_id = 0
        self.error_on_tool: Dict[str, Exception] = {}

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Mock tool call that tracks calls and returns configured responses."""
        self.message_id += 1

        # Record the call
        self.call_history.append({
            "tool": tool_name,
            "arguments": arguments,
            "message_id": self.message_id,
            "timestamp": None
        })

        # Check for configured error
        if tool_name in self.error_on_tool:
            raise self.error_on_tool[tool_name]

        # Return configured response or default
        if tool_name in self.response_map:
            return self.response_map[tool_name]
        else:
            return self._default_response(tool_name)

    def _default_response(self, tool_name: str) -> Dict[str, Any]:
        """Generate default response based on tool name."""
        if tool_name == "coderef_scan":
            return MockCoderefScanResponse.with_components(3)
        elif tool_name == "coderef_query":
            return MockCoderefQueryResponse.with_dependencies(2)
        elif tool_name == "coderef_patterns":
            return MockCoderefPatternsResponse.with_patterns(2)
        elif tool_name == "coderef_coverage":
            return MockCoderefCoverageResponse.high_coverage()
        else:
            return {"result": "ok"}

    def get_call_count(self, tool_name: str = None) -> int:
        """Get number of calls to a specific tool or total calls."""
        if tool_name is None:
            return len(self.call_history)
        return sum(1 for call in self.call_history if call["tool"] == tool_name)

    def get_calls_for_tool(self, tool_name: str) -> List[Dict[str, Any]]:
        """Get all calls for a specific tool."""
        return [call for call in self.call_history if call["tool"] == tool_name]

    def reset(self):
        """Reset call history and configuration."""
        self.call_history = []
        self.response_map = {}
        self.message_id = 0
        self.error_on_tool = {}

    def configure_response(self, tool_name: str, response: Dict[str, Any]):
        """Configure response for a specific tool."""
        self.response_map[tool_name] = response

    def configure_error(self, tool_name: str, error: Exception):
        """Configure tool to raise an error."""
        self.error_on_tool[tool_name] = error


def create_mock_subprocess() -> MagicMock:
    """Create mock subprocess.Popen object."""
    mock_proc = MagicMock()
    mock_proc.pid = 12345
    mock_proc.returncode = None
    mock_proc.stdin = MagicMock()
    mock_proc.stdout = MagicMock()
    mock_proc.stderr = MagicMock()
    mock_proc.poll.return_value = None  # Process is running
    mock_proc.wait.return_value = 0  # Exits cleanly
    return mock_proc


def create_mock_json_rpc_request(tool_name: str, arguments: Dict[str, Any], message_id: int = 1) -> str:
    """Create a JSON-RPC 2.0 request string."""
    request = {
        "jsonrpc": "2.0",
        "id": message_id,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }
    return json.dumps(request) + "\n"


def create_mock_json_rpc_response(result: Dict[str, Any], message_id: int = 1) -> str:
    """Create a JSON-RPC 2.0 response string."""
    response = {
        "jsonrpc": "2.0",
        "id": message_id,
        "result": result
    }
    return json.dumps(response) + "\n"


def create_mock_json_rpc_error(code: int, message: str, message_id: int = 1) -> str:
    """Create a JSON-RPC 2.0 error response string."""
    response = {
        "jsonrpc": "2.0",
        "id": message_id,
        "error": {
            "code": code,
            "message": message
        }
    }
    return json.dumps(response) + "\n"


async def create_async_mock_generator(items: List[Any]):
    """Create an async generator that yields items."""
    for item in items:
        yield item
