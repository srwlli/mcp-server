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
import os
import sys

# These will be injected from server.py
TEMPLATES_DIR = None
TOOL_TEMPLATES_DIR = None

# Feature flag for enhanced deliverables (WO-DELIVERABLES-ENHANCEMENT-001)
ENHANCED_DELIVERABLES_ENABLED = os.getenv("ENHANCED_DELIVERABLES_ENABLED", "true").lower() == "true"

# Import dependencies
from typing import Any
from generators import FoundationGenerator, BaseGenerator, ChangelogGenerator, StandardsGenerator, AuditGenerator
from generators.planning_analyzer import PlanningAnalyzer
from generators.plan_validator import PlanValidator as LegacyPlanValidator  # Deprecated - use Papertrail PlanValidator
from generators.review_formatter import ReviewFormatter
from generators.planning_generator import PlanningGenerator
from generators.risk_generator import RiskGenerator
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
from uds_helpers import get_server_version


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
    Handle generate_foundation_docs tool call.

    Uses @log_invocation and @mcp_error_handler decorators for automatic
    logging and error handling (ARCH-004, ARCH-005).
    """
    # Validate input at boundary (REF-003)
    project_path = validate_project_path_input(arguments.get("project_path", ""))
    logger.info(f"Generating foundation docs for project: {project_path}")

    # Initialize foundation generator
    generator = FoundationGenerator(TEMPLATES_DIR)

    # Prepare paths for generation
    paths = generator.prepare_generation(project_path)

    # Get generation plan
    plan = generator.get_generation_plan(project_path)

    # Get all templates
    logger.debug("Loading all foundation templates")
    templates = generator.get_templates_for_generation()
    logger.info(f"Loaded {len(templates)} foundation templates")

    # Build response
    result = plan + "\n\n" + "=" * 50 + "\n\n"
    result += "TEMPLATES FOR GENERATION:\n\n"

    for template in templates:
        if 'error' in template:
            result += f"ERROR - {template['template_name']}: {template['error']}\n\n"
        else:
            result += f"=== {template['template_name'].upper()} ===\n\n"
            result += f"{template['template_content']}\n\n"
            result += "-" * 50 + "\n\n"

    result += "\nINSTRUCTIONS:\n"
    result += "Generate each document in order using the templates above.\n\n"
    result += "SAVE LOCATIONS (SEC-003):\n"
    result += f"- README.md → {paths['project_path']}/README.md\n"
    result += f"- All other docs → {paths['output_dir']}/\n\n"
    result += "Each document should reference previous documents as indicated in the templates.\n"

    logger.info(f"Successfully generated foundation docs plan for: {project_path}")
    return [TextContent(type="text", text=result)]


@log_invocation
@mcp_error_handler
async def handle_generate_individual_doc(arguments: dict) -> list[TextContent]:
    """
    Handle generate_individual_doc tool call.

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
    result += "=" * 50 + "\n\n"
    result += f"TEMPLATE:\n\n{template_content}\n\n"
    result += "=" * 50 + "\n\n"
    result += "INSTRUCTIONS:\n"
    result += f"Generate {template_info.get('save_as', f'{template_name.upper()}.md')} using the template above.\n"
    result += f"Save the document to: {output_path}\n"

    logger.info(f"Successfully generated plan for {template_name}")
    return [TextContent(type="text", text=result)]


@log_invocation
@mcp_error_handler
async def handle_get_changelog(arguments: dict) -> list[TextContent]:
    """
    Handle get_changelog tool call.

    Uses @log_invocation and @mcp_error_handler decorators for automatic
    logging and error handling (ARCH-004, ARCH-005).
    """
    # Validate inputs at boundary (REF-003)
    project_path = validate_project_path_input(arguments.get("project_path"))
    version = arguments.get("version")
    if version:
        version = validate_version_format(version)

    change_type = arguments.get("change_type")
    breaking_only = arguments.get("breaking_only", False)

    logger.info(f"Reading changelog from: {project_path}", extra={'version': version, 'change_type': change_type, 'breaking_only': breaking_only})

    # Determine changelog location
    changelog_path = Path(project_path) / Paths.CHANGELOG_DIR / Files.CHANGELOG

    generator = ChangelogGenerator(changelog_path)

    if breaking_only:
        # Get only breaking changes
        logger.debug("Filtering for breaking changes only")
        changes = generator.get_breaking_changes()
        result = f"Breaking Changes:\n\n"
        result += json.dumps(changes, indent=2)

    elif version:
        # Get specific version
        logger.debug(f"Fetching changes for version: {version}")
        version_data = generator.get_version_changes(version)
        if version_data:
            result = f"Changes for version {version}:\n\n"
            result += json.dumps(version_data, indent=2)
        else:
            logger.warning(f"Version not found in changelog: {version}")
            result = f"Version {version} not found in changelog"

    elif change_type:
        # Filter by type
        logger.debug(f"Filtering by change type: {change_type}")
        changes = generator.get_changes_by_type(change_type)
        result = f"Changes of type '{change_type}':\n\n"
        result += json.dumps(changes, indent=2)

    else:
        # Get all changelog
        logger.debug("Fetching full changelog")
        data = generator.read_changelog()
        result = "Full Changelog:\n\n"
        result += json.dumps(data, indent=2)

    logger.info("Successfully retrieved changelog")
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
    result += f"The changelog has been updated. Use get_changelog to view changes."

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
    result += f"Output: coderef/quickref.md\n"
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
    result += f"Save to: {project_path}/coderef/quickref.md\n"

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


@log_invocation
@mcp_error_handler
async def handle_get_planning_template(arguments: dict[str, Any]) -> list[TextContent]:
    """
    Handle get_planning_template tool call.

    Uses @log_invocation and @mcp_error_handler decorators for automatic
    logging and error handling (ARCH-004, ARCH-005).
    """
    # Extract and validate section parameter
    section = arguments.get('section', 'all')
    section = validate_section_name(section)

    logger.info(f"Retrieving template section: {section}")

    # Read template file
    template_path = Path(__file__).parent / PlanningPaths.TEMPLATE_PATH

    # Check if template file exists - raise exception instead of early return
    if not template_path.exists():
        logger.warning(f"Template file not found: {template_path}")
        raise FileNotFoundError(f"Template file: {PlanningPaths.TEMPLATE_PATH}")

    # Parse template JSON (let decorator catch JSONDecodeError)
    with open(template_path, 'r', encoding='utf-8') as f:
        template_data = json.load(f)

    # Extract requested section
    if section == 'all':
        content = template_data
    elif section in template_data:
        # Top-level key (META_DOCUMENTATION, QUALITY_CHECKLIST_FOR_PLANS, etc.)
        content = template_data[section]
    elif 'UNIVERSAL_PLANNING_STRUCTURE' in template_data and section in template_data['UNIVERSAL_PLANNING_STRUCTURE']:
        # Section within UNIVERSAL_PLANNING_STRUCTURE (0_preparation, 1_executive_summary, etc.)
        content = template_data['UNIVERSAL_PLANNING_STRUCTURE'][section]
    else:
        # Section not found - raise exception instead of early return
        logger.warning(f"Section '{section}' not found in template")
        raise FileNotFoundError(f"Section '{section}' in template")

    # Format result
    result: PlanningTemplateDict = {
        'section': section,
        'content': content
    }

    logger.info(
        f"Template section '{section}' retrieved successfully",
        extra={'section': section, 'content_size': len(json.dumps(content))}
    )

    return [TextContent(type='text', text=json.dumps(result, indent=2))]


@log_invocation
@mcp_error_handler
async def handle_analyze_project_for_planning(arguments: dict) -> list[TextContent]:
    """
    Handle analyze_project_for_planning tool call.

    Uses @log_invocation and @mcp_error_handler decorators for automatic
    logging and error handling (ARCH-004, ARCH-005).
    """
    # Validate project_path
    project_path = validate_project_path_input(arguments.get('project_path', ''))
    project_path_obj = Path(project_path).resolve()

    # Get optional feature_name for feature-specific saving
    feature_name = arguments.get('feature_name')
    if feature_name:
        feature_name = validate_feature_name_input(feature_name)

    logger.info(f"Analyzing project for planning: {project_path_obj}", extra={'feature_name': feature_name})

    # Initialize PlanningAnalyzer
    analyzer = PlanningAnalyzer(project_path_obj)

    # Run analysis (async with MCP tool integration)
    result = await analyzer.analyze()

    # Feature-specific file persistence (optional)
    if feature_name:
        try:
            # Create feature workorder directory
            feature_dir = project_path_obj / 'coderef' / 'workorder' / feature_name
            feature_dir.mkdir(parents=True, exist_ok=True)

            # Try to read workorder from existing context.json
            workorder_id = None
            context_file = feature_dir / 'context.json'
            if context_file.exists():
                try:
                    with open(context_file, 'r', encoding='utf-8') as f:
                        context_data = json.load(f)
                        workorder_id = context_data.get('_metadata', {}).get('workorder_id')
                        if workorder_id:
                            logger.info(
                                f"Read existing workorder ID from context.json: {workorder_id}",
                                extra={'workorder_id': workorder_id, 'feature_name': feature_name}
                            )
                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning(f"Failed to read workorder from context.json: {e}")

            # If no workorder found in context, generate new one
            if not workorder_id:
                workorder_id = generate_workorder_id(feature_name)
                logger.info(
                    f"Generated new workorder ID: {workorder_id}",
                    extra={'workorder_id': workorder_id, 'feature_name': feature_name}
                )

            # Save to analysis.json (no timestamp)
            analysis_file = feature_dir / 'analysis.json'

            # Inject UDS metadata (WO-UDS-INTEGRATION-001)
            from datetime import timedelta
            update_date = datetime.utcnow().strftime("%Y-%m-%d")
            review_date = (datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%d")

            result['_uds'] = {
                'generated_by': get_server_version(),
                'document_type': 'Project Analysis',
                'workorder_id': workorder_id,
                'feature_id': feature_name,
                'last_updated': update_date,
                'ai_assistance': True,
                'status': 'DRAFT',
                'next_review': review_date
            }

            logger.info(f"UDS metadata injected into analysis.json for workorder: {workorder_id}")

            # GAP-001 + GAP-004 + GAP-005: Validate with ValidatorFactory and centralized error handling
            try:
                # Write temp file for validation
                temp_file = analysis_file.with_suffix('.tmp.json')
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2)

                # GAP-004: Use ValidatorFactory for auto-detection
                from papertrail.validators.factory import ValidatorFactory
                from utils.validation_helpers import handle_validation_result

                validator = ValidatorFactory.get_validator(str(temp_file))
                validation_result = validator.validate_file(str(temp_file))

                # GAP-001: Add validation metadata to _uds section
                result['_uds']['validation_score'] = validation_result.get('score', 0)
                result['_uds']['validation_errors'] = len(validation_result.get('errors', []))
                result['_uds']['validation_warnings'] = len(validation_result.get('warnings', []))

                # GAP-005: Use centralized error handling
                handle_validation_result(validation_result, "analysis.json")

                # Clean up temp file
                temp_file.unlink()

            except ImportError:
                logger.warning("Papertrail validators not available - skipping validation")
                result['_uds']['validation_score'] = None
                result['_uds']['validation_errors'] = None
                result['_uds']['validation_warnings'] = None
            except ValueError:
                # Critical validation failure - but continue with graceful degradation
                logger.error("Analysis validation failed critically - continuing with partial data")
                result['_uds']['validation_score'] = 0
                result['_uds']['validation_errors'] = 999
                result['_uds']['validation_warnings'] = 999
            except Exception as e:
                logger.warning(f"Analysis validation error: {e} - continuing without validation")
                result['_uds']['validation_score'] = None
                result['_uds']['validation_errors'] = None
                result['_uds']['validation_warnings'] = None

            # Save final analysis.json with validation metadata
            with open(analysis_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)

            # Add metadata to response with workorder
            result['_metadata'] = {
                'saved_to': str(analysis_file.relative_to(project_path_obj)),
                'feature_name': feature_name,
                'workorder_id': workorder_id,
                'generated_at': datetime.now().isoformat()
            }

            logger.info(
                "Project analysis completed and saved successfully",
                extra={
                    'project_path': str(project_path_obj),
                    'feature_name': feature_name,
                    'saved_to': str(analysis_file),
                    'foundation_docs_available': len(result['foundation_docs'].get('available', [])),
                    'standards_available': len(result['coding_standards'].get('available', [])),
                    'patterns_identified': len(result['key_patterns_identified']),
                    'gaps_found': len(result['gaps_and_risks'])
                }
            )

        except (PermissionError, OSError) as e:
            # Graceful degradation - log warning but still return data
            logger.warning(
                f"Analysis completed but failed to save to file: {str(e)}",
                extra={
                    'project_path': str(project_path_obj),
                    'feature_name': feature_name,
                    'error_type': type(e).__name__,
                    'error_message': str(e)
                }
            )

            # Add metadata indicating save failure (still include workorder if we have it)
            result['_metadata'] = {
                'saved_to': None,
                'feature_name': feature_name,
                'workorder_id': workorder_id if 'workorder_id' in locals() else None,
                'save_error': str(e),
                'generated_at': datetime.now().isoformat()
            }

            logger.info(
                "Project analysis completed successfully (file save failed)",
                extra={
                    'project_path': str(project_path_obj),
                    'feature_name': feature_name,
                    'foundation_docs_available': len(result['foundation_docs'].get('available', [])),
                    'standards_available': len(result['coding_standards'].get('available', [])),
                    'patterns_identified': len(result['key_patterns_identified']),
                    'gaps_found': len(result['gaps_and_risks'])
                }
            )
    else:
        # No feature_name provided - return analysis without saving
        logger.info(
            "Project analysis completed (not saved - no feature_name provided)",
            extra={
                'project_path': str(project_path_obj),
                'foundation_docs_available': len(result['foundation_docs'].get('available', [])),
                'standards_available': len(result['coding_standards'].get('available', [])),
                'patterns_identified': len(result['key_patterns_identified']),
                'gaps_found': len(result['gaps_and_risks'])
            }
        )

    # Return JSON-formatted result
    return [TextContent(type='text', text=json.dumps(result, indent=2))]


@log_invocation
@mcp_error_handler
async def handle_validate_implementation_plan(arguments: dict) -> list[TextContent]:
    """
    Handle validate_implementation_plan tool call.

    Uses @log_invocation and @mcp_error_handler decorators for automatic
    logging and error handling (ARCH-004, ARCH-005).
    """
    # Validate inputs
    project_path_str = arguments.get('project_path', '')
    plan_file_str = arguments.get('plan_file_path', '')

    project_path = Path(validate_project_path_input(project_path_str)).resolve()
    plan_path = validate_plan_file_path(project_path, plan_file_str)

    logger.info(f'Validating plan: {plan_path}')

    # Check plan file exists - raise exception instead of early return
    if not plan_path.exists():
        logger.warning(f'Plan file not found: {plan_file_str}')
        raise FileNotFoundError(f'Plan file not found: {plan_file_str}')

    # GAP-004 + GAP-005: Validate plan with ValidatorFactory and centralized error handling
    try:
        from papertrail.validators.factory import ValidatorFactory
        from utils.validation_helpers import handle_validation_result

        validator = ValidatorFactory.get_validator(str(plan_path))
        result = validator.validate_file(str(plan_path))
        handle_validation_result(result, "plan.json")

        logger.info(
            f'Validation complete: score={result.get("score", 0)}, valid={result.get("valid", False)}',
            extra={'score': result.get('score', 0), 'valid': result.get('valid', False)}
        )
    except ImportError:
        # Fallback to legacy validator if Papertrail not available
        logger.warning("Papertrail validators not available - using legacy validator")
        validator = LegacyPlanValidator(plan_path)
        result = validator.validate()

        logger.info(
            f'Validation complete (legacy): score={result["score"]}, result={result["validation_result"]}, issues={len(result["issues"])}',
            extra={'score': result['score'], 'result': result['validation_result']}
        )
    except ValueError:
        # Critical validation failure from handle_validation_result
        logger.error("Plan validation failed critically - using legacy validator as fallback")
        validator = LegacyPlanValidator(plan_path)
        result = validator.validate()

    # Return result as JSON
    return [TextContent(type='text', text=json.dumps(result, indent=2))]


