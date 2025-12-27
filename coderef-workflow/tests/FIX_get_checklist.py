"""
Fix for get_checklist() validation bug.

LOCATION: schema_validator.py lines 386-387

PROBLEM:
  get_checklist() only checks UNIVERSAL_PLANNING_STRUCTURE for section 9,
  but plan.json has flat structure with section 9 at top level.

SOLUTION:
  Add fallback to check top-level if not found in nested structure.

BEFORE:
  structure = plan.get("UNIVERSAL_PLANNING_STRUCTURE", {})
  section_9 = structure.get("9_implementation_checklist", {})

AFTER:
  structure = plan.get("UNIVERSAL_PLANNING_STRUCTURE", {})
  section_9 = structure.get("9_implementation_checklist")  # No default {}

  # Fallback to top-level (flat format)
  if section_9 is None:
      section_9 = plan.get("9_implementation_checklist", {})
"""

from pathlib import Path

def show_fix():
    """Display the exact changes needed."""

    schema_validator_path = Path(__file__).parent / "schema_validator.py"

    print("=" * 80)
    print("FIX FOR get_checklist() VALIDATION BUG")
    print("=" * 80)
    print(f"\nFile: {schema_validator_path}")
    print("Lines: 386-387")

    print("\n" + "=" * 80)
    print("CURRENT CODE (BUGGY):")
    print("=" * 80)
    print("""
def get_checklist(plan: dict, strict: bool = None) -> dict:
    if strict is None:
        strict = STRICT_MODE

    structure = plan.get("UNIVERSAL_PLANNING_STRUCTURE", {})
    section_9 = structure.get("9_implementation_checklist", {})  # ← BUG: Only checks nested

    # Expected format: dict with category keys like "pre_implementation", etc.
    if isinstance(section_9, dict):
        # ... normalization logic
""")

    print("\n" + "=" * 80)
    print("FIXED CODE:")
    print("=" * 80)
    print("""
def get_checklist(plan: dict, strict: bool = None) -> dict:
    if strict is None:
        strict = STRICT_MODE

    structure = plan.get("UNIVERSAL_PLANNING_STRUCTURE", {})
    section_9 = structure.get("9_implementation_checklist")  # ← Changed: No default {}

    # Fallback to top-level (flat format) - handles plans without UNIVERSAL_PLANNING_STRUCTURE
    if section_9 is None:
        section_9 = plan.get("9_implementation_checklist", {})

    # Expected format: dict with category keys like "pre_implementation", etc.
    if isinstance(section_9, dict):
        # ... normalization logic unchanged
""")

    print("\n" + "=" * 80)
    print("CHANGES REQUIRED:")
    print("=" * 80)
    print("""
1. Line 387: Remove default {} parameter
   FROM: section_9 = structure.get("9_implementation_checklist", {})
   TO:   section_9 = structure.get("9_implementation_checklist")

2. After line 387: Add fallback logic
   ADD:  # Fallback to top-level (flat format)
         if section_9 is None:
             section_9 = plan.get("9_implementation_checklist", {})
""")

    print("\n" + "=" * 80)
    print("WHY THIS WORKS:")
    print("=" * 80)
    print("""
1. Checks nested structure first (preferred schema format)
2. Falls back to top-level if not found (handles flat format)
3. Maintains backward compatibility with both formats
4. Aligns with validation logic in tool_handlers.py:2742-2746
5. No breaking changes to existing code
""")

    print("\n" + "=" * 80)
    print("TESTING:")
    print("=" * 80)
    print("""
After applying fix:

cd C:\\Users\\willh\\.mcp-servers\\coderef-workflow
python test_validation_bug_simple.py

Expected output:
  BUG STATUS: NOT REPRODUCED
  Returned section_9 length: 5 items
  Returned section_9 keys: ['phase_1_setup', 'phase_2_integration', ...]
""")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    show_fix()
