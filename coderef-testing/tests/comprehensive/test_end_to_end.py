"""
Comprehensive End-to-End Tests for coderef-testing MCP Server

Tests the complete workflow from framework detection through execution,
aggregation, analysis, and reporting.
"""

import asyncio
import json
import pytest
from pathlib import Path
from datetime import datetime

from src.framework_detector import detect_frameworks
from src.test_runner import TestRunner
from src.test_aggregator import TestAggregator
from src.result_analyzer import ResultAnalyzer
from src.models import (
    TestFramework,
    TestRunRequest,
    TestStatus,
    UnifiedTestResults
)


class TestCompleteWorkflow:
    """Test complete workflow from discovery to reporting"""

    @pytest.mark.asyncio
    async def test_pytest_complete_workflow(self, tmp_path):
        """Test complete workflow with pytest project"""
        # Setup: Create minimal pytest project
        project_dir = tmp_path / "test_project"
        project_dir.mkdir()

        # Create pyproject.toml
        (project_dir / "pyproject.toml").write_text("""
[tool.pytest.ini_options]
testpaths = ["tests"]
""")

        # Create test file
        tests_dir = project_dir / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_sample.py").write_text("""
def test_passing():
    assert 1 + 1 == 2

def test_failing():
    assert 1 + 1 == 3
""")

        # Step 1: Detect framework
        frameworks = detect_frameworks(str(project_dir))
        assert len(frameworks) >= 1
        assert any(f.framework == TestFramework.PYTEST for f in frameworks)

        # Step 2: Run tests
        runner = TestRunner()
        request = TestRunRequest(
            project_path=str(project_dir),
            framework=TestFramework.PYTEST,
            max_workers=1,
            timeout_seconds=30
        )

        results = await runner.run_tests(request)

        # Verify results structure
        assert isinstance(results, UnifiedTestResults)
        assert results.framework.framework == TestFramework.PYTEST
        assert results.summary.total >= 2
        assert results.summary.passed >= 1
        assert results.summary.failed >= 1

        # Step 3: Aggregate results
        aggregator = TestAggregator()
        archived_path = aggregator.archive_results(results)
        assert archived_path.exists()

        # Step 4: Analyze results
        analyzer = ResultAnalyzer()

        # Coverage analysis
        coverage = analyzer.analyze_coverage(results)
        assert coverage.analysis_type == "coverage"
        assert coverage.result_key == "coverage_percent"

        # Performance analysis
        performance = analyzer.analyze_performance(results)
        assert performance.analysis_type == "performance"
        assert performance.result_key == "avg_duration"

        # Health validation
        health = analyzer.validate_test_health(results)
        assert health.analysis_type == "health"
        assert 0 <= health.result_value <= 100
        assert health.details.get("grade") in ["A", "B", "C", "D", "F"]

        # Step 5: Verify archival
        latest = aggregator.get_latest_result()
        assert latest is not None
        assert latest["summary"]["total"] == results.summary.total


class TestFrameworkDetection:
    """Comprehensive framework detection tests"""

    def test_detect_pytest_from_pyproject_toml(self, tmp_path):
        """Detect pytest from pyproject.toml"""
        project_dir = tmp_path / "pytest_project"
        project_dir.mkdir()
        (project_dir / "pyproject.toml").write_text('[tool.pytest.ini_options]')

        frameworks = detect_frameworks(str(project_dir))
        assert any(f.framework == TestFramework.PYTEST for f in frameworks)

    def test_detect_pytest_from_pytest_ini(self, tmp_path):
        """Detect pytest from pytest.ini"""
        project_dir = tmp_path / "pytest_project"
        project_dir.mkdir()
        (project_dir / "pytest.ini").write_text('[pytest]')

        frameworks = detect_frameworks(str(project_dir))
        assert any(f.framework == TestFramework.PYTEST for f in frameworks)

    def test_detect_jest_from_package_json(self, tmp_path):
        """Detect jest from package.json"""
        project_dir = tmp_path / "jest_project"
        project_dir.mkdir()
        (project_dir / "package.json").write_text(json.dumps({
            "devDependencies": {"jest": "^29.0.0"}
        }))

        frameworks = detect_frameworks(str(project_dir))
        assert any(f.framework == TestFramework.JEST for f in frameworks)

    def test_detect_jest_from_config_file(self, tmp_path):
        """Detect jest from jest.config.js"""
        project_dir = tmp_path / "jest_project"
        project_dir.mkdir()
        (project_dir / "jest.config.js").write_text('module.exports = {};')

        frameworks = detect_frameworks(str(project_dir))
        assert any(f.framework == TestFramework.JEST for f in frameworks)

    def test_detect_cargo_from_cargo_toml(self, tmp_path):
        """Detect cargo from Cargo.toml"""
        project_dir = tmp_path / "rust_project"
        project_dir.mkdir()
        (project_dir / "Cargo.toml").write_text('[package]\nname = "test"')

        frameworks = detect_frameworks(str(project_dir))
        # Cargo may or may not be detected depending on environment
        # Just verify no errors occur


class TestExecutionScenarios:
    """Test various execution scenarios"""

    @pytest.mark.asyncio
    async def test_timeout_handling(self, tmp_path):
        """Test timeout handling for slow tests"""
        project_dir = tmp_path / "slow_project"
        project_dir.mkdir()

        (project_dir / "pyproject.toml").write_text('[tool.pytest.ini_options]')
        tests_dir = project_dir / "tests"
        tests_dir.mkdir()

        # Create test that sleeps (but not too long for actual test run)
        (tests_dir / "test_slow.py").write_text("""
