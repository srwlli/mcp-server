#!/usr/bin/env python3
"""MCP Server for CodeRef service.

This module implements the Model Context Protocol (MCP) server for CodeRef,
exposing 6 tools for semantic code reference analysis and validation.
"""

import logging
import asyncio
import json
from typing import Any, Dict
from datetime import datetime

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, Resource, Prompt, PromptArgument, PromptMessage

from logger_config import setup_logging, get_logger
from tool_handlers import TOOL_HANDLERS
from constants import SERVICE_NAME, SERVICE_VERSION

# Setup logging
setup_logging()
logger = get_logger(__name__)


# ============================================================================
# Tool Schema Definitions
# ============================================================================

TOOL_SCHEMAS: Dict[str, Dict[str, Any]] = {
    "mcp__coderef__query": {
        "description": "Query CodeRef elements by reference or pattern",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "CodeRef reference or search pattern"
                },
                "filter": {
                    "type": "object",
                    "description": "Optional filter criteria",
                    "properties": {
                        "type_designators": {"type": "array"},
                        "path_pattern": {"type": "string"},
                        "metadata_filters": {"type": "object"},
                    }
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum results (1-1000)",
                    "default": 100
                },
                "include_relationships": {
                    "type": "boolean",
                    "description": "Include relationship information",
                    "default": True
                },
                "include_metadata": {
                    "type": "boolean",
                    "description": "Include element metadata",
                    "default": True
                },
                "include_source": {
                    "type": "boolean",
                    "description": "Include source code snippets",
                    "default": False
                }
            },
            "required": ["query"]
        }
    },
    "mcp__coderef__analyze": {
        "description": "Perform deep analysis on CodeRef elements (impact, coverage, complexity)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "reference": {
                    "type": "string",
                    "description": "CodeRef reference to analyze"
                },
                "analysis_type": {
                    "type": "string",
                    "enum": ["impact", "deep", "coverage", "complexity"],
                    "description": "Type of analysis to perform",
                    "default": "impact"
                },
                "depth": {
                    "type": "integer",
                    "description": "Analysis depth (1-10)",
                    "default": 3
                },
                "include_test_impact": {
                    "type": "boolean",
                    "description": "Include test-related impacts",
                    "default": True
                }
            },
            "required": ["reference"]
        }
    },
    "mcp__coderef__validate": {
        "description": "Validate CodeRef reference format and structure",
        "inputSchema": {
            "type": "object",
            "properties": {
                "reference": {
                    "type": "string",
                    "description": "Single CodeRef reference to validate"
                },
                "references": {
                    "type": "array",
                    "description": "Multiple references to validate",
                    "items": {"type": "string"}
                },
                "validate_existence": {
                    "type": "boolean",
                    "description": "Check if element exists",
                    "default": False
                }
            }
        }
    },
    "mcp__coderef__batch_validate": {
        "description": "Validate multiple CodeRef references in batch (sequential or parallel)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "references": {
                    "type": "array",
                    "description": "References to validate",
                    "items": {"type": "string"}
                },
                "parallel": {
                    "type": "boolean",
                    "description": "Process in parallel",
                    "default": True
                },
                "max_workers": {
                    "type": "integer",
                    "description": "Max concurrent workers",
                    "default": 5
                },
                "timeout_ms": {
                    "type": "integer",
                    "description": "Timeout in milliseconds",
                    "default": 5000
                }
            },
            "required": ["references"]
        }
    },
    "mcp__coderef__generate_docs": {
        "description": "Generate documentation for CodeRef elements (simplified, no UDS)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "reference": {
                    "type": "string",
                    "description": "CodeRef reference to document"
                },
                "doc_type": {
                    "type": "string",
                    "enum": ["summary", "detailed", "api"],
                    "description": "Type of documentation",
                    "default": "summary"
                },
                "include_examples": {
                    "type": "boolean",
                    "description": "Include code examples",
                    "default": True
                },
                "include_metadata": {
                    "type": "boolean",
                    "description": "Include element metadata",
                    "default": True
                }
            },
            "required": ["reference"]
        }
    },
    "mcp__coderef__audit": {
        "description": "Audit CodeRef elements for validation, coverage, and performance",
        "inputSchema": {
            "type": "object",
            "properties": {
                "scope": {
                    "type": "string",
                    "enum": ["all", "element", "path", "type"],
                    "description": "Audit scope",
                    "default": "all"
                },
                "target": {
                    "type": "string",
                    "description": "Optional target reference or path"
                },
                "audit_type": {
                    "type": "string",
                    "enum": ["validation", "coverage", "performance"],
                    "description": "Type of audit",
                    "default": "validation"
                },
                "include_issues": {
                    "type": "boolean",
                    "description": "Include detailed issue list",
                    "default": True
                }
            }
        }
    },
    "mcp__coderef__nl_query": {
        "description": "Natural language query interface for CodeRef - Ask questions in plain English",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural language query (e.g., 'what calls the login function?', 'find all tests for auth module')"
                },
                "context": {
                    "type": "object",
                    "description": "Optional context for disambiguating queries",
                    "properties": {
                        "current_file": {
                            "type": "string",
                            "description": "Current file path being worked on"
                        },
                        "current_element": {
                            "type": "string",
                            "description": "Current element reference (CodeRef format)"
                        },
                        "language": {
                            "type": "string",
                            "description": "Programming language context (ts, js, py, etc.)"
                        }
                    }
                },
                "format": {
                    "type": "string",
                    "enum": ["natural", "structured", "json"],
                    "description": "Response format preference",
                    "default": "natural"
                }
            },
            "required": ["query"]
        }
    },
    "mcp__coderef__scan_realtime": {
        "description": "Scan source code in real-time using the CodeRef CLI and update the index",
        "inputSchema": {
            "type": "object",
            "properties": {
                "source_dir": {
                    "type": "string",
                    "description": "Directory to scan (absolute or relative path)"
                },
                "languages": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Languages to scan (e.g., ['ts', 'tsx', 'js', 'jsx', 'py'])",
                    "default": ["ts", "tsx", "js", "jsx"]
                },
                "analyzer": {
                    "type": "string",
                    "enum": ["regex", "ast"],
                    "description": "Scanner type: 'regex' (fast) or 'ast' (99% precision with relationships)",
                    "default": "ast"
                },
                "exclude": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Glob patterns to exclude (e.g., ['**/node_modules/**', '**/dist/**'])",
                    "default": ["**/node_modules/**", "**/dist/**", "**/.git/**"]
                },
                "update_index": {
                    "type": "boolean",
                    "description": "Whether to update the QueryExecutor index with scan results",
                    "default": True
                },
                "force_rescan": {
                    "type": "boolean",
                    "description": "Force full rescan ignoring cache",
                    "default": False
                }
            },
            "required": ["source_dir"]
        }
    },
}


