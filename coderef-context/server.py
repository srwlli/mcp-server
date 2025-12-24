#!/usr/bin/env python3
"""
CodeRef Context MCP Server

Exposes @coderef/core CLI tools as standardized MCP tools for Claude agents.

Tools exposed:
- /scan - Discover code elements
- /query - Query relationships (what-calls, what-imports, shortest-path)
- /impact - Analyze change impact
- /complexity - Function/class complexity metrics
- /patterns - Discover patterns and test gaps
- /coverage - Test coverage analysis
- /context - Generate comprehensive codebase context
- /validate - Validate CodeRef2 references
- /drift - Detect drift between index and code
- /diagram - Generate dependency diagrams

Architecture:
- Each tool wraps a @coderef/core CLI command
- Subprocess calls for isolation and reliability
- JSON parsing for agent consumption
"""

__version__ = "1.0.0"
__mcp_version__ = "1.0"

import os
import subprocess
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

# Get CLI path from environment or use default
DEFAULT_CLI_PATH = os.path.expandvars(
    r"C:\Users\willh\Desktop\projects\coderef-system\packages\cli"
)
CLI_PATH = os.environ.get("CODEREF_CLI_PATH", DEFAULT_CLI_PATH)
CLI_BIN = os.path.join(CLI_PATH, "dist", "cli.js")

# Initialize MCP server
app = Server("coderef-context")

print(f"[coderef-context] Initializing MCP server v{__version__}")
print(f"[coderef-context] CLI path: {CLI_BIN}")
print(f"[coderef-context] CLI exists: {os.path.exists(CLI_BIN)}")


# ============================================================================
# Tool Definitions
# ============================================================================

@app.list_tools()
async def list_tools() -> List[Tool]:
    """List all available CodeRef tools."""
    return [
        Tool(
            name="coderef_scan",
            description="Scan project and discover all code elements (functions, classes, components, hooks)",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Absolute path to project root"
                    },
                    "languages": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Languages to scan (default: ts,tsx,js,jsx)",
                        "default": ["ts", "tsx", "js", "jsx"]
                    },
                    "use_ast": {
                        "type": "boolean",
                        "description": "Use AST-based analysis (99% accuracy) vs regex (85%)",
                        "default": True
                    }
                },
                "required": ["project_path"]
            }
        ),
        Tool(
            name="coderef_query",
            description="Query code relationships (what-calls, what-imports, shortest-path, etc)",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Project root"
                    },
                    "query_type": {
                        "type": "string",
                        "enum": ["calls", "calls-me", "imports", "imports-me", "depends-on", "depends-on-me"],
                        "description": "Type of relationship query"
                    },
                    "target": {
                        "type": "string",
                        "description": "Element to query (e.g., 'authenticateUser' or 'AuthService#login')"
                    },
                    "source": {
                        "type": "string",
                        "description": "For path queries: starting element"
                    },
                    "max_depth": {
                        "type": "integer",
                        "description": "Maximum traversal depth",
                        "default": 3
                    }
                },
                "required": ["project_path", "query_type", "target"]
            }
        ),
        Tool(
            name="coderef_impact",
            description="Analyze impact of modifying or deleting a code element",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Project root"
                    },
                    "element": {
                        "type": "string",
                        "description": "Element to analyze (e.g., 'AuthService')"
                    },
                    "operation": {
                        "type": "string",
                        "enum": ["modify", "delete", "refactor"],
                        "description": "Type of change",
                        "default": "modify"
                    },
                    "max_depth": {
                        "type": "integer",
                        "description": "Maximum traversal depth",
                        "default": 3
                    }
                },
                "required": ["project_path", "element"]
            }
        ),
        Tool(
            name="coderef_complexity",
            description="Get complexity metrics for a code element",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Project root"
                    },
                    "element": {
                        "type": "string",
                        "description": "Element to analyze"
                    }
                },
                "required": ["project_path", "element"]
            }
        ),
        Tool(
            name="coderef_patterns",
            description="Discover code patterns and test coverage gaps",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Project root"
                    },
                    "pattern_type": {
                        "type": "string",
                        "description": "Type of pattern to find (optional)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results",
                        "default": 10
                    }
                },
                "required": ["project_path"]
            }
        ),
        Tool(
            name="coderef_coverage",
            description="Analyze test coverage in the codebase",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Project root"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["summary", "detailed"],
                        "description": "Coverage report format",
                        "default": "summary"
                    }
                },
                "required": ["project_path"]
            }
        ),
        Tool(
            name="coderef_context",
            description="Generate comprehensive codebase context (markdown + JSON)",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Project root"
                    },
                    "languages": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Languages to scan",
                        "default": ["ts", "tsx", "js", "jsx"]
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["json", "markdown", "both"],
                        "description": "Output format",
                        "default": "json"
                    }
                },
                "required": ["project_path"]
            }
        ),
        Tool(
            name="coderef_validate",
            description="Validate CodeRef2 references in codebase",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Project root"
                    },
                    "pattern": {
                        "type": "string",
                        "description": "File glob pattern",
                        "default": "**/*.ts"
                    }
                },
                "required": ["project_path"]
            }
        ),
        Tool(
            name="coderef_drift",
            description="Detect drift between CodeRef index and current code",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Project root"
                    },
                    "index_path": {
                        "type": "string",
                        "description": "Path to coderef-index.json",
                        "default": ".coderef-index.json"
                    }
                },
                "required": ["project_path"]
            }
        ),
        Tool(
            name="coderef_diagram",
            description="Generate visual dependency diagrams (Mermaid or Graphviz)",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Project root"
                    },
                    "diagram_type": {
                        "type": "string",
                        "enum": ["dependencies", "calls", "imports", "all"],
                        "description": "Type of diagram",
                        "default": "dependencies"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["mermaid", "dot"],
                        "description": "Output format",
                        "default": "mermaid"
                    },
                    "depth": {
                        "type": "integer",
                        "description": "Maximum depth",
                        "default": 2
                    }
                },
                "required": ["project_path"]
            }
        ),
    ]


