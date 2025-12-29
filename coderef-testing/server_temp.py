#!/usr/bin/env python3
"""
coderef-testing: Universal MCP server for test orchestration, execution, and reporting.

Provides framework-agnostic test discovery, execution, aggregation, and analysis tools
for any project using pytest, jest, vitest, cargo, mocha, or custom test frameworks.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.types import Tool, TextContent

from src.models import (
    TestFramework,
    TestRunRequest,
    UnifiedTestResults,
    FrameworkDetectionResult,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize MCP server
server = Server("coderef-testing")


# ============================================================================
# Tool Definitions
# ============================================================================

DISCOVERY_TOOLS: List[Tool] = [
    {
        "name": "discover_tests",
        "description": "Find all tests in a project and auto-detect test framework",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Path to project to scan for tests"
                }
            },
            "required": ["project_path"]
        }
    },
    {
        "name": "list_test_frameworks",
        "description": "List all detected test frameworks and their versions",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Path to project to scan"
                }
            },
            "required": ["project_path"]
        }
    }
]

EXECUTION_TOOLS: List[Tool] = [
    {
        "name": "run_all_tests",
        "description": "Execute the entire test suite in a project",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Path to project"
                },
                "framework": {
                    "type": "string",
                    "enum": ["pytest", "jest", "vitest", "cargo", "mocha"],
                    "description": "Framework (auto-detected if not specified)"
                },
                "parallel_workers": {
                    "type": "integer",
                    "description": "Number of parallel workers (default: 4)"
                },
                "timeout": {
                    "type": "integer",
                    "description": "Timeout in seconds (default: 300)"
                }
            },
            "required": ["project_path"]
        }
    },
    {
        "name": "run_test_file",
        "description": "Run tests from a specific test file",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Path to project"
                },
                "test_file": {
                    "type": "string",
                    "description": "Path to test file relative to project"
                }
            },
            "required": ["project_path", "test_file"]
        }
    },
    {
        "name": "run_test_category",
        "description": "Run tests matching a pattern or tag",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Path to project"
                },
                "pattern": {
                    "type": "string",
                    "description": "Pattern to match tests (e.g., 'test_auth' or '@tag:integration')"
                }
            },
            "required": ["project_path", "pattern"]
        }
    },
    {
        "name": "run_tests_in_parallel",
        "description": "Execute tests with explicit parallelization control",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Path to project"
                },
                "parallel_workers": {
                    "type": "integer",
                    "description": "Number of parallel workers"
                }
            },
            "required": ["project_path", "parallel_workers"]
        }
    }
]

MANAGEMENT_TOOLS: List[Tool] = [
    {
        "name": "get_test_results",
        "description": "Retrieve stored test results",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Path to project"
                },
                "date": {
                    "type": "string",
                    "description": "Date to query (YYYY-MM-DD, default: latest)"
                }
            },
            "required": ["project_path"]
        }
    },
    {
        "name": "aggregate_results",
        "description": "Aggregate results across multiple test runs",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Path to project"
                }
            },
            "required": ["project_path"]
        }
    },
    {
        "name": "generate_test_report",
        "description": "Generate test report in specified format",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Path to project"
                },
                "format": {
                    "type": "string",
                    "enum": ["markdown", "html", "json"],
                    "description": "Report format (default: markdown)"
                }
            },
            "required": ["project_path"]
        }
    },
    {
        "name": "compare_test_runs",
        "description": "Compare results between two test runs",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Path to project"
                },
                "date1": {
                    "type": "string",
                    "description": "First date to compare (YYYY-MM-DD)"
                },
                "date2": {
                    "type": "string",
                    "description": "Second date to compare (YYYY-MM-DD)"
                }
            },
            "required": ["project_path", "date1", "date2"]
        }
    }
]

