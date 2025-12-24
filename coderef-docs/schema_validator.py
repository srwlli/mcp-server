"""
Schema validation utilities for coderef-docs planning tools.

This module provides schema validation for plan.json files using the
plan.schema.json as the single source of truth.

Part of WO-DOCS-MCP-SCHEMA-FIX-001: Schema-First Planning Architecture

Modes:
- strict=False (default): Silently normalize legacy formats
- strict=True: Log warnings when normalization is required
"""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Global strict mode flag - set True to log warnings on normalization
STRICT_MODE = True  # Enable by default to help identify where AI generates wrong formats

# Schema directory relative to this file
SCHEMA_DIR = Path(__file__).parent / "schemas"
PLAN_SCHEMA_PATH = SCHEMA_DIR / "plan.schema.json"


def load_plan_schema() -> dict:
    """Load the plan.schema.json file."""
    if not PLAN_SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Schema file not found: {PLAN_SCHEMA_PATH}")

    with open(PLAN_SCHEMA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_plan_schema(plan: dict) -> tuple[bool, list[str]]:
    """
    Validate a plan against the schema.

    Returns:
        tuple: (is_valid, list of error messages)
    """
    errors = []

    # Check for required top-level keys
    if "META_DOCUMENTATION" not in plan:
        errors.append("Missing required section: META_DOCUMENTATION")

    if "UNIVERSAL_PLANNING_STRUCTURE" not in plan:
        errors.append("Missing required section: UNIVERSAL_PLANNING_STRUCTURE")
        return False, errors

    structure = plan.get("UNIVERSAL_PLANNING_STRUCTURE", {})

    # Check for required sections
    required_sections = [
        "0_preparation",
        "1_executive_summary",
        "2_risk_assessment",
        "3_current_state_analysis",
        "4_key_features",
        "5_task_id_system",
        "6_implementation_phases",
        "7_testing_strategy",
        "8_success_criteria",
        "9_implementation_checklist"
    ]

    for section in required_sections:
        if section not in structure:
            errors.append(f"Missing required section: {section}")

    # Validate specific structures
    errors.extend(_validate_phases(structure.get("6_implementation_phases", {})))
    errors.extend(_validate_tasks(structure.get("5_task_id_system", {})))
    errors.extend(_validate_files(structure.get("3_current_state_analysis", {})))

    return len(errors) == 0, errors


def _validate_phases(phases_section: dict) -> list[str]:
    """Validate the implementation phases section."""
    errors = []

    # Handle both array format (correct) and legacy dict format
    if "phases" in phases_section:
        phases = phases_section["phases"]
        if not isinstance(phases, list):
            errors.append("6_implementation_phases.phases must be an array")
            return errors

        for i, phase in enumerate(phases):
            if not isinstance(phase, dict):
                errors.append(f"Phase {i} must be an object")
                continue

            if "phase" not in phase:
                errors.append(f"Phase {i} missing required field: phase (number)")
            if "name" not in phase:
                errors.append(f"Phase {i} missing required field: name")
            if "tasks" not in phase:
                errors.append(f"Phase {i} missing required field: tasks")
            if "deliverables" not in phase:
                errors.append(f"Phase {i} missing required field: deliverables")
    else:
        # Check for legacy phase_1, phase_2 format
        phase_keys = [k for k in phases_section.keys() if k.startswith("phase_")]
        if phase_keys:
            # Legacy format detected - not an error, but log warning
            logger.warning("Legacy phase format detected (phase_1, phase_2). Consider migrating to phases[] array.")
        elif phases_section:
            errors.append("6_implementation_phases must contain 'phases' array")

    return errors


def _validate_tasks(task_section: dict) -> list[str]:
    """Validate the task ID system section."""
    errors = []

    if "workorder" not in task_section:
        errors.append("5_task_id_system missing required field: workorder")
    else:
        workorder = task_section["workorder"]
        if "id" not in workorder:
            errors.append("5_task_id_system.workorder missing required field: id")

    # Handle both array format (correct) and legacy task_breakdown format
    if "tasks" in task_section:
        tasks = task_section["tasks"]
        if not isinstance(tasks, list):
            errors.append("5_task_id_system.tasks must be an array")
            return errors

        for i, task in enumerate(tasks):
            if not isinstance(task, dict):
                errors.append(f"Task {i} must be an object")
                continue

            if "id" not in task:
                errors.append(f"Task {i} missing required field: id")
            if "description" not in task:
                errors.append(f"Task {i} missing required field: description")
    elif "task_breakdown" in task_section:
        # Legacy format - not an error but log warning
        logger.warning("Legacy task_breakdown format detected. Consider migrating to tasks[] array.")
    else:
        errors.append("5_task_id_system must contain 'tasks' array")

    return errors


def _validate_files(current_state: dict) -> list[str]:
    """Validate the current state analysis section."""
    errors = []

    # files_to_create can be strings or objects - both are valid
    files_to_create = current_state.get("files_to_create", [])
    if isinstance(files_to_create, list):
        for i, file_entry in enumerate(files_to_create):
            # Accept both string format and object format
            if isinstance(file_entry, str):
                # Simple string format is valid
                pass
            elif isinstance(file_entry, dict):
                # Object format should have path and purpose
                if "path" not in file_entry:
                    errors.append(f"files_to_create[{i}] object missing 'path' field")
            else:
                errors.append(f"files_to_create[{i}] must be string or object")

    return errors


def format_validation_errors(errors: list[str]) -> str:
    """Format validation errors into a human-readable message."""
    if not errors:
        return "Plan is valid."

    header = f"Schema validation failed with {len(errors)} error(s):\n"
    formatted_errors = "\n".join(f"  • {error}" for error in errors)

    return header + formatted_errors


# Helper functions for safe access to plan data

def get_phases(plan: dict, strict: bool = None) -> list[dict]:
    """
    Safely extract phases from a plan, handling both array and legacy formats.

    Args:
        plan: The plan.json dict
        strict: Override global STRICT_MODE. If True, logs warnings on normalization.

    Returns a normalized list of phase objects.
    """
    if strict is None:
        strict = STRICT_MODE

    structure = plan.get("UNIVERSAL_PLANNING_STRUCTURE", {})
    phases_section = structure.get("6_implementation_phases", {})

    # New format: phases array (schema-compliant)
    if "phases" in phases_section:
        return phases_section["phases"]

    # Legacy format: phase_1, phase_2, etc.
    phase_keys = sorted([k for k in phases_section.keys() if k.startswith("phase_")])
    if phase_keys:
        if strict:
            logger.warning(
                f"SCHEMA: Legacy phase format detected (phase_1, phase_2...). "
                f"Expected: 6_implementation_phases.phases[] array. "
                f"Plan: {plan.get('META_DOCUMENTATION', {}).get('feature_name', 'unknown')}"
            )
        phases = []
        for i, key in enumerate(phase_keys, 1):
            phase = phases_section[key].copy()
            phase["phase"] = i
            phases.append(phase)
        return phases

    return []


def get_tasks(plan: dict, strict: bool = None) -> list[dict]:
    """
    Safely extract tasks from a plan, handling both array and legacy formats.

    Args:
        plan: The plan.json dict
        strict: Override global STRICT_MODE. If True, logs warnings on normalization.

    Returns a normalized list of task objects.
    """
    if strict is None:
        strict = STRICT_MODE

    structure = plan.get("UNIVERSAL_PLANNING_STRUCTURE", {})
    task_section = structure.get("5_task_id_system", {})

    # New format: tasks array (schema-compliant)
    if "tasks" in task_section:
        return task_section["tasks"]

    # Legacy format: task_breakdown with feature_tasks
    if "task_breakdown" in task_section:
        if strict:
            logger.warning(
                f"SCHEMA: Legacy task_breakdown format detected. "
                f"Expected: 5_task_id_system.tasks[] array. "
                f"Plan: {plan.get('META_DOCUMENTATION', {}).get('feature_name', 'unknown')}"
            )
        tasks = []
        for feature_key, feature_tasks in task_section["task_breakdown"].items():
            if isinstance(feature_tasks, list):
                tasks.extend(feature_tasks)
        return tasks

    return []


def get_files_to_create(plan: dict, strict: bool = None) -> list[dict]:
    """
    Safely extract files_to_create, normalizing to object format.

    Args:
        plan: The plan.json dict
        strict: Override global STRICT_MODE. If True, logs warnings on normalization.

    Returns list of {"path": str, "purpose": str} objects.
    """
    if strict is None:
        strict = STRICT_MODE

    structure = plan.get("UNIVERSAL_PLANNING_STRUCTURE", {})
    current_state = structure.get("3_current_state_analysis", {})
    files = current_state.get("files_to_create", [])

    normalized = []
    has_strings = False
    for f in files:
        if isinstance(f, str):
            has_strings = True
            normalized.append({"path": f, "purpose": "TBD"})
        elif isinstance(f, dict):
            normalized.append({
                "path": f.get("path", "unknown"),
                "purpose": f.get("purpose", "TBD")
            })

    if has_strings and strict:
        logger.warning(
            f"SCHEMA: files_to_create contains strings instead of objects. "
            f"Expected: [{{path: '...', purpose: '...'}}]. "
            f"Plan: {plan.get('META_DOCUMENTATION', {}).get('feature_name', 'unknown')}"
        )

    return normalized


def get_files_to_modify(plan: dict, strict: bool = None) -> list[dict]:
    """
    Safely extract files_to_modify, normalizing to object format.

    Args:
        plan: The plan.json dict
        strict: Override global STRICT_MODE. If True, logs warnings on normalization.

    Returns list of {"path": str, "changes": str} objects.
    """
    if strict is None:
        strict = STRICT_MODE

    structure = plan.get("UNIVERSAL_PLANNING_STRUCTURE", {})
    current_state = structure.get("3_current_state_analysis", {})
    files = current_state.get("files_to_modify", [])

    normalized = []
    has_strings = False
    for f in files:
        if isinstance(f, str):
            has_strings = True
            normalized.append({"path": f, "changes": "TBD"})
        elif isinstance(f, dict):
            normalized.append({
                "path": f.get("path", "unknown"),
                "changes": f.get("changes", "TBD")
            })

    if has_strings and strict:
        logger.warning(
            f"SCHEMA: files_to_modify contains strings instead of objects. "
            f"Expected: [{{path: '...', changes: '...'}}]. "
            f"Plan: {plan.get('META_DOCUMENTATION', {}).get('feature_name', 'unknown')}"
        )

    return normalized


def get_workorder_id(plan: dict) -> str:
    """Safely extract workorder ID from plan."""
    structure = plan.get("UNIVERSAL_PLANNING_STRUCTURE", {})
    task_section = structure.get("5_task_id_system", {})
    workorder = task_section.get("workorder", {})
    return workorder.get("id", "N/A")


def get_success_criteria(plan: dict) -> dict:
    """Safely extract success criteria from plan."""
    structure = plan.get("UNIVERSAL_PLANNING_STRUCTURE", {})
    success = structure.get("8_success_criteria", {})

    # Handle both formats
    return {
        "functional": success.get("functional", success.get("functional_requirements", [])),
        "performance": success.get("performance", []),
        "quality": success.get("quality", [])
    }




def get_checklist(plan: dict, strict: bool = None) -> dict:
    """
    Safely extract implementation checklist from section 9.

    Args:
        plan: The plan.json dict
        strict: Override global STRICT_MODE. If True, logs warnings on normalization.

    Returns:
        Normalized dict with checklist categories. If section 9 is a list,
        wraps it in {"tasks": [...]} for consistent access.

        Handles both formats:
        - Direct arrays: {"phase_1": ["task1", "task2"]}
        - Nested objects: {"phase_1": {"tasks": ["task1", "task2"], "validation": "..."}}
    """
    if strict is None:
        strict = STRICT_MODE

    structure = plan.get("UNIVERSAL_PLANNING_STRUCTURE", {})
    section_9 = structure.get("9_implementation_checklist", {})

    # Expected format: dict with category keys like "pre_implementation", "implementation", etc.
    if isinstance(section_9, dict):
        # DEBUG: Log what we received
        logger.debug(f"get_checklist: section_9 is dict with keys: {list(section_9.keys())}")

        # Normalize nested {tasks: [...], validation: "..."} format to direct arrays
        normalized = {}
        for key, value in section_9.items():
            logger.debug(f"get_checklist: processing key={key}, value type={type(value).__name__}, has 'tasks'={isinstance(value, dict) and 'tasks' in value}")

            if isinstance(value, dict) and "tasks" in value:
                # Extract tasks array from nested object (common AI pattern)
                if strict:
                    logger.warning(
                        f"SCHEMA: 9_implementation_checklist.{key} has nested {{tasks: [...]}}, extracting to direct array. "
                        f"Plan: {plan.get('META_DOCUMENTATION', {}).get('feature_name', 'unknown')}"
                    )
                normalized[key] = value["tasks"]
                logger.debug(f"get_checklist: extracted {len(value['tasks'])} tasks from {key}")
            elif isinstance(value, list):
                # Already in correct format (direct array)
                normalized[key] = value
                logger.debug(f"get_checklist: direct list with {len(value)} tasks from {key}")
            else:
                # Skip non-conforming entries
                if strict:
                    logger.warning(
                        f"SCHEMA: 9_implementation_checklist.{key} has unexpected type {type(value).__name__}, skipping. "
                        f"Plan: {plan.get('META_DOCUMENTATION', {}).get('feature_name', 'unknown')}"
                    )
                continue

        logger.debug(f"get_checklist: returning normalized dict with {len(normalized)} keys: {list(normalized.keys())}")
        return normalized

    # Legacy format: list of items (common AI generation pattern)
    if isinstance(section_9, list):
        if strict:
            logger.warning(
                f"SCHEMA: 9_implementation_checklist is list, expected dict with categories. "
                f"Wrapping in {{'tasks': [...]}}. "
                f"Plan: {plan.get('META_DOCUMENTATION', {}).get('feature_name', 'unknown')}"
            )
        return {"tasks": section_9}

    # Fallback for unexpected types
    if strict and section_9 is not None:
        logger.warning(
            f"SCHEMA: 9_implementation_checklist has unexpected type {type(section_9).__name__}. "
            f"Plan: {plan.get('META_DOCUMENTATION', {}).get('feature_name', 'unknown')}"
        )
    return {}

def validate_plan_exists(plan_path) -> tuple[bool, str]:
    """
    Check if plan.json exists and is valid JSON.

    Returns:
        tuple: (exists: bool, error_message: str or None)
    """
    from pathlib import Path
    plan_path = Path(plan_path)

    if not plan_path.exists():
        return False, f"Plan file not found: {plan_path}. Run /create-plan first."

    if not plan_path.is_file():
        return False, f"Path is not a file: {plan_path}"

    try:
        with open(plan_path, 'r', encoding='utf-8') as f:
            json.load(f)
        return True, None
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON in {plan_path}: {e}"
    except Exception as e:
        return False, f"Error reading {plan_path}: {e}"


def quick_validate(plan: dict, verbose: bool = False) -> tuple[bool, list[str]]:
    """
    Quick validation for CI/pre-commit - validate schema without generating deliverables.

    Args:
        plan: The plan.json dict
        verbose: If True, print validation results

    Returns:
        tuple: (is_valid: bool, errors: list[str])
    """
    is_valid, errors = validate_plan_schema(plan)

    if verbose:
        if is_valid:
            print("✅ Plan schema is valid")
        else:
            print("❌ Plan schema validation failed:")
            for error in errors:
                print(f"  • {error}")

    return is_valid, errors


# ============================================================================
# SMOKE TEST - Run with: python schema_validator.py
# ============================================================================

if __name__ == "__main__":
    print("Running schema_validator smoke tests...\n")

    # Test 1: get_phases with new format
    test_plan_new = {
        "META_DOCUMENTATION": {"feature_name": "test"},
        "UNIVERSAL_PLANNING_STRUCTURE": {
            "6_implementation_phases": {
                "phases": [
                    {"phase": 1, "name": "Foundation", "tasks": [], "deliverables": []},
                    {"phase": 2, "name": "Core", "tasks": [], "deliverables": []}
                ]
            }
        }
    }
    phases = get_phases(test_plan_new, strict=False)
    assert len(phases) == 2, f"Expected 2 phases, got {len(phases)}"
    assert phases[0]["name"] == "Foundation"
    print("✅ Test 1: get_phases (new format) - PASSED")

    # Test 2: get_phases with legacy format
    test_plan_legacy = {
        "META_DOCUMENTATION": {"feature_name": "test-legacy"},
        "UNIVERSAL_PLANNING_STRUCTURE": {
            "6_implementation_phases": {
                "phase_1": {"name": "Legacy Phase 1", "deliverables": []},
                "phase_2": {"name": "Legacy Phase 2", "deliverables": []}
            }
        }
    }
    phases = get_phases(test_plan_legacy, strict=False)
    assert len(phases) == 2, f"Expected 2 phases, got {len(phases)}"
    assert phases[0]["name"] == "Legacy Phase 1"
    print("✅ Test 2: get_phases (legacy format) - PASSED")

    # Test 3: get_tasks with new format
    test_plan_tasks = {
        "META_DOCUMENTATION": {"feature_name": "test"},
        "UNIVERSAL_PLANNING_STRUCTURE": {
            "5_task_id_system": {
                "workorder": {"id": "WO-TEST-001"},
                "tasks": [
                    {"id": "TASK-001", "description": "First task"},
                    {"id": "TASK-002", "description": "Second task"}
                ]
            }
        }
    }
    tasks = get_tasks(test_plan_tasks, strict=False)
    assert len(tasks) == 2, f"Expected 2 tasks, got {len(tasks)}"
    assert tasks[0]["id"] == "TASK-001"
    print("✅ Test 3: get_tasks (new format) - PASSED")

    # Test 4: get_files_to_create normalizes strings
    test_plan_files = {
        "META_DOCUMENTATION": {"feature_name": "test"},
        "UNIVERSAL_PLANNING_STRUCTURE": {
            "3_current_state_analysis": {
                "files_to_create": ["file1.ts", "file2.ts"]
            }
        }
    }
    files = get_files_to_create(test_plan_files, strict=False)
    assert len(files) == 2
    assert files[0]["path"] == "file1.ts"
    assert files[0]["purpose"] == "TBD"
    print("✅ Test 4: get_files_to_create (string normalization) - PASSED")

    # Test 5: get_workorder_id
    wo_id = get_workorder_id(test_plan_tasks)
    assert wo_id == "WO-TEST-001"
    print("✅ Test 5: get_workorder_id - PASSED")

    # Test 6: validate_plan_schema
    complete_plan = {
        "META_DOCUMENTATION": {"feature_name": "test", "schema_version": "1.0.0", "status": "complete"},
        "UNIVERSAL_PLANNING_STRUCTURE": {
            "0_preparation": {},
            "1_executive_summary": {},
            "2_risk_assessment": {},
            "3_current_state_analysis": {},
            "4_key_features": {},
            "5_task_id_system": {"workorder": {"id": "WO-TEST-001"}, "tasks": []},
            "6_implementation_phases": {"phases": []},
            "7_testing_strategy": {},
            "8_success_criteria": {},
            "9_implementation_checklist": {}
        }
    }
    is_valid, errors = validate_plan_schema(complete_plan)
    assert is_valid, f"Expected valid plan, got errors: {errors}"
    print("✅ Test 6: validate_plan_schema (complete plan) - PASSED")

    # Test 7: validate_plan_schema catches missing sections
    incomplete_plan = {"META_DOCUMENTATION": {}}
    is_valid, errors = validate_plan_schema(incomplete_plan)
    assert not is_valid
    assert any("UNIVERSAL_PLANNING_STRUCTURE" in e for e in errors)
    print("✅ Test 7: validate_plan_schema (catches missing sections) - PASSED")

    print("\n" + "=" * 50)
    print("All smoke tests PASSED!")
    print("=" * 50)
