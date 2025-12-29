"""
Unit tests for cli_utils.py - CLI path resolution and command execution.

Tests the multi-tier CLI path resolution system:
1. CODEREF_CLI_PATH environment variable
2. Global 'coderef' in PATH
3. Hardcoded fallback

Part of WO-ENV-VAR-CLI-PATH-001.
"""

import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the module to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
import cli_utils


class TestGetCliPath:
    """Test suite for get_cli_path() function."""

    def test_env_var_override_takes_priority(self, tmp_path):
        """Test that CODEREF_CLI_PATH environment variable takes priority."""
        # Create a temporary CLI file
        cli_file = tmp_path / "custom_cli.js"
        cli_file.write_text("// mock CLI")

        with patch.dict(os.environ, {"CODEREF_CLI_PATH": str(cli_file)}):
            result = cli_utils.get_cli_path()
            assert result == str(cli_file.absolute())

    def test_env_var_invalid_file_falls_back(self, tmp_path):
        """Test that invalid CODEREF_CLI_PATH falls back to next option."""
        invalid_path = tmp_path / "nonexistent.js"

        with patch.dict(os.environ, {"CODEREF_CLI_PATH": str(invalid_path)}):
            # Mock shutil.which to return None (no global install)
            with patch("shutil.which", return_value=None):
                # Mock the hardcoded path to exist
                with patch("pathlib.Path.exists", return_value=True):
                    result = cli_utils.get_cli_path()
                    # Should use hardcoded path
                    assert result == cli_utils.DEFAULT_CLI_PATH

    def test_global_install_detected(self):
        """Test that global 'coderef' command is detected from PATH."""
        global_cli_path = "/usr/local/bin/coderef"

        # Mock environment (no CODEREF_CLI_PATH)
        with patch.dict(os.environ, {}, clear=True):
            # Mock shutil.which to find global install
            with patch("shutil.which", return_value=global_cli_path):
                result = cli_utils.get_cli_path()
                assert result == global_cli_path

    def test_hardcoded_fallback_with_warning(self):
        """Test that hardcoded path is used as last resort with deprecation warning."""
        # Mock environment (no CODEREF_CLI_PATH)
        with patch.dict(os.environ, {}, clear=True):
            # Mock shutil.which to return None (no global install)
            with patch("shutil.which", return_value=None):
                # Mock the hardcoded path to exist
                with patch("pathlib.Path.exists", return_value=True):
                    # Mock logger to capture warning
                    with patch("cli_utils.logger") as mock_logger:
                        result = cli_utils.get_cli_path()

                        # Should use hardcoded path
                        assert result == cli_utils.DEFAULT_CLI_PATH

                        # Should have logged a warning
                        mock_logger.warning.assert_called_once()
                        warning_message = mock_logger.warning.call_args[0][0]
                        assert "deprecated" in warning_message.lower()
                        assert "CODEREF_CLI_PATH" in warning_message

    def test_cli_not_found_raises_error(self):
        """Test that FileNotFoundError is raised when CLI not found anywhere."""
        # Mock environment (no CODEREF_CLI_PATH)
        with patch.dict(os.environ, {}, clear=True):
            # Mock shutil.which to return None (no global install)
            with patch("shutil.which", return_value=None):
                # Mock hardcoded path to not exist
                with patch("pathlib.Path.exists", return_value=False):
                    with pytest.raises(FileNotFoundError) as exc_info:
                        cli_utils.get_cli_path()

                    # Check error message
                    error_message = str(exc_info.value)
                    assert "Could not find @coderef/core CLI" in error_message
                    assert "CODEREF_CLI_PATH" in error_message
                    assert "npm install -g @coderef/cli" in error_message

    def test_env_var_directory_rejected(self, tmp_path):
        """Test that CODEREF_CLI_PATH pointing to directory is rejected."""
        # Create a directory instead of a file
        cli_dir = tmp_path / "cli_directory"
        cli_dir.mkdir()

        with patch.dict(os.environ, {"CODEREF_CLI_PATH": str(cli_dir)}):
            # Mock shutil.which to return None
            with patch("shutil.which", return_value=None):
                # Mock hardcoded path to exist
                with patch("pathlib.Path.exists", return_value=True):
                    with patch("cli_utils.logger") as mock_logger:
                        result = cli_utils.get_cli_path()

                        # Should warn about invalid path
                        mock_logger.warning.assert_called()
                        warning_calls = [call[0][0] for call in mock_logger.warning.call_args_list]
                        assert any("invalid" in msg.lower() for msg in warning_calls)

                        # Should fall back to hardcoded path
                        assert result == cli_utils.DEFAULT_CLI_PATH