# ============================================================================
# MCP Server Implementation
# ============================================================================

# Create server instance
app = Server(SERVICE_NAME)


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available CodeRef tools.

    Returns:
        list[Tool]: Available tools with schemas
    """
    tools = []
    for tool_name, schema in TOOL_SCHEMAS.items():
        tools.append(
            Tool(
                name=tool_name,
                description=schema.get("description", ""),
                inputSchema=schema.get("inputSchema", {})
            )
        )

    logger.debug(f"Listing {len(tools)} tools")
    return tools


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool invocation.

    Args:
        name: Tool name
        arguments: Tool arguments

    Returns:
        list[TextContent]: Tool results
    """
    logger.debug(f"Tool invoked: {name} with args: {arguments}")

    # Get handler
    handler = TOOL_HANDLERS.get(name)
    if not handler:
        error_msg = f"Unknown tool: {name}"
        logger.error(error_msg)
        return [
            TextContent(
                type="text",
                text=_error_json("UNKNOWN_TOOL", error_msg)
            )
        ]

    try:
        # Call handler (may be async or sync)
        if asyncio.iscoroutinefunction(handler):
            result = await handler(arguments)
        else:
            result = handler(arguments)

        # Convert result to JSON string
        result_text = json.dumps(result, indent=2, default=str)

        return [
            TextContent(
                type="text",
                text=result_text
            )
        ]

    except Exception as e:
        logger.error(f"Tool error in {name}: {e}", exc_info=True)
        return [
            TextContent(
                type="text",
                text=_error_json("TOOL_EXECUTION_ERROR", str(e))
            )
        ]


# ============================================================================
# MCP Resources Implementation
# ============================================================================

@app.list_resources()
async def list_resources() -> list[Resource]:
    """List available CodeRef resources.

    Returns:
        list[Resource]: Available read-only resources for AI agents
    """
    resources = [
        Resource(
            uri="coderef://graph/current",
            name="Current Dependency Graph",
            description="Complete dependency graph with nodes (elements) and edges (relationships)",
            mimeType="application/json"
        ),
        Resource(
            uri="coderef://stats/summary",
            name="Codebase Statistics",
            description="Aggregate statistics including element counts by type/language, complexity metrics",
            mimeType="application/json"
        ),
        Resource(
            uri="coderef://index/elements",
            name="Element Index",
            description="Complete index of all code elements with metadata",
            mimeType="application/json"
        ),
        Resource(
            uri="coderef://coverage/test",
            name="Test Coverage Map",
            description="Test coverage mapping showing covered and uncovered elements",
            mimeType="application/json"
        )
    ]

    logger.debug(f"Listing {len(resources)} resources")
    return resources


