"""
Input validation functions for MCP tool boundaries (REF-003).

Validates inputs at the tool boundary before passing to generators,
enabling fail-fast error handling with clear messages.
"""

import re
from constants import (
    MAX_PATH_LENGTH, VERSION_PATTERN, TemplateNames, ChangeType, Severity,
    ScanDepth, FocusArea, AuditSeverity, AuditScope
)

__all__ = [
    'validate_project_path_input',
    'validate_version_format',
    'validate_template_name_input',
    'validate_changelog_inputs',
    'validate_scan_depth',
    'validate_focus_areas',
    'validate_severity_filter',
    'validate_audit_scope',
    'validate_severity_threshold',
    'validate_file_list',
    # Planning workflow validation
    'VALID_TEMPLATE_SECTIONS',
    'validate_section_name',
    'validate_plan_file_path',
    'validate_plan_json_structure',
    'validate_feature_name_input',
    # Workorder tracking validation
    'validate_workorder_id',
    # Risk assessment validation
    'validate_risk_inputs',
    # Context Expert validation
    'validate_resource_path',
    'validate_expert_id',
    'validate_resource_type',
    'validate_expert_domain',
    'validate_expert_capabilities',
    'validate_context_expert_inputs',
]


def validate_project_path_input(path: str) -> str:
    """
    Validate project path at tool boundary.

    Args:
        path: Project path string to validate

    Returns:
        Validated path string

    Raises:
        ValueError: If path is invalid
    """
    if not path or not isinstance(path, str):
        raise ValueError('project_path must be a non-empty string')

    if len(path) > MAX_PATH_LENGTH:
        raise ValueError(f'project_path too long (max {MAX_PATH_LENGTH} characters)')

    # Check for null bytes (security)
    if '\x00' in path:
        raise ValueError('project_path contains null bytes')

    return path


def validate_version_format(version: str) -> str:
    """
    Validate semantic version format.

    Args:
        version: Version string to validate (e.g., '1.0.2')

    Returns:
        Validated version string

    Raises:
        ValueError: If version format is invalid
    """
    if not version or not isinstance(version, str):
        raise ValueError('version must be a non-empty string')

    if not re.match(VERSION_PATTERN, version):
        raise ValueError(
            f'Invalid version format: {version}. '
            f'Expected format: MAJOR.MINOR.PATCH (e.g., 1.0.2)'
        )

    return version


def validate_template_name_input(template_name: str) -> str:
    """
    Validate template name at tool boundary.

    Args:
        template_name: Template name to validate

    Returns:
        Validated template name

    Raises:
        ValueError: If template name is invalid
    """
    if not template_name or not isinstance(template_name, str):
        raise ValueError('template_name must be a non-empty string')

    # Use enum for valid templates (QUA-003)
    valid_templates = [t.value for t in TemplateNames]

    if template_name not in valid_templates:
        raise ValueError(
            f'Invalid template: {template_name}. '
            f'Valid options: {", ".join(valid_templates)}'
        )

    return template_name


def validate_changelog_inputs(
    version: str,
    change_type: str,
    severity: str,
    title: str,
    description: str,
    files: list,
    reason: str,
    impact: str
) -> dict:
    """
    Validate all required inputs for changelog entry.

    Args:
        version: Version number
        change_type: Type of change
        severity: Severity level
        title: Change title
        description: Change description
        files: List of affected files
        reason: Reason for change
        impact: Impact description

    Returns:
        Dictionary of validated inputs

    Raises:
        ValueError: If any input is invalid
    """
    # Validate version
    validate_version_format(version)

    # Validate change_type (QUA-003)
    valid_types = [t.value for t in ChangeType]
    if change_type not in valid_types:
        raise ValueError(
            f'Invalid change_type: {change_type}. '
            f'Valid options: {", ".join(valid_types)}'
        )

    # Validate severity (QUA-003)
    valid_severities = [s.value for s in Severity]
    if severity not in valid_severities:
        raise ValueError(
            f'Invalid severity: {severity}. '
            f'Valid options: {", ".join(valid_severities)}'
        )

    # Validate required string fields
    if not title or not isinstance(title, str):
        raise ValueError('title must be a non-empty string')

    if not description or not isinstance(description, str):
        raise ValueError('description must be a non-empty string')

    if not reason or not isinstance(reason, str):
        raise ValueError('reason must be a non-empty string')

    if not impact or not isinstance(impact, str):
        raise ValueError('impact must be a non-empty string')

    # Validate files list
    if not files or not isinstance(files, list):
        raise ValueError('files must be a non-empty list')

    if not all(isinstance(f, str) for f in files):
        raise ValueError('files must contain only strings')

    return {
        'version': version,
        'change_type': change_type,
        'severity': severity,
        'title': title,
        'description': description,
        'files': files,
        'reason': reason,
        'impact': impact
    }


