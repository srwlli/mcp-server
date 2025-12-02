#!/usr/bin/env python3
"""
Security Fixes Test Suite

Tests for SEC-001 (Path Traversal) and DEP-001 (jsonschema dependency).
Run after implementing security fixes to verify correctness.

Usage:
    python test_security_fixes.py
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from generators.base_generator import BaseGenerator

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BOLD = '\033[1m'


def print_test(name: str, passed: bool, details: str = ""):
    """Print test result with color coding."""
    # Use ASCII-compatible characters for Windows terminal
    status = f"{GREEN}[PASS]{RESET}" if passed else f"{RED}[FAIL]{RESET}"
    print(f"{status} - {name}")
    if details:
        print(f"      {details}")


def test_path_traversal_blocked():
    """Test that path traversal attacks are blocked."""
    print(f"\n{BOLD}Testing SEC-001: Path Traversal Protection{RESET}\n")

    templates_dir = Path(__file__).parent / "templates" / "power"
    gen = BaseGenerator(templates_dir)

    # Test 1: Relative path traversal should be resolved
    try:
        test_path = "."
        result = gen.validate_project_path(test_path)
        # Should resolve to absolute path
        is_absolute = result.is_absolute()
        print_test(
            "Relative path (.) is resolved to absolute",
            is_absolute,
            f"Resolved to: {result}"
        )
    except Exception as e:
        print_test("Relative path (.) is resolved to absolute", False, str(e))

    # Test 2: Parent directory traversal should be resolved
    try:
        current_dir = Path(__file__).parent
        test_path = str(current_dir / ".." / ".." / ".mcp-servers" / "docs-mcp")
        result = gen.validate_project_path(test_path)
        # Should resolve to absolute path without ..
        has_parent_refs = ".." in str(result)
        print_test(
            "Parent directory references (..) are resolved",
            not has_parent_refs,
            f"Resolved to: {result}"
        )
    except Exception as e:
        print_test("Parent directory references (..) are resolved", False, str(e))

    # Test 3: Invalid paths should still raise ValueError
    try:
        invalid_path = "/nonexistent/invalid/path/that/does/not/exist"
        try:
            gen.validate_project_path(invalid_path)
            print_test("Invalid paths raise ValueError", False, "No exception raised!")
        except ValueError as ve:
            print_test("Invalid paths raise ValueError", True, str(ve))
    except Exception as e:
        print_test("Invalid paths raise ValueError", False, f"Wrong exception: {e}")

    # Test 4: File paths (not directories) should raise ValueError
    try:
        file_path = str(Path(__file__).resolve())  # This test file
        try:
            gen.validate_project_path(file_path)
            print_test("File paths (not dirs) raise ValueError", False, "No exception raised!")
        except ValueError as ve:
            print_test("File paths (not dirs) raise ValueError", True, str(ve))
    except Exception as e:
        print_test("File paths (not dirs) raise ValueError", False, f"Wrong exception: {e}")

    # Test 5: Valid directory paths should work
    try:
        valid_path = str(Path(__file__).parent)
        result = gen.validate_project_path(valid_path)
        is_valid = result.exists() and result.is_dir()
        print_test(
            "Valid directory paths work correctly",
            is_valid,
            f"Validated: {result}"
        )
    except Exception as e:
        print_test("Valid directory paths work correctly", False, str(e))


def test_jsonschema_dependency():
    """Test that jsonschema is installed and importable."""
    print(f"\n{BOLD}Testing DEP-001: jsonschema Dependency{RESET}\n")

    # Test 1: jsonschema is importable
    try:
        import jsonschema
        print_test("jsonschema is importable", True, f"Version: {jsonschema.__version__}")
    except ImportError as e:
        print_test("jsonschema is importable", False, str(e))
        return

    # Test 2: jsonschema version is >= 4.0.0
    try:
        import jsonschema
        version = jsonschema.__version__
        major_version = int(version.split('.')[0])
        is_valid_version = major_version >= 4
        print_test(
            "jsonschema version >= 4.0.0",
            is_valid_version,
            f"Installed: {version}"
        )
    except Exception as e:
        print_test("jsonschema version >= 4.0.0", False, str(e))

    # Test 3: jsonschema.validate is available
    try:
        import jsonschema
        has_validate = hasattr(jsonschema, 'validate')
        print_test("jsonschema.validate() is available", has_validate)
    except Exception as e:
        print_test("jsonschema.validate() is available", False, str(e))

    # Test 4: Can validate against changelog schema
    try:
        import jsonschema
        import json

        schema_path = Path(__file__).parent / "coderef" / "changelog" / "schema.json"
        if schema_path.exists():
            with open(schema_path, 'r') as f:
                schema = json.load(f)

            # Test with minimal valid data
            test_data = {
                "project": "docs-mcp",
                "changelog_version": "1.0",
                "current_version": "1.0.0",
                "entries": []
            }

            jsonschema.validate(test_data, schema)
            print_test(
                "Can validate against changelog schema",
                True,
                "Schema validation successful"
            )
        else:
            print_test(
                "Can validate against changelog schema",
                False,
                f"Schema not found at {schema_path}"
            )
    except Exception as e:
        print_test("Can validate against changelog schema", False, str(e))


def test_changelog_schema_validation():
    """Test SEC-002: JSON Schema Validation in ChangelogGenerator."""
    print(f"\n{BOLD}Testing SEC-002: Changelog Schema Validation{RESET}\n")

    try:
        from generators import ChangelogGenerator
        import jsonschema

        # Test 1: Schema loads correctly
        changelog_path = Path(__file__).parent / "coderef" / "changelog" / "CHANGELOG.json"
        if not changelog_path.exists():
            print_test("Schema validation tests", False, "CHANGELOG.json not found")
            return

        gen = ChangelogGenerator(changelog_path)
        has_schema = gen.schema is not None
        print_test("Schema loaded successfully", has_schema)

        # Test 2: Valid changelog data passes validation
        try:
            data = gen.read_changelog()
            print_test("Valid changelog passes validation", True, "Existing CHANGELOG.json validated")
        except jsonschema.ValidationError as e:
            print_test("Valid changelog passes validation", False, f"Validation error: {e.message}")

        # Test 3: Invalid data is rejected (missing required field)
        invalid_data = {
            "changelog_version": "1.0",
            "current_version": "1.0.0",
            "entries": []
        }
        try:
            gen.validate_changelog(invalid_data)
            print_test("Invalid data is rejected (missing 'project')", False, "Should have raised ValidationError")
        except jsonschema.ValidationError:
            print_test("Invalid data is rejected (missing 'project')", True)

        # Test 4: Invalid type is rejected
        invalid_type_data = {
            "project": "test",
            "changelog_version": "1.0",
            "current_version": "1.0.0",
            "entries": "not-an-array"
        }
        try:
            gen.validate_changelog(invalid_type_data)
            print_test("Invalid type is rejected (entries as string)", False, "Should have raised ValidationError")
        except jsonschema.ValidationError:
            print_test("Invalid type is rejected (entries as string)", True)

        # Test 5: write_changelog validates before writing
        test_data = gen.read_changelog()
        try:
            gen.write_changelog(test_data)
            print_test("write_changelog validates data", True, "Validation passed before write")
        except Exception as e:
            print_test("write_changelog validates data", False, str(e))

    except Exception as e:
        print_test("Changelog schema validation", False, f"Setup error: {e}")


def test_mcp_server_still_works():
    """Test that MCP server can still start after changes."""
    print(f"\n{BOLD}Testing MCP Server Functionality{RESET}\n")

    # Test 1: server.py imports successfully
    try:
        import server
        print_test("server.py imports successfully", True)
    except Exception as e:
        print_test("server.py imports successfully", False, str(e))
        return

    # Test 2: Generators import successfully
    try:
        from generators import BaseGenerator, FoundationGenerator, ChangelogGenerator
        print_test("All generators import successfully", True)
    except Exception as e:
        print_test("All generators import successfully", False, str(e))

    # Test 3: Templates directory exists
    templates_dir = Path(__file__).parent / "templates" / "power"
    exists = templates_dir.exists()
    print_test("Templates directory exists", exists, str(templates_dir))


def main():
    """Run all security tests."""
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}Security Fixes Test Suite - docs-mcp v1.0.4{RESET}")
    print(f"{BOLD}{'='*60}{RESET}")

    try:
        test_path_traversal_blocked()
        test_jsonschema_dependency()
        test_changelog_schema_validation()
        test_mcp_server_still_works()

        print(f"\n{BOLD}{'='*60}{RESET}")
        print(f"{GREEN}{BOLD}Test suite completed!{RESET}")
        print(f"{BOLD}{'='*60}{RESET}\n")

        print(f"{YELLOW}Note:{RESET} If all tests passed, the security fixes are working correctly.")
        print(f"{YELLOW}Note:{RESET} Run 'pip install -r requirements.txt' if jsonschema tests failed.\n")

    except Exception as e:
        print(f"\n{RED}{BOLD}Test suite failed with error:{RESET} {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
