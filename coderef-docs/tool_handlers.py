"""
Tool handler functions for MCP server (QUA-002).

Extracted from server.py to improve maintainability and testability.
Each handler is a standalone async function that can be tested independently.
"""

from pathlib import Path
from mcp.types import TextContent
import json
import jsonschema
import time
from datetime import datetime

# These will be injected from server.py
TEMPLATES_DIR = None
TOOL_TEMPLATES_DIR = None
CODEREF_CONTEXT_AVAILABLE = False  # WO-CONTEXT-DOCS-INTEGRATION-001

# Import dependencies
from typing import Any
from generators import FoundationGenerator, BaseGenerator, ChangelogGenerator, StandardsGenerator, AuditGenerator
from generators.planning_analyzer import PlanningAnalyzer
from generators.plan_validator import PlanValidator
from generators.review_formatter import ReviewFormatter
from generators.planning_generator import PlanningGenerator
from generators.risk_generator import RiskGenerator

# Import extractors for context injection (WO-CONTEXT-DOCS-INTEGRATION-001)
try:
    from extractors import extract_apis, extract_schemas, extract_components
except ImportError:
    # Graceful fallback if extractors not available
    extract_apis = None
    extract_schemas = None
    extract_components = None
from constants import Paths, Files, ScanDepth, FocusArea, AuditSeverity, AuditScope, PlanningPaths
from validation import (
    validate_project_path_input,
    validate_version_format,
    validate_template_name_input,
    validate_changelog_inputs,
    validate_scan_depth,
    validate_focus_areas,
    validate_severity_filter,
    validate_audit_scope,
    validate_section_name,
    validate_plan_file_path,
    validate_feature_name_input,
    validate_risk_inputs,
    validate_resource_path,
    validate_expert_id,
    validate_resource_type,
    validate_expert_domain,
    validate_expert_capabilities,
    VALID_TEMPLATE_SECTIONS
)
from type_defs import PlanningTemplateDict, PreparationSummaryDict, PlanResultDict
from error_responses import ErrorResponse

# Import logging (ARCH-003)
from logger_config import logger

# Import decorators and helpers (ARCH-004, ARCH-005, QUA-004)
from handler_decorators import mcp_error_handler, log_invocation
from handler_helpers import format_success_response, generate_workorder_id, get_workorder_timestamp, add_response_timestamp


@log_invocation
@mcp_error_handler
async def handle_list_templates(arguments: dict) -> list[TextContent]:
    """
    Handle list_templates tool call.

    Uses @log_invocation and @mcp_error_handler decorators for automatic
    logging and error handling (ARCH-004, ARCH-005).
    """
    logger.debug(f"Listing templates from {TEMPLATES_DIR}")
    templates = []
    if TEMPLATES_DIR.exists():
        for file in TEMPLATES_DIR.glob("*.txt"):
            templates.append(file.stem)

    logger.info(f"Found {len(templates)} templates")

    if templates:
        result = "Available POWER Framework Templates:\n\n"
        for i, template in enumerate(sorted(templates), 1):
            result += f"{i}. {template}\n"
        result += f"\nTotal: {len(templates)} templates"
    else:
        logger.warning("No templates found in templates directory")
        result = "No templates found in templates/power/"

    return [TextContent(type="text", text=result)]


@log_invocation
@mcp_error_handler
async def handle_get_template(arguments: dict) -> list[TextContent]:
    """
    Handle get_template tool call.

    Uses @log_invocation and @mcp_error_handler decorators for automatic
    logging and error handling (ARCH-004, ARCH-005).
    """
    # Validate input at boundary (REF-003)
    template_name = validate_template_name_input(arguments.get("template_name", ""))

    logger.debug(f"Reading template: {template_name}")
    template_file = TEMPLATES_DIR / f"{template_name}.txt"

    if not template_file.exists():
        logger.warning(f"Template not found: {template_name}")
        raise FileNotFoundError(f"Template '{template_name}'")

    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()

    logger.info(f"Successfully read template: {template_name}")
    result = f"=== {template_name.upper()} Template ===\n\n{content}"
    return [TextContent(type="text", text=result)]


