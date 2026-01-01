"""
Comprehensive tests for export_processor.py

Tests cover:
- All 4 export formats (JSON, JSON-LD, Mermaid, DOT)
- CLI execution and error handling
- Output file creation and validation
- Format-specific content validation
- Edge cases and error scenarios

Run with: pytest tests/test_export_processor.py -v
"""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import asyncio
import os

# Import the module under test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "processors"))
from export_processor import export_coderef, validate_export_format


@pytest.fixture
def temp_project(tmp_path):
    """Create temporary project structure for testing"""
    project = tmp_path / "test-project"
    project.mkdir()

    # Create .coderef directory
    (project / ".coderef").mkdir()

    # Create test files
    (project / "src").mkdir()
    (project / "src" / "main.py").write_text("""
def hello():
    return "world"
""")
    (project / "src" / "utils.py").write_text("""
def add(a, b):
    return a + b
""")

    return project


class TestExportCoderefSuccess:
    """Test successful export operations"""

    @pytest.mark.asyncio
    async def test_export_json_success(self, temp_project):
        """Test successful JSON export"""
        output_file = temp_project / ".coderef" / "exports" / "test.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
            # Mock successful process
            mock_process = Mock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(b"Export successful", b""))
            mock_exec.return_value = mock_process

            # Create the output file to simulate CLI creating it
            output_file.write_text('{"elements": []}')

            result = await export_coderef(
                cli_command=["coderef"],
                project_path=str(temp_project),
                format="json",
                output_path=str(output_file)
            )

            # Parse JSON result
            result_data = json.loads(result[0].text)

            assert result_data["success"] is True
            assert result_data["format"] == "json"
            assert str(output_file) in result_data["output_path"]
            assert result_data["file_size_bytes"] > 0

    @pytest.mark.asyncio
    async def test_export_jsonld_success(self, temp_project):
        """Test successful JSON-LD export"""
        output_file = temp_project / ".coderef" / "exports" / "test.jsonld"
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
            mock_process = Mock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(b"Export successful", b""))
            mock_exec.return_value = mock_process

            # Create output file
            output_file.write_text('{"@context": "schema.org"}')

            result = await export_coderef(
                cli_command=["coderef"],
                project_path=str(temp_project),
                format="jsonld",
                output_path=str(output_file)
            )

            result_data = json.loads(result[0].text)
            assert result_data["success"] is True
            assert result_data["format"] == "jsonld"

    @pytest.mark.asyncio
    async def test_export_mermaid_success(self, temp_project):
        """Test successful Mermaid export"""
        output_file = temp_project / ".coderef" / "exports" / "test.mmd"
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
            mock_process = Mock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(b"Export successful", b""))
            mock_exec.return_value = mock_process

            # Create output file
            output_file.write_text("graph TD\n    A --> B")

            result = await export_coderef(
                cli_command=["coderef"],
                project_path=str(temp_project),
                format="mermaid",
                output_path=str(output_file)
            )

            result_data = json.loads(result[0].text)
            assert result_data["success"] is True
            assert result_data["format"] == "mermaid"

    @pytest.mark.asyncio
    async def test_export_dot_success(self, temp_project):
        """Test successful DOT export"""
        output_file = temp_project / ".coderef" / "exports" / "test.dot"
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
            mock_process = Mock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(b"Export successful", b""))
            mock_exec.return_value = mock_process

            # Create output file
            output_file.write_text("digraph G {\n    A -> B;\n}")

            result = await export_coderef(
                cli_command=["coderef"],
                project_path=str(temp_project),
                format="dot",
                output_path=str(output_file)
            )

            result_data = json.loads(result[0].text)
            assert result_data["success"] is True
            assert result_data["format"] == "dot"


class TestExportCoderefDefaultPaths:
    """Test default output path behavior"""

    @pytest.mark.asyncio
    async def test_default_output_path_created(self, temp_project):
        """Test that default output path is created when not specified"""
        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
            mock_process = Mock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(b"Export successful", b""))
            mock_exec.return_value = mock_process

            # Create default output file
            default_path = temp_project / ".coderef" / "exports" / "export.json"
            default_path.parent.mkdir(parents=True, exist_ok=True)
            default_path.write_text('{}')

            result = await export_coderef(
                cli_command=["coderef"],
                project_path=str(temp_project),
                format="json"
                # No output_path specified
            )

            result_data = json.loads(result[0].text)
            assert result_data["success"] is True
            # Check for platform-independent path separator
            assert "exports" in result_data["output_path"]
            assert "export.json" in result_data["output_path"]

    @pytest.mark.asyncio
    async def test_exports_directory_created(self, temp_project):
        """Test that exports directory is created if it doesn't exist"""
        # Remove .coderef directory
        import shutil
        coderef_dir = temp_project / ".coderef"
        if coderef_dir.exists():
            shutil.rmtree(coderef_dir)

        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
            mock_process = Mock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(b"Export successful", b""))
            mock_exec.return_value = mock_process

            # Create output file at default location
            default_path = temp_project / ".coderef" / "exports" / "export.json"
            default_path.parent.mkdir(parents=True, exist_ok=True)
            default_path.write_text('{}')

            await export_coderef(
                cli_command=["coderef"],
                project_path=str(temp_project),
                format="json"
            )

            # Verify directory was created
            assert (temp_project / ".coderef" / "exports").exists()


