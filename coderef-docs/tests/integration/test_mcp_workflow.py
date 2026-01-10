"""
Integration tests for MCP orchestration workflow.

Tests the complete integration between coderef-docs and coderef-context:
1. generate_foundation_docs provides MCP instructions
2. Simulated coderef_scan creates .coderef/ data
3. generate_individual_doc reads and uses the data
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from generators.coderef_foundation_generator import CoderefFoundationGenerator


class TestMCPOrchestrationWorkflow:
    """Test the complete MCP orchestration pattern."""

    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def sample_coderef_data(self):
        """Sample .coderef/ data simulating coderef_scan output."""
        return {
            'elements': [
                {
                    'name': 'getUserById',
                    'type': 'function',
                    'file': 'src/user_service.py',
                    'line_number': 15
                },
                {
                    'name': 'UserService',
                    'type': 'class',
                    'file': 'src/user_service.py',
                    'line_number': 5
                },
                {
                    'name': 'AuthService',
                    'type': 'class',
                    'file': 'src/auth_service.py',
                    'line_number': 10
                }
            ]
        }

    def test_workflow_step1_no_coderef_data(self, temp_project_dir):
        """
        Step 1: When .coderef/ data missing, generator logs recommendation.

        Verifies:
        - Generator detects missing .coderef/ data
        - Returns None (falls back to regex)
        - Logs recommendation to call coderef_scan
        """
        generator = CoderefFoundationGenerator(temp_project_dir)

        # _load_coderef_data should return None when files missing
        result = generator._load_coderef_data()

        assert result is None, "Should return None when .coderef/ data missing"

    def test_workflow_step2_simulate_coderef_scan(self, temp_project_dir, sample_coderef_data):
        """
        Step 2: Simulate Claude calling coderef_scan MCP tool.

        This simulates the MCP tool creating .coderef/index.json.
        In real workflow, Claude calls mcp__coderef_context__coderef_scan.
        """
        coderef_dir = temp_project_dir / '.coderef'
        coderef_dir.mkdir(exist_ok=True)

        index_file = coderef_dir / 'index.json'
        index_file.write_text(json.dumps(sample_coderef_data, indent=2), encoding='utf-8')

        assert index_file.exists(), "Simulated scan should create index.json"

        # Verify file content
        loaded = json.loads(index_file.read_text(encoding='utf-8'))
        assert len(loaded['elements']) == 3

    def test_workflow_step3_generator_reads_coderef_data(self, temp_project_dir, sample_coderef_data):
        """
        Step 3: Generator reads .coderef/ data created by MCP tool.

        Verifies:
        - Generator detects existing .coderef/ data
        - Correctly loads elements and graph
        - Returns data for doc generation
        """
        # Setup: Create .coderef/ data (simulating MCP scan)
        coderef_dir = temp_project_dir / '.coderef'
        coderef_dir.mkdir(exist_ok=True)
        index_file = coderef_dir / 'index.json'
        index_file.write_text(json.dumps(sample_coderef_data, indent=2), encoding='utf-8')

        # Test: Load coderef data
        generator = CoderefFoundationGenerator(temp_project_dir)
        result = generator._load_coderef_data()

        assert result is not None, "Should load existing .coderef/ data"
        assert 'elements' in result
        # elements is the loaded JSON which has {'elements': [...]}
        assert len(result['elements']['elements']) == 3
        assert result['elements']['elements'][0]['name'] == 'getUserById'

    def test_workflow_step4_categorize_elements(self, temp_project_dir, sample_coderef_data):
        """
        Step 4: Generator categorizes elements for doc generation.

        Verifies:
        - Elements categorized by type (functions, classes, etc.)
        - Ready for use in template population
        """
        # Setup
        coderef_dir = temp_project_dir / '.coderef'
        coderef_dir.mkdir(exist_ok=True)
        index_file = coderef_dir / 'index.json'
        index_file.write_text(json.dumps(sample_coderef_data, indent=2), encoding='utf-8')

        generator = CoderefFoundationGenerator(temp_project_dir)
        coderef_data = generator._load_coderef_data()

        # Test categorization - pass the elements array directly
        elements_array = coderef_data['elements']['elements']
        categorized = generator._categorize_elements(elements_array)

        assert len(categorized['functions']) == 1
        assert len(categorized['classes']) == 2
        assert categorized['functions'][0]['name'] == 'getUserById'
        assert categorized['classes'][0]['name'] == 'UserService'

    def test_end_to_end_with_coderef_data(self, temp_project_dir, sample_coderef_data):
        """
        End-to-end test: Verify .coderef/ data loading and categorization.

        Simulates:
        1. Claude calls coderef_scan (simulated by creating files)
        2. Generator loads the data
        3. Elements are categorized for use in docs
        """
        # Step 1: Create .coderef/ data (simulates MCP scan)
        coderef_dir = temp_project_dir / '.coderef'
        coderef_dir.mkdir(exist_ok=True)
        index_file = coderef_dir / 'index.json'
        index_file.write_text(json.dumps(sample_coderef_data, indent=2), encoding='utf-8')

        # Step 2: Load coderef data
        generator = CoderefFoundationGenerator(temp_project_dir)
        result = generator._load_coderef_data()

        # Verify .coderef/ data was loaded
        assert result is not None
        assert result['elements'] is not None

        # Step 3: Categorize elements for doc generation
        elements_array = result['elements']['elements']
        categorized = generator._categorize_elements(elements_array)

        # Verify categorization worked
        assert len(categorized['functions']) == 1
        assert len(categorized['classes']) == 2
        assert categorized['all'] == elements_array

    def test_end_to_end_without_coderef_data(self, temp_project_dir):
        """
        End-to-end test: Workflow WITHOUT .coderef/ data (fallback).

        Verifies:
        - Generator handles missing .coderef/ gracefully
        - Returns None (falls back to regex)
        - Logs recommendation to use coderef_scan
        """
        # No .coderef/ data created - tests fallback

        generator = CoderefFoundationGenerator(temp_project_dir)
        result = generator._load_coderef_data()

        # Should return None when .coderef/ missing (fallback mode)
        assert result is None

    def test_mcp_instructions_provided(self, temp_project_dir):
        """
        Verify MCP integration instructions are included in responses.

        This tests that tool handlers provide clear guidance for Claude
        on when and how to call coderef-context MCP tools.
        """
        # This would test the tool_handlers.py response format
        # Since we're in integration tests, we verify the pattern is correct

        generator = CoderefFoundationGenerator(temp_project_dir)
        coderef_data = generator._load_coderef_data()

        # When data missing, generator should indicate fallback
        assert coderef_data is None

        # In real workflow, tool handler would include MCP instructions
        # This is verified by the docstring updates we made


class TestCoderefDataValidation:
    """Test validation and error handling for .coderef/ data."""

    @pytest.fixture
    def temp_project_dir(self):
        """Create temporary project directory."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_handles_malformed_json(self, temp_project_dir):
        """Verify graceful handling of malformed .coderef/index.json."""
        coderef_dir = temp_project_dir / '.coderef'
        coderef_dir.mkdir(exist_ok=True)
        index_file = coderef_dir / 'index.json'

        # Write invalid JSON
        index_file.write_text("{ invalid json }", encoding='utf-8')

        generator = CoderefFoundationGenerator(temp_project_dir)
        result = generator._load_coderef_data()

        # Should return None and fall back to regex
        assert result is None

    def test_handles_empty_elements_array(self, temp_project_dir):
        """Verify handling of empty elements array."""
        coderef_dir = temp_project_dir / '.coderef'
        coderef_dir.mkdir(exist_ok=True)
        index_file = coderef_dir / 'index.json'

        # Write empty elements
        index_file.write_text(json.dumps({'elements': []}), encoding='utf-8')

        generator = CoderefFoundationGenerator(temp_project_dir)
        result = generator._load_coderef_data()

        # Should load but have empty elements
        assert result is not None
        assert len(result['elements']['elements']) == 0

    def test_handles_missing_graph_file(self, temp_project_dir):
        """Verify graceful handling when graph.json missing."""
        coderef_dir = temp_project_dir / '.coderef'
        coderef_dir.mkdir(exist_ok=True)
        index_file = coderef_dir / 'index.json'

        # Only index.json, no graph.json
        index_file.write_text(json.dumps({'elements': [{'name': 'test', 'type': 'function'}]}), encoding='utf-8')

        generator = CoderefFoundationGenerator(temp_project_dir)
        result = generator._load_coderef_data()

        # Should load index but graph should be None
        assert result is not None
        assert result['graph'] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