@log_invocation
@mcp_error_handler
async def handle_generate_foundation_docs(arguments: dict) -> list[TextContent]:
    """
    Handle generate_foundation_docs tool call - SEQUENTIAL GENERATION WITH CONTEXT INJECTION.

    UPGRADED (WO-CONTEXT-DOCS-INTEGRATION-001):
    - Uses sequential generation calling generate_individual_doc 5 times
    - Injects coderef-context intelligence when available
    - Eliminates timeout errors (~250-350 lines per call vs 1,470 all at once)
    - Shows progress markers [1/5], [2/5], etc for visibility

    This provides a complete combination of:
    1. Context injection (real code analysis from @coderef/core CLI)
    2. Sequential generation (no timeouts, manageable response sizes)
    3. Progress visibility (user sees [i/N] markers as docs generate)

    Uses @log_invocation and @mcp_error_handler decorators for automatic
    logging and error handling (ARCH-004, ARCH-005).
    """
    # Validate input at boundary (REF-003)
    project_path = validate_project_path_input(arguments.get("project_path", ""))
    logger.info(f"Generating foundation docs for project: {project_path}")

    # Sequential templates to generate - ordered by dependency
    templates_to_generate = [
        ("api", "API endpoints and integrations"),
        ("schema", "Database schema and data models"),
        ("components", "UI components and architecture"),
        ("architecture", "Overall system architecture"),
        ("readme", "Project README and overview")
    ]

    # Start building response with plan
    result = "=== FOUNDATION DOCS - SEQUENTIAL GENERATION WITH CONTEXT INJECTION ===\n\n"
    result += f"Project: {project_path}\n"
    result += f"Total documents: {len(templates_to_generate)}\n"
    result += f"Context Injection: "
    result += "ENABLED (coderef-context integration active)\n" if CODEREF_CONTEXT_AVAILABLE and extract_apis else "DISABLED (fallback mode)\n"
    result += "\nGeneration Plan:\n"
    result += "-" * 50 + "\n\n"

    for i, (template_name, description) in enumerate(templates_to_generate, 1):
        result += f"[{i}/{len(templates_to_generate)}] {template_name.upper()}\n"
        result += f"    Description: {description}\n"
        if template_name in ["api", "schema", "components"]:
            result += f"    Context Source: @coderef/core CLI (real code analysis)\n"
        result += "\n"

    result += "\n" + "=" * 50 + "\n\n"
    result += "GENERATION SEQUENCE:\n\n"

    # Generate each template sequentially with context injection info
    for i, (template_name, description) in enumerate(templates_to_generate, 1):
        result += f"[{i}/{len(templates_to_generate)}] Generating {template_name.upper()}...\n"
        result += f"Tool: generate_individual_doc\n"
        result += f"Template: {template_name}\n"

        # Show context injection status for API/Schema/Components
        if template_name in ["api", "schema", "components"] and CODEREF_CONTEXT_AVAILABLE and extract_apis:
            result += f"Context Injection: ENABLED\n"
            result += f"  - Calls @coderef/core CLI to extract real {template_name}\n"
            result += f"  - Results cached for efficiency\n"
        elif template_name in ["api", "schema", "components"]:
            result += f"Context Injection: DISABLED (fallback to template placeholders)\n"
        else:
            result += f"Context Injection: N/A (non-extraction template)\n"

        result += "\n"

    result += "=" * 50 + "\n\n"
    result += "INSTRUCTIONS:\n"
    result += "1. Each template will generate in sequence with progress indicators\n"
    result += "2. For API/Schema/Components: Real code intelligence from @coderef/core CLI\n"
    result += "3. Claude will populate templates with extracted data or placeholders\n"
    result += "4. Save each document to its output location as indicated\n"
    result += "5. Each doc builds on previous ones (refs to earlier docs where needed)\n"

    logger.info(f"Successfully generated foundation docs plan with context injection for: {project_path}")
    return [TextContent(type="text", text=result)]


