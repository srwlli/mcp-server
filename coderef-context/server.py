#!/usr/bin/env python3
"""
CodeRef Context MCP Server

Reads pre-scanned code intelligence from .coderef/ directory.
Provides fast, read-only access to code analysis for workflow and docs agents.

Tools exposed:
- /scan - Get scanned code elements
- /query - Query relationships (what-calls, what-imports, shortest-path)
- /impact - Analyze change impact
- /complexity - Function/class complexity metrics
- /patterns - Discover patterns and test gaps
- /coverage - Test coverage analysis
- /context - Get comprehensive codebase context
- /validate - Validate CodeRef2 references
- /drift - Detect drift between index and code
- /diagram - Get dependency diagrams
- /tag - Add CodeRef2 tags (requires CLI)
- /export - Get exported data (JSON, JSON-LD, Mermaid, DOT)

Architecture:
- Reads from .coderef/ directory (pre-scanned by dashboard or scripts)
- No subprocess overhead (100x faster than CLI)
- Direct file access for instant results
- Read-only operations (safe)
"""

__version__ = "2.0.0"
__mcp_version__ = "1.0"

import asyncio
import os
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

# Import refactored handlers (read from .coderef/ files)
from src.handlers_refactored import (
    handle_coderef_scan,
    handle_coderef_query,
    handle_coderef_impact,
    handle_coderef_complexity,
    handle_coderef_patterns,
    handle_coderef_coverage,
    handle_coderef_context,
    handle_coderef_validate,
    handle_coderef_drift,
    handle_coderef_incremental_scan,
    handle_coderef_diagram,
    handle_coderef_tag,
    handle_coderef_export,
    handle_generate_foundation_docs,
    handle_validate_coderef_outputs,
)

# Initialize MCP server
app = Server("coderef-context")

print(f"[coderef-context] Initializing MCP server v{__version__}")
print(f"[coderef-context] Mode: File Reader (reads from .coderef/ directory)")


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
            name="coderef_incremental_scan",
            description="Perform incremental scan (only re-scan files with detected drift, merge with existing index)",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Project root"
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
        Tool(
            name="coderef_tag",
            description="Add CodeRef2 tags to source files for better tracking and validation",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File or directory path to tag"
                    },
                    "dry_run": {
                        "type": "boolean",
                        "description": "Preview changes without writing to files",
                        "default": False
                    },
                    "force": {
                        "type": "boolean",
                        "description": "Force update existing tags",
                        "default": False
                    },
                    "verbose": {
                        "type": "boolean",
                        "description": "Show detailed output",
                        "default": False
                    },
                    "update_lineno": {
                        "type": "boolean",
                        "description": "Update line numbers in existing tags",
                        "default": False
                    },
                    "include_private": {
                        "type": "boolean",
                        "description": "Include private elements (starting with _)",
                        "default": False
                    },
                    "lang": {
                        "type": "string",
                        "description": "File extensions to process (comma-separated)",
                        "default": "ts,tsx,js,jsx"
                    },
                    "exclude": {
                        "type": "string",
                        "description": "Exclusion patterns (comma-separated)"
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="coderef_export",
            description="Export coderef data in various formats (JSON, JSON-LD, Mermaid, DOT)",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Absolute path to project root"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["json", "jsonld", "mermaid", "dot"],
                        "description": "Export format"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Optional output file path (defaults to .coderef/exports/{format})"
                    },
                    "max_nodes": {
                        "type": "integer",
                        "description": "Optional limit on graph nodes (for large codebases)"
                    }
                },
                "required": ["project_path", "format"]
            }
        ),
        Tool(
            name="generate_foundation_docs",
            description="Auto-generate foundation documentation (API.md, SCHEMA.md, COMPONENTS.md) from .coderef/index.json",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Absolute path to project root"
                    },
                    "docs": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Doc types to generate: api, schema, components, readme",
                        "default": ["api", "schema", "components"]
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "Output directory for generated docs",
                        "default": "coderef/foundation-docs"
                    }
                },
                "required": ["project_path"]
            }
        ),
        Tool(
            name="validate_coderef_outputs",
            description="Validate .coderef/ files against schemas using Papertrail MCP validation",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Absolute path to project root"
                    }
                },
                "required": ["project_path"]
            }
        ),
    ]




# ============================================================================
# Tool Handlers - Imported from handlers_refactored.py
# ============================================================================

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls by reading from .coderef/ directory."""

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
        elif name == "coderef_incremental_scan":
            return await handle_coderef_incremental_scan(arguments)
        elif name == "coderef_diagram":
            return await handle_coderef_diagram(arguments)
        elif name == "coderef_tag":
            return await handle_coderef_tag(arguments)
        elif name == "coderef_export":
            return await handle_coderef_export(arguments)
        elif name == "generate_foundation_docs":
            return await handle_generate_foundation_docs(arguments)
        elif name == "validate_coderef_outputs":
            return await handle_validate_coderef_outputs(arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        return [TextContent(type="text", text=f"Error calling tool {name}: {str(e)}")]


# ============================================================================
# Server Entry Point
# ============================================================================

async def main():
    """Main entry point for MCP server."""
    print("[coderef-context] Starting MCP server...")
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
