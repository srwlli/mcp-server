"""
Comprehensive unit tests for coderef_context.py
Tests index.json snapshot comparison and delta calculation
"""
import pytest
import json
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path
from papertrail.extensions.coderef_context import CodeRefContextExtension


class TestCodeRefContextInitialization:
    """Test initialization and setup"""

    def test_init_without_project_path(self):
        ext = CodeRefContextExtension()
        assert ext.project_path is None

    def test_init_with_project_path(self):
        ext = CodeRefContextExtension(project_path=Path("/test/project"))
        assert ext.project_path == Path("/test/project")

    def test_init_with_string_project_path(self):
        ext = CodeRefContextExtension(project_path="/test/project")
        assert ext.project_path == Path("/test/project")


class TestLoadIndex:
    """Test _load_index helper method"""

    def test_loads_valid_index(self):
        index_data = [
            {"name": "Component1", "type": "component", "file": "src/a.py", "line": 10},
            {"name": "func1", "type": "function", "file": "src/b.py", "line": 20}
        ]
        mock_path = MagicMock()
        mock_path.exists.return_value = True

        with patch('builtins.open', mock_open(read_data=json.dumps(index_data))):
            ext = CodeRefContextExtension()
            result = ext._load_index(mock_path)
            assert len(result) == 2
            assert result[0]['name'] == 'Component1'

    def test_handles_file_not_found(self):
        ext = CodeRefContextExtension()
        mock_path = MagicMock()
        mock_path.exists.return_value = False
        result = ext._load_index(mock_path)
        assert result == []

    def test_handles_invalid_json(self):
        ext = CodeRefContextExtension()
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        with patch('builtins.open', mock_open(read_data="invalid json")):
            result = ext._load_index(mock_path)
            assert result == []

    def test_handles_non_array_json(self):
        ext = CodeRefContextExtension()
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        with patch('builtins.open', mock_open(read_data='{"key": "value"}')):
            result = ext._load_index(mock_path)
            assert result == []


class TestGetComponentsAdded:
    """Test get_components_added method"""

    @patch.object(CodeRefContextExtension, '_load_index')
    def test_detects_new_components(self, mock_load):
        baseline = [
            {"name": "OldComponent", "type": "component", "file": "src/old.py", "line": 10}
        ]
        current = [
            {"name": "OldComponent", "type": "component", "file": "src/old.py", "line": 10},
            {"name": "NewComponent", "type": "component", "file": "src/new.py", "line": 20}
        ]

        mock_load.side_effect = [baseline, current]
        ext = CodeRefContextExtension()
        added = ext.get_components_added("baseline.json", "current.json")

        assert len(added) == 1
        assert added[0]['name'] == 'NewComponent'
        assert added[0]['type'] == 'component'

    @patch.object(CodeRefContextExtension, '_load_index')
    def test_no_new_components(self, mock_load):
        baseline = [
            {"name": "Component1", "type": "component", "file": "src/a.py", "line": 10}
        ]
        current = baseline.copy()

        mock_load.side_effect = [baseline, current]
        ext = CodeRefContextExtension()
        added = ext.get_components_added("baseline.json", "current.json")

        assert len(added) == 0

    @patch.object(CodeRefContextExtension, '_load_index')
    def test_ignores_non_components(self, mock_load):
        baseline = []
        current = [
            {"name": "NewFunc", "type": "function", "file": "src/a.py", "line": 10},
            {"name": "NewComp", "type": "component", "file": "src/b.py", "line": 20}
        ]

        mock_load.side_effect = [baseline, current]
        ext = CodeRefContextExtension()
        added = ext.get_components_added("baseline.json", "current.json")

        assert len(added) == 1
        assert added[0]['name'] == 'NewComp'

    @patch.object(CodeRefContextExtension, '_load_index')
    def test_handles_empty_baseline(self, mock_load):
        baseline = []
        current = [
            {"name": "Comp1", "type": "component", "file": "src/a.py", "line": 10},
            {"name": "Comp2", "type": "component", "file": "src/b.py", "line": 20}
        ]

        mock_load.side_effect = [baseline, current]
        ext = CodeRefContextExtension()
        added = ext.get_components_added("baseline.json", "current.json")

        assert len(added) == 2


class TestGetFunctionsAdded:
    """Test get_functions_added method"""

    @patch.object(CodeRefContextExtension, '_load_index')
    def test_detects_new_functions(self, mock_load):
        baseline = [
            {"name": "oldFunc", "type": "function", "file": "src/old.py", "line": 10}
        ]
        current = [
            {"name": "oldFunc", "type": "function", "file": "src/old.py", "line": 10},
            {"name": "newFunc", "type": "function", "file": "src/new.py", "line": 20}
        ]

        mock_load.side_effect = [baseline, current]
        ext = CodeRefContextExtension()
        added = ext.get_functions_added("baseline.json", "current.json")

        assert len(added) == 1
        assert added[0]['name'] == 'newFunc'

    @patch.object(CodeRefContextExtension, '_load_index')
    def test_detects_methods_and_functions(self, mock_load):
        baseline = []
        current = [
            {"name": "func1", "type": "function", "file": "src/a.py", "line": 10},
            {"name": "method1", "type": "method", "file": "src/b.py", "line": 20}
        ]

        mock_load.side_effect = [baseline, current]
        ext = CodeRefContextExtension()
        added = ext.get_functions_added("baseline.json", "current.json")

        assert len(added) == 2

    @patch.object(CodeRefContextExtension, '_load_index')
    def test_ignores_non_functions(self, mock_load):
        baseline = []
        current = [
            {"name": "Comp", "type": "component", "file": "src/a.py", "line": 10},
            {"name": "func", "type": "function", "file": "src/b.py", "line": 20}
        ]

        mock_load.side_effect = [baseline, current]
        ext = CodeRefContextExtension()
        added = ext.get_functions_added("baseline.json", "current.json")

        assert len(added) == 1
        assert added[0]['name'] == 'func'


