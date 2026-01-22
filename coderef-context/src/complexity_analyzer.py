"""Complexity analyzer for populating .coderef/reports/complexity.json

Analyzes:
- Cyclomatic complexity per function
- Per-file complexity metrics
- High-complexity hotspots
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any

from .schema_utils import normalize_index_data

logger = logging.getLogger(__name__)


def estimate_cyclomatic_complexity(elem: Dict[str, Any]) -> int:
    """Estimate cyclomatic complexity from element metadata

    Args:
        elem: Element from index.json

    Returns:
        Estimated complexity score (1-50)
    """
    # Base complexity is 1
    complexity = 1

    # Add complexity for parameters (each parameter adds decision points)
    params = elem.get("parameters", [])
    complexity += len(params)

    # Estimate from function size (rough heuristic)
    start_line = elem.get("line", 0)
    end_line = elem.get("end_line", start_line)
    loc = end_line - start_line

    # More lines often means more branching
    if loc > 100:
        complexity += 10
    elif loc > 50:
        complexity += 5
    elif loc > 20:
        complexity += 2

    # Check for complexity indicators in name
    name = elem.get("name", "").lower()
    if any(keyword in name for keyword in ["process", "handle", "parse", "validate", "transform"]):
        complexity += 3

    # Cap at reasonable max
    return min(complexity, 50)


def analyze_complexity(coderef_dir: Path) -> Dict[str, Any]:
    """Analyze code complexity from index.json

    Args:
        coderef_dir: Path to .coderef/ directory

    Returns:
        Dictionary with complexity metrics
    """
    index_path = coderef_dir / "index.json"

    if not index_path.exists():
        raise FileNotFoundError(f"Index not found: {index_path}")

    with open(index_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Normalize data to v1.0.0 format (flat array)
    elements = normalize_index_data(data)
    logger.info(f"Loaded {len(elements)} elements for complexity analysis")

    # Analyze functions and methods
    function_metrics = []
    file_metrics = {}

    for elem in elements:
        elem_type = elem.get("type", "unknown")

        if elem_type in ["function", "method"]:
            elem_name = elem.get("name", "")
            elem_file = elem.get("file", "")
            elem_line = elem.get("line", 0)
            start_line = elem.get("line", 0)
            end_line = elem.get("end_line", start_line + 10)  # Default estimate
            params = elem.get("parameters", [])

            # Estimate complexity
            complexity = estimate_cyclomatic_complexity(elem)

            # Classify complexity level
            if complexity >= 20:
                level = "very_high"
            elif complexity >= 15:
                level = "high"
            elif complexity >= 10:
                level = "medium"
            elif complexity >= 5:
                level = "low"
            else:
                level = "trivial"

            # Record function metric
            function_metrics.append({
                "name": elem_name,
                "file": elem_file,
                "line": elem_line,
                "complexity": level,
                "parameters": len(params),
                "lines_of_code": end_line - start_line,
                "cyclomatic_complexity": complexity
            })

            # Aggregate by file
            if elem_file not in file_metrics:
                file_metrics[elem_file] = {
                    "file": elem_file,
                    "function_count": 0,
                    "total_complexity": 0,
                    "max_complexity": 0,
                    "average_complexity": 0
                }

            file_metrics[elem_file]["function_count"] += 1
            file_metrics[elem_file]["total_complexity"] += complexity
            file_metrics[elem_file]["max_complexity"] = max(
                file_metrics[elem_file]["max_complexity"],
                complexity
            )

    # Calculate averages
    for file_data in file_metrics.values():
        if file_data["function_count"] > 0:
            file_data["average_complexity"] = round(
                file_data["total_complexity"] / file_data["function_count"],
                2
            )

    # Find high complexity functions
    high_complexity = [
        f for f in function_metrics
        if f["cyclomatic_complexity"] >= 15
    ]
    high_complexity.sort(key=lambda x: x["cyclomatic_complexity"], reverse=True)

    # Build complexity report
    complexity_report = {
        "functions": function_metrics,
        "files": list(file_metrics.values()),
        "high_complexity": high_complexity,
        "summary": {
            "total_functions": len(function_metrics),
            "total_files": len(file_metrics),
            "high_complexity_count": len(high_complexity),
            "average_file_complexity": round(
                sum(f["average_complexity"] for f in file_metrics.values()) / len(file_metrics),
                2
            ) if file_metrics else 0
        }
    }

    return complexity_report


def populate_complexity_report(coderef_dir: Path) -> None:
    """Generate and save complexity.json report

    Args:
        coderef_dir: Path to .coderef/ directory
    """
    complexity = analyze_complexity(coderef_dir)

    reports_dir = coderef_dir / "reports"
    reports_dir.mkdir(exist_ok=True)

    complexity_path = reports_dir / "complexity.json"
    with open(complexity_path, 'w', encoding='utf-8') as f:
        json.dump(complexity, f, indent=2)

    print(f"complexity.json created: {complexity['summary']['total_functions']} functions, "
          f"{complexity['summary']['high_complexity_count']} high complexity")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        coderef_path = Path(sys.argv[1])
        populate_complexity_report(coderef_path)
    else:
        print("Usage: python complexity_analyzer.py <coderef_dir>")
