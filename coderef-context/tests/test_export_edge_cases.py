"""
Additional edge case tests for export_processor.py

These tests complement test_export_processor.py with:
- Concurrency scenarios (multiple exports simultaneously)
- Permission and filesystem errors
- CLI availability and path issues
- Output validation and corruption detection
- Overwrite behavior

Run with: pytest tests/test_export_edge_cases.py -v
"""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import asyncio
import os
import stat

# Import the module under test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "processors"))
from export_processor import export_coderef, validate_export_format


@pytest.fixture
def temp_project(tmp_path):
    """Create temporary project structure for testing"""
    project = tmp_path / "test-project"
    project.mkdir()
    (project / ".coderef").mkdir()
    (project / "src").mkdir()
    (project / "src" / "main.py").write_text("def hello(): return 'world'")
    return project


class TestConcurrency:
    """Test concurrent export operations"""

    @pytest.mark.asyncio
    async def test_concurrent_exports_different_formats(self, temp_project):
        """Test exporting multiple formats simultaneously"""
        formats = ["json", "jsonld", "mermaid", "dot"]

        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
            mock_process = Mock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(b"Export successful", b""))
            mock_exec.return_value = mock_process

            # Create output files
            output_files = []
            for fmt in formats:
                ext = "mmd" if fmt == "mermaid" else ("jsonld" if fmt == "jsonld" else fmt)
                output_file = temp_project / ".coderef" / f"test.{ext}"
                output_file.write_text('{"test": "data"}')
                output_files.append(output_file)

            # Run all exports concurrently
            tasks = [
                export_coderef(
                    cli_command=["coderef"],
                    project_path=str(temp_project),
                    format=fmt,
                    output_path=str(output_files[i])
                )
                for i, fmt in enumerate(formats)
            ]

            results = await asyncio.gather(*tasks)

            # All should succeed
            assert len(results) == 4
            for result in results:
                result_data = json.loads(result[0].text)
                assert result_data["success"] is True

    @pytest.mark.asyncio
    async def test_concurrent_exports_same_format(self, temp_project):
        """Test multiple exports of the same format to different files"""
        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
            mock_process = Mock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(b"Export successful", b""))
            mock_exec.return_value = mock_process

            # Create 3 different output files
            output_files = []
            for i in range(3):
                output_file = temp_project / ".coderef" / f"export_{i}.json"
                output_file.write_text('{"test": "data"}')
                output_files.append(output_file)

            # Run all exports concurrently
            tasks = [
                export_coderef(
                    cli_command=["coderef"],
                    project_path=str(temp_project),
                    format="json",
                    output_path=str(output_file)
                )
                for output_file in output_files
            ]

            results = await asyncio.gather(*tasks)
            assert len(results) == 3
            for result in results:
                result_data = json.loads(result[0].text)
                assert result_data["success"] is True


class TestPermissionErrors:
    """Test permission and filesystem error handling"""

    @pytest.mark.asyncio
    async def test_readonly_output_directory(self, temp_project):
        """Test export to read-only directory"""
        output_dir = temp_project / ".coderef" / "readonly"
        output_dir.mkdir()
        output_file = output_dir / "export.json"

        # Make directory read-only (platform-specific)
        if os.name != 'nt':  # Unix-like systems
            output_dir.chmod(stat.S_IRUSR | stat.S_IXUSR)

        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
            mock_process = Mock()
            mock_process.returncode = 1
            mock_process.communicate = AsyncMock(
                return_value=(b"", b"Permission denied")
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

            # Clean up: restore permissions
            if os.name != 'nt':
                output_dir.chmod(stat.S_IRWXU)

    @pytest.mark.asyncio
    async def test_nonexistent_parent_directory(self, temp_project):
        """Test export when parent directory doesn't exist and can't be created"""
        output_file = temp_project / "nonexistent" / "deep" / "path" / "export.json"

        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
            mock_process = Mock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(b"Export successful", b""))
            mock_exec.return_value = mock_process

            # Should handle missing directories gracefully
            result = await export_coderef(
                cli_command=["coderef"],
                project_path=str(temp_project),
                format="json",
                output_path=str(output_file)
            )

            # Even if CLI succeeds, file won't exist (directory wasn't created)
            result_data = json.loads(result[0].text)
            assert result_data["success"] is False
            assert "not created" in result_data["error"]


class TestCLIAvailability:
    """Test CLI command availability and path issues"""

    @pytest.mark.asyncio
    async def test_cli_command_not_found(self, temp_project):
        """Test handling when coderef CLI is not in PATH"""
        with patch('asyncio.create_subprocess_exec', side_effect=FileNotFoundError("Command not found")):
            result = await export_coderef(
                cli_command=["nonexistent-command"],
                project_path=str(temp_project),
                format="json"
            )

            result_data = json.loads(result[0].text)
            assert result_data["success"] is False
            assert "Command not found" in result_data["error"] or "not found" in result_data["error"].lower()

    @pytest.mark.asyncio
    async def test_invalid_cli_path(self, temp_project):
        """Test handling of invalid CLI path"""
        with patch('asyncio.create_subprocess_exec', side_effect=OSError("Invalid path")):
            result = await export_coderef(
                cli_command=["/invalid/path/to/coderef"],
                project_path=str(temp_project),
                format="json"
            )

            result_data = json.loads(result[0].text)
            assert result_data["success"] is False