class TestCalculateComplexityDelta:
    """Test calculate_complexity_delta method"""

    @patch.object(CodeRefContextExtension, '_load_index')
    def test_calculates_average_complexity_increase(self, mock_load):
        baseline = [
            {"name": "func1", "type": "function", "complexity": 5},
            {"name": "func2", "type": "function", "complexity": 10}
        ]
        current = [
            {"name": "func1", "type": "function", "complexity": 8},
            {"name": "func2", "type": "function", "complexity": 12}
        ]

        mock_load.side_effect = [baseline, current]
        ext = CodeRefContextExtension()
        delta = ext.calculate_complexity_delta("baseline.json", "current.json")

        # Baseline avg: (5+10)/2 = 7.5, Current avg: (8+12)/2 = 10, Delta: 2.5
        assert delta == 2.5

    @patch.object(CodeRefContextExtension, '_load_index')
    def test_calculates_complexity_decrease(self, mock_load):
        baseline = [
            {"name": "func1", "type": "function", "complexity": 10}
        ]
        current = [
            {"name": "func1", "type": "function", "complexity": 5}
        ]

        mock_load.side_effect = [baseline, current]
        ext = CodeRefContextExtension()
        delta = ext.calculate_complexity_delta("baseline.json", "current.json")

        assert delta == -5.0

    @patch.object(CodeRefContextExtension, '_load_index')
    def test_handles_missing_complexity(self, mock_load):
        baseline = [
            {"name": "func1", "type": "function"}  # No complexity field
        ]
        current = [
            {"name": "func1", "type": "function", "complexity": 5}
        ]

        mock_load.side_effect = [baseline, current]
        ext = CodeRefContextExtension()
        delta = ext.calculate_complexity_delta("baseline.json", "current.json")

        # Should handle gracefully
        assert isinstance(delta, (int, float))

    @patch.object(CodeRefContextExtension, '_load_index')
    def test_empty_indexes_return_zero(self, mock_load):
        mock_load.side_effect = [[], []]
        ext = CodeRefContextExtension()
        delta = ext.calculate_complexity_delta("baseline.json", "current.json")

        assert delta == 0.0


class TestGetAllChanges:
    """Test get_all_changes method"""

    @patch.object(CodeRefContextExtension, 'calculate_complexity_delta')
    @patch.object(CodeRefContextExtension, 'get_functions_added')
    @patch.object(CodeRefContextExtension, 'get_components_added')
    def test_aggregates_all_changes(self, mock_comps, mock_funcs, mock_complexity):
        mock_comps.return_value = [
            {"name": "NewComp", "type": "component", "file": "src/comp.py", "line": 10}
        ]
        mock_funcs.return_value = [
            {"name": "newFunc", "type": "function", "file": "src/func.py", "line": 20}
        ]
        mock_complexity.return_value = 2.5

        ext = CodeRefContextExtension()
        changes = ext.get_all_changes("baseline.json", "current.json")

        assert len(changes['components_added']) == 1
        assert len(changes['functions_added']) == 1
        assert changes['complexity_delta'] == 2.5

    @patch.object(CodeRefContextExtension, 'calculate_complexity_delta')
    @patch.object(CodeRefContextExtension, 'get_functions_added')
    @patch.object(CodeRefContextExtension, 'get_components_added')
    def test_no_changes(self, mock_comps, mock_funcs, mock_complexity):
        mock_comps.return_value = []
        mock_funcs.return_value = []
        mock_complexity.return_value = 0.0

        ext = CodeRefContextExtension()
        changes = ext.get_all_changes("baseline.json", "current.json")

        assert changes['components_added'] == []
        assert changes['functions_added'] == []
        assert changes['complexity_delta'] == 0.0


class TestLegacyMethods:
    """Test backward compatibility with legacy scan method"""

    def test_scan_legacy_returns_success(self):
        ext = CodeRefContextExtension()
        result = ext.scan()
        assert result['status'] == 'success'

    def test_scan_legacy_has_message(self):
        ext = CodeRefContextExtension()
        result = ext.scan()
        assert 'message' in result
        assert 'stub' in result['message'].lower()

    def test_scan_legacy_has_elements_found(self):
        ext = CodeRefContextExtension()
        result = ext.scan()
        assert 'elements_found' in result
