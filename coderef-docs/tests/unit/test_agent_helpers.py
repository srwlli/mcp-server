"""
Unit tests for agent communication helper functions (Phase 0).

Tests the 4 core helper functions:
- generate_agent_workorder_id()
- validate_forbidden_files()
- aggregate_agent_metrics()
- parse_agent_status()
"""

import pytest
from pathlib import Path
import json
import tempfile
import subprocess
from handler_helpers import (
    generate_agent_workorder_id,
    validate_forbidden_files,
    aggregate_agent_metrics,
    parse_agent_status
)


class TestGenerateAgentWorkorderId:
    """Test generate_agent_workorder_id() helper function."""

    def test_basic_workorder_generation(self):
        """Test basic workorder ID generation."""
        result = generate_agent_workorder_id('WO-AUTH-SYSTEM-001', 2)
        assert result == 'WO-AUTH-SYSTEM-002'

    def test_multiple_agents(self):
        """Test generating IDs for multiple agents."""
        base = 'WO-FEATURE-001'
        assert generate_agent_workorder_id(base, 2) == 'WO-FEATURE-002'
        assert generate_agent_workorder_id(base, 3) == 'WO-FEATURE-003'
        assert generate_agent_workorder_id(base, 10) == 'WO-FEATURE-010'

    def test_hyphenated_feature_names(self):
        """Test with feature names containing multiple hyphens."""
        result = generate_agent_workorder_id('WO-DELIVERABLES-GENERATOR-001', 2)
        assert result == 'WO-DELIVERABLES-GENERATOR-002'

    def test_invalid_workorder_format(self):
        """Test error handling for invalid workorder ID format."""
        with pytest.raises(ValueError, match="Invalid workorder ID format"):
            generate_agent_workorder_id('INVALID', 2)

    def test_invalid_agent_number(self):
        """Test error handling for invalid agent number."""
        with pytest.raises(ValueError, match="Agent number must be >= 1"):
            generate_agent_workorder_id('WO-FEATURE-001', 0)

        with pytest.raises(ValueError, match="Agent number must be >= 1"):
            generate_agent_workorder_id('WO-FEATURE-001', -1)

    def test_zero_padding(self):
        """Test that agent numbers are zero-padded to 3 digits."""
        assert generate_agent_workorder_id('WO-TEST-001', 1) == 'WO-TEST-001'
        assert generate_agent_workorder_id('WO-TEST-001', 99) == 'WO-TEST-099'
        assert generate_agent_workorder_id('WO-TEST-001', 100) == 'WO-TEST-100'


class TestValidateForbiddenFiles:
    """Test validate_forbidden_files() helper function."""

    @pytest.fixture
    def git_repo(self, tmp_path):
        """Create a temporary git repository for testing."""
        repo_path = tmp_path / "test_repo"
        repo_path.mkdir()

        # Initialize git repo
        subprocess.run(['git', 'init'], cwd=str(repo_path), capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=str(repo_path))
        subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=str(repo_path))

        # Create test files
        (repo_path / "file1.txt").write_text("original content")
        (repo_path / "file2.txt").write_text("original content")

        # Initial commit
        subprocess.run(['git', 'add', '.'], cwd=str(repo_path))
        subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=str(repo_path))

        return repo_path

    def test_no_modifications(self, git_repo):
        """Test when forbidden files are unchanged."""
        result = validate_forbidden_files(git_repo, ['file1.txt', 'file2.txt'])
        assert result['passed'] is True
        assert len(result['violations']) == 0
        assert 'file1.txt' in result['checked']
        assert 'file2.txt' in result['checked']

    def test_forbidden_file_comments_stripped(self, git_repo):
        """Test that comments in forbidden file paths are stripped."""
        result = validate_forbidden_files(
            git_repo,
            ['file1.txt - DO NOT MODIFY (production)', 'file2.txt - DO NOT MODIFY']
        )
        assert result['passed'] is True
        assert 'file1.txt' in result['checked']
        assert 'file2.txt' in result['checked']

    def test_modified_file_detected(self, git_repo):
        """Test detection of modified forbidden file."""
        # Modify file1.txt
        (git_repo / "file1.txt").write_text("modified content")

        result = validate_forbidden_files(git_repo, ['file1.txt', 'file2.txt'])
        assert result['passed'] is False
        assert len(result['violations']) == 1
        assert result['violations'][0]['file'] == 'file1.txt'
        assert result['violations'][0]['status'] == 'modified'

    def test_staged_changes_detected(self, git_repo):
        """Test detection of staged changes to forbidden files."""
        # Modify and stage file1.txt
        (git_repo / "file1.txt").write_text("staged content")
        subprocess.run(['git', 'add', 'file1.txt'], cwd=str(git_repo))

        result = validate_forbidden_files(git_repo, ['file1.txt'])
        assert result['passed'] is False
        assert len(result['violations']) == 1
        assert result['violations'][0]['file'] == 'file1.txt'
        assert result['violations'][0]['status'] in ['modified', 'staged']

    def test_not_a_git_repo(self, tmp_path):
        """Test error handling when path is not a git repository."""
        with pytest.raises(ValueError, match="Not a git repository"):
            validate_forbidden_files(tmp_path, ['file1.txt'])


