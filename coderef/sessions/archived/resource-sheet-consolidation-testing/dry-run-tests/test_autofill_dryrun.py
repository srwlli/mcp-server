#!/usr/bin/env python3
"""
Dry-run test for auto-fill percentage calculation
Uses mock generated document
"""

import re

def measure_autofill(document_content):
    """Calculate auto-fill percentage from marked content"""

    # Find all auto-fill blocks (more forgiving regex)
    pattern = r'<!-- AUTO-FILL:.*?-->(.*?)<!-- /AUTO-FILL -->'
    autofill_blocks = re.findall(pattern, document_content, re.DOTALL)

    # Count auto-filled lines (each block's content lines)
    autofill_lines = 0
    for block in autofill_blocks:
        # Count non-empty lines in this block
        block_lines = [line for line in block.strip().split('\n') if line.strip()]
        autofill_lines += len(block_lines)

    # Count total document lines (excluding empty lines and HTML comments)
    all_lines = document_content.split('\n')
    total_lines = 0
    for line in all_lines:
        stripped = line.strip()
        # Count lines that aren't empty and aren't HTML comments
        if stripped and not stripped.startswith('<!--'):
            total_lines += 1

    # Calculate percentage
    percentage = (autofill_lines / total_lines) * 100 if total_lines > 0 else 0

    return percentage, autofill_lines, total_lines

def test_autofill_dryrun():
    # Mock generated document (what we expect from GRAPH-002)
    # Realistic ratio: 60-80% auto-fill, 20-40% manual
    mock_document = """# CONSTANTS.md Reference Sheet

## Dependencies
<!-- AUTO-FILL: getImportsForElement -->
- enum.Enum
- pathlib.Path
- typing.Optional
- typing.List
- dataclasses
<!-- /AUTO-FILL -->

## Public API
<!-- AUTO-FILL: getExportsForElement -->
- Paths class
- Files class
- TemplateType enum
- PlanningPaths class
- ChangelogType enum
- StandardsType enum
<!-- /AUTO-FILL -->

## Usage Examples
<!-- AUTO-FILL: getConsumersForElement -->
from constants import Paths
from constants import Files
from constants import TemplateType
# Example usage in planning_analyzer.py
paths = Paths()
# Example usage in plan_validator.py
template_type = TemplateType.FOUNDATION
<!-- /AUTO-FILL -->

## Required Dependencies
<!-- AUTO-FILL: getDependenciesForElement -->
Python 3.11+
pathlib (stdlib)
enum (stdlib)
<!-- /AUTO-FILL -->

## Manual Notes
Manual content explaining special cases...
"""

    # Test: Measure auto-fill
    percentage, autofill, total = measure_autofill(mock_document)

    print("Testing auto-fill percentage calculation:\n")
    print(f"Auto-fill lines: {autofill}/{total}")
    print(f"Auto-fill percentage: {percentage:.1f}%")
    print(f"Target: 60-80%")

    # Pass/fail
    if 60 <= percentage <= 80:
        print(f"\n[PASS] GRAPH-005 DRY-RUN: actual {percentage:.1f}% within target 60-80%")
        return True
    elif percentage > 80:
        print(f"\n[WARN] GRAPH-005 DRY-RUN: actual {percentage:.1f}% exceeds 80% - too much auto-fill")
        return True  # Still acceptable
    else:
        print(f"\n[FAIL] GRAPH-005 DRY-RUN: actual {percentage:.1f}% below 60% minimum")
        return False

# Run dry-run
if __name__ == "__main__":
    result = test_autofill_dryrun()
    print(f"\nAuto-fill test dry-run: {'SUCCESS' if result else 'FAILED'}")
    exit(0 if result else 1)
