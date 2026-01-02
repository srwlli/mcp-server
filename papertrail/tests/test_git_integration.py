"""
Comprehensive unit tests for git_integration.py
Tests real git parsing logic with actual command output formats
"""
import pytest
import subprocess
from unittest.mock import patch, MagicMock
from pathlib import Path
from papertrail.extensions.git_integration import GitExtension


class TestGitExtensionInitialization:
    """Test initialization and setup"""

    def test_init_without_repo_path(self):
        ext = GitExtension()
        assert ext.repo_path is None

    def test_init_with_repo_path(self):
        ext = GitExtension(repo_path=Path("/test/repo"))
        assert ext.repo_path == Path("/test/repo")

    def test_init_with_string_repo_path(self):
        ext = GitExtension(repo_path="/test/repo")
        assert ext.repo_path == Path("/test/repo")


class TestRunGitCommand:
    """Test _run_git_command helper"""

    @patch('subprocess.run')
    def test_successful_command(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="test output"
        )
        ext = GitExtension()
        result = ext._run_git_command(['status'])
        assert result == "test output"
        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_command_failure_returns_none(self, mock_run):
        # With check=True, CalledProcessError is raised on non-zero returncode
        mock_run.side_effect = subprocess.CalledProcessError(1, ['git', 'invalid'])
        ext = GitExtension()
        result = ext._run_git_command(['invalid'])
        assert result is None

    @patch('subprocess.run')
    def test_command_exception_returns_none(self, mock_run):
        # FileNotFoundError is caught (e.g., git not installed)
        mock_run.side_effect = FileNotFoundError("Git not found")
        ext = GitExtension()
        result = ext._run_git_command(['status'])
        assert result is None

    @patch('subprocess.run')
    def test_empty_output(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="")
        ext = GitExtension()
        result = ext._run_git_command(['status'])
        assert result == ""

    @patch('subprocess.run')
    def test_multiline_output(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="line1\nline2\nline3"
        )
        ext = GitExtension()
        result = ext._run_git_command(['log'])
        assert "line1" in result
        assert "line2" in result


class TestGetFilesChanged:
    """Test get_files_changed method"""

    @patch.object(GitExtension, '_run_git_command')
    def test_parses_modified_files(self, mock_git):
        mock_git.return_value = "M\tsrc/file.py\n10\t5\tsrc/file.py"
        ext = GitExtension()
        files = ext.get_files_changed("WO-TEST-001")

        assert len(files) == 1
        assert files[0]['path'] == 'src/file.py'
        assert files[0]['status'] == 'modified'
        assert files[0]['additions'] == 10
        assert files[0]['deletions'] == 5

    @patch.object(GitExtension, '_run_git_command')
    def test_parses_added_files(self, mock_git):
        mock_git.return_value = "A\tsrc/new.py\n20\t0\tsrc/new.py"
        ext = GitExtension()
        files = ext.get_files_changed("WO-TEST-001")

        assert len(files) == 1
        assert files[0]['status'] == 'added'
        assert files[0]['additions'] == 20
        assert files[0]['deletions'] == 0

    @patch.object(GitExtension, '_run_git_command')
    def test_parses_deleted_files(self, mock_git):
        mock_git.return_value = "D\tsrc/old.py\n0\t50\tsrc/old.py"
        ext = GitExtension()
        files = ext.get_files_changed("WO-TEST-001")

        assert len(files) == 1
        assert files[0]['status'] == 'deleted'
        assert files[0]['additions'] == 0
        assert files[0]['deletions'] == 50

    @patch.object(GitExtension, '_run_git_command')
    def test_parses_multiple_files(self, mock_git):
        mock_git.return_value = """M\tsrc/a.py
A\tsrc/b.py
D\tsrc/c.py
10\t5\tsrc/a.py
20\t0\tsrc/b.py
0\t30\tsrc/c.py"""
        ext = GitExtension()
        files = ext.get_files_changed("WO-TEST-001")

        assert len(files) == 3
        assert files[0]['path'] == 'src/a.py'
        assert files[1]['path'] == 'src/b.py'
        assert files[2]['path'] == 'src/c.py'

    @patch.object(GitExtension, '_run_git_command')
    def test_no_files_changed(self, mock_git):
        mock_git.return_value = ""
        ext = GitExtension()
        files = ext.get_files_changed("WO-TEST-001")
        assert files == []

    @patch.object(GitExtension, '_run_git_command')
    def test_git_command_fails(self, mock_git):
        mock_git.return_value = None
        ext = GitExtension()
        files = ext.get_files_changed("WO-TEST-001")
        assert files == []

    @patch.object(GitExtension, '_run_git_command')
    def test_malformed_output_graceful(self, mock_git):
        mock_git.return_value = "invalid output"
        ext = GitExtension()
        files = ext.get_files_changed("WO-TEST-001")
        # Should handle gracefully without crashing
        assert isinstance(files, list)