@app.read_resource()
async def read_resource(uri: str) -> str:
    """Read a specific resource by URI.

    Args:
        uri: Resource URI (e.g., "coderef://graph/current")

    Returns:
        str: JSON-formatted resource data

    Raises:
        ValueError: If URI is unknown or invalid
    """
    logger.debug(f"Reading resource: {uri}")

    try:
        if uri == "coderef://graph/current":
            # Import here to avoid circular dependencies
            from tool_handlers import get_dependency_graph
            graph_data = await get_dependency_graph()
            return json.dumps(graph_data, indent=2, default=str)

        elif uri == "coderef://stats/summary":
            from tool_handlers import get_statistics
            stats_data = await get_statistics()
            return json.dumps(stats_data, indent=2, default=str)

        elif uri == "coderef://index/elements":
            from tool_handlers import get_all_elements
            index_data = await get_all_elements()
            return json.dumps(index_data, indent=2, default=str)

        elif uri == "coderef://coverage/test":
            from tool_handlers import get_test_coverage
            coverage_data = await get_test_coverage()
            return json.dumps(coverage_data, indent=2, default=str)

        else:
            error_msg = f"Unknown resource URI: {uri}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    except Exception as e:
        logger.error(f"Resource read error for {uri}: {e}", exc_info=True)
        # Return error as JSON for consistency
        return json.dumps({
            "status": "error",
            "error_code": "RESOURCE_READ_ERROR",
            "message": str(e),
            "uri": uri,
            "timestamp": datetime.utcnow().isoformat()
        }, indent=2)


# ============================================================================
# MCP Prompts Implementation
# ============================================================================

@app.list_prompts()
async def list_prompts() -> list[Prompt]:
    """List available CodeRef workflow prompts.

    Returns:
        list[Prompt]: Available pre-built workflow templates
    """
    prompts = [
        Prompt(
            name="analyze_function",
            description="Deep analysis of a function including dependencies, callers, impact, and test coverage",
            arguments=[
                PromptArgument(
                    name="function_name",
                    description="Name of the function to analyze",
                    required=True
                ),
                PromptArgument(
                    name="include_tests",
                    description="Whether to include test coverage analysis (true/false)",
                    required=False
                )
            ]
        ),
        Prompt(
            name="review_changes",
            description="Review code changes in a file and identify impacts with risk assessment",
            arguments=[
                PromptArgument(
                    name="file_path",
                    description="Path to the changed file",
                    required=True
                ),
                PromptArgument(
                    name="changed_elements",
                    description="Comma-separated list of changed element names",
                    required=True
                )
            ]
        ),
        Prompt(
            name="refactor_plan",
            description="Generate a safe refactoring plan with type-specific instructions and validation steps",
            arguments=[
                PromptArgument(
                    name="element_id",
                    description="CodeRef ID of element to refactor (e.g., @Fn/path/file#element:line)",
                    required=True
                ),
                PromptArgument(
                    name="refactor_type",
                    description="Type of refactoring: rename, extract, inline, or move",
                    required=True
                )
            ]
        ),
        Prompt(
            name="find_dead_code",
            description="Identify potentially unused code elements with confidence scoring",
            arguments=[
                PromptArgument(
                    name="directory",
                    description="Directory to analyze (defaults to current directory)",
                    required=False
                ),
                PromptArgument(
                    name="min_confidence",
                    description="Minimum confidence threshold 0-1 (default: 0.8)",
                    required=False
                )
            ]
        )
    ]

    logger.debug(f"Listing {len(prompts)} prompts")
    return prompts