class TestValidateCliAvailable:
    """Test suite for validate_cli_available() function."""

    def test_cli_available_returns_true(self):
        """Test that validate_cli_available returns True when CLI is found."""
        # Mock get_cli_path to return a valid path
        with patch("cli_utils.get_cli_path", return_value="/path/to/cli.js"):
            # Mock file operations
            with patch("pathlib.Path.exists", return_value=True):
                with patch("pathlib.Path.is_file", return_value=True):
                    with patch("builtins.open", MagicMock()):
                        result = cli_utils.validate_cli_available()
                        assert result is True

    def test_cli_not_available_returns_false(self):
        """Test that validate_cli_available returns False when CLI not found."""
        # Mock get_cli_path to raise FileNotFoundError
        with patch("cli_utils.get_cli_path", side_effect=FileNotFoundError("CLI not found")):
            with patch("cli_utils.logger"):
                result = cli_utils.validate_cli_available()
                # Should return False instead of raising
                assert result is False


class TestRunCoderefCommand:
    """Test suite for run_coderef_command() function."""

    def test_successful_command_execution(self):
        """Test successful CLI command execution with JSON output."""
        mock_output = '{"elements": [{"name": "test"}]}'

        # Mock get_cli_path
        with patch("cli_utils.get_cli_path", return_value="/path/to/cli.js"):
            # Mock subprocess.run
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = mock_output
            mock_result.stderr = ""

            with patch("subprocess.run", return_value=mock_result):
                result = cli_utils.run_coderef_command("scan", ["--project", "/test"])

                # Should parse JSON correctly
                assert isinstance(result, dict)
                assert "elements" in result
                assert result["elements"][0]["name"] == "test"

    def test_empty_output_returns_error(self):
        """Test that empty CLI output returns error dict."""
        # Mock get_cli_path
        with patch("cli_utils.get_cli_path", return_value="/path/to/cli.js"):
            # Mock subprocess.run with empty output
            mock_result = MagicMock()
            mock_result.stdout = ""
            mock_result.stderr = ""

            with patch("subprocess.run", return_value=mock_result):
                with patch("cli_utils.logger"):
                    result = cli_utils.run_coderef_command("scan")

                    # Should return error dict
                    assert "error" in result
                    assert "Empty output" in result["error"]

    def test_invalid_json_returns_error(self):
        """Test that invalid JSON output returns error dict."""
        # Mock get_cli_path
        with patch("cli_utils.get_cli_path", return_value="/path/to/cli.js"):
            # Mock subprocess.run with invalid JSON
            mock_result = MagicMock()
            mock_result.stdout = "not valid json"
            mock_result.stderr = ""

            with patch("subprocess.run", return_value=mock_result):
                with patch("cli_utils.logger"):
                    result = cli_utils.run_coderef_command("scan")

                    # Should return error dict
                    assert "error" in result
                    assert "Invalid JSON" in result["error"]

    def test_command_timeout(self):
        """Test that command timeout is handled gracefully."""
        import subprocess

        # Mock get_cli_path
        with patch("cli_utils.get_cli_path", return_value="/path/to/cli.js"):
            # Mock subprocess.run to raise TimeoutExpired
            with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("cmd", 120)):
                with patch("cli_utils.logger"):
                    result = cli_utils.run_coderef_command("scan", timeout=120)

                    # Should return error dict
                    assert "error" in result
                    assert "timed out" in result["error"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
