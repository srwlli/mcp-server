"""
Tests for dynamic import warnings (WO-DOCS-SCANNER-INTEGRATION-001, Task 4).

Verifies that dynamic import detection correctly processes ElementData.dynamicImports
field from Phase 1 scanner task_6 and formats warnings for documentation.
"""

import pytest
from tool_handlers import detect_dynamic_imports


# Mock ElementData with dynamicImports
ELEMENTS_WITH_DYNAMIC_IMPORTS = [
    {
        "name": "RouteLoader",
        "file": "router.ts",
        "line": 50,
        "dynamicImports": [
            {
                "pattern": "import('./routes/' + routeName)",
                "location": "conditional expression",
                "line": 55
            },
            {
                "pattern": "import(`./plugins/${name}.js`)",
                "location": "template literal",
                "line": 62
            }
        ]
    },
    {
        "name": "PluginManager",
        "file": "plugins.ts",
        "line": 10,
        "dynamicImports": [
            {
                "pattern": "require.resolve(moduleName)",
                "location": "function call",
                "line": 20
            }
        ]
    }
]

ELEMENTS_WITHOUT_DYNAMIC_IMPORTS = [
    {"name": "StaticComponent", "file": "static.ts", "line": 1},
    {"name": "NormalFunction", "file": "utils.ts", "line": 50},
]

ELEMENTS_MIXED = [
    {"name": "WithDynamic", "file": "a.ts", "dynamicImports": [{"pattern": "import(x)", "location": "call", "line": 10}]},
    {"name": "WithoutDynamic", "file": "b.ts"},
]


def test_basic_detection():
    """Verify dynamic imports are detected correctly."""
    result = detect_dynamic_imports(ELEMENTS_WITH_DYNAMIC_IMPORTS)

    assert result['has_dynamic_imports'] is True
    assert result['total_dynamic_imports'] == 3  # 2 from RouteLoader + 1 from PluginManager
    assert len(result['warnings']) == 3
    assert len(result['affected_files']) == 2  # router.ts, plugins.ts


def test_warning_structure():
    """Verify warning dicts have correct structure."""
    result = detect_dynamic_imports(ELEMENTS_WITH_DYNAMIC_IMPORTS)

    warning = result['warnings'][0]

    # Check required fields
    assert 'file' in warning
    assert 'element' in warning
    assert 'line' in warning
    assert 'pattern' in warning
    assert 'location' in warning
    assert 'severity' in warning
    assert 'message' in warning
    assert 'recommendation' in warning

    # Check values
    assert warning['file'] == 'router.ts'
    assert warning['element'] == 'RouteLoader'
    assert warning['pattern'] == "import('./routes/' + routeName)"
    assert warning['severity'] == 'medium'
    assert 'tree-shaking' in warning['recommendation']


def test_graceful_degradation_no_dynamic_imports():
    """Verify handling of elements without dynamicImports field."""
    result = detect_dynamic_imports(ELEMENTS_WITHOUT_DYNAMIC_IMPORTS)

    assert result['has_dynamic_imports'] is False
    assert result['total_dynamic_imports'] == 0
    assert result['warnings'] == []
    assert result['affected_files'] == []
    assert result['summary'] == "No dynamic imports detected"


def test_mixed_elements():
    """Verify handling of mixed elements (some with/without dynamicImports)."""
    result = detect_dynamic_imports(ELEMENTS_MIXED)

    assert result['has_dynamic_imports'] is True
    assert result['total_dynamic_imports'] == 1
    assert len(result['warnings']) == 1
    assert len(result['affected_files']) == 1
    assert result['affected_files'][0] == 'a.ts'


def test_empty_elements_list():
    """Verify handling of empty elements list."""
    result = detect_dynamic_imports([])

    assert result['has_dynamic_imports'] is False
    assert result['total_dynamic_imports'] == 0
    assert result['warnings'] == []
    assert result['affected_files'] == []


def test_affected_files_unique():
    """Verify affected_files list contains unique paths only."""
    elements = [
        {"name": "Func1", "file": "a.ts", "dynamicImports": [{"pattern": "x", "location": "y", "line": 1}]},
        {"name": "Func2", "file": "a.ts", "dynamicImports": [{"pattern": "z", "location": "y", "line": 2}]},
        {"name": "Func3", "file": "b.ts", "dynamicImports": [{"pattern": "w", "location": "y", "line": 3}]},
    ]

    result = detect_dynamic_imports(elements)

    # Should have 3 warnings but only 2 unique files
    assert result['total_dynamic_imports'] == 3
    assert len(result['affected_files']) == 2
    assert set(result['affected_files']) == {'a.ts', 'b.ts'}


def test_summary_formatting():
    """Verify summary message formatting."""
    result_with_imports = detect_dynamic_imports(ELEMENTS_WITH_DYNAMIC_IMPORTS)
    result_without_imports = detect_dynamic_imports(ELEMENTS_WITHOUT_DYNAMIC_IMPORTS)

    assert "3 dynamic import(s) across 2 file(s)" in result_with_imports['summary']
    assert "No dynamic imports detected" in result_without_imports['summary']


def test_multiple_dynamic_imports_per_element():
    """Verify multiple dynamic imports in single element are handled."""
    result = detect_dynamic_imports(ELEMENTS_WITH_DYNAMIC_IMPORTS)

    # RouteLoader has 2 dynamic imports
    route_loader_warnings = [w for w in result['warnings'] if w['element'] == 'RouteLoader']
    assert len(route_loader_warnings) == 2

    # Check both patterns are captured
    patterns = [w['pattern'] for w in route_loader_warnings]
    assert "import('./routes/' + routeName)" in patterns
    assert "import(`./plugins/${name}.js`)" in patterns


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
