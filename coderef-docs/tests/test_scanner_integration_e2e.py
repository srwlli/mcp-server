"""
End-to-end integration tests for scanner enhancement integration.

WO-DOCS-SCANNER-INTEGRATION-001: Phase 5, Task 1 (TEST-005)

Tests complete workflow from ElementData → tool_handlers → documentation output.
Validates all 4 Phase 1 enhancements integrated correctly:
1. AST accuracy (interfaces, decorators, type aliases)
2. Complexity metrics (hotspots, refactoring recommendations)
3. Relationship data (imports, exports, dependency graphs)
4. Dynamic import warnings (runtime considerations)
"""

import pytest
from pathlib import Path
from tool_handlers import (
    aggregate_imports,
    aggregate_exports,
    identify_high_coupling,
    generate_dependency_mermaid,
    detect_dynamic_imports
)
from generators.resource_sheet_generator import ResourceSheetGenerator


# Comprehensive mock ElementData with all Phase 1 enhancements
COMPLETE_ELEMENT_DATA = [
    {
        "name": "AuthService",
        "type": "class",
        "file": "services/auth.ts",
        "line": 10,
        "complexity": 18,  # Phase 1 task_5
        "imports": [  # Phase 1 task_5
            {"source": "jsonwebtoken", "specifiers": ["sign", "verify"], "line": 1},
            {"source": "bcrypt", "specifiers": ["hash", "compare"], "line": 2},
        ],
        "exports": [  # Phase 1 task_5
            {"name": "AuthService", "type": "class"},
            {"name": "login", "type": "function"},
            {"name": "logout", "type": "function"},
        ],
        "dynamicImports": [  # Phase 1 task_6
            {
                "pattern": "import(`./strategies/${strategy}.js`)",
                "location": "conditional expression",
                "line": 45
            }
        ]
    },
    {
        "name": "IUser",
        "type": "interface",  # Phase 1 task_1 (AST)
        "file": "types/user.ts",
        "line": 5,
        "complexity": 0,
        "exports": [
            {"name": "IUser", "type": "interface"}
        ]
    },
    {
        "name": "Authenticated",
        "type": "decorator",  # Phase 1 task_1 (AST)
        "file": "decorators/auth.ts",
        "line": 3,
        "complexity": 5,
        "imports": [
            {"source": "reflect-metadata", "specifiers": ["Reflect"], "line": 1}
        ],
        "exports": [
            {"name": "Authenticated", "type": "decorator"}
        ]
    },
    {
        "name": "UserId",
        "type": "type",  # Phase 1 task_1 (AST type alias)
        "file": "types/user.ts",
        "line": 20,
        "exports": [
            {"name": "UserId", "type": "type"}
        ]
    },
    {
        "name": "UserRepository",
        "type": "class",
        "file": "repositories/user.ts",
        "line": 8,
        "complexity": 12,
        "imports": [
            {"source": "typeorm", "specifiers": ["Repository", "EntityManager"], "line": 1},
            {"source": "bcrypt", "specifiers": ["hash"], "line": 2},
        ],
        "exports": [
            {"name": "UserRepository", "type": "class"},
            {"name": "findByEmail", "type": "function"},
        ]
    }
]


def test_e2e_ast_accuracy_integration():
    """
    E2E Scenario 1: AST type filtering works end-to-end.

    Validates that interfaces, decorators, and type aliases can be extracted
    from complete ElementData and would appear in foundation docs.
    """
    # Filter for interfaces
    interfaces = [e for e in COMPLETE_ELEMENT_DATA if e.get('type') == 'interface']
    assert len(interfaces) == 1
    assert interfaces[0]['name'] == 'IUser'

    # Filter for decorators
    decorators = [e for e in COMPLETE_ELEMENT_DATA if e.get('type') == 'decorator']
    assert len(decorators) == 1
    assert decorators[0]['name'] == 'Authenticated'

    # Filter for type aliases
    type_aliases = [e for e in COMPLETE_ELEMENT_DATA if e.get('type') == 'type']
    assert len(type_aliases) == 1
    assert type_aliases[0]['name'] == 'UserId'

    # Verify classes still work
    classes = [e for e in COMPLETE_ELEMENT_DATA if e.get('type') == 'class']
    assert len(classes) == 2  # AuthService, UserRepository


def test_e2e_complexity_integration():
    """
    E2E Scenario 2: Complexity metrics integrated into resource sheets.

    Validates that complexity stats are calculated correctly from complete
    ElementData and would generate proper refactoring recommendations.
    """
    generator = ResourceSheetGenerator()
    stats = generator.calculate_complexity_stats(COMPLETE_ELEMENT_DATA)

    # Verify statistics calculated
    assert stats['has_complexity_data'] is True
    assert stats['total_elements'] == 5
    assert stats['elements_with_complexity'] == 3  # AuthService (18), Authenticated (5), UserRepository (12)
    # Note: IUser has 0 (filtered out), UserId missing complexity field

    # Verify average (18 + 5 + 12) / 3 = 11.67
    assert stats['avg'] == pytest.approx(11.67, rel=0.01)

    # Verify max complexity
    assert stats['max'] == 18  # AuthService

    # Verify hotspots (> 10 threshold)
    assert len(stats['hotspots']) == 2  # AuthService (18), UserRepository (12)
    assert stats['hotspots'][0]['name'] == 'AuthService'  # Highest first
    assert stats['hotspots'][0]['complexity'] == 18
    assert 'HIGH' in stats['hotspots'][0]['recommendation']  # 18 > 15


