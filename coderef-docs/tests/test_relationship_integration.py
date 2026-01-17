"""
Tests for relationship integration (WO-DOCS-SCANNER-INTEGRATION-001, Task 3).

Verifies that relationship data (imports, exports, dependencies) is correctly
aggregated and visualized for architecture documentation.
"""

import pytest
from tool_handlers import (
    aggregate_imports,
    aggregate_exports,
    identify_high_coupling,
    generate_dependency_mermaid
)


# Mock ElementData with imports/exports
ELEMENTS_WITH_RELATIONSHIPS = [
    {
        "name": "Scanner",
        "file": "scanner.ts",
        "line": 10,
        "imports": [
            {"source": "acorn", "specifiers": ["parse"], "line": 1},
            {"source": "typescript", "specifiers": ["createSourceFile"], "line": 2},
        ],
        "exports": [
            {"name": "Scanner", "type": "class"},
            {"name": "scanElements", "type": "function"},
        ]
    },
    {
        "name": "Analyzer",
        "file": "analyzer.ts",
        "line": 20,
        "imports": [
            {"source": "acorn", "specifiers": ["parse"], "line": 1},
            {"source": "fs/promises", "specifiers": ["readFile"], "line": 2},
        ],
        "exports": [
            {"name": "Analyzer", "type": "class"},
        ]
    },
    {
        "name": "Helpers",
        "file": "utils.ts",
        "line": 5,
        "imports": [
            {"source": "fs/promises", "specifiers": ["readFile", "writeFile"], "line": 1},
        ],
        "exports": [
            {"name": "sanitize", "type": "function"},
            {"name": "validate", "type": "function"},
        ]
    },
]


def test_import_aggregation():
    """Verify import counts aggregated correctly."""
    import_counts = aggregate_imports(ELEMENTS_WITH_RELATIONSHIPS)

    # acorn imported 2 times (Scanner + Analyzer)
    assert import_counts['acorn'] == 2

    # typescript imported 1 time (Scanner)
    assert import_counts['typescript'] == 1

    # fs/promises imported 2 times (Analyzer + Helpers)
    assert import_counts['fs/promises'] == 2

    # Total unique modules
    assert len(import_counts) == 3


def test_export_aggregation():
    """Verify exports grouped by file correctly."""
    exports_by_file = aggregate_exports(ELEMENTS_WITH_RELATIONSHIPS)

    # scanner.ts has 2 exports
    assert len(exports_by_file['scanner.ts']) == 2
    assert any(e['name'] == 'Scanner' for e in exports_by_file['scanner.ts'])
    assert any(e['name'] == 'scanElements' for e in exports_by_file['scanner.ts'])

    # analyzer.ts has 1 export
    assert len(exports_by_file['analyzer.ts']) == 1
    assert exports_by_file['analyzer.ts'][0]['name'] == 'Analyzer'

    # utils.ts has 2 exports
    assert len(exports_by_file['utils.ts']) == 2


def test_high_coupling_identification():
    """Verify high-dependency modules identified correctly."""
    import_counts = {
        'acorn': 12,
        'typescript': 8,
        'fs/promises': 15,
        'path': 23,
        'lodash': 3,  # Below threshold
    }

    high_deps = identify_high_coupling(import_counts, threshold=5)

    # Should include only modules with >= 5 usages
    assert len(high_deps) == 4
    assert 'lodash' not in high_deps

    # Should be sorted descending by count
    modules = list(high_deps.keys())
    assert modules[0] == 'path'  # 23
    assert modules[1] == 'fs/promises'  # 15
    assert modules[2] == 'acorn'  # 12
    assert modules[3] == 'typescript'  # 8


def test_mermaid_diagram_generation():
    """Verify Mermaid diagram syntax is valid."""
    import_counts = {
        'acorn': 12,
        'typescript': 8,
        'fs/promises': 15,
    }

    diagram = generate_dependency_mermaid(import_counts, limit=10)

    # Check basic structure
    assert diagram.startswith("```mermaid")
    assert diagram.endswith("```")
    assert "graph TD" in diagram
    assert "Project" in diagram

    # Check dependencies included
    assert "acorn" in diagram
    assert "typescript" in diagram
    assert "fs/promises" in diagram

    # Check usage counts shown
    assert "(12 usages)" in diagram
    assert "(8 usages)" in diagram
    assert "(15 usages)" in diagram


def test_graceful_degradation_missing_imports():
    """Verify handling of elements without imports field."""
    elements = [
        {"name": "func1", "file": "a.ts", "line": 1},  # No imports
        {"name": "func2", "file": "b.ts", "line": 2},
    ]

    import_counts = aggregate_imports(elements)
    assert import_counts == {}  # Empty dict, not error


def test_graceful_degradation_missing_exports():
    """Verify handling of elements without exports field."""
    elements = [
        {"name": "func1", "file": "a.ts", "line": 1},  # No exports
        {"name": "func2", "file": "b.ts", "line": 2},
    ]

    exports_by_file = aggregate_exports(elements)
    assert exports_by_file == {}  # Empty dict, not error


def test_mermaid_diagram_with_special_chars():
    """Verify Mermaid sanitizes module names with special characters."""
    import_counts = {
        '@babel/core': 5,
        'lodash/fp': 3,
        'react.component': 2,
    }

    diagram = generate_dependency_mermaid(import_counts)

    # Check sanitized names (/ @ . replaced with _)
    assert "_babel_core" in diagram
    assert "lodash_fp" in diagram
    assert "react_component" in diagram


def test_mermaid_diagram_limit():
    """Verify Mermaid diagram respects limit parameter."""
    import_counts = {
        f'module{i}': i for i in range(1, 21)  # 20 modules
    }

    diagram = generate_dependency_mermaid(import_counts, limit=5)

    # Should only include top 5 modules by count
    lines = diagram.split('\n')
    dependency_lines = [l for l in lines if '-->' in l]

    assert len(dependency_lines) == 5  # Only 5 dependencies


def test_empty_import_counts():
    """Verify handling of empty import data."""
    diagram = generate_dependency_mermaid({})

    assert "```mermaid" in diagram
    assert "No dependencies detected" in diagram


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