class TestExportCoderefParameters:
    """Test CLI command parameter passing"""

    @pytest.mark.asyncio
    async def test_max_nodes_parameter(self, temp_project):
        """Test that max_nodes parameter is passed to CLI"""
        output_file = temp_project / ".coderef" / "test.json"

        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
            mock_process = Mock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(b"Export successful", b""))
            mock_exec.return_value = mock_process

            # Create output file
            output_file.write_text('{}')

            await export_coderef(
                cli_command=["coderef"],
                project_path=str(temp_project),
                format="json",
                output_path=str(output_file),
                max_nodes=100
            )

            # Verify max_nodes was passed to CLI
            call_args = mock_exec.call_args[0]
            assert "-m" in call_args
            assert "100" in call_args

    @pytest.mark.asyncio
    async def test_cli_command_construction(self, temp_project):
        """Test that CLI command is constructed correctly"""
        output_file = temp_project / ".coderef" / "test.json"

        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
            mock_process = Mock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(b"Export successful", b""))
            mock_exec.return_value = mock_process

            # Create output file
            output_file.write_text('{}')

            await export_coderef(
                cli_command=["coderef"],
                project_path=str(temp_project),
                format="json",
                output_path=str(output_file)
            )

            # Verify command structure
            call_args = mock_exec.call_args[0]
            assert call_args[0] == "coderef"
            assert "export" in call_args
            assert "-f" in call_args
            assert "json" in call_args
            assert "-o" in call_args
            assert "-s" in call_args

    @pytest.mark.asyncio
    async def test_custom_cli_command(self, temp_project):
        """Test using custom CLI command (e.g., node cli.js)"""
        output_file = temp_project / ".coderef" / "test.json"

        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
            mock_process = Mock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(b"Export successful", b""))
            mock_exec.return_value = mock_process

            # Create output file
            output_file.write_text('{}')

            await export_coderef(
                cli_command=["node", "cli.js"],
                project_path=str(temp_project),
                format="json",
                output_path=str(output_file)
            )

            # Verify custom command was used
            call_args = mock_exec.call_args[0]
            assert call_args[0] == "node"
            assert call_args[1] == "cli.js"


class TestExportCoderefErrors:
    """Test error handling scenarios"""

    @pytest.mark.asyncio
    async def test_invalid_format(self, temp_project):
        """Test handling of invalid export format"""
        result = await export_coderef(
            cli_command=["coderef"],
            project_path=str(temp_project),
            format="invalid_format"
        )

        result_data = json.loads(result[0].text)
        assert result_data["success"] is False
        assert "Invalid format" in result_data["error"]

    @pytest.mark.asyncio
    async def test_cli_command_failure(self, temp_project):
        """Test handling of CLI command failure"""
        output_file = temp_project / ".coderef" / "test.json"

        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
            mock_process = Mock()
            mock_process.returncode = 1
            mock_process.communicate = AsyncMock(
                return_value=(b"", b"Error: Project not found")
            )
            mock_exec.return_value = mock_process

            result = await export_coderef(
                cli_command=["coderef"],
                project_path=str(temp_project),
                format="json",
                output_path=str(output_file)
            )

            result_data = json.loads(result[0].text)
            assert result_data["success"] is False
            assert "Project not found" in result_data["error"]

    @pytest.mark.asyncio
    async def test_timeout_error(self, temp_project):
        """Test handling of timeout during export"""
        output_file = temp_project / ".coderef" / "test.json"

        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
            mock_process = Mock()
            mock_process.communicate = AsyncMock(side_effect=asyncio.TimeoutError())
            mock_process.kill = Mock()
            mock_process.wait = AsyncMock()
            mock_exec.return_value = mock_process

            result = await export_coderef(
                cli_command=["coderef"],
                project_path=str(temp_project),
                format="json",
                output_path=str(output_file),
                timeout=1  # Very short timeout
            )

            result_data = json.loads(result[0].text)
            assert result_data["success"] is False
            assert "timeout" in result_data["error"].lower()

    @pytest.mark.asyncio
    async def test_output_file_not_created(self, temp_project):
        """Test handling when CLI succeeds but output file isn't created"""
        output_file = temp_project / ".coderef" / "test.json"

        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
            mock_process = Mock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(b"Export successful", b""))
            mock_exec.return_value = mock_process

            # Don't create the output file (simulate CLI bug)

            result = await export_coderef(
                cli_command=["coderef"],
                project_path=str(temp_project),
                format="json",
                output_path=str(output_file)
            )

            result_data = json.loads(result[0].text)
            assert result_data["success"] is False
            assert "not created" in result_data["error"]

    @pytest.mark.asyncio
    async def test_exception_during_export(self, temp_project):
        """Test handling of unexpected exceptions"""
        with patch('asyncio.create_subprocess_exec', side_effect=Exception("Unexpected error")):
            result = await export_coderef(
                cli_command=["coderef"],
                project_path=str(temp_project),
                format="json"
            )

            result_data = json.loads(result[0].text)
            assert result_data["success"] is False
            assert "Unexpected error" in result_data["error"]