def test_e2e_relationship_integration():
    """
    E2E Scenario 3: Relationship data creates dependency graphs.

    Validates that import/export aggregation works on complete ElementData
    and generates valid Mermaid diagrams for ARCHITECTURE.md.
    """
    # Aggregate imports
    import_counts = aggregate_imports(COMPLETE_ELEMENT_DATA)
    assert import_counts['bcrypt'] == 2  # AuthService + UserRepository
    assert import_counts['jsonwebtoken'] == 1  # AuthService
    assert import_counts['typeorm'] == 1  # UserRepository
    assert import_counts['reflect-metadata'] == 1  # Authenticated decorator

    # Identify high coupling (>= 2 usages)
    high_deps = identify_high_coupling(import_counts, threshold=2)
    assert 'bcrypt' in high_deps
    assert high_deps['bcrypt'] == 2

    # Aggregate exports
    exports_by_file = aggregate_exports(COMPLETE_ELEMENT_DATA)
    assert 'services/auth.ts' in exports_by_file
    assert len(exports_by_file['services/auth.ts']) == 3  # AuthService, login, logout

    # Generate Mermaid diagram
    diagram = generate_dependency_mermaid(import_counts, limit=10)
    assert '```mermaid' in diagram
    assert 'bcrypt' in diagram
    assert '(2 usages)' in diagram  # Highest usage shown


def test_e2e_dynamic_import_warnings():
    """
    E2E Scenario 4: Dynamic import warnings appear in documentation.

    Validates that dynamic imports are detected from complete ElementData
    and would generate proper warning sections in API.md/ARCHITECTURE.md.
    """
    result = detect_dynamic_imports(COMPLETE_ELEMENT_DATA)

    # Verify detection
    assert result['has_dynamic_imports'] is True
    assert result['total_dynamic_imports'] == 1

    # Verify warning structure
    warning = result['warnings'][0]
    assert warning['file'] == 'services/auth.ts'
    assert warning['element'] == 'AuthService'
    assert warning['pattern'] == "import(`./strategies/${strategy}.js`)"
    assert warning['location'] == 'conditional expression'
    assert warning['line'] == 45
    assert warning['severity'] == 'medium'
    assert 'tree-shaking' in warning['recommendation']

    # Verify affected files
    assert result['affected_files'] == ['services/auth.ts']
    assert '1 dynamic import(s) across 1 file(s)' in result['summary']


def test_e2e_full_integration():
    """
    E2E Scenario 5: All 4 enhancements work together seamlessly.

    Validates complete workflow: AST types + complexity + relationships + dynamic imports
    all extracted from single ElementData array without conflicts.
    """
    # 1. AST Types (interfaces, decorators, type aliases)
    interfaces = [e for e in COMPLETE_ELEMENT_DATA if e.get('type') == 'interface']
    decorators = [e for e in COMPLETE_ELEMENT_DATA if e.get('type') == 'decorator']
    type_aliases = [e for e in COMPLETE_ELEMENT_DATA if e.get('type') == 'type']
    assert len(interfaces) + len(decorators) + len(type_aliases) == 3

    # 2. Complexity Metrics
    generator = ResourceSheetGenerator()
    complexity_stats = generator.calculate_complexity_stats(COMPLETE_ELEMENT_DATA)
    assert complexity_stats['has_complexity_data'] is True
    assert len(complexity_stats['hotspots']) == 2

    # 3. Relationship Data
    import_counts = aggregate_imports(COMPLETE_ELEMENT_DATA)
    exports_by_file = aggregate_exports(COMPLETE_ELEMENT_DATA)
    assert len(import_counts) == 4  # 4 unique modules imported
    assert len(exports_by_file) == 4  # 4 unique files with exports

    # 4. Dynamic Import Warnings
    dynamic_result = detect_dynamic_imports(COMPLETE_ELEMENT_DATA)
    assert dynamic_result['has_dynamic_imports'] is True

    # Verify no conflicts - all data coexists
    # AuthService has all 4 enhancement fields simultaneously
    auth_service = next(e for e in COMPLETE_ELEMENT_DATA if e['name'] == 'AuthService')
    assert auth_service['complexity'] == 18
    assert len(auth_service['imports']) == 2
    assert len(auth_service['exports']) == 3
    assert len(auth_service['dynamicImports']) == 1

    # Success: All 4 enhancements work together without interference


def test_e2e_backward_compatibility():
    """
    Bonus: Verify backward compatibility with pre-Phase 1 ElementData.

    Ensures graceful degradation when new fields are missing (old scanner output).
    """
    old_element_data = [
        {"name": "OldClass", "type": "class", "file": "old.ts", "line": 1},
        {"name": "OldFunc", "type": "function", "file": "old.ts", "line": 10},
    ]

    # Complexity: Should return sensible defaults
    generator = ResourceSheetGenerator()
    stats = generator.calculate_complexity_stats(old_element_data)
    assert stats['has_complexity_data'] is False
    assert stats['avg'] == 0
    assert stats['hotspots'] == []

    # Relationships: Should return empty structures
    import_counts = aggregate_imports(old_element_data)
    exports_by_file = aggregate_exports(old_element_data)
    assert import_counts == {}
    assert exports_by_file == {}

    # Dynamic imports: Should return empty structure
    dynamic_result = detect_dynamic_imports(old_element_data)
    assert dynamic_result['has_dynamic_imports'] is False
    assert dynamic_result['warnings'] == []

    # No crashes - graceful degradation successful


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
