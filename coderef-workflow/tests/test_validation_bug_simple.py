"""
Test script to reproduce the execute_plan validation bug.
"""

import json
from pathlib import Path
import sys

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent))

from schema_validator import get_checklist

def test_flat_structure_bug():
    print("=" * 80)
    print("REPRODUCING VALIDATION BUG")
    print("=" * 80)

    # Load the actual plan.json that's failing
    plan_path = Path(r"C:\Users\willh\.mcp-servers\coderef-docs\coderef\workorder\context-docs-integration\plan.json")

    if not plan_path.exists():
        print(f"ERROR: Plan file not found: {plan_path}")
        return

    with open(plan_path, 'r', encoding='utf-8') as f:
        plan_data = json.load(f)

    print(f"\nLoaded plan.json from: {plan_path}")
    print(f"File size: {plan_path.stat().st_size} bytes")

    # Analyze structure
    print("\nSTRUCTURE ANALYSIS:")
    print(f"  Top-level keys: {list(plan_data.keys())}")
    print(f"  Has UNIVERSAL_PLANNING_STRUCTURE: {'UNIVERSAL_PLANNING_STRUCTURE' in plan_data}")
    print(f"  Has 9_implementation_checklist at top-level: {'9_implementation_checklist' in plan_data}")

    structure = plan_data.get("UNIVERSAL_PLANNING_STRUCTURE", {})
    print(f"  UNIVERSAL_PLANNING_STRUCTURE keys: {list(structure.keys()) if structure else 'N/A (empty dict)'}")
    print(f"  Has 9_implementation_checklist in UNIVERSAL_PLANNING_STRUCTURE: {'9_implementation_checklist' in structure}")

    # Reproduce the validation logic from tool_handlers.py:2742-2746
    print("\nSIMULATING VALIDATION (tool_handlers.py:2742-2746):")
    has_checklist = (
        "9_implementation_checklist" in plan_data or
        "9_implementation_checklist" in structure
    )
    print(f"  Check #1: '9_implementation_checklist' in plan_data = {('9_implementation_checklist' in plan_data)}")
    print(f"  Check #2: '9_implementation_checklist' in structure = {('9_implementation_checklist' in structure)}")
    print(f"  has_checklist = {has_checklist}")
    print(f"  Validation result: {'PASS' if has_checklist else 'FAIL'}")

    # Now test get_checklist() which is called at line 2773
    print("\nSIMULATING get_checklist() (schema_validator.py:367):")
    section_9 = get_checklist(plan_data, strict=True)
    print(f"  Returned section_9 type: {type(section_9).__name__}")
    print(f"  Returned section_9 length: {len(section_9)} items")
    print(f"  Returned section_9 keys: {list(section_9.keys()) if isinstance(section_9, dict) else 'N/A'}")
    print(f"  Is empty: {not section_9}")

    # Check what should have been returned
    actual_section_9 = plan_data.get("9_implementation_checklist", {})
    print(f"\nWHAT SHOULD HAVE BEEN RETURNED:")
    print(f"  plan_data['9_implementation_checklist'] type: {type(actual_section_9).__name__}")
    print(f"  plan_data['9_implementation_checklist'] keys: {list(actual_section_9.keys()) if isinstance(actual_section_9, dict) else 'N/A'}")

    # Final verdict
    print("\n" + "=" * 80)
    print("ROOT CAUSE IDENTIFIED:")
    print("=" * 80)
    print("""
The plan.json uses a FLAT structure (sections at top level).
The get_checklist() function ONLY checks inside UNIVERSAL_PLANNING_STRUCTURE.

Validation code (line 2742-2746) checks BOTH:
  - Top-level: "9_implementation_checklist" in plan_data = TRUE
  - Nested: "9_implementation_checklist" in structure = FALSE
  Result: has_checklist = TRUE (PASSES)

But get_checklist() (line 2773 -> schema_validator.py:367) checks ONLY:
  - Nested: structure.get("9_implementation_checklist", {})
  Result: RETURNS EMPTY DICT (because not in UNIVERSAL_PLANNING_STRUCTURE)

SOLUTION:
Fix get_checklist() at schema_validator.py:386-387 to check BOTH:

  structure = plan.get("UNIVERSAL_PLANNING_STRUCTURE", {})
  section_9 = structure.get("9_implementation_checklist")

  # ADD THIS FALLBACK:
  if section_9 is None:
      section_9 = plan.get("9_implementation_checklist", {})
""")

    print(f"\nBUG STATUS: {'REPRODUCED' if not section_9 else 'NOT REPRODUCED'}")
    print("=" * 80)

if __name__ == "__main__":
    test_flat_structure_bug()
