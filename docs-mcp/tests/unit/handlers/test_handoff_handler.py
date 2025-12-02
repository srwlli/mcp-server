"""Unit tests for handoff context generation handler."""

import pytest
from pathlib import Path
import json
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from generators.handoff_generator import HandoffGenerator


class TestPlanJsonParser:
    """Test plan.json parsing functionality."""

    def test_parse_plan_json_valid(self, tmp_path):
        """TEST-001: Verify plan.json parsing with valid input."""
        # Create test plan.json
        plan_data = {
            "META_DOCUMENTATION": {
                "workorder_id": "WO-TEST-001",
                "feature_name": "test-feature"
            },
            "UNIVERSAL_PLANNING_STRUCTURE": {
                "1_executive_summary": {
                    "description": "Test feature description"
                },
                "9_implementation_checklist": {
                    "phase_1": [
                        "☑ TASK-001: Completed task",
                        "☐ TASK-002: Pending task"
                    ]
                }
            }
        }

        feature_dir = tmp_path / "test-feature"
        feature_dir.mkdir()
        plan_file = feature_dir / "plan.json"
        plan_file.write_text(json.dumps(plan_data), encoding="utf-8")

        # Test parsing
        generator = HandoffGenerator(tmp_path)
        result = generator._parse_plan_json(feature_dir)

        assert result is not None
        assert result["META_DOCUMENTATION"]["workorder_id"] == "WO-TEST-001"
        assert "1_executive_summary" in result["UNIVERSAL_PLANNING_STRUCTURE"]

    def test_parse_plan_json_missing(self, tmp_path):
        """TEST-001: Verify graceful handling of missing plan.json."""
        feature_dir = tmp_path / "test-feature"
        feature_dir.mkdir()

        generator = HandoffGenerator(tmp_path)
        result = generator._parse_plan_json(feature_dir)

        assert result is None

    def test_parse_plan_json_malformed(self, tmp_path):
        """TEST-001: Verify error handling for malformed JSON."""
        feature_dir = tmp_path / "test-feature"
        feature_dir.mkdir()
        plan_file = feature_dir / "plan.json"
        plan_file.write_text("{ invalid json }", encoding="utf-8")

        generator = HandoffGenerator(tmp_path)
        result = generator._parse_plan_json(feature_dir)

        assert result is None


class TestAnalysisJsonParser:
    """Test analysis.json parsing functionality."""

    def test_parse_analysis_json_valid(self, tmp_path):
        """TEST-002: Verify analysis.json parsing."""
        # Create test analysis.json
        analysis_data = {
            "technology_stack": {
                "language": "Python",
                "framework": "Flask"
            },
            "project_structure": {
                "organization_pattern": "modular"
            }
        }

        feature_dir = tmp_path / "test-feature"
        feature_dir.mkdir()
        analysis_file = feature_dir / "analysis.json"
        analysis_file.write_text(json.dumps(analysis_data), encoding="utf-8")

        generator = HandoffGenerator(tmp_path)
        result = generator._parse_analysis_json(feature_dir)

        assert result is not None
        assert result["technology_stack"]["language"] == "Python"
        assert result["technology_stack"]["framework"] == "Flask"

    def test_parse_analysis_json_missing(self, tmp_path):
        """TEST-002: Verify graceful handling of missing analysis.json."""
        feature_dir = tmp_path / "test-feature"
        feature_dir.mkdir()

        generator = HandoffGenerator(tmp_path)
        result = generator._parse_analysis_json(feature_dir)

        assert result is None


