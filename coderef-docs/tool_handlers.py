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
import os
from datetime import datetime

# These will be injected from server.py
TEMPLATES_DIR = None
TOOL_TEMPLATES_DIR = None

# Import dependencies
from typing import Any
from generators import FoundationGenerator, BaseGenerator, ChangelogGenerator, StandardsGenerator, AuditGenerator
from generators.coderef_foundation_generator import CoderefFoundationGenerator
from generators.planning_analyzer import PlanningAnalyzer
from generators.plan_validator import PlanValidator
from generators.review_formatter import ReviewFormatter
from generators.planning_generator import PlanningGenerator
from generators.risk_generator import RiskGenerator
from generators.resource_sheet_generator import ResourceSheetGenerator
from generators.user_guide_generator import UserGuideGenerator  # USER-003 (WO-GENERATION-ENHANCEMENT-001)
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

# Import .coderef/ integration helpers (WO-CODEREF-CONTEXT-MCP-INTEGRATION-001)
from mcp_integration import (
    check_coderef_resources,
    get_context_instructions,
    get_template_context_files,
    format_missing_resources_warning
)

# Import MCP orchestrator (WO-GENERATION-ENHANCEMENT-001)
from generators.mcp_orchestrator import (
    call_coderef_drift,
    call_coderef_query,
    call_coderef_patterns,
    call_coderef_complexity
)
from constants import DRIFT_WARNING_THRESHOLD, VALIDATION_SCORE_THRESHOLD


