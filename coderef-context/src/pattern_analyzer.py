"""Pattern analyzer for populating .coderef/reports/patterns.json

Analyzes index.json to extract:
- Handlers (functions starting with 'handle_')
- Decorators (@ usage patterns)
- Common imports
- Naming conventions
"""

import json
import logging
from pathlib import Path
from collections import Counter
from typing import Dict, List, Any

from .schema_utils import normalize_index_data

logger = logging.getLogger(__name__)


def analyze_patterns(coderef_dir: Path) -> Dict[str, Any]:
    """Analyze code patterns from index.json

    Args:
        coderef_dir: Path to .coderef/ directory

    Returns:
        Dictionary with pattern analysis
    """
    index_path = coderef_dir / "index.json"

    if not index_path.exists():
        raise FileNotFoundError(f"Index not found: {index_path}")

    with open(index_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Normalize data to v1.0.0 format (flat array)
    elements = normalize_index_data(data)
    logger.info(f"Loaded {len(elements)} elements for pattern analysis")

    # Initialize pattern containers
    handlers = []
    decorators = Counter()
    imports = Counter()
    naming_by_type = {}

    for elem in elements:
        elem_type = elem.get("type", "unknown")
        elem_name = elem.get("name", "")
        elem_file = elem.get("file", "")
        elem_line = elem.get("line", 0)

        # Detect handlers (handle_* functions)
        if elem_type == "function" and elem_name.startswith("handle_"):
            handlers.append({
                "name": elem_name,
                "file": elem_file,
                "line": elem_line
            })

        # Track naming conventions
        if elem_type not in naming_by_type:
            naming_by_type[elem_type] = []
        naming_by_type[elem_type].append(elem_name)

        # Detect decorators (from metadata if available)
        if "decorators" in elem:
            for decorator in elem.get("decorators", []):
                decorators[decorator] += 1

        # Track imports (from dependencies if available)
        if "imports" in elem:
            for imp in elem.get("imports", []):
                imports[imp] += 1

    # Determine naming conventions
    naming_conventions = {}
    for elem_type, names in naming_by_type.items():
        if names:
            # Simple heuristic: check first name's case pattern
            first_name = names[0]
            if first_name and first_name[0].isupper():
                naming_conventions[elem_type] = "PascalCase"
            elif '_' in first_name:
                naming_conventions[elem_type] = "snake_case"
            elif first_name and first_name[0].islower():
                naming_conventions[elem_type] = "camelCase"
            else:
                naming_conventions[elem_type] = "unknown"

    # Build pattern report
    patterns = {
        "handlers": handlers,
        "decorators": [
            {"name": name, "usage_count": count}
            for name, count in decorators.most_common(10)
        ],
        "common_imports": [
            {"module": module, "usage_count": count}
            for module, count in imports.most_common(10)
        ],
        "naming_conventions": naming_conventions,
        "pattern_summary": {
            "handler_count": len(handlers),
            "unique_decorators": len(decorators),
            "unique_imports": len(imports)
        }
    }

    return patterns


def populate_patterns_report(coderef_dir: Path) -> None:
    """Generate and save patterns.json report

    Args:
        coderef_dir: Path to .coderef/ directory
    """
    patterns = analyze_patterns(coderef_dir)

    reports_dir = coderef_dir / "reports"
    reports_dir.mkdir(exist_ok=True)

    patterns_path = reports_dir / "patterns.json"
    with open(patterns_path, 'w', encoding='utf-8') as f:
        json.dump(patterns, f, indent=2)

    print(f"patterns.json created: {len(patterns['handlers'])} handlers, "
          f"{len(patterns['decorators'])} decorators")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        coderef_path = Path(sys.argv[1])
        populate_patterns_report(coderef_path)
    else:
        print("Usage: python pattern_analyzer.py <coderef_dir>")