# Standards Validation Functions (INFRA-007)

def validate_scan_depth(scan_depth: str) -> str:
    """
    Validate scan_depth parameter using ScanDepth enum.

    Args:
        scan_depth: Analysis depth ('quick', 'standard', or 'deep')

    Returns:
        Validated scan_depth string

    Raises:
        ValueError: If scan_depth is not a valid option
    """
    valid_depths = [d.value for d in ScanDepth]  # Use enum instead of hardcoded list (REF-002)
    if scan_depth not in valid_depths:
        raise ValueError(
            f"Invalid scan_depth: {scan_depth}. "
            f"Must be one of: {', '.join(valid_depths)}"
        )
    return scan_depth


def validate_focus_areas(focus_areas: list) -> list:
    """
    Validate focus_areas parameter using FocusArea enum.

    Args:
        focus_areas: List of areas to analyze

    Returns:
        Validated focus_areas list

    Raises:
        ValueError: If any focus_area is not valid
    """
    if not isinstance(focus_areas, list):
        raise ValueError("focus_areas must be a list")

    valid_areas = [a.value for a in FocusArea]  # Use enum instead of hardcoded list (REF-002)
    for area in focus_areas:
        if area not in valid_areas:
            raise ValueError(
                f"Invalid focus_area: {area}. "
                f"Must be one of: {', '.join(valid_areas)}"
            )
    return focus_areas


# Audit Validation Functions (INFRA-007 Tool #9)

def validate_severity_filter(severity: str) -> str:
    """
    Validate severity_filter parameter using AuditSeverity enum.

    Args:
        severity: Severity level to filter by ('critical', 'major', 'minor', or 'all')

    Returns:
        Validated severity string

    Raises:
        ValueError: If severity is not a valid option
    """
    valid_severities = [s.value for s in AuditSeverity]  # Use enum instead of hardcoded list (REF-002)
    if severity not in valid_severities:
        raise ValueError(
            f"Invalid severity_filter: {severity}. "
            f"Must be one of: {', '.join(valid_severities)}"
        )
    return severity


def validate_audit_scope(scope: list) -> list:
    """
    Validate audit scope parameter using AuditScope enum.

    Args:
        scope: List of audit areas to scan

    Returns:
        Validated scope list

    Raises:
        ValueError: If any scope value is not valid
    """
    if not isinstance(scope, list):
        raise ValueError("scope must be a list")

    valid_scopes = [s.value for s in AuditScope]  # Use enum instead of hardcoded list (REF-002)
    for scope_item in scope:
        if scope_item not in valid_scopes:
            raise ValueError(
                f"Invalid scope value: {scope_item}. "
                f"Must be one of: {', '.join(valid_scopes)}"
            )
    return scope


# Consistency Checker Validation Functions (INFRA-007 Tool #10)

def validate_severity_threshold(threshold: str) -> str:
    """
    Validate severity_threshold parameter using SeverityThreshold enum.

    Args:
        threshold: Severity threshold ('critical', 'major', or 'minor')

    Returns:
        Validated threshold string

    Raises:
        ValueError: If threshold is not a valid option
    """
    from constants import SeverityThreshold  # Import here to avoid circular dependency
    valid_thresholds = SeverityThreshold.values()
    if threshold not in valid_thresholds:
        raise ValueError(
            f"Invalid severity_threshold: {threshold}. "
            f"Must be one of: {', '.join(valid_thresholds)}"
        )
    return threshold


