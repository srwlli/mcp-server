#!/usr/bin/env python3
"""
Documentation Generation MCP Server

Provides tools for generating project documentation using POWER framework templates.
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
app = Server("coderef-workflow")

# Log server initialization
logger.info(f"MCP server starting", extra={'version': __version__, 'mcp_version': __mcp_version__})


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available documentation tools."""
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
            name="update_changelog",
            description="Agentic workflow tool that instructs the agent to analyze their recent changes and update the changelog using context. Agent reviews modified files, determines change details, and calls add_changelog_entry.",
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
        Tool(
            name='get_planning_template',
            description='Returns feature-implementation-planning-standard.json template content or specific sections for AI reference during implementation planning',
            inputSchema={
                'type': 'object',
                'properties': {
                    'section': {
                        'type': 'string',
                        'enum': VALID_TEMPLATE_SECTIONS,
                        'description': 'Which section of the template to return (default: all)',
                        'default': 'all'
                    }
                },
                'required': []
            }
        ),
        Tool(
            name='analyze_project_for_planning',
            description='Analyzes project to discover foundation docs, coding standards, reference components, and patterns - automates section 0 (Preparation) of implementation plans. Optionally saves analysis to feature folder. Reduces prep time from 30-60 minutes to 30-60 seconds.',
            inputSchema={
                'type': 'object',
                'properties': {
                    'project_path': {
                        'type': 'string',
                        'description': 'Absolute path to project directory to analyze'
                    },
                    'feature_name': {
                        'type': 'string',
                        'description': 'Optional: Feature name for saving analysis to coderef/workorder/{feature_name}/analysis.json. If omitted, analysis is returned without saving.',
                        'pattern': '^[a-zA-Z0-9_-]+$'
                    }
                },
                'required': ['project_path']
            }
        ),
        Tool(
            name='gather_context',
            description='Gather feature requirements and save to context.json. Accepts structured feature data (name, description, goal, requirements, constraints) and creates a properly formatted context file in coderef/workorder/{feature_name}/ for use with planning workflows.',
            inputSchema={
                'type': 'object',
                'properties': {
                    'project_path': {
                        'type': 'string',
                        'description': 'Absolute path to project directory'
                    },
                    'feature_name': {
                        'type': 'string',
                        'description': 'Feature name (alphanumeric, hyphens, underscores only). Max 100 characters.',
                        'pattern': '^[a-zA-Z0-9_-]+$'
                    },
                    'description': {
                        'type': 'string',
                        'description': 'What the user wants to build (plain language description)'
                    },
                    'goal': {
                        'type': 'string',
                        'description': 'Why they want this feature (primary objective)'
                    },
                    'requirements': {
                        'type': 'array',
                        'items': {'type': 'string'},
                        'description': 'Must-have requirements (array of strings)'
                    },
                    'out_of_scope': {
                        'type': 'array',
                        'items': {'type': 'string'},
                        'description': 'Optional: Features explicitly excluded from this phase'
                    },
                    'constraints': {
                        'type': 'array',
                        'items': {'type': 'string'},
                        'description': 'Optional: Technical or business constraints'
                    },
                    'decisions': {
                        'type': 'object',
                        'description': 'Optional: Key decisions made during gathering (key-value pairs)'
                    },
                    'success_criteria': {
                        'type': 'object',
                        'description': 'Optional: How to measure success (nested structure)'
                    }
                },
                'required': ['project_path', 'feature_name', 'description', 'goal', 'requirements']
            }
        ),
        Tool(
            name='validate_implementation_plan',
            description='Validates implementation plan JSON against feature-implementation-planning-standard.json quality checklist. Scores plan 0-100 based on completeness, quality, and autonomy. Identifies issues by severity (critical/major/minor) with specific fix suggestions. Enables iterative review loop - AI validates plan, refines based on feedback, re-validates until score >= 85 before presenting to user.',
            inputSchema={
                'type': 'object',
                'properties': {
                    'project_path': {
                        'type': 'string',
                        'description': 'Absolute path to project directory containing the plan file'
                    },
                    'plan_file_path': {
                        'type': 'string',
                        'description': 'Relative path to plan JSON file within project (e.g., feature-auth-plan.json)'
                    }
                },
                'required': ['project_path', 'plan_file_path']
            }
        ),
        Tool(
            name='generate_plan_review_report',
            description='Transforms validation results from validate_implementation_plan into human-readable markdown review reports. Creates comprehensive report with score, grade, issue breakdown by severity, recommendations, and approval status. Saves to coderef/reviews/ directory.',
            inputSchema={
                'type': 'object',
                'properties': {
                    'project_path': {
                        'type': 'string',
                        'description': 'Absolute path to project directory'
                    },
                    'plan_file_path': {
                        'type': 'string',
                        'description': 'Relative path to plan JSON file within project (e.g., feature-auth-plan.json)'
                    },
                    'output_path': {
                        'type': 'string',
                        'description': 'Optional: Custom output path for review report (relative to project root). Default: coderef/reviews/review-{planname}-{timestamp}.md'
                    }
                },
                'required': ['project_path', 'plan_file_path']
            }
        ),
        Tool(
            name='create_plan',
            description='Create implementation plan by synthesizing context, analysis, and template. Generates complete 10-section plan.json file in batch mode. Saves partial plan with TODOs if generation fails. NEW in v1.7.0: Supports multi_agent mode for automatic agent coordination setup.',
            inputSchema={
                'type': 'object',
                'properties': {
                    'project_path': {
                        'type': 'string',
                        'description': 'Absolute path to project directory'
                    },
                    'feature_name': {
                        'type': 'string',
                        'description': 'Feature name (alphanumeric, hyphens, underscores only). Max 100 characters.',
                        'pattern': '^[a-zA-Z0-9_-]+$'
                    },
                    'workorder_id': {
                        'type': 'string',
                        'description': 'Optional workorder ID for tracking (e.g., WO-AUTH-SYSTEM-001). If omitted, auto-generated.',
                        'pattern': '^WO-[A-Z0-9-]+-\\d{3}$'
                    },
                    'multi_agent': {
                        'type': 'boolean',
                        'description': 'Enable multi-agent coordination mode. When true, automatically generates communication.json after plan creation for parallel agent execution.',
                        'default': False
                    }
                },
                'required': ['project_path', 'feature_name']
            }
        ),
        Tool(
            name='finalize_plan_from_agent',
            description='Finalize plan generation by parsing Task agent response, saving to plan.json, and auto-validating. Called automatically by Claude Code after Task agent completes in /create-workorder workflow.',
            inputSchema={
                'type': 'object',
                'properties': {
                    'project_path': {
                        'type': 'string',
                        'description': 'Absolute path to project directory'
                    },
                    'feature_name': {
                        'type': 'string',
                        'description': 'Feature name (alphanumeric, hyphens, underscores only)',
                        'pattern': '^[a-zA-Z0-9_-]+$'
                    },
                    'agent_response': {
                        'type': 'string',
                        'description': 'Raw text response from Task agent containing plan JSON'
                    }
                },
                'required': ['project_path', 'feature_name', 'agent_response']
            }
        ),
        Tool(
            name='generate_deliverables_template',
            description='Generate DELIVERABLES.md template from plan.json structure with phase/task checklists and metric placeholders. Automatically called by /create-plan workflow. Saves to coderef/workorder/{feature-name}/DELIVERABLES.md.',
            inputSchema={
                'type': 'object',
                'properties': {
                    'project_path': {
                        'type': 'string',
                        'description': 'Absolute path to project directory'
                    },
                    'feature_name': {
                        'type': 'string',
                        'description': 'Feature name (alphanumeric, hyphens, underscores only)'
                    }
                },
                'required': ['project_path', 'feature_name']
            }
        ),
        Tool(
            name='update_deliverables',
            description='Update DELIVERABLES.md with actual metrics from git history (LOC, commits, time spent). Parses git log to find feature-related commits and calculates implementation metrics. Run after feature implementation completes.',
            inputSchema={
                'type': 'object',
                'properties': {
                    'project_path': {
                        'type': 'string',
                        'description': 'Absolute path to project directory (must be git repository)'
                    },
                    'feature_name': {
                        'type': 'string',
                        'description': 'Feature name to search for in git commit messages'
                    }
                },
                'required': ['project_path', 'feature_name']
            }
        ),
        Tool(
            name='generate_agent_communication',
            description='Generate communication.json from plan.json for multi-agent coordination. Auto-generates precise steps, forbidden files, success criteria, and agent status fields from implementation plan.',
            inputSchema={
                'type': 'object',
                'properties': {
                    'project_path': {
                        'type': 'string',
                        'description': 'Absolute path to project directory'
                    },
                    'feature_name': {
                        'type': 'string',
                        'description': 'Feature name (alphanumeric, hyphens, underscores only)',
                        'pattern': '^[a-zA-Z0-9_-]+$'
                    }
                },
                'required': ['project_path', 'feature_name']
            }
        ),
        Tool(
            name='assign_agent_task',
            description='Assign specific task to agent with workorder scoping and conflict detection. Updates communication.json with agent assignment and generates agent-scoped workorder ID.',
            inputSchema={
                'type': 'object',
                'properties': {
                    'project_path': {
                        'type': 'string',
                        'description': 'Absolute path to project directory'
                    },
                    'feature_name': {
                        'type': 'string',
                        'description': 'Feature name (alphanumeric, hyphens, underscores only)',
                        'pattern': '^[a-zA-Z0-9_-]+$'
                    },
                    'agent_number': {
                        'type': 'integer',
                        'description': 'Agent number (1-10)',
                        'minimum': 1,
                        'maximum': 10
                    },
                    'phase_id': {
                        'type': 'string',
                        'description': 'Optional phase ID to assign (e.g., "phase_1")'
                    }
                },
                'required': ['project_path', 'feature_name', 'agent_number']
            }
        ),
        Tool(
            name='verify_agent_completion',
            description='Verify agent completion with automated git diff checks and success criteria validation. Validates forbidden files unchanged and updates agent status to VERIFIED.',
            inputSchema={
                'type': 'object',
                'properties': {
                    'project_path': {
                        'type': 'string',
                        'description': 'Absolute path to project directory'
                    },
                    'feature_name': {
                        'type': 'string',
                        'description': 'Feature name (alphanumeric, hyphens, underscores only)',
                        'pattern': '^[a-zA-Z0-9_-]+$'
                    },
                    'agent_number': {
                        'type': 'integer',
                        'description': 'Agent number to verify (1-10)',
                        'minimum': 1,
                        'maximum': 10
                    }
                },
                'required': ['project_path', 'feature_name', 'agent_number']
            }
        ),
        Tool(
            name='aggregate_agent_deliverables',
            description='Aggregate metrics from multiple agent DELIVERABLES.md files into combined report. Sums LOC, counts commits, merges contributors, and calculates total time elapsed.',
            inputSchema={
                'type': 'object',
                'properties': {
                    'project_path': {
                        'type': 'string',
                        'description': 'Absolute path to project directory'
                    },
                    'feature_name': {
                        'type': 'string',
                        'description': 'Feature name (alphanumeric, hyphens, underscores only)',
                        'pattern': '^[a-zA-Z0-9_-]+$'
                    }
                },
                'required': ['project_path', 'feature_name']
            }
        ),
        Tool(
            name='track_agent_status',
            description='Track agent status across all features with real-time coordination dashboard. Provides feature-level and project-wide agent status tracking using parse_agent_status helper.',
            inputSchema={
                'type': 'object',
                'properties': {
                    'project_path': {
                        'type': 'string',
                        'description': 'Absolute path to project directory'
                    },
                    'feature_name': {
                        'type': 'string',
                        'description': 'Optional - specific feature to track. If omitted, tracks all features.',
                        'pattern': '^[a-zA-Z0-9_-]+$'
                    }
                },
                'required': ['project_path']
            }
        ),
        Tool(
            name='archive_feature',
            description='Archive completed features from coderef/workorder/ to coderef/archived/. Checks DELIVERABLES.md status and prompts user for confirmation if status != Complete. Moves entire feature folder and updates archive index.json with metadata.',
            inputSchema={
                'type': 'object',
                'properties': {
                    'project_path': {
                        'type': 'string',
                        'description': 'Absolute path to project directory'
                    },
                    'feature_name': {
                        'type': 'string',
                        'description': 'Feature name (folder name in coderef/workorder/). Alphanumeric, hyphens, underscores only.',
                        'pattern': '^[a-zA-Z0-9_-]+$'
                    },
                    'force': {
                        'type': 'boolean',
                        'description': 'Optional: Skip user confirmation even if status != Complete. Default: false',
                        'default': False
                    }
                },
                'required': ['project_path', 'feature_name']
            }
        ),
        Tool(
            name='update_all_documentation',
            description='''AGENTIC WORKFLOW: Update all documentation files after completing a feature. Designed for AI agents to leverage their own context instead of parsing files.

WHAT IS AGENTIC?
Agentic = Designed for AI-to-AI communication. The agent who completed work has full context and provides it directly to the tool. No file parsing, git analysis, or manual version decisions needed.

HOW IT WORKS:
1. Agent completes feature (already knows: what changed, why, which files, workorder)
2. Agent calls this tool with context from conversation history
3. Tool auto-increments version based on change_type:
   - breaking_change → Major bump (1.x.x → 2.0.0)
   - feature → Minor bump (1.0.x → 1.1.0)
   - bugfix/enhancement → Patch bump (1.0.0 → 1.0.1)
4. Tool updates 3 files automatically:
   - README.md: Version number + What's New section
   - CLAUDE.md: Version history + workorder tracking
   - CHANGELOG.json: Structured entry with metadata

WHY AGENTIC DESIGN MATTERS:
- Agent has conversation context (no need to parse files)
- Agent knows exact change details (no guessing)
- Agent tracked workorder during implementation
- Structured data prevents errors
- Fast: 30 seconds vs 10-15 minutes manual updates

WORKFLOW INTEGRATION:
Run AFTER /update-deliverables and BEFORE /archive-feature:
  Feature Implementation → /update-deliverables → /update-docs → /archive-feature

MANUAL UPDATES STILL NEEDED:
- user-guide.md: Add feature documentation manually
- my-guide.md: Add tool to tool list manually

EXAMPLE (Multi-agent scenario):
  Agent 2: "I finished auth system"
  Agent 2: *calls update_all_documentation({
    change_type: 'feature',
    feature_description: 'Added JWT authentication with refresh tokens',
    workorder_id: 'WO-AUTH-SYSTEM-002',
    files_changed: ['src/auth.py', 'tests/test_auth.py']
  })*
  Tool: *auto-updates README, CLAUDE, CHANGELOG with correct version*
  Agent 2: *updates my-guide.md manually*
  Done!

Run after /update-deliverables and before /archive-feature.''',
            inputSchema={
                'type': 'object',
                'properties': {
                    'project_path': {
                        'type': 'string',
                        'description': 'Absolute path to project directory'
                    },
                    'change_type': {
                        'type': 'string',
                        'enum': ['breaking_change', 'feature', 'enhancement', 'bugfix', 'security', 'deprecation'],
                        'description': 'REQUIRED: Type of change made (agent knows this from their work)'
                    },
                    'feature_description': {
                        'type': 'string',
                        'description': 'REQUIRED: Description of what was changed (agent provides from context)'
                    },
                    'workorder_id': {
                        'type': 'string',
                        'description': 'REQUIRED: Workorder ID from agent task (e.g., WO-UPDATE-DOCS-001) for tracking',
                        'pattern': '^WO-[A-Z0-9-]+-\\d{3}$'
                    },
                    'files_changed': {
                        'type': 'array',
                        'items': {'type': 'string'},
                        'description': 'Optional: List of files modified (agent knows this from their work)'
                    },
                    'feature_name': {
                        'type': 'string',
                        'description': 'Optional: Feature name for reference'
                    },
                    'version': {
                        'type': 'string',
                        'description': 'Optional: Manual version override (rarely needed - auto-increments by default)',
                        'pattern': '^\\d+\\.\\d+\\.\\d+$'
                    }
                },
                'required': ['project_path', 'change_type', 'feature_description', 'workorder_id']
            }
        ),
        Tool(
            name='execute_plan',
            description='Generate TodoWrite task list from plan.json with WO-ID | TASK-ID: Description format for Lloyd\'s CLI checklist display. Reads plan from coderef/workorder/{feature}/, extracts workorder ID and tasks, generates properly formatted todos with activeForm for progress tracking.',
            inputSchema={
                'type': 'object',
                'properties': {
                    'project_path': {
                        'type': 'string',
                        'description': 'Absolute path to project directory'
                    },
                    'feature_name': {
                        'type': 'string',
                        'description': 'Feature name (alphanumeric, hyphens, underscores only)',
                        'pattern': '^[a-zA-Z0-9_-]+$'
                    }
                },
                'required': ['project_path', 'feature_name']
            }
        ),
        Tool(
            name='update_task_status',
            description='Update task status in plan.json as agents complete work (STUB-009). Enables progress tracking during execution. Updates task status and calculates progress summary.',
            inputSchema={
                'type': 'object',
                'properties': {
                    'project_path': {
                        'type': 'string',
                        'description': 'Absolute path to project directory'
                    },
                    'feature_name': {
                        'type': 'string',
                        'description': 'Feature name (folder in coderef/workorder/)',
                        'pattern': '^[a-zA-Z0-9_-]+$'
                    },
                    'task_id': {
                        'type': 'string',
                        'description': 'Task ID to update (e.g., "SETUP-001", "IMPL-002")'
                    },
                    'status': {
                        'type': 'string',
                        'description': 'New status',
                        'enum': ['pending', 'in_progress', 'completed', 'blocked']
                    },
                    'notes': {
                        'type': 'string',
                        'description': 'Optional notes about the status change'
                    }
                },
                'required': ['project_path', 'feature_name', 'task_id', 'status']
            }
        ),
        Tool(
            name='audit_plans',
            description='Audit all plans in coderef/workorder/ directory (STUB-011). Provides plan format validation, progress status extraction, stale plan detection, issue identification and recommendations. Returns health score (0-100).',
            inputSchema={
                'type': 'object',
                'properties': {
                    'project_path': {
                        'type': 'string',
                        'description': 'Absolute path to project directory'
                    },
                    'stale_days': {
                        'type': 'integer',
                        'description': 'Days without update to consider stale (default: 7)',
                        'default': 7,
                        'minimum': 1,
                        'maximum': 365
                    },
                    'include_archived': {
                        'type': 'boolean',
                        'description': 'Whether to also audit archived plans (default: false)',
                        'default': False
                    }
                },
                'required': ['project_path']
            }
        ),
        Tool(
            name='log_workorder',
            description='Log a new workorder entry to the global workorder log file. Creates simple one-line entry with format: WO-ID | Project | Description | Timestamp. Latest entries appear at top (prepend, reverse chronological). Thread-safe with file locking for concurrent access.',
            inputSchema={
                'type': 'object',
                'properties': {
                    'project_path': {
                        'type': 'string',
                        'description': 'Absolute path to project directory'
                    },
                    'workorder_id': {
                        'type': 'string',
                        'description': 'Workorder ID (e.g., WO-AUTH-001)',
                        'pattern': '^WO-[A-Z0-9-]+-\\d{3}$'
                    },
                    'project_name': {
                        'type': 'string',
                        'description': 'Project name (short identifier)'
                    },
                    'description': {
                        'type': 'string',
                        'description': 'Brief description of the workorder (max 50 chars recommended)'
                    },
                    'timestamp': {
                        'type': 'string',
                        'description': 'Optional: ISO 8601 timestamp. Auto-generated if not provided.'
                    }
                },
                'required': ['project_path', 'workorder_id', 'project_name', 'description']
            }
        ),
        Tool(
            name='get_workorder_log',
            description='Read and query the global workorder log file. Returns all entries or filtered by project name, workorder ID pattern, or date range. Entries displayed in reverse chronological order (latest first).',
            inputSchema={
                'type': 'object',
                'properties': {
                    'project_path': {
                        'type': 'string',
                        'description': 'Absolute path to project directory'
                    },
                    'project_name': {
                        'type': 'string',
                        'description': 'Optional: Filter by project name (partial match, case-insensitive)'
                    },
                    'workorder_pattern': {
                        'type': 'string',
                        'description': 'Optional: Filter by workorder ID pattern (e.g., "WO-AUTH" matches WO-AUTH-001, WO-AUTH-002)'
                    },
                    'limit': {
                        'type': 'integer',
                        'description': 'Optional: Maximum number of entries to return (default: all)',
                        'minimum': 1
                    }
                },
                'required': ['project_path']
            }
        ),
        Tool(
            name='generate_handoff_context',
            description='Generate automated agent handoff context files (claude.md) from plan.json, analysis.json, and git history. Reduces agent handoff time from 20-30 minutes to under 5 minutes by auto-populating 80%+ context fields. Supports full and minimal modes.',
            inputSchema={
                'type': 'object',
                'properties': {
                    'project_path': {
                        'type': 'string',
                        'description': 'Absolute path to project directory'
                    },
                    'feature_name': {
                        'type': 'string',
                        'description': 'Feature name (alphanumeric, hyphens, underscores only). Must match feature directory in coderef/workorder/',
                        'pattern': '^[a-zA-Z0-9_-]+$'
                    },
                    'mode': {
                        'type': 'string',
                        'enum': ['full', 'minimal'],
                        'description': 'Template mode - "full" for comprehensive context or "minimal" for quick summary (default: full)'
                    }
                },
                'required': ['project_path', 'feature_name']
            }
        ),
        Tool(
            name='assess_risk',
            description='AI-powered risk assessment tool that evaluates proposed code changes across 5 dimensions (breaking changes, security, performance, maintainability, reversibility) with structured scoring, multi-option comparison, and go/no-go recommendations. Completes in < 5 seconds. (WO-RISK-ASSESSMENT-001)',
            inputSchema={
                'type': 'object',
                'properties': {
                    'project_path': {
                        'type': 'string',
                        'description': 'Absolute path to project directory'
                    },
                    'proposed_change': {
                        'type': 'object',
                        'description': 'Details of the proposed code change to assess',
                        'properties': {
                            'description': {
                                'type': 'string',
                                'description': 'Human-readable description of the proposed change'
                            },
                            'change_type': {
                                'type': 'string',
                                'enum': ['create', 'modify', 'delete', 'refactor', 'migrate'],
                                'description': 'Type of change being proposed'
                            },
                            'files_affected': {
                                'type': 'array',
                                'items': {'type': 'string'},
                                'description': 'List of file paths that will be modified'
                            },
                            'context': {
                                'type': 'object',
                                'description': 'Optional additional context for the change'
                            }
                        },
                        'required': ['description', 'change_type', 'files_affected']
                    },
                    'options': {
                        'type': 'array',
                        'description': 'Optional: List of alternative options for comparison (max 5 total including primary)',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'description': {
                                    'type': 'string'
                                },
                                'change_type': {
                                    'type': 'string',
                                    'enum': ['create', 'modify', 'delete', 'refactor', 'migrate']
                                },
                                'files_affected': {
                                    'type': 'array',
                                    'items': {'type': 'string'}
                                }
                            },
                            'required': ['description', 'files_affected']
                        },
                        'maxItems': 4
                    },
                    'threshold': {
                        'type': 'number',
                        'description': 'Optional: Risk score threshold for go/no-go decision (0-100, default: 50)',
                        'minimum': 0,
                        'maximum': 100
                    },
                    'feature_name': {
                        'type': 'string',
                        'description': 'Optional: Feature name for assessment filename (alphanumeric, hyphens, underscores only)',
                        'pattern': '^[a-zA-Z0-9_-]+$'
                    }
                },
                'required': ['project_path', 'proposed_change']
            }
        ),
        Tool(
            name='coderef_foundation_docs',
            description='''Unified foundation docs generator powered by coderef analysis. Generates comprehensive project context for planning workflows by:
- Deep extraction from existing ARCHITECTURE.md, SCHEMA.md (patterns, decisions, constraints)
- Auto-detection of API endpoints, database schemas, dependencies
- Git activity analysis (recent commits, active files, contributors)
- Code pattern detection via coderef-mcp integration (handlers, decorators, error handling)
- Similar feature discovery from coderef/archived/

Outputs:
- ARCHITECTURE.md (patterns, decisions, constraints)
- SCHEMA.md (entities, relationships)
- COMPONENTS.md (component hierarchy - for UI projects only)
- project-context.json (structured context for planning)

Replaces: api_inventory, database_inventory, dependency_inventory, config_inventory, test_inventory, inventory_manifest, documentation_inventory''',
            inputSchema={
                'type': 'object',
                'properties': {
                    'project_path': {
                        'type': 'string',
                        'description': 'Absolute path to project directory'
                    },
                    'include_components': {
                        'type': 'boolean',
                        'description': 'Generate COMPONENTS.md for UI/frontend projects. Default: auto-detect based on project type',
                        'default': None
                    },
                    'deep_extraction': {
                        'type': 'boolean',
                        'description': 'Enable deep extraction from existing foundation docs (vs shallow 500-char preview). Default: true',
                        'default': True
                    },
                    'use_coderef': {
                        'type': 'boolean',
                        'description': 'Use coderef-mcp for code pattern detection. Default: true',
                        'default': True
                    },
                    'force_regenerate': {
                        'type': 'boolean',
                        'description': 'Regenerate existing docs even if they exist. Use after code changes to update documentation. Default: false',
                        'default': False
                    }
                },
                'required': ['project_path']
            }
        ),
        Tool(
            name='generate_features_inventory',
            description='Generate inventory of all features in coderef/workorder/ and coderef/archived/. Returns structured list of features with status, progress, workorder tracking, and workflow coverage. Supports JSON and markdown output formats.',
            inputSchema={
                'type': 'object',
                'properties': {
                    'project_path': {
                        'type': 'string',
                        'description': 'Absolute path to project directory'
                    },
                    'format': {
                        'type': 'string',
                        'enum': ['json', 'markdown'],
                        'description': 'Output format (default: json)',
                        'default': 'json'
                    },
                    'include_archived': {
                        'type': 'boolean',
                        'description': 'Include archived features (default: true)',
                        'default': True
                    },
                    'save_to_file': {
                        'type': 'boolean',
                        'description': 'Save output to coderef/features-inventory.json or .md (default: false)',
                        'default': False
                    }
                },
                'required': ['project_path']
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
