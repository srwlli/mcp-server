"""
Code intelligence extractors for foundation documentation.

Provides extraction functions that call @coderef/core CLI to extract:
- API endpoints (routes, methods, parameters)
- Database schemas (entities, fields, relationships)
- Component definitions (React/Vue components, props, hierarchy)

Part of WO-CONTEXT-DOCS-INTEGRATION-001 Phase 1.

These are STUBS for Phase 1 setup. Real implementation happens in Phase 2.
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from cli_utils import run_coderef_command, get_cli_path, validate_cli_available
from logger_config import logger


def extract_apis(project_path: str) -> Dict[str, Any]:
    """
    Extract API endpoints from project using @coderef/core CLI.

    Scans the project codebase to discover API routes, HTTP methods,
    parameters, and descriptions. Works with Express, FastAPI, Flask, etc.

    Args:
        project_path: Absolute path to project directory

    Returns:
        dict with keys:
            - endpoints: list of dicts with {method, path, params, description}
            - error: str if extraction failed (or None if successful)
            - timestamp: ISO 8601 timestamp when extraction happened
            - source: "coderef-cli" or "placeholder"

    Example:
        >>> result = extract_apis("/path/to/project")
        >>> if "error" not in result:
        ...     for endpoint in result["endpoints"]:
        ...         print(f"{endpoint['method']} {endpoint['path']}")

    Phase 1 Implementation:
        STUB - Returns empty dict with metadata.
        Real implementation in Phase 2 (IMPL-001).
    """
    try:
        logger.info(f"extract_apis called for project: {project_path}")

        # STUB: Phase 1 - Just return structure without real extraction
        # TODO Phase 2 (IMPL-001): Call run_coderef_command to get API data
        # TODO Phase 2 (IMPL-001): Transform CLI output to standard format
        # TODO Phase 2 (IMPL-001): Parse route decorators, detect HTTP methods

        return {
            "endpoints": [],
            "error": None,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "placeholder",
            "note": "STUB - Phase 1 placeholder. Real extraction in Phase 2 (IMPL-001)"
        }

    except Exception as e:
        logger.warning(f"API extraction failed: {str(e)}")
        return {
            "endpoints": [],
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "error"
        }


def extract_schemas(project_path: str) -> Dict[str, Any]:
    """
    Extract database schemas from project using @coderef/core CLI.

    Scans the project codebase to discover database models, entities,
    fields, data types, and relationships. Works with SQLAlchemy, TypeORM,
    Prisma, Mongoose, etc.

    Args:
        project_path: Absolute path to project directory

    Returns:
        dict with keys:
            - entities: list of dicts with {name, fields, relationships}
            - error: str if extraction failed (or None if successful)
            - timestamp: ISO 8601 timestamp when extraction happened
            - source: "coderef-cli" or "placeholder"

    Example:
        >>> result = extract_schemas("/path/to/project")
        >>> if "error" not in result:
        ...     for entity in result["entities"]:
        ...         print(f"Entity: {entity['name']} ({len(entity['fields'])} fields)")

    Phase 1 Implementation:
        STUB - Returns empty dict with metadata.
        Real implementation in Phase 2 (IMPL-002).
    """
    try:
        logger.info(f"extract_schemas called for project: {project_path}")

        # STUB: Phase 1 - Just return structure without real extraction
        # TODO Phase 2 (IMPL-002): Call run_coderef_command to get schema data
        # TODO Phase 2 (IMPL-002): Transform CLI output to standard format
        # TODO Phase 2 (IMPL-002): Parse ORM models, detect relationships

        return {
            "entities": [],
            "error": None,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "placeholder",
            "note": "STUB - Phase 1 placeholder. Real extraction in Phase 2 (IMPL-002)"
        }

    except Exception as e:
        logger.warning(f"Schema extraction failed: {str(e)}")
        return {
            "entities": [],
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "error"
        }


def extract_components(project_path: str) -> Dict[str, Any]:
    """
    Extract component definitions from project using @coderef/core CLI.

    Scans the project codebase to discover UI components, their props,
    state, and hierarchy. Works with React, Vue, Svelte, Angular, etc.

    Args:
        project_path: Absolute path to project directory

    Returns:
        dict with keys:
            - components: list of component dicts with {name, props, hierarchy}
            - error: str if extraction failed (or None if successful)
            - timestamp: ISO 8601 timestamp when extraction happened
            - source: "coderef-cli" or "placeholder"

    Example:
        >>> result = extract_components("/path/to/project")
        >>> if "error" not in result:
        ...     for component in result["components"]:
        ...         print(f"Component: {component['name']} ({len(component.get('props', []))} props)")

    Phase 1 Implementation:
        STUB - Returns empty dict with metadata.
        Real implementation in Phase 2 (IMPL-003).
    """
    try:
        logger.info(f"extract_components called for project: {project_path}")

        # STUB: Phase 1 - Just return structure without real extraction
        # TODO Phase 2 (IMPL-003): Call run_coderef_command to get component data
        # TODO Phase 2 (IMPL-003): Transform CLI output to standard format
        # TODO Phase 2 (IMPL-003): Parse JSX/TSX, detect props and state

        return {
            "components": [],
            "error": None,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "placeholder",
            "note": "STUB - Phase 1 placeholder. Real extraction in Phase 2 (IMPL-003)"
        }

    except Exception as e:
        logger.warning(f"Component extraction failed: {str(e)}")
        return {
            "components": [],
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "error"
        }


# Module-level test function (for manual verification)
def _test_extractors() -> None:
    """
    Test extractor functions (manual verification only).

    This function is for development/debugging purposes.
    Run with: python -c "from extractors import _test_extractors; _test_extractors()"
    """
    print("Testing extractors...")

    # Dummy project path for testing
    test_project = r"C:\Users\willh\.mcp-servers\coderef-docs"

    # Test 1: extract_apis
    print("\n1. Testing extract_apis...")
    result = extract_apis(test_project)
    print(f"   ✓ Returned: {len(result.get('endpoints', []))} endpoints")
    print(f"   ✓ Source: {result.get('source')}")
    if result.get('error'):
        print(f"   ✗ Error: {result['error']}")

    # Test 2: extract_schemas
    print("\n2. Testing extract_schemas...")
    result = extract_schemas(test_project)
    print(f"   ✓ Returned: {len(result.get('entities', []))} entities")
    print(f"   ✓ Source: {result.get('source')}")
    if result.get('error'):
        print(f"   ✗ Error: {result['error']}")

    # Test 3: extract_components
    print("\n3. Testing extract_components...")
    result = extract_components(test_project)
    print(f"   ✓ Returned: {len(result.get('components', []))} components")
    print(f"   ✓ Source: {result.get('source')}")
    if result.get('error'):
        print(f"   ✗ Error: {result['error']}")

    print("\n✓ All extractor tests completed (Phase 1 stubs)")


if __name__ == "__main__":
    # Allow running as script for quick tests
    _test_extractors()
