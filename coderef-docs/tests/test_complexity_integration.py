"""
Tests for complexity integration (WO-DOCS-SCANNER-INTEGRATION-001, Task 2).

Verifies that resource sheet generation correctly reads and processes
ElementData.complexity field from Phase 1 scanner task_5.
"""

import pytest
from generators.resource_sheet_generator import ResourceSheetGenerator


# Mock ElementData samples with complexity
ELEMENTS_WITH_COMPLEXITY = [
    {"name": "simpleFunc", "complexity": 3, "file": "a.ts", "line": 1},
    {"name": "mediumFunc", "complexity": 12, "file": "b.ts", "line": 50},
    {"name": "complexFunc", "complexity": 18, "file": "c.ts", "line": 100},
    {"name": "veryComplexFunc", "complexity": 25, "file": "d.ts", "line": 200},
    {"name": "anotherSimple", "complexity": 5, "file": "e.ts", "line": 10},
]

ELEMENTS_WITHOUT_COMPLEXITY = [
    {"name": "func1", "file": "a.ts", "line": 1},
    {"name": "func2", "file": "b.ts", "line": 50},
]

ELEMENTS_MIXED_COMPLEXITY = [
    {"name": "withComplexity", "complexity": 15, "file": "a.ts", "line": 1},
    {"name": "withoutComplexity", "file": "b.ts", "line": 50},  # Missing field
    {"name": "zeroComplexity", "complexity": 0, "file": "c.ts", "line": 100},  # Zero (filtered out)
]


@pytest.fixture
def generator():
    """Create ResourceSheetGenerator instance for testing."""
    return ResourceSheetGenerator()


def test_complexity_stats_calculation(generator):
    """Verify complexity statistics calculated correctly."""
    stats = generator.calculate_complexity_stats(ELEMENTS_WITH_COMPLEXITY)

    # Check averages
    expected_avg = (3 + 12 + 18 + 25 + 5) / 5
    assert stats['avg'] == pytest.approx(expected_avg, rel=0.01)

    # Check max
    assert stats['max'] == 25

    # Check hotspots (complexity > 10)
    assert len(stats['hotspots']) == 3  # mediumFunc, complexFunc, veryComplexFunc
    assert stats['hotspots'][0]['name'] == 'veryComplexFunc'  # Sorted by complexity
    assert stats['hotspots'][0]['complexity'] == 25

    # Check metadata
    assert stats['total_elements'] == 5
    assert stats['elements_with_complexity'] == 5
    assert stats['has_complexity_data'] is True


def test_graceful_degradation_no_complexity(generator):
    """Verify graceful degradation when complexity field missing."""
    stats = generator.calculate_complexity_stats(ELEMENTS_WITHOUT_COMPLEXITY)

    assert stats['avg'] == 0
    assert stats['max'] == 0
    assert stats['hotspots'] == []
    assert stats['total_elements'] == 2
    assert stats['elements_with_complexity'] == 0
    assert stats['has_complexity_data'] is False


def test_mixed_complexity_data(generator):
    """Verify handling of mixed elements (some with/without complexity)."""
    stats = generator.calculate_complexity_stats(ELEMENTS_MIXED_COMPLEXITY)

    # Only element with complexity=15 should be counted
    assert stats['avg'] == 15.0
    assert stats['max'] == 15
    assert len(stats['hotspots']) == 1  # Only withComplexity (15 > 10)
    assert stats['hotspots'][0]['name'] == 'withComplexity'
    assert stats['total_elements'] == 3
    assert stats['elements_with_complexity'] == 1  # Only 1 non-zero complexity
    assert stats['has_complexity_data'] is True


def test_refactoring_recommendations(generator):
    """Verify refactoring recommendations based on thresholds."""
    stats = generator.calculate_complexity_stats(ELEMENTS_WITH_COMPLEXITY)

    hotspots = {h['name']: h for h in stats['hotspots']}

    # veryComplexFunc (25) -> HIGH priority
    assert "HIGH" in hotspots['veryComplexFunc']['recommendation']

    # complexFunc (18) -> HIGH priority (> 15)
    assert "HIGH" in hotspots['complexFunc']['recommendation']

    # mediumFunc (12) -> MEDIUM priority (11-15)
    assert "MEDIUM" in hotspots['mediumFunc']['recommendation']


def test_hotspot_sorting(generator):
    """Verify hotspots sorted by complexity (highest first)."""
    stats = generator.calculate_complexity_stats(ELEMENTS_WITH_COMPLEXITY)

    complexities = [h['complexity'] for h in stats['hotspots']]

    # Should be sorted descending
    assert complexities == sorted(complexities, reverse=True)
    assert complexities[0] == 25  # veryComplexFunc
    assert complexities[-1] == 12  # mediumFunc


def test_empty_elements_list(generator):
    """Verify handling of empty elements list."""
    stats = generator.calculate_complexity_stats([])

    assert stats['avg'] == 0
    assert stats['max'] == 0
    assert stats['hotspots'] == []
    assert stats['total_elements'] == 0
    assert stats['elements_with_complexity'] == 0
    assert stats['has_complexity_data'] is False


def test_all_low_complexity(generator):
    """Verify handling when all elements below hotspot threshold."""
    low_complexity = [
        {"name": "func1", "complexity": 5, "file": "a.ts", "line": 1},
        {"name": "func2", "complexity": 8, "file": "b.ts", "line": 50},
        {"name": "func3", "complexity": 10, "file": "c.ts", "line": 100},
    ]

    stats = generator.calculate_complexity_stats(low_complexity)

    assert stats['avg'] == pytest.approx(7.67, rel=0.01)
    assert stats['max'] == 10
    assert stats['hotspots'] == []  # None > 10
    assert stats['has_complexity_data'] is True


def test_recommendation_thresholds(generator):
    """Verify recommendation thresholds are correct."""
    # Acceptable (1-10)
    assert "Acceptable" in generator._get_complexity_recommendation(5)
    assert "Acceptable" in generator._get_complexity_recommendation(10)

    # Medium (11-15)
    assert "MEDIUM" in generator._get_complexity_recommendation(11)
    assert "MEDIUM" in generator._get_complexity_recommendation(15)

    # High (16+)
    assert "HIGH" in generator._get_complexity_recommendation(16)
    assert "HIGH" in generator._get_complexity_recommendation(100)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
