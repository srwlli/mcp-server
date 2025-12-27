"""
Code intelligence extractors for foundation documentation.

Provides extraction functions that call @coderef/core CLI to extract:
- API endpoints (routes, methods, parameters)
- Database schemas (entities, fields, relationships)
- Component definitions (React/Vue components, props, hierarchy)

Part of WO-CONTEXT-DOCS-INTEGRATION-001 Phase 2.

Real implementation with caching and error handling.
"""

import json
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from pathlib import Path
from functools import lru_cache

from cli_utils import run_coderef_command, get_cli_path, validate_cli_available
from logger_config import logger


@lru_cache(maxsize=32)
def extract_apis(project_path: str) -> Dict[str, Any]:
    """
    Extract API endpoints from project using @coderef/core CLI.

    Scans the project codebase to discover API routes, HTTP methods,
    parameters, and descriptions. Works with Express, FastAPI, Flask, etc.

    Args:
        project_path: Absolute path to project directory

    Returns:
        dict with keys:
            - endpoints: list of dicts with {method, path, params, response, description}
            - error: str if extraction failed (or None if successful)
            - timestamp: ISO 8601 timestamp when extraction happened
            - source: "coderef-cli" or "placeholder"

    Example:
        >>> result = extract_apis("/path/to/project")
        >>> if "error" not in result:
        ...     for endpoint in result["endpoints"]:
        ...         print(f"{endpoint['method']} {endpoint['path']}")

    Phase 2 Implementation (INTEGRATE-001):
        Calls @coderef/core CLI to scan for API patterns, transforms to standard format.
    """
    try:
        logger.info(f"extract_apis called for project: {project_path}")

        # Check if CLI is available
        if not validate_cli_available():
            logger.warning("CLI not available, returning empty results")
            return {
                "endpoints": [],
                "error": None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "placeholder"
            }

        # Phase 2 (INTEGRATE-001): Call coderef-context CLI to scan for API patterns
        # Use 'scan' command to find all code elements, then filter for API patterns
        cli_result = run_coderef_command(
            "scan",
            args=["--project", project_path, "--output", "json"],
            timeout=120
        )

        # Check for errors
        if "error" in cli_result:
            logger.warning(f"CLI scan failed: {cli_result['error']}")
            return {
                "endpoints": [],
                "error": cli_result["error"],
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "error"
            }

        # Transform CLI output to standard API endpoint format
        endpoints = []
        elements = cli_result.get("elements", [])

        # Parse elements looking for API route patterns
        for element in elements:
            # Look for route decorators/patterns (FastAPI, Flask, Express, etc.)
            element_type = element.get("type", "")
            element_name = element.get("name", "")
            element_file = element.get("file", "")

            # Pattern matching for API frameworks
            # FastAPI: @app.get("/users"), @router.post("/auth/login")
            # Flask: @app.route("/users", methods=["GET"])
            # Express: app.get("/users", ...)

            if any(keyword in element_name.lower() for keyword in ["route", "endpoint", "api"]) or \
               any(keyword in element_file.lower() for keyword in ["routes", "api", "endpoints"]):

                # Extract HTTP method from decorator or function name
                method = "GET"  # default
                if any(m in element_name.lower() for m in ["post", "create"]):
                    method = "POST"
                elif any(m in element_name.lower() for m in ["put", "update"]):
                    method = "PUT"
                elif any(m in element_name.lower() for m in ["delete", "remove"]):
                    method = "DELETE"
                elif any(m in element_name.lower() for m in ["patch"]):
                    method = "PATCH"

                # Extract path from element metadata or name
                # This is simplified - real implementation would parse decorators
                path = element.get("path", f"/{element_name.replace('_', '/').lower()}")

                # Extract parameters (simplified - would need AST parsing)
                params = []
                if "params" in element:
                    params = element.get("params", [])

                # Build endpoint entry
                endpoint = {
                    "method": method,
                    "path": path,
                    "params": params,
                    "response": element.get("return_type", "unknown"),
                    "description": element.get("description", f"{method} endpoint at {path}")
                }

                endpoints.append(endpoint)

        logger.info(f"Extracted {len(endpoints)} API endpoints from {len(elements)} code elements")

        return {
            "endpoints": endpoints,
            "error": None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "coderef-cli" if endpoints else "placeholder"
        }

    except Exception as e:
        logger.warning(f"API extraction failed: {str(e)}")
        return {
            "endpoints": [],
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "error"
        }