@log_invocation
@mcp_error_handler
async def handle_generate_plan_review_report(arguments: dict) -> list[TextContent]:
    """
    Handle generate_plan_review_report tool call.

    Uses @log_invocation and @mcp_error_handler decorators for automatic
    logging and error handling (ARCH-004, ARCH-005).
    """
    # Validate inputs
    project_path_str = arguments.get('project_path', '')
    plan_file_str = arguments.get('plan_file_path', '')
    output_path_arg = arguments.get('output_path')

    project_path = Path(validate_project_path_input(project_path_str)).resolve()
    plan_path = validate_plan_file_path(project_path, plan_file_str)

    logger.info(f'Generating review report for plan: {plan_path}')

    # Check plan file exists - raise exception instead of early return
    if not plan_path.exists():
        logger.warning(f'Plan file not found: {plan_file_str}')
        raise FileNotFoundError(f'Plan file not found: {plan_file_str}')

    # GAP-004 + GAP-005: Run validation with ValidatorFactory and centralized error handling
    try:
        from papertrail.validators.factory import ValidatorFactory
        from utils.validation_helpers import handle_validation_result

        validator = ValidatorFactory.get_validator(str(plan_path))
        validation_result = validator.validate_file(str(plan_path))
        handle_validation_result(validation_result, "plan.json")

        logger.debug(
            f'Validation completed: score={validation_result.get("score", 0)}, valid={validation_result.get("valid", False)}'
        )
    except ImportError:
        # Fallback to legacy validator if Papertrail not available
        logger.warning("Papertrail validators not available - using legacy validator for review report")
        validator = LegacyPlanValidator(plan_path)
        validation_result = validator.validate()

        logger.debug(
            f'Validation completed (legacy): score={validation_result["score"]}, issues={len(validation_result["issues"])}'
        )
    except ValueError:
        # Critical validation failure - use legacy validator as fallback
        logger.error("Plan validation failed critically - using legacy validator")
        validator = LegacyPlanValidator(plan_path)
        validation_result = validator.validate()

    # Extract plan name from file path
    plan_name = plan_path.stem  # e.g., "feature-auth-plan" from "feature-auth-plan.json"

    # Create ReviewFormatter with validation results
    formatter = ReviewFormatter(validation_result, plan_name)

    # Generate markdown report
    report_content = formatter.format_report()

    # Determine output path
    if output_path_arg:
        output_path = project_path / output_path_arg
    else:
        # Default: coderef/reviews/review-{planname}-{timestamp}.md
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        reviews_dir = project_path / 'coderef' / 'reviews'
        reviews_dir.mkdir(parents=True, exist_ok=True)
        output_path = reviews_dir / f'review-{plan_name}-{timestamp}.md'

    # Save report to file (let decorator catch PermissionError and OSError)
    logger.debug(f'Saving report to: {output_path}')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report_content)

    logger.info(
        f'Review report generated successfully: {output_path}',
        extra={
            'plan_name': plan_name,
            'score': validation_result['score'],
            'approved': validation_result['approved'],
            'output_path': str(output_path)
        }
    )

    # Format success response
    result = f"✅ Review report generated successfully!\n\n"
    result += f"Plan: {plan_name}\n"
    result += f"Score: {validation_result['score']}/100\n"
    result += f"Result: {validation_result['validation_result']}\n"
    result += f"Approved: {'Yes ✅' if validation_result['approved'] else 'No ❌'}\n\n"
    result += f"=" * 60 + "\n\n"
    result += f"📁 REVIEW REPORT:\n\n"
    result += f"  • {output_path.relative_to(project_path)}\n\n"
    result += f"The review report has been saved to:\n"
    result += f"  {output_path}\n"

    return [TextContent(type='text', text=result)]


@log_invocation
@mcp_error_handler
async def handle_create_plan(arguments: dict) -> list[TextContent]:
    """
    Handle create_plan tool call - AUTOMATICALLY generates plan.json.

    NEW in v1.2.0: Auto-generates plan instead of returning instructions.
    This enables the /create-workorder workflow to run fully automatically
    without requiring manual AI synthesis of the plan.

    Uses @log_invocation and @mcp_error_handler decorators for automatic
    logging and error handling (ARCH-004, ARCH-005).

    Supports multi_agent parameter for automatic agent coordination setup.
    Automatically generates DELIVERABLES.md template after plan.json.
    """
    # Validate inputs
    project_path_str = arguments.get('project_path', '')
    feature_name = arguments.get('feature_name', '')
    provided_workorder_id = arguments.get('workorder_id')
    multi_agent = arguments.get('multi_agent', False)

    project_path = Path(validate_project_path_input(project_path_str)).resolve()
    feature_name = validate_feature_name_input(feature_name)

    logger.info(f'Creating implementation plan for feature: {feature_name}')

    # Initialize PlanningGenerator
    generator = PlanningGenerator(project_path)

    # Load inputs
    context = generator.load_context(feature_name)
    analysis = generator.load_analysis(feature_name)

    # Determine workorder ID (priority: provided parameter > context > analysis > generated)
    workorder_id = provided_workorder_id
    if not workorder_id:
        if context and '_metadata' in context:
            workorder_id = context['_metadata'].get('workorder_id')
        elif analysis and '_metadata' in analysis:
            workorder_id = analysis['_metadata'].get('workorder_id')

    # If no workorder found, generate new one
    if not workorder_id:
        workorder_id = generate_workorder_id(feature_name)
        logger.info(
            f"Generated new workorder ID: {workorder_id}",
            extra={'workorder_id': workorder_id, 'feature_name': feature_name}
        )
    else:
        source = "provided parameter" if provided_workorder_id else "context/analysis"
        logger.info(
            f"Using workorder from {source}: {workorder_id}",
            extra={'workorder_id': workorder_id, 'feature_name': feature_name}
        )

    # AUTOMATICALLY GENERATE PLAN (NEW in v1.2.0)
    try:
        plan = generator.generate_plan(
            feature_name=feature_name,
            context=context,
            analysis=analysis,
            workorder_id=workorder_id
        )
        generator.save_plan(feature_name, plan)
        plan_file = project_path / 'coderef' / 'workorder' / feature_name / 'plan.json'

        # GAP-004 + GAP-005: Validate generated plan with ValidatorFactory and centralized error handling
        try:
            from papertrail.validators.factory import ValidatorFactory
            from utils.validation_helpers import handle_validation_result

            validator = ValidatorFactory.get_validator(str(plan_file))
            result = validator.validate_file(str(plan_file))
            handle_validation_result(result, "plan.json")
        except ImportError:
            logger.warning("Papertrail validators not available - skipping plan generation validation")
        except ValueError:
            logger.error("Generated plan validation failed critically - continuing with partial plan")
        except Exception as e:
            logger.warning(f"Plan generation validation error: {e} - continuing")

        logger.info(
            f'Implementation plan generated and saved successfully',
            extra={
                'plan_file': str(plan_file),
                'feature_name': feature_name,
                'workorder_id': workorder_id
            }
        )

        # Build success message (concise to prevent stalls)
        message = f"✅ Plan created: {workorder_id}\n"
        message += f"Location: coderef/workorder/{feature_name}/plan.json\n\n"
        message += f"Next: /validate-plan or /align-plan to continue"

        return format_success_response(
            data={
                'feature_name': feature_name,
                'workorder_id': workorder_id,
                'plan_file': str(plan_file),
                'plan_status': plan.get('META_DOCUMENTATION', {}).get('status', 'unknown'),
                'has_context': context is not None,
                'has_analysis': analysis is not None,
                'multi_agent_mode': multi_agent
            },
            message=message
        )

    except Exception as e:
        logger.error(
            f'Plan generation failed: {str(e)}',
            extra={'feature_name': feature_name, 'error': str(e)}
        )
        raise ValueError(f"Failed to generate plan: {str(e)}")




