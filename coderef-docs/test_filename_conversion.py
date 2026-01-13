"""
Test script for convert_subject_to_filename() function.
"""

import sys
sys.path.insert(0, '/c/Users/willh/.mcp-servers/coderef-docs')

from generators.resource_sheet_generator import convert_subject_to_filename

# Test cases
test_cases = [
    ("Auth Service", "Auth-Service-RESOURCE-SHEET.md"),
    ("AuthService", "Auth-Service-RESOURCE-SHEET.md"),
    ("Widget System", "Widget-System-RESOURCE-SHEET.md"),
    ("File API Route", "File-Api-Route-RESOURCE-SHEET.md"),
    ("User Controller", "User-Controller-RESOURCE-SHEET.md"),
    ("UserController", "User-Controller-RESOURCE-SHEET.md"),
    ("DATABASE MIGRATION", "Database-Migration-RESOURCE-SHEET.md"),
    ("api gateway", "Api-Gateway-RESOURCE-SHEET.md"),
]

print("Testing convert_subject_to_filename()...\n")
print("=" * 80)

passed = 0
failed = 0

for subject, expected in test_cases:
    try:
        result = convert_subject_to_filename(subject)
        status = "[PASS]" if result == expected else "[FAIL]"

        if result == expected:
            passed += 1
        else:
            failed += 1

        print(f"{status}")
        print(f"  Input:    {subject!r}")
        print(f"  Expected: {expected}")
        print(f"  Got:      {result}")
        print()
    except Exception as e:
        failed += 1
        print(f"[ERROR]")
        print(f"  Input:    {subject!r}")
        print(f"  Error:    {e}")
        print()

print("=" * 80)
print(f"Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")

if failed == 0:
    print("\n[SUCCESS] All tests passed!")
    sys.exit(0)
else:
    print(f"\n[FAILURE] {failed} test(s) failed")
    sys.exit(1)
