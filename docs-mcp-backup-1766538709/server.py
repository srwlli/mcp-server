#!/usr/bin/env python3
"""
Documentation Generation MCP Server (Minimal Implementation)

Provides tools for generating project documentation using POWER framework templates.
This minimal version contains 11 documentation-focused tools.

Recent changes:
- Deprecated: update_changelog (purely instructional tool - replaced by record_changes agentic tool)
- Added: record_changes (smart agentic tool with git auto-detection, change_type suggestion, severity calculation, and agent confirmation)

Removed tools (now in coderef-workflow MCP):
- Planning tools: get_planning_template, analyze_project_for_planning, gather_context, create_plan, validate_implementation_plan, generate_plan_review_report, generate_deliverables_template, generate_handoff_context
- Execution tools: execute_plan, update_task_status
- Agent coordination tools: generate_agent_communication, assign_agent_task, verify_agent_completion, aggregate_agent_deliverables, track_agent_status
- Archive tools: archive_feature
- Admin tools: log_workorder, get_workorder_log, update_all_documentation, audit_plans, coderef_foundation_docs, generate_features_inventory
"""

__version__ = "2.0.0"
__schema_version__ = "1.0.0"
__mcp_version__ = "1.0"

import asyncio
from pathlib import Path
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

# Import generators
from generators import FoundationGenerator, BaseGenerator
import json
import jsonschema

# Import constants (REF-002)
from constants import Paths, Files

# Import validation functions (REF-003)
from validation import (
    validate_project_path_input,
    validate_version_format,
    validate_template_name_input,
    validate_changelog_inputs,
    VALID_TEMPLATE_SECTIONS
)

# Import error response factory (ARCH-001)
from error_responses import ErrorResponse

# Import tool handlers (QUA-002)
import tool_handlers

# Import logging (ARCH-003)
from logger_config import logger, log_tool_call

# Get server directory
SERVER_DIR = Path(__file__).parent
TEMPLATES_DIR = SERVER_DIR / Paths.TEMPLATES_DIR
TOOL_TEMPLATES_DIR = SERVER_DIR / Paths.TOOL_TEMPLATES_DIR

# Initialize tool handlers with TEMPLATES_DIR
tool_handlers.set_templates_dir(TEMPLATES_DIR)
tool_handlers.set_tool_templates_dir(TOOL_TEMPLATES_DIR)

# Create MCP server
app = Server("docs-mcp")