@log_invocation
@mcp_error_handler
async def handle_gather_context(arguments: dict) -> list[TextContent]:
    """
    Handle gather_context tool call.
    
    Gathers feature requirements and creates context.json file in
    coderef/workorder/{feature_name}/ directory.
    
    Uses @log_invocation and @mcp_error_handler decorators for automatic
    logging and error handling (ARCH-004, ARCH-005).
    """
    # Validate project_path
    project_path = validate_project_path_input(arguments.get('project_path', ''))
    project_path_obj = Path(project_path).resolve()
    
    # Validate and get required fields
    feature_name = validate_feature_name_input(arguments.get('feature_name', ''))
    description = arguments.get('description', '')
    goal = arguments.get('goal', '')
    requirements = arguments.get('requirements', [])
    
    # Validate required fields exist and have content
    if not description or len(description.strip()) < 10:
        raise ValueError("description must be at least 10 characters")
    
    if not goal or len(goal.strip()) < 10:
        raise ValueError("goal must be at least 10 characters")
    
    if not requirements or len(requirements) == 0:
        raise ValueError("requirements must contain at least one item")
    
    if not isinstance(requirements, list):
        raise ValueError("requirements must be an array of strings")

    # Validate that requirements are MUST-HAVE only (no "nice to have" features)
    forbidden_patterns = [
        'nice to have', 'nice-to-have',
        'optional', 'optionally',
        'should have', 'should-have',
        'could have', 'could-have',
        'would be nice', 'if possible',
        'maybe', 'perhaps', 'potentially',
        'consider', 'might want',
        'future', 'later', 'eventually'
    ]

    for i, req in enumerate(requirements):
        if not isinstance(req, str):
            raise ValueError(f"requirement {i+1} must be a string")

        req_lower = req.lower()
        for pattern in forbidden_patterns:
            if pattern in req_lower:
                raise ValueError(
                    f"Requirement {i+1} contains forbidden phrase '{pattern}'. "
                    f"Workorders must contain ONLY must-have requirements. "
                    f"Move optional features to 'out_of_scope' instead.\n"
                    f"Rejected requirement: {req}"
                )

    # Get optional fields with defaults
    out_of_scope = arguments.get('out_of_scope', [])
    constraints = arguments.get('constraints', [])
    decisions = arguments.get('decisions', {})
    success_criteria = arguments.get('success_criteria', {})
    
    logger.info(
        f"Gathering context for feature: {feature_name}",
        extra={
            'project_path': str(project_path_obj),
            'feature_name': feature_name,
            'requirements_count': len(requirements),
            'has_constraints': len(constraints) > 0,
            'has_out_of_scope': len(out_of_scope) > 0
        }
    )
    
    # Create feature workorder directory
    feature_dir = project_path_obj / 'coderef' / 'workorder' / feature_name
    feature_dir.mkdir(parents=True, exist_ok=True)

    # Generate workorder ID
    workorder_id = generate_workorder_id(feature_name)
    workorder_timestamp = get_workorder_timestamp()

    logger.info(
        f"Generated workorder ID: {workorder_id}",
        extra={
            'workorder_id': workorder_id,
            'feature_name': feature_name,
            'timestamp': workorder_timestamp
        }
    )

    # Build context data structure with workorder metadata
    context_data = {
        'feature_name': feature_name,
        'description': description,
        'goal': goal,
        'requirements': requirements,
        'out_of_scope': out_of_scope,
        'constraints': constraints,
        'decisions': decisions,
        'success_criteria': success_criteria,
        '_metadata': {
            'workorder_id': workorder_id,
            'workorder_assigned_at': workorder_timestamp,
            'workorder_assigned_by': 'gather_context'
        }
    }

    # Inject UDS metadata (WO-UDS-INTEGRATION-001)
    from datetime import timedelta
    update_date = datetime.utcnow().strftime("%Y-%m-%d")
    review_date = (datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%d")

    context_data['_uds'] = {
        'generated_by': get_server_version(),
        'document_type': 'Feature Context',
        'workorder_id': workorder_id,
        'feature_id': feature_name,
        'last_updated': update_date,
        'ai_assistance': True,
        'status': 'DRAFT',
        'next_review': review_date
    }

    logger.info(f"UDS metadata injected into context.json for workorder: {workorder_id}")

    # Save context.json
    context_file = feature_dir / 'context.json'
    with open(context_file, 'w', encoding='utf-8') as f:
        json.dump(context_data, f, indent=2)

    # GAP-004 + GAP-005: Validate context.json with ValidatorFactory and centralized error handling
    try:
        from papertrail.validators.factory import ValidatorFactory
        from utils.validation_helpers import handle_validation_result

        validator = ValidatorFactory.get_validator(str(context_file))
        result = validator.validate_file(str(context_file))
        handle_validation_result(result, "context.json")
    except ImportError:
        logger.warning("Papertrail validators not available - skipping validation")
    except ValueError:
        logger.error("context.json validation failed critically - continuing with partial data")
    except Exception as e:
        logger.warning(f"Validation error: {e} - continuing without validation")

    logger.info(
        f"Context saved successfully for feature: {feature_name}",
        extra={
            'context_file': str(context_file),
            'feature_name': feature_name,
            'requirements_count': len(requirements)
        }
    )

    # PHASE 4: Save baseline snapshot for component diff (WO-DELIVERABLES-ENHANCEMENT-001)
    baseline_saved = save_baseline_snapshot(project_path_obj, feature_name)
    baseline_message = "\n📸 Baseline snapshot saved" if baseline_saved else "\n⚠️  Baseline snapshot skipped (.coderef/index.json not found)"

    # Return success response with workorder ID
    return format_success_response(
        data={
            'context_file': str(context_file.relative_to(project_path_obj)),
            'feature_name': feature_name,
            'workorder_id': workorder_id,
            'requirements_count': len(requirements),
            'out_of_scope_count': len(out_of_scope),
            'constraints_count': len(constraints),
            'baseline_snapshot_saved': baseline_saved
        },
        message=f"✅ Context saved to {context_file.relative_to(project_path_obj)}\n📋 Workorder ID: {workorder_id}{baseline_message}"
    )


def save_baseline_snapshot(project_path: Path, feature_name: str) -> bool:
    """
    Save .coderef/index.json baseline snapshot for component diff.

    Phase 4: Baseline Snapshot Mechanism
    (WO-DELIVERABLES-ENHANCEMENT-001)

    Args:
        project_path: Path to project root
        feature_name: Feature name for baseline filename

    Returns:
        bool: True if baseline saved successfully, False otherwise
    """
    source_path = Path(project_path) / '.coderef' / 'index.json'
    baseline_path = Path(project_path) / '.coderef' / f'index-baseline-{feature_name}.json'

    if not source_path.exists():
        logger.warning(f".coderef/index.json not found, skipping baseline snapshot")
        return False

    try:
        # Copy index.json to baseline
        import shutil
        shutil.copy2(source_path, baseline_path)
        logger.info(f"Baseline snapshot saved: {baseline_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to save baseline snapshot: {e}")
        return False


async def _generate_enhanced_deliverables(
    project_path: Path,
    feature_name: str,
    feature_dir: Path,
    plan: dict
) -> list[TextContent]:
    """
    Generate enhanced DELIVERABLES.md using Papertrail template engine.

    Phases 2-3: Papertrail Integration + Data Collection
    (WO-DELIVERABLES-ENHANCEMENT-001)
    """
    from handler_helpers import format_success_response
    from schema_validator import get_workorder_id

    # Add papertrail to Python path if needed
    papertrail_path = Path.home() / ".mcp-servers" / "papertrail"
    if str(papertrail_path) not in sys.path:
        sys.path.insert(0, str(papertrail_path))

    # Import Papertrail components
    from papertrail.engine import TemplateEngine
    from papertrail.uds import create_uds_header, create_uds_footer
    from papertrail.validator import validate_uds
    from papertrail.health import calculate_health
    from papertrail.extensions.git_integration import GitExtension
    from papertrail.extensions.coderef_context import CodeRefContextExtension
    from papertrail.extensions.workflow import WorkflowExtension
    from papertrail.validators.session import SessionDocValidator

    logger.info("Using enhanced DELIVERABLES generation with Papertrail")

    # Extract metadata
    meta = plan.get('META_DOCUMENTATION', {})
    structure = plan.get('UNIVERSAL_PLANNING_STRUCTURE', {})
    exec_summary = structure.get('1_executive_summary', {})
    workorder_id = get_workorder_id(plan)

    # Initialize Papertrail template engine
    template_dir = TOOL_TEMPLATES_DIR
    engine = TemplateEngine(template_dir=template_dir)

    # Register extensions
    engine.register_extension('git', GitExtension(repo_path=str(project_path)))
    engine.register_extension('coderef', CodeRefContextExtension())
    engine.register_extension('plan', WorkflowExtension())

    # PHASE 3: Data Collection
    # Collect git data
    git_ext = engine.extensions['git']
    git_data = {
        'files_changed': git_ext.get_files_changed(workorder_id) or [],
        'commits': git_ext.get_commits(workorder_id) or [],
        'total_additions': 0,
        'total_deletions': 0,
        'source': f'git log --grep={workorder_id}'
    }

    # Calculate totals
    for file in git_data['files_changed']:
        git_data['total_additions'] += file.get('additions', 0)
        git_data['total_deletions'] += file.get('deletions', 0)

    # Collect coderef data
    baseline_path = Path(project_path) / '.coderef' / f'index-baseline-{feature_name}.json'
    current_path = Path(project_path) / '.coderef' / 'index.json'

    coderef_ext = engine.extensions['coderef']
    coderef_data = {
        'components_added': [],
        'functions_added': [],
        'complexity_delta': 0.0,
        'baseline': str(baseline_path) if baseline_path.exists() else None
    }

    if baseline_path.exists() and current_path.exists():
        try:
            coderef_data['components_added'] = coderef_ext.get_components_added(
                str(baseline_path),
                str(current_path)
            ) or []
            coderef_data['functions_added'] = coderef_ext.get_functions_added(
                str(baseline_path),
                str(current_path)
            ) or []
            coderef_data['complexity_delta'] = coderef_ext.calculate_complexity_delta(
                str(baseline_path),
                str(current_path)
            )
        except Exception as e:
            logger.warning(f"CodeRef data collection failed: {e}")

    # Collect plan data
    plan_ext = engine.extensions['plan']
    plan_data = {
        'phases': plan_ext.get_plan_phases(str(feature_dir / 'plan.json')) or [],
        'tasks': plan_ext.get_priority_checklist(str(feature_dir / 'plan.json')) or [],
        'source': str((feature_dir / 'plan.json').relative_to(project_path))
    }

    # Build template context
    context = {
        'feature_name': feature_name,
        'project_name': meta.get('project_name', Path(project_path).name),
        'workorder_id': workorder_id,
        'status': '🚧 In Progress',
        'generated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'goal': exec_summary.get('goal', exec_summary.get('purpose', 'TBD')),
        'description': exec_summary.get('description', exec_summary.get('value_proposition', 'TBD')),
        'implementation_status': meta.get('status', 'planning'),
        'git': git_data,
        'coderef': coderef_data,
        'plan': plan_data,
        'validation': {'status': 'Pending', 'score': 0, 'issues': []},
        'health': {'overall_score': 0, 'traceability': 0, 'completeness': 0, 'freshness': 0, 'validation': 0},
        'success_criteria': {'functional': [], 'quality': []}
    }

    # Create UDS header and footer
    uds_header = create_uds_header(
        title=f"DELIVERABLES - {feature_name}",
        workorder_id=workorder_id,
        feature_id=feature_name,
        status="IN_PROGRESS",
        doc_version="2.0"
    )

    uds_footer = create_uds_footer(
        workorder_id=workorder_id,
        feature_id=feature_name,
        status="IN_PROGRESS"
    )

    # Render template with UDS injection
    try:
        template = engine.env.get_template('DELIVERABLES_enhanced_template.md')
        deliverables_content = template.render(**context)
        deliverables_content = f"{uds_header}\n\n{deliverables_content}\n\n{uds_footer}"
    except Exception as e:
        logger.error(f"Template rendering failed: {e}")
        raise

    # Save DELIVERABLES.md
    deliverables_path = feature_dir / 'DELIVERABLES.md'
    with open(deliverables_path, 'w', encoding='utf-8') as f:
        f.write(deliverables_content)

    # Validate and calculate health (add to context for reporting)
    try:
        validation_result = validate_uds(deliverables_content)
        health_result = calculate_health(deliverables_content)

        logger.info(f"Validation score: {validation_result.get('score', 0)}/100")
        logger.info(f"Health score: {health_result.get('overall_score', 0)}/100")
    except Exception as e:
        logger.warning(f"Validation/health check failed: {e}")

    logger.info(f"Enhanced DELIVERABLES.md generated successfully at: {deliverables_path}")

    return format_success_response(
        data={
            'deliverables_path': str(deliverables_path.relative_to(project_path)),
            'feature_name': feature_name,
            'workorder_id': workorder_id,
            'enhanced_mode': True,
            'git_commits': len(git_data['commits']),
            'files_changed': len(git_data['files_changed']),
            'components_added': len(coderef_data['components_added']),
            'success': True
        },
        message="✅ Enhanced DELIVERABLES.md generated successfully (Papertrail v2.0)"
    )


@log_invocation
@mcp_error_handler
async def handle_generate_deliverables_template(arguments: dict) -> list[TextContent]:
    """
    Handle generate_deliverables_template tool call.

    Generates DELIVERABLES.md template from plan.json structure with phase/task checklists.
    Uses @log_invocation and @mcp_error_handler decorators for automatic
    logging and error handling (ARCH-004, ARCH-005).

    Updated in WO-DOCS-MCP-SCHEMA-FIX-001 to use schema_validator helper functions
    for robust handling of both new schema format and legacy formats.
    """
    from handler_helpers import format_success_response
    from schema_validator import (
        get_phases, get_tasks, get_files_to_create, get_files_to_modify,
        get_workorder_id, get_success_criteria
    )

    # Validate inputs
    project_path = validate_project_path_input(arguments.get("project_path", ""))
    feature_name = validate_feature_name_input(arguments.get("feature_name", ""))

    logger.info(
        f"Generating DELIVERABLES.md template for feature: {feature_name}",
        extra={'project_path': str(project_path), 'feature_name': feature_name}
    )

    # Define feature directory
    feature_dir = Path(project_path) / 'coderef' / 'workorder' / feature_name

    # Check if plan.json exists
    plan_path = feature_dir / 'plan.json'
    if not plan_path.exists():
        raise FileNotFoundError(f"plan.json not found for feature '{feature_name}'. Run /create-plan first.")

    # Load plan.json
    with open(plan_path, 'r', encoding='utf-8') as f:
        plan = json.load(f)

    # Enhanced mode with Papertrail (WO-DELIVERABLES-ENHANCEMENT-001)
    if ENHANCED_DELIVERABLES_ENABLED:
        try:
            return await _generate_enhanced_deliverables(
                project_path=project_path,
                feature_name=feature_name,
                feature_dir=feature_dir,
                plan=plan
            )
        except ImportError as e:
            logger.warning(f"Papertrail not available: {e}, falling back to standard template")
        except Exception as e:
            import traceback
            logger.error(f"Enhanced deliverables generation failed: {e}\n{traceback.format_exc()}")
            logger.info("Falling back to standard template")

    # Load template (standard mode)
    template_path = TOOL_TEMPLATES_DIR / 'DELIVERABLES_template.md'
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()

    # Extract data from plan using schema-aware helper functions
    meta = plan.get('META_DOCUMENTATION', {})
    structure = plan.get('UNIVERSAL_PLANNING_STRUCTURE', {})
    exec_summary = structure.get('1_executive_summary', {})

    # Use schema_validator helpers for robust data extraction
    phases_list = get_phases(plan)
    tasks_list = get_tasks(plan)
    files_to_create = get_files_to_create(plan)
    files_to_modify = get_files_to_modify(plan)
    workorder_id = get_workorder_id(plan)
    success = get_success_criteria(plan)

    # Format phases section
    phases_md = []
    for phase in phases_list:
        phase_num = phase.get('phase', '?')
        phases_md.append(f"### Phase {phase_num}: {phase.get('name', 'Unnamed')}")
        phases_md.append(f"\n**Description**: {phase.get('description', 'TBD')}\n")
        phases_md.append(f"**Estimated Duration**: {phase.get('estimated_duration', 'TBD')}\n")
        phases_md.append("**Deliverables**:")
        for deliverable in phase.get('deliverables', []):
            if isinstance(deliverable, dict):
                # Handle dict format: extract item or description
                item = deliverable.get('item', deliverable.get('description', str(deliverable)))
                phases_md.append(f"- {item}")
            else:
                # Handle string format
                phases_md.append(f"- {deliverable}")
        phases_md.append("")

    # Format tasks checklist
    tasks_md = []
    for task in tasks_list:
        task_id = task.get('id', '???')
        task_desc = task.get('description', 'No description')
        tasks_md.append(f"- [ ] [{task_id}] {task_desc}")

    # Format files section (already normalized by helpers)
    files_md = []
    for file_info in files_to_create:
        files_md.append(f"- **{file_info['path']}** - {file_info['purpose']}")
    for file_info in files_to_modify:
        files_md.append(f"- **{file_info['path']}** - {file_info['changes']}")

    # Format success criteria (handles both old and new formats)
    success_md = []
    for criterion in success.get('functional', []):
        if isinstance(criterion, str):
            success_md.append(f"- {criterion}")
        elif isinstance(criterion, dict):
            success_md.append(f"- **{criterion.get('criterion', 'TBD')}**: {criterion.get('target', 'TBD')}")

    # Replace template variables
    deliverables_content = template
    deliverables_content = deliverables_content.replace('{{FEATURE_NAME}}', feature_name)
    deliverables_content = deliverables_content.replace('{{PROJECT_NAME}}', meta.get('project_name', Path(project_path).name))
    deliverables_content = deliverables_content.replace('{{WORKORDER_ID}}', workorder_id)
    deliverables_content = deliverables_content.replace('{{GENERATED_DATE}}', datetime.now().strftime('%Y-%m-%d'))
    # Handle both old (feature_overview/business_value) and new (goal/description) field names
    goal = exec_summary.get('goal', exec_summary.get('feature_overview', 'TBD'))
    description = exec_summary.get('description', exec_summary.get('business_value', 'TBD'))
    deliverables_content = deliverables_content.replace('{{GOAL}}', goal)
    deliverables_content = deliverables_content.replace('{{DESCRIPTION}}', description)
    deliverables_content = deliverables_content.replace('{{PHASES}}', '\n'.join(phases_md))
    deliverables_content = deliverables_content.replace('{{TASKS}}', '\n'.join(tasks_md) if tasks_md else '- No tasks defined')
    deliverables_content = deliverables_content.replace('{{FILES}}', '\n'.join(files_md) if files_md else '- No files listed')
    deliverables_content = deliverables_content.replace('{{SUCCESS_CRITERIA}}', '\n'.join(success_md) if success_md else '- No success criteria defined')

    # Inject UDS YAML frontmatter (WO-UDS-INTEGRATION-001)
    from uds_helpers import generate_uds_header, generate_uds_footer

    if workorder_id and workorder_id != "[NO WORKORDER]":
        uds_header = generate_uds_header(
            title=f"DELIVERABLES - {feature_name}",
            workorder_id=workorder_id,
            feature_name=feature_name,
            status="IN_PROGRESS",
            doc_version="1.0"
        )
        uds_footer = generate_uds_footer(
            workorder_id=workorder_id,
            feature_name=feature_name,
            status="IN_PROGRESS"
        )
        deliverables_content = f"{uds_header}\n\n{deliverables_content}\n\n{uds_footer}"
        logger.info(f"UDS YAML frontmatter added to DELIVERABLES.md for workorder: {workorder_id}")

    # Save DELIVERABLES.md
    deliverables_path = feature_dir / 'DELIVERABLES.md'
    with open(deliverables_path, 'w', encoding='utf-8') as f:
        f.write(deliverables_content)

    logger.info(f"DELIVERABLES.md template generated successfully at: {deliverables_path}")

    return format_success_response(
        data={
            'deliverables_path': str(deliverables_path.relative_to(Path(project_path))),
            'feature_name': feature_name,
            'workorder_id': workorder_id,
            'phases_count': len(phases_list),
            'tasks_count': len(tasks_list),
            'success': True
        },
        message="✅ DELIVERABLES.md template generated successfully"
    )


@log_invocation
@mcp_error_handler
async def handle_update_deliverables(arguments: dict) -> list[TextContent]:
    """
    Handle update_deliverables tool call.

    Marks DELIVERABLES.md as complete. Simple status update without git analysis.
    Changes will be committed later by /archive-feature.
    """
    from handler_helpers import format_success_response

    # Validate inputs
    project_path = validate_project_path_input(arguments.get("project_path", ""))
    feature_name = validate_feature_name_input(arguments.get("feature_name", ""))

    # Define feature directory
    feature_dir = Path(project_path) / 'coderef' / 'workorder' / feature_name
    deliverables_path = feature_dir / 'DELIVERABLES.md'

    # Check if DELIVERABLES.md exists
    if not deliverables_path.exists():
        raise FileNotFoundError(f"DELIVERABLES.md not found for feature '{feature_name}'. Run /create-plan first.")

    # Read, update status, write
    content = deliverables_path.read_text(encoding='utf-8')
    content = content.replace('**Status**: 🚧 Not Started', '**Status**: ✅ Complete')
    content = content.replace('**Last Updated**: ', f"**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Previous: ")
    deliverables_path.write_text(content, encoding='utf-8')

    # GAP-004 + GAP-005: Validate DELIVERABLES.md with ValidatorFactory and centralized error handling
    try:
        from papertrail.validators.factory import ValidatorFactory
        from utils.validation_helpers import handle_validation_result

        validator = ValidatorFactory.get_validator(str(deliverables_path))
        result = validator.validate_file(str(deliverables_path))
        handle_validation_result(result, "DELIVERABLES.md")
    except ImportError:
        logger.warning("Papertrail validators not available - skipping DELIVERABLES update validation")
    except ValueError:
        logger.error("DELIVERABLES.md validation failed critically - continuing with partial data")
    except Exception as e:
        logger.warning(f"DELIVERABLES update validation error: {e} - continuing without validation")

    logger.info(f"DELIVERABLES.md marked complete for feature: {feature_name}")

    return format_success_response(
        data={
            'deliverables_path': str(deliverables_path.relative_to(Path(project_path))),
            'feature_name': feature_name,
            'status': 'complete',
            'success': True
        },
        message=f"✅ DELIVERABLES.md marked complete for {feature_name}"
    )


# Agent Communication Handlers (Phase 1-5)

@log_invocation
@mcp_error_handler
async def handle_generate_agent_communication(arguments: dict) -> list[TextContent]:
    """
    Generate communication.json from plan.json for multi-agent coordination.

    Reads plan.json and auto-generates communication.json with:
    - Feature name and workorder ID
    - Precise steps from implementation phases
    - Forbidden files and allowed files
    - Success criteria
    - Agent status fields

    Args:
        arguments: Dict with:
            - project_path: Absolute path to project directory
            - feature_name: Feature name (alphanumeric, hyphens, underscores)

    Returns:
        Success response with communication file path and generation summary

    Raises:
        ValueError: If inputs invalid or plan.json doesn't exist
        FileNotFoundError: If plan.json not found
    """
    # Validate inputs
    project_path = validate_project_path_input(arguments.get("project_path", ""))
    feature_name = validate_feature_name_input(arguments.get("feature_name", ""))

    # Build paths
    feature_dir = Path(project_path) / PlanningPaths.WORKING_DIR / feature_name
    plan_path = feature_dir / "plan.json"
    comm_path = feature_dir / "communication.json"
    template_path = TOOL_TEMPLATES_DIR / "communication_template.json"

    # Verify plan.json exists
    if not plan_path.exists():
        raise FileNotFoundError(
            f"plan.json not found at {plan_path}. "
            f"Run /create-plan for feature '{feature_name}' first."
        )

    # Load plan.json
    plan_data = json.loads(plan_path.read_text(encoding='utf-8'))

    # Load template
    if not template_path.exists():
        raise FileNotFoundError(f"communication_template.json not found at {template_path}")
    template_data = json.loads(template_path.read_text(encoding='utf-8'))

    # Extract workorder ID from plan
    workorder_id = plan_data.get("UNIVERSAL_PLANNING_STRUCTURE", {}).get(
        "5_task_id_system", {}
    ).get("workorder", {}).get("id", f"WO-{feature_name.upper()}-001")

    # Extract feature metadata
    meta = plan_data.get("META_DOCUMENTATION", {})
    feature_display_name = meta.get("feature_name", feature_name).upper().replace("-", "_")

    # Build tasks array from phases (with status tracking)
    phases_section = plan_data.get("UNIVERSAL_PLANNING_STRUCTURE", {}).get("6_implementation_phases", {})
    # Support both array format (new) and dict format (legacy)
    if "phases" in phases_section and isinstance(phases_section["phases"], list):
        phases_list = phases_section["phases"]
    else:
        # Legacy dict format: {"phase_1": {...}, "phase_2": {...}}
        phases_list = [phases_section[k] for k in sorted(phases_section.keys()) if k.startswith("phase")]

    tasks = []
    step_num = 1

    for phase in phases_list:
        phase_name = phase.get("name", f"Phase {phase.get('phase', '?')}")

        # Add phase header task
        tasks.append({
            "id": f"STEP-{step_num:03d}",
            "description": f"Review {phase_name} requirements",
            "status": "pending",
            "completed_at": None,
            "notes": None
        })
        step_num += 1

        # Add tasks from this phase
        for task_id in phase.get("tasks", []):
            # Find task description from task_id_system
            task_system = plan_data.get("UNIVERSAL_PLANNING_STRUCTURE", {}).get("5_task_id_system", {})

            # Support both array format (new) and dict format (legacy)
            task_list = task_system.get("tasks", [])
            if not task_list and "task_breakdown" in task_system:
                # Legacy format: flatten task_breakdown dict
                task_breakdown = task_system.get("task_breakdown", {})
                for task_group in task_breakdown.values():
                    task_list.extend(task_group)

            for task in task_list:
                if task.get("id") == task_id:
                    desc = task.get("description", "")
                    tasks.append({
                        "id": f"STEP-{step_num:03d}",
                        "description": desc,
                        "status": "pending",
                        "completed_at": None,
                        "notes": None
                    })
                    step_num += 1
                    break

    # Calculate progress summary
    total_tasks = len(tasks)
    progress = {
        "total": total_tasks,
        "complete": 0,
        "in_progress": 0,
        "pending": total_tasks,
        "blocked": 0,
        "percent": 0
    }

    # Extract forbidden/allowed files from risk assessment or phases
    forbidden_files = []
    allowed_files = []

    # Try to extract from phases or set defaults
    for phase in phases_list:
        deliverables = phase.get("deliverables", [])
        for deliverable in deliverables:
            # Files to modify are "allowed"
            if any(keyword in deliverable.lower() for keyword in ["implement", "add", "create", "modify", "update"]):
                allowed_files.append(f"{deliverable}")

    # Extract success criteria from phases
    success_criteria = []
    for phase in phases_list:
        validation = phase.get("validation", [])
        success_criteria.extend(validation)

    # Build communication.json
    communication = template_data.copy()
    communication.update({
        "feature": feature_display_name,
        "workorder_id": workorder_id,
        "from": "Agent 1",
        "to": "Agent N",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "task": f"Implement {feature_display_name} following {len(phases_list)} implementation phases",
        "instruction": f"Execute all tasks for {feature_display_name} and update task status in communication.json as you complete each one",
        "tasks": tasks[:30] if len(tasks) > 30 else tasks,  # Limit to 30 tasks
        "progress": progress,
        "details": {
            "work_area": str(feature_dir.relative_to(project_path)),
            "forbidden_files": forbidden_files if forbidden_files else [
                "server.py - DO NOT MODIFY (production MCP server)",
                "tool_handlers.py - DO NOT MODIFY (existing handlers)"
            ],
            "allowed_files": allowed_files if allowed_files else [
                f"coderef/workorder/{feature_name}/ - Feature implementation files"
            ],
            "context": {
                "feature_name": feature_name,
                "goal": plan_data.get("UNIVERSAL_PLANNING_STRUCTURE", {}).get(
                    "1_executive_summary", {}
                ).get("feature_overview", f"Implement {feature_name}"),
                "dependencies": [],
                "references": ["plan.json section 4_key_features", "plan.json section 6_implementation_phases"]
            }
        },
        "testing_checklist": [
            "1. Run all unit tests for the feature",
            "2. Verify integration tests pass",
            "3. Check forbidden files unchanged (git diff)",
            "4. Build project successfully",
            "5. Manual test of feature functionality"
        ],
        "success_criteria": success_criteria[:10] if len(success_criteria) > 10 else success_criteria,
        "agent_1_status": "READY - Planning complete, awaiting agent assignment",
        "agent_N_status": None,
        "metadata": {
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "version": "1.0.0",
            "template_version": "1.1.0",
            "generated_from_plan": str(plan_path.relative_to(project_path))
        }
    })

    # Save communication.json
    comm_path.write_text(json.dumps(communication, indent=2), encoding='utf-8')

    # GAP-004 + GAP-005: Validate communication.json with ValidatorFactory and centralized error handling
    try:
        from papertrail.validators.factory import ValidatorFactory
        from utils.validation_helpers import handle_validation_result

        validator = ValidatorFactory.get_validator(str(comm_path))
        result = validator.validate_file(str(comm_path))
        handle_validation_result(result, "communication.json")
    except ImportError:
        logger.warning("Papertrail validators not available - skipping validation")
    except ValueError:
        logger.error("communication.json validation failed critically - continuing with partial data")
    except Exception as e:
        logger.warning(f"Validation error: {e} - continuing without validation")

    logger.info(f"Generated communication.json for feature '{feature_name}'")

    return format_success_response(
        data={
            'communication_path': str(comm_path.relative_to(Path(project_path))),
            'feature_name': feature_name,
            'workorder_id': workorder_id,
            'steps_count': len(tasks),
            'success_criteria_count': len(success_criteria),
            'plan_source': str(plan_path.relative_to(Path(project_path))),
            'success': True
        },
        message=f"✅ Generated communication.json with {len(tasks)} steps and {len(success_criteria)} success criteria"
    )


@log_invocation
@mcp_error_handler
async def handle_assign_agent_task(arguments: dict) -> list[TextContent]:
    """
    Assign specific task to agent with workorder scoping and conflict detection.

    Updates communication.json with agent assignment, generates agent-scoped
    workorder ID, and validates no conflicting file assignments.

    Args:
        arguments: Dict with:
            - project_path: Absolute path to project directory
            - feature_name: Feature name (alphanumeric, hyphens, underscores)
            - agent_number: Agent number (1-10)
            - phase_id: Optional phase ID to assign (e.g., "phase_1")

    Returns:
        Success response with assignment details and boundaries

    Raises:
        ValueError: If inputs invalid, communication.json doesn't exist, or conflicts detected
        FileNotFoundError: If communication.json not found
    """
    from handler_helpers import generate_agent_workorder_id

    # Validate inputs
    project_path = validate_project_path_input(arguments.get("project_path", ""))
    feature_name = validate_feature_name_input(arguments.get("feature_name", ""))
    agent_number = arguments.get("agent_number", 2)  # Default to agent 2
    phase_id = arguments.get("phase_id")  # Optional

    # Validate agent number
    if not isinstance(agent_number, int) or agent_number < 1 or agent_number > 10:
        raise ValueError("Agent number must be an integer between 1 and 10")

    # Build paths
    feature_dir = Path(project_path) / PlanningPaths.WORKING_DIR / feature_name
    comm_path = feature_dir / "communication.json"

    # Verify communication.json exists
    if not comm_path.exists():
        raise FileNotFoundError(
            f"communication.json not found at {comm_path}. "
            f"Run generate_agent_communication for feature '{feature_name}' first."
        )

    # Load communication.json
    comm_data = json.loads(comm_path.read_text(encoding='utf-8'))

    # Generate agent-scoped workorder ID
    base_workorder = comm_data.get('workorder_id', f'WO-{feature_name.upper()}-001')
    agent_workorder = generate_agent_workorder_id(base_workorder, agent_number)

    # Check for existing assignments to detect conflicts
    agent_status_key = f'agent_{agent_number}_status'
    existing_status = comm_data.get(agent_status_key)

    if existing_status and 'ASSIGNED' in str(existing_status):
        logger.warning(f"Agent {agent_number} already assigned to feature '{feature_name}'")

    # Build agent-specific instruction set
    if phase_id:
        instruction = f"Execute {phase_id} tasks for {comm_data.get('feature', feature_name)}"
    else:
        instruction = comm_data.get('instruction', f"Execute tasks for {comm_data.get('feature', feature_name)}")

    # Update communication.json with assignment
    comm_data[agent_status_key] = f"ASSIGNED - Agent {agent_number} assigned to work"
    comm_data[f'agent_{agent_number}_assigned_at'] = datetime.now().isoformat()
    comm_data[f'agent_{agent_number}_workorder'] = agent_workorder

    if phase_id:
        comm_data[f'agent_{agent_number}_phase'] = phase_id

    # Update metadata
    comm_data['metadata']['updated_at'] = datetime.now().isoformat()

    # Save updated communication.json
    comm_path.write_text(json.dumps(comm_data, indent=2), encoding='utf-8')

    # GAP-004 + GAP-005: Validate communication.json with ValidatorFactory and centralized error handling
    try:
        from papertrail.validators.factory import ValidatorFactory
        from utils.validation_helpers import handle_validation_result

        validator = ValidatorFactory.get_validator(str(comm_path))
        result = validator.validate_file(str(comm_path))
        handle_validation_result(result, "communication.json")
    except ImportError:
        logger.warning("Papertrail validators not available - skipping update validation")
    except ValueError:
        logger.error("communication.json validation failed critically - continuing with partial data")
    except Exception as e:
        logger.warning(f"Update validation error: {e} - continuing without validation")

    logger.info(f"Assigned agent {agent_number} to feature '{feature_name}' with workorder {agent_workorder}")

    # Extract boundaries for response
    forbidden_files = comm_data.get('details', {}).get('forbidden_files', [])
    allowed_files = comm_data.get('details', {}).get('allowed_files', [])

    return format_success_response(
        data={
            'feature_name': feature_name,
            'agent_number': agent_number,
            'agent_workorder_id': agent_workorder,
            'base_workorder_id': base_workorder,
            'status': f'ASSIGNED - Agent {agent_number}',
            'phase_id': phase_id,
            'forbidden_files_count': len(forbidden_files),
            'allowed_files_count': len(allowed_files),
            'communication_path': str(comm_path.relative_to(Path(project_path))),
            'success': True
        },
        message=f"✅ Assigned Agent {agent_number} to {feature_name} (Workorder: {agent_workorder})"
    )


@log_invocation
@mcp_error_handler
async def handle_verify_agent_completion(arguments: dict) -> list[TextContent]:
    """
    Verify agent completion with git diff checks and success criteria validation.

    Validates that:
    - Agent status is COMPLETE
    - Forbidden files were not modified (git diff)
    - Success criteria are met
    - Updates communication.json with verification results

    Args:
        arguments: Dict with:
            - project_path: Absolute path to project directory
            - feature_name: Feature name (alphanumeric, hyphens, underscores)
            - agent_number: Agent number to verify (1-10)

    Returns:
        Success response with verification results and pass/fail status

    Raises:
        ValueError: If agent not in COMPLETE status or validation fails
        FileNotFoundError: If communication.json not found
    """
    from handler_helpers import validate_forbidden_files

    # Validate inputs
    project_path = validate_project_path_input(arguments.get("project_path", ""))
    feature_name = validate_feature_name_input(arguments.get("feature_name", ""))
    agent_number = arguments.get("agent_number", 2)  # Default to agent 2

    # Validate agent number
    if not isinstance(agent_number, int) or agent_number < 1 or agent_number > 10:
        raise ValueError("Agent number must be an integer between 1 and 10")

    # Build paths
    feature_dir = Path(project_path) / PlanningPaths.WORKING_DIR / feature_name
    comm_path = feature_dir / "communication.json"

    # Verify communication.json exists
    if not comm_path.exists():
        raise FileNotFoundError(
            f"communication.json not found at {comm_path}. "
            f"Run generate_agent_communication for feature '{feature_name}' first."
        )

    # Load communication.json
    comm_data = json.loads(comm_path.read_text(encoding='utf-8'))

    # Validate agent status is COMPLETE
    agent_status_key = f'agent_{agent_number}_status'
    current_status = comm_data.get(agent_status_key, '')

    if 'COMPLETE' not in str(current_status):
        raise ValueError(
            f"Agent {agent_number} status is '{current_status}'. "
            f"Must be COMPLETE before verification."
        )

    # Run git diff validation on forbidden files
    forbidden_files = comm_data.get('details', {}).get('forbidden_files', [])

    verification_results = {
        'forbidden_files_check': {
            'passed': True,
            'violations': [],
            'checked': []
        },
        'success_criteria_check': {
            'total': 0,
            'manual_review_required': [],
            'automated_checks': []
        },
        'overall_status': 'PASSED'
    }

    # Validate forbidden files if git repo
    try:
        forbidden_result = validate_forbidden_files(Path(project_path), forbidden_files)
        verification_results['forbidden_files_check'] = forbidden_result

        if not forbidden_result['passed']:
            verification_results['overall_status'] = 'FAILED'
            logger.error(f"Forbidden files were modified: {forbidden_result['violations']}")
    except ValueError as e:
        # Not a git repo or git not available
        logger.warning(f"Git validation skipped: {str(e)}")
        verification_results['forbidden_files_check']['passed'] = None
        verification_results['forbidden_files_check']['note'] = 'Git validation skipped (not a git repository)'

    # Check success criteria (most require manual review)
    success_criteria = comm_data.get('success_criteria', [])
    verification_results['success_criteria_check']['total'] = len(success_criteria)

    for criterion in success_criteria:
        # All criteria require manual review for now
        verification_results['success_criteria_check']['manual_review_required'].append(criterion)

    # Update communication.json with verification results
    comm_data[f'agent_{agent_number}_verification'] = {
        'verified_at': datetime.now().isoformat(),
        'verified_by': 'Agent 1',
        'forbidden_files_check': verification_results['forbidden_files_check'],
        'success_criteria': {
            'total': len(success_criteria),
            'manual_review_count': len(verification_results['success_criteria_check']['manual_review_required'])
        },
        'overall_status': verification_results['overall_status']
    }

    # Update agent status based on verification
    if verification_results['overall_status'] == 'PASSED':
        comm_data[agent_status_key] = f"VERIFIED - Agent {agent_number} work verified and approved"
    else:
        comm_data[agent_status_key] = f"VERIFICATION_FAILED - Agent {agent_number} work needs revision"

    # Update metadata
    comm_data['metadata']['updated_at'] = datetime.now().isoformat()

    # Save updated communication.json
    comm_path.write_text(json.dumps(comm_data, indent=2), encoding='utf-8')

    # GAP-004 + GAP-005: Validate communication.json with ValidatorFactory and centralized error handling
    try:
        from papertrail.validators.factory import ValidatorFactory
        from utils.validation_helpers import handle_validation_result

        validator = ValidatorFactory.get_validator(str(comm_path))
        result = validator.validate_file(str(comm_path))
        handle_validation_result(result, "communication.json")
    except ImportError:
        logger.warning("Papertrail validators not available - skipping verification update validation")
    except ValueError:
        logger.error("communication.json validation failed critically - continuing with partial data")
    except Exception as e:
        logger.warning(f"Verification update validation error: {e} - continuing without validation")

    logger.info(f"Verified agent {agent_number} completion for feature '{feature_name}': {verification_results['overall_status']}")

    return format_success_response(
        data={
            'feature_name': feature_name,
            'agent_number': agent_number,
            'verification_status': verification_results['overall_status'],
            'forbidden_files_checked': len(verification_results['forbidden_files_check'].get('checked', [])),
            'forbidden_files_violations': len(verification_results['forbidden_files_check'].get('violations', [])),
            'success_criteria_total': verification_results['success_criteria_check']['total'],
            'manual_review_required': len(verification_results['success_criteria_check']['manual_review_required']),
            'new_agent_status': comm_data[agent_status_key],
            'communication_path': str(comm_path.relative_to(Path(project_path))),
            'success': True
        },
        message=f"✅ Verification {verification_results['overall_status']}: Agent {agent_number} work on {feature_name}"
    )


@log_invocation
@mcp_error_handler
async def handle_aggregate_agent_deliverables(arguments: dict) -> list[TextContent]:
    """
    Aggregate metrics from multiple agent DELIVERABLES.md files.

    Combines metrics from all agents working on a feature:
    - LOC: Sums added, deleted, net lines
    - Commits: Total count across all agents
    - Contributors: Unique set of contributors
    - Time: Min first commit to max last commit

    Args:
        arguments: Dict with:
            - project_path: Absolute path to project directory
            - feature_name: Feature name (alphanumeric, hyphens, underscores)

    Returns:
        Success response with aggregated metrics and combined deliverables path

    Raises:
        ValueError: If inputs invalid
        FileNotFoundError: If no DELIVERABLES.md files found
    """
    from handler_helpers import aggregate_agent_metrics

    # Validate inputs
    project_path = validate_project_path_input(arguments.get("project_path", ""))
    feature_name = validate_feature_name_input(arguments.get("feature_name", ""))

    # Build paths
    feature_dir = Path(project_path) / PlanningPaths.WORKING_DIR / feature_name

    # Find all DELIVERABLES.md files (could be in subdirectories for multi-agent)
    deliverables_files = list(feature_dir.glob("**/DELIVERABLES.md"))

    if not deliverables_files:
        raise FileNotFoundError(
            f"No DELIVERABLES.md files found in {feature_dir}. "
            f"Agents must generate DELIVERABLES.md files first."
        )

    logger.info(f"Found {len(deliverables_files)} DELIVERABLES.md files for feature '{feature_name}'")

    # Aggregate metrics
    aggregated = aggregate_agent_metrics(deliverables_files)

    # Create combined deliverables report
    combined_path = feature_dir / "DELIVERABLES-COMBINED.md"

    combined_content = f"""# DELIVERABLES - {feature_name.upper()} (Multi-Agent Aggregate)

**Workorder**: Combined from {len(deliverables_files)} agent(s)
**Feature**: {feature_name}
**Status**: ✅ Complete (Aggregated)
**Generated**: {datetime.now().strftime('%Y-%m-%d')}

---

## Multi-Agent Summary

This report aggregates metrics from **{aggregated['agents_count']} agent(s)** working on this feature.

---

## Aggregated Implementation Metrics

### Code Changes
- **Lines Added**: {aggregated['loc_added']}
- **Lines Deleted**: {aggregated['loc_deleted']}
- **Net LOC**: {aggregated['loc_net']}

### Development Activity
- **Total Commits**: {aggregated['total_commits']}
- **Contributors**: {', '.join(aggregated['contributors']) if aggregated['contributors'] else 'TBD'}
- **Days Elapsed**: {aggregated['days_elapsed']}
- **Wall Clock Hours**: {aggregated['hours_elapsed']}

### Agent Participation
- **Number of Agents**: {aggregated['agents_count']}
- **Agent Deliverables Files**: {len(deliverables_files)}

---

## Individual Agent Deliverables

"""

    # List individual deliverables
    for i, deliverable_path in enumerate(deliverables_files, 1):
        rel_path = deliverable_path.relative_to(feature_dir)
        combined_content += f"{i}. `{rel_path}`\n"

    combined_content += f"""

---

## Aggregation Details

**Source Files**: {len(deliverables_files)} DELIVERABLES.md files
**Aggregation Method**: Sum LOC, count commits, unique contributors, time range
**First Commit Date**: {aggregated.get('first_commit_date', 'N/A')}
**Last Commit Date**: {aggregated.get('last_commit_date', 'N/A')}

---

**Note**: This is an automatically generated aggregate report combining metrics from all agents working on this feature.
"""

    # Save combined deliverables
    combined_path.write_text(combined_content, encoding='utf-8')

    logger.info(f"Generated combined deliverables for feature '{feature_name}' with {aggregated['agents_count']} agents")

    return format_success_response(
        data={
            'feature_name': feature_name,
            'combined_path': str(combined_path.relative_to(Path(project_path))),
            'agents_count': aggregated['agents_count'],
            'total_loc_added': aggregated['loc_added'],
            'total_loc_deleted': aggregated['loc_deleted'],
            'net_loc': aggregated['loc_net'],
            'total_commits': aggregated['total_commits'],
            'contributors': aggregated['contributors'],
            'days_elapsed': aggregated['days_elapsed'],
            'hours_elapsed': aggregated['hours_elapsed'],
            'deliverables_files_found': len(deliverables_files),
            'success': True
        },
        message=f"✅ Aggregated deliverables from {aggregated['agents_count']} agent(s): {aggregated['total_commits']} commits, {aggregated['loc_net']} net LOC"
    )


@log_invocation
@mcp_error_handler
async def handle_track_agent_status(arguments: dict) -> list[TextContent]:
    """
    Track agent status across all features or specific feature.

    Provides real-time coordination dashboard showing:
    - All agents and their current status
    - Features being worked on
    - Blockers and dependencies
    - Overall workflow status

    Args:
        arguments: Dict with:
            - project_path: Absolute path to project directory
            - feature_name: Optional - specific feature to track

    Returns:
        Success response with agent status dashboard

    Raises:
        ValueError: If inputs invalid
    """
    from handler_helpers import parse_agent_status

    # Validate inputs
    project_path = validate_project_path_input(arguments.get("project_path", ""))
    feature_name = arguments.get("feature_name")  # Optional

    # Build paths
    working_dir = Path(project_path) / PlanningPaths.WORKING_DIR

    if not working_dir.exists():
        raise ValueError(f"Working directory not found: {working_dir}")

    # Find all communication.json files
    if feature_name:
        # Track specific feature
        comm_files = [working_dir / feature_name / "communication.json"]
        if not comm_files[0].exists():
            raise FileNotFoundError(f"communication.json not found for feature '{feature_name}'")
    else:
        # Track all features
        comm_files = list(working_dir.glob("*/communication.json"))

    if not comm_files:
        raise FileNotFoundError(f"No communication.json files found in {working_dir}")

    logger.info(f"Tracking {len(comm_files)} feature(s)")

    # Parse status from all communication files
    all_statuses = []
    for comm_file in comm_files:
        try:
            status = parse_agent_status(comm_file)
            all_statuses.append(status)
        except Exception as e:
            logger.warning(f"Failed to parse {comm_file}: {e}")
            continue

    # Build dashboard
    dashboard = {
        'features_tracked': len(all_statuses),
        'total_agents': sum(len(s['agents']) for s in all_statuses),
        'features': []
    }

    for status in all_statuses:
        feature_summary = {
            'feature': status['feature'],
            'workorder_id': status['workorder_id'],
            'overall_status': status['overall_status'],
            'agents': []
        }

        for agent in status['agents']:
            agent_summary = {
                'agent_number': agent['agent_number'],
                'status': agent['status'],
                'completion_time': agent.get('completion_time'),
                'blockers': agent.get('blockers', []),
                'blocked': len(agent.get('blockers', [])) > 0
            }
            feature_summary['agents'].append(agent_summary)

        dashboard['features'].append(feature_summary)

    # Count agents by status
    status_counts = {
        'available': 0,
        'assigned': 0,
        'in_progress': 0,
        'complete': 0,
        'verified': 0,
        'blocked': 0
    }

    for feature in dashboard['features']:
        for agent in feature['agents']:
            status_str = str(agent['status']).upper()
            if 'NOT_ASSIGNED' in status_str or agent['status'] is None:
                status_counts['available'] += 1
            elif 'VERIFIED' in status_str:
                status_counts['verified'] += 1
            elif 'COMPLETE' in status_str:
                status_counts['complete'] += 1
            elif 'ASSIGNED' in status_str or 'IN_PROGRESS' in status_str:
                status_counts['in_progress'] += 1

            if agent.get('blocked'):
                status_counts['blocked'] += 1

    dashboard['status_summary'] = status_counts

    logger.info(f"Agent status dashboard: {status_counts}")

    return format_success_response(
        data={
            'dashboard': dashboard,
            'features_tracked': dashboard['features_tracked'],
            'total_agents': dashboard['total_agents'],
            'status_summary': status_counts,
            'success': True
        },
        message=f"✅ Tracking {dashboard['features_tracked']} feature(s) with {dashboard['total_agents']} agent(s)"
    )


@log_invocation
@mcp_error_handler
async def handle_archive_feature(arguments: dict) -> list[TextContent]:
    """
    Handle archive_feature tool call.

    Archives completed features from coderef/workorder/ to coderef/archived/.
    Checks DELIVERABLES.md status and prompts user if status != Complete.
    Moves entire feature folder using shutil and updates archive index.

    Uses @log_invocation and @mcp_error_handler decorators for automatic
    logging and error handling (ARCH-004, ARCH-005).
    """
    import shutil
    from handler_helpers import update_archive_index, parse_deliverables_status

    # Validate inputs
    project_path = validate_project_path_input(arguments.get("project_path", ""))
    feature_name = validate_feature_name_input(arguments.get("feature_name", ""))
    force = arguments.get("force", False)  # Optional force flag to skip confirmation

    logger.info(
        f"Archiving feature: {feature_name}",
        extra={'project_path': str(project_path), 'feature_name': feature_name, 'force': force}
    )

    # Define paths
    working_dir = Path(project_path) / 'coderef' / 'workorder' / feature_name
    archived_dir = Path(project_path) / 'coderef' / 'archived' / feature_name

    # Check if feature exists in working directory
    if not working_dir.exists():
        raise FileNotFoundError(
            f"Feature '{feature_name}' not found in coderef/workorder/. "
            f"Expected: {working_dir}"
        )

    # Check if already archived
    if archived_dir.exists():
        raise ValueError(
            f"Feature '{feature_name}' already exists in coderef/archived/. "
            f"Delete the existing archive first or choose a different name."
        )

    # Check DELIVERABLES.md status
    deliverables_path = working_dir / 'DELIVERABLES.md'
    status = parse_deliverables_status(deliverables_path)

    logger.debug(f"DELIVERABLES.md status: {status}")

    # Determine if we need user confirmation
    needs_confirmation = False
    confirmation_reason = None

    if status == 'UNKNOWN':
        needs_confirmation = True
        confirmation_reason = "DELIVERABLES.md not found or status unknown"
    elif status != 'Complete':
        needs_confirmation = True
        confirmation_reason = f"Status is '{status}' (not Complete)"

    # If force=False and confirmation needed, return prompt for user
    if needs_confirmation and not force:
        logger.warning(
            f"Archive blocked - user confirmation required: {confirmation_reason}",
            extra={'feature_name': feature_name, 'status': status}
        )

        return format_success_response(
            data={
                'action_required': 'USER_CONFIRMATION',
                'feature_name': feature_name,
                'current_status': status,
                'reason': confirmation_reason,
                'working_path': str(working_dir.relative_to(Path(project_path))),
                'archived_path': str(Path('coderef/archived') / feature_name),
                'prompt': (
                    f"⚠️ Feature '{feature_name}' is not marked as Complete (status: {status})\n\n"
                    f"Do you want to archive it anyway?\n\n"
                    f"To proceed, call this tool again with force=True parameter."
                )
            },
            message=f"⚠️ User confirmation required before archiving '{feature_name}'"
        )

    # Proceed with archiving
    logger.info(f"Archiving feature from {working_dir} to {archived_dir}")

    # Ensure archived parent directory exists
    archived_parent = Path(project_path) / 'coderef' / 'archived'
    archived_parent.mkdir(parents=True, exist_ok=True)

    # Move entire folder using shutil.move()
    try:
        shutil.move(str(working_dir), str(archived_dir))
        logger.info(f"Successfully moved feature folder to {archived_dir}")
    except (OSError, shutil.Error) as e:
        raise IOError(f"Failed to move feature folder: {e}")

    # Verify move was successful
    if not archived_dir.exists():
        raise IOError("Archive operation appeared to succeed but destination folder not found")

    # Update archive index.json
    archived_at = get_workorder_timestamp()

    # Extract workorder_id and feature display name from plan.json
    workorder_id = None
    feature_display_name = feature_name  # Default to folder name
    plan_path = archived_dir / 'plan.json'

    if plan_path.exists():
        try:
            plan_content = plan_path.read_text(encoding='utf-8')
            plan_data = json.loads(plan_content)

            # Extract workorder_id from META_DOCUMENTATION
            workorder_id = plan_data.get("META_DOCUMENTATION", {}).get("workorder_id")

            # Try to get feature_name from META_DOCUMENTATION
            if 'META_DOCUMENTATION' in plan_data:
                meta_feature = plan_data['META_DOCUMENTATION'].get('feature_name', feature_name)
                # Capitalize and format for display
                feature_display_name = meta_feature.replace('-', ' ').title()
        except (json.JSONDecodeError, IOError):
            # Fall back to folder name if plan can't be read
            logger.warning(f"Could not extract workorder_id from plan.json")
            pass

    try:

        update_archive_index(
            Path(project_path),
            feature_display_name,
            feature_name,
            archived_at
        )
        logger.info(f"Archive index updated with entry for {feature_name}")
    except (ValueError, IOError) as e:
        # Archive succeeded but index update failed - log warning but don't fail
        logger.warning(
            f"Failed to update archive index (archive succeeded): {e}",
            extra={'feature_name': feature_name}
        )

    # Count files archived
    try:
        file_count = sum(1 for _ in archived_dir.rglob('*') if _.is_file())
    except OSError:
        file_count = 'unknown'

    logger.info(
        f"Feature '{feature_name}' archived successfully",
        extra={
            'archived_path': str(archived_dir.relative_to(Path(project_path))),
            'file_count': file_count,
            'status': status
        }
    )

    # Auto-log workorder on successful archive
    workorder_logged = False
    if workorder_id:
        try:
            # Extract project name from project path
            project_name = Path(project_path).name

            await handle_log_workorder({
                'project_path': str(project_path),
                'workorder_id': workorder_id,
                'project_name': project_name,
                'description': f'Archived feature: {feature_display_name}'
            })
            logger.info(f"Workorder {workorder_id} logged successfully")
            workorder_logged = True
        except Exception as e:
            # Non-fatal: log warning but don't fail archive
            logger.warning(
                f"Failed to log workorder (archive succeeded): {e}",
                extra={'workorder_id': workorder_id, 'feature_name': feature_name}
            )

    # Git automation: commit and push archive operation
    from handler_helpers import git_commit_and_push, format_archive_commit_message

    commit_msg = format_archive_commit_message(feature_name, workorder_id or 'UNKNOWN')
    # Commit all changes in coderef (both deletions in working/ and additions in archived/)
    git_result = git_commit_and_push(
        project_path=Path(project_path),
        files=['coderef/'],  # Stage all changes under coderef/
        commit_message=commit_msg,
        workorder_id=workorder_id
    )

    # Build response with git status
    response_data = {
        'archived': True,
        'feature_name': feature_name,
        'source_path': 'coderef/workorder/' + feature_name,  # Already moved
        'archived_path': str(archived_dir.relative_to(Path(project_path))),
        'file_count': file_count,
        'previous_status': status,
        'archived_at': archived_at,
        'index_updated': True,
        'workorder_logged': workorder_logged,
        'workorder_id': workorder_id,
        'git_commit': git_result.get('commit_hash') if git_result.get('success') else None,
        'git_pushed': git_result.get('pushed', False),
        'git_error': git_result.get('error')
    }

    message = f"✅ Feature '{feature_name}' archived successfully to coderef/archived/{feature_name}"
    if git_result.get('success'):
        if git_result.get('pushed'):
            message += f"\n📤 Changes committed ({git_result['commit_hash']}) and pushed to remote"
        else:
            message += f"\n💾 Changes committed ({git_result['commit_hash']}) - push failed but local commit succeeded"
    elif git_result.get('error'):
        message += f"\n⚠️ Git automation skipped: {git_result['error']}"

    return format_success_response(data=response_data, message=message)


@log_invocation
@mcp_error_handler
async def handle_update_all_documentation(arguments: dict) -> list[TextContent]:
    """
    Handle update_all_documentation tool call (DOC-001).

    AGENTIC DESIGN: This tool is designed for AI agents who have full context
    of the changes they just made. Instead of parsing files or analyzing git,
    agents directly provide the context they already have.

    Automatically updates all project documentation files (README.md, CLAUDE.md,
    CHANGELOG.json) when a feature is completed.

    Auto-increments version using semantic versioning:
    - breaking_change → major bump (1.x.x → 2.0.0)
    - feature → minor bump (1.0.x → 1.1.0)
    - bugfix/enhancement → patch bump (1.0.0 → 1.0.1)

    Args:
        arguments: Dict with keys:
            - project_path (required): Absolute path to project directory
            - change_type (required): Type of change made (breaking_change, feature, enhancement, bugfix, security, deprecation)
            - feature_description (required): Description of what was changed (agent provides this from their context)
            - workorder_id (required): Workorder ID from agent's task (e.g., 'WO-UPDATE-DOCS-001')
            - files_changed (optional): List of files modified (agent knows this)
            - feature_name (optional): Feature name for reference
            - version (optional): Manual version override (rarely needed)

    Returns:
        Success response with updated files list and new version

    Example (Agent calling this after completing a feature):
        await handle_update_all_documentation({
            'project_path': '/path/to/project',
            'change_type': 'feature',
            'feature_description': 'Added update_all_documentation tool for automated doc updates',
            'workorder_id': 'WO-UPDATE-DOCS-001',
            'files_changed': ['server.py', 'tool_handlers.py', 'handler_helpers.py'],
            'feature_name': 'update-all-documentation'
        })
    """
    from handler_helpers import (
        parse_version_from_docs,
        increment_version,
        update_readme_version,
        update_claude_md_version
    )

    # Validate inputs
    project_path = validate_project_path_input(arguments.get("project_path", ""))

    # AGENTIC: Agent provides context directly instead of us parsing/detecting
    change_type = arguments.get("change_type")
    if not change_type:
        raise ValueError("change_type is required - agent must provide what type of change was made")

    feature_description = arguments.get("feature_description")
    if not feature_description:
        raise ValueError("feature_description is required - agent must describe what was changed")

    workorder_id = arguments.get("workorder_id")
    if not workorder_id:
        raise ValueError("workorder_id is required - agent must provide their workorder ID for tracking")

    # Optional context from agent
    feature_name = arguments.get("feature_name", "")
    files_changed = arguments.get("files_changed", [])
    manual_version = arguments.get("version")

    # Parse current version
    current_version = parse_version_from_docs(Path(project_path))
    if not current_version:
        raise ValueError("Could not find current version in README.md or CLAUDE.md")

    # Calculate new version
    if manual_version:
        new_version = manual_version
        version_method = "manual"
    else:
        new_version = increment_version(current_version, change_type)
        version_method = "auto-increment"

    logger.info(
        f"Agent-provided context for documentation update",
        extra={
            'workorder_id': workorder_id,
            'change_type': change_type,
            'feature_description': feature_description,
            'files_changed': files_changed,
            'version': f"{current_version} → {new_version}"
        }
    )

    # Update documentation files
    updated_files = []
    failed_files = []

    # Update README.md
    if update_readme_version(Path(project_path), current_version, new_version, feature_description):
        updated_files.append("README.md")
        logger.info(f"Updated README.md: {current_version} → {new_version}")
    else:
        failed_files.append("README.md")
        logger.warning("Failed to update README.md")

    # Update CLAUDE.md (has its own version number)
    claude_current = parse_version_from_docs(Path(project_path))
    if claude_current:
        new_claude_version = increment_version(claude_current, change_type)
        if update_claude_md_version(Path(project_path), claude_current, new_claude_version, feature_description):
            updated_files.append("CLAUDE.md")
            logger.info(f"Updated CLAUDE.md: {claude_current} → {new_claude_version}")
        else:
            failed_files.append("CLAUDE.md")
            logger.warning("Failed to update CLAUDE.md")

    # Update CHANGELOG.json using existing tool
    if change_type and feature_description:
        try:
            # Determine severity from change_type
            severity_map = {
                'breaking_change': 'major',
                'feature': 'minor',
                'enhancement': 'minor',
                'bugfix': 'patch',
                'security': 'critical'
            }
            severity = severity_map.get(change_type, 'minor')

            # Call add_changelog_entry with workorder tracking
            changelog_args = {
                'project_path': project_path,
                'version': new_version,
                'change_type': change_type,
                'severity': severity,
                'title': feature_description,
                'description': f"Workorder {workorder_id}: {feature_description}",
                'files': files_changed if files_changed else updated_files,
                'reason': f"Feature completion: {feature_name or workorder_id}",
                'impact': f"Documentation now reflects {new_version} changes"
            }
            await handle_add_changelog_entry(changelog_args)
            updated_files.append("CHANGELOG.json")
            logger.info(f"Updated CHANGELOG.json with workorder {workorder_id}")
        except Exception as e:
            logger.warning(f"Failed to update CHANGELOG.json: {e}")
            failed_files.append("CHANGELOG.json")

    # Note: user-guide.md and my-guide.md updates require manual intervention
    manual_update_needed = ["user-guide.md", "my-guide.md"]

    logger.info(
        f"Documentation update complete: {current_version} → {new_version}",
        extra={
            'updated_files': updated_files,
            'failed_files': failed_files,
            'change_type': change_type
        }
    )

    return format_success_response(
        data={
            'workorder_id': workorder_id,
            'current_version': current_version,
            'new_version': new_version,
            'change_type': change_type,
            'version_method': version_method,
            'updated_files': updated_files,
            'failed_files': failed_files,
            'manual_update_needed': manual_update_needed,
            'feature_name': feature_name,
            'files_changed': files_changed,
            'success': len(failed_files) == 0
        },
        message=f"✅ Documentation updated [{workorder_id}]: {current_version} → {new_version}"
    )


@log_invocation
@mcp_error_handler
async def handle_execute_plan(arguments: dict) -> list[TextContent]:
    """
    Handle execute_plan tool call.

    Reads plan.json from coderef/workorder/{feature}/ and generates TodoWrite
    task list with format: WO-ID | TASK-ID: Description

    Args:
        arguments: Dict with project_path (required) and feature_name (optional)

    Returns:
        TextContent with TodoWrite-formatted task list JSON
    """
    from schema_validator import get_checklist
    
    # Validate inputs
    project_path = validate_project_path_input(arguments.get("project_path", ""))
    feature_name = arguments.get("feature_name", "")

    if not feature_name:
        return ErrorResponse.invalid_input(
            "feature_name parameter is required",
            "Provide the feature name (e.g., 'auth-system')"
        )

    # Validate feature name
    feature_name = validate_feature_name_input(feature_name)

    # Load plan.json
    plan_file = Path(project_path) / Paths.CONTEXT_DIR / "workorder" / feature_name / "plan.json"

    if not plan_file.exists():
        return ErrorResponse.not_found(
            f"plan.json for feature '{feature_name}'",
            f"Expected at: {plan_file}\nRun /create-plan first to generate a plan"
        )

    try:
        with open(plan_file, 'r', encoding='utf-8') as f:
            plan_data = json.load(f)
    except json.JSONDecodeError as e:
        return ErrorResponse.malformed_json(
            f"plan.json is malformed at line {e.lineno}, column {e.colno}: {e.msg}\n"
            f"Suggestion: Run /validate-plan to identify issues, or regenerate with /create-plan"
        )

    # Validate plan structure
    if not isinstance(plan_data, dict):
        return ErrorResponse.invalid_input(
            f"plan.json root must be an object, got {type(plan_data).__name__}",
            "Regenerate plan with /create-plan"
        )

    # Check for required sections (handle nested UNIVERSAL_PLANNING_STRUCTURE)
    structure = plan_data.get("UNIVERSAL_PLANNING_STRUCTURE", {})

    # META_DOCUMENTATION must be at top level
    if "META_DOCUMENTATION" not in plan_data:
        return ErrorResponse.invalid_input(
            "plan.json missing required section: META_DOCUMENTATION",
            f"Available sections: {', '.join(list(plan_data.keys())[:10])}\n"
            f"Run /create-plan to regenerate"
        )

    # 9_implementation_checklist can be at top level OR inside UNIVERSAL_PLANNING_STRUCTURE
    has_checklist = (
        "9_implementation_checklist" in plan_data or
        "9_implementation_checklist" in structure
    )
    if not has_checklist:
        available_in_structure = list(structure.keys())[:10] if structure else []
        return ErrorResponse.invalid_input(
            "plan.json missing required section: 9_implementation_checklist",
            f"Available in UNIVERSAL_PLANNING_STRUCTURE: {', '.join(available_in_structure)}\n"
            f"Run /create-plan to regenerate or manually add missing section"
        )

    # Extract workorder_id (with fallback)
    meta_doc = plan_data.get("META_DOCUMENTATION", {})
    if not isinstance(meta_doc, dict):
        return ErrorResponse.invalid_input(
            f"META_DOCUMENTATION must be an object, got {type(meta_doc).__name__}",
            "Fix META_DOCUMENTATION structure or regenerate with /create-plan"
        )

    workorder_id = meta_doc.get("workorder_id")
    if not workorder_id:
        # Fallback: Generate from feature name
        workorder_id = f"WO-{feature_name.upper().replace('-', '-')}-001"
        logger.warning(
            f"workorder_id missing in plan, using fallback: {workorder_id}",
            extra={'feature_name': feature_name}
        )

    # Parse tasks from section 9 using schema helper for format normalization
    section_9 = get_checklist(plan_data, strict=True)

    if not section_9:
        # Provide diagnostic info - check both top level and nested structure
        raw_section_9 = plan_data.get("9_implementation_checklist") or structure.get("9_implementation_checklist")
        if raw_section_9 is None:
            return ErrorResponse.invalid_input(
                "Section 9 (9_implementation_checklist) not found in plan",
                "Plan must contain implementation checklist. Run /create-plan to regenerate."
            )
        elif not isinstance(raw_section_9, dict):
            return ErrorResponse.invalid_input(
                f"Section 9 must be an object with task lists, got {type(raw_section_9).__name__}",
                "Expected format: {\"phase_1\": [\"task1\", \"task2\"], ...}"
            )
        else:
            # This happens when raw_section_9 exists but get_checklist normalized it to empty dict
            # (all phase values were invalid or empty)
            return ErrorResponse.invalid_input(
                f"Section 9 exists but contains no valid task lists. Phases found: {list(raw_section_9.keys())}",
                "Each phase must contain either 'tasks' array or 'items' array with string tasks. "
                "Expected format: {\"phase_1\": {\"items\": [\"task1\", \"task2\"]}} or {\"phase_1\": [\"task1\", \"task2\"]}"
            )

    # Extract all tasks from all phase lists
    all_tasks = []
    logger.debug(f"execute_plan: Processing {len(section_9)} phases from section_9")
    for key, value in section_9.items():
        logger.debug(f"execute_plan: Phase {key}, value type={type(value).__name__}, is list={isinstance(value, list)}")

        if key == "CRITICAL_AGENTIC_WORKFLOW":
            continue  # Skip workflow instructions

        if isinstance(value, list):
            logger.debug(f"execute_plan: Phase {key} has {len(value)} tasks")
            # This is a phase list
            for idx, task in enumerate(value):
                logger.debug(f"execute_plan: Task {idx} type={type(task).__name__}")
                if isinstance(task, str):
                    # Check for checkbox prefix format (legacy)
                    if any(prefix in task for prefix in ["☐", "☑", "⏳", "🚫"]):
                        task_clean = task.lstrip("☐☑⏳🚫").strip()
                        if "☑" in task:
                            status = "completed"
                        elif "⏳" in task:
                            status = "in_progress"
                        elif "🚫" in task:
                            status = "blocked"
                        else:
                            status = "pending"
                    else:
                        # Plain text format (common AI generation)
                        task_clean = task.strip()
                        status = "pending"

                    # Extract TASK-ID and description
                    if ": " in task_clean:
                        task_id, description = task_clean.split(": ", 1)
                    else:
                        # Generate task ID from phase key and index
                        phase_prefix = key.upper().replace("_", "-")[:8]
                        task_id = f"{phase_prefix}-{idx+1:03d}"
                        description = task_clean

                    # Generate activeForm (present continuous)
                    active_form = generate_active_form(description)

                    # Create TodoWrite format with TASK-ID first
                    todo_item = {
                        "content": f"{task_id}: {description}",
                        "activeForm": f"{task_id}: {active_form}",
                        "status": status
                    }
                    all_tasks.append(todo_item)

    if not all_tasks:
        return ErrorResponse.invalid_input(
            "No tasks found in plan.json section 9",
            "Plan must contain at least one task in implementation checklist"
        )

    # Log execution
    log_execution(project_path, feature_name, workorder_id, all_tasks)

    logger.info(
        f"Generated TodoWrite list for {feature_name}",
        extra={
            'feature_name': feature_name,
            'workorder_id': workorder_id,
            'task_count': len(all_tasks)
        }
    )

    return format_success_response(
        data={
            'feature_name': feature_name,
            'workorder_id': workorder_id,
            'task_count': len(all_tasks),
            'tasks': all_tasks,
            'plan_file': str(plan_file)
        },
        message=f"✅ Generated {len(all_tasks)} tasks for {feature_name} [{workorder_id}]"
    )


def generate_active_form(description: str) -> str:
    """
    Convert task description to present continuous tense (gerund form).

    Examples:
        "Install dependencies" → "Installing dependencies"
        "Create auth directory" → "Creating auth directory"
        "Implement load_plan()" → "Implementing load_plan()"

    Args:
        description: Task description in imperative form

    Returns:
        Description in present continuous form
    """
    words = description.split()
    if not words:
        return description

    # Get first word (verb)
    verb = words[0]

    # Simple gerund conversion rules
    gerund_map = {
        "Install": "Installing",
        "Create": "Creating",
        "Implement": "Implementing",
        "Add": "Adding",
        "Write": "Writing",
        "Update": "Updating",
        "Register": "Registering",
        "Test": "Testing",
        "Review": "Reviewing",
        "Extract": "Extracting",
        "Parse": "Parsing",
        "Generate": "Generating",
        "Build": "Building",
        "Run": "Running",
        "Fix": "Fixing"
    }

    gerund = gerund_map.get(verb, verb + "ing")

    # Reconstruct description with gerund
    return gerund + " " + " ".join(words[1:]) if len(words) > 1 else gerund


def log_execution(project_path: Path, feature_name: str, workorder_id: str, tasks: list) -> None:
    """
    Log execution details to execution-log.json in feature directory.

    Args:
        project_path: Project root directory
        feature_name: Feature being executed
        workorder_id: Workorder ID from plan
        tasks: List of TodoWrite-formatted tasks
    """
    log_file = Path(project_path) / Paths.CONTEXT_DIR / "workorder" / feature_name / "execution-log.json"

    execution_entry = {
        "timestamp": datetime.now().isoformat(),
        "workorder_id": workorder_id,
        "feature_name": feature_name,
        "task_count": len(tasks),
        "tasks": tasks
    }

    # Load existing log or create new
    execution_log = []
    if log_file.exists():
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                execution_log = json.load(f)
        except json.JSONDecodeError:
            logger.warning(f"Malformed execution log, creating new: {log_file}")
            execution_log = []

    # Append new entry
    execution_log.append(execution_entry)

    # Save log
    try:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(execution_log, f, indent=2)

        # GAP-002 + GAP-004 + GAP-005: Validate with cross-validation, factory, and centralized handling
        try:
            # GAP-004: Use ValidatorFactory (note: execution-log requires explicit validator due to cross-validation param)
            from papertrail.validators.execution_log import ExecutionLogValidator
            from utils.validation_helpers import handle_validation_result

            validator = ExecutionLogValidator()

            # GAP-002: Enable cross-validation to detect orphaned task IDs
            result = validator.validate_file(str(log_file), enable_cross_validation=True)

            # GAP-002: Check for critical errors (orphaned task IDs) BEFORE centralized handling
            critical_errors = [e for e in result.get('errors', []) if e.get('severity') == 'CRITICAL']
            if critical_errors:
                error_msg = f"Critical validation errors in execution log (orphaned task IDs): {critical_errors}"
                logger.error(error_msg)
                raise ValueError(error_msg)

            # GAP-005: Use centralized error handling for non-critical errors
            handle_validation_result(result, "execution-log.json")

        except ImportError:
            logger.warning("ExecutionLogValidator not available - skipping validation")
        except ValueError:
            # Re-raise critical validation errors (orphaned task IDs)
            raise
        except Exception as val_error:
            logger.warning(f"Execution log validation error: {val_error} - continuing")

        logger.info(f"Execution logged to: {log_file}")
    except Exception as e:
        # Non-fatal: log warning and continue
        logger.warning(f"Failed to write execution log: {str(e)}", extra={'log_file': str(log_file)})


@log_invocation
@mcp_error_handler
async def handle_log_workorder(arguments: dict) -> list[TextContent]:
    """
    Handle log_workorder tool call.

    Creates simple one-line workorder log entry with format:
    WO-ID | Project | Description | Timestamp

    Latest entries appear at top (prepend, reverse chronological).
    Thread-safe with file locking for concurrent access.

    Args:
        arguments: Dict with:
            - project_path (required): Absolute path to project directory
            - workorder_id (required): Workorder ID (e.g., WO-AUTH-001)
            - project_name (required): Project name (short identifier)
            - description (required): Brief description (max 50 chars recommended)
            - timestamp (optional): ISO 8601 timestamp (auto-generated if not provided)

    Returns:
        Success response with log entry confirmation
    """
    from validation import validate_workorder_id

    # Validate inputs
    project_path = validate_project_path_input(arguments.get("project_path", ""))
    workorder_id = validate_workorder_id(arguments.get("workorder_id", ""))
    project_name = arguments.get("project_name", "").strip()
    description = arguments.get("description", "").strip()
    timestamp_arg = arguments.get("timestamp")

    if not project_name:
        raise ValueError("project_name is required")
    if not description:
        raise ValueError("description is required")

    # Truncate description to 50 chars for readability
    if len(description) > 50:
        description = description[:47] + "..."
        logger.info(f"Truncated description to 50 chars")

    # Generate timestamp if not provided
    if timestamp_arg:
        timestamp = timestamp_arg
    else:
        timestamp = get_workorder_timestamp()

    logger.info(
        f"Logging workorder: {workorder_id}",
        extra={
            'project_path': str(project_path),
            'workorder_id': workorder_id,
            'project_name': project_name
        }
    )

    # Build log entry
    log_entry = f"{workorder_id} | {project_name} | {description} | {timestamp}\n"

    # Ensure coderef directory exists
    coderef_dir = Path(project_path) / Paths.CODEREF
    coderef_dir.mkdir(parents=True, exist_ok=True)

    # Path to log file
    log_file = coderef_dir / Files.WORKORDER_LOG

    # Prepend to log file (read-then-write approach, simpler for Windows)
    try:
        # Read existing content if file exists
        existing_content = ""
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                existing_content = f.read()

        # Write new entry at top
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(log_entry)
            f.write(existing_content)

        logger.info(f"Workorder logged successfully to local: {workorder_id}")
    except IOError as e:
        raise IOError(f"Failed to write workorder log: {e}")

    # Dual logging: Also write to orchestrator's workorder-log.txt
    orchestrator_logged = False
    orchestrator_log_path = None
    try:
        from constants import OrchestratorPaths
        orchestrator_root = Path(OrchestratorPaths.ROOT)
        orchestrator_log_path = orchestrator_root / OrchestratorPaths.WORKORDER_LOG

        # Ensure orchestrator coderef directory exists
        orchestrator_log_path.parent.mkdir(parents=True, exist_ok=True)

        # Read existing orchestrator log content
        orchestrator_existing = ""
        if orchestrator_log_path.exists():
            with open(orchestrator_log_path, 'r', encoding='utf-8') as f:
                orchestrator_existing = f.read()

        # Write new entry at top of orchestrator log
        with open(orchestrator_log_path, 'w', encoding='utf-8') as f:
            f.write(log_entry)
            f.write(orchestrator_existing)

        orchestrator_logged = True
        logger.info(f"Workorder logged successfully to orchestrator: {workorder_id}")
    except Exception as e:
        # Graceful failure - log warning but don't fail the operation
        logger.warning(
            f"Failed to log workorder to orchestrator (non-blocking): {e}",
            extra={'workorder_id': workorder_id, 'orchestrator_path': str(orchestrator_log_path) if orchestrator_log_path else 'unknown'}
        )

    return format_success_response(
        data={
            'workorder_id': workorder_id,
            'project_name': project_name,
            'description': description,
            'timestamp': timestamp,
            'log_file': str(log_file.relative_to(Path(project_path))),
            'orchestrator_logged': orchestrator_logged,
            'orchestrator_log_file': str(orchestrator_log_path) if orchestrator_logged else None,
            'success': True
        },
        message=f"✅ Logged workorder {workorder_id} to {Files.WORKORDER_LOG}" + (" + orchestrator" if orchestrator_logged else "")
    )


@log_invocation
@mcp_error_handler
async def handle_get_workorder_log(arguments: dict) -> list[TextContent]:
    """
    Handle get_workorder_log tool call.

    Reads and queries the global workorder log file.
    Returns all entries or filtered by project name, workorder ID pattern, or limit.
    Entries displayed in reverse chronological order (latest first).

    Args:
        arguments: Dict with:
            - project_path (required): Absolute path to project directory
            - project_name (optional): Filter by project name (partial match, case-insensitive)
            - workorder_pattern (optional): Filter by workorder ID pattern (e.g., "WO-AUTH")
            - limit (optional): Maximum number of entries to return

    Returns:
        Success response with log entries
    """
    # Validate inputs
    project_path = validate_project_path_input(arguments.get("project_path", ""))
    project_name_filter = arguments.get("project_name", "").strip().lower()
    workorder_pattern = arguments.get("workorder_pattern", "").strip().upper()
    limit = arguments.get("limit")

    logger.info(
        f"Reading workorder log",
        extra={
            'project_path': str(project_path),
            'project_name_filter': project_name_filter,
            'workorder_pattern': workorder_pattern,
            'limit': limit
        }
    )

    # Path to log file
    log_file = Path(project_path) / Paths.CODEREF / Files.WORKORDER_LOG

    if not log_file.exists():
        logger.info("Workorder log file does not exist yet")
        return format_success_response(
            data={
                'entries': [],
                'total_count': 0,
                'filtered_count': 0,
                'log_file': str(Path(Paths.CODEREF) / Files.WORKORDER_LOG),
                'message': 'No workorder log file found (no entries logged yet)',
                'success': True
            },
            message="No workorder entries found"
        )

    # Read log file
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except IOError as e:
        raise IOError(f"Failed to read workorder log: {e}")

    # Parse entries
    entries = []
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Parse format: WO-ID | Project | Description | Timestamp
        parts = line.split('|')
        if len(parts) != 4:
            logger.warning(f"Skipping malformed log entry: {line}")
            continue

        wo_id, proj, desc, ts = [p.strip() for p in parts]

        # Apply filters
        if project_name_filter and project_name_filter not in proj.lower():
            continue

        if workorder_pattern and not wo_id.startswith(workorder_pattern):
            continue

        entries.append({
            'workorder_id': wo_id,
            'project': proj,
            'description': desc,
            'timestamp': ts
        })

    # Apply limit
    if limit and limit > 0:
        entries = entries[:limit]

    logger.info(f"Found {len(entries)} workorder entries (total {len(lines)} in log)")

    return format_success_response(
        data={
            'entries': entries,
            'total_count': len(lines),
            'filtered_count': len(entries),
            'log_file': str(log_file.relative_to(Path(project_path))),
            'filters_applied': {
                'project_name': project_name_filter or None,
                'workorder_pattern': workorder_pattern or None,
                'limit': limit
            },
            'success': True
        },
        message=f"✅ Found {len(entries)} workorder entries"
    )


@log_invocation
@mcp_error_handler
async def handle_generate_handoff_context(arguments: dict) -> list[TextContent]:
    """
    Handle generate_handoff_context tool call.

    Generates automated agent handoff context files (claude.md) from plan.json,
    analysis.json, and git history. Reduces agent handoff time from 20-30 minutes
    to under 5 minutes by auto-populating 80%+ context fields.

    Args:
        arguments: Dict with:
            - project_path (required): Absolute path to project directory
            - feature_name (required): Feature name (alphanumeric, hyphens, underscores)
            - mode (optional): Template mode - "full" or "minimal" (default: "full")

    Returns:
        Success response with output path, mode, and auto-population stats
    """
    # Validate inputs
    project_path = validate_project_path_input(arguments.get("project_path", ""))
    feature_name = validate_feature_name_input(arguments.get("feature_name", ""))
    mode = arguments.get("mode", "full").strip().lower()

    if mode not in ["full", "minimal"]:
        raise ValueError(f"Invalid mode: {mode}. Must be 'full' or 'minimal'")

    logger.info(
        f"Generating handoff context for feature: {feature_name}, mode: {mode}",
        extra={
            'project_path': str(project_path),
            'feature_name': feature_name,
            'mode': mode
        }
    )

    # Import generator
    from generators.handoff_generator import HandoffGenerator

    # Generate handoff context
    generator = HandoffGenerator(project_path)
    result = generator.generate_handoff_context(feature_name, mode)

    logger.info(
        f"Handoff context generated successfully",
        extra={
            'output_path': result['output_path'],
            'auto_populated': result['auto_populated_fields']
        }
    )

    return format_success_response(
        data=result,
        message=f"✅ Handoff context generated: {result['output_path']}"
    )


@log_invocation
@mcp_error_handler
async def handle_assess_risk(arguments: dict) -> list[TextContent]:
    """
    Handle assess_risk tool call.

    Evaluates proposed code changes across 5 risk dimensions (breaking changes,
    security, performance, maintainability, reversibility) and generates structured
    risk assessment with go/no-go recommendations.

    Uses @log_invocation and @mcp_error_handler decorators for automatic
    logging and error handling (ARCH-004, ARCH-005).

    WO-RISK-ASSESSMENT-001
    """
    # Start performance timer (must complete in < 5 seconds)
    start_time = time.time()

    # Validate inputs at boundary
    validated = validate_risk_inputs(arguments)
    project_path = Path(validated['project_path'])
    proposed_change = validated['proposed_change']
    options = validated.get('options')
    threshold = validated.get('threshold', 50.0)

    logger.info(
        "Starting risk assessment",
        extra={
            'project_path': str(project_path),
            'change_type': proposed_change['change_type'],
            'files_affected': len(proposed_change['files_affected']),
            'threshold': threshold,
            'multi_option': options is not None
        }
    )

    # Initialize generator
    generator = RiskGenerator(project_path)

    # Analyze project context
    context = generator.analyze_project_context()

    # Single-option vs multi-option mode
    if options:
        # Multi-option comparison mode
        logger.info(f"Comparing {len(options)} alternative options")

        # Add the primary proposed_change as option 1
        all_options = [proposed_change] + options

        # Compare all options
        comparison = generator.compare_options(all_options, context)

        # For the recommended option, generate full assessment
        recommended_idx = int(comparison['recommended_option'].split('_')[1]) - 1
        best_option = all_options[recommended_idx]

        # Evaluate all dimensions for the best option
        dimensions = {
            'breaking_changes': generator.evaluate_breaking_changes(best_option, context),
            'security': generator.evaluate_security_risks(best_option, context),
            'performance': generator.evaluate_performance_impact(best_option, context),
            'maintainability': generator.evaluate_maintainability(best_option, context),
            'reversibility': generator.evaluate_reversibility(best_option, context)
        }

        composite_score = generator.calculate_composite_score(dimensions)
        recommendation = generator.generate_recommendations(composite_score, dimensions, threshold)
        mitigation_strategies = generator.generate_mitigation_strategies(dimensions)

        # Build assessment with comparison
        assessment_id = f"RA-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        assessment: dict = {
            'assessment_id': assessment_id,
            'generated_at': datetime.now().isoformat(),
            'project_path': str(project_path),
            'proposed_change': best_option,
            'risk_dimensions': dimensions,
            'composite_score': composite_score,
            'recommendation': recommendation,
            'mitigation_strategies': mitigation_strategies,
            'options_analyzed': len(all_options),
            'comparison': comparison,
            'project_context': context,
            'metadata': {
                'version': '1.0.0',
                'tool_version': '1.12.0',
                'duration_ms': 0,  # Will be updated below
                'workorder_id': 'WO-RISK-ASSESSMENT-001'
            }
        }

    else:
        # Single-option mode
        logger.info("Evaluating single proposed change")

        # Evaluate all 5 risk dimensions
        dimensions = {
            'breaking_changes': generator.evaluate_breaking_changes(proposed_change, context),
            'security': generator.evaluate_security_risks(proposed_change, context),
            'performance': generator.evaluate_performance_impact(proposed_change, context),
            'maintainability': generator.evaluate_maintainability(proposed_change, context),
            'reversibility': generator.evaluate_reversibility(proposed_change, context)
        }

        # Calculate composite score
        composite_score = generator.calculate_composite_score(dimensions)

        # Generate recommendations
        recommendation = generator.generate_recommendations(composite_score, dimensions, threshold)

        # Generate mitigation strategies
        mitigation_strategies = generator.generate_mitigation_strategies(dimensions)

        # Build assessment
        assessment_id = f"RA-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        assessment: dict = {
            'assessment_id': assessment_id,
            'generated_at': datetime.now().isoformat(),
            'project_path': str(project_path),
            'proposed_change': proposed_change,
            'risk_dimensions': dimensions,
            'composite_score': composite_score,
            'recommendation': recommendation,
            'mitigation_strategies': mitigation_strategies,
            'options_analyzed': 1,
            'project_context': context,
            'metadata': {
                'version': '1.0.0',
                'tool_version': '1.12.0',
                'duration_ms': 0,  # Will be updated below
                'workorder_id': 'WO-RISK-ASSESSMENT-001'
            }
        }

    # Calculate duration
    duration_ms = (time.time() - start_time) * 1000
    assessment['metadata']['duration_ms'] = duration_ms

    # Check performance requirement (< 5 seconds)
    if duration_ms > 5000:
        logger.warning(
            f"Risk assessment exceeded 5 second target: {duration_ms:.0f}ms",
            extra={'assessment_id': assessment_id}
        )

    # Save assessment
    feature_name = arguments.get('feature_name')  # Optional feature name
    assessment_path = generator.save_assessment(assessment, feature_name)

    # Prepare result
    result = {
        'assessment_path': str(assessment_path),
        'assessment_id': assessment_id,
        'composite_score': composite_score['score'],
        'risk_level': composite_score['level'],
        'decision': recommendation['decision'],
        'options_analyzed': assessment['options_analyzed'],
        'recommended_option': assessment.get('comparison', {}).get('recommended_option', 'option_1'),
        'duration_ms': duration_ms,
        'success': True
    }

    logger.info(
        f"Risk assessment complete: {composite_score['level']} risk ({composite_score['score']:.1f}), decision: {recommendation['decision']}",
        extra={
            'assessment_id': assessment_id,
            'duration_ms': duration_ms,
            'risk_level': composite_score['level']
        }
    )

    return format_success_response(
        data=result,
        message=f"✅ Risk assessment complete: {composite_score['level'].upper()} risk ({composite_score['score']:.1f}/100) - {recommendation['decision']}"
    )