def validate_file_list(files: list) -> list:
    """
    Validate file list parameter for check_consistency tool.

    Args:
        files: List of file paths (relative to project root)

    Returns:
        Validated files list

    Raises:
        ValueError: If files list is invalid, contains absolute paths, or has path traversal
    """
    from pathlib import Path  # Import Path for path validation

    if not isinstance(files, list):
        raise ValueError("files must be a list")

    for file_path in files:
        if not isinstance(file_path, str):
            raise ValueError(f"All file paths must be strings, got: {type(file_path).__name__}")

        # Check for absolute paths (security - SEC-001)
        if Path(file_path).is_absolute():
            raise ValueError(
                f"File paths must be relative to project_path, got absolute path: {file_path}"
            )

        # Check for path traversal (security - SEC-001)
        if '..' in file_path:
            raise ValueError(
                f"Path traversal detected in file path: {file_path}"
            )

    return files


# Planning Workflow System Validation Functions

# Valid template sections - exported for reuse (single source of truth)
VALID_TEMPLATE_SECTIONS = [
    'all',
    'META_DOCUMENTATION',
    '0_preparation',
    '1_executive_summary',
    '2_risk_assessment',
    '3_current_state_analysis',
    '4_key_features',
    '5_task_id_system',
    '6_implementation_phases',
    '7_testing_strategy',
    '8_success_criteria',
    '9_implementation_checklist',
    'QUALITY_CHECKLIST_FOR_PLANS',
    'COMMON_MISTAKES_TO_AVOID',
    'USAGE_INSTRUCTIONS'
]


def validate_section_name(section: str) -> str:
    """Validate template section name."""
    if section not in VALID_TEMPLATE_SECTIONS:
        raise ValueError(
            f"Invalid section: '{section}'. "
            f"Valid sections: {', '.join(VALID_TEMPLATE_SECTIONS)}"
        )
    return section


def validate_plan_file_path(project_path, plan_file: str):
    """Validate plan file path to prevent path traversal."""
    from pathlib import Path

    # Resolve to absolute path
    plan_path = (project_path / plan_file).resolve()

    # Check if path is within project directory
    if not plan_path.is_relative_to(project_path):
        raise ValueError(
            f"Plan file path '{plan_file}' traverses outside project directory. "
            "Plan file must be within project directory."
        )
    return plan_path


def validate_plan_json_structure(plan_data: dict) -> dict:
    """Validate plan JSON has required structure."""
    required_keys = ['META_DOCUMENTATION', 'UNIVERSAL_PLANNING_STRUCTURE']

    for key in required_keys:
        if key not in plan_data:
            raise ValueError(
                f"Plan JSON missing required key: '{key}'. "
                f"Valid implementation plans must have: {', '.join(required_keys)}"
            )
    return plan_data


def validate_feature_name_input(feature_name: str) -> str:
    """
    Validate feature name to prevent path traversal and invalid characters.

    Args:
        feature_name: Feature name to validate

    Returns:
        Validated feature name

    Raises:
        ValueError: If feature name contains invalid characters or path separators
    """
    if not feature_name or not isinstance(feature_name, str):
        raise ValueError('feature_name must be a non-empty string')

    if len(feature_name) > 100:
        raise ValueError('feature_name too long (max 100 characters)')

    # Only allow alphanumeric, hyphens, and underscores (no path separators)
    if not re.match(r'^[a-zA-Z0-9_-]+$', feature_name):
        raise ValueError(
            f"Invalid feature_name: '{feature_name}'. "
            "Only alphanumeric characters, hyphens, and underscores are allowed."
        )

    return feature_name


# Workorder Tracking Validation Functions

def validate_workorder_id(workorder_id: str) -> str:
    """
    Validate workorder ID format.

    Expected format: WO-{FEATURE-NAME}-{NUMBER}
    Example: WO-AUTH-001, WO-UPDATE-DOCS-002

    Args:
        workorder_id: Workorder ID to validate

    Returns:
        Validated workorder ID

    Raises:
        ValueError: If workorder ID format is invalid
    """
    if not workorder_id or not isinstance(workorder_id, str):
        raise ValueError('workorder_id must be a non-empty string')

    # Pattern: WO-{ALPHANUM-HYPHENS}-{3DIGITS}
    # Examples: WO-AUTH-001, WO-UPDATE-DOCS-001, WO-FEATURE-NAME-123
    pattern = r'^WO-[A-Z0-9-]+-\d{3}$'

    if not re.match(pattern, workorder_id):
        raise ValueError(
            f"Invalid workorder_id format: '{workorder_id}'. "
            f"Expected format: WO-FEATURE-NAME-001 (uppercase letters, numbers, hyphens, ending with 3 digits)"
        )

    return workorder_id


