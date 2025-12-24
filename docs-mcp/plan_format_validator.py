"""
Plan format enforcement for coderef-docs (STUB-032).

This module enforces the standard plan.json format:
- Standard location: coderef/working/{feature}/plan.json
- Standard format: JSON (not .md, not .txt)
- Created via /create-plan workflow

Rejects non-standard formats with clear guidance.
"""

import json
import re
from pathlib import Path
from typing import Tuple, Optional, List
from logger_config import logger


# Standard plan location pattern
PLAN_LOCATION_PATTERN = re.compile(
    r'^coderef[/\\]working[/\\]([a-zA-Z0-9_-]+)[/\\]plan\.json$'
)

# Invalid plan file extensions (reject these)
INVALID_PLAN_EXTENSIONS = {'.md', '.txt', '.yaml', '.yml'}

# Invalid plan filenames (reject these patterns)
INVALID_PLAN_PATTERNS = [
    re.compile(r'plan\.md$', re.IGNORECASE),
    re.compile(r'PLAN\.md$', re.IGNORECASE),
    re.compile(r'implementation[-_]?plan\.(md|txt)$', re.IGNORECASE),
]


class PlanFormatError(ValueError):
    """Raised when plan format is invalid."""

    def __init__(self, message: str, suggestion: str):
        self.message = message
        self.suggestion = suggestion
        super().__init__(f"{message}\n\nSuggestion: {suggestion}")


def validate_plan_format(plan_path: Path) -> Tuple[bool, Optional[str]]:
    """
    Validate that plan file is in correct format.

    Checks:
    1. File must have .json extension
    2. File must be valid JSON
    3. File should be in standard location (warning if not)

    Args:
        plan_path: Path to plan file

    Returns:
        Tuple of (is_valid, error_message)

    Example:
        >>> valid, error = validate_plan_format(Path('coderef/working/auth/plan.json'))
        >>> valid
        True
        >>> valid, error = validate_plan_format(Path('plan.md'))
        >>> valid
        False
        >>> 'must be JSON' in error
        True
    """
    plan_path = Path(plan_path).resolve()

    # Check extension
    if plan_path.suffix.lower() != '.json':
        return False, (
            f"Plan file must be .json format, got '{plan_path.suffix}'\n"
            f"Found: {plan_path.name}\n"
            f"Expected: plan.json\n\n"
            "Use /create-plan to generate a proper plan.json file."
        )

    # Check for invalid patterns in filename
    for pattern in INVALID_PLAN_PATTERNS:
        if pattern.search(plan_path.name):
            return False, (
                f"Invalid plan file format: {plan_path.name}\n"
                f"Plans must be JSON files, not markdown.\n\n"
                "Use /create-plan to generate a proper plan.json file."
            )

    # Check if file exists
    if not plan_path.exists():
        return False, f"Plan file not found: {plan_path}"

    # Validate JSON content
    try:
        with open(plan_path, 'r', encoding='utf-8') as f:
            json.load(f)
    except json.JSONDecodeError as e:
        return False, (
            f"Invalid JSON in plan file: {plan_path}\n"
            f"JSON Error: {e}\n\n"
            "Ensure the plan file contains valid JSON."
        )
    except UnicodeDecodeError as e:
        return False, (
            f"Encoding error in plan file: {plan_path}\n"
            f"Error: {e}\n\n"
            "Plan files must be UTF-8 encoded."
        )

    return True, None


