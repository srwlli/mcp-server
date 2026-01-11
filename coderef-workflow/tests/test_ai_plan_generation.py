"""Unit tests for AI-powered plan generation."""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from generators.planning_generator import PlanningGenerator


class TestCodeRefDataLoading:
    """Test coderef data loading methods."""

    def test_load_coderef_index_success(self, tmp_path):
        """Test successful loading of index.json."""
        # Setup
        coderef_dir = tmp_path / ".coderef"
        coderef_dir.mkdir()
        index_file = coderef_dir / "index.json"
        test_data = [{"name": "test_function", "type": "function"}]
        index_file.write_text(json.dumps(test_data))

        generator = PlanningGenerator(tmp_path)

        # Execute
        result = generator._load_coderef_index()

        # Verify
        assert result == test_data
        assert len(result) == 1

    def test_load_coderef_index_missing(self, tmp_path):
        """Test loading when index.json doesn't exist."""
        generator = PlanningGenerator(tmp_path)

        # Execute
        result = generator._load_coderef_index()

        # Verify
        assert result is None

    def test_load_coderef_patterns_success(self, tmp_path):
        """Test successful loading of patterns.json."""
        # Setup
        reports_dir = tmp_path / ".coderef" / "reports"
        reports_dir.mkdir(parents=True)
        patterns_file = reports_dir / "patterns.json"
        test_data = {"patterns": [{"name": "error_handling", "count": 5}]}
        patterns_file.write_text(json.dumps(test_data))

        generator = PlanningGenerator(tmp_path)

        # Execute
        result = generator._load_coderef_patterns()

        # Verify
        assert result == test_data
        assert "patterns" in result

    def test_load_coderef_graph_success(self, tmp_path):
        """Test successful loading of graph.json."""
        # Setup
        coderef_dir = tmp_path / ".coderef"
        coderef_dir.mkdir()
        graph_file = coderef_dir / "graph.json"
        test_data = {"nodes": [{"id": "node1"}, {"id": "node2"}]}
        graph_file.write_text(json.dumps(test_data))

        generator = PlanningGenerator(tmp_path)

        # Execute
        result = generator._load_coderef_graph()

        # Verify
        assert result == test_data
        assert len(result["nodes"]) == 2

    def test_load_coderef_coverage_success(self, tmp_path):
        """Test successful loading of coverage.json."""
        # Setup
        reports_dir = tmp_path / ".coderef" / "reports"
        reports_dir.mkdir(parents=True)
        coverage_file = reports_dir / "coverage.json"
        test_data = {"overall_coverage": 85.5}
        coverage_file.write_text(json.dumps(test_data))

        generator = PlanningGenerator(tmp_path)

        # Execute
        result = generator._load_coderef_coverage()

        # Verify
        assert result == test_data
        assert result["overall_coverage"] == 85.5

    def test_load_coderef_complexity_success(self, tmp_path):
        """Test successful loading of complexity.json."""
        # Setup
        reports_dir = tmp_path / ".coderef" / "reports"
        reports_dir.mkdir(parents=True)
        complexity_file = reports_dir / "complexity.json"
        test_data = {"files": [{"path": "file1.py", "complexity": 10}]}
        complexity_file.write_text(json.dumps(test_data))

        generator = PlanningGenerator(tmp_path)

        # Execute
        result = generator._load_coderef_complexity()

        # Verify
        assert result == test_data
        assert len(result["files"]) == 1


class TestPreFlightValidation:
    """Test pre-flight validation method."""

    def test_validate_coderef_exists_success(self, tmp_path):
        """Test validation passes when all required files exist."""
        # Setup - create all required files
        coderef_dir = tmp_path / ".coderef"
        coderef_dir.mkdir()
        (coderef_dir / "index.json").write_text("[]")
        (coderef_dir / "graph.json").write_text("{}")

        reports_dir = coderef_dir / "reports"
        reports_dir.mkdir()
        (reports_dir / "patterns.json").write_text("{}")

        generator = PlanningGenerator(tmp_path)

        # Execute - should not raise
        generator._validate_coderef_exists()

    def test_validate_coderef_exists_missing_directory(self, tmp_path):
        """Test validation fails when .coderef/ directory missing."""
        generator = PlanningGenerator(tmp_path)

        # Execute & Verify
        with pytest.raises(ValueError) as exc_info:
            generator._validate_coderef_exists()

        assert ".coderef/ directory not found" in str(exc_info.value)
        assert "coderef scan" in str(exc_info.value)

    def test_validate_coderef_exists_missing_files(self, tmp_path):
        """Test validation fails when required files missing."""
        # Setup - create directory but not files
        coderef_dir = tmp_path / ".coderef"
        coderef_dir.mkdir()

        generator = PlanningGenerator(tmp_path)

        # Execute & Verify
        with pytest.raises(ValueError) as exc_info:
            generator._validate_coderef_exists()

        assert "Required .coderef/ files missing" in str(exc_info.value)

    def test_validate_coderef_exists_warns_on_stale(self, tmp_path):
        """Test validation warns when drift >10%."""
        # Setup
        coderef_dir = tmp_path / ".coderef"
        coderef_dir.mkdir()
        (coderef_dir / "index.json").write_text("[]")
        (coderef_dir / "graph.json").write_text("{}")

        reports_dir = coderef_dir / "reports"
        reports_dir.mkdir()
        (reports_dir / "patterns.json").write_text("{}")
        (reports_dir / "drift.json").write_text('{"drift_percentage": 15}')

        generator = PlanningGenerator(tmp_path)

        # Execute - should warn but not raise
        with patch('generators.planning_generator.logger') as mock_logger:
            generator._validate_coderef_exists()
            # Verify warning was logged
            assert any("stale" in str(call) for call in mock_logger.warning.call_args_list)