class TestGetCommits:
    """Test get_commits method"""

    @patch.object(GitExtension, '_run_git_command')
    def test_parses_single_commit(self, mock_git):
        # Format: hash\x00author\x00date\x00message (null-separated)
        mock_git.return_value = "abc123\x00John Doe\x002026-01-02T10:00:00Z\x00feat: add feature"
        ext = GitExtension()
        commits = ext.get_commits("WO-TEST-001")

        assert len(commits) == 1
        assert commits[0]['hash'] == 'abc123'
        assert commits[0]['author'] == 'John Doe'
        assert commits[0]['date'] == '2026-01-02T10:00:00Z'
        assert commits[0]['message'] == 'feat: add feature'

    @patch.object(GitExtension, '_run_git_command')
    def test_parses_multiple_commits(self, mock_git):
        mock_git.return_value = "abc123\x00John\x002026-01-02T10:00:00Z\x00feat: first\ndef456\x00Jane\x002026-01-02T11:00:00Z\x00fix: second"
        ext = GitExtension()
        commits = ext.get_commits("WO-TEST-001")

        assert len(commits) == 2
        assert commits[0]['hash'] == 'abc123'
        assert commits[1]['hash'] == 'def456'

    @patch.object(GitExtension, '_run_git_command')
    def test_no_commits(self, mock_git):
        mock_git.return_value = ""
        ext = GitExtension()
        commits = ext.get_commits("WO-TEST-001")
        assert commits == []

    @patch.object(GitExtension, '_run_git_command')
    def test_git_command_fails(self, mock_git):
        mock_git.return_value = None
        ext = GitExtension()
        commits = ext.get_commits("WO-TEST-001")
        assert commits == []


class TestStats:
    """Test stats aggregation method"""

    @patch.object(GitExtension, 'get_commits')
    @patch.object(GitExtension, 'get_files_changed')
    def test_aggregates_stats(self, mock_files, mock_commits):
        mock_commits.return_value = [
            {'hash': 'abc', 'author': 'John', 'date': '2026-01-02', 'message': 'msg1'},
            {'hash': 'def', 'author': 'Jane', 'date': '2026-01-02', 'message': 'msg2'}
        ]
        mock_files.return_value = [
            {'path': 'a.py', 'status': 'modified', 'additions': 10, 'deletions': 5},
            {'path': 'b.py', 'status': 'added', 'additions': 20, 'deletions': 0}
        ]

        ext = GitExtension()
        stats = ext.stats("WO-TEST-001")

        assert stats['workorder_id'] == 'WO-TEST-001'
        assert stats['commits'] == 2
        assert stats['total_additions'] == 30
        assert stats['total_deletions'] == 5
        assert stats['files_changed'] == 2

    @patch.object(GitExtension, 'get_commits')
    @patch.object(GitExtension, 'get_files_changed')
    def test_no_workorder_id(self, mock_files, mock_commits):
        mock_commits.return_value = []
        mock_files.return_value = []

        ext = GitExtension()
        stats = ext.stats()

        assert stats['workorder_id'] is None
        assert stats['commits'] == 0
        assert stats['total_additions'] == 0
        assert stats['total_deletions'] == 0


class TestOtherMethods:
    """Test additional methods (contributors, last_commit)"""

    @patch.object(GitExtension, '_run_git_command')
    def test_contributors(self, mock_git):
        mock_git.return_value = "John\nJane\nJohn\nBob"
        ext = GitExtension()
        contributors = ext.contributors()

        assert len(contributors) == 3
        assert 'John' in contributors
        assert 'Jane' in contributors
        assert 'Bob' in contributors
        assert contributors == sorted(contributors)  # Should be sorted

    @patch.object(GitExtension, '_run_git_command')
    def test_last_commit(self, mock_git):
        mock_git.return_value = "abc123\x00John\x002026-01-02T10:00:00Z\x00Last commit"
        ext = GitExtension()
        commit = ext.last_commit()

        assert commit['hash'] == 'abc123'
        assert commit['author'] == 'John'
        assert commit['message'] == 'Last commit'
