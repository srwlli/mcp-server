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


# Placeholder handlers - will be fully implemented after CLI_SPEC.md
async def handle_coderef_scan(args: dict) -> list[TextContent]:
    """Handle /scan tool."""
    return [TextContent(text="TODO: Implement after CLI_SPEC.md")]


async def handle_coderef_query(args: dict) -> list[TextContent]:
    """Handle /query tool."""
    return [TextContent(text="TODO: Implement after CLI_SPEC.md")]


async def handle_coderef_impact(args: dict) -> list[TextContent]:
    """Handle /impact tool."""
    return [TextContent(text="TODO: Implement after CLI_SPEC.md")]


async def handle_coderef_complexity(args: dict) -> list[TextContent]:
    """Handle /complexity tool."""
    return [TextContent(text="TODO: Implement after CLI_SPEC.md")]


async def handle_coderef_patterns(args: dict) -> list[TextContent]:
    """Handle /patterns tool."""
    return [TextContent(text="TODO: Implement after CLI_SPEC.md")]


async def handle_coderef_coverage(args: dict) -> list[TextContent]:
    """Handle /coverage tool."""
    return [TextContent(text="TODO: Implement after CLI_SPEC.md")]


async def handle_coderef_context(args: dict) -> list[TextContent]:
    """Handle /context tool."""
    return [TextContent(text="TODO: Implement after CLI_SPEC.md")]


async def handle_coderef_validate(args: dict) -> list[TextContent]:
    """Handle /validate tool."""
    return [TextContent(text="TODO: Implement after CLI_SPEC.md")]


async def handle_coderef_drift(args: dict) -> list[TextContent]:
    """Handle /drift tool."""
    return [TextContent(text="TODO: Implement after CLI_SPEC.md")]


async def handle_coderef_diagram(args: dict) -> list[TextContent]:
    """Handle /diagram tool."""
    return [TextContent(text="TODO: Implement after CLI_SPEC.md")]


# ============================================================================
# Server Entry Point
# ============================================================================

if __name__ == "__main__":
    print("[coderef-context] Starting MCP server...")
    stdio_server(app).run()
