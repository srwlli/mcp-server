#!/usr/bin/env python3
"""
Test SEC-004 and SEC-005 security fixes.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from generators.base_generator import BaseGenerator

# Color codes
GREEN = '\033[92m'
RED = '\033[91m'
BOLD = '\033[1m'
RESET = '\033[0m'


def print_test(name: str, passed: bool, details: str = ""):
    """Print test result with color coding."""
    status = f"{GREEN}[PASS]{RESET}" if passed else f"{RED}[FAIL]{RESET}"
    print(f"{status} - {name}")
    if details:
        print(f"      {details}")


def test_sec_005():
    """Test SEC-005: Template name sanitization."""
    print(f"\n{BOLD}Testing SEC-005: Template Name Sanitization{RESET}\n")

    templates_dir = Path(__file__).parent / "templates" / "power"
    gen = BaseGenerator(templates_dir)

    # Test 1: Valid template names should work
    try:
        result = gen._sanitize_template_name("readme")
        print_test("Valid template name 'readme' accepted", result == "readme")
    except Exception as e:
        print_test("Valid template name 'readme' accepted", False, str(e))

    # Test 2: Valid name with hyphen
    try:
        result = gen._sanitize_template_name("user-guide")
        print_test("Valid template name 'user-guide' accepted", result == "user-guide")
    except Exception as e:
        print_test("Valid template name 'user-guide' accepted", False, str(e))

    # Test 3: Path traversal with ../ should be blocked
    try:
        result = gen._sanitize_template_name("../../etc/passwd")
        print_test("Path traversal '../../../etc/passwd' blocked", False, "Should have raised ValueError!")
    except ValueError as e:
        print_test("Path traversal '../../etc/passwd' blocked", True, str(e))
    except Exception as e:
        print_test("Path traversal '../../etc/passwd' blocked", False, f"Wrong exception: {e}")

    # Test 4: Path with ./ should be blocked
    try:
        result = gen._sanitize_template_name("./template")
        print_test("Path with './' blocked", False, "Should have raised ValueError!")
    except ValueError as e:
        print_test("Path with './' blocked", True, str(e))
    except Exception as e:
        print_test("Path with './' blocked", False, f"Wrong exception: {e}")

    # Test 5: Path with / should be blocked
    try:
        result = gen._sanitize_template_name("path/to/template")
        print_test("Path with '/' blocked", False, "Should have raised ValueError!")
    except ValueError as e:
        print_test("Path with '/' blocked", True, str(e))
    except Exception as e:
        print_test("Path with '/' blocked", False, f"Wrong exception: {e}")

    # Test 6: Empty string should be blocked
    try:
        result = gen._sanitize_template_name("")
        print_test("Empty string blocked", False, "Should have raised ValueError!")
    except ValueError as e:
        print_test("Empty string blocked", True, str(e))
    except Exception as e:
        print_test("Empty string blocked", False, f"Wrong exception: {e}")

    # Test 7: Special characters should be blocked
    try:
        result = gen._sanitize_template_name("template@#$")
        print_test("Special characters blocked", False, "Should have raised ValueError!")
    except ValueError as e:
        print_test("Special characters blocked", True, str(e))
    except Exception as e:
        print_test("Special characters blocked", False, f"Wrong exception: {e}")


def test_sec_004():
    """Test SEC-004: ValidationError handling in server.py."""
    print(f"\n{BOLD}Testing SEC-004: ValidationError Handling{RESET}\n")

    # We can verify the import exists
    try:
        import server
        has_jsonschema = hasattr(server, 'jsonschema')
        print_test("server.py imports jsonschema", has_jsonschema)
    except Exception as e:
        print_test("server.py imports jsonschema", False, str(e))

    # Verify that ValidationError is handled (by reading server.py)
    try:
        server_path = Path(__file__).parent / "server.py"
        with open(server_path, 'r', encoding='utf-8') as f:
            server_code = f.read()

        has_import = "import jsonschema" in server_code
        has_handler_1 = "except jsonschema.ValidationError as e:" in server_code
        count = server_code.count("except jsonschema.ValidationError as e:")

        print_test("jsonschema imported in server.py", has_import)
        print_test("ValidationError handler in get_changelog", has_handler_1 and count >= 1)
        print_test("ValidationError handler in add_changelog_entry", count >= 2, f"Found {count} handlers")

    except Exception as e:
        print_test("ValidationError handlers present", False, str(e))


def main():
    """Run all tests."""
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}SEC-004/005 Security Fixes Test Suite{RESET}")
    print(f"{BOLD}{'='*60}{RESET}")

    test_sec_005()
    test_sec_004()

    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{GREEN}{BOLD}Test suite completed!{RESET}")
    print(f"{BOLD}{'='*60}{RESET}\n")


if __name__ == "__main__":
    main()
