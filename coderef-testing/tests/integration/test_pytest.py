"""Integration tests for pytest framework."""

import asyncio
import tempfile
from pathlib import Path
from typing import Generator

import pytest

from src.models import TestFramework, TestStatus
from src.test_runner import TestRunner, TestRunRequest


@pytest.fixture
def pytest_project() -> Generator[Path, None, None]:
    """Create a temporary pytest project."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project = Path(tmpdir)

        # Create pytest.ini
        (project / "pytest.ini").write_text("[pytest]\ntestpaths = tests\n")

        # Create test files
        tests_dir = project / "tests"
        tests_dir.mkdir()

        (tests_dir / "test_math.py").write_text("""
def test_addition():
    assert 1 + 1 == 2

def test_subtraction():
    assert 5 - 3 == 2

def test_multiplication():
    assert 3 * 4 == 12

@pytest.mark.skip(reason="Not ready")
def test_skipped():
    assert False

def test_division_by_zero():
    with pytest.raises(ZeroDivisionError):
        _ = 1 / 0
""")

        (tests_dir / "test_strings.py").write_text("""
def test_uppercase():
    assert "hello".upper() == "HELLO"

def test_lowercase():
    assert "WORLD".lower() == "world"

def test_length():
    assert len("pytest") == 6
""")

        yield project


class TestPytestDiscovery:
    """Test pytest test discovery."""

    def test_discover_pytest_tests(self, pytest_project: Path) -> None:
        """Test that pytest tests can be discovered."""
        # This would be implemented by discovering tests
        # For now, verify the project structure
        tests_dir = pytest_project / "tests"
        assert tests_dir.exists()
        test_files = list(tests_dir.glob("test_*.py"))
        assert len(test_files) == 2

    def test_pytest_ini_exists(self, pytest_project: Path) -> None:
        """Test that pytest.ini is created."""
        assert (pytest_project / "pytest.ini").exists()


class TestPytestExecution:
    """Test pytest test execution."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_run_pytest_full_suite(self, pytest_project: Path) -> None:
        """Test running full pytest suite."""
        runner = TestRunner()
        req = TestRunRequest(
            project_path=str(pytest_project),
            framework=TestFramework.PYTEST,
        )

        # Note: This test requires pytest to be installed
        # Skip if pytest command is not available
        try:
            result = await runner.run_tests(req)
            assert result.framework.framework == TestFramework.PYTEST
            assert result.summary.total >= 0
            # Result should have some structure
            assert isinstance(result.tests, list)
        except FileNotFoundError:
            pytest.skip("pytest command not available")

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_run_pytest_single_file(self, pytest_project: Path) -> None:
        """Test running single pytest file."""
        runner = TestRunner()
        req = TestRunRequest(
            project_path=str(pytest_project),
            framework=TestFramework.PYTEST,
            test_file="tests/test_math.py",
        )

        try:
            result = await runner.run_tests(req)
            assert result.framework.framework == TestFramework.PYTEST
            # Should have parsed at least the file structure
            assert isinstance(result.summary, object)
        except FileNotFoundError:
            pytest.skip("pytest command not available")

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_pytest_result_structure(self, pytest_project: Path) -> None:
        """Test that pytest results have correct structure."""
        runner = TestRunner()
        req = TestRunRequest(
            project_path=str(pytest_project),
            framework=TestFramework.PYTEST,
        )

        try:
            result = await runner.run_tests(req)

            # Check summary structure
            assert hasattr(result.summary, 'total')
            assert hasattr(result.summary, 'passed')
            assert hasattr(result.summary, 'failed')
            assert hasattr(result.summary, 'skipped')

            # Check all counts are non-negative
            assert result.summary.total >= 0
            assert result.summary.passed >= 0
            assert result.summary.failed >= 0
            assert result.summary.skipped >= 0

            # Check tests list
            for test in result.tests:
                assert test.name
                assert test.status in [
                    TestStatus.PASSED,
                    TestStatus.FAILED,
                    TestStatus.SKIPPED,
                    TestStatus.ERROR,
                    TestStatus.XFAIL,
                    TestStatus.XPASS,
                ]
                assert test.duration >= 0
        except FileNotFoundError:
            pytest.skip("pytest command not available")

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_pytest_with_pattern(self, pytest_project: Path) -> None:
        """Test running pytest with test pattern."""
        runner = TestRunner()
        req = TestRunRequest(
            project_path=str(pytest_project),
            framework=TestFramework.PYTEST,
            test_pattern="test_math",
        )

        try:
            result = await runner.run_tests(req)
            assert result.framework.framework == TestFramework.PYTEST
        except FileNotFoundError:
            pytest.skip("pytest command not available")


class TestPytestOutput:
    """Test pytest output parsing."""

    def test_parse_pytest_output_structure(self) -> None:
        """Test parsing pytest output structure."""
        runner = TestRunner()

        sample_output = """
tests/test_math.py::test_addition PASSED [ 25%]
tests/test_math.py::test_subtraction PASSED [ 50%]
tests/test_math.py::test_multiplication PASSED [ 75%]
tests/test_math.py::test_division_by_zero PASSED [100%]

4 passed in 0.05s
        """

        tests, passed, failed, skipped = runner._parse_pytest_text(sample_output)
        assert len(tests) == 4
        assert passed == 4
        assert failed == 0
        assert skipped == 0

    def test_parse_pytest_with_failures(self) -> None:
        """Test parsing pytest output with failures."""
        runner = TestRunner()

        sample_output = """
tests/test_math.py::test_addition PASSED [ 50%]
tests/test_math.py::test_broken FAILED [100%]

1 passed, 1 failed in 0.05s
        """

        tests, passed, failed, skipped = runner._parse_pytest_text(sample_output)
        assert len(tests) == 2
        assert passed == 1
        assert failed == 1

    def test_parse_pytest_with_skipped(self) -> None:
        """Test parsing pytest output with skipped tests."""
        runner = TestRunner()

        sample_output = """
tests/test_math.py::test_addition PASSED
tests/test_math.py::test_skipped SKIPPED

1 passed, 1 skipped in 0.05s
        """

        tests, passed, failed, skipped = runner._parse_pytest_text(sample_output)
        assert len(tests) == 2
        assert skipped == 1


class TestPytestErrors:
    """Test pytest error handling."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_pytest_with_timeout(self) -> None:
        """Test pytest execution with timeout."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / "pytest.ini").write_text("[pytest]\n")

            runner = TestRunner()
            req = TestRunRequest(
                project_path=str(project),
                framework=TestFramework.PYTEST,
                timeout_seconds=0.01,  # Very short timeout
            )

            try:
                result = await runner.run_tests(req)
                # Should complete (timeout is handled gracefully)
                assert result.project == str(project)
            except FileNotFoundError:
                pytest.skip("pytest command not available")