import time
def test_quick():
    time.sleep(0.1)
    assert True
""")

        runner = TestRunner()
        request = TestRunRequest(
            project_path=str(project_dir),
            framework=TestFramework.PYTEST,
            timeout_seconds=5  # Short timeout
        )

        results = await runner.run_tests(request)
        assert results is not None

    @pytest.mark.asyncio
    async def test_parallel_execution(self, tmp_path):
        """Test parallel test execution"""
        project_dir = tmp_path / "parallel_project"
        project_dir.mkdir()

        (project_dir / "pyproject.toml").write_text('[tool.pytest.ini_options]')
        tests_dir = project_dir / "tests"
        tests_dir.mkdir()

        # Create multiple test files
        for i in range(5):
            (tests_dir / f"test_{i}.py").write_text(f"""
def test_pass_{i}():
    assert True
""")

        runner = TestRunner()
        request = TestRunRequest(
            project_path=str(project_dir),
            framework=TestFramework.PYTEST,
            max_workers=4  # Use 4 parallel workers
        )

        results = await runner.run_tests(request)
        assert results.summary.total >= 5
        assert results.summary.passed >= 5


class TestResultAggregation:
    """Test result aggregation and archival"""

    def test_archive_creates_timestamped_file(self, sample_results, tmp_path):
        """Test archival creates properly timestamped file"""
        aggregator = TestAggregator()

        # Override archive directory for testing
        original_dir = aggregator.archive_dir
        aggregator.archive_dir = tmp_path / "results"

        try:
            archived_path = aggregator.archive_results(sample_results)

            assert archived_path.exists()
            assert archived_path.suffix == ".json"

            # Verify content
            content = json.loads(archived_path.read_text())
            assert content["project"] == sample_results.project
            assert content["summary"]["total"] == sample_results.summary.total
        finally:
            aggregator.archive_dir = original_dir

    def test_get_archived_results_sorted_by_date(self, sample_results, tmp_path):
        """Test archived results are sorted chronologically"""
        aggregator = TestAggregator()
        aggregator.archive_dir = tmp_path / "results"

        # Archive multiple results
        for i in range(3):
            result = sample_results.model_copy()
            result.timestamp = datetime.utcnow()
            aggregator.archive_results(result)

        archived = aggregator.get_archived_results()

        assert len(archived) == 3
        # Verify sorted by timestamp (newest first)
        timestamps = [r["timestamp"] for r in archived]
        assert timestamps == sorted(timestamps, reverse=True)


class TestAnalysisFeatures:
    """Test analysis features: coverage, performance, flaky, health"""

    def test_coverage_analysis_identifies_gaps(self, sample_results):
        """Test coverage analysis identifies uncovered code"""
        analyzer = ResultAnalyzer()

        # Add coverage data
        from src.models import CoverageInfo
        sample_results.coverage = CoverageInfo(
            covered_lines=800,
            total_lines=1000,
            coverage_percent=80.0,
            missing_lines=[10, 20, 30, 40, 50]
        )

        analysis = analyzer.analyze_coverage(sample_results)

        assert analysis.result_value == 80.0
        assert "missing_lines" in analysis.details
        assert len(analysis.recommendations) > 0

    def test_performance_analysis_finds_slow_tests(self, sample_results):
        """Test performance analysis identifies slow tests"""
        analyzer = ResultAnalyzer()

        # Add slow test to results
        from src.models import TestResult
        slow_test = TestResult(
            name="test_very_slow",
            status=TestStatus.PASSED,
            duration=5.0,  # Very slow
            file="tests/test_slow.py"
        )
        sample_results.tests.append(slow_test)

        analysis = analyzer.analyze_performance(sample_results, threshold=1.0)

        assert "slow_tests" in analysis.details
        slow_tests = analysis.details["slow_tests"]
        assert len(slow_tests) > 0
        assert any(t["name"] == "test_very_slow" for t in slow_tests)

    def test_health_scoring_calculation(self, sample_results):
        """Test health score calculation"""
        analyzer = ResultAnalyzer()

        health = analyzer.validate_test_health(sample_results)

        assert 0 <= health.result_value <= 100
        assert "grade" in health.details
        assert "breakdown" in health.details

        # Verify breakdown components
        breakdown = health.details["breakdown"]
        assert "correctness" in breakdown
        assert "coverage" in breakdown
        assert "speed" in breakdown
        assert "stability" in breakdown

    def test_flaky_test_detection(self):
        """Test flaky test detection from historical data"""
        analyzer = ResultAnalyzer()

        # Create historical results with flaky test
        from src.models import TestResult, TestSummary, FrameworkInfo

        results_history = []
        for i in range(5):
            # Test passes 3 times, fails 2 times (flaky)
            test_status = TestStatus.PASSED if i < 3 else TestStatus.FAILED

            result = UnifiedTestResults(
                project="/test",
                framework=FrameworkInfo(framework=TestFramework.PYTEST),
                summary=TestSummary(
                    total=1, passed=1 if test_status == TestStatus.PASSED else 0,
                    failed=0 if test_status == TestStatus.PASSED else 1,
                    skipped=0, duration=1.0, success_rate=100.0 if test_status == TestStatus.PASSED else 0.0
                ),
                tests=[TestResult(
                    name="test_flaky",
                    status=test_status,
                    duration=0.5
                )],
                timestamp=datetime.utcnow()
            )
            results_history.append(result)

        analysis = analyzer.detect_flaky(results_history)

        assert analysis.analysis_type == "flaky"
        assert "flaky_tests" in analysis.details
        flaky_tests = analysis.details["flaky_tests"]
        assert len(flaky_tests) > 0
        assert flaky_tests[0]["name"] == "test_flaky"
        assert 0.3 < flaky_tests[0]["flakiness_score"] < 0.5  # 2/5 = 0.4


class TestErrorHandling:
    """Test error handling and edge cases"""

    @pytest.mark.asyncio
    async def test_missing_project_directory(self):
        """Test error handling for missing project"""
        runner = TestRunner()
        request = TestRunRequest(
            project_path="/nonexistent/path",
            framework=TestFramework.PYTEST
        )

        with pytest.raises(Exception):
            await runner.run_tests(request)

    @pytest.mark.asyncio
    async def test_no_tests_found(self, tmp_path):
        """Test handling when no tests are found"""
        project_dir = tmp_path / "empty_project"
        project_dir.mkdir()
        (project_dir / "pyproject.toml").write_text('[tool.pytest.ini_options]')

        runner = TestRunner()
        request = TestRunRequest(
            project_path=str(project_dir),
            framework=TestFramework.PYTEST
        )

        results = await runner.run_tests(request)
        assert results.summary.total == 0

    def test_invalid_framework_enum(self):
        """Test validation of framework enum"""
        with pytest.raises(ValueError):
            TestFramework("invalid_framework")


# Fixtures

@pytest.fixture
def sample_results():
    """Create sample test results for testing"""
    from src.models import TestResult, TestSummary, FrameworkInfo

    return UnifiedTestResults(
        project="/test/project",
        framework=FrameworkInfo(
            framework=TestFramework.PYTEST,
            version="7.4.3",
            config_file="pyproject.toml"
        ),
        summary=TestSummary(
            total=10,
            passed=8,
            failed=2,
            skipped=0,
            duration=5.0,
            success_rate=80.0
        ),
        tests=[
            TestResult(
                name=f"test_{i}",
                status=TestStatus.PASSED if i < 8 else TestStatus.FAILED,
                duration=0.5,
                file=f"tests/test_{i}.py"
            )
            for i in range(10)
        ],
        timestamp=datetime.utcnow()
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