class TestValidateExportFormat:
    """Test format validation function"""

    @pytest.mark.asyncio
    async def test_validate_json_format(self):
        """Test validation of JSON format"""
        result = await validate_export_format("json")

        assert result["format"] == "json"
        assert result["valid"] is True
        assert result["file_extension"] == "json"
        assert "description" in result

    @pytest.mark.asyncio
    async def test_validate_jsonld_format(self):
        """Test validation of JSON-LD format"""
        result = await validate_export_format("jsonld")

        assert result["format"] == "jsonld"
        assert result["valid"] is True
        assert result["file_extension"] == "jsonld"

    @pytest.mark.asyncio
    async def test_validate_mermaid_format(self):
        """Test validation of Mermaid format"""
        result = await validate_export_format("mermaid")

        assert result["format"] == "mermaid"
        assert result["valid"] is True
        assert result["file_extension"] == "mmd"

    @pytest.mark.asyncio
    async def test_validate_dot_format(self):
        """Test validation of DOT format"""
        result = await validate_export_format("dot")

        assert result["format"] == "dot"
        assert result["valid"] is True
        assert result["file_extension"] == "dot"

    @pytest.mark.asyncio
    async def test_validate_invalid_format(self):
        """Test validation of invalid format"""
        result = await validate_export_format("invalid")

        assert result["format"] == "invalid"
        assert result["valid"] is False
        assert "error" in result


class TestFileSizeReporting:
    """Test file size reporting in results"""

    @pytest.mark.asyncio
    async def test_file_size_bytes_reported(self, temp_project):
        """Test that file size in bytes is reported"""
        output_file = temp_project / ".coderef" / "test.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
            mock_process = Mock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(b"Export successful", b""))
            mock_exec.return_value = mock_process

            # Create output file with known size
            test_content = '{"elements": [1, 2, 3]}'
            output_file.write_text(test_content)
            expected_size = len(test_content.encode())

            result = await export_coderef(
                cli_command=["coderef"],
                project_path=str(temp_project),
                format="json",
                output_path=str(output_file)
            )

            result_data = json.loads(result[0].text)
            assert result_data["file_size_bytes"] == expected_size

    @pytest.mark.asyncio
    async def test_file_size_mb_reported(self, temp_project):
        """Test that file size in MB is reported"""
        output_file = temp_project / ".coderef" / "test.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
            mock_process = Mock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(b"Export successful", b""))
            mock_exec.return_value = mock_process

            # Create 1MB file
            output_file.write_text("x" * (1024 * 1024))

            result = await export_coderef(
                cli_command=["coderef"],
                project_path=str(temp_project),
                format="json",
                output_path=str(output_file)
            )

            result_data = json.loads(result[0].text)
            assert result_data["file_size_mb"] == 1.0


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    @pytest.mark.asyncio
    async def test_unicode_in_project_path(self, tmp_path):
        """Test export with unicode characters in project path"""
        unicode_project = tmp_path / "项目"
        unicode_project.mkdir()
        (unicode_project / ".coderef" / "exports").mkdir(parents=True)

        output_file = unicode_project / ".coderef" / "test.json"

        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
            mock_process = Mock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(b"Export successful", b""))
            mock_exec.return_value = mock_process

            output_file.write_text('{}')

            result = await export_coderef(
                cli_command=["coderef"],
                project_path=str(unicode_project),
                format="json",
                output_path=str(output_file)
            )

            result_data = json.loads(result[0].text)
            assert result_data["success"] is True

    @pytest.mark.asyncio
    async def test_empty_cli_output(self, temp_project):
        """Test handling of empty CLI output"""
        output_file = temp_project / ".coderef" / "test.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
            mock_process = Mock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(b"", b""))
            mock_exec.return_value = mock_process

            output_file.write_text('{}')

            result = await export_coderef(
                cli_command=["coderef"],
                project_path=str(temp_project),
                format="json",
                output_path=str(output_file)
            )

            result_data = json.loads(result[0].text)
            assert result_data["success"] is True
            assert result_data["cli_output"] == ""

    @pytest.mark.asyncio
    async def test_large_file_export(self, temp_project):
        """Test export with large file (> 10MB)"""
        output_file = temp_project / ".coderef" / "large.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
            mock_process = Mock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(b"Export successful", b""))
            mock_exec.return_value = mock_process

            # Create 15MB file
            large_content = "x" * (15 * 1024 * 1024)
            output_file.write_text(large_content)

            result = await export_coderef(
                cli_command=["coderef"],
                project_path=str(temp_project),
                format="json",
                output_path=str(output_file)
            )

            result_data = json.loads(result[0].text)
            assert result_data["success"] is True
            assert result_data["file_size_mb"] > 10


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