@log_invocation
@mcp_error_handler
async def handle_generate_individual_doc(arguments: dict) -> list[TextContent]:
    """
    Handle generate_individual_doc tool call with context injection.

    UPGRADED (WO-CONTEXT-DOCS-INTEGRATION-001):
    - For API/Schema/Components templates: Injects real code intelligence from @coderef/core CLI
    - Displays extracted data alongside template for Claude to use
    - Gracefully degrades to template-only if extraction unavailable

    Uses @log_invocation and @mcp_error_handler decorators for automatic
    logging and error handling (ARCH-004, ARCH-005).
    """
    # Validate inputs at boundary (REF-003)
    project_path = validate_project_path_input(arguments.get("project_path", ""))
    template_name = validate_template_name_input(arguments.get("template_name", ""))
    logger.info(f"Generating individual doc: {template_name} for project: {project_path}")

    generator = BaseGenerator(TEMPLATES_DIR)

    paths = generator.prepare_generation(project_path)

    template_content = generator.read_template(template_name)
    template_info = generator.get_template_info(template_name)

    # Get correct output path (SEC-003: README goes to root)
    output_path = generator.get_doc_output_path(paths['project_path'], template_name)
    logger.debug(f"Output path determined: {output_path}")

    result = f"=== Generating {template_name.upper()} ===\n\n"
    result += f"Project: {paths['project_path']}\n"
    result += f"Output: {output_path}\n\n"

    # Extract and inject context intelligence for relevant templates
    extracted_data = None
    if CODEREF_CONTEXT_AVAILABLE and template_name in ["api", "schema", "components"]:
        logger.debug(f"Extracting {template_name} using coderef-context CLI")
        try:
            if template_name == "api" and extract_apis:
                extracted_data = extract_apis(paths['project_path'])
            elif template_name == "schema" and extract_schemas:
                extracted_data = extract_schemas(paths['project_path'])
            elif template_name == "components" and extract_components:
                extracted_data = extract_components(paths['project_path'])
        except Exception as e:
            logger.warning(f"Context extraction failed for {template_name}: {e}")
            extracted_data = None

    # Add extraction status to response
    result += "=" * 50 + "\n"
    if template_name in ["api", "schema", "components"]:
        if extracted_data and extracted_data.get('source') == 'coderef-cli':
            result += f"Code Intelligence: [ACTIVE] Real {template_name} extracted via @coderef/core\n"
            result += f"Data Source: @coderef/core CLI (AST-based analysis)\n"
        else:
            result += f"Code Intelligence: [FALLBACK] Using template placeholders\n"
    result += "=" * 50 + "\n\n"

    # Include extracted data in response if available
    if extracted_data and extracted_data.get('source') == 'coderef-cli':
        result += f"EXTRACTED {template_name.upper()} DATA:\n\n"
        if template_name == "api" and "endpoints" in extracted_data:
            result += f"Found {len(extracted_data.get('endpoints', []))} API endpoints:\n\n"
            for endpoint in extracted_data.get('endpoints', [])[:10]:  # Show first 10
                result += f"  - {endpoint.get('method', 'UNKNOWN')} {endpoint.get('path', 'N/A')}\n"
            if len(extracted_data.get('endpoints', [])) > 10:
                result += f"  ... and {len(extracted_data.get('endpoints', [])) - 10} more\n"
        elif template_name == "schema" and "entities" in extracted_data:
            result += f"Found {len(extracted_data.get('entities', []))} data entities:\n\n"
            for entity in extracted_data.get('entities', [])[:10]:  # Show first 10
                result += f"  - {entity.get('name', 'Unknown')}\n"
            if len(extracted_data.get('entities', [])) > 10:
                result += f"  ... and {len(extracted_data.get('entities', [])) - 10} more\n"
        elif template_name == "components" and "components" in extracted_data:
            result += f"Found {len(extracted_data.get('components', []))} UI components:\n\n"
            for component in extracted_data.get('components', [])[:10]:  # Show first 10
                result += f"  - {component.get('name', 'Unknown')} ({component.get('type', 'Component')})\n"
            if len(extracted_data.get('components', [])) > 10:
                result += f"  ... and {len(extracted_data.get('components', [])) - 10} more\n"
        result += "\n" + "=" * 50 + "\n\n"

    result += f"TEMPLATE:\n\n{template_content}\n\n"
    result += "=" * 50 + "\n\n"
    result += "INSTRUCTIONS:\n"
    result += f"Generate {template_info.get('save_as', f'{template_name.upper()}.md')} using the template above.\n"
    if extracted_data and extracted_data.get('source') == 'coderef-cli':
        result += f"IMPORTANT: Populate the template with the extracted {template_name} data above (not placeholders).\n"
        result += f"This ensures the documentation reflects real code structures from @coderef/core analysis.\n"
    result += f"Save the document to: {output_path}\n"

    logger.info(f"Successfully generated plan for {template_name}")
    return [TextContent(type="text", text=result)]


@log_invocation
@mcp_error_handler
async def handle_add_changelog_entry(arguments: dict) -> list[TextContent]:
    """
    Handle add_changelog_entry tool call.

    Uses @log_invocation and @mcp_error_handler decorators for automatic
    logging and error handling (ARCH-004, ARCH-005).
    """
    # Validate inputs at boundary (REF-003)
    project_path = validate_project_path_input(arguments.get("project_path"))

    validated = validate_changelog_inputs(
        version=arguments.get("version"),
        change_type=arguments.get("change_type"),
        severity=arguments.get("severity"),
        title=arguments.get("title"),
        description=arguments.get("description"),
        files=arguments.get("files"),
        reason=arguments.get("reason"),
        impact=arguments.get("impact")
    )

    logger.info(f"Adding changelog entry", extra={
        'project_path': project_path,
        'version': validated['version'],
        'change_type': validated['change_type'],
        'severity': validated['severity'],
        'title': validated['title']
    })

    # Determine changelog location
    changelog_dir = Path(project_path) / Paths.CHANGELOG_DIR
    changelog_path = changelog_dir / Files.CHANGELOG

    # Create directory structure if it doesn't exist
    changelog_dir.mkdir(parents=True, exist_ok=True)

    # Create initial CHANGELOG.json if it doesn't exist
    if not changelog_path.exists():
        initial_data = {
            "$schema": "./schema.json",
            "project": Path(project_path).name,
            "changelog_version": "1.0",
            "current_version": "0.0.0",
            "entries": []
        }
        with open(changelog_path, 'w', encoding='utf-8') as f:
            json.dump(initial_data, f, indent=2)
            f.write('\n')

    generator = ChangelogGenerator(changelog_path)

    # Get optional arguments (validated inputs are in 'validated' dict)
    breaking = arguments.get("breaking", False)
    migration = arguments.get("migration")
    summary = arguments.get("summary")
    contributors = arguments.get("contributors")

    # Add the change (using validated inputs)
    change_id = generator.add_change(
        version=validated['version'],
        change_type=validated['change_type'],
        severity=validated['severity'],
        title=validated['title'],
        description=validated['description'],
        files=validated['files'],
        reason=validated['reason'],
        impact=validated['impact'],
        breaking=breaking,
        migration=migration,
        summary=summary,
        contributors=contributors
    )

    result = f"✅ Changelog entry added successfully!\n\n"
    result += f"Change ID: {change_id}\n"
    result += f"Version: {validated['version']}\n"
    result += f"Type: {validated['change_type']}\n"
    result += f"Title: {validated['title']}\n\n"
    result += f"The changelog has been updated. View coderef/changelog/CHANGELOG.json to see all changes."

    logger.info(f"Successfully added changelog entry: {change_id}", extra={'version': validated['version'], 'change_id': change_id})
    return [TextContent(type="text", text=result)]