class TestPromptBuilder:
    """Test agent prompt building."""

    def test_build_agent_prompt_includes_requirements(self, tmp_path):
        """Test prompt includes all requirements from context."""
        generator = PlanningGenerator(tmp_path)

        context = {
            "description": "Test feature",
            "goal": "Test goal",
            "requirements": ["Req 1", "Req 2", "Req 3"],
            "constraints": ["Constraint 1"]
        }
        analysis = {"foundation_doc_content": {}}
        coderef_data = {
            "index": [{"name": "func1"}],
            "patterns": {"patterns": []},
            "graph": {"nodes": []},
            "coverage": {"overall_coverage": 80},
            "complexity": {}
        }
        template = {}

        # Execute
        prompt = generator._build_agent_prompt(
            "test-feature", context, analysis, coderef_data, template
        )

        # Verify
        assert "Test feature" in prompt
        assert "Test goal" in prompt
        assert "Req 1" in prompt
        assert "Req 2" in prompt
        assert "Req 3" in prompt
        assert "Constraint 1" in prompt

    def test_build_agent_prompt_includes_coderef_data(self, tmp_path):
        """Test prompt includes coderef data counts."""
        generator = PlanningGenerator(tmp_path)

        context = {"description": "Test", "goal": "Test", "requirements": [], "constraints": []}
        analysis = {"foundation_doc_content": {}}
        coderef_data = {
            "index": [{"name": f"elem{i}"} for i in range(100)],
            "patterns": {"patterns": [{"name": "pattern1"}]},
            "graph": {"nodes": [{"id": "node1"}]},
            "coverage": {"overall_coverage": 75.5},
            "complexity": {}
        }
        template = {}

        # Execute
        prompt = generator._build_agent_prompt(
            "test-feature", context, analysis, coderef_data, template
        )

        # Verify
        assert "100" in prompt  # index count
        assert "75.5%" in prompt  # coverage
        assert "CODE INVENTORY" in prompt
        assert "CODING PATTERNS" in prompt

    def test_format_list_truncates_long_lists(self, tmp_path):
        """Test list formatting truncates when >10 items."""
        generator = PlanningGenerator(tmp_path)

        long_list = [f"Item {i}" for i in range(15)]

        # Execute
        result = generator._format_list(long_list, max_items=10)

        # Verify
        assert "Item 0" in result
        assert "Item 9" in result
        assert "and 5 more" in result


class TestPostGenerationValidation:
    """Test post-generation plan validation."""

    def test_validate_plan_uses_coderef_detects_generic_tasks(self, tmp_path):
        """Test validation detects generic tasks without file references."""
        generator = PlanningGenerator(tmp_path)

        plan = {
            "UNIVERSAL_PLANNING_STRUCTURE": {
                "5_task_id_system": {
                    "tasks": [
                        "IMPL-001: Implement feature following existing patterns",
                        "IMPL-002: Add functionality following existing patterns",
                        "IMPL-003: Modify src/auth.py lines 45-60 - add method"
                    ]
                },
                "6_implementation_phases": {
                    "phases": [{"rationale": "Test"}]
                }
            }
        }
        coderef_data = {}

        # Execute - should warn but not raise
        with patch('generators.planning_generator.logger') as mock_logger:
            generator._validate_plan_uses_coderef(plan, coderef_data)
            # Verify warning about generic tasks
            assert any("generic tasks" in str(call) for call in mock_logger.warning.call_args_list)

    def test_validate_plan_uses_coderef_detects_missing_rationale(self, tmp_path):
        """Test validation detects phases without rationale."""
        generator = PlanningGenerator(tmp_path)

        plan = {
            "UNIVERSAL_PLANNING_STRUCTURE": {
                "5_task_id_system": {
                    "tasks": ["IMPL-001: Modify src/file.py - add method"]
                },
                "6_implementation_phases": {
                    "phases": [
                        {"name": "Phase 1"},  # Missing rationale
                        {"name": "Phase 2", "rationale": "Good reason"}
                    ]
                }
            }
        }
        coderef_data = {}

        # Execute
        with patch('generators.planning_generator.logger') as mock_logger:
            generator._validate_plan_uses_coderef(plan, coderef_data)
            # Verify warning about missing rationale
            assert any("rationale" in str(call) for call in mock_logger.warning.call_args_list)


class TestTelemetryTracking:
    """Test telemetry tracking."""

    def test_track_coderef_usage_logs_tool_calls(self, tmp_path):
        """Test telemetry tracks tool usage."""
        generator = PlanningGenerator(tmp_path)

        execution_log = {
            "actions": [
                {"tool": "coderef_query"},
                {"tool": "coderef_impact"},
                {"tool": "coderef_query"},  # Duplicate
                {"tool": "other_tool"}  # Not tracked
            ]
        }

        # Execute
        with patch('generators.planning_generator.logger') as mock_logger:
            result = generator._track_coderef_usage(execution_log)

            # Verify
            assert result["coderef_query"] == 2
            assert result["coderef_impact"] == 1
            assert result["coderef_patterns"] == 0

    def test_track_coderef_usage_warns_on_low_usage(self, tmp_path):
        """Test telemetry warns when <5 tool calls."""
        generator = PlanningGenerator(tmp_path)

        execution_log = {
            "actions": [
                {"tool": "coderef_query"},
                {"tool": "coderef_impact"}
            ]
        }

        # Execute
        with patch('generators.planning_generator.logger') as mock_logger:
            generator._track_coderef_usage(execution_log)
            # Verify warning about low usage
            assert any("only 2 coderef tool calls" in str(call)
                      for call in mock_logger.warning.call_args_list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