# ============================================================================
# Tool Handlers (Placeholder - will implement after CLI_SPEC.md)
# ============================================================================

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls by wrapping @coderef/core CLI commands."""

    try:
        if name == "coderef_scan":
            return await handle_coderef_scan(arguments)
        elif name == "coderef_query":
            return await handle_coderef_query(arguments)
        elif name == "coderef_impact":
            return await handle_coderef_impact(arguments)
        elif name == "coderef_complexity":
            return await handle_coderef_complexity(arguments)
        elif name == "coderef_patterns":
            return await handle_coderef_patterns(arguments)
        elif name == "coderef_coverage":
            return await handle_coderef_coverage(arguments)
        elif name == "coderef_context":
            return await handle_coderef_context(arguments)
        elif name == "coderef_validate":
            return await handle_coderef_validate(arguments)
        elif name == "coderef_drift":
            return await handle_coderef_drift(arguments)
        elif name == "coderef_diagram":
            return await handle_coderef_diagram(arguments)
        else:
            return [TextContent(text=f"Unknown tool: {name}")]

    except Exception as e:
        return [TextContent(text=f"Error calling tool {name}: {str(e)}")]


# ============================================================================
# Tool Handler Implementations (Based on CLI_SPEC.md)
# ============================================================================

async def handle_coderef_scan(args: dict) -> list[TextContent]:
    """Handle /scan tool - Discover code elements."""
    project_path = args.get("project_path", ".")
    languages = args.get("languages", ["ts", "tsx", "js", "jsx"])
    use_ast = args.get("use_ast", False)

    # Build CLI command: coderef scan <sourceDir> --lang ts,tsx --json [--ast]
    cmd = [
        "node", CLI_BIN, "scan",
        project_path,
        "--lang", ",".join(languages),
        "--json"
    ]
    if use_ast:
        cmd.append("--ast")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            return [TextContent(text=f"Error: {result.stderr}")]

        # Parse JSON output
        try:
            data = json.loads(result.stdout)
            return [TextContent(text=json.dumps({
                "success": True,
                "elements_found": len(data) if isinstance(data, list) else 0,
                "elements": data
            }, indent=2))]
        except json.JSONDecodeError as e:
            return [TextContent(text=f"JSON parse error: {str(e)}")]

    except subprocess.TimeoutExpired:
        return [TextContent(text="Error: Scan timeout (30s exceeded)")]
    except Exception as e:
        return [TextContent(text=f"Error: {str(e)}")]


async def handle_coderef_query(args: dict) -> list[TextContent]:
    """Handle /query tool - Query code relationships."""
    project_path = args.get("project_path", ".")
    query_type = args.get("query_type", "depends-on-me")
    target = args.get("target")
    max_depth = args.get("max_depth", 3)

    if not target:
        return [TextContent(text="Error: target parameter is required")]

    # Build CLI command: coderef query <target> --type <type> --depth <depth> --format json
    cmd = [
        "node", CLI_BIN, "query",
        target,
        "--type", query_type,
        "--depth", str(max_depth),
        "--format", "json"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, cwd=project_path)

        if result.returncode != 0:
            return [TextContent(text=f"Error: {result.stderr}")]

        try:
            data = json.loads(result.stdout)
            return [TextContent(text=json.dumps({
                "success": True,
                "query_type": query_type,
                "target": target,
                "results": data
            }, indent=2))]
        except json.JSONDecodeError as e:
            return [TextContent(text=f"JSON parse error: {str(e)}")]

    except subprocess.TimeoutExpired:
        return [TextContent(text="Error: Query timeout (30s exceeded)")]
    except Exception as e:
        return [TextContent(text=f"Error: {str(e)}")]


async def handle_coderef_impact(args: dict) -> list[TextContent]:
    """Handle /impact tool - Analyze change impact."""
    project_path = args.get("project_path", ".")
    element = args.get("element")
    operation = args.get("operation", "modify")
    max_depth = args.get("max_depth", 3)

    if not element:
        return [TextContent(text="Error: element parameter is required")]

    # Build CLI command: coderef impact <target> --depth <depth> --format json
    cmd = [
        "node", CLI_BIN, "impact",
        element,
        "--depth", str(max_depth),
        "--format", "json"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, cwd=project_path)

        if result.returncode != 0:
            return [TextContent(text=f"Error: {result.stderr}")]

        try:
            data = json.loads(result.stdout)
            return [TextContent(text=json.dumps({
                "success": True,
                "element": element,
                "operation": operation,
                "impact": data
            }, indent=2))]
        except json.JSONDecodeError as e:
            return [TextContent(text=f"JSON parse error: {str(e)}")]

    except subprocess.TimeoutExpired:
        return [TextContent(text="Error: Impact analysis timeout (30s exceeded)")]
    except Exception as e:
        return [TextContent(text=f"Error: {str(e)}")]


async def handle_coderef_complexity(args: dict) -> list[TextContent]:
    """Handle /complexity tool - Get complexity metrics."""
    project_path = args.get("project_path", ".")
    element = args.get("element")

    if not element:
        return [TextContent(text="Error: element parameter is required")]

    # Complexity metrics come from context command with element filtering
    # For now, return a note that this should use context command
    cmd = [
        "node", CLI_BIN, "context",
        project_path,
        "--lang", "ts,tsx,js,jsx",
        "--json"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, cwd=project_path)

        if result.returncode != 0:
            return [TextContent(text=f"Error: {result.stderr}")]

        try:
            data = json.loads(result.stdout)
            # Extract complexity info for target element if available
            return [TextContent(text=json.dumps({
                "success": True,
                "element": element,
                "note": "Complexity metrics derived from context generation",
                "context": data
            }, indent=2))]
        except json.JSONDecodeError as e:
            return [TextContent(text=f"JSON parse error: {str(e)}")]

    except subprocess.TimeoutExpired:
        return [TextContent(text="Error: Context generation timeout (60s exceeded)")]
    except Exception as e:
        return [TextContent(text=f"Error: {str(e)}")]


async def handle_coderef_patterns(args: dict) -> list[TextContent]:
    """Handle /patterns tool - Discover patterns."""
    project_path = args.get("project_path", ".")
    pattern_type = args.get("pattern_type", "all")
    limit = args.get("limit", 10)

    # Pattern discovery comes from context command's test pattern analysis
    cmd = [
        "node", CLI_BIN, "context",
        project_path,
        "--lang", "ts,tsx,js,jsx",
        "--json"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, cwd=project_path)

        if result.returncode != 0:
            return [TextContent(text=f"Error: {result.stderr}")]

        try:
            data = json.loads(result.stdout)
            return [TextContent(text=json.dumps({
                "success": True,
                "pattern_type": pattern_type,
                "limit": limit,
                "patterns": data.get("testPatterns", {}) if isinstance(data, dict) else {}
            }, indent=2))]
        except json.JSONDecodeError as e:
            return [TextContent(text=f"JSON parse error: {str(e)}")]

    except subprocess.TimeoutExpired:
        return [TextContent(text="Error: Pattern discovery timeout (60s exceeded)")]
    except Exception as e:
        return [TextContent(text=f"Error: {str(e)}")]


async def handle_coderef_coverage(args: dict) -> list[TextContent]:
    """Handle /coverage tool - Test coverage analysis."""
    project_path = args.get("project_path", ".")
    format_type = args.get("format", "summary")

    # Build CLI command: coderef coverage --format json
    cmd = [
        "node", CLI_BIN, "coverage",
        "--format", "json"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, cwd=project_path)

        if result.returncode != 0:
            return [TextContent(text=f"Error: {result.stderr}")]

        try:
            data = json.loads(result.stdout)
            return [TextContent(text=json.dumps({
                "success": True,
                "coverage": data
            }, indent=2))]
        except json.JSONDecodeError as e:
            return [TextContent(text=f"JSON parse error: {str(e)}")]

    except subprocess.TimeoutExpired:
        return [TextContent(text="Error: Coverage analysis timeout (30s exceeded)")]
    except Exception as e:
        return [TextContent(text=f"Error: {str(e)}")]


async def handle_coderef_context(args: dict) -> list[TextContent]:
    """Handle /context tool - Generate comprehensive context."""
    project_path = args.get("project_path", ".")
    languages = args.get("languages", ["ts", "tsx", "js", "jsx"])
    output_format = args.get("output_format", "json")

    # Build CLI command: coderef context <sourceDir> --lang <langs> --json
    cmd = [
        "node", CLI_BIN, "context",
        project_path,
        "--lang", ",".join(languages)
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=project_path)

        if result.returncode != 0:
            return [TextContent(text=f"Error: {result.stderr}")]

        try:
            data = json.loads(result.stdout)
            return [TextContent(text=json.dumps({
                "success": True,
                "format": output_format,
                "context": data
            }, indent=2))]
        except json.JSONDecodeError as e:
            return [TextContent(text=f"JSON parse error: {str(e)}")]

    except subprocess.TimeoutExpired:
        return [TextContent(text="Error: Context generation timeout (120s exceeded)")]
    except Exception as e:
        return [TextContent(text=f"Error: {str(e)}")]


async def handle_coderef_validate(args: dict) -> list[TextContent]:
    """Handle /validate tool - Validate CodeRef references."""
    project_path = args.get("project_path", ".")
    pattern = args.get("pattern", "**/*.ts")

    # Build CLI command: coderef validate <sourceDir> --pattern <pattern> --format json
    cmd = [
        "node", CLI_BIN, "validate",
        project_path,
        "--pattern", pattern,
        "--format", "json"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, cwd=project_path)

        if result.returncode != 0:
            return [TextContent(text=f"Error: {result.stderr}")]

        try:
            data = json.loads(result.stdout)
            return [TextContent(text=json.dumps({
                "success": True,
                "pattern": pattern,
                "validation": data
            }, indent=2))]
        except json.JSONDecodeError as e:
            return [TextContent(text=f"JSON parse error: {str(e)}")]

    except subprocess.TimeoutExpired:
        return [TextContent(text="Error: Validation timeout (30s exceeded)")]
    except Exception as e:
        return [TextContent(text=f"Error: {str(e)}")]


async def handle_coderef_drift(args: dict) -> list[TextContent]:
    """Handle /drift tool - Detect reference drift."""
    project_path = args.get("project_path", ".")
    index_path = args.get("index_path", ".coderef-index.json")

    # Build CLI command: coderef drift <sourceDir> --index <indexPath> --format json
    cmd = [
        "node", CLI_BIN, "drift",
        project_path,
        "--index", index_path,
        "--format", "json"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, cwd=project_path)

        if result.returncode != 0:
            return [TextContent(text=f"Error: {result.stderr}")]

        try:
            data = json.loads(result.stdout)
            return [TextContent(text=json.dumps({
                "success": True,
                "drift_report": data
            }, indent=2))]
        except json.JSONDecodeError as e:
            return [TextContent(text=f"JSON parse error: {str(e)}")]

    except subprocess.TimeoutExpired:
        return [TextContent(text="Error: Drift detection timeout (30s exceeded)")]
    except Exception as e:
        return [TextContent(text=f"Error: {str(e)}")]


async def handle_coderef_diagram(args: dict) -> list[TextContent]:
    """Handle /diagram tool - Generate dependency diagrams."""
    project_path = args.get("project_path", ".")
    diagram_type = args.get("diagram_type", "dependencies")
    format_type = args.get("format", "mermaid")
    depth = args.get("depth", 2)

    # Build CLI command: coderef diagram --format <format> --depth <depth> --output stdout
    cmd = [
        "node", CLI_BIN, "diagram",
        "--format", format_type,
        "--depth", str(depth)
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, cwd=project_path)

        if result.returncode != 0:
            return [TextContent(text=f"Error: {result.stderr}")]

        # For non-JSON formats (mermaid, dot), return text directly
        if format_type in ["mermaid", "dot"]:
            return [TextContent(text=result.stdout)]

        # For JSON format, parse and wrap
        try:
            data = json.loads(result.stdout)
            return [TextContent(text=json.dumps({
                "success": True,
                "diagram": data
            }, indent=2))]
        except json.JSONDecodeError:
            # If not JSON, return as-is
            return [TextContent(text=result.stdout)]

    except subprocess.TimeoutExpired:
        return [TextContent(text="Error: Diagram generation timeout (30s exceeded)")]
    except Exception as e:
        return [TextContent(text=f"Error: {str(e)}")]


# ============================================================================
# Server Entry Point
# ============================================================================

if __name__ == "__main__":
    print("[coderef-context] Starting MCP server...")
    import asyncio
    from mcp.server.stdio import stdio_server

    asyncio.run(stdio_server(app))