# Risk Assessment Validation Functions (WO-RISK-ASSESSMENT-001)

def validate_risk_inputs(arguments: dict) -> dict:
    """
    Validate risk assessment tool inputs at MCP boundary.

    Args:
        arguments: Tool arguments dict with:
            - project_path (str, required): Absolute project path
            - proposed_change (dict, required): Change description and details
            - options (list, optional): List of alternative options for comparison
            - threshold (float, optional): Risk score threshold for go/no-go (0-100)

    Returns:
        Validated arguments dict

    Raises:
        ValueError: If any input is invalid
    """
    # Validate project_path (required)
    if 'project_path' not in arguments:
        raise ValueError("Missing required parameter: 'project_path'")

    project_path = validate_project_path_input(arguments['project_path'])

    # Validate proposed_change (required)
    if 'proposed_change' not in arguments:
        raise ValueError("Missing required parameter: 'proposed_change'")

    proposed_change = arguments['proposed_change']
    if not isinstance(proposed_change, dict):
        raise ValueError("'proposed_change' must be a dictionary")

    # Validate proposed_change required fields
    required_change_fields = ['description', 'change_type', 'files_affected']
    for field in required_change_fields:
        if field not in proposed_change:
            raise ValueError(f"proposed_change missing required field: '{field}'")

    # Validate change_type
    valid_change_types = ['create', 'modify', 'delete', 'refactor', 'migrate']
    if proposed_change['change_type'] not in valid_change_types:
        raise ValueError(
            f"Invalid change_type: '{proposed_change['change_type']}'. "
            f"Must be one of: {', '.join(valid_change_types)}"
        )

    # Validate files_affected is a list
    if not isinstance(proposed_change['files_affected'], list):
        raise ValueError("'files_affected' must be a list of file paths")

    # Validate description is non-empty
    if not proposed_change['description'] or not isinstance(proposed_change['description'], str):
        raise ValueError("'description' must be a non-empty string")

    # Validate options (optional)
    if 'options' in arguments and arguments['options'] is not None:
        options = arguments['options']
        if not isinstance(options, list):
            raise ValueError("'options' must be a list")

        if len(options) > 5:
            raise ValueError("Maximum 5 options allowed for comparison")

        # Validate each option has required fields
        for i, option in enumerate(options):
            if not isinstance(option, dict):
                raise ValueError(f"Option {i+1} must be a dictionary")

            if 'description' not in option:
                raise ValueError(f"Option {i+1} missing required field: 'description'")

            if 'files_affected' not in option:
                raise ValueError(f"Option {i+1} missing required field: 'files_affected'")

    # Validate threshold (optional)
    if 'threshold' in arguments and arguments['threshold'] is not None:
        threshold = arguments['threshold']
        if not isinstance(threshold, (int, float)):
            raise ValueError("'threshold' must be a number")

        if threshold < 0 or threshold > 100:
            raise ValueError("'threshold' must be between 0 and 100")

    return {
        'project_path': project_path,
        'proposed_change': proposed_change,
        'options': arguments.get('options'),
        'threshold': arguments.get('threshold', 50.0)  # Default threshold: 50
    }

# Context Expert Validation Functions (WO-CONTEXT-EXPERTS-001)

def validate_resource_path(project_path, resource_path: str) -> str:
    """
    Validate resource path exists within project and is valid.

    Args:
        project_path: Project root path (Path object)
        resource_path: Relative path to resource within project

    Returns:
        Validated resource path string

    Raises:
        ValueError: If path is invalid or outside project
    """
    from pathlib import Path

    if not resource_path or not isinstance(resource_path, str):
        raise ValueError('resource_path must be a non-empty string')

    # Check for path traversal
    if '..' in resource_path:
        raise ValueError(f"Path traversal detected in resource_path: {resource_path}")

    # Resolve full path
    full_path = (project_path / resource_path).resolve()

    # Ensure path is within project
    if not full_path.is_relative_to(project_path):
        raise ValueError(
            f"resource_path '{resource_path}' is outside project directory"
        )

    # Check if path exists
    if not full_path.exists():
        raise ValueError(
            f"resource_path '{resource_path}' does not exist in project"
        )

    return resource_path