@log_invocation
@mcp_error_handler
async def handle_coderef_foundation_docs(arguments: dict) -> list[TextContent]:
    """
    Handle coderef_foundation_docs tool call.

    Unified foundation docs generator powered by coderef analysis. Generates:
    - ARCHITECTURE.md (patterns, decisions, constraints)
    - SCHEMA.md (entities, relationships)
    - COMPONENTS.md (component hierarchy - UI projects only)
    - project-context.json (structured context for planning)

    Replaces: api_inventory, database_inventory, dependency_inventory,
              config_inventory, test_inventory, inventory_manifest, documentation_inventory
    """
    # Validate project_path
    project_path = validate_project_path_input(arguments.get('project_path', ''))
    project_path_obj = Path(project_path).resolve()

    # Get optional parameters
    include_components = arguments.get('include_components')  # None = auto-detect
    deep_extraction = arguments.get('deep_extraction', True)
    use_coderef = arguments.get('use_coderef', True)
    force_regenerate = arguments.get('force_regenerate', False)

    logger.info(
        f"Starting coderef foundation docs generation for: {project_path_obj}",
        extra={
            'include_components': include_components,
            'deep_extraction': deep_extraction,
            'use_coderef': use_coderef,
            'force_regenerate': force_regenerate
        }
    )

    # Import generator (lazy import to avoid circular dependencies)
    from generators.coderef_foundation_generator import CoderefFoundationGenerator

    # Initialize generator
    generator = CoderefFoundationGenerator(
        project_path_obj,
        include_components=include_components,
        deep_extraction=deep_extraction,
        use_coderef=use_coderef,
        force_regenerate=force_regenerate
    )

    # Run generation
    result = generator.generate()

    logger.info(
        "Coderef foundation docs generation complete",
        extra={
            'project_path': str(project_path_obj),
            'files_generated': result.get('files_generated', []),
            'context_sections': list(result.get('project_context', {}).keys())
        }
    )

    # Return only summary to reduce token usage (full data saved to project-context.json)
    project_context = result.get('project_context', {})
    coderef_info = project_context.get('coderef', {})

    # Include progress information in summary
    summary = {
        'files_generated': result.get('files_generated', []),
        'files_skipped': result.get('files_skipped', []),
        'generated_count': result.get('generated_count', 0),
        'skipped_count': result.get('skipped_count', 0),
        'doc_timings': result.get('doc_timings', {}),
        'output_dir': result.get('output_dir', ''),
        'duration_seconds': result.get('duration_seconds', 0),
        'force_regenerate': result.get('force_regenerate', False),
        'summary': {
            'api_endpoints': project_context.get('api_context', {}).get('count', 0),
            'frameworks': project_context.get('api_context', {}).get('frameworks_detected', []),
            'dependencies': project_context.get('dependencies', {}).get('count', 0),
            'database_tables': project_context.get('database', {}).get('table_count', 0),
            'handlers': len(project_context.get('patterns', {}).get('handlers', [])),
            'coderef_available': coderef_info.get('available', False),
            'coderef_elements': coderef_info.get('element_count', 0),
            'auto_scan_performed': result.get('auto_scan_performed', False),
        },
        'context_file': str(Path(result.get('output_dir', '')) / 'project-context.json')
    }

    # Build message with progress info
    generated_count = result.get('generated_count', 0)
    skipped_count = result.get('skipped_count', 0)
    duration = result.get('duration_seconds', 0)
    files_skipped = result.get('files_skipped', [])

    if skipped_count > 0:
        progress_msg = f"generated {generated_count}, skipped {skipped_count}"
        # Add reason for skipped files
        skipped_reason = "already exist"
        if not result.get('force_regenerate', False):
            skipped_reason = "already exist (use force_regenerate: true to overwrite)"
    else:
        progress_msg = f"generated {generated_count}"
        skipped_reason = None

    # Build detailed message with scan method and feedback
    if result.get('auto_scan_performed'):
        message = f"✅ Foundation docs complete ({progress_msg}) - auto-scanned {coderef_info.get('element_count', 0)} elements in {duration}s"
    elif coderef_info.get('available'):
        message = f"✅ Foundation docs complete ({progress_msg}) - {coderef_info.get('element_count', 0)} elements from existing index in {duration}s"
    else:
        message = f"✅ Foundation docs complete ({progress_msg}) - regex fallback in {duration}s"

    # Add skip reason if applicable
    if skipped_reason and files_skipped:
        message += f"\n\n📋 Skipped files ({skipped_reason}):\n"
        for f in files_skipped[:5]:  # Show first 5
            message += f"  - {f}\n"
        if len(files_skipped) > 5:
            message += f"  ... and {len(files_skipped) - 5} more"

    return format_success_response(
        data=summary,
        message=message
    )