class TestAggregateAgentMetrics:
    """Test aggregate_agent_metrics() helper function."""

    @pytest.fixture
    def deliverables_files(self, tmp_path):
        """Create test DELIVERABLES.md files."""
        paths = []

        # Agent 1 deliverables
        agent1 = tmp_path / "agent1_DELIVERABLES.md"
        agent1.write_text("""
# DELIVERABLES - Agent 1

## Implementation Metrics

### Code Changes
- **Lines Added**: 300
- **Lines Deleted**: 50
- **Net LOC**: 250

### Development Activity
- **Total Commits**: 5
- **Contributors**: Alice, Bob
- **first_commit**: 2025-10-15
- **last_commit**: 2025-10-17
""")
        paths.append(agent1)

        # Agent 2 deliverables
        agent2 = tmp_path / "agent2_DELIVERABLES.md"
        agent2.write_text("""
# DELIVERABLES - Agent 2

## Implementation Metrics

### Code Changes
- **Lines Added**: 150
- **Lines Deleted**: 70
- **Net LOC**: 80

### Development Activity
- **Total Commits**: 3
- **Contributors**: Bob, Charlie
- **first_commit**: 2025-10-16
- **last_commit**: 2025-10-18
""")
        paths.append(agent2)

        return paths

    def test_aggregate_two_agents(self, deliverables_files):
        """Test aggregating metrics from two agents."""
        result = aggregate_agent_metrics(deliverables_files)

        assert result['loc_added'] == 450  # 300 + 150
        assert result['loc_deleted'] == 120  # 50 + 70
        assert result['loc_net'] == 330  # 250 + 80
        assert result['total_commits'] == 8  # 5 + 3
        assert set(result['contributors']) == {'Alice', 'Bob', 'Charlie'}
        assert result['agents_count'] == 2

    def test_date_range_calculation(self, deliverables_files):
        """Test time elapsed calculation across agents."""
        result = aggregate_agent_metrics(deliverables_files)

        # First commit: 2025-10-15, Last commit: 2025-10-18
        assert result['days_elapsed'] == 3
        assert result['hours_elapsed'] == 72

    def test_empty_deliverables_list(self):
        """Test with no deliverables files."""
        result = aggregate_agent_metrics([])

        assert result['loc_added'] == 0
        assert result['total_commits'] == 0
        assert result['contributors'] == []
        assert result['agents_count'] == 0

    def test_nonexistent_files_skipped(self, tmp_path):
        """Test that nonexistent files are skipped gracefully."""
        fake_path = tmp_path / "nonexistent.md"
        result = aggregate_agent_metrics([fake_path])

        assert result['loc_added'] == 0
        assert result['total_commits'] == 0


class TestParseAgentStatus:
    """Test parse_agent_status() helper function."""

    @pytest.fixture
    def communication_file(self, tmp_path):
        """Create a test communication.json file."""
        comm_file = tmp_path / "communication.json"
        data = {
            "feature": "AUTH_SYSTEM",
            "workorder_id": "WO-AUTH-SYSTEM-001",
            "from": "Agent 1",
            "to": "Agent 2",
            "agent_1_status": "READY - Planning complete",
            "agent_2_status": "IN_PROGRESS",
            "agent_3_status": "COMPLETE",
            "agent_2_completion": {
                "timestamp": "2025-10-18T15:30:00Z",
                "verification": {
                    "forbidden_files_unchanged": True,
                    "tests_passing": True
                }
            }
        }
        comm_file.write_text(json.dumps(data, indent=2))
        return comm_file

    def test_parse_basic_status(self, communication_file):
        """Test parsing basic agent status information."""
        result = parse_agent_status(communication_file)

        assert result['feature'] == 'AUTH_SYSTEM'
        assert result['workorder_id'] == 'WO-AUTH-SYSTEM-001'
        assert len(result['agents']) == 3

    def test_agent_status_detection(self, communication_file):
        """Test correct detection of agent statuses."""
        result = parse_agent_status(communication_file)

        agent_statuses = {a['agent_number']: a['status'] for a in result['agents']}
        assert 'READY' in agent_statuses['1']
        assert agent_statuses['2'] == 'IN_PROGRESS'
        assert agent_statuses['3'] == 'COMPLETE'

    def test_overall_status_in_progress(self, communication_file):
        """Test overall status calculation when work is in progress."""
        result = parse_agent_status(communication_file)
        assert result['overall_status'] == 'IN_PROGRESS'

    def test_overall_status_ready(self, tmp_path):
        """Test overall status when all agents are unassigned."""
        comm_file = tmp_path / "communication.json"
        data = {
            "feature": "TEST",
            "workorder_id": "WO-TEST-001",
            "agent_1_status": "READY",
            "agent_2_status": None
        }
        comm_file.write_text(json.dumps(data))

        result = parse_agent_status(comm_file)
        assert result['overall_status'] == 'READY'

    def test_blocker_detection(self, tmp_path):
        """Test detection of blockers in agent work."""
        comm_file = tmp_path / "communication.json"
        data = {
            "feature": "TEST",
            "workorder_id": "WO-TEST-001",
            "agent_2_status": "COMPLETE",
            "agent_2_completion": {
                "verification": {
                    "forbidden_files_unchanged": False,
                    "tests_passing": False
                }
            }
        }
        comm_file.write_text(json.dumps(data))

        result = parse_agent_status(comm_file)
        agent_2 = result['agents'][0]
        assert 'FORBIDDEN_FILES_MODIFIED' in agent_2['blockers']
        assert 'TESTS_FAILING' in agent_2['blockers']

    def test_file_not_found(self, tmp_path):
        """Test error handling when communication file doesn't exist."""
        fake_path = tmp_path / "nonexistent.json"
        with pytest.raises(FileNotFoundError):
            parse_agent_status(fake_path)

    def test_invalid_json(self, tmp_path):
        """Test error handling for malformed JSON."""
        comm_file = tmp_path / "bad.json"
        comm_file.write_text("{invalid json")

        with pytest.raises(ValueError, match="Invalid JSON"):
            parse_agent_status(comm_file)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
