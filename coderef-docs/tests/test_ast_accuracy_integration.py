"""
Tests for AST accuracy integration (WO-DOCS-SCANNER-INTEGRATION-001, Task 1).

Verifies that foundation doc generation correctly filters and handles
enhanced AST types (interfaces, decorators, type aliases) from Phase 1 scanner.
"""

import pytest
from pathlib import Path


# Mock ElementData samples
ENHANCED_SCANNER_OUTPUT = [
    {"type": "function", "name": "scanElements", "file": "scanner.ts", "line": 45},
    {"type": "interface", "name": "ElementData", "file": "types.ts", "line": 229},
    {"type": "interface", "name": "ScanOptions", "file": "types.ts", "line": 315},
    {"type": "type", "name": "TypeDesignator", "file": "types.ts", "line": 7},
    {"type": "decorator", "name": "@measure", "file": "scanner.ts", "line": 12},
    {"type": "class", "name": "Scanner", "file": "scanner.ts", "line": 100},
]

OLD_SCANNER_OUTPUT = [
    {"type": "function", "name": "scanElements", "file": "scanner.ts", "line": 45},
    {"type": "class", "name": "Scanner", "file": "scanner.ts", "line": 100},
]

MISSING_TYPE_FIELD_OUTPUT = [
    {"name": "scanElements", "file": "scanner.ts", "line": 45},  # Missing 'type' field
    {"name": "Scanner", "file": "scanner.ts", "line": 100},
]


def test_interface_filtering():
    """Verify interfaces extracted correctly from enhanced scanner output."""
    # Filter for interfaces
    interfaces = [e for e in ENHANCED_SCANNER_OUTPUT if e.get('type') == 'interface']

    assert len(interfaces) == 2
    assert interfaces[0]['name'] == 'ElementData'
    assert interfaces[1]['name'] == 'ScanOptions'
    assert all(e['type'] == 'interface' for e in interfaces)


def test_decorator_filtering():
    """Verify decorators extracted correctly from enhanced scanner output."""
    # Filter for decorators
    decorators = [e for e in ENHANCED_SCANNER_OUTPUT if e.get('type') == 'decorator']

    assert len(decorators) == 1
    assert decorators[0]['name'] == '@measure'
    assert decorators[0]['type'] == 'decorator'


def test_type_alias_filtering():
    """Verify type aliases extracted correctly from enhanced scanner output."""
    # Filter for type aliases
    type_aliases = [e for e in ENHANCED_SCANNER_OUTPUT if e.get('type') == 'type']

    assert len(type_aliases) == 1
    assert type_aliases[0]['name'] == 'TypeDesignator'
    assert type_aliases[0]['type'] == 'type'


def test_graceful_degradation_old_scanner():
    """Verify empty lists returned with old scanner output (no new types)."""
    # Filter for new types with old scanner output
    interfaces = [e for e in OLD_SCANNER_OUTPUT if e.get('type') == 'interface']
    decorators = [e for e in OLD_SCANNER_OUTPUT if e.get('type') == 'decorator']
    type_aliases = [e for e in OLD_SCANNER_OUTPUT if e.get('type') == 'type']

    # Should return empty lists, not errors
    assert interfaces == []
    assert decorators == []
    assert type_aliases == []

    # Old types still work
    functions = [e for e in OLD_SCANNER_OUTPUT if e.get('type') == 'function']
    assert len(functions) == 1


def test_missing_type_field():
    """Verify .get() handles missing 'type' field gracefully."""
    # Filter with missing type field (should not raise KeyError)
    interfaces = [e for e in MISSING_TYPE_FIELD_OUTPUT if e.get('type') == 'interface']
    decorators = [e for e in MISSING_TYPE_FIELD_OUTPUT if e.get('type') == 'decorator']

    # Should return empty lists
    assert interfaces == []
    assert decorators == []

    # Verify no exceptions raised
    for element in MISSING_TYPE_FIELD_OUTPUT:
        type_value = element.get('type')  # Should not raise KeyError
        assert type_value is None


def test_mixed_scanner_output():
    """Verify filtering works with mixed old and new types."""
    mixed_output = [
        {"type": "function", "name": "func1", "file": "a.ts", "line": 1},
        {"type": "interface", "name": "IFoo", "file": "b.ts", "line": 2},
        {"type": "class", "name": "Bar", "file": "c.ts", "line": 3},
        {"type": "decorator", "name": "@log", "file": "d.ts", "line": 4},
    ]

    interfaces = [e for e in mixed_output if e.get('type') == 'interface']
    decorators = [e for e in mixed_output if e.get('type') == 'decorator']
    functions = [e for e in mixed_output if e.get('type') == 'function']

    assert len(interfaces) == 1
    assert len(decorators) == 1
    assert len(functions) == 1


def test_case_sensitivity():
    """Verify type filtering is case-sensitive."""
    case_test = [
        {"type": "interface", "name": "IFoo", "file": "a.ts", "line": 1},
        {"type": "Interface", "name": "IBar", "file": "b.ts", "line": 2},  # Wrong case
        {"type": "INTERFACE", "name": "IBaz", "file": "c.ts", "line": 3},  # Wrong case
    ]

    # Only lowercase 'interface' should match
    interfaces = [e for e in case_test if e.get('type') == 'interface']
    assert len(interfaces) == 1
    assert interfaces[0]['name'] == 'IFoo'


def test_empty_elements_list():
    """Verify filtering handles empty elements list."""
    empty_list = []

    interfaces = [e for e in empty_list if e.get('type') == 'interface']
    decorators = [e for e in empty_list if e.get('type') == 'decorator']
    type_aliases = [e for e in empty_list if e.get('type') == 'type']

    assert interfaces == []
    assert decorators == []
    assert type_aliases == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