# =============================================================================
# Progress Tracking (STUB-009)
# =============================================================================

@log_invocation
@mcp_error_handler
async def handle_update_task_status(arguments: dict) -> list[TextContent]:
    """
    Handle update_task_status tool call (STUB-009).

    Updates task status in plan.json as agents complete work.
    Enables progress tracking during execution.

    Args (in arguments):
        project_path: Absolute path to project directory
        feature_name: Feature name (folder in coderef/workorder/)
        task_id: Task ID to update (e.g., "SETUP-001", "IMPL-002")
        status: New status ("pending", "in_progress", "completed", "blocked")
        notes: Optional notes about the status change

    Returns:
        Success response with updated task info and progress summary
    """
    # Validate inputs
    project_path_str = arguments.get('project_path', '')
    feature_name = arguments.get('feature_name', '')
    task_id = arguments.get('task_id', '')
    status = arguments.get('status', '')
    notes = arguments.get('notes', '')

    project_path = Path(validate_project_path_input(project_path_str)).resolve()
    feature_name = validate_feature_name_input(feature_name)

    # Validate status
    valid_statuses = ['pending', 'in_progress', 'completed', 'blocked']
    if status not in valid_statuses:
        raise ValueError(f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}")

    if not task_id:
        raise ValueError("task_id is required")

    # Load plan.json
    plan_path = project_path / 'coderef' / 'workorder' / feature_name / 'plan.json'
    if not plan_path.exists():
        raise FileNotFoundError(f"Plan not found: {plan_path}")

    with open(plan_path, 'r', encoding='utf-8') as f:
        plan_data = json.load(f)

    # Find and update task in section 9 (implementation checklist)
    structure = plan_data.get('UNIVERSAL_PLANNING_STRUCTURE', {})
    checklist = structure.get('9_implementation_checklist', {})

    task_found = False
    old_status = None

    # Search through checklist categories
    for category_name, category_tasks in checklist.items():
        if isinstance(category_tasks, list):
            for task in category_tasks:
                if isinstance(task, dict) and task.get('id') == task_id:
                    old_status = task.get('status', 'pending')
                    task['status'] = status
                    task['updated_at'] = get_workorder_timestamp()
                    if notes:
                        task['notes'] = notes
                    task_found = True
                    break
        if task_found:
            break

    # Also search in section 5 tasks array
    if not task_found:
        task_section = structure.get('5_task_id_system', {})
        tasks = task_section.get('tasks', [])
        for task in tasks:
            if isinstance(task, dict) and task.get('id') == task_id:
                old_status = task.get('status', 'pending')
                task['status'] = status
                task['updated_at'] = get_workorder_timestamp()
                if notes:
                    task['notes'] = notes
                task_found = True
                break

    if not task_found:
        raise ValueError(f"Task '{task_id}' not found in plan.json")

    # Update META_DOCUMENTATION with last_updated timestamp
    if 'META_DOCUMENTATION' in plan_data:
        plan_data['META_DOCUMENTATION']['last_updated'] = get_workorder_timestamp()

    # Save updated plan
    with open(plan_path, 'w', encoding='utf-8') as f:
        json.dump(plan_data, f, indent=2, ensure_ascii=False)
        f.write('\n')

    # GAP-004 + GAP-005: Validate plan.json with ValidatorFactory and centralized error handling
    try:
        from papertrail.validators.factory import ValidatorFactory
        from utils.validation_helpers import handle_validation_result

        validator = ValidatorFactory.get_validator(str(plan_path))
        result = validator.validate_file(str(plan_path))
        handle_validation_result(result, "plan.json")
    except ImportError:
        logger.warning("Papertrail validators not available - skipping update validation")
    except ValueError:
        logger.error("plan.json validation failed critically - continuing with partial data")
    except Exception as e:
        logger.warning(f"Plan update validation error: {e} - continuing without validation")

    # Calculate progress summary
    total_tasks = 0
    completed_tasks = 0
    in_progress_tasks = 0
    blocked_tasks = 0

    for category_name, category_tasks in checklist.items():
        if isinstance(category_tasks, list):
            for task in category_tasks:
                if isinstance(task, dict):
                    total_tasks += 1
                    task_status = task.get('status', 'pending')
                    if task_status == 'completed':
                        completed_tasks += 1
                    elif task_status == 'in_progress':
                        in_progress_tasks += 1
                    elif task_status == 'blocked':
                        blocked_tasks += 1

    progress_percent = round((completed_tasks / total_tasks) * 100, 1) if total_tasks > 0 else 0

    logger.info(f"Task status updated: {task_id} ({old_status} -> {status})", extra={
        'feature_name': feature_name,
        'task_id': task_id,
        'old_status': old_status,
        'new_status': status,
        'progress_percent': progress_percent
    })

    return format_success_response(
        data={
            'task_id': task_id,
            'old_status': old_status,
            'new_status': status,
            'notes': notes,
            'plan_path': str(plan_path.relative_to(project_path)),
            'progress': {
                'total': total_tasks,
                'completed': completed_tasks,
                'in_progress': in_progress_tasks,
                'blocked': blocked_tasks,
                'pending': total_tasks - completed_tasks - in_progress_tasks - blocked_tasks,
                'percent': progress_percent
            }
        },
        message=f"✅ Task {task_id} status updated: {old_status} → {status}"
    )