@lru_cache(maxsize=32)
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

    Phase 2 Implementation (INTEGRATE-002):
        Calls @coderef/core CLI to scan for model/schema files, transforms to standard format.
    """
    try:
        logger.info(f"extract_schemas called for project: {project_path}")

        # Check if CLI is available
        if not validate_cli_available():
            logger.warning("CLI not available, returning empty results")
            return {
                "entities": [],
                "error": None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "placeholder"
            }

        # Phase 2 (INTEGRATE-002): Call coderef-context CLI to scan for schema/model patterns
        # Use 'scan' command to find all code elements, then filter for models/schemas
        cli_result = run_coderef_command(
            "scan",
            args=["--project", project_path, "--output", "json"],
            timeout=120
        )

        # Check for errors
        if "error" in cli_result:
            logger.warning(f"CLI scan failed: {cli_result['error']}")
            return {
                "entities": [],
                "error": cli_result["error"],
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "error"
            }

        # Transform CLI output to standard schema/entity format
        entities = []
        elements = cli_result.get("elements", [])

        # Parse elements looking for model/schema patterns
        for element in elements:
            element_type = element.get("type", "")
            element_name = element.get("name", "")
            element_file = element.get("file", "")

            # Pattern matching for ORM frameworks
            # SQLAlchemy: class User(Base), class Post(db.Model)
            # TypeORM: @Entity() class User
            # Prisma: model User { ... }
            # Mongoose: const userSchema = new Schema({ ... })

            if element_type in ["class", "model", "entity"] or \
               any(keyword in element_file.lower() for keyword in ["model", "schema", "entity", "db"]):

                # Extract fields from class/model definition
                fields = []
                properties = element.get("properties", []) or element.get("fields", [])

                for prop in properties:
                    if isinstance(prop, dict):
                        field = {
                            "name": prop.get("name", "unknown"),
                            "type": prop.get("type", "unknown"),
                            "constraints": prop.get("constraints", [])
                        }
                        fields.append(field)
                    elif isinstance(prop, str):
                        # Simple field name without metadata
                        fields.append({
                            "name": prop,
                            "type": "unknown",
                            "constraints": []
                        })

                # Extract relationships (hasMany, belongsTo, etc.)
                relationships = []
                # Look for relationship keywords in element metadata
                if "relationships" in element:
                    for rel in element.get("relationships", []):
                        relationship = {
                            "type": rel.get("type", "unknown"),
                            "target": rel.get("target", "unknown"),
                            "foreignKey": rel.get("foreignKey", "")
                        }
                        relationships.append(relationship)

                # Build entity entry
                entity = {
                    "name": element_name,
                    "fields": fields,
                    "relationships": relationships
                }

                entities.append(entity)

        logger.info(f"Extracted {len(entities)} schema entities from {len(elements)} code elements")

        return {
            "entities": entities,
            "error": None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "coderef-cli" if entities else "placeholder"
        }

    except Exception as e:
        logger.warning(f"Schema extraction failed: {str(e)}")
        return {
            "entities": [],
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "error"
        }


@lru_cache(maxsize=32)
def extract_components(project_path: str) -> Dict[str, Any]:
    """
    Extract component definitions from project using @coderef/core CLI.

    Scans the project codebase to discover UI components, their props,
    state, and hierarchy. Works with React, Vue, Svelte, Angular, etc.

    Args:
        project_path: Absolute path to project directory

    Returns:
        dict with keys:
            - components: list of component dicts with {name, type, props, children, description}
            - error: str if extraction failed (or None if successful)
            - timestamp: ISO 8601 timestamp when extraction happened
            - source: "coderef-cli" or "placeholder"

    Example:
        >>> result = extract_components("/path/to/project")
        >>> if "error" not in result:
        ...     for component in result["components"]:
        ...         print(f"Component: {component['name']} ({len(component.get('props', []))} props)")

    Phase 2 Implementation (INTEGRATE-003):
        Calls @coderef/core CLI to scan for component files, transforms to standard format.
    """
    try:
        logger.info(f"extract_components called for project: {project_path}")

        # Check if CLI is available
        if not validate_cli_available():
            logger.warning("CLI not available, returning empty results")
            return {
                "components": [],
                "error": None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "placeholder"
            }

        # Phase 2 (INTEGRATE-003): Call coderef-context CLI to scan for component patterns
        # Use 'scan' command to find all code elements, then filter for components
        cli_result = run_coderef_command(
            "scan",
            args=["--project", project_path, "--output", "json"],
            timeout=120
        )

        # Check for errors
        if "error" in cli_result:
            logger.warning(f"CLI scan failed: {cli_result['error']}")
            return {
                "components": [],
                "error": cli_result["error"],
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "error"
            }

        # Transform CLI output to standard component format
        components = []
        elements = cli_result.get("elements", [])

        # Parse elements looking for component patterns
        for element in elements:
            element_type = element.get("type", "")
            element_name = element.get("name", "")
            element_file = element.get("file", "")

            # Pattern matching for component frameworks
            # React: function Button(props), const Modal = ({...}), class App extends Component
            # Vue: export default { name: 'Button', ... }
            # Svelte: <script> export let ... </script>

            # Check if file is a component file (.tsx, .jsx, .vue, .svelte)
            is_component_file = any(ext in element_file.lower() for ext in [".tsx", ".jsx", ".vue", ".svelte"])

            # Check if element is a component (function, class, or export with component-like name)
            is_component_type = element_type in ["function", "class", "component", "export"]

            # Component naming convention (starts with uppercase)
            is_component_name = element_name and element_name[0].isupper()

            if is_component_file and is_component_type and is_component_name:
                # Extract props from function parameters or class properties
                props = []
                params = element.get("params", []) or element.get("properties", [])

                for param in params:
                    if isinstance(param, dict):
                        prop = {
                            "name": param.get("name", "unknown"),
                            "type": param.get("type", "unknown"),
                            "default": param.get("default", None),
                            "required": param.get("required", False)
                        }
                        props.append(prop)
                    elif isinstance(param, str):
                        # Simple param name without metadata
                        props.append({
                            "name": param,
                            "type": "unknown",
                            "default": None,
                            "required": False
                        })

                # Extract child components (components used within this component)
                children = []
                # Look for import statements or JSX usage
                if "dependencies" in element:
                    for dep in element.get("dependencies", []):
                        # Filter for component-like dependencies
                        dep_name = dep if isinstance(dep, str) else dep.get("name", "")
                        if dep_name and dep_name[0].isupper():
                            children.append(dep_name)

                # Determine component type
                comp_type = "Functional Component"
                if element_type == "class":
                    comp_type = "Class Component"
                elif "vue" in element_file.lower():
                    comp_type = "Vue Component"
                elif "svelte" in element_file.lower():
                    comp_type = "Svelte Component"

                # Build component entry
                component = {
                    "name": element_name,
                    "type": comp_type,
                    "props": props,
                    "children": children,
                    "description": element.get("description", f"{comp_type}: {element_name}")
                }

                components.append(component)

        logger.info(f"Extracted {len(components)} UI components from {len(elements)} code elements")

        return {
            "components": components,
            "error": None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "coderef-cli" if components else "placeholder"
        }

    except Exception as e:
        logger.warning(f"Component extraction failed: {str(e)}")
        return {
            "components": [],
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat(),
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
    print(f"   [OK] Returned: {len(result.get('endpoints', []))} endpoints")
    print(f"   [OK] Source: {result.get('source')}")
    if result.get('error'):
        print(f"   [ERR] Error: {result['error']}")

    # Test 2: extract_schemas
    print("\n2. Testing extract_schemas...")
    result = extract_schemas(test_project)
    print(f"   [OK] Returned: {len(result.get('entities', []))} entities")
    print(f"   [OK] Source: {result.get('source')}")
    if result.get('error'):
        print(f"   [ERR] Error: {result['error']}")

    # Test 3: extract_components
    print("\n3. Testing extract_components...")
    result = extract_components(test_project)
    print(f"   [OK] Returned: {len(result.get('components', []))} components")
    print(f"   [OK] Source: {result.get('source')}")
    if result.get('error'):
        print(f"   [ERR] Error: {result['error']}")

    print("\n[OK] All extractor tests completed (Phase 2 integration)")


if __name__ == "__main__":
    # Allow running as script for quick tests
    _test_extractors()