class TestGitHistoryParser:
    """Test git history parsing functionality."""

    @patch('subprocess.run')
    def test_parse_git_history_with_commits(self, mock_run, tmp_path):
        """TEST-003: Verify git commit extraction."""
        # Mock git log output
        mock_log_result = Mock()
        mock_log_result.returncode = 0
        mock_log_result.stdout = "abc123 First commit\ndef456 Second commit\n"

        # Mock git status output
        mock_status_result = Mock()
        mock_status_result.returncode = 0
        mock_status_result.stdout = " M file1.py\n?? file2.py\n"

        mock_run.side_effect = [mock_log_result, mock_status_result]

        generator = HandoffGenerator(tmp_path)
        result = generator._parse_git_history("test-feature")

        assert result is not None
        assert len(result["recent_commits"]) == 2
        assert "abc123 First commit" in result["recent_commits"]
        assert len(result["uncommitted_changes"]) == 2

    @patch('subprocess.run')
    def test_parse_git_history_no_git(self, mock_run, tmp_path):
        """TEST-003: Verify handling when git not available."""
        mock_run.side_effect = FileNotFoundError("git not found")

        generator = HandoffGenerator(tmp_path)
        result = generator._parse_git_history("test-feature")

        assert result is None

    @patch('subprocess.run')
    def test_parse_git_history_no_commits(self, mock_run, tmp_path):
        """TEST-003: Verify handling when no matching commits."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = ""

        mock_run.return_value = mock_result

        generator = HandoffGenerator(tmp_path)
        result = generator._parse_git_history("test-feature")

        assert result is not None
        assert len(result["recent_commits"]) == 0


class TestHandoffGenerator:
    """Test HandoffGenerator template rendering."""

    def test_generate_full_mode(self, tmp_path):
        """TEST-004: Verify full template rendering."""
        # Setup test feature directory
        feature_dir = tmp_path / "coderef" / "working" / "test-feature"
        feature_dir.mkdir(parents=True)

        # Create minimal plan.json
        plan_data = {
            "META_DOCUMENTATION": {"workorder_id": "WO-TEST-001"},
            "UNIVERSAL_PLANNING_STRUCTURE": {
                "1_executive_summary": {"description": "Test description"},
                "9_implementation_checklist": {"phase_1": ["☐ TASK-001: Test task"]}
            }
        }
        (feature_dir / "plan.json").write_text(json.dumps(plan_data), encoding="utf-8")

        generator = HandoffGenerator(tmp_path)

        with patch.object(generator, '_parse_git_history', return_value=None):
            result = generator.generate_handoff_context("test-feature", "full")

        assert result["success"] is True
        assert result["mode"] == "full"
        assert "claude.md" in result["output_path"]

    def test_generate_minimal_mode(self, tmp_path):
        """TEST-004: Verify minimal template rendering."""
        # Setup test feature directory
        feature_dir = tmp_path / "coderef" / "working" / "test-feature"
        feature_dir.mkdir(parents=True)

        # Create minimal plan.json
        plan_data = {
            "META_DOCUMENTATION": {"workorder_id": "WO-TEST-001"},
            "UNIVERSAL_PLANNING_STRUCTURE": {
                "1_executive_summary": {"description": "Test"},
                "9_implementation_checklist": {}
            }
        }
        (feature_dir / "plan.json").write_text(json.dumps(plan_data), encoding="utf-8")

        generator = HandoffGenerator(tmp_path)

        with patch.object(generator, '_parse_git_history', return_value=None):
            result = generator.generate_handoff_context("test-feature", "minimal")

        assert result["success"] is True
        assert result["mode"] == "minimal"

    def test_backup_existing_claude_md(self, tmp_path):
        """TEST-004: Verify backup creation for existing files."""
        feature_dir = tmp_path / "coderef" / "working" / "test-feature"
        feature_dir.mkdir(parents=True)

        # Create existing claude.md
        existing_content = "# Existing Content"
        claude_file = feature_dir / "claude.md"
        claude_file.write_text(existing_content, encoding="utf-8")

        # Create minimal plan.json
        plan_data = {
            "META_DOCUMENTATION": {"workorder_id": "WO-TEST-001"},
            "UNIVERSAL_PLANNING_STRUCTURE": {
                "1_executive_summary": {"description": "Test"},
                "9_implementation_checklist": {}
            }
        }
        (feature_dir / "plan.json").write_text(json.dumps(plan_data), encoding="utf-8")

        generator = HandoffGenerator(tmp_path)

        with patch.object(generator, '_parse_git_history', return_value=None):
            result = generator.generate_handoff_context("test-feature", "full")

        # Check backup was created
        backup_files = list(feature_dir.glob("claude.backup-*.md"))
        assert len(backup_files) == 1
        assert backup_files[0].read_text(encoding="utf-8") == existing_content


class TestIntegration:
    """Integration tests for full handoff workflow."""

    def test_full_handoff_workflow(self, tmp_path):
        """TEST-005: End-to-end test of /handoff command with real project data."""
        # Setup complete feature directory
        feature_dir = tmp_path / "coderef" / "working" / "integration-test"
        feature_dir.mkdir(parents=True)

        # Create plan.json
        plan_data = {
            "META_DOCUMENTATION": {"workorder_id": "WO-INTEGRATION-001"},
            "UNIVERSAL_PLANNING_STRUCTURE": {
                "1_executive_summary": {"description": "Integration test feature"},
                "9_implementation_checklist": {
                    "phase_1": ["☑ TASK-001: Done", "☐ TASK-002: Pending"]
                }
            }
        }
        (feature_dir / "plan.json").write_text(json.dumps(plan_data), encoding="utf-8")

        # Create analysis.json
        analysis_data = {
            "technology_stack": {"language": "Python", "framework": "Flask"}
        }
        (feature_dir / "analysis.json").write_text(json.dumps(analysis_data), encoding="utf-8")

        # Generate handoff
        generator = HandoffGenerator(tmp_path)

        with patch.object(generator, '_parse_git_history', return_value={
            "recent_commits": ["abc123 Test commit"],
            "uncommitted_changes": [],
            "commit_count": 1
        }):
            result = generator.generate_handoff_context("integration-test", "full")

        # Verify result
        assert result["success"] is True
        assert result["data_sources"]["plan_json"] is True
        assert result["data_sources"]["analysis_json"] is True
        assert result["data_sources"]["git_history"] is True
        assert result["auto_populated_fields"] == 100

        # Verify file created
        claude_md = feature_dir / "claude.md"
        assert claude_md.exists()
        content = claude_md.read_text(encoding="utf-8")
        assert "WO-INTEGRATION-001" in content
        assert "Integration test feature" in content


class TestErrorHandling:
    """Test error handling and graceful degradation."""

    def test_error_handling_missing_all_data(self, tmp_path):
        """TEST-006: Verify graceful degradation with no data sources."""
        feature_dir = tmp_path / "coderef" / "working" / "empty-feature"
        feature_dir.mkdir(parents=True)

        # Create minimal plan.json (required file)
        plan_data = {
            "META_DOCUMENTATION": {"workorder_id": "WO-EMPTY-001"},
            "UNIVERSAL_PLANNING_STRUCTURE": {
                "1_executive_summary": {"description": "Empty test"},
                "9_implementation_checklist": {}
            }
        }
        (feature_dir / "plan.json").write_text(json.dumps(plan_data), encoding="utf-8")

        generator = HandoffGenerator(tmp_path)

        with patch.object(generator, '_parse_git_history', return_value=None):
            result = generator.generate_handoff_context("empty-feature", "full")

        # Should succeed with graceful degradation
        assert result["success"] is True
        assert result["auto_populated_fields"] == 33  # Only plan.json available (1/3 sources)

    def test_invalid_feature_name(self, tmp_path):
        """TEST-006: Verify validation of feature name."""
        generator = HandoffGenerator(tmp_path)

        with pytest.raises(ValueError, match="Invalid feature name"):
            generator.generate_handoff_context("../../../etc/passwd", "full")

    def test_invalid_mode(self, tmp_path):
        """TEST-006: Verify mode parameter validation."""
        feature_dir = tmp_path / "coderef" / "working" / "test"
        feature_dir.mkdir(parents=True)

        generator = HandoffGenerator(tmp_path)

        with pytest.raises(ValueError, match="Invalid mode"):
            generator.generate_handoff_context("test", "invalid_mode")


@pytest.fixture
def tmp_path(tmp_path_factory):
    """Create temporary directory for tests."""
    return tmp_path_factory.mktemp("test_handoff")