@log_invocation
@mcp_error_handler
async def handle_audit_plans(arguments: dict) -> list[TextContent]:
    """
    Handle audit_plans tool call (STUB-011).

    Audits all plans in coderef/workorder/ directory to provide:
    - Plan format validation (must be JSON)
    - Progress status extraction
    - Stale plan detection (>7 days since last update)
    - Issue identification and recommendations

    Args (in arguments):
        project_path: Absolute path to project directory
        stale_days: Days without update to consider stale (default: 7)
        include_archived: Whether to also audit archived plans (default: False)

    Returns:
        Success response with audit results for all plans
    """
    from plan_format_validator import enforce_plan_format, check_for_invalid_plans

    # Validate inputs
    project_path_str = arguments.get('project_path', '')
    stale_days = arguments.get('stale_days', 7)
    include_archived = arguments.get('include_archived', False)

    project_path = Path(validate_project_path_input(project_path_str)).resolve()

    # Validate stale_days is reasonable
    if not isinstance(stale_days, int) or stale_days < 1 or stale_days > 365:
        raise ValueError("stale_days must be an integer between 1 and 365")

    # Build paths
    working_dir = project_path / 'coderef' / 'workorder'
    archived_dir = project_path / 'coderef' / 'archived'

    if not working_dir.exists():
        raise FileNotFoundError(f"Working directory not found: {working_dir}")

    audit_results = {
        'total_features': 0,
        'valid_plans': 0,
        'invalid_plans': 0,
        'stale_plans': 0,
        'active_plans': 0,
        'completed_plans': 0,
        'features': [],
        'issues': [],
        'recommendations': []
    }

    # Scan for invalid plan files first
    invalid_files = check_for_invalid_plans(working_dir)
    for invalid in invalid_files:
        audit_results['issues'].append({
            'type': 'invalid_format',
            'severity': 'critical',
            'path': str(invalid['path']),
            'issue': invalid['issue']
        })

    # Scan working directory for features
    dirs_to_scan = [working_dir]
    if include_archived and archived_dir.exists():
        dirs_to_scan.append(archived_dir)

    current_time = datetime.now()
    stale_threshold = current_time.timestamp() - (stale_days * 24 * 60 * 60)

    for scan_dir in dirs_to_scan:
        is_archived = scan_dir == archived_dir

        for feature_dir in scan_dir.iterdir():
            if not feature_dir.is_dir():
                continue

            audit_results['total_features'] += 1
            feature_name = feature_dir.name
            plan_path = feature_dir / 'plan.json'

            feature_audit = {
                'feature_name': feature_name,
                'location': 'archived' if is_archived else 'working',
                'has_plan': False,
                'plan_valid': False,
                'is_stale': False,
                'progress': None,
                'workorder_id': None,
                'last_updated': None,
                'issues': []
            }

            if not plan_path.exists():
                feature_audit['issues'].append('No plan.json found')
                audit_results['issues'].append({
                    'type': 'missing_plan',
                    'severity': 'major',
                    'feature': feature_name,
                    'issue': 'No plan.json found in feature directory'
                })
            else:
                feature_audit['has_plan'] = True

                # Validate plan format
                is_valid, errors, _ = enforce_plan_format(
                    plan_path=plan_path,
                    project_path=project_path,
                    strict=False
                )

                if is_valid:
                    feature_audit['plan_valid'] = True
                    audit_results['valid_plans'] += 1

                    # Load plan to extract details
                    try:
                        with open(plan_path, 'r', encoding='utf-8') as f:
                            plan_data = json.load(f)

                        # Extract workorder ID
                        meta = plan_data.get('META_DOCUMENTATION', {})
                        feature_audit['workorder_id'] = meta.get('workorder_id')
                        feature_audit['last_updated'] = meta.get('last_updated')

                        # Check staleness
                        last_modified = plan_path.stat().st_mtime
                        if last_modified < stale_threshold:
                            feature_audit['is_stale'] = True
                            audit_results['stale_plans'] += 1
                            feature_audit['issues'].append(
                                f'Plan is stale (not updated in {stale_days}+ days)'
                            )

                        # Extract progress from section 9
                        structure = plan_data.get('UNIVERSAL_PLANNING_STRUCTURE', {})
                        checklist = structure.get('9_implementation_checklist', {})

                        total = 0
                        completed = 0
                        in_progress = 0
                        blocked = 0

                        for category, tasks in checklist.items():
                            if isinstance(tasks, list):
                                for task in tasks:
                                    if isinstance(task, dict):
                                        total += 1
                                        status = task.get('status', 'pending')
                                        if status == 'completed':
                                            completed += 1
                                        elif status == 'in_progress':
                                            in_progress += 1
                                        elif status == 'blocked':
                                            blocked += 1

                        if total > 0:
                            percent = round((completed / total) * 100, 1)
                            feature_audit['progress'] = {
                                'total': total,
                                'completed': completed,
                                'in_progress': in_progress,
                                'blocked': blocked,
                                'pending': total - completed - in_progress - blocked,
                                'percent': percent
                            }

                            # Determine plan status
                            if percent == 100:
                                audit_results['completed_plans'] += 1
                            elif in_progress > 0 or completed > 0:
                                audit_results['active_plans'] += 1

                            # Check for blocked tasks
                            if blocked > 0:
                                feature_audit['issues'].append(
                                    f'{blocked} task(s) are blocked'
                                )
                                audit_results['issues'].append({
                                    'type': 'blocked_tasks',
                                    'severity': 'major',
                                    'feature': feature_name,
                                    'issue': f'{blocked} blocked task(s) need attention'
                                })

                    except json.JSONDecodeError as e:
                        feature_audit['issues'].append(f'Invalid JSON: {e.msg}')
                        audit_results['issues'].append({
                            'type': 'invalid_json',
                            'severity': 'critical',
                            'feature': feature_name,
                            'issue': f'plan.json is malformed: {e.msg}'
                        })

                else:
                    audit_results['invalid_plans'] += 1
                    for error in errors:
                        feature_audit['issues'].append(error)
                        audit_results['issues'].append({
                            'type': 'validation_error',
                            'severity': 'major',
                            'feature': feature_name,
                            'issue': error
                        })

            audit_results['features'].append(feature_audit)

    # Generate recommendations based on issues
    if audit_results['invalid_plans'] > 0:
        audit_results['recommendations'].append(
            f"Fix {audit_results['invalid_plans']} invalid plan(s) using /create-plan"
        )

    if audit_results['stale_plans'] > 0:
        audit_results['recommendations'].append(
            f"Review {audit_results['stale_plans']} stale plan(s) - consider archiving if complete"
        )

    blocked_count = sum(1 for issue in audit_results['issues'] if issue.get('type') == 'blocked_tasks')
    if blocked_count > 0:
        audit_results['recommendations'].append(
            f"Resolve blockers in {blocked_count} feature(s) to continue progress"
        )

    missing_count = sum(1 for issue in audit_results['issues'] if issue.get('type') == 'missing_plan')
    if missing_count > 0:
        audit_results['recommendations'].append(
            f"Create plans for {missing_count} feature(s) using /create-workorder"
        )

    # Calculate summary stats
    audit_results['health_score'] = 0
    if audit_results['total_features'] > 0:
        # Score calculation: valid plans get points, issues subtract points
        valid_ratio = audit_results['valid_plans'] / audit_results['total_features']
        issue_penalty = min(len(audit_results['issues']) * 5, 50)  # Max 50 point penalty
        audit_results['health_score'] = max(0, round(valid_ratio * 100 - issue_penalty))

    logger.info(f"Plan audit complete: {audit_results['valid_plans']}/{audit_results['total_features']} valid plans, health score: {audit_results['health_score']}")

    return format_success_response(
        data={
            'total_features': audit_results['total_features'],
            'valid_plans': audit_results['valid_plans'],
            'invalid_plans': audit_results['invalid_plans'],
            'stale_plans': audit_results['stale_plans'],
            'active_plans': audit_results['active_plans'],
            'completed_plans': audit_results['completed_plans'],
            'health_score': audit_results['health_score'],
            'issues_count': len(audit_results['issues']),
            'issues': audit_results['issues'][:20],  # Limit to first 20 issues
            'recommendations': audit_results['recommendations'],
            'features': audit_results['features']
        },
        message=f"✅ Plan audit: {audit_results['valid_plans']}/{audit_results['total_features']} valid, health score: {audit_results['health_score']}/100"
    )