def validate_plan_location(plan_path: Path, project_path: Path) -> Tuple[bool, Optional[str], str]:
    """
    Validate that plan is in standard location.

    Standard location: {project}/coderef/working/{feature}/plan.json

    Args:
        plan_path: Path to plan file
        project_path: Root project directory

    Returns:
        Tuple of (is_standard_location, warning_message, feature_name)

    Example:
        >>> is_std, warn, feature = validate_plan_location(
        ...     Path('coderef/working/auth/plan.json'),
        ...     Path('.')
        ... )
        >>> is_std
        True
        >>> feature
        'auth'
    """
    plan_path = Path(plan_path).resolve()
    project_path = Path(project_path).resolve()

    # Get relative path from project root
    try:
        relative_path = plan_path.relative_to(project_path)
        relative_str = str(relative_path).replace('\\', '/')
    except ValueError:
        # Plan not under project - non-standard location
        return False, (
            f"Plan file not under project directory.\n"
            f"Plan: {plan_path}\n"
            f"Project: {project_path}\n\n"
            "Standard location: coderef/working/{feature}/plan.json"
        ), ""

    # Check against standard pattern
    match = PLAN_LOCATION_PATTERN.match(relative_str)
    if match:
        feature_name = match.group(1)
        return True, None, feature_name

    # Extract feature name from path if possible
    parts = relative_path.parts
    feature_name = ""
    if len(parts) >= 2:
        # Try to find feature name from parent directory
        feature_name = parts[-2] if parts[-1] == 'plan.json' else parts[-1]

    return False, (
        f"Plan file not in standard location.\n"
        f"Current: {relative_str}\n"
        f"Expected: coderef/working/{{feature}}/plan.json\n\n"
        f"Use /create-plan to create plans in the standard location."
    ), feature_name


def enforce_plan_format(
    plan_path: Path,
    project_path: Path = None,
    strict: bool = False
) -> Tuple[bool, List[str], Optional[str]]:
    """
    Enforce plan.json format with comprehensive validation.

    This is the main entry point for format enforcement (STUB-032).

    Args:
        plan_path: Path to plan file
        project_path: Root project directory (optional)
        strict: If True, treat location warnings as errors

    Returns:
        Tuple of (is_valid, errors_list, feature_name)

    Example:
        >>> valid, errors, feature = enforce_plan_format(
        ...     Path('coderef/working/auth/plan.json'),
        ...     Path('.'),
        ...     strict=True
        ... )
        >>> valid
        True
        >>> len(errors)
        0
        >>> feature
        'auth'
    """
    errors = []
    feature_name = None

    # Step 1: Validate format
    format_valid, format_error = validate_plan_format(plan_path)
    if not format_valid:
        errors.append(format_error)
        logger.warning(f"Plan format validation failed: {plan_path}", extra={
            'error': format_error,
            'plan_path': str(plan_path)
        })
        return False, errors, None

    # Step 2: Validate location (if project_path provided)
    if project_path:
        location_valid, location_warning, feature_name = validate_plan_location(
            plan_path, project_path
        )
        if not location_valid and location_warning:
            if strict:
                errors.append(location_warning)
                logger.warning(f"Plan location validation failed (strict mode): {plan_path}")
            else:
                # Just log warning but don't fail
                logger.info(f"Plan not in standard location: {plan_path}")
    else:
        # Extract feature name from path
        plan_path = Path(plan_path)
        if plan_path.parent.name != 'working':
            feature_name = plan_path.parent.name

    is_valid = len(errors) == 0

    if is_valid:
        logger.debug(f"Plan format validation passed: {plan_path}", extra={
            'feature_name': feature_name
        })

    return is_valid, errors, feature_name


def check_for_invalid_plans(working_dir: Path) -> List[dict]:
    """
    Scan working directory for invalid plan formats.

    Finds plan.md, PLAN.md, and other non-standard formats.

    Args:
        working_dir: Path to coderef/working directory

    Returns:
        List of dicts with 'path', 'issue', and 'suggestion' keys

    Example:
        >>> invalid = check_for_invalid_plans(Path('coderef/working'))
        >>> for item in invalid:
        ...     print(f"{item['path']}: {item['issue']}")
    """
    invalid_plans = []
    working_dir = Path(working_dir)

    if not working_dir.exists():
        return invalid_plans

    # Scan for markdown plans
    for md_file in working_dir.glob('**/plan.md'):
        invalid_plans.append({
            'path': str(md_file),
            'issue': 'Markdown plan file (should be JSON)',
            'suggestion': f"Convert to JSON or use /create-plan for {md_file.parent.name}"
        })

    # Scan for uppercase PLAN.md
    for md_file in working_dir.glob('**/PLAN.md'):
        invalid_plans.append({
            'path': str(md_file),
            'issue': 'Markdown plan file (should be JSON)',
            'suggestion': f"Convert to JSON or use /create-plan for {md_file.parent.name}"
        })

    # Scan for other patterns
    for pattern in ['**/implementation-plan.md', '**/implementation_plan.md']:
        for md_file in working_dir.glob(pattern):
            invalid_plans.append({
                'path': str(md_file),
                'issue': 'Non-standard plan file format',
                'suggestion': f"Use standard plan.json format via /create-plan"
            })

    return invalid_plans


