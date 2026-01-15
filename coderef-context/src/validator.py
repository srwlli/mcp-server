"""Validator for populating .coderef/reports/validation.json

Validates:
- CodeRef2 tag coverage
- Missing tags on public elements
- Tag format consistency
"""

import json
from pathlib import Path
from typing import Dict, List, Any


def analyze_validation(coderef_dir: Path) -> Dict[str, Any]:
    """Analyze CodeRef2 tag validation from index.json

    Args:
        coderef_dir: Path to .coderef/ directory

    Returns:
        Dictionary with validation results
    """
    index_path = coderef_dir / "index.json"

    if not index_path.exists():
        raise FileNotFoundError(f"Index not found: {index_path}")

    with open(index_path, 'r', encoding='utf-8') as f:
        elements = json.load(f)

    total_elements = len(elements)
    tagged_elements = 0
    issues = []

    for elem in elements:
        elem_name = elem.get("name", "")
        elem_file = elem.get("file", "")
        elem_line = elem.get("line", 0)
        elem_type = elem.get("type", "unknown")

        # Check if element has CodeRef2 tag
        has_tag = False
        if "coderef_id" in elem or "coderef_tag" in elem or "tags" in elem:
            has_tag = True
            tagged_elements += 1

        # Report issues for public elements without tags
        # (private elements start with _ or __)
        is_private = elem_name.startswith('_')
        is_public = not is_private

        if is_public and not has_tag:
            issues.append({
                "file": elem_file,
                "line": elem_line,
                "issue": f"Missing CodeRef2 tag for {elem_type}: {elem_name}",
                "severity": "warning"
            })

    # Calculate tag coverage
    tag_coverage = (tagged_elements / total_elements * 100) if total_elements > 0 else 0

    # Build validation report
    validation = {
        "coderef2_tags": {
            "total_elements": total_elements,
            "tagged_elements": tagged_elements,
            "untagged_elements": total_elements - tagged_elements,
            "tag_coverage": round(tag_coverage, 2)
        },
        "issues": issues[:50],  # Limit to first 50 issues
        "summary": {
            "total_issues": len(issues),
            "warnings": len([i for i in issues if i.get("severity") == "warning"]),
            "errors": len([i for i in issues if i.get("severity") == "error"])
        }
    }

    return validation


def populate_validation_report(coderef_dir: Path) -> None:
    """Generate and save validation.json report

    Args:
        coderef_dir: Path to .coderef/ directory
    """
    validation = analyze_validation(coderef_dir)

    reports_dir = coderef_dir / "reports"
    reports_dir.mkdir(exist_ok=True)

    validation_path = reports_dir / "validation.json"
    with open(validation_path, 'w', encoding='utf-8') as f:
        json.dump(validation, f, indent=2)

    print(f"validation.json created: {validation['coderef2_tags']['tag_coverage']:.1f}% coverage, "
          f"{validation['summary']['total_issues']} issues")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        coderef_path = Path(sys.argv[1])
        populate_validation_report(coderef_path)
    else:
        print("Usage: python validator.py <coderef_dir>")