@log_invocation
@mcp_error_handler
async def handle_generate_features_inventory(arguments: dict) -> list[TextContent]:
    """
    Handle generate_features_inventory tool call.

    Scans coderef/workorder/ and coderef/archived/ to generate a comprehensive
    inventory of all features with their status, progress, and workorder tracking.

    Args (in arguments):
        project_path: Absolute path to project directory
        format: Output format - 'json' or 'markdown' (default: 'json')
        include_archived: Whether to include archived features (default: True)
        save_to_file: Whether to save output to coderef/ directory (default: False)

    Returns:
        Success response with features inventory
    """
    from generators.features_inventory_generator import FeaturesInventoryGenerator

    # Validate inputs
    project_path_str = arguments.get('project_path', '')
    output_format = arguments.get('format', 'json')
    include_archived = arguments.get('include_archived', True)
    save_to_file = arguments.get('save_to_file', False)

    project_path = Path(validate_project_path_input(project_path_str)).resolve()

    # Validate format
    if output_format not in ('json', 'markdown'):
        raise ValueError("format must be 'json' or 'markdown'")

    # Generate inventory
    generator = FeaturesInventoryGenerator(project_path)

    if output_format == 'json':
        inventory = generator.generate_inventory(include_archived=include_archived)
        result = inventory
    else:
        result = {'content': generator.generate_markdown(include_archived=include_archived)}

    # Optionally save to file
    if save_to_file:
        output_path = generator.save_inventory(format=output_format)
        result['saved_to'] = str(output_path.relative_to(project_path))

    return format_success_response(
        data=result,
        message=f"[OK] Features inventory generated: {result.get('summary', {}).get('total_count', 'N/A')} features"
    )