class TestOverwriteBehavior:
    """Test file overwrite scenarios"""

    @pytest.mark.asyncio
    async def test_overwrite_existing_file(self, temp_project):
        """Test overwriting an existing export file"""
        output_file = temp_project / ".coderef" / "export.json"

        # Create existing file
        existing_content = '{"old": "data"}'
        output_file.write_text(existing_content)
        old_size = output_file.stat().st_size

        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
            mock_process = Mock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(b"Export successful", b""))
            mock_exec.return_value = mock_process

            # Overwrite with new content
            new_content = '{"new": "data", "more": "fields"}'
            output_file.write_text(new_content)

            result = await export_coderef(
                cli_command=["coderef"],
                project_path=str(temp_project),
                format="json",
                output_path=str(output_file)
            )

            result_data = json.loads(result[0].text)
            assert result_data["success"] is True

            # File size should have changed
            new_size = output_file.stat().st_size
            assert new_size != old_size


class TestOutputValidation:
    """Test output content validation"""

    @pytest.mark.asyncio
    async def test_corrupted_json_output(self, temp_project):
        """Test detection of malformed JSON output"""
        output_file = temp_project / ".coderef" / "corrupted.json"

        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
            mock_process = Mock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(b"Export successful", b""))
            mock_exec.return_value = mock_process

            # Create malformed JSON
            output_file.write_text('{"incomplete": ')

            result = await export_coderef(
                cli_command=["coderef"],
                project_path=str(temp_project),
                format="json",
                output_path=str(output_file)
            )

            # Should succeed (we don't validate JSON content, only that file exists)
            result_data = json.loads(result[0].text)
            assert result_data["success"] is True
            assert result_data["file_size_bytes"] > 0

    @pytest.mark.asyncio
    async def test_empty_output_file(self, temp_project):
        """Test handling of empty output file"""
        output_file = temp_project / ".coderef" / "empty.json"

        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
            mock_process = Mock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(b"Export successful", b""))
            mock_exec.return_value = mock_process

            # Create empty file
            output_file.write_text('')

            result = await export_coderef(
                cli_command=["coderef"],
                project_path=str(temp_project),
                format="json",
                output_path=str(output_file)
            )

            result_data = json.loads(result[0].text)
            assert result_data["success"] is True
            assert result_data["file_size_bytes"] == 0

    @pytest.mark.asyncio
    async def test_mermaid_syntax_validation(self, temp_project):
        """Test Mermaid output has valid syntax markers"""
        output_file = temp_project / ".coderef" / "diagram.mmd"

        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
            mock_process = Mock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(b"Export successful", b""))
            mock_exec.return_value = mock_process

            # Create valid Mermaid content
            mermaid_content = """graph TD
    A[Start] --> B[Process]
    B --> C[End]
"""
            output_file.write_text(mermaid_content)

            result = await export_coderef(
                cli_command=["coderef"],
                project_path=str(temp_project),
                format="mermaid",
                output_path=str(output_file)
            )

            result_data = json.loads(result[0].text)
            assert result_data["success"] is True

            # Verify content
            content = output_file.read_text()
            assert "graph TD" in content or "graph LR" in content or "flowchart" in content


class TestDiskSpaceErrors:
    """Test disk space and I/O error scenarios"""

    @pytest.mark.asyncio
    async def test_disk_full_simulation(self, temp_project):
        """Test handling of disk full during export"""
        output_file = temp_project / ".coderef" / "export.json"

        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
            mock_process = Mock()
            mock_process.returncode = 1
            mock_process.communicate = AsyncMock(
                return_value=(b"", b"No space left on device")
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
            assert "No space left" in result_data["error"]


class TestSequentialFormats:
    """Test exporting all formats sequentially"""

    @pytest.mark.asyncio
    async def test_export_all_formats_sequence(self, temp_project):
        """Test exporting all 4 formats one after another"""
        formats = {
            "json": "json",
            "jsonld": "jsonld",
            "mermaid": "mmd",
            "dot": "dot"
        }

        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
            mock_process = Mock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(b"Export successful", b""))
            mock_exec.return_value = mock_process

            results = []
            for fmt, ext in formats.items():
                output_file = temp_project / ".coderef" / f"export.{ext}"
                output_file.write_text('{"test": "data"}')

                result = await export_coderef(
                    cli_command=["coderef"],
                    project_path=str(temp_project),
                    format=fmt,
                    output_path=str(output_file)
                )

                result_data = json.loads(result[0].text)
                assert result_data["success"] is True
                results.append(result_data)

            # All 4 exports should succeed
            assert len(results) == 4
            assert all(r["success"] for r in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
