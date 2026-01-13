#!/usr/bin/env python3
"""
Test script for ResourceSheetValidator enhancements
Tests directory location and filename format validation
"""

from pathlib import Path
from papertrail.validators.resource_sheet import ResourceSheetValidator

def test_validator():
    """Test the enhanced ResourceSheetValidator"""
    validator = ResourceSheetValidator()

    # Test files
    test_files = [
        # Existing resource sheets (may have issues)
        "C:/Users/willh/.mcp-servers/papertrail/coderef/resource/PAPERTRAIL-RESOURCE-SHEET.md",
        "C:/Users/willh/.mcp-servers/papertrail/docs/PAPERTRAIL-SERVER-RESOURCE-SHEET.md",
        "C:/Users/willh/.mcp-servers/papertrail/docs/UDS-Validation-RESOURCE-SHEET.md",
    ]

    print("=" * 80)
    print("RESOURCE SHEET VALIDATOR TEST")
    print("=" * 80)
    print()

    for file_path_str in test_files:
        file_path = Path(file_path_str)

        if not file_path.exists():
            print(f"[SKIP] {file_path.name} (file not found)")
            print()
            continue

        print(f"Testing: {file_path.name}")
        print(f"Path: {file_path.parent}")
        print("-" * 80)

        try:
            result = validator.validate_file(file_path)

            # Display results
            if result.valid:
                print(f"[PASS] VALID - Score: {result.score}/100")
            else:
                print(f"[FAIL] INVALID - Score: {result.score}/100")

            # Show errors
            if result.errors:
                print(f"\nErrors ({len(result.errors)}):")
                for error in result.errors:
                    severity_marker = "[CRITICAL]" if error.severity.name == "CRITICAL" else "[MAJOR]" if error.severity.name == "MAJOR" else "[MINOR]"
                    field_info = f" [{error.field}]" if error.field else ""
                    print(f"  {severity_marker}{field_info}: {error.message}")

            # Show warnings
            if result.warnings:
                print(f"\nWarnings ({len(result.warnings)}):")
                for warning in result.warnings:
                    print(f"  [WARN] {warning}")

        except Exception as e:
            print(f"[ERROR] {e}")

        print()
        print("=" * 80)
        print()

if __name__ == "__main__":
    test_validator()