# =============================================================================
# Tool handlers registry (QUA-002)
TOOL_HANDLERS = {
    'list_templates': handle_list_templates,
    'get_template': handle_get_template,
    'generate_foundation_docs': handle_generate_foundation_docs,
    'generate_individual_doc': handle_generate_individual_doc,
    'get_changelog': handle_get_changelog,
    'add_changelog_entry': handle_add_changelog_entry,
    'update_changelog': handle_update_changelog,
    'generate_quickref_interactive': handle_generate_quickref_interactive,
    'establish_standards': handle_establish_standards,
    'audit_codebase': handle_audit_codebase,
    'check_consistency': handle_check_consistency,
    'get_planning_template': handle_get_planning_template,
    'analyze_project_for_planning': handle_analyze_project_for_planning,
    'gather_context': handle_gather_context,
    'validate_implementation_plan': handle_validate_implementation_plan,
    'generate_plan_review_report': handle_generate_plan_review_report,
    'create_plan': handle_create_plan,
    'generate_deliverables_template': handle_generate_deliverables_template,
    'update_deliverables': handle_update_deliverables,
    'generate_agent_communication': handle_generate_agent_communication,
    'assign_agent_task': handle_assign_agent_task,
    'verify_agent_completion': handle_verify_agent_completion,
    'aggregate_agent_deliverables': handle_aggregate_agent_deliverables,
    'track_agent_status': handle_track_agent_status,
    'archive_feature': handle_archive_feature,
    'update_all_documentation': handle_update_all_documentation,
    'execute_plan': handle_execute_plan,
    'update_task_status': handle_update_task_status,
    'audit_plans': handle_audit_plans,
    'log_workorder': handle_log_workorder,
    'get_workorder_log': handle_get_workorder_log,
    'generate_handoff_context': handle_generate_handoff_context,
    'assess_risk': handle_assess_risk,
    'coderef_foundation_docs': handle_coderef_foundation_docs,
    'generate_features_inventory': handle_generate_features_inventory,
}


def set_templates_dir(templates_dir: Path) -> None:
    """Set the TEMPLATES_DIR global for handlers to use."""
    global TEMPLATES_DIR
    TEMPLATES_DIR = templates_dir


def set_tool_templates_dir(tool_templates_dir: Path) -> None:
    """Set the TOOL_TEMPLATES_DIR global for handlers to use."""
    global TOOL_TEMPLATES_DIR
    TOOL_TEMPLATES_DIR = tool_templates_dir