@app.get_prompt()
async def get_prompt(name: str, arguments: dict) -> PromptMessage:
    """Get a specific prompt with arguments filled in.

    Args:
        name: Prompt name
        arguments: Prompt arguments

    Returns:
        PromptMessage: Populated prompt template

    Raises:
        ValueError: If prompt name is unknown or required arguments missing
    """
    logger.debug(f"Getting prompt: {name} with args: {arguments}")

    if name == "analyze_function":
        function_name = arguments.get("function_name")
        if not function_name:
            raise ValueError("Missing required argument: function_name")

        include_tests = arguments.get("include_tests", "true").lower() == "true"

        content = f"""Analyze the function '{function_name}' using CodeRef tools:

1. Query what calls this function:
   Use mcp__coderef__query with:
   - query: "{function_name}"
   - filter: {{"query_type": "incoming_calls"}}

2. Query what this function calls:
   Use mcp__coderef__query with:
   - query: "{function_name}"
   - filter: {{"query_type": "outgoing_calls"}}

3. Analyze impact if this function changes:
   Use mcp__coderef__analyze with:
   - reference: (from step 1 results)
   - analysis_type: "impact"
   - depth: 3

{"4. Check test coverage:\n   Use mcp__coderef__query to find tests that reference this function" if include_tests else ""}

Provide a summary including:
- Function purpose and complexity
- Direct callers and callees
- Impact radius (how many elements affected by changes)
- Risk assessment for modifications (LOW/MEDIUM/HIGH/CRITICAL)
{"- Test coverage status" if include_tests else ""}
"""

        return PromptMessage(role="user", content=content)

    elif name == "review_changes":
        file_path = arguments.get("file_path")
        changed_elements = arguments.get("changed_elements")

        if not file_path:
            raise ValueError("Missing required argument: file_path")
        if not changed_elements:
            raise ValueError("Missing required argument: changed_elements")

        content = f"""Review code changes in {file_path}:

Changed elements: {changed_elements}

For each changed element:

1. Validate existing references:
   Use mcp__coderef__validate with the file path

2. Analyze impact:
   Use mcp__coderef__analyze for each changed element with analysis_type: "impact"

3. Check for breaking changes:
   - Did function signatures change?
   - Were any elements removed?
   - Did return types change?
   - Did parameter types or order change?

4. Identify affected tests:
   Query for test files that reference these elements

Provide:
- Risk level (LOW/MEDIUM/HIGH/CRITICAL)
- List of affected downstream code
- Suggested actions (update tests, update docs, notify team, etc.)
- Breaking change warnings
"""

        return PromptMessage(role="user", content=content)

    elif name == "refactor_plan":
        element_id = arguments.get("element_id")
        refactor_type = arguments.get("refactor_type")

        if not element_id:
            raise ValueError("Missing required argument: element_id")
        if not refactor_type:
            raise ValueError("Missing required argument: refactor_type")

        if refactor_type not in ["rename", "extract", "inline", "move"]:
            raise ValueError(f"Invalid refactor_type: {refactor_type}. Must be: rename, extract, inline, or move")

        content = f"""Generate a refactoring plan for {element_id}:

Refactoring type: {refactor_type}

Step 1 - Analyze current state:
   Use mcp__coderef__analyze with depth=5 to find all dependencies

Step 2 - Identify risks:
   - How many elements depend on this?
   - Are there circular dependencies?
   - Is this element exported/public?
   - Check test coverage

Step 3 - Generate plan based on refactor type '{refactor_type}':

"""

        if refactor_type == "rename":
            content += """   RENAME Strategy:
   - List all references to update
   - Check for string references in tests/docs
   - Verify no name conflicts with new name
   - Update imports/exports
"""
        elif refactor_type == "extract":
            content += """   EXTRACT Strategy:
   - Identify code to extract
   - Determine new element signature
   - Update callers to use new element
   - Ensure proper scoping
"""
        elif refactor_type == "inline":
            content += """   INLINE Strategy:
   - Verify element is only called from one place
   - Check if inlining increases complexity
   - Ensure no side effects
"""
        elif refactor_type == "move":
            content += """   MOVE Strategy:
   - Identify new location
   - Update all imports
   - Check for circular dependencies
   - Update module exports
"""

        content += """
Step 4 - Provide ordered checklist:
   1. [ ] Run tests before refactoring
   2. [ ] Make changes in order
   3. [ ] Update tests
   4. [ ] Run tests after refactoring
   5. [ ] Update documentation
   6. [ ] Verify no broken references
"""

        return PromptMessage(role="user", content=content)

    elif name == "find_dead_code":
        directory = arguments.get("directory", ".")
        min_confidence = float(arguments.get("min_confidence", "0.8"))

        content = f"""Find potentially unused code in {directory}:

Use mcp__coderef__audit to get:
- All elements in directory
- Reference counts for each element

Criteria for "dead code" (confidence >= {min_confidence}):
- Zero incoming references AND not exported
- Zero incoming references AND not in public API
- Only referenced in commented code
- Only referenced in other dead code (recursive check)

Exceptions (NOT dead code):
- Entry points (main functions, exports)
- Test utilities and fixtures
- CLI command handlers
- Event handlers and callbacks
- React components (may be lazy loaded)
- Configuration objects

Output format:
- File path and element name
- Confidence score (0-1)
- Reason (no refs, only dead refs, etc.)
- Recommendation (delete, investigate, keep)

Sort by confidence (highest first).
"""

        return PromptMessage(role="user", content=content)

    else:
        raise ValueError(f"Unknown prompt: {name}")


def _error_json(error_code: str, message: str) -> str:
    """Generate error JSON response.

    Args:
        error_code: Error code
        message: Error message

    Returns:
        str: JSON error response
    """
    return json.dumps({
        "status": "error",
        "error_code": error_code,
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    })


# ============================================================================
# Server Entry Point
# ============================================================================

async def main() -> None:
    """Run the MCP server."""
    logger.info(f"Starting {SERVICE_NAME} v{SERVICE_VERSION}")
    logger.info(f"Available tools: {', '.join(TOOL_HANDLERS.keys())}")
    logger.info(f"Server ready with {len(TOOL_HANDLERS)} tools")

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
