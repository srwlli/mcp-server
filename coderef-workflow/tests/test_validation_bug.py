"""
Test script to reproduce the execute_plan validation bug.

ROOT CAUSE IDENTIFIED:
======================

The plan.json file uses a FLAT structure (all sections at top level):
{
  "META_DOCUMENTATION": {...},
  "0_PREPARATION": {...},
  "1_EXECUTIVE_SUMMARY": {...},
  ...
  "9_implementation_checklist": {...}
}

But the validation code in tool_handlers.py expects a NESTED structure:
{
  "META_DOCUMENTATION": {...},  # Top level
  "UNIVERSAL_PLANNING_STRUCTURE": {  # Nested wrapper
    "0_PREPARATION": {...},
    "1_EXECUTIVE_SUMMARY": {...},
    ...
    "9_implementation_checklist": {...}
  }
}

VALIDATION LOGIC (tool_handlers.py:2732-2753):
------------------------------------------------
Line 2732: structure = plan_data.get("UNIVERSAL_PLANNING_STRUCTURE", {})
Line 2742-2746:
    has_checklist = (
        "9_implementation_checklist" in plan_data or
        "9_implementation_checklist" in structure
    )

The code checks BOTH:
1. Top-level plan_data for "9_implementation_checklist"
2. Nested structure for "9_implementation_checklist"

BUT the plan.json has:
- No UNIVERSAL_PLANNING_STRUCTURE key
- 9_implementation_checklist at top level

So:
- structure = {} (empty dict, since UNIVERSAL_PLANNING_STRUCTURE doesn't exist)
- "9_implementation_checklist" in plan_data = True ✅
- "9_implementation_checklist" in structure = False (structure is empty)
- has_checklist = True ✅

Wait... that should pass! Let me trace deeper into schema_validator.py

ACTUAL BUG (schema_validator.py:367-388):
------------------------------------------
Line 2773 in tool_handlers.py:
    section_9 = get_checklist(plan_data, strict=True)

The get_checklist() function at schema_validator.py:367:
    structure = plan.get("UNIVERSAL_PLANNING_STRUCTURE", {})  # Line 386
    section_9 = structure.get("9_implementation_checklist", {})  # Line 387

This ONLY looks inside UNIVERSAL_PLANNING_STRUCTURE!
It NEVER checks the top-level for "9_implementation_checklist".

So even though the validation at line 2742-2746 passes,
the get_checklist() function returns {} (empty dict),
which fails later validation at line 2775.

MISMATCH:
- Validation logic (line 2742-2746): Checks BOTH top-level AND nested
- Extraction logic (get_checklist): ONLY checks nested structure

This is the bug.
"""

import json
from pathlib import Path
import sys

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent))

from schema_validator import get_checklist

def test_flat_structure_bug():
    """
    Reproduce the bug: plan.json has flat structure but get_checklist expects nested.
    """
    print("=" * 80)
    print("REPRODUCING VALIDATION BUG")
    print("=" * 80)

    # Load the actual plan.json that's failing
    plan_path = Path(r"C:\Users\willh\.mcp-servers\coderef-docs\coderef\workorder\context-docs-integration\plan.json")

    if not plan_path.exists():
        print(f"❌ Plan file not found: {plan_path}")
        return

    with open(plan_path, 'r', encoding='utf-8') as f:
        plan_data = json.load(f)

    print(f"\n📁 Loaded plan.json from: {plan_path}")
    print(f"   File size: {plan_path.stat().st_size} bytes")

    # Analyze structure
    print("\n🔍 STRUCTURE ANALYSIS:")
    print(f"   Top-level keys: {list(plan_data.keys())}")
    print(f"   Has UNIVERSAL_PLANNING_STRUCTURE: {'UNIVERSAL_PLANNING_STRUCTURE' in plan_data}")
    print(f"   Has 9_implementation_checklist at top-level: {'9_implementation_checklist' in plan_data}")

    structure = plan_data.get("UNIVERSAL_PLANNING_STRUCTURE", {})
    print(f"   UNIVERSAL_PLANNING_STRUCTURE keys: {list(structure.keys()) if structure else 'N/A (empty dict)'}")
    print(f"   Has 9_implementation_checklist in UNIVERSAL_PLANNING_STRUCTURE: {'9_implementation_checklist' in structure}")

    # Reproduce the validation logic from tool_handlers.py:2742-2746
    print("\n🧪 SIMULATING VALIDATION (tool_handlers.py:2742-2746):")
    has_checklist = (
        "9_implementation_checklist" in plan_data or
        "9_implementation_checklist" in structure
    )
    print(f"   Check #1: '9_implementation_checklist' in plan_data = {('9_implementation_checklist' in plan_data)}")
    print(f"   Check #2: '9_implementation_checklist' in structure = {('9_implementation_checklist' in structure)}")
    print(f"   has_checklist = {has_checklist}")
    print(f"   Validation result: {'✅ PASS' if has_checklist else '❌ FAIL'}")

    # Now test get_checklist() which is called at line 2773
    print("\n🧪 SIMULATING get_checklist() (schema_validator.py:367):")
    section_9 = get_checklist(plan_data, strict=True)
    print(f"   Returned section_9 type: {type(section_9).__name__}")
    print(f"   Returned section_9 length: {len(section_9)} items")
    print(f"   Returned section_9 keys: {list(section_9.keys()) if isinstance(section_9, dict) else 'N/A'}")
    print(f"   Is empty: {not section_9}")

    # Check what should have been returned
    actual_section_9 = plan_data.get("9_implementation_checklist", {})
    print(f"\n📊 WHAT SHOULD HAVE BEEN RETURNED:")
    print(f"   plan_data['9_implementation_checklist'] type: {type(actual_section_9).__name__}")
    print(f"   plan_data['9_implementation_checklist'] keys: {list(actual_section_9.keys()) if isinstance(actual_section_9, dict) else 'N/A'}")

    # Final verdict
    print("\n" + "=" * 80)
    print("ROOT CAUSE IDENTIFIED:")
    print("=" * 80)
    print("""
The plan.json uses a FLAT structure (sections at top level).
The get_checklist() function ONLY checks inside UNIVERSAL_PLANNING_STRUCTURE.

Validation code (line 2742-2746) checks BOTH:
  ✅ Top-level: "9_implementation_checklist" in plan_data
  ✅ Nested: "9_implementation_checklist" in structure
  Result: PASSES (because found at top-level)

But get_checklist() (line 2773 → schema_validator.py:367) checks ONLY:
  ❌ Nested: structure.get("9_implementation_checklist", {})
  Result: RETURNS EMPTY DICT (because not in UNIVERSAL_PLANNING_STRUCTURE)

SOLUTION:
---------
Fix get_checklist() to check BOTH top-level AND nested structure:

def get_checklist(plan: dict, strict: bool = None) -> dict:
    structure = plan.get("UNIVERSAL_PLANNING_STRUCTURE", {})

    # Check nested structure first (preferred schema format)
    section_9 = structure.get("9_implementation_checklist")

    # Fallback to top-level (legacy/flat format)
    if section_9 is None:
        section_9 = plan.get("9_implementation_checklist", {})

    # ... rest of normalization logic
""")

    print(f"\n{'✅ BUG REPRODUCED' if not section_9 else '❌ BUG NOT REPRODUCED'}")
    print("=" * 80)

if __name__ == "__main__":
    test_flat_structure_bug()