def validate_expert_id(expert_id: str) -> str:
    """
    Validate context expert ID format.

    Expected format: CE-{resource-slug}-{NUMBER}
    Example: CE-src-auth-001, CE-components-ui-002

    Args:
        expert_id: Expert ID to validate

    Returns:
        Validated expert ID

    Raises:
        ValueError: If expert ID format is invalid
    """
    if not expert_id or not isinstance(expert_id, str):
        raise ValueError('expert_id must be a non-empty string')

    from constants import EXPERT_ID_PATTERN

    if not re.match(EXPERT_ID_PATTERN, expert_id):
        raise ValueError(
            f"Invalid expert_id format: '{expert_id}'. "
            f"Expected format: CE-resource-slug-001 (e.g., CE-src-auth-001)"
        )

    return expert_id


def validate_resource_type(resource_type: str) -> str:
    """
    Validate resource type parameter.

    Args:
        resource_type: Type of resource ('file' or 'directory')

    Returns:
        Validated resource type

    Raises:
        ValueError: If resource type is invalid
    """
    from constants import ResourceType

    valid_types = [t.value for t in ResourceType]
    if resource_type not in valid_types:
        raise ValueError(
            f"Invalid resource_type: '{resource_type}'. "
            f"Must be one of: {', '.join(valid_types)}"
        )

    return resource_type


def validate_expert_domain(domain: str) -> str:
    """
    Validate expert domain parameter.

    Args:
        domain: Domain specialization (ui, db, api, core, etc.)

    Returns:
        Validated domain

    Raises:
        ValueError: If domain is invalid
    """
    from constants import ExpertDomain

    valid_domains = [d.value for d in ExpertDomain]
    if domain not in valid_domains:
        raise ValueError(
            f"Invalid domain: '{domain}'. "
            f"Must be one of: {', '.join(valid_domains)}"
        )

    return domain


def validate_expert_capabilities(capabilities: list) -> list:
    """
    Validate expert capabilities list.

    Args:
        capabilities: List of capabilities

    Returns:
        Validated capabilities list

    Raises:
        ValueError: If any capability is invalid
    """
    from constants import ContextExpertCapability

    if not isinstance(capabilities, list):
        raise ValueError("capabilities must be a list")

    valid_caps = [c.value for c in ContextExpertCapability]
    for cap in capabilities:
        if cap not in valid_caps:
            raise ValueError(
                f"Invalid capability: '{cap}'. "
                f"Must be one of: {', '.join(valid_caps)}"
            )

    return capabilities


def validate_context_expert_inputs(arguments: dict) -> dict:
    """
    Validate context expert tool inputs at MCP boundary.

    Args:
        arguments: Tool arguments dict

    Returns:
        Validated arguments dict

    Raises:
        ValueError: If any input is invalid
    """
    from pathlib import Path

    # Validate project_path (required)
    if 'project_path' not in arguments:
        raise ValueError("Missing required parameter: 'project_path'")

    project_path = Path(validate_project_path_input(arguments['project_path'])).resolve()

    # Validate resource_path (required for create)
    if 'resource_path' in arguments:
        validate_resource_path(project_path, arguments['resource_path'])

    # Validate resource_type (required for create)
    if 'resource_type' in arguments:
        validate_resource_type(arguments['resource_type'])

    # Validate expert_id (required for get/update/activate)
    if 'expert_id' in arguments:
        validate_expert_id(arguments['expert_id'])

    # Validate domain (optional)
    if 'domain' in arguments and arguments['domain']:
        validate_expert_domain(arguments['domain'])

    # Validate capabilities (optional)
    if 'capabilities' in arguments and arguments['capabilities']:
        validate_expert_capabilities(arguments['capabilities'])

    return arguments
