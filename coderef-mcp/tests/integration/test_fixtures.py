"""Test fixtures - 281 baseline elements for comprehensive testing."""

from typing import List, Dict, Any


def create_baseline_elements() -> List[Dict[str, Any]]:
    """Create 281 baseline CodeRef2 elements for testing.

    Returns:
        list: 281 test fixture elements
    """
    elements = []

    # Category 1: Function elements (70 elements)
    for i in range(70):
        elements.append({
            "reference": f"@Fn/src/handlers#func_{i:03d}:{100+i}",
            "type": "Fn",
            "path": f"src/handlers",
            "element": f"func_{i:03d}",
            "line": 100 + i,
            "complexity": "low" if i % 3 == 0 else ("medium" if i % 3 == 1 else "high"),
            "coverage": 95 - (i % 20),
            "tested": i % 2 == 0,
        })

    # Category 2: Class elements (60 elements)
    for i in range(60):
        elements.append({
            "reference": f"@C/src/models#Model_{i:03d}:{200+i}",
            "type": "C",
            "path": f"src/models",
            "element": f"Model_{i:03d}",
            "line": 200 + i,
            "complexity": "low" if i % 3 == 0 else ("medium" if i % 3 == 1 else "high"),
            "coverage": 85 - (i % 20),
            "tested": i % 2 == 0,
        })

    # Category 3: Method elements (60 elements)
    for i in range(60):
        elements.append({
            "reference": f"@M/src/service#method_{i:03d}:{300+i}",
            "type": "M",
            "path": f"src/service",
            "element": f"method_{i:03d}",
            "line": 300 + i,
            "complexity": "medium" if i % 2 == 0 else "high",
            "coverage": 75 - (i % 20),
            "tested": i % 3 == 0,
        })

    # Category 4: Module/File elements (50 elements)
    for i in range(50):
        elements.append({
            "reference": f"@F/src/module_{i:03d}.py:{i*10}",
            "type": "F",
            "path": f"src/module_{i:03d}.py",
            "element": None,
            "line": None,
            "complexity": "low",
            "coverage": 80 - (i % 20),
            "tested": True,
        })

    # Category 5: Variable/Constant elements (41 elements)
    for i in range(41):
        elements.append({
            "reference": f"@V/src/constants#CONST_{i:03d}:{400+i}",
            "type": "V",
            "path": f"src/constants",
            "element": f"CONST_{i:03d}",
            "line": 400 + i,
            "complexity": "low",
            "coverage": 100 if i % 5 == 0 else 90,
            "tested": True,
        })

    # Ensure we have exactly 281
    assert len(elements) == 281, f"Expected 281 elements, got {len(elements)}"
    return elements


def get_baseline_elements_by_type(elements: List[Dict[str, Any]], type_code: str) -> List[Dict[str, Any]]:
    """Get baseline elements of a specific type.

    Args:
        elements: All baseline elements
        type_code: Type code (e.g., "Fn", "C", "M")

    Returns:
        list: Elements of specified type
    """
    return [e for e in elements if e["type"] == type_code]


def get_baseline_elements_by_complexity(
    elements: List[Dict[str, Any]],
    complexity: str
) -> List[Dict[str, Any]]:
    """Get baseline elements of a specific complexity.

    Args:
        elements: All baseline elements
        complexity: Complexity level ("low", "medium", "high")

    Returns:
        list: Elements of specified complexity
    """
    return [e for e in elements if e.get("complexity") == complexity]


def get_baseline_elements_untested(elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Get baseline elements without tests.

    Args:
        elements: All baseline elements

    Returns:
        list: Untested elements
    """
    return [e for e in elements if not e.get("tested", False)]


def create_reference_pairs() -> List[tuple]:
    """Create element reference pairs for relationship testing.

    Returns:
        list: Tuples of (source_ref, target_ref, relationship_type)
    """
    pairs = []

    # Create some dependency relationships
    for i in range(0, 70, 10):
        for j in range(i + 1, min(i + 5, 70)):
            pairs.append((
                f"@Fn/src/handlers#func_{i:03d}:100",
                f"@Fn/src/handlers#func_{j:03d}:100",
                "calls"
            ))

    # Create some inheritance relationships
    for i in range(0, 60, 20):
        for j in range(i + 1, min(i + 5, 60)):
            pairs.append((
                f"@C/src/models#Model_{j:03d}:200",
                f"@C/src/models#Model_{i:03d}:200",
                "extends"
            ))

    # Create some import relationships
    for i in range(0, 50, 10):
        for j in range(i + 1, min(i + 3, 50)):
            pairs.append((
                f"@F/src/module_{i:03d}.py:0",
                f"@F/src/module_{j:03d}.py:0",
                "imports"
            ))

    return pairs


def create_high_risk_elements() -> List[Dict[str, Any]]:
    """Create high-risk elements (complex, low coverage).

    Returns:
        list: High-risk elements
    """
    elements = []
    for i in range(10):
        elements.append({
            "reference": f"@Fn/src/critical#risky_{i:03d}:{500+i}",
            "type": "Fn",
            "path": f"src/critical",
            "element": f"risky_{i:03d}",
            "line": 500 + i,
            "complexity": "high",
            "coverage": 20 + (i * 5),  # 20-65% coverage
            "tested": False,
        })
    return elements


class BaselineElementDataset:
    """Helper class for working with baseline element dataset."""

    def __init__(self):
        """Initialize dataset."""
        self.elements = create_baseline_elements()
        self.pairs = create_reference_pairs()
        self.high_risk = create_high_risk_elements()

    def get_all(self) -> List[Dict[str, Any]]:
        """Get all baseline elements."""
        return self.elements

    def get_by_type(self, type_code: str) -> List[Dict[str, Any]]:
        """Get elements by type."""
        return get_baseline_elements_by_type(self.elements, type_code)

    def get_by_complexity(self, complexity: str) -> List[Dict[str, Any]]:
        """Get elements by complexity."""
        return get_baseline_elements_by_complexity(self.elements, complexity)

    def get_untested(self) -> List[Dict[str, Any]]:
        """Get untested elements."""
        return get_baseline_elements_untested(self.elements)

    def get_high_risk(self) -> List[Dict[str, Any]]:
        """Get high-risk elements."""
        return self.high_risk

    def get_references_only(self) -> List[str]:
        """Get just the references."""
        return [e["reference"] for e in self.elements]

    def get_stats(self) -> Dict[str, Any]:
        """Get dataset statistics."""
        low_complexity = len(self.get_by_complexity("low"))
        medium_complexity = len(self.get_by_complexity("medium"))
        high_complexity = len(self.get_by_complexity("high"))
        tested = len([e for e in self.elements if e.get("tested", False)])
        untested = len(self.get_untested())

        avg_coverage = sum(e.get("coverage", 0) for e in self.elements) / len(self.elements) if self.elements else 0

        return {
            "total_elements": len(self.elements),
            "by_type": {
                "functions": len(self.get_by_type("Fn")),
                "classes": len(self.get_by_type("C")),
                "methods": len(self.get_by_type("M")),
                "files": len(self.get_by_type("F")),
                "variables": len(self.get_by_type("V")),
            },
            "by_complexity": {
                "low": low_complexity,
                "medium": medium_complexity,
                "high": high_complexity,
            },
            "by_test_status": {
                "tested": tested,
                "untested": untested,
            },
            "coverage": {
                "average": round(avg_coverage, 2),
                "high_risk_count": len(self.get_high_risk()),
            }
        }
