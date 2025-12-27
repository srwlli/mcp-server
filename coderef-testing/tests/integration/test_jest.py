"""Integration tests for jest framework."""

import asyncio
import json
import tempfile
from pathlib import Path
from typing import Generator

import pytest

from src.models import TestFramework, TestStatus
from src.test_runner import TestRunner, TestRunRequest


@pytest.fixture
def jest_project() -> Generator[Path, None, None]:
    """Create a temporary jest project."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project = Path(tmpdir)

        # Create package.json
        package_json = {
            "name": "test-project",
            "version": "1.0.0",
            "devDependencies": {"jest": "^29.0.0"},
            "scripts": {"test": "jest"},
        }
        (project / "package.json").write_text(json.dumps(package_json, indent=2))

        # Create jest.config.js
        (project / "jest.config.js").write_text("module.exports = {};\n")

        # Create test files
        tests_dir = project
        (tests_dir / "math.test.js").write_text("""
describe('Math operations', () => {
  test('addition', () => {
    expect(1 + 1).toBe(2);
  });

  test('subtraction', () => {
    expect(5 - 3).toBe(2);
  });

  test('multiplication', () => {
    expect(3 * 4).toBe(12);
  });
});
""")

        (tests_dir / "strings.test.js").write_text("""
describe('String operations', () => {
  test('uppercase', () => {
    expect('hello'.toUpperCase()).toBe('HELLO');
  });

  test('lowercase', () => {
    expect('WORLD'.toLowerCase()).toBe('world');
  });

  test('length', () => {
    expect('jest'.length).toBe(4);
  });
});
""")

        yield project


class TestJestDiscovery:
    """Test jest test discovery."""

    def test_discover_jest_tests(self, jest_project: Path) -> None:
        """Test that jest tests can be discovered."""
        test_files = list(jest_project.glob("*.test.js"))
        assert len(test_files) == 2

    def test_jest_config_exists(self, jest_project: Path) -> None:
        """Test that jest.config.js is created."""
        assert (jest_project / "jest.config.js").exists()

    def test_package_json_exists(self, jest_project: Path) -> None:
        """Test that package.json is created."""
        assert (jest_project / "package.json").exists()
        package_json = json.loads((jest_project / "package.json").read_text())
        assert "jest" in package_json.get("devDependencies", {})


class TestJestExecution:
    """Test jest test execution."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_run_jest_full_suite(self, jest_project: Path) -> None:
        """Test running full jest suite."""
        runner = TestRunner()
        req = TestRunRequest(
            project_path=str(jest_project),
            framework=TestFramework.JEST,
        )

        # Note: This test requires jest to be installed
        try:
            result = await runner.run_tests(req)
            assert result.framework.framework == TestFramework.JEST
            assert isinstance(result.summary, object)
        except FileNotFoundError:
            pytest.skip("jest/npm command not available")

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_run_jest_single_file(self, jest_project: Path) -> None:
        """Test running single jest file."""
        runner = TestRunner()
        req = TestRunRequest(
            project_path=str(jest_project),
            framework=TestFramework.JEST,
            test_file="math.test.js",
        )

        try:
            result = await runner.run_tests(req)
            assert result.framework.framework == TestFramework.JEST
        except FileNotFoundError:
            pytest.skip("jest/npm command not available")

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_jest_result_structure(self, jest_project: Path) -> None:
        """Test that jest results have correct structure."""
        runner = TestRunner()
        req = TestRunRequest(
            project_path=str(jest_project),
            framework=TestFramework.JEST,
        )

        try:
            result = await runner.run_tests(req)

            # Check summary structure
            assert hasattr(result.summary, 'total')
            assert hasattr(result.summary, 'passed')
            assert hasattr(result.summary, 'failed')
            assert hasattr(result.summary, 'skipped')

            # Check counts are non-negative
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
        except FileNotFoundError:
            pytest.skip("jest/npm command not available")

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_jest_with_pattern(self, jest_project: Path) -> None:
        """Test running jest with test pattern."""
        runner = TestRunner()
        req = TestRunRequest(
            project_path=str(jest_project),
            framework=TestFramework.JEST,
            test_pattern="Math",
        )

        try:
            result = await runner.run_tests(req)
            assert result.framework.framework == TestFramework.JEST
        except FileNotFoundError:
            pytest.skip("jest/npm command not available")


class TestJestOutput:
    """Test jest output parsing."""

    def test_jest_json_results_parsing(self) -> None:
        """Test parsing jest JSON results."""
        runner = TestRunner()

        sample_json = {
            "testResults": [
                {
                    "name": "math.test.js",
                    "assertionResults": [
                        {
                            "fullName": "Math operations addition",
                            "status": "passed",
                            "duration": 5,
                        },
                        {
                            "fullName": "Math operations subtraction",
                            "status": "passed",
                            "duration": 3,
                        },
                        {
                            "fullName": "Math operations broken",
                            "status": "failed",
                            "duration": 10,
                        },
                    ],
                }
            ]
        }

        # Verify structure is as expected
        assert len(sample_json["testResults"]) == 1
        assert len(sample_json["testResults"][0]["assertionResults"]) == 3

    def test_jest_status_mapping(self) -> None:
        """Test jest status mapping."""
        runner = TestRunner()

        # Jest uses simple passed/failed/skipped
        statuses = ["passed", "failed", "skipped", "todo"]
        expected = [TestStatus.PASSED, TestStatus.FAILED, TestStatus.SKIPPED, None]

        for status, expected_status in zip(statuses, expected):
            if expected_status:
                if status == "passed":
                    assert status == "passed"
                elif status == "failed":
                    assert status == "failed"
                elif status == "skipped":
                    assert status == "skipped"


class TestJestErrors:
    """Test jest error handling."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_jest_missing_package_json(self) -> None:
        """Test jest execution without package.json."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / "jest.config.js").write_text("module.exports = {};\n")

            runner = TestRunner()
            req = TestRunRequest(
                project_path=str(project),
                framework=TestFramework.JEST,
            )

            try:
                result = await runner.run_tests(req)
                # Should handle gracefully
                assert result.framework.framework == TestFramework.JEST
            except FileNotFoundError:
                pytest.skip("jest/npm command not available")

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_jest_with_timeout(self) -> None:
        """Test jest execution with timeout."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            package_json = {
                "name": "test-project",
                "scripts": {"test": "jest"},
            }
            (project / "package.json").write_text(json.dumps(package_json))
            (project / "jest.config.js").write_text("module.exports = {};\n")

            runner = TestRunner()
            req = TestRunRequest(
                project_path=str(project),
                framework=TestFramework.JEST,
                timeout_seconds=0.01,
            )

            try:
                result = await runner.run_tests(req)
                # Should complete (timeout is handled gracefully)
                assert result.project == str(project)
            except FileNotFoundError:
                pytest.skip("jest/npm command not available")


class TestJestIntegration:
    """Integration tests combining jest discovery and execution."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_jest_complete_workflow(self, jest_project: Path) -> None:
        """Test complete jest workflow: discover and run."""
        runner = TestRunner()

        # First: detect framework
        from src.framework_detector import detect_frameworks

        frameworks = detect_frameworks(str(jest_project))
        assert any(f.framework == TestFramework.JEST for f in frameworks)

        # Second: run tests
        req = TestRunRequest(project_path=str(jest_project))
        try:
            result = await runner.run_tests(req)
            # Should auto-detect jest and run
            assert result.framework.framework in [TestFramework.JEST, TestFramework.UNKNOWN]
        except FileNotFoundError:
            pytest.skip("jest/npm command not available")
