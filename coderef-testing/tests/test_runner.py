"""Unit tests for test_runner module."""

import asyncio
import tempfile
from pathlib import Path
from typing import Generator

import pytest

from src.models import TestFramework, TestStatus
from src.test_runner import TestRunner, TestRunRequest


@pytest.fixture
def temp_project() -> Generator[Path, None, None]:
    """Create a temporary project directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def runner() -> TestRunner:
    """Create a fresh test runner instance."""
    return TestRunner()


@pytest.fixture
def basic_pytest_project(temp_project: Path) -> Path:
    """Create a basic pytest project."""
    (temp_project / "pytest.ini").write_text("[pytest]\n")
    tests_dir = temp_project / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_example.py").write_text(
        "def test_pass():\n    assert True\n\ndef test_fail():\n    assert False\n"
    )
    return temp_project


class TestTestRunRequest:
    """Test TestRunRequest dataclass."""

    def test_basic_request(self) -> None:
        """Test creating a basic test run request."""
        req = TestRunRequest(project_path="/tmp/test")
        assert req.project_path == "/tmp/test"
        assert req.framework is None
        assert req.timeout_seconds == 300.0
        assert req.max_workers == 4

    def test_request_with_options(self) -> None:
        """Test creating request with options."""
        req = TestRunRequest(
            project_path="/tmp/test",
            framework=TestFramework.PYTEST,
            test_file="tests/test_example.py",
            timeout_seconds=60.0,
            max_workers=2,
            verbose=True,
        )
        assert req.framework == TestFramework.PYTEST
        assert req.test_file == "tests/test_example.py"
        assert req.timeout_seconds == 60.0
        assert req.max_workers == 2
        assert req.verbose is True


class TestCommandExecution:
    """Test command execution helper."""

    @pytest.mark.asyncio
    async def test_execute_command_success(self, runner: TestRunner, temp_project: Path) -> None:
        """Test executing a successful command."""
        # Use 'echo' which should be available on all platforms
        result = await runner._execute_command(["echo", "hello"], temp_project, 10.0)
        assert "hello" in result

    @pytest.mark.asyncio
    async def test_execute_command_missing_command(
        self, runner: TestRunner, temp_project: Path
    ) -> None:
        """Test executing a non-existent command."""
        with pytest.raises(FileNotFoundError):
            await runner._execute_command(
                ["nonexistent-command-12345"], temp_project, 10.0
            )

    @pytest.mark.asyncio
    async def test_execute_command_timeout(
        self, runner: TestRunner, temp_project: Path
    ) -> None:
        """Test command execution timeout."""
        with pytest.raises(asyncio.TimeoutError):
            # Use 'sleep' to simulate a long-running command
            await runner._execute_command(["sleep", "10"], temp_project, 0.1)


class TestPytestParsing:
    """Test pytest output parsing."""

    def test_map_pytest_status(self, runner: TestRunner) -> None:
        """Test mapping pytest outcomes to TestStatus."""
        assert runner._map_pytest_status("passed") == TestStatus.PASSED
        assert runner._map_pytest_status("failed") == TestStatus.FAILED
        assert runner._map_pytest_status("skipped") == TestStatus.SKIPPED
        assert runner._map_pytest_status("error") == TestStatus.ERROR
        assert runner._map_pytest_status("xfail") == TestStatus.XFAIL
        assert runner._map_pytest_status("xpass") == TestStatus.XPASS
        assert runner._map_pytest_status("unknown") == TestStatus.ERROR

    def test_parse_pytest_text_output(self, runner: TestRunner) -> None:
        """Test parsing pytest text output."""
        output = """
