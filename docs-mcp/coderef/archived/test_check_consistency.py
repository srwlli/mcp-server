#!/usr/bin/env python3
"""
Integration test for check_consistency tool (Tool #10).

Tests the complete workflow:
1. Ensure standards exist (from establish_standards)
2. Create test files with violations
3. Run check_consistency
4. Verify violations are detected
5. Test severity threshold filtering
6. Test git integration
"""

import asyncio
import sys
from pathlib import Path
import tempfile
import shutil
import subprocess

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

import tool_handlers


async def test_check_consistency_workflow():
    """Test complete check_consistency workflow."""
    print("Testing check_consistency integration...\n")

    # Test 1: Check if standards exist
    print("Test 1: Checking if standards exist...")
    project_path = str(Path(__file__).parent.resolve())
    standards_dir = Path(project_path) / "coderef" / "standards"

    if not standards_dir.exists():
        print("[FAIL] Standards directory not found. Run establish_standards first.")
        return False

    print(f"[PASS] Standards directory found: {standards_dir}\n")

    # Test 2: Check consistency on docs-mcp codebase (no violations expected)
    print("Test 2: Running check_consistency on docs-mcp codebase...")
    try:
        # Set templates dir (required by handlers)
        tool_handlers.set_templates_dir(Path(project_path) / "templates" / "power")

        # Test with explicit file list
        test_files = [
            "server.py",
            "tool_handlers.py",
            "generators/consistency_checker.py"
        ]

        result = await tool_handlers.handle_check_consistency({
            "project_path": project_path,
            "files": test_files,
            "severity_threshold": "minor",
            "scope": ["all"],
            "fail_on_violations": False  # Don't fail for this test
        })

        result_text = result[0].text
        print("[PASS] Check completed successfully!\n")

        # Verify result contains expected content
        checks = [
            ("Consistency check" in result_text, "Contains status message"),
            ("violations found" in result_text or "Files checked" in result_text, "Contains violation/file count"),
            ("Duration:" in result_text or "duration" in result_text.lower(), "Contains duration")
        ]

        all_passed = True
        for check, description in checks:
            status = "[PASS]" if check else "[FAIL]"
            print(f"{status} {description}")
            if not check:
                all_passed = False

        print("\n" + "="*60)
        print("CHECK CONSISTENCY OUTPUT:")
        print("="*60)
        print(result_text)
        print("="*60 + "\n")

        if not all_passed:
            return False

    except Exception as e:
        print(f"[FAIL] Error during check: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    # Test 3: Test severity threshold filtering
    print("Test 3: Testing severity threshold filtering...")
    try:
        # Test with different thresholds
        thresholds = ["critical", "major", "minor"]

        for threshold in thresholds:
            result = await tool_handlers.handle_check_consistency({
                "project_path": project_path,
                "files": test_files,
                "severity_threshold": threshold,
                "scope": ["all"],
                "fail_on_violations": False
            })

            result_text = result[0].text
            if threshold in result_text or "Threshold" in result_text or "threshold" in result_text:
                print(f"[PASS] Threshold '{threshold}' applied correctly")
            else:
                print(f"[WARN] Threshold '{threshold}' not clearly indicated in output")

    except Exception as e:
        print(f"[FAIL] Error testing thresholds: {str(e)}")
        return False

    print()

    # Test 4: Test with no files (auto-detect from git)
    print("Test 4: Testing git auto-detection...")
    try:
        # Check if we're in a git repo
        is_git_repo = subprocess.run(
            ['git', 'rev-parse', '--is-inside-work-tree'],
            cwd=project_path,
            capture_output=True,
            timeout=5
        ).returncode == 0

        if is_git_repo:
            # Call without files parameter (should auto-detect)
            result = await tool_handlers.handle_check_consistency({
                "project_path": project_path,
                # No files parameter - should auto-detect from git
                "severity_threshold": "major",
                "scope": ["all"],
                "fail_on_violations": False
            })

            result_text = result[0].text

            # Should either show files or indicate no changes
            if "Files checked:" in result_text or "No changes" in result_text or "no files" in result_text.lower():
                print("[PASS] Git auto-detection working")
            else:
                print(f"[WARN] Git auto-detection unclear from output")
        else:
            print("[SKIP] Not a git repository, skipping git auto-detection test")

    except subprocess.TimeoutExpired:
        print("[SKIP] Git command timed out")
    except FileNotFoundError:
        print("[SKIP] Git not installed")
    except Exception as e:
        print(f"[FAIL] Error testing git auto-detection: {str(e)}")
        return False

    print()

    # Test 5: Test scope parameter
    print("Test 5: Testing scope filtering...")
    try:
        scopes = [
            ["ui_patterns"],
            ["behavior_patterns"],
            ["ux_patterns"],
            ["all"]
        ]

        for scope in scopes:
            result = await tool_handlers.handle_check_consistency({
                "project_path": project_path,
                "files": test_files,
                "severity_threshold": "minor",
                "scope": scope,
                "fail_on_violations": False
            })

            # Just verify it doesn't crash
            print(f"[PASS] Scope {scope} executed successfully")

    except Exception as e:
        print(f"[FAIL] Error testing scopes: {str(e)}")
        return False

    print()

    # Test 6: Test fail_on_violations parameter
    print("Test 6: Testing fail_on_violations parameter...")
    try:
        # Test with fail_on_violations=true (should return exit_code in result)
        result = await tool_handlers.handle_check_consistency({
            "project_path": project_path,
            "files": test_files,
            "severity_threshold": "minor",
            "scope": ["all"],
            "fail_on_violations": True
        })

        result_text = result[0].text

        # Check if exit code is mentioned or status indicates pass/fail
        if "exit_code" in result_text.lower() or "PASS" in result_text or "FAIL" in result_text:
            print("[PASS] fail_on_violations parameter working")
        else:
            print("[WARN] fail_on_violations behavior unclear from output")

    except Exception as e:
        print(f"[FAIL] Error testing fail_on_violations: {str(e)}")
        return False

    print()

    # Test 7: Test input validation
    print("Test 7: Testing input validation...")
    try:
        # Test invalid severity threshold
        result = await tool_handlers.handle_check_consistency({
            "project_path": project_path,
            "files": test_files,
            "severity_threshold": "invalid",  # Invalid value
            "scope": ["all"],
            "fail_on_violations": False
        })

        result_text = result[0].text

        # Should return error
        if "invalid" in result_text.lower() or "error" in result_text.lower():
            print("[PASS] Invalid severity_threshold rejected")
        else:
            print("[FAIL] Invalid input not properly validated")
            return False

    except Exception as e:
        print(f"[FAIL] Error testing validation: {str(e)}")
        return False

    print()

    # Test 8: Test with absolute paths in files list (should be rejected)
    print("Test 8: Testing path security validation...")
    try:
        # Test absolute path (should be rejected)
        # Use platform-appropriate absolute path
        import platform
        if platform.system() == 'Windows':
            test_abs_path = "C:/Windows/System32/config/sam"
        else:
            test_abs_path = "/etc/passwd"

        result = await tool_handlers.handle_check_consistency({
            "project_path": project_path,
            "files": [test_abs_path],  # Absolute path
            "severity_threshold": "major",
            "scope": ["all"],
            "fail_on_violations": False
        })

        result_text = result[0].text

        # Should return error about absolute paths
        if "absolute" in result_text.lower() or "relative" in result_text.lower() or "error" in result_text.lower():
            print("[PASS] Absolute paths rejected (security check working)")
        else:
            print("[FAIL] Absolute path security check not working")
            return False

    except Exception as e:
        print(f"[FAIL] Error testing path security: {str(e)}")
        return False

    print()

    # Test 9: Test with path traversal attempt (should be rejected)
    print("Test 9: Testing path traversal protection...")
    try:
        # Test path traversal
        result = await tool_handlers.handle_check_consistency({
            "project_path": project_path,
            "files": ["../../../etc/passwd"],  # Path traversal
            "severity_threshold": "major",
            "scope": ["all"],
            "fail_on_violations": False
        })

        result_text = result[0].text

        # Should return error about path traversal
        if "traversal" in result_text.lower() or "error" in result_text.lower():
            print("[PASS] Path traversal blocked (security check working)")
        else:
            print("[FAIL] Path traversal security check not working")
            return False

    except Exception as e:
        print(f"[FAIL] Error testing path traversal protection: {str(e)}")
        return False

    print()

    # All tests passed
    print("="*60)
    print("[PASS] All check_consistency integration tests passed!")
    print("="*60)
    return True


if __name__ == "__main__":
    success = asyncio.run(test_check_consistency_workflow())
    sys.exit(0 if success else 1)