# Log server initialization
logger.info(f"MCP server starting", extra={'version': __version__, 'mcp_version': __mcp_version__})


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available documentation tools (12 tools - minimal implementation)."""
    return [
        Tool(
            name="list_templates",
            description="Lists all available documentation templates (README, ARCHITECTURE, API, COMPONENTS, SCHEMA)",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_template",
            description="Retrieves the content of a specific documentation template",
            inputSchema={
                "type": "object",
                "properties": {
                    "template_name": {
                        "type": "string",
                        "description": "Name of template: readme, architecture, api, components, my-guide, schema, or user-guide",
                        "enum": ["readme", "architecture", "api", "components", "my-guide", "schema", "user-guide"]
                    }
                },
                "required": ["template_name"]
            }
        ),
        Tool(
            name="generate_foundation_docs",
            description="Generate foundation documentation (README, ARCHITECTURE, API, COMPONENTS, SCHEMA) for a project. Returns templates and generation plan - Claude will generate and save the actual documents.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Absolute path to the project directory"
                    }
                },
                "required": ["project_path"]
            }
        ),
        Tool(
            name="generate_individual_doc",
            description="Generate a single individual documentation file for a project. Returns the template - Claude will generate and save the document.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Absolute path to the project directory"
                    },
                    "template_name": {
                        "type": "string",
                        "description": "Name of template to generate",
                        "enum": ["readme", "architecture", "api", "components", "my-guide", "schema", "user-guide"]
                    }
                },
                "required": ["project_path", "template_name"]
            }
        ),
        Tool(
            name="get_changelog",
            description="Get project changelog with structured change history for agent context. Returns all changes or filtered by version/type.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Absolute path to project directory"
                    },
                    "version": {
                        "type": "string",
                        "description": "Optional: Get specific version (e.g., '1.0.1'). Omit for all versions."
                    },
                    "change_type": {
                        "type": "string",
                        "enum": ["bugfix", "enhancement", "feature", "breaking_change", "deprecation", "security"],
                        "description": "Optional: Filter by change type"
                    },
                    "breaking_only": {
                        "type": "boolean",
                        "description": "Optional: Show only breaking changes"
                    }
                },
                "required": ["project_path"]
            }
        ),
        Tool(
            name="add_changelog_entry",
            description="Add a new entry to the project changelog. Requires all change details including version, type, title, description, files, reason, and impact.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Absolute path to project directory"
                    },
                    "version": {
                        "type": "string",
                        "description": "Version number (e.g., '1.0.2')",
                        "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"
                    },
                    "change_type": {
                        "type": "string",
                        "enum": ["bugfix", "enhancement", "feature", "breaking_change", "deprecation", "security"],
                        "description": "Type of change"
                    },
                    "severity": {
                        "type": "string",
                        "enum": ["critical", "major", "minor", "patch"],
                        "description": "Severity level"
                    },
                    "title": {
                        "type": "string",
                        "description": "Short title of the change"
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed description of what changed"
                    },
                    "files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of files affected"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Why this change was made"
                    },
                    "impact": {
                        "type": "string",
                        "description": "Impact on users/system"
                    },
                    "breaking": {
                        "type": "boolean",
                        "description": "Whether this is a breaking change",
                        "default": False
                    },
                    "migration": {
                        "type": "string",
                        "description": "Migration guide (if breaking)"
                    },
                    "summary": {
                        "type": "string",
                        "description": "Version summary (for new versions)"
                    },
                    "contributors": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of contributors"
                    }
                },
                "required": ["project_path", "version", "change_type", "severity", "title", "description", "files", "reason", "impact"]
            }
        ),
        Tool(
            name="record_changes",
            description="Smart agentic changelog recording with git auto-detection. Auto-detects changed files (git diff --staged), suggests change_type from commit messages, calculates severity from scope, and shows preview for agent confirmation before creating entry.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Absolute path to project directory"
                    },
                    "version": {
                        "type": "string",
                        "description": "Version number for this change (e.g., '1.0.3')",
                        "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"
                    },
                    "context": {
                        "type": "object",
                        "description": "Optional context for git-less environments. Can include files_changed, commit_messages, feature_name, description",
                        "default": {}
                    }
                },
                "required": ["project_path", "version"]
            }
        ),
        Tool(
            name="generate_quickref_interactive",
            description="Interactive workflow to generate a universal quickref guide for ANY application (CLI, Web, API, Desktop, Library). Returns interview questions for AI to ask user. AI guides conversation, user answers in plain English, then AI generates scannable quickref.md (150-250 lines) following proven pattern.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Absolute path to project directory where quickref.md will be saved"
                    },
                    "app_type": {
                        "type": "string",
                        "enum": ["cli", "web", "api", "desktop", "library"],
                        "description": "Optional: Type of application (can be inferred from user responses)"
                    }
                },
                "required": ["project_path"]
            }
        ),
        Tool(
            name="establish_standards",
            description="Scan codebase to discover UI/UX/behavior patterns and generate standards documentation. Creates 4 markdown files in coderef/standards/. Run ONCE per project to establish baseline standards for consistency validation (Tools #9 and #10).",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Absolute path to project directory"
                    },
                    "scan_depth": {
                        "type": "string",
                        "enum": ["quick", "standard", "deep"],
                        "description": "Analysis depth: quick (common patterns, ~1-2 min), standard (comprehensive, ~3-5 min), deep (exhaustive, ~10-15 min)",
                        "default": "standard"
                    },
                    "focus_areas": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["ui_components", "behavior_patterns", "ux_flows", "all"]
                        },
                        "description": "Areas to analyze: ui_components (buttons, modals, forms), behavior_patterns (errors, loading), ux_flows (navigation, permissions), or all",
                        "default": ["all"]
                    }
                },
                "required": ["project_path"]
            }
        ),
        Tool(
            name="audit_codebase",
            description="Audit codebase for standards violations using established standards documents. Scans all source files, compares against standards, and generates comprehensive compliance report with violations, severity levels, and fix suggestions.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Absolute path to project directory"
                    },
                    "standards_dir": {
                        "type": "string",
                        "description": "Path to standards directory (relative to project root)",
                        "default": "coderef/standards"
                    },
                    "severity_filter": {
                        "type": "string",
                        "enum": ["critical", "major", "minor", "all"],
                        "description": "Filter violations by severity level",
                        "default": "all"
                    },
                    "scope": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["ui_patterns", "behavior_patterns", "ux_patterns", "all"]
                        },
                        "description": "Which areas to audit: ui_patterns, behavior_patterns, ux_patterns, or all",
                        "default": ["all"]
                    },
                    "generate_fixes": {
                        "type": "boolean",
                        "description": "Include automated fix suggestions in report",
                        "default": True
                    }
                },
                "required": ["project_path"]
            }
        ),
        Tool(
            name="check_consistency",
            description="Check code changes against established standards for consistency violations. Lightweight quality gate for pre-commit checks and CI/CD pipelines. Only scans modified files. Auto-detects changes via git or accepts explicit file list.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Absolute path to project directory"
                    },
                    "files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of files to check (relative to project_path). If not provided, auto-detects git changes (staged files by default)."
                    },
                    "standards_dir": {
                        "type": "string",
                        "description": "Path to standards directory (relative to project root)",
                        "default": "coderef/standards"
                    },
                    "severity_threshold": {
                        "type": "string",
                        "enum": ["critical", "major", "minor"],
                        "description": "Fail if violations at or above this severity are found. 'critical'=only critical, 'major'=critical+major, 'minor'=all violations",
                        "default": "major"
                    },
                    "scope": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["ui_patterns", "behavior_patterns", "ux_patterns", "all"]
                        },
                        "description": "Which standards to check against. 'all' checks UI, behavior, and UX patterns.",
                        "default": ["all"]
                    },
                    "fail_on_violations": {
                        "type": "boolean",
                        "description": "Return error status (exit code 1) if violations found. Set false for reporting only.",
                        "default": True
                    }
                },
                "required": ["project_path"]
            }
        ),
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """
    Handle tool calls by dispatching to registered handlers (QUA-002).

    This function now uses a registry pattern for clean separation of concerns.
    Each tool has its own handler function in tool_handlers.py for better
    testability and maintainability.
    """
    # Log tool invocation (ARCH-003)
    log_tool_call(name, args_keys=list(arguments.keys()))

    handler = tool_handlers.TOOL_HANDLERS.get(name)
    if not handler:
        logger.error(f"Unknown tool requested: {name}")
        raise ValueError(f"Unknown tool: {name}")

    return await handler(arguments)


async def main() -> None:
    """Run the server using stdio transport."""
    logger.info("Starting MCP server main loop")
    try:
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
    except Exception as e:
        logger.error(f"Server error: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