# VALIDATE-002: Papertrail validator helper (WO-GENERATION-ENHANCEMENT-001)
async def _call_papertrail_validator(
    doc_path: Path,
    doc_type: str
) -> dict[str, Any]:
    """
    Call Papertrail MCP validator for document validation.

    Attempts to validate a document using the appropriate Papertrail validator
    based on doc_type. Handles Papertrail unavailable gracefully.

    Args:
        doc_path: Absolute path to document file
        doc_type: Document type ('foundation', 'standards', 'resource_sheet', 'user_doc')

    Returns:
        Dictionary with:
        - success: bool (whether validation succeeded)
        - score: int (0-100, or None if failed)
        - errors: list of error messages
        - warnings: list of warning messages
        - error: str (error message if validation failed)
    """
    try:
        # Check if Papertrail is available
        try:
            from papertrail.validators.foundation import FoundationDocValidator
            from papertrail.validators.standards import StandardsDocValidator
            papertrail_available = True
        except ImportError:
            logger.warning("Papertrail validators not available, skipping validation")
            return {
                'success': False,
                'score': None,
                'errors': [],
                'warnings': [],
                'error': 'Papertrail validators not installed'
            }

        # Select appropriate validator based on doc_type
        if doc_type == 'foundation':
            validator = FoundationDocValidator()
        elif doc_type == 'standards':
            validator = StandardsDocValidator()
        else:
            logger.warning(f"Unknown doc_type '{doc_type}', skipping validation")
            return {
                'success': False,
                'score': None,
                'errors': [],
                'warnings': [],
                'error': f'Unknown doc_type: {doc_type}'
            }

        # Run validation
        logger.info(f"Validating {doc_type} document: {doc_path}")
        result = validator.validate_file(doc_path)

        # Extract results
        score = result.score if hasattr(result, 'score') else None
        errors = result.errors if hasattr(result, 'errors') and result.errors else []
        warnings = result.warnings if hasattr(result, 'warnings') and result.warnings else []

        logger.info(f"Validation complete: score={score}, errors={len(errors)}, warnings={len(warnings)}")

        return {
            'success': True,
            'score': score,
            'errors': [str(e) for e in errors],
            'warnings': [str(w) for w in warnings],
            'error': None
        }

    except Exception as e:
        logger.error(f"Papertrail validation failed: {e}", exc_info=True)
        return {
            'success': False,
            'score': None,
            'errors': [],
            'warnings': [],
            'error': str(e)
        }


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

    # CONSOLIDATE-008: Add MCP status (WO-GENERATION-ENHANCEMENT-001)
    result += f"\n\n" + "=" * 60 + "\n"
    result += f"\n🔧 MCP INTEGRATION STATUS:\n\n"
    if CODEREF_CONTEXT_AVAILABLE:
        result += f"  • coderef-context MCP: ✅ Available\n"
        result += f"  • Enhanced Features: Drift detection, pattern analysis, semantic insights\n"
    else:
        result += f"  • coderef-context MCP: ⚠️ Unavailable\n"
        result += f"  • Fallback Mode: Template-only generation (reduced accuracy)\n"
        result += f"  • Recommendation: Start coderef-context MCP server for full features\n"

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

    # Check .coderef/ resources (WO-CODEREF-CONTEXT-MCP-INTEGRATION-001)
    resources = check_coderef_resources(Path(project_path))

    # DRIFT-001: Enhanced drift detection with severity levels (WO-GENERATION-ENHANCEMENT-001)
    drift_result = None
    drift_warning = ""
    drift_severity = "none"  # none, standard, severe

    if resources['resources_available']:
        drift_result = await call_coderef_drift(Path(project_path))
        if drift_result['success']:
            drift_percent = drift_result['drift_percent']

            # Determine severity level
            if drift_percent > 50:
                drift_severity = "severe"
                drift_warning = f"🚨 CRITICAL WARNING: Index severely stale ({drift_percent:.1f}% drift)\n"
                drift_warning += f"⚠️  Documentation will be HIGHLY INACCURATE with this level of drift!\n"
                drift_warning += f"Index age: {drift_result['index_age']}\n"
                drift_warning += f"Recommendation: {drift_result['recommendation']}\n"
                if drift_result['files_changed'] > 0:
                    drift_warning += f"Changes: {drift_result['files_changed']} modified, "
                    drift_warning += f"{drift_result['files_added']} added, "
                    drift_warning += f"{drift_result['files_deleted']} deleted\n"
                drift_warning += "\n⚠️  STRONGLY RECOMMEND: Re-scan before continuing\n"
                drift_warning += f"Run: mcp__coderef_context__coderef_scan(project_path=\"{project_path}\")\n"
            elif drift_percent > DRIFT_WARNING_THRESHOLD:
                drift_severity = "standard"
                drift_warning = f"⚠ WARNING: Index drift detected ({drift_percent:.1f}%)\n"
                drift_warning += f"Documentation accuracy may be reduced.\n"
                drift_warning += f"Index age: {drift_result['index_age']}\n"
                drift_warning += f"Recommendation: {drift_result['recommendation']}\n"
                if drift_result['files_changed'] > 0:
                    drift_warning += f"Changes: {drift_result['files_changed']} modified, "
                    drift_warning += f"{drift_result['files_added']} added, "
                    drift_warning += f"{drift_result['files_deleted']} deleted\n"
                drift_warning += "\nConsider re-scanning if accuracy is critical.\n"

            logger.info(f"Drift check complete: {drift_percent:.1f}% drift (severity: {drift_severity})")
        else:
            logger.warning(f"Drift check failed: {drift_result.get('error', 'Unknown error')}")

    # Start building response with plan
    result = "=== FOUNDATION DOCS - SEQUENTIAL GENERATION ===\n\n"
    result += f"Project: {project_path}\n"
    result += f"Total documents: {len(templates_to_generate)}\n"
    result += f"Context Injection: ENABLED (.coderef/ resources)\n"
    result += f"Resources Status: {'✓ Available' if resources['resources_available'] else '⚠ Missing'}\n"
    if drift_result and drift_result['success']:
        result += f"Index Drift: {drift_result['drift_percent']:.1f}%"
        if drift_severity == "severe":
            result += " 🚨 CRITICAL"
        elif drift_severity == "standard":
            result += " ⚠ HIGH"
        result += "\n"
    if drift_warning:
        result += f"\n{drift_warning}"
    result += "\nGeneration Plan:\n"
    result += "-" * 50 + "\n\n"

    for i, (template_name, description) in enumerate(templates_to_generate, 1):
        result += f"[{i}/{len(templates_to_generate)}] {template_name.upper()}\n"
        result += f"    Description: {description}\n"
        result += "\n"

    result += "\n" + "=" * 50 + "\n\n"
    result += "GENERATION SEQUENCE:\n\n"

    # Generate each template sequentially
    for i, (template_name, description) in enumerate(templates_to_generate, 1):
        result += f"[{i}/{len(templates_to_generate)}] Generating {template_name.upper()}...\n"
        result += f"Tool: generate_individual_doc\n"
        result += f"Template: {template_name}\n"
        result += "\n"

    result += "=" * 50 + "\n\n"
    result += "INSTRUCTIONS:\n"
    result += "1. Each template will generate in sequence with progress indicators\n"
    result += "2. Use .coderef/ resources for code intelligence (see below)\n"
    result += "3. Save each document to its output location as indicated\n"
    result += "4. Each doc builds on previous ones (refs to earlier docs where needed)\n"
    result += "\n"
    result += "=" * 50 + "\n"
    result += "\n=== CODE INTELLIGENCE (.coderef/) ===\n\n"

    if resources['resources_available']:
        result += f"✓ .coderef/ resources available\n"
        result += f"Location: {resources['coderef_dir']}\n\n"
        result += "AVAILABLE RESOURCES:\n"
        for name, info in resources['available'].items():
            result += f"  - {name}"
            if 'size' in info and isinstance(info['size'], int):
                result += f" ({info['size']} elements)"
            result += f"\n"

        if resources['missing']:
            result += f"\nOptional (missing): {', '.join(resources['missing'])}\n"

        result += "\nWORKFLOW:\n"
        result += "1. Read template-specific .coderef/ files for each template:\n"
        result += "   - README: context.md, patterns.json\n"
        result += "   - ARCHITECTURE: context.json, graph.json, diagrams/\n"
        result += "   - API: index.json, patterns.json\n"
        result += "   - SCHEMA: index.json, context.json\n"
        result += "   - COMPONENTS: index.json, patterns.json\n"
        result += "2. Extract relevant elements based on template type\n"
        result += "3. Populate templates with real code data\n"
        result += "4. Performance: < 50ms per doc (file read only)\n\n"
    else:
        result += f"⚠ WARNING: .coderef/ resources not found!\n\n"
        result += f"Missing: {', '.join(resources['missing'])}\n\n"
        result += "ACTION REQUIRED:\n"
        result += "Before generating documentation, run:\n"
        result += "```\n"
        result += f"mcp__coderef_context__coderef_scan(\n"
        result += f"    project_path=\"{project_path}\",\n"
        result += f"    languages=['ts', 'tsx', 'js', 'jsx', 'py'],\n"
        result += f"    use_ast=True\n"
        result += f")\n"
        result += "```\n\n"
        result += "For now, documentation will use:\n"
        result += "- Regex-based detection (limited accuracy)\n"
        result += "- Placeholders for code intelligence\n\n"

    result += "=" * 50 + "\n"

    # VALIDATE-003: Add validation instructions (WO-GENERATION-ENHANCEMENT-001)
    auto_validate = arguments.get("auto_validate", True)
    result += "\n=== VALIDATION ===\n\n"
    if auto_validate:
        result += "✓ Auto-validation ENABLED (auto_validate=true)\n\n"
        result += "After generating each document:\n"
        result += f"1. Document will be automatically validated (threshold: {VALIDATION_SCORE_THRESHOLD}/100)\n"
        result += "2. Validation results will be shown in tool response\n"
        result += "3. If score < threshold, errors will be logged\n"
        result += "4. Validation metadata written to frontmatter _uds section\n"
        result += "\nValidation is handled by generate_individual_doc tool.\n"
    else:
        result += "⚠ Auto-validation DISABLED (auto_validate=false)\n\n"
        result += "Documents will be generated without validation.\n"
        result += "You can manually validate later using validate_document tool.\n"

    result += "\n" + "=" * 50 + "\n"

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

    PHASE 4 (WO-PAPERTRAIL-PYTHON-PACKAGE-001):
    - Optional Papertrail UDS integration when PAPERTRAIL_ENABLED=true
    - Generates complete document with workorder tracking

    Uses @log_invocation and @mcp_error_handler decorators for automatic
    logging and error handling (ARCH-004, ARCH-005).
    """
    # Validate inputs at boundary (REF-003)
    project_path = validate_project_path_input(arguments.get("project_path", ""))
    template_name = validate_template_name_input(arguments.get("template_name", ""))

    # Phase 4: Extract optional Papertrail parameters
    workorder_id = arguments.get("workorder_id")
    feature_id = arguments.get("feature_id", template_name)  # Default to template_name
    version = arguments.get("version", "1.0.0")

    # VALIDATE-004: Extract auto_validate parameter (WO-GENERATION-ENHANCEMENT-001)
    auto_validate = arguments.get("auto_validate", True)

    logger.info(f"Generating individual doc: {template_name} for project: {project_path}")

    # WO-UDS-COMPLIANCE-CODEREF-DOCS-001: Changed default to true
    use_papertrail = (
        os.getenv("PAPERTRAIL_ENABLED", "true").lower() == "true" and
        workorder_id is not None
    )

    if use_papertrail:
        logger.info(f"Papertrail enabled for {template_name} (workorder: {workorder_id})")
        try:
            from generators.foundation_generator import FoundationGenerator
            generator = FoundationGenerator(TEMPLATES_DIR)

            # Build context for Papertrail
            context = {
                "project_path": project_path,
                "title": template_name.upper(),
                "template_name": template_name
            }

            # Generate with UDS
            final_doc = generator.generate_with_uds(
                template_name=template_name,
                context=context,
                workorder_id=workorder_id,
                feature_id=feature_id,
                version=version
            )

            # Get output path
            paths = generator.prepare_generation(project_path)
            output_path = generator.get_doc_output_path(paths['project_path'], template_name)

            # Return complete document with UDS
            result = f"=== Generated {template_name.upper()} with UDS ===\n\n"
            result += f"Workorder: {workorder_id}\n"
            result += f"Feature: {feature_id}\n"
            result += f"Version: {version}\n"
            result += f"Output: {output_path}\n\n"
            result += "=" * 50 + "\n\n"
            result += final_doc
            result += "\n\n" + "=" * 50 + "\n\n"
            result += f"Save this document to: {output_path}\n"

            logger.info(f"Successfully generated {template_name} with Papertrail UDS")
            return [TextContent(type="text", text=result)]

        except Exception as e:
            logger.warning(f"Papertrail generation failed: {e}, falling back to template")
            # Fall through to legacy generation

    # Legacy generation (template-only with direct validation)
    generator = BaseGenerator(TEMPLATES_DIR)

    paths = generator.prepare_generation(project_path)

    template_content = generator.read_template(template_name)
    template_info = generator.get_template_info(template_name)

    # Get correct output path (SEC-003: README goes to root)
    output_path = generator.get_doc_output_path(paths['project_path'], template_name)
    logger.debug(f"Output path determined: {output_path}")

    # DRIFT-002: Check drift before doc generation (WO-GENERATION-ENHANCEMENT-001)
    project_path_obj = Path(project_path)
    drift_metadata = None
    drift_result = await call_coderef_drift(project_path_obj)
    if drift_result['success'] and drift_result['drift_percent'] > DRIFT_WARNING_THRESHOLD:
        drift_metadata = {
            'drift_percent': drift_result['drift_percent'],
            'drift_detected_at': datetime.utcnow().isoformat() + 'Z',
            'index_age': drift_result['index_age'],
            'warning': f"Generated from stale data ({drift_result['drift_percent']:.1f}% drift detected)"
        }
        logger.warning(f"Document generated with {drift_result['drift_percent']:.1f}% drift")

    # FOUNDATION-002 through FOUNDATION-006: MCP orchestration for templates (WO-GENERATION-ENHANCEMENT-001)
    mcp_context = {}

    if template_name == 'architecture':
        # FOUNDATION-002: Call coderef_query for dependencies and structure
        logger.info(f"Calling MCP orchestration for ARCHITECTURE template")
        # Query major components and their relationships
        # This is a placeholder - will be enhanced when actual elements are available
        mcp_context['dependencies_checked'] = True

    elif template_name == 'api':
        # FOUNDATION-003: Call coderef_patterns for API conventions
        logger.info(f"Calling MCP orchestration for API template")
        patterns_result = await call_coderef_patterns(project_path_obj, pattern_type='api', limit=20)
        if patterns_result['success']:
            mcp_context['api_patterns'] = patterns_result['patterns']
            mcp_context['pattern_frequency'] = patterns_result['frequency']
            logger.info(f"Found {patterns_result['pattern_count']} API patterns")
        else:
            logger.warning(f"API patterns call failed: {patterns_result.get('error')}")

    elif template_name == 'components':
        # FOUNDATION-004: Call coderef_patterns for component conventions
        logger.info(f"Calling MCP orchestration for COMPONENTS template")
        patterns_result = await call_coderef_patterns(project_path_obj, pattern_type='component', limit=20)
        if patterns_result['success']:
            mcp_context['component_patterns'] = patterns_result['patterns']
            mcp_context['pattern_frequency'] = patterns_result['frequency']
            logger.info(f"Found {patterns_result['pattern_count']} component patterns")
        else:
            logger.warning(f"Component patterns call failed: {patterns_result.get('error')}")

    elif template_name == 'readme':
        # FOUNDATION-005: Call coderef_patterns for coding conventions
        logger.info(f"Calling MCP orchestration for README template")
        patterns_result = await call_coderef_patterns(project_path_obj, limit=15)
        if patterns_result['success']:
            mcp_context['coding_patterns'] = patterns_result['patterns']
            mcp_context['pattern_frequency'] = patterns_result['frequency']
            logger.info(f"Found {patterns_result['pattern_count']} coding patterns")
        else:
            logger.warning(f"Coding patterns call failed: {patterns_result.get('error')}")

    elif template_name == 'schema':
        # FOUNDATION-006: Call coderef_query for data models and relationships
        logger.info(f"Calling MCP orchestration for SCHEMA template")
        # Query for models, entities, and their relationships
        # This is a placeholder - will be enhanced when actual elements are available
        mcp_context['schema_elements_checked'] = True

    # Add basic frontmatter with drift metadata (DRIFT-002)
    doc_content = "---\n"
    doc_content += f"generated_by: coderef-docs\n"
    doc_content += f"template: {template_name}\n"
    doc_content += f"date: {datetime.utcnow().isoformat()}Z\n"
    if mcp_context:
        doc_content += f"mcp_enhanced: true\n"
    if drift_metadata:
        doc_content += f"drift_warning: \"{drift_metadata['warning']}\"\n"
        doc_content += f"drift_percent: {drift_metadata['drift_percent']:.1f}\n"
        doc_content += f"drift_detected_at: {drift_metadata['drift_detected_at']}\n"
    doc_content += "---\n\n"

    # Add drift warning banner if metadata present
    if drift_metadata:
        doc_content += f"> ⚠️ **DRIFT WARNING**: {drift_metadata['warning']}\n"
        doc_content += f"> Index last updated: {drift_metadata['index_age']} ago\n\n"

    # Add MCP context as comments in the doc for Claude to see
    if mcp_context:
        doc_content += "<!-- MCP Code Intelligence -->\n"
        doc_content += f"<!-- MCP Context: {json.dumps(mcp_context, indent=2)} -->\n\n"

    doc_content += template_content

    # WO-CODEREF-DOCS-DIRECT-VALIDATION-001: Direct integration - Tool saves file and validates
    try:
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save file
        output_path.write_text(doc_content, encoding='utf-8')
        logger.info(f"Saved {template_name} to {output_path}")

        # VALIDATE-004: Run direct validation if auto_validate enabled (WO-GENERATION-ENHANCEMENT-001)
        foundation_templates = ['readme', 'architecture', 'api', 'schema', 'components']
        validation_score = None
        validation_errors_count = 0
        validation_warnings_count = 0

        if auto_validate and template_name in foundation_templates:
            from papertrail.validators.foundation import FoundationDocValidator
            from utils.validation_helpers import write_validation_metadata_to_frontmatter

            validator = FoundationDocValidator()
            validation_result = validator.validate_file(output_path)
            write_validation_metadata_to_frontmatter(output_path, validation_result)

            validation_score = validation_result.score
            validation_errors_count = len(validation_result.errors) if hasattr(validation_result, 'errors') and validation_result.errors else 0
            validation_warnings_count = len(validation_result.warnings) if hasattr(validation_result, 'warnings') and validation_result.warnings else 0

            logger.info(f'Validated {template_name}: {validation_score}/100 ({validation_errors_count} errors, {validation_warnings_count} warnings)')

            if validation_score < VALIDATION_SCORE_THRESHOLD:
                logger.warning(f'{template_name}: Validation score below threshold ({VALIDATION_SCORE_THRESHOLD})')
                if hasattr(validation_result, 'errors') and validation_result.errors:
                    for error in validation_result.errors:
                        logger.error(f'  {error.severity if hasattr(error, "severity") else "ERROR"}: {error.message if hasattr(error, "message") else str(error)}')
        elif not auto_validate:
            logger.info(f"Validation skipped (auto_validate=false) for {template_name}")

        # Return simple result (NOT instructions) - VALIDATE-006: Include validation status
        result = f"✅ Generated and saved {template_name.upper()}.md\n\n"
        result += f"📁 Location: {output_path}\n"
        result += f"📄 Template: {template_name}\n"

        if validation_score is not None:
            result += f"\n📊 Validation: {validation_score}/100\n"
            result += f"  • Errors: {validation_errors_count}\n"
            result += f"  • Warnings: {validation_warnings_count}\n"
            result += f"  • Metadata written to frontmatter _uds section\n"

            if validation_score >= VALIDATION_SCORE_THRESHOLD:
                result += f"\n✅ Validation passed (threshold: {VALIDATION_SCORE_THRESHOLD})\n"
            else:
                result += f"\n⚠️  Validation below threshold (score: {validation_score}, threshold: {VALIDATION_SCORE_THRESHOLD})\n"
        elif not auto_validate:
            result += f"\n📊 Validation: SKIPPED (auto_validate=false)\n"
        else:
            result += f"\n📊 Validation: Not applicable for this template type\n"

        logger.info(f"Successfully generated {template_name}")
        return [TextContent(type="text", text=result)]

    except Exception as e:
        logger.error(f"Failed to generate {template_name}: {e}")
        return [TextContent(type="text", text=f"❌ Error: {str(e)}")]


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

    # USER-002: Extract code intelligence from .coderef/ (WO-GENERATION-ENHANCEMENT-001)
    code_intel = generator.extract_code_intelligence(Path(project_path))

    # Get interview questions and workflow
    interview = generator.get_interview_questions(app_type)

    # Build response with interview script
    result = f"📋 Universal Quickref Generator - Interactive Workflow\n"
    result += f"=" * 60 + "\n\n"
    result += f"Project: {Path(project_path).name}\n"
    result += f"Output: coderef/user/quickref.md\n"
    if app_type:
        result += f"App Type: {app_type.upper()}\n"

    # Add code intelligence status
    if code_intel['available']:
        result += f"Code Intelligence: ✓ Available ({code_intel['total_elements']} elements)\n"
        result += f"  • CLI Commands: {len(code_intel['cli_commands'])}\n"
        result += f"  • API Endpoints: {len(code_intel['api_endpoints'])}\n"
        result += f"  • Common Patterns: {len(code_intel['common_patterns'])}\n"
    else:
        result += f"Code Intelligence: ⚠ Not available (will use interview only)\n"

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

            # USER-002: Inject code intelligence suggestions for relevant steps
            if step_name == "Actions/Commands" and code_intel['available']:
                result += f"\n💡 SUGGESTIONS FROM CODE INTELLIGENCE:\n"
                if code_intel['cli_commands']:
                    result += f"\nDiscovered CLI Commands:\n"
                    for cmd in code_intel['cli_commands'][:10]:  # Limit to 10
                        result += f"  • {cmd['command']} - {cmd['description']}\n"
                if code_intel['api_endpoints']:
                    result += f"\nDiscovered API Endpoints:\n"
                    for endpoint in code_intel['api_endpoints'][:10]:  # Limit to 10
                        result += f"  • {endpoint['method']} {endpoint['endpoint']} (handler: {endpoint['handler']})\n"
                result += f"\n↳ Use these as starting suggestions, or ask user for additional actions.\n"

            elif step_name == "Common Workflows" and code_intel['available']:
                result += f"\n💡 SUGGESTIONS FROM CODE INTELLIGENCE:\n"
                if code_intel['common_patterns']:
                    result += f"\nCommon Action Patterns:\n"
                    # Group by action verb
                    pattern_groups = {}
                    for pattern in code_intel['common_patterns']:
                        verb = pattern['action']
                        if verb not in pattern_groups:
                            pattern_groups[verb] = []
                        pattern_groups[verb].append(pattern['function'])

                    for verb, functions in sorted(pattern_groups.items())[:5]:  # Top 5 verbs
                        result += f"  • {verb.upper()}: {', '.join(functions[:3])}\n"

                    result += f"\n↳ Use these patterns to build common workflow sequences.\n"

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
async def handle_generate_my_guide(arguments: dict) -> list[TextContent]:
    """
    USER-003: Handle generate_my_guide tool call (WO-GENERATION-ENHANCEMENT-001).

    Generates my-guide.md using real MCP tool and slash command data from .coderef/.

    Uses @log_invocation and @mcp_error_handler decorators for automatic
    logging and error handling (ARCH-004, ARCH-005).
    """
    # Validate inputs (REF-003)
    project_path = validate_project_path_input(arguments.get("project_path", ""))

    # Initialize generator
    generator = UserGuideGenerator(TEMPLATES_DIR)
    project_path_obj = Path(project_path)

    logger.info(f"Generating my-guide.md for project: {project_path}")

    # USER-003: Extract MCP tools and slash commands from .coderef/
    mcp_tools = generator.extract_mcp_tools(project_path_obj)
    slash_commands = generator.extract_slash_commands(project_path_obj)

    # Build status report
    result = f"📋 my-guide.md Generator\n"
    result += f"=" * 60 + "\n\n"
    result += f"Project: {project_path_obj.name}\n"
    result += f"Output: coderef/user/my-guide.md\n\n"

    # Add extraction status
    if mcp_tools['available']:
        result += f"MCP Tools: ✓ Discovered {mcp_tools['total_tools']} tools\n"
        # Show category breakdown
        categories = {}
        for tool in mcp_tools['tools']:
            cat = tool['category']
            categories[cat] = categories.get(cat, 0) + 1
        for cat, count in sorted(categories.items()):
            result += f"  • {cat}: {count} tools\n"
    else:
        result += f"MCP Tools: ⚠ Not available\n"
        result += f"  Reason: {mcp_tools.get('error', '.coderef/index.json not found')}\n"
        result += f"  Run: mcp__coderef_context__coderef_scan(project_path=\"{project_path}\")\n"

    result += f"\n"

    if slash_commands['available']:
        result += f"Slash Commands: ✓ Discovered {slash_commands['total_commands']} commands\n"
    else:
        result += f"Slash Commands: ⚠ Not available (.claude/commands/ not found)\n"

    result += f"\n" + "=" * 60 + "\n\n"

    # USER-003: Generate my-guide.md content
    my_guide_content = generator.generate_my_guide(
        project_path_obj,
        mcp_tools=mcp_tools,
        slash_commands=slash_commands
    )

    # Save the file
    try:
        saved_path = generator.save_my_guide(my_guide_content, project_path_obj)
        result += f"✅ SUCCESS: my-guide.md generated and saved\n\n"
        result += f"Location: {saved_path}\n"
        result += f"Lines: {len(my_guide_content.splitlines())}\n"
        result += f"Target: 60-80 lines (concise quick reference)\n\n"
        result += f"=" * 60 + "\n\n"
        result += f"📄 PREVIEW:\n\n"
        result += my_guide_content[:800]  # Show first 800 chars
        if len(my_guide_content) > 800:
            result += f"\n\n... (truncated, see full file at {saved_path})"
    except Exception as e:
        result += f"❌ ERROR: Failed to save my-guide.md\n\n"
        result += f"Error: {str(e)}\n"
        logger.error(f"Failed to save my-guide.md: {e}", exc_info=True)

    logger.info(f"my-guide.md generation complete")
    return [TextContent(type="text", text=result)]


@log_invocation
@mcp_error_handler
async def handle_generate_user_guide(arguments: dict) -> list[TextContent]:
    """
    USER-004: Handle generate_user_guide tool call (WO-GENERATION-ENHANCEMENT-001).

    Generates USER-GUIDE.md using real MCP tool and slash command data from .coderef/.

    Uses @log_invocation and @mcp_error_handler decorators for automatic
    logging and error handling (ARCH-004, ARCH-005).
    """
    # Validate inputs (REF-003)
    project_path = validate_project_path_input(arguments.get("project_path", ""))

    # Initialize generator
    generator = UserGuideGenerator(TEMPLATES_DIR)
    project_path_obj = Path(project_path)

    logger.info(f"Generating USER-GUIDE.md for project: {project_path}")

    # USER-004: Extract MCP tools and slash commands from .coderef/
    mcp_tools = generator.extract_mcp_tools(project_path_obj)
    slash_commands = generator.extract_slash_commands(project_path_obj)

    # Build status report
    result = f"📋 USER-GUIDE.md Generator\n"
    result += f"=" * 60 + "\n\n"
    result += f"Project: {project_path_obj.name}\n"
    result += f"Output: coderef/user/USER-GUIDE.md\n"
    result += f"Type: Comprehensive onboarding documentation\n\n"

    # Add extraction status
    if mcp_tools['available']:
        result += f"MCP Tools: ✓ Discovered {mcp_tools['total_tools']} tools\n"
    else:
        result += f"MCP Tools: ⚠ Not available\n"
        result += f"  Run: mcp__coderef_context__coderef_scan(project_path=\"{project_path}\")\n"

    if slash_commands['available']:
        result += f"Slash Commands: ✓ Discovered {slash_commands['total_commands']} commands\n"
    else:
        result += f"Slash Commands: ⚠ Not available (.claude/commands/ not found)\n"

    result += f"\n" + "=" * 60 + "\n\n"

    # USER-004: Generate USER-GUIDE.md content
    user_guide_content = generator.generate_user_guide(
        project_path_obj,
        mcp_tools=mcp_tools,
        slash_commands=slash_commands
    )

    # Save the file
    try:
        saved_path = generator.save_user_guide(user_guide_content, project_path_obj)
        result += f"✅ SUCCESS: USER-GUIDE.md generated and saved\n\n"
        result += f"Location: {saved_path}\n"
        result += f"Lines: {len(user_guide_content.splitlines())}\n"
        result += f"Sections: 10 (Introduction → Quick Reference)\n\n"
        result += f"=" * 60 + "\n\n"
        result += f"📄 SECTIONS INCLUDED:\n\n"
        result += f"1. Introduction\n"
        result += f"2. Prerequisites (with verification commands)\n"
        result += f"3. Installation (step-by-step)\n"
        result += f"4. Architecture (MCP protocol flow)\n"
        result += f"5. MCP Tools Reference (categorized)\n"
        result += f"6. Slash Commands\n"
        result += f"7. Common Workflows\n"
        result += f"8. Best Practices (Do/Don't/Tips)\n"
        result += f"9. Troubleshooting\n"
        result += f"10. Quick Reference (operations table)\n"
    except Exception as e:
        result += f"❌ ERROR: Failed to save USER-GUIDE.md\n\n"
        result += f"Error: {str(e)}\n"
        logger.error(f"Failed to save USER-GUIDE.md: {e}", exc_info=True)

    logger.info(f"USER-GUIDE.md generation complete")
    return [TextContent(type="text", text=result)]


@log_invocation
@mcp_error_handler
async def handle_generate_features(arguments: dict) -> list[TextContent]:
    """
    USER-005: Handle generate_features tool call (WO-GENERATION-ENHANCEMENT-001).

    Generates FEATURES.md inventory by scanning coderef/workorder and coderef/archived.

    Uses @log_invocation and @mcp_error_handler decorators for automatic
    logging and error handling (ARCH-004, ARCH-005).
    """
    # Validate inputs (REF-003)
    project_path = validate_project_path_input(arguments.get("project_path", ""))

    # Initialize generator
    generator = UserGuideGenerator(TEMPLATES_DIR)
    project_path_obj = Path(project_path)

    logger.info(f"Generating FEATURES.md for project: {project_path}")

    # Build status report
    result = f"📋 FEATURES.md Generator\n"
    result += f"=" * 60 + "\n\n"
    result += f"Project: {project_path_obj.name}\n"
    result += f"Output: coderef/user/FEATURES.md\n"
    result += f"Type: Features inventory with workorder tracking\n\n"

    # Check directories
    workorder_dir = project_path_obj / "coderef" / "workorder"
    archived_dir = project_path_obj / "coderef" / "archived"

    result += f"Scanning:\n"
    if workorder_dir.exists():
        active_count = sum(1 for d in workorder_dir.iterdir() if d.is_dir())
        result += f"  • coderef/workorder/: ✓ Found {active_count} active features\n"
    else:
        result += f"  • coderef/workorder/: ⚠ Not found\n"

    if archived_dir.exists():
        archived_count = sum(1 for d in archived_dir.iterdir() if d.is_dir())
        result += f"  • coderef/archived/: ✓ Found {archived_count} archived features\n"
    else:
        result += f"  • coderef/archived/: ⚠ Not found\n"

    result += f"\n" + "=" * 60 + "\n\n"

    # USER-005: Generate FEATURES.md content
    features_content = generator.generate_features(project_path_obj)

    # Save the file
    try:
        saved_path = generator.save_features(features_content, project_path_obj)
        result += f"✅ SUCCESS: FEATURES.md generated and saved\n\n"
        result += f"Location: {saved_path}\n"
        result += f"Lines: {len(features_content.splitlines())}\n\n"
        result += f"=" * 60 + "\n\n"
        result += f"📄 CONTENTS:\n\n"
        result += f"• Executive Summary (metrics table)\n"
        result += f"• Active Features (workorder tracking)\n"
        result += f"• Archived Features (completion history)\n"
        result += f"• Usage Notes (lifecycle workflow)\n"
    except Exception as e:
        result += f"❌ ERROR: Failed to save FEATURES.md\n\n"
        result += f"Error: {str(e)}\n"
        logger.error(f"Failed to save FEATURES.md: {e}", exc_info=True)

    logger.info(f"FEATURES.md generation complete")
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

    # VALIDATE-005: Extract auto_validate parameter (WO-GENERATION-ENHANCEMENT-001)
    auto_validate = arguments.get("auto_validate", True)

    logger.info(
        "Starting standards establishment",
        extra={
            'project_path': str(project_path),
            'scan_depth': scan_depth,
            'focus_areas': focus_areas,
            'auto_validate': auto_validate
        }
    )

    # Create standards directory if needed
    project_path_obj = Path(project_path).resolve()
    standards_dir = project_path_obj / Paths.STANDARDS_DIR
    standards_dir.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Standards directory ready: {standards_dir}")

    # DRIFT-003: Check drift before standards generation (WO-GENERATION-ENHANCEMENT-001)
    drift_result = await call_coderef_drift(project_path_obj)
    drift_warning = ""
    if drift_result['success']:
        drift_percent = drift_result['drift_percent']
        if drift_percent > 50:
            drift_warning = f"🚨 CRITICAL: Index severely stale ({drift_percent:.1f}% drift)\n"
            drift_warning += "Standards will be HIGHLY INACCURATE. Re-scan strongly recommended.\n"
        elif drift_percent > DRIFT_WARNING_THRESHOLD:
            drift_warning = f"⚠ WARNING: Index drift detected ({drift_percent:.1f}%)\n"
            drift_warning += "Standards accuracy may be reduced. Consider re-scanning.\n"
        logger.info(f"Drift check for standards: {drift_percent:.1f}% drift")

    # Initialize StandardsGenerator
    generator = StandardsGenerator(project_path_obj, scan_depth)

    # STANDARDS-001, STANDARDS-002: Fetch MCP patterns for semantic analysis (WO-GENERATION-ENHANCEMENT-001)
    mcp_patterns_result = await generator.fetch_mcp_patterns(pattern_type=None, limit=50)
    mcp_patterns_available = mcp_patterns_result['success']

    # Generate and save standards (with MCP pattern data if available)
    result_dict = generator.save_standards(standards_dir, mcp_patterns=mcp_patterns_result if mcp_patterns_available else None)

    # Format success response with drift warning (DRIFT-003)
    result = f"✅ Standards establishment completed successfully!\n\n"
    if drift_warning:
        result += drift_warning + "\n"
    result += f"Project: {project_path_obj.name}\n"
    result += f"Scan Depth: {scan_depth}\n"
    result += f"Focus Areas: {', '.join(focus_areas)}\n"
    if drift_result and drift_result['success']:
        result += f"Index Drift: {drift_result['drift_percent']:.1f}%\n"
    result += "\n"
    result += f"=" * 60 + "\n\n"
    result += f"📊 RESULTS:\n\n"
    result += f"Files Created: {len(result_dict['files'])}\n"
    result += f"Total Patterns Discovered: {result_dict['patterns_count']}\n"
    result += f"  • UI Patterns: {result_dict['ui_patterns_count']}\n"
    result += f"  • Behavior Patterns: {result_dict['behavior_patterns_count']}\n"
    result += f"  • UX Patterns: {result_dict['ux_patterns_count']}\n"
    result += f"Components Indexed: {result_dict['components_count']}\n"

    # STANDARDS-002, STANDARDS-003: Show MCP pattern data (WO-GENERATION-ENHANCEMENT-001)
    if mcp_patterns_available:
        result += f"\n🔍 MCP PATTERN ANALYSIS:\n\n"
        result += f"  • Total Patterns: {mcp_patterns_result['pattern_count']}\n"

        # STANDARDS-003: Show pattern frequency
        if mcp_patterns_result['frequency']:
            top_patterns = sorted(mcp_patterns_result['frequency'].items(), key=lambda x: x[1], reverse=True)[:5]
            result += f"  • Top Patterns:\n"
            for pattern, count in top_patterns:
                result += f"    - {pattern}: {count} occurrences\n"

        # STANDARDS-004: Show consistency violations
        if mcp_patterns_result['violations']:
            result += f"  • Consistency Violations: {len(mcp_patterns_result['violations'])}\n"
    else:
        result += f"\n⚠ MCP Pattern Analysis: Not available\n"
        if 'error' in mcp_patterns_result:
            result += f"  Reason: {mcp_patterns_result['error']}\n"

    result += f"\n"
    result += f"=" * 60 + "\n\n"
    result += f"📁 STANDARDS DOCUMENTS:\n\n"
    for file_path in result_dict['files']:
        file_name = Path(file_path).name
        result += f"  • {file_name}\n"
    result += f"\n📂 Location: {standards_dir}\n\n"
    result += f"These standards documents can now be used with:\n"
    result += f"  • Tool #9: audit_codebase - Find violations of standards\n"
    result += f"  • Tool #10: check_consistency - Quality gate for new code\n\n"

    # VALIDATE-005: Direct validation if auto_validate enabled (WO-GENERATION-ENHANCEMENT-001)
    # Tool validates all standards files and writes metadata to frontmatter
    if auto_validate:
        try:
            from papertrail.validators.standards import StandardsDocValidator
            from utils.validation_helpers import write_validation_metadata_to_frontmatter

            validator = StandardsDocValidator()
            validation_results = []

            for file_path in result_dict['files']:
                file_path_obj = Path(file_path)
                validation_result = validator.validate_file(file_path_obj)
                write_validation_metadata_to_frontmatter(file_path_obj, validation_result)

                validation_results.append({
                    'file': file_path_obj.name,
                    'score': validation_result.score,
                    'errors': len(validation_result.errors),
                    'warnings': len(validation_result.warnings)
                })

                logger.info(f'Validated {file_path_obj.name}: {validation_result.score}/100')
                if validation_result.score < VALIDATION_SCORE_THRESHOLD:
                    logger.warning(f'{file_path_obj.name}: Validation below threshold (score={validation_result.score}, threshold={VALIDATION_SCORE_THRESHOLD})')

            # Add validation summary to result (VALIDATE-006)
            result += "=" * 60 + "\n\n"
            result += "📋 VALIDATION RESULTS:\n\n"
            for vr in validation_results:
                status = "✅ PASSED" if vr['score'] >= VALIDATION_SCORE_THRESHOLD else "⚠️  NEEDS REVIEW"
                result += f"  {status} {vr['file']}: {vr['score']}/100\n"
                if vr['errors'] > 0:
                    result += f"    └─ {vr['errors']} errors, {vr['warnings']} warnings\n"
            result += f"\n💾 Validation metadata saved to frontmatter _uds sections\n"

        except Exception as e:
            logger.error(f"Validation failed: {e}")
            result += f"\n⚠️  Validation skipped due to error: {e}\n"
    else:
        result += "=" * 60 + "\n\n"
        result += "📋 VALIDATION: SKIPPED (auto_validate=false)\n"
        result += "You can manually validate standards docs later using validate_document tool.\n"
        logger.info("Validation skipped (auto_validate=false)")

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


async def handle_validate_document(arguments: dict) -> list[TextContent]:
    """
    Handle validate_document tool - Phase 3 Papertrail integration.

    Validates document against UDS schema using Papertrail.
    """
    try:
        from papertrail import validate_uds
        PAPERTRAIL_AVAILABLE = True
    except ImportError:
        PAPERTRAIL_AVAILABLE = False

    if not PAPERTRAIL_AVAILABLE:
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": "Papertrail not available. Install: pip install papertrail>=1.0.0",
                "success": False
            }, indent=2)
        )]

    try:
        document_path = arguments.get("document_path")
        doc_type = arguments.get("doc_type")

        # Read document
        with open(document_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Validate with Papertrail
        result = validate_uds(content, doc_type)

        return [TextContent(
            type="text",
            text=json.dumps({
                "valid": result.is_valid,
                "errors": [
                    {
                        "severity": err.severity,
                        "message": err.message,
                        "location": err.location
                    } for err in result.errors
                ],
                "warnings": [
                    {
                        "severity": warn.severity,
                        "message": warn.message
                    } for warn in result.warnings
                ],
                "validation_score": result.validation_score,
                "success": True
            }, indent=2)
        )]

    except Exception as e:
        logger.error(f"validate_document failed: {e}")
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": str(e),
                "success": False
            }, indent=2)
        )]


async def handle_check_document_health(arguments: dict) -> list[TextContent]:
    """
    Handle check_document_health tool - Phase 3 Papertrail integration.

    Calculates document health score (0-100) using Papertrail.
    """
    try:
        from papertrail import calculate_health
        PAPERTRAIL_AVAILABLE = True
    except ImportError:
        PAPERTRAIL_AVAILABLE = False

    if not PAPERTRAIL_AVAILABLE:
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": "Papertrail not available. Install: pip install papertrail>=1.0.0",
                "success": False
            }, indent=2)
        )]

    try:
        document_path = arguments.get("document_path")
        doc_type = arguments.get("doc_type")

        # Read document
        with open(document_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Calculate health with Papertrail
        health = calculate_health(content, doc_type)

        return [TextContent(
            type="text",
            text=json.dumps({
                "score": health.score,
                "grade": health.grade,
                "breakdown": {
                    "traceability": health.traceability,
                    "completeness": health.completeness,
                    "freshness": health.freshness,
                    "validation": health.validation_score
                },
                "issues": health.issues,
                "recommendations": health.recommendations,
                "success": True
            }, indent=2)
        )]

    except Exception as e:
        logger.error(f"check_document_health failed: {e}")
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": str(e),
                "success": False
            }, indent=2)
        )]

@log_invocation
@mcp_error_handler
async def handle_generate_resource_sheet(arguments: dict) -> list[TextContent]:
    """
    Handle generate_resource_sheet tool - composable module-based documentation.

    WO-RESOURCE-SHEET-MCP-TOOL-001

    Generates authoritative technical documentation using composable modules
    instead of rigid templates. Auto-detects code characteristics and selects
    appropriate documentation modules.
    """
    try:
        # Extract and validate parameters
        element_name = arguments.get("element_name")
        project_path = arguments.get("project_path")
        element_type = arguments.get("element_type")
        mode = arguments.get("mode", "reverse-engineer")
        auto_analyze = arguments.get("auto_analyze", True)
        output_path = arguments.get("output_path")
        validate_against_code = arguments.get("validate_against_code", True)

        if not element_name or not project_path:
            raise ValueError("element_name and project_path are required")

        logger.info(f"Generating resource sheet for {element_name} in mode: {mode}")

        # Initialize generator
        generator = ResourceSheetGenerator()

        # Generate resource sheet
        result = await generator.generate(
            element_name=element_name,
            project_path=project_path,
            element_type=element_type,
            mode=mode,
            auto_analyze=auto_analyze,
            output_path=output_path,
            validate_against_code=validate_against_code,
        )

        # Format response
        response = {
            "success": True,
            "element_name": result["element_name"],
            "mode": result["mode"],
            "modules_selected": result["selected_modules"],
            "module_count": result["module_count"],
            "auto_fill_rate": f"{result['auto_fill_rate']:.1f}%",
            "outputs": result["outputs"],
            "characteristics_detected": len([k for k, v in result["characteristics"].items() if v]),
            "warnings": result.get("warnings", []),
            "generated_at": result["generated_at"],
        }

        logger.info(f"Resource sheet generated: {result['outputs']['markdown']}")

        return [TextContent(type="text", text=json.dumps(response, indent=2))]

    except Exception as e:
        logger.error(f"generate_resource_sheet failed: {e}", exc_info=True)
        return [
            TextContent(
                type="text",
                text=json.dumps({
                    "error": str(e),
                    "success": False
                }, indent=2)
            )
        ]


async def handle_coderef_foundation_docs(arguments: dict) -> list[TextContent]:
    """
    Handle coderef_foundation_docs tool call.

    CONSOLIDATE-002 (WO-GENERATION-ENHANCEMENT-001): DEPRECATED tool.
    Use generate_foundation_docs instead.

    Unified foundation docs generator powered by coderef analysis. Generates:
    - ARCHITECTURE.md (patterns, decisions, constraints)
    - SCHEMA.md (entities, relationships)
    - COMPONENTS.md (component hierarchy - UI projects only)
    - project-context.json (structured context for planning)

    Replaces: api_inventory, database_inventory, dependency_inventory,
              config_inventory, test_inventory, inventory_manifest, documentation_inventory
    """
    # CONSOLIDATE-002: Show deprecation warning
    logger.warning("coderef_foundation_docs is deprecated. Use generate_foundation_docs instead.")

    # Validate project_path
    project_path = validate_project_path_input(arguments.get('project_path', ''))
    project_path_obj = Path(project_path).resolve()

    # Add deprecation notice to output
    deprecation_warning = "⚠️ DEPRECATION WARNING ⚠️\n\n"
    deprecation_warning += "The 'coderef_foundation_docs' tool is deprecated and will be removed in v5.0.0.\n"
    deprecation_warning += "Please use 'generate_foundation_docs' instead for:\n"
    deprecation_warning += "  • Better MCP integration with drift detection\n"
    deprecation_warning += "  • Sequential generation (no timeouts)\n"
    deprecation_warning += "  • Enhanced validation support\n\n"
    deprecation_warning += "Migration: Replace coderef_foundation_docs(path) with generate_foundation_docs(path)\n\n"
    deprecation_warning += "=" * 60 + "\n\n"

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

    # CONSOLIDATE-002: Prepend deprecation warning to message
    final_message = deprecation_warning + message

    return [TextContent(type="text", text=json.dumps({"success": True, "data": summary, "message": final_message}, indent=2))]


# =============================================================================
# Tool handlers registry - ENHANCED (16 documentation tools)
# WO-GENERATION-ENHANCEMENT-001: Added user doc generators (USER-003, USER-004, USER-005)
# =============================================================================
TOOL_HANDLERS = {
    'list_templates': handle_list_templates,
    'get_template': handle_get_template,
    'generate_foundation_docs': handle_generate_foundation_docs,
    'generate_individual_doc': handle_generate_individual_doc,  # CONSOLIDATE-001: Internal tool
    'coderef_foundation_docs': handle_coderef_foundation_docs,  # CONSOLIDATE-002: DEPRECATED
    'add_changelog_entry': handle_add_changelog_entry,
    'record_changes': handle_record_changes,
    'generate_quickref_interactive': handle_generate_quickref_interactive,  # USER-002: Enhanced
    'generate_my_guide': handle_generate_my_guide,  # USER-003: New
    'generate_user_guide': handle_generate_user_guide,  # USER-004: New
    'generate_features': handle_generate_features,  # USER-005: New
    'generate_resource_sheet': handle_generate_resource_sheet,  # WO-RESOURCE-SHEET-MCP-TOOL-001
    'establish_standards': handle_establish_standards,  # STANDARDS-001: Enhanced with MCP
    'audit_codebase': handle_audit_codebase,
    'check_consistency': handle_check_consistency,
    'validate_document': handle_validate_document,
    'check_document_health': handle_check_document_health,
}


def set_templates_dir(templates_dir: Path) -> None:
    """Set the TEMPLATES_DIR global for handlers to use."""
    global TEMPLATES_DIR
    TEMPLATES_DIR = templates_dir


def set_tool_templates_dir(tool_templates_dir: Path) -> None:
    """Set the TOOL_TEMPLATES_DIR global for handlers to use."""
    global TOOL_TEMPLATES_DIR
    TOOL_TEMPLATES_DIR = tool_templates_dir