test_example.py::test_pass PASSED [ 50%]
test_example.py::test_fail FAILED [100%]
test_example.py::test_skip SKIPPED
        """
        tests, passed, failed, skipped = runner._parse_pytest_text(output)
        assert len(tests) == 3
        assert passed == 1
        assert failed == 1
        assert skipped == 1
        assert any(t.status == TestStatus.PASSED for t in tests)
        assert any(t.status == TestStatus.FAILED for t in tests)
        assert any(t.status == TestStatus.SKIPPED for t in tests)

    def test_parse_empty_pytest_output(self, runner: TestRunner) -> None:
        """Test parsing empty pytest output."""
        output = ""
        tests, passed, failed, skipped = runner._parse_pytest_text(output)
        assert len(tests) == 0
        assert passed == 0
        assert failed == 0
        assert skipped == 0


class TestRunTestsIntegration:
    """Integration tests for test execution."""

    @pytest.mark.asyncio
    async def test_run_tests_unknown_framework(
        self, runner: TestRunner, temp_project: Path
    ) -> None:
        """Test running tests with unknown framework."""
        req = TestRunRequest(project_path=str(temp_project))
        result = await runner.run_tests(req)
        assert result.framework.framework == TestFramework.UNKNOWN
        assert result.summary.total == 0

    @pytest.mark.asyncio
    async def test_unified_results_structure(
        self, runner: TestRunner, temp_project: Path
    ) -> None:
        """Test that results follow unified schema."""
        req = TestRunRequest(project_path=str(temp_project))
        result = await runner.run_tests(req)

        # Check required fields
        assert result.project == str(temp_project)
        assert result.framework.framework in [f for f in TestFramework]
        assert isinstance(result.summary, object)
        assert hasattr(result.summary, 'total')
        assert hasattr(result.summary, 'passed')
        assert hasattr(result.summary, 'failed')
        assert hasattr(result.summary, 'skipped')
        assert isinstance(result.tests, list)

    @pytest.mark.asyncio
    async def test_timeout_error_handling(self, runner: TestRunner, temp_project: Path) -> None:
        """Test handling of timeout errors."""
        # Create pytest project
        (temp_project / "pytest.ini").write_text("[pytest]\n")
        tests_dir = temp_project / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_slow.py").write_text(
            "import time\ndef test_slow():\n    time.sleep(10)\n"
        )

        req = TestRunRequest(
            project_path=str(temp_project),
            framework=TestFramework.PYTEST,
            timeout_seconds=0.1,
        )
        result = await runner.run_tests(req)

        # Should have error or timeout indicator
        assert result.error is not None or result.summary.get("timeout", 0) > 0


class TestStatusMapping:
    """Test status mappings across frameworks."""

    def test_all_test_statuses_defined(self) -> None:
        """Test that all TestStatus enum values are defined."""
        statuses = [
            TestStatus.PASSED,
            TestStatus.FAILED,
            TestStatus.SKIPPED,
            TestStatus.ERROR,
            TestStatus.XFAIL,
            TestStatus.XPASS,
        ]
        assert len(statuses) == 6

    def test_all_frameworks_defined(self) -> None:
        """Test that all TestFramework enum values are defined."""
        frameworks = [
            TestFramework.PYTEST,
            TestFramework.JEST,
            TestFramework.VITEST,
            TestFramework.CARGO,
            TestFramework.MOCHA,
            TestFramework.UNKNOWN,
        ]
        assert len(frameworks) == 6


class TestRunRequestValidation:
    """Test request validation."""

    def test_request_with_both_file_and_pattern(self) -> None:
        """Test request with both test file and pattern."""
        req = TestRunRequest(
            project_path="/tmp/test",
            test_file="tests/test_example.py",
            test_pattern="test_specific",
        )
        # Both should be allowed (the runner decides priority)
        assert req.test_file is not None
        assert req.test_pattern is not None

    def test_request_timeout_validation(self) -> None:
        """Test request timeout values."""
        req_short = TestRunRequest(project_path="/tmp/test", timeout_seconds=1.0)
        req_long = TestRunRequest(project_path="/tmp/test", timeout_seconds=3600.0)
        assert req_short.timeout_seconds == 1.0
        assert req_long.timeout_seconds == 3600.0

    def test_request_workers_validation(self) -> None:
        """Test request max_workers values."""
        req_one = TestRunRequest(project_path="/tmp/test", max_workers=1)
        req_many = TestRunRequest(project_path="/tmp/test", max_workers=16)
        assert req_one.max_workers == 1
        assert req_many.max_workers == 16
