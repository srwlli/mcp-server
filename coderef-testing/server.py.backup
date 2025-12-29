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

ANALYSIS_TOOLS: List[Tool] = [
    {
        "name": "analyze_coverage",
        "description": "Analyze code coverage metrics and gaps",
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
        "name": "detect_flaky_tests",
        "description": "Find tests that fail intermittently",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Path to project"
                },
                "runs": {
                    "type": "integer",
                    "description": "Number of runs to analyze (default: 5)"
                }
            },
            "required": ["project_path"]
        }
    },
    {
        "name": "analyze_test_performance",
        "description": "Analyze test execution speed and identify slow tests",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Path to project"
                },
                "threshold": {
                    "type": "number",
                    "description": "Slowness threshold in seconds (default: 1.0)"
                }
            },
            "required": ["project_path"]
        }
    },
    {
        "name": "validate_test_health",
        "description": "Perform overall test suite health check",
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
    }
]

# Register all tools
ALL_TOOLS = DISCOVERY_TOOLS + EXECUTION_TOOLS + MANAGEMENT_TOOLS + ANALYSIS_TOOLS


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List all available tools."""
    return ALL_TOOLS


# ============================================================================
# Tool Handlers
# ============================================================================

@server.call_tool()
async def handle_tool_call(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls - route to appropriate handler."""
    try:
        if name == "discover_tests":
            return await handle_discover_tests(arguments)
        elif name == "list_test_frameworks":
            return await handle_list_frameworks(arguments)
        elif name == "run_all_tests":
            return await handle_run_all_tests(arguments)
        elif name == "run_test_file":
            return await handle_run_test_file(arguments)
        elif name == "run_test_category":
            return await handle_run_test_category(arguments)
        elif name == "run_tests_in_parallel":
            return await handle_run_tests_parallel(arguments)
        elif name == "get_test_results":
            return await handle_get_test_results(arguments)
        elif name == "aggregate_results":
            return await handle_aggregate_results(arguments)
        elif name == "generate_test_report":
            return await handle_generate_test_report(arguments)
        elif name == "compare_test_runs":
            return await handle_compare_test_runs(arguments)
        elif name == "analyze_coverage":
            return await handle_analyze_coverage(arguments)
        elif name == "detect_flaky_tests":
            return await handle_detect_flaky_tests(arguments)
        elif name == "analyze_test_performance":
            return await handle_analyze_test_performance(arguments)
        elif name == "validate_test_health":
            return await handle_validate_test_health(arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    except Exception as e:
        logger.error(f"Error handling tool {name}: {e}", exc_info=True)
        return [TextContent(type="text", text=f"Error: {str(e)}")]


# Discovery handlers
async def handle_discover_tests(args: Dict[str, Any]) -> List[TextContent]:
    """Handle discover_tests tool call - discover and list all tests."""
    from src.framework_detector import detect_frameworks
    from pathlib import Path

    project_path = args.get("project_path")
    logger.info(f"Discovering tests in {project_path}")

    try:
        # Detect frameworks
        frameworks = detect_frameworks(project_path)

        # Find test files
        test_files = []
        proj_path = Path(project_path)

        for pattern in ["**/test_*.py", "**/*_test.py", "**/*.test.js", "**/*.test.ts", "**/tests/**.rs"]:
            test_files.extend([str(f.relative_to(proj_path)) for f in proj_path.glob(pattern)])

        result = {
            "frameworks": [f.framework.value for f in frameworks],
            "test_count": len(test_files),
            "test_files": sorted(set(test_files))[:20],  # Limit to 20 for display
        }

        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    except Exception as e:
        return [TextContent(type="text", text=f"Error discovering tests: {str(e)}")]


async def handle_list_frameworks(args: Dict[str, Any]) -> List[TextContent]:
    """Handle list_test_frameworks tool call - list detected frameworks."""
    from src.framework_detector import detect_frameworks

    project_path = args.get("project_path")
    logger.info(f"Listing frameworks in {project_path}")

    try:
        frameworks = detect_frameworks(project_path)

        result = {
            "framework_count": len(frameworks),
            "frameworks": [
                {
                    "name": f.framework.value,
                    "version": f.version,
                    "config_file": f.config_file,
                    "detected_at": f.detected_at.isoformat(),
                }
                for f in frameworks
            ]
        }

        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    except Exception as e:
        return [TextContent(type="text", text=f"Error listing frameworks: {str(e)}")]


# Execution handlers
async def handle_run_all_tests(args: Dict[str, Any]) -> List[TextContent]:
    """Handle run_all_tests tool call - execute full test suite."""
    from src.test_runner import TestRunner, TestRunRequest

    project_path = args.get("project_path")
    framework_str = args.get("framework")
    timeout = args.get("timeout", 300)
    workers = args.get("parallel_workers", 4)

    logger.info(f"Running all tests in {project_path}")

    try:
        runner = TestRunner()
        framework = TestFramework(framework_str) if framework_str else None

        req = TestRunRequest(
            project_path=project_path,
            framework=framework,
            timeout_seconds=timeout,
            max_workers=workers,
        )

        result = await runner.run_tests(req)

        return [TextContent(type="text", text=json.dumps({
            "framework": result.framework.value,
            "summary": result.summary,
            "test_count": len(result.tests),
        }, indent=2))]
    except Exception as e:
        return [TextContent(type="text", text=f"Error running tests: {str(e)}")]


async def handle_run_test_file(args: Dict[str, Any]) -> List[TextContent]:
    """Handle run_test_file tool call - run specific test file."""
    from src.test_runner import TestRunner, TestRunRequest

    project_path = args.get("project_path")
    test_file = args.get("test_file")

    logger.info(f"Running test file {test_file} in {project_path}")

    try:
        runner = TestRunner()
        req = TestRunRequest(
            project_path=project_path,
            test_file=test_file,
        )

        result = await runner.run_tests(req)

        return [TextContent(type="text", text=json.dumps({
            "test_file": test_file,
            "summary": result.summary,
        }, indent=2))]
    except Exception as e:
        return [TextContent(type="text", text=f"Error running test file: {str(e)}")]


async def handle_run_test_category(args: Dict[str, Any]) -> List[TextContent]:
    """Handle run_test_category tool call - run tests matching pattern."""
    from src.test_runner import TestRunner, TestRunRequest

    project_path = args.get("project_path")
    pattern = args.get("pattern")

    logger.info(f"Running tests matching {pattern} in {project_path}")

    try:
        runner = TestRunner()
        req = TestRunRequest(
            project_path=project_path,
            test_pattern=pattern,
        )

        result = await runner.run_tests(req)

        return [TextContent(type="text", text=json.dumps({
            "pattern": pattern,
            "summary": result.summary,
        }, indent=2))]
    except Exception as e:
        return [TextContent(type="text", text=f"Error running tests by pattern: {str(e)}")]


async def handle_run_tests_parallel(args: Dict[str, Any]) -> List[TextContent]:
    """Handle run_tests_in_parallel tool call - parallel execution."""
    from src.test_runner import TestRunner, TestRunRequest

    project_path = args.get("project_path")
    workers = args.get("parallel_workers", 4)

    logger.info(f"Running tests in parallel ({workers} workers) in {project_path}")

    try:
        runner = TestRunner()
        req = TestRunRequest(
            project_path=project_path,
            max_workers=workers,
        )

        result = await runner.run_tests(req)

        return [TextContent(type="text", text=json.dumps({
            "workers": workers,
            "summary": result.summary,
        }, indent=2))]
    except Exception as e:
        return [TextContent(type="text", text=f"Error running tests in parallel: {str(e)}")]


# Management handlers
async def handle_get_test_results(args: Dict[str, Any]) -> List[TextContent]:
    """Handle get_test_results tool call - retrieve archived results."""
    from src.test_aggregator import TestAggregator

    project_path = args.get("project_path")

    logger.info(f"Getting test results for {project_path}")

    try:
        aggregator = TestAggregator()
        archived = aggregator.get_archived_results()

        return [TextContent(type="text", text=json.dumps({
            "total_runs": len(archived),
            "latest_runs": archived[:5],
        }, indent=2, default=str))]
    except Exception as e:
        return [TextContent(type="text", text=f"Error getting results: {str(e)}")]


async def handle_aggregate_results(args: Dict[str, Any]) -> List[TextContent]:
    """Handle aggregate_results tool call - aggregate multiple runs."""
    from src.test_aggregator import TestAggregator

    project_path = args.get("project_path")
    logger.info(f"Aggregating results for {project_path}")

    try:
        aggregator = TestAggregator()
        archived = aggregator.get_archived_results()

        if archived:
            return [TextContent(type="text", text=json.dumps({
                "archived_runs": len(archived),
                "latest_run": archived[0] if archived else None,
            }, indent=2, default=str))]
        else:
            return [TextContent(type="text", text="No archived results found")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error aggregating results: {str(e)}")]


async def handle_generate_test_report(args: Dict[str, Any]) -> List[TextContent]:
    """Handle generate_test_report tool call - generate formatted report."""
    from src.test_aggregator import TestAggregator

    project_path = args.get("project_path")
    format_type = args.get("format", "markdown")

    logger.info(f"Generating {format_type} report for {project_path}")

    try:
        aggregator = TestAggregator()
        latest = aggregator.get_latest_result()

        if latest:
            return [TextContent(type="text", text=json.dumps({
                "format": format_type,
                "generated_at": latest.get("archived_at"),
                "summary": latest.get("summary"),
            }, indent=2))]
        else:
            return [TextContent(type="text", text="No test results to report")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error generating report: {str(e)}")]


async def handle_compare_test_runs(args: Dict[str, Any]) -> List[TextContent]:
    """Handle compare_test_runs tool call - compare two test runs."""
    from src.result_analyzer import ResultAnalyzer

    project_path = args.get("project_path")
    date1 = args.get("date1")
    date2 = args.get("date2")

    logger.info(f"Comparing test runs for {project_path} ({date1} vs {date2})")

    try:
        return [TextContent(type="text", text=json.dumps({
            "comparison": f"Comparing {date1} vs {date2}",
            "message": "Comparison functionality available via analyzer module",
        }, indent=2))]
    except Exception as e:
        return [TextContent(type="text", text=f"Error comparing runs: {str(e)}")]


# Analysis handlers
async def handle_analyze_coverage(args: Dict[str, Any]) -> List[TextContent]:
    """Handle analyze_coverage tool call - analyze code coverage."""
    from src.result_analyzer import ResultAnalyzer
    from src.test_runner import TestRunner, TestRunRequest

    project_path = args.get("project_path")
    logger.info(f"Analyzing coverage for {project_path}")

    try:
        runner = TestRunner()
        req = TestRunRequest(project_path=project_path)
        result = await runner.run_tests(req)

        analyzer = ResultAnalyzer()
        coverage = analyzer.analyze_coverage(result)

        return [TextContent(type="text", text=json.dumps(coverage, indent=2))]
    except Exception as e:
        return [TextContent(type="text", text=f"Error analyzing coverage: {str(e)}")]


async def handle_detect_flaky_tests(args: Dict[str, Any]) -> List[TextContent]:
    """Handle detect_flaky_tests tool call - find flaky tests."""
    from src.result_analyzer import ResultAnalyzer
    from src.test_aggregator import TestAggregator

    project_path = args.get("project_path")
    runs = args.get("runs", 5)

    logger.info(f"Detecting flaky tests in {project_path} ({runs} runs)")

    try:
        aggregator = TestAggregator()
        archived = aggregator.get_archived_results()[:runs]

        if archived:
            analyzer = ResultAnalyzer()
            # Note: Would need actual UnifiedTestResults objects
            return [TextContent(type="text", text=json.dumps({
                "runs_analyzed": len(archived),
                "message": "Flaky test detection requires multiple UnifiedTestResults",
            }, indent=2))]
        else:
            return [TextContent(type="text", text="No test results available for flaky detection")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error detecting flaky tests: {str(e)}")]


async def handle_analyze_test_performance(args: Dict[str, Any]) -> List[TextContent]:
    """Handle analyze_test_performance tool call - analyze execution speed."""
    from src.result_analyzer import ResultAnalyzer
    from src.test_runner import TestRunner, TestRunRequest

    project_path = args.get("project_path")
    threshold = args.get("threshold", 1.0)

    logger.info(f"Analyzing performance in {project_path} (threshold: {threshold}s)")

    try:
        runner = TestRunner()
        req = TestRunRequest(project_path=project_path)
        result = await runner.run_tests(req)

        analyzer = ResultAnalyzer()
        performance = analyzer.analyze_performance(result)

        return [TextContent(type="text", text=json.dumps(performance, indent=2))]
    except Exception as e:
        return [TextContent(type="text", text=f"Error analyzing performance: {str(e)}")]


async def handle_validate_test_health(args: Dict[str, Any]) -> List[TextContent]:
    """Handle validate_test_health tool call - check overall test health."""
    from src.result_analyzer import ResultAnalyzer
    from src.test_runner import TestRunner, TestRunRequest

    project_path = args.get("project_path")
    logger.info(f"Validating test health for {project_path}")

    try:
        runner = TestRunner()
        req = TestRunRequest(project_path=project_path)
        result = await runner.run_tests(req)

        analyzer = ResultAnalyzer()
        health = analyzer.validate_test_health(result)

        return [TextContent(type="text", text=json.dumps(health, indent=2))]
    except Exception as e:
        return [TextContent(type="text", text=f"Error validating test health: {str(e)}")]


# ============================================================================
# Server Initialization
# ============================================================================

async def main():
    """Start the MCP server."""
    logger.info("Starting coderef-testing MCP server")
    logger.info(f"Registered {len(ALL_TOOLS)} tools")
    async with server:
        logger.info("Server running - listening for requests")
        await asyncio.sleep(float('inf'))


if __name__ == "__main__":
    asyncio.run(main())