@log_invocation
@mcp_error_handler
async def handle_update_changelog(arguments: dict) -> list[TextContent]:
    """
    Handle update_changelog tool call.

    Uses @log_invocation and @mcp_error_handler decorators for automatic
    logging and error handling (ARCH-004, ARCH-005).
    """
    # Validate inputs at boundary (REF-003)
    project_path = validate_project_path_input(arguments.get("project_path"))
    version = validate_version_format(arguments.get("version"))

    logger.info(f"Preparing agentic changelog update workflow", extra={'project_path': project_path, 'version': version})

    project_name = Path(project_path).name

    result = f"📝 Agentic Changelog Update Workflow\n"
    result += f"=" * 60 + "\n\n"
    result += f"Project: {project_name}\n"
    result += f"Version: {version}\n"
    result += f"Location: {project_path}\n\n"
    result += f"=" * 60 + "\n\n"
    result += f"INSTRUCTIONS FOR AGENT:\n\n"
    result += f"You have the context of recent changes you made to this project.\n"
    result += f"Use that context to document your work in the changelog.\n\n"
    result += f"STEP 1: Analyze Your Changes\n"
    result += f"-" * 60 + "\n"
    result += f"Review the changes you just made:\n"
    result += f"• What files did you modify?\n"
    result += f"• What functionality did you add/fix/change?\n"
    result += f"• Why did you make these changes?\n"
    result += f"• What impact does this have on users/system?\n\n"
    result += f"STEP 2: Determine Change Details\n"
    result += f"-" * 60 + "\n"
    result += f"Based on your analysis, determine:\n\n"
    result += f"change_type (pick one):\n"
    result += f"  • bugfix - Fixed a bug or error\n"
    result += f"  • enhancement - Improved existing functionality\n"
    result += f"  • feature - Added new functionality\n"
    result += f"  • breaking_change - Incompatible API changes\n"
    result += f"  • deprecation - Marked features for removal\n"
    result += f"  • security - Security patches\n\n"
    result += f"severity (pick one):\n"
    result += f"  • critical - System broken, data loss risk\n"
    result += f"  • major - Significant feature impact\n"
    result += f"  • minor - Small improvements\n"
    result += f"  • patch - Cosmetic, docs-only\n\n"
    result += f"STEP 3: Call add_changelog_entry\n"
    result += f"-" * 60 + "\n"
    result += f"Use the add_changelog_entry tool with:\n\n"
    result += f"add_changelog_entry(\n"
    result += f"    project_path=\"{project_path}\",\n"
    result += f"    version=\"{version}\",\n"
    result += f"    change_type=\"...\",  # from step 2\n"
    result += f"    severity=\"...\",  # from step 2\n"
    result += f"    title=\"...\",  # short, clear title\n"
    result += f"    description=\"...\",  # what changed\n"
    result += f"    files=[...],  # list of modified files\n"
    result += f"    reason=\"...\",  # why you made this change\n"
    result += f"    impact=\"...\",  # effect on users/system\n"
    result += f"    breaking=false,  # or true if breaking change\n"
    result += f"    contributors=[\"your_name\"]  # optional\n"
    result += f")\n\n"
    result += f"=" * 60 + "\n\n"
    result += f"Execute the above steps using your context and call add_changelog_entry.\n"

    logger.info(f"Changelog update workflow instructions generated for version {version}")
    return [TextContent(type="text", text=result)]