def get_enforcement_message() -> str:
    """
    Get the standard enforcement message for documentation.

    Returns the message to include in CLAUDE.md and persona instructions.

    Returns:
        Formatted enforcement message
    """
    return """## Plan Format Enforcement (STUB-032)

All implementation plans MUST use the following standard:

**Location**: `coderef/working/{feature}/plan.json`
**Format**: JSON (not markdown, not plaintext)
**Creation**: Use `/create-plan` workflow

### Why JSON?
- Machine-readable for orchestrator discovery
- Validated against schema
- Enables automated tracking
- Supports workorder ID system

### Invalid Formats (REJECTED)
- plan.md, PLAN.md
- implementation-plan.md
- *.txt plans
- Plans outside coderef/working/

### Enforcement
- Tools validate plan format before execution
- Lloyd persona operates in strict mode
- /audit-plans reports non-compliant plans
"""


# ============================================================================
# SMOKE TEST - Run with: python plan_format_validator.py
# ============================================================================

if __name__ == "__main__":
    import tempfile
    import os

    print("Running plan_format_validator smoke tests...\n")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create test structure
        working = tmpdir / "coderef" / "working" / "test-feature"
        working.mkdir(parents=True)

        # Test 1: Valid JSON plan
        valid_plan = working / "plan.json"
        valid_plan.write_text('{"test": true}', encoding='utf-8')

        is_valid, error = validate_plan_format(valid_plan)
        assert is_valid, f"Expected valid, got error: {error}"
        print("[OK] Test 1: Valid JSON plan - PASSED")

        # Test 2: Invalid .md plan
        invalid_plan = working / "plan.md"
        invalid_plan.write_text('# Plan', encoding='utf-8')

        is_valid, error = validate_plan_format(invalid_plan)
        assert not is_valid, "Expected invalid for .md file"
        assert ".json format" in error
        print("[OK] Test 2: Invalid .md plan rejected - PASSED")

        # Test 3: Location validation (standard)
        is_std, warn, feature = validate_plan_location(valid_plan, tmpdir)
        assert is_std, f"Expected standard location, got: {warn}"
        assert feature == "test-feature"
        print("[OK] Test 3: Standard location validation - PASSED")

        # Test 4: Location validation (non-standard)
        non_std_plan = tmpdir / "plan.json"
        non_std_plan.write_text('{}', encoding='utf-8')

        is_std, warn, feature = validate_plan_location(non_std_plan, tmpdir)
        assert not is_std, "Expected non-standard location"
        assert "not in standard location" in warn
        print("[OK] Test 4: Non-standard location detected - PASSED")

        # Test 5: Full enforcement (non-strict)
        is_valid, errors, feature = enforce_plan_format(valid_plan, tmpdir, strict=False)
        assert is_valid
        assert feature == "test-feature"
        print("[OK] Test 5: Full enforcement (non-strict) - PASSED")

        # Test 6: Check for invalid plans
        invalid_md = working / "bad"
        invalid_md.mkdir(exist_ok=True)
        (invalid_md / "plan.md").write_text('# Bad', encoding='utf-8')

        invalid_list = check_for_invalid_plans(tmpdir / "coderef" / "working")
        assert len(invalid_list) >= 1
        assert any("plan.md" in str(p['path']) for p in invalid_list)
        print("[OK] Test 6: Invalid plan detection - PASSED")

        # Test 7: Invalid JSON
        bad_json = tmpdir / "bad.json"
        bad_json.write_text('{"invalid": }', encoding='utf-8')

        is_valid, error = validate_plan_format(bad_json)
        assert not is_valid
        assert "Invalid JSON" in error
        print("[OK] Test 7: Invalid JSON detected - PASSED")

    print("\n" + "=" * 50)
    print("All smoke tests PASSED!")
    print("=" * 50)