@log_invocation
@mcp_error_handler
async def handle_record_changes(arguments: dict) -> list[TextContent]:
    """
    Handle record_changes tool call - smart agentic changelog recording.

    Auto-detects git context, suggests change_type/severity, shows preview,
    and creates changelog entry upon agent confirmation.

    Uses @log_invocation and @mcp_error_handler decorators for automatic
    logging and error handling (ARCH-004, ARCH-005).
    """
    import subprocess
    import re

    # Validate inputs at boundary (REF-003)
    project_path = validate_project_path_input(arguments.get("project_path"))
    version = validate_version_format(arguments.get("version"))
    context = arguments.get("context", {})

    logger.info(f"Recording changes with auto-detection", extra={'project_path': project_path, 'version': version})

    # Step 1: Auto-detect changed files from git
    changed_files = []
    git_status = "unknown"
    try:
        result = subprocess.run(
            ["git", "-C", project_path, "diff", "--staged", "--name-only"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            changed_files = [f for f in result.stdout.strip().split('\n') if f]
            git_status = "detected"
            logger.debug(f"Detected {len(changed_files)} staged files via git")
        else:
            logger.warning(f"Git diff failed: {result.stderr}")
            git_status = "error"
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        logger.warning(f"Git detection failed: {str(e)}")
        git_status = "unavailable"

    # Fallback to context if provided
    if not changed_files and "files_changed" in context:
        changed_files = context["files_changed"]
        git_status = "from_context"
        logger.debug(f"Using {len(changed_files)} files from context")

    # Step 2: Auto-detect change_type from commit messages
    suggested_type = "enhancement"
    type_from = "default"
    try:
        result = subprocess.run(
            ["git", "-C", project_path, "log", "--oneline", "-5"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            commits = result.stdout.strip()
            # Pattern matching for commit types
            if "BREAKING CHANGE" in commits or re.search(r"^break", commits, re.MULTILINE):
                suggested_type = "breaking_change"
                type_from = "commit: BREAKING CHANGE"
            elif re.search(r"^feat", commits, re.MULTILINE):
                suggested_type = "feature"
                type_from = "commit: feat(...)"
            elif re.search(r"^fix", commits, re.MULTILINE):
                suggested_type = "bugfix"
                type_from = "commit: fix(...)"
            elif re.search(r"^docs", commits, re.MULTILINE):
                suggested_type = "enhancement"
                type_from = "commit: docs(...)"
            logger.debug(f"Suggested change_type: {suggested_type} from {type_from}")
    except Exception as e:
        logger.warning(f"Commit parsing failed: {str(e)}")

    # Step 3: Calculate severity from scope
    suggested_severity = "patch"
    severity_from = "default"

    if suggested_type == "breaking_change":
        suggested_severity = "major"
        severity_from = "breaking API change"
    elif len(changed_files) > 5:
        suggested_severity = "major"
        severity_from = f"scope: {len(changed_files)} files"
    elif len(changed_files) > 2:
        suggested_severity = "minor"
        severity_from = f"scope: {len(changed_files)} files"
    else:
        suggested_severity = "patch"
        severity_from = f"scope: {len(changed_files)} files"

    logger.debug(f"Suggested severity: {suggested_severity} ({severity_from})")

    # Step 4: Generate preview for agent
    preview = f"""📝 CHANGELOG ENTRY PREVIEW
════════════════════════════════════════════════════════

Type: {suggested_type} (from {type_from})
Severity: {suggested_severity} ({severity_from})

Files detected: {len(changed_files)}
{chr(10).join('  • ' + f for f in changed_files[:10])}
{'  ... and ' + str(len(changed_files) - 10) + ' more' if len(changed_files) > 10 else ''}

════════════════════════════════════════════════════════

⚠️  NEXT STEP: Agent must confirm this entry by calling:

record_changes_confirm(
    project_path="{project_path}",
    version="{version}",
    change_type="{suggested_type}",
    severity="{suggested_severity}",
    title="...",  # REQUIRED: Agent must provide
    description="...",  # REQUIRED: what changed
    files={changed_files if changed_files else ['file1.py', 'file2.py']},
    reason="...",  # REQUIRED: why this change
    impact="...",  # REQUIRED: user/system impact
    breaking={'true' if suggested_type == 'breaking_change' else 'false'},
    migration="..." if suggested_type == 'breaking_change' else ""  # REQUIRED if breaking
)

Or use defaults from context and confirm with agent to proceed.
"""

    logger.info(f"Preview generated for {version}", extra={'git_status': git_status, 'type': suggested_type, 'severity': suggested_severity})

    result = f"✅ Auto-detection complete for v{version}\n\n"
    result += preview
    result += f"\n════════════════════════════════════════════════════════\n"
    result += f"Auto-detect metadata:\n"
    result += f"  Files detected via: {git_status}\n"
    result += f"  Type suggested from: {type_from}\n"
    result += f"  Severity from: {severity_from}\n"
    result += f"\nAgent must provide: title, description, reason, impact, and migration (if breaking)\n"

    return [TextContent(type="text", text=result)]


@log_invocation
@mcp_error_handler
async def handle_generate_quickref_interactive(arguments: dict) -> list[TextContent]:
    """
    Handle generate_quickref_interactive tool call (meta-tool).

    Uses @log_invocation and @mcp_error_handler decorators for automatic
    logging and error handling (ARCH-004, ARCH-005).
    """
    # Validate inputs at boundary (REF-003)
    project_path = validate_project_path_input(arguments.get("project_path"))
    app_type = arguments.get("app_type")

    logger.info(f"Initiating quickref generation workflow", extra={'project_path': project_path, 'app_type': app_type})

    # Import QuickrefGenerator
    from generators.quickref_generator import QuickrefGenerator

    # Initialize generator
    generator = QuickrefGenerator()

    # Get interview questions and workflow
    interview = generator.get_interview_questions(app_type)

    # Build response with interview script
    result = f"📋 Universal Quickref Generator - Interactive Workflow\n"
    result += f"=" * 60 + "\n\n"
    result += f"Project: {Path(project_path).name}\n"
    result += f"Output: coderef/user/quickref.md\n"
    if app_type:
        result += f"App Type: {app_type.upper()}\n"
    result += f"\n" + "=" * 60 + "\n\n"
    result += f"INSTRUCTIONS FOR AI:\n\n"
    result += f"{interview['instructions_for_ai']}\n\n"
    result += f"=" * 60 + "\n\n"
    result += f"📝 INTERVIEW WORKFLOW ({interview['total_steps']} steps):\n\n"

    for step in interview['steps']:
        step_num = step.get('step')
        step_name = step.get('name')
        result += f"STEP {step_num}: {step_name}\n"
        result += f"-" * 60 + "\n"

        if 'questions' in step:
            result += f"Ask the user:\n"
            for q in step['questions']:
                result += f"  • {q}\n"
            if 'format' in step:
                result += f"\nExpected format: {step['format']}\n"
        elif 'action' in step:
            result += f"{step['action']}\n"
            if 'output_location' in step:
                result += f"Output: {step['output_location']}\n"

        result += f"\n"

    result += f"=" * 60 + "\n\n"
    result += f"Begin the interview by asking the Step 1 questions.\n"
    result += f"After gathering all information, generate quickref.md using the universal pattern.\n"
    result += f"Save to: {project_path}/coderef/user/quickref.md\n"

    logger.info(f"Quickref generation workflow initiated")
    return [TextContent(type="text", text=result)]


@log_invocation
@mcp_error_handler
async def handle_establish_standards(arguments: dict) -> list[TextContent]:
    """
    Handle establish_standards tool call.

    Uses @log_invocation and @mcp_error_handler decorators for automatic
    logging and error handling (ARCH-004, ARCH-005).
    """
    # Validate and extract inputs (REF-003)
    project_path = validate_project_path_input(arguments.get("project_path", ""))
    scan_depth = validate_scan_depth(
        arguments.get("scan_depth", ScanDepth.STANDARD.value)
    )
    focus_areas = validate_focus_areas(
        arguments.get("focus_areas", [FocusArea.ALL.value])
    )

    logger.info(
        "Starting standards establishment",
        extra={
            'project_path': str(project_path),
            'scan_depth': scan_depth,
            'focus_areas': focus_areas
        }
    )

    # Create standards directory if needed
    project_path_obj = Path(project_path).resolve()
    standards_dir = project_path_obj / Paths.STANDARDS_DIR
    standards_dir.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Standards directory ready: {standards_dir}")

    # Initialize StandardsGenerator
    generator = StandardsGenerator(project_path_obj, scan_depth)

    # Generate and save standards
    result_dict = generator.save_standards(standards_dir)

    # Format success response
    result = f"✅ Standards establishment completed successfully!\n\n"
    result += f"Project: {project_path_obj.name}\n"
    result += f"Scan Depth: {scan_depth}\n"
    result += f"Focus Areas: {', '.join(focus_areas)}\n\n"
    result += f"=" * 60 + "\n\n"
    result += f"📊 RESULTS:\n\n"
    result += f"Files Created: {len(result_dict['files'])}\n"
    result += f"Total Patterns Discovered: {result_dict['patterns_count']}\n"
    result += f"  • UI Patterns: {result_dict['ui_patterns_count']}\n"
    result += f"  • Behavior Patterns: {result_dict['behavior_patterns_count']}\n"
    result += f"  • UX Patterns: {result_dict['ux_patterns_count']}\n"
    result += f"Components Indexed: {result_dict['components_count']}\n\n"
    result += f"=" * 60 + "\n\n"
    result += f"📁 STANDARDS DOCUMENTS:\n\n"
    for file_path in result_dict['files']:
        file_name = Path(file_path).name
        result += f"  • {file_name}\n"
    result += f"\n📂 Location: {standards_dir}\n\n"
    result += f"These standards documents can now be used with:\n"
    result += f"  • Tool #9: audit_codebase - Find violations of standards\n"
    result += f"  • Tool #10: check_consistency - Quality gate for new code\n"

    logger.info(
        "Standards establishment completed successfully",
        extra={
            'files_created': len(result_dict['files']),
            'patterns_discovered': result_dict['patterns_count'],
            'components': result_dict['components_count']
        }
    )

    return [TextContent(type="text", text=result)]


@log_invocation
@mcp_error_handler
async def handle_audit_codebase(arguments: dict) -> list[TextContent]:
    """
    Handle audit_codebase tool call.

    Uses @log_invocation and @mcp_error_handler decorators for automatic
    logging and error handling (ARCH-004, ARCH-005).
    """
    # Validate and extract inputs (REF-003)
    project_path = validate_project_path_input(arguments.get("project_path", ""))
    standards_dir_arg = arguments.get("standards_dir", Paths.STANDARDS_DIR)
    severity_filter = validate_severity_filter(
        arguments.get("severity_filter", AuditSeverity.ALL.value)
    )
    scope = validate_audit_scope(
        arguments.get("scope", [AuditScope.ALL.value])
    )
    generate_fixes = arguments.get("generate_fixes", True)

    logger.info(
        "Starting codebase audit",
        extra={
            'project_path': str(project_path),
            'standards_dir': standards_dir_arg,
            'severity_filter': severity_filter,
            'scope': scope,
            'generate_fixes': generate_fixes
        }
    )

    # Resolve project path and standards directory
    project_path_obj = Path(project_path).resolve()
    standards_dir = project_path_obj / standards_dir_arg

    # Check if standards documents exist (SEC-001) - raise exception instead of early return
    if not standards_dir.exists():
        logger.warning(f"Standards directory not found: {standards_dir}")
        raise FileNotFoundError(f"Standards directory: {standards_dir}")

    # Check if required standards files exist - raise exception instead of early return
    required_files = [Files.UI_STANDARDS, Files.BEHAVIOR_STANDARDS, Files.UX_PATTERNS]
    missing_files = []
    for file_name in required_files:
        if not (standards_dir / file_name).exists():
            missing_files.append(file_name)

    if missing_files:
        logger.warning(f"Missing standards files: {missing_files}")
        raise FileNotFoundError(f"Standards files: {', '.join(missing_files)}")

    logger.debug(f"Standards directory verified: {standards_dir}")

    # Initialize AuditGenerator
    generator = AuditGenerator(project_path_obj, standards_dir)
    logger.debug("AuditGenerator initialized")

    # Start timing
    start_time = time.time()

    # Parse standards documents
    logger.info("Parsing standards documents")
    standards = generator.parse_standards_documents(standards_dir)

    if standards.get('parse_errors'):
        logger.warning(f"Standards parsing had errors: {standards['parse_errors']}")

    # Scan for violations
    logger.info("Scanning codebase for violations")
    violations = generator.scan_for_violations(standards)

    # Extract files_scanned metadata
    files_scanned = 0
    if violations:
        # Check if first violation has metadata
        if '_files_scanned' in violations[0]:
            files_scanned = violations[0].pop('_files_scanned')

        # Remove metadata-only entries
        violations = [v for v in violations if not v.get('_is_metadata', False)]

    # Filter violations by severity if not 'all'
    if severity_filter != AuditSeverity.ALL.value:
        violations = [v for v in violations if v.get('severity') == severity_filter]
        logger.debug(f"Filtered to {len(violations)} violations with severity={severity_filter}")

    # Calculate compliance score
    logger.info("Calculating compliance score")
    total_patterns = (
        len(standards.get('ui_patterns', {}).get('buttons', {}).get('allowed_sizes', [])) +
        len(standards.get('ui_patterns', {}).get('buttons', {}).get('allowed_variants', [])) +
        len(standards.get('ui_patterns', {}).get('colors', {}).get('allowed_hex_codes', [])) +
        len(standards.get('behavior_patterns', {}).get('error_handling', {}).get('expected_patterns', []))
    )
    compliance = generator.calculate_compliance_score(violations, total_patterns)

    # End timing
    end_time = time.time()
    duration = end_time - start_time

    # Build scan metadata
    scan_metadata = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'duration': duration,
        'files_scanned': files_scanned,
        'standards_files': standards.get('source_files', []),
        'parse_errors': standards.get('parse_errors', [])
    }

    # Generate audit report
    logger.info("Generating audit report")
    report_content = generator.generate_audit_report(violations, compliance, scan_metadata)

    # Save audit report
    audits_dir = project_path_obj / Paths.AUDITS_DIR
    result_dict = generator.save_audit_report(
        report_content, audits_dir, violations, compliance, scan_metadata
    )

    # Format success response
    result = f"✅ Codebase audit completed successfully!\n\n"
    result += f"Project: {project_path_obj.name}\n"
    result += f"Standards: {standards_dir_arg}\n"
    result += f"Severity Filter: {severity_filter}\n"
    result += f"Scope: {', '.join(scope)}\n\n"
    result += f"=" * 60 + "\n\n"
    result += f"📊 AUDIT RESULTS:\n\n"
    result += f"Compliance Score: {compliance['overall_score']}/100 ({compliance['grade']})\n"
    result += f"Status: {'✅ PASSING' if compliance['passing'] else '❌ FAILING'}\n\n"
    result += f"Violations Found: {result_dict['violation_stats']['total_violations']}\n"
    result += f"  • Critical: {result_dict['violation_stats']['critical_count']}\n"
    result += f"  • Major: {result_dict['violation_stats']['major_count']}\n"
    result += f"  • Minor: {result_dict['violation_stats']['minor_count']}\n\n"
    result += f"Scan Duration: {duration:.2f} seconds\n"
    result += f"Files Scanned: {scan_metadata['files_scanned']}\n\n"
    result += f"=" * 60 + "\n\n"
    result += f"📁 AUDIT REPORT:\n\n"
    result += f"  • {result_dict['report_path']}\n\n"

    if standards.get('parse_errors'):
        result += f"⚠️  WARNINGS:\n"
        for error in standards['parse_errors']:
            result += f"  • {error}\n"
        result += "\n"

    result += f"Next steps:\n"
    result += f"  1. Review the audit report at {result_dict['report_path']}\n"
    result += f"  2. Address critical and major violations first\n"
    if generate_fixes:
        result += f"  3. Use the fix suggestions in the report\n"
    result += f"  4. Re-run audit_codebase to verify fixes\n"

    logger.info(
        "Codebase audit completed successfully",
        extra={
            'compliance_score': compliance['overall_score'],
            'violations_found': len(violations),
            'report_path': result_dict['report_path']
        }
    )

    return [TextContent(type="text", text=result)]


@log_invocation
@mcp_error_handler
async def handle_check_consistency(arguments: dict) -> list[TextContent]:
    """
    Handle check_consistency tool call.

    Uses @log_invocation and @mcp_error_handler decorators for automatic
    logging and error handling (ARCH-004, ARCH-005).
    """
    # Validate and extract inputs (REF-003)
    project_path = validate_project_path_input(arguments.get("project_path", ""))
    files = arguments.get("files")  # Optional - will auto-detect if not provided
    standards_dir_arg = arguments.get("standards_dir", Paths.STANDARDS_DIR)
    severity_threshold = arguments.get("severity_threshold", "major")  # critical, major, or minor
    scope = validate_audit_scope(arguments.get("scope", [AuditScope.ALL.value]))
    fail_on_violations = arguments.get("fail_on_violations", True)

    # Validate optional parameters
    from validation import validate_severity_threshold, validate_file_list
    severity_threshold = validate_severity_threshold(severity_threshold)
    if files is not None:
        files = validate_file_list(files)

    logger.info(
        "Starting consistency check",
        extra={
            'project_path': str(project_path),
            'files_provided': files is not None,
            'severity_threshold': severity_threshold,
            'scope': scope
        }
    )

    # Resolve paths
    project_path_obj = Path(project_path).resolve()
    standards_dir = project_path_obj / standards_dir_arg

    # Check if standards exist - raise exception instead of early return
    if not standards_dir.exists():
        logger.warning(f"Standards directory not found: {standards_dir}")
        raise FileNotFoundError(f"Standards directory: {standards_dir}")

    # Initialize ConsistencyChecker
    from generators.consistency_checker import ConsistencyChecker
    checker = ConsistencyChecker(project_path_obj, standards_dir)
    logger.debug("ConsistencyChecker initialized")

    # Detect or use provided files
    if files is None:
        # Auto-detect from git
        logger.info("Auto-detecting changed files from git")
        files_to_check = checker.detect_changed_files(mode='staged')

        if not checker.is_git_repository():
            logger.error("Not a git repository and no files specified")
            raise ValueError("Not a git repository and no files specified")

        # Check if no files to check (this is NOT an error, just "no work to do")
        if not files_to_check:
            logger.info("No files to check (no staged changes)")
            result = "[PASS] Consistency check PASSED\n\n"
            result += "0 violations found\n"
            result += "Files checked: 0\n"
            result += "Duration: 0.00s\n\n"
            result += "No files to check (no staged changes)."
            return [TextContent(type="text", text=result)]
    else:
        # Use provided files (convert to Path objects)
        files_to_check = [Path(f) for f in files]

    logger.info(f"Checking {len(files_to_check)} files", extra={'files_count': len(files_to_check)})

    # Start timing
    start_time = time.time()

    # Parse standards
    logger.info("Parsing standards documents")
    standards = checker.audit_generator.parse_standards_documents(standards_dir)

    # Check files for violations
    logger.info("Checking files for violations")
    violations = checker.check_files(files_to_check, standards, scope)

    # Filter by severity threshold
    logger.info(f"Filtering violations by severity threshold: {severity_threshold}")
    violations = checker.filter_by_severity_threshold(violations, severity_threshold)

    # Calculate duration
    duration = time.time() - start_time

    # Determine status and exit code
    status = 'pass' if len(violations) == 0 else 'fail'
    exit_code = 1 if (fail_on_violations and status == 'fail') else 0

    # Generate terminal-friendly summary
    summary = checker.generate_check_summary(violations, len(files_to_check), duration)

    # Log completion
    logger.info(
        "Consistency check completed",
        extra={
            'status': status,
            'violations_found': len(violations),
            'files_checked': len(files_to_check),
            'duration': duration,
            'exit_code': exit_code
        }
    )

    return [TextContent(type="text", text=summary)]



# =============================================================================
# Tool handlers registry - MINIMAL (10 documentation tools)
# =============================================================================
TOOL_HANDLERS = {
    'list_templates': handle_list_templates,
    'get_template': handle_get_template,
    'generate_foundation_docs': handle_generate_foundation_docs,
    'generate_individual_doc': handle_generate_individual_doc,
    'add_changelog_entry': handle_add_changelog_entry,
    'record_changes': handle_record_changes,
    'generate_quickref_interactive': handle_generate_quickref_interactive,
    'establish_standards': handle_establish_standards,
    'audit_codebase': handle_audit_codebase,
    'check_consistency': handle_check_consistency,
}


def set_templates_dir(templates_dir: Path) -> None:
    """Set the TEMPLATES_DIR global for handlers to use."""
    global TEMPLATES_DIR
    TEMPLATES_DIR = templates_dir


def set_tool_templates_dir(tool_templates_dir: Path) -> None:
    """Set the TOOL_TEMPLATES_DIR global for handlers to use."""
    global TOOL_TEMPLATES_DIR
    TOOL_TEMPLATES_DIR = tool_templates_dir


def set_coderef_context_available(available: bool) -> None:
    """
    Set the CODEREF_CONTEXT_AVAILABLE global flag for handlers to use.

    Part of WO-CONTEXT-DOCS-INTEGRATION-001 Phase 1.
    """
    global CODEREF_CONTEXT_AVAILABLE
    CODEREF_CONTEXT_AVAILABLE = available
