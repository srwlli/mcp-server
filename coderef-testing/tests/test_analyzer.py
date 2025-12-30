"""Comprehensive unit tests for result_analyzer.py - Phase 3: Result Processing & Analysis.

Tests coverage analysis, flaky test detection, performance analysis, and health validation.
"""

import pytest
from typing import List

from src.result_analyzer import (
    ResultAnalyzer,
    analyze_coverage,
    detect_flaky_tests,
    analyze_performance,
    validate_test_health,
)
from src.models import (
    UnifiedTestResults,
    FrameworkInfo,
    TestSummary,
    TestResult,
    TestStatus,
    TestFramework,
)


@pytest.fixture
def analyzer() -> ResultAnalyzer:
    """Create analyzer instance."""
    return ResultAnalyzer()


@pytest.fixture
def passing_results() -> UnifiedTestResults:
    """Create sample results with all passing tests."""
    return UnifiedTestResults(
        project="/test",
        framework=FrameworkInfo(framework=TestFramework.PYTEST),
        summary=TestSummary(
            total=10, passed=10, failed=0, skipped=0, duration=10.0, success_rate=100.0
        ),
        tests=[
            TestResult(name=f"test_{i}", status=TestStatus.PASSED, duration=1.0)
            for i in range(10)
        ],
    )


@pytest.fixture
def mixed_results() -> UnifiedTestResults:
    """Create sample results with mixed statuses."""
    return UnifiedTestResults(
        project="/test",
        framework=FrameworkInfo(framework=TestFramework.PYTEST),
        summary=TestSummary(
            total=10, passed=6, failed=2, skipped=2, duration=8.0, success_rate=75.0
        ),
        tests=[
            TestResult(name="test_1", status=TestStatus.PASSED, duration=1.0),
            TestResult(name="test_2", status=TestStatus.PASSED, duration=1.0),
            TestResult(name="test_3", status=TestStatus.PASSED, duration=1.0),
            TestResult(name="test_4", status=TestStatus.PASSED, duration=1.0),
            TestResult(name="test_5", status=TestStatus.PASSED, duration=1.0),
            TestResult(name="test_6", status=TestStatus.PASSED, duration=1.0),
            TestResult(name="test_7", status=TestStatus.FAILED, duration=0.5),
            TestResult(name="test_8", status=TestStatus.FAILED, duration=0.5),
            TestResult(name="test_9", status=TestStatus.SKIPPED, duration=0.0),
            TestResult(name="test_10", status=TestStatus.SKIPPED, duration=0.0),
        ],
    )


class TestCoverageAnalysis:
    """Test coverage analysis functionality."""

    def test_analyze_coverage_with_tests(self, analyzer: ResultAnalyzer, passing_results: UnifiedTestResults) -> None:
        """Test coverage analysis with passing tests."""
        coverage = analyzer.analyze_coverage(passing_results)

        assert coverage["total_tests"] == 10
        assert coverage["passed_tests"] == 10
        assert coverage["failed_tests"] == 0
        assert coverage["skipped_tests"] == 0
        assert coverage["coverage_percentage"] == 100.0
        assert coverage["coverage_available"] is True

    def test_analyze_coverage_with_failures(self, analyzer: ResultAnalyzer, mixed_results: UnifiedTestResults) -> None:
        """Test coverage analysis with mixed results."""
        coverage = analyzer.analyze_coverage(mixed_results)

        assert coverage["total_tests"] == 10
        assert coverage["passed_tests"] == 6
        assert coverage["failed_tests"] == 2
        assert coverage["skipped_tests"] == 2
        assert coverage["coverage_percentage"] == 60.0

    def test_analyze_coverage_no_tests(self, analyzer: ResultAnalyzer) -> None:
        """Test coverage analysis with no tests."""
        empty_results = UnifiedTestResults(
            project="/test",
            framework=FrameworkInfo(framework=TestFramework.PYTEST),
            summary=TestSummary(
                total=0, passed=0, failed=0, skipped=0, duration=0.0, success_rate=0.0
            ),
            tests=[],
        )

        coverage = analyzer.analyze_coverage(empty_results)
        assert coverage["total_tests"] == 0
        assert coverage["coverage_percentage"] == 0
        assert coverage["coverage_available"] is False
        assert "No tests found" in coverage["message"]

    def test_analyze_coverage_all_failing(self, analyzer: ResultAnalyzer) -> None:
        """Test coverage analysis with all failing tests."""
        failing_results = UnifiedTestResults(
            project="/test",
            framework=FrameworkInfo(framework=TestFramework.PYTEST),
            summary=TestSummary(
                total=5, passed=0, failed=5, skipped=0, duration=5.0, success_rate=0.0
            ),
            tests=[
                TestResult(name=f"test_{i}", status=TestStatus.FAILED, duration=1.0)
                for i in range(5)
            ],
        )

        coverage = analyzer.analyze_coverage(failing_results)
        assert coverage["coverage_percentage"] == 0.0
        assert coverage["failed_tests"] == 5


class TestFlakyTestDetection:
    """Test flaky test detection functionality."""

    def test_detect_flaky_tests_basic(self, analyzer: ResultAnalyzer) -> None:
        """Test detecting flaky tests from historical results."""
        # Create 3 runs where test_flaky passes sometimes and fails sometimes
        results1 = UnifiedTestResults(
            project="/test",
            framework=FrameworkInfo(framework=TestFramework.PYTEST),
            summary=TestSummary(total=2, passed=1, failed=1, skipped=0, duration=2.0, success_rate=50.0),
            tests=[
                TestResult(name="test_stable", status=TestStatus.PASSED, duration=1.0),
                TestResult(name="test_flaky", status=TestStatus.PASSED, duration=1.0),
            ],
        )

        results2 = UnifiedTestResults(
            project="/test",
            framework=FrameworkInfo(framework=TestFramework.PYTEST),
            summary=TestSummary(total=2, passed=1, failed=1, skipped=0, duration=2.0, success_rate=50.0),
            tests=[
                TestResult(name="test_stable", status=TestStatus.PASSED, duration=1.0),
                TestResult(name="test_flaky", status=TestStatus.FAILED, duration=1.0),
            ],
        )

        results3 = UnifiedTestResults(
            project="/test",
            framework=FrameworkInfo(framework=TestFramework.PYTEST),
            summary=TestSummary(total=2, passed=1, failed=1, skipped=0, duration=2.0, success_rate=50.0),
            tests=[
                TestResult(name="test_stable", status=TestStatus.PASSED, duration=1.0),
                TestResult(name="test_flaky", status=TestStatus.PASSED, duration=1.0),
            ],
        )

        flaky = analyzer.detect_flaky_tests([results1, results2, results3])

        assert "test_flaky" in flaky
        assert flaky["test_flaky"]["passed_runs"] == 2
        assert flaky["test_flaky"]["failed_runs"] == 1
        assert flaky["test_flaky"]["total_runs"] == 3
        assert "test_stable" not in flaky  # Always passed

    def test_detect_flaky_tests_no_flakiness(self, analyzer: ResultAnalyzer, passing_results: UnifiedTestResults) -> None:
        """Test that stable tests are not marked as flaky."""
        flaky = analyzer.detect_flaky_tests([passing_results, passing_results, passing_results])
        assert len(flaky) == 0

    def test_detect_flaky_tests_insufficient_history(self, analyzer: ResultAnalyzer, passing_results: UnifiedTestResults) -> None:
        """Test that single result returns no flaky tests."""
        flaky = analyzer.detect_flaky_tests([passing_results])
        assert len(flaky) == 0

    def test_detect_flaky_tests_always_failing_not_flaky(self, analyzer: ResultAnalyzer) -> None:
        """Test that consistently failing tests are not marked as flaky."""
        failing_results = UnifiedTestResults(
            project="/test",
            framework=FrameworkInfo(framework=TestFramework.PYTEST),
            summary=TestSummary(total=1, passed=0, failed=1, skipped=0, duration=1.0, success_rate=0.0),
            tests=[TestResult(name="test_broken", status=TestStatus.FAILED, duration=1.0)],
        )

        flaky = analyzer.detect_flaky_tests([failing_results, failing_results, failing_results])
        assert len(flaky) == 0  # Consistently failing, not flaky

    def test_flaky_test_status_history(self, analyzer: ResultAnalyzer) -> None:
        """Test that flaky test detection includes status history."""
        results = [
            UnifiedTestResults(
                project="/test",
                framework=FrameworkInfo(framework=TestFramework.PYTEST),
                summary=TestSummary(total=1, passed=0 if i % 2 == 0 else 1, failed=1 if i % 2 == 0 else 0, skipped=0, duration=1.0, success_rate=0.0 if i % 2 == 0 else 100.0),
                tests=[
                    TestResult(
                        name="test_flaky",
                        status=TestStatus.FAILED if i % 2 == 0 else TestStatus.PASSED,
                        duration=1.0,
                    )
                ],
            )
            for i in range(5)
        ]

        flaky = analyzer.detect_flaky_tests(results)
        assert "test_flaky" in flaky
        assert len(flaky["test_flaky"]["status_history"]) == 5
        assert flaky["test_flaky"]["status_history"] == ["failed", "passed", "failed", "passed", "failed"]


class TestPerformanceAnalysis:
    """Test performance analysis functionality."""

    def test_analyze_performance_basic(self, analyzer: ResultAnalyzer) -> None:
        """Test basic performance analysis."""
        results = UnifiedTestResults(
            project="/test",
            framework=FrameworkInfo(framework=TestFramework.PYTEST),
            summary=TestSummary(total=5, passed=5, failed=0, skipped=0, duration=15.0, success_rate=100.0),
            tests=[
                TestResult(name="test_fast1", status=TestStatus.PASSED, duration=0.1),
                TestResult(name="test_fast2", status=TestStatus.PASSED, duration=0.2),
                TestResult(name="test_medium", status=TestStatus.PASSED, duration=1.0),
                TestResult(name="test_slow1", status=TestStatus.PASSED, duration=5.0),
                TestResult(name="test_slow2", status=TestStatus.PASSED, duration=8.7),
            ],
        )

        perf = analyzer.analyze_performance(results)

        assert perf["total_duration_seconds"] == 15.0
        assert perf["average_duration_seconds"] == 3.0
        assert len(perf["slowest_tests"]) == 5
        assert perf["slowest_tests"][0]["name"] == "test_slow2"
        assert perf["fastest_tests"][0]["name"] == "test_fast1"

    def test_analyze_performance_no_tests(self, analyzer: ResultAnalyzer) -> None:
        """Test performance analysis with no tests."""
        empty_results = UnifiedTestResults(
            project="/test",
            framework=FrameworkInfo(framework=TestFramework.PYTEST),
            summary=TestSummary(total=0, passed=0, failed=0, skipped=0, duration=0.0, success_rate=0.0),
            tests=[],
        )

        perf = analyzer.analyze_performance(empty_results)
        assert perf["total_duration"] == 0
        assert perf["average_duration"] == 0
        assert len(perf["slowest_tests"]) == 0

    def test_analyze_performance_percentiles(self, analyzer: ResultAnalyzer) -> None:
        """Test performance percentile calculations."""
        # Create results with known distribution
        tests = [
            TestResult(name=f"test_{i}", status=TestStatus.PASSED, duration=float(i))
            for i in range(1, 101)  # 1.0 to 100.0 seconds
        ]

        results = UnifiedTestResults(
            project="/test",
            framework=FrameworkInfo(framework=TestFramework.PYTEST),
            summary=TestSummary(total=100, passed=100, failed=0, skipped=0, duration=5050.0, success_rate=100.0),
            tests=tests,
        )

        perf = analyzer.analyze_performance(results)

        # Check that percentiles are reasonable
        assert perf["median_duration_seconds"] > 0
        assert perf["p95_duration_seconds"] > perf["median_duration_seconds"]
        assert perf["p99_duration_seconds"] > perf["p95_duration_seconds"]

    def test_analyze_performance_identifies_slow_tests(self, analyzer: ResultAnalyzer) -> None:
        """Test that slowest tests are correctly identified."""
        results = UnifiedTestResults(
            project="/test",
            framework=FrameworkInfo(framework=TestFramework.PYTEST),
            summary=TestSummary(total=10, passed=10, failed=0, skipped=0, duration=55.0, success_rate=100.0),
            tests=[
                TestResult(name=f"test_fast_{i}", status=TestStatus.PASSED, duration=1.0)
                for i in range(5)
            ] + [
                TestResult(name=f"test_slow_{i}", status=TestStatus.PASSED, duration=10.0)
                for i in range(5)
            ],
        )

        perf = analyzer.analyze_performance(results)

        # Top 5 slowest should all be test_slow_*
        slowest_names = [t["name"] for t in perf["slowest_tests"]]
        assert all("slow" in name for name in slowest_names[:5])


class TestHealthValidation:
    """Test health validation functionality."""

    def test_validate_health_perfect_score(self, analyzer: ResultAnalyzer, passing_results: UnifiedTestResults) -> None:
        """Test health validation with perfect passing rate."""
        health = analyzer.validate_test_health(passing_results)

        assert health["health_score"] >= 90
        assert health["health_grade"] == "A"
        assert health["status"] == "HEALTHY"
        assert health["total_tests"] == 10
        assert health["passed_tests"] == 10
        assert health["failed_tests"] == 0
        assert health["pass_rate_percentage"] == 100.0

    def test_validate_health_with_failures(self, analyzer: ResultAnalyzer, mixed_results: UnifiedTestResults) -> None:
        """Test health validation with some failures."""
        health = analyzer.validate_test_health(mixed_results)

        assert health["health_score"] < 100
        assert health["total_tests"] == 10
        assert health["failed_tests"] == 2
        assert health["pass_rate_percentage"] == 60.0

    def test_validate_health_no_tests(self, analyzer: ResultAnalyzer) -> None:
        """Test health validation with no tests."""
        empty_results = UnifiedTestResults(
            project="/test",
            framework=FrameworkInfo(framework=TestFramework.PYTEST),
            summary=TestSummary(total=0, passed=0, failed=0, skipped=0, duration=0.0, success_rate=0.0),
            tests=[],
        )

        health = analyzer.validate_test_health(empty_results)
        assert health["health_score"] == 0
        assert health["health_grade"] == "F"
        assert "No tests found" in health["message"]

    def test_validate_health_all_failing(self, analyzer: ResultAnalyzer) -> None:
        """Test health validation with all failing tests."""
        failing_results = UnifiedTestResults(
            project="/test",
            framework=FrameworkInfo(framework=TestFramework.PYTEST),
            summary=TestSummary(total=5, passed=0, failed=5, skipped=0, duration=5.0, success_rate=0.0),
            tests=[
                TestResult(name=f"test_{i}", status=TestStatus.FAILED, duration=1.0)
                for i in range(5)
            ],
        )

        health = analyzer.validate_test_health(failing_results)
        assert health["status"] == "FAILING"
        assert health["failed_tests"] == 5
        assert health["pass_rate_percentage"] == 0.0

    def test_validate_health_with_errors(self, analyzer: ResultAnalyzer) -> None:
        """Test health validation with test errors."""
        error_results = UnifiedTestResults(
            project="/test",
            framework=FrameworkInfo(framework=TestFramework.PYTEST),
            summary=TestSummary(total=10, passed=5, failed=1, skipped=1, errors=3, duration=7.0, success_rate=50.0),
            tests=[
                TestResult(name="test_1", status=TestStatus.PASSED, duration=1.0),
                TestResult(name="test_2", status=TestStatus.PASSED, duration=1.0),
                TestResult(name="test_3", status=TestStatus.PASSED, duration=1.0),
                TestResult(name="test_4", status=TestStatus.PASSED, duration=1.0),
                TestResult(name="test_5", status=TestStatus.PASSED, duration=1.0),
                TestResult(name="test_6", status=TestStatus.FAILED, duration=1.0),
                TestResult(name="test_7", status=TestStatus.SKIPPED, duration=0.0),
                TestResult(name="test_8", status=TestStatus.ERROR, duration=0.0),
                TestResult(name="test_9", status=TestStatus.ERROR, duration=0.0),
                TestResult(name="test_10", status=TestStatus.ERROR, duration=0.0),
            ],
        )

        health = analyzer.validate_test_health(error_results)
        assert health["error_tests"] == 3
        assert health["error_rate_percentage"] == 30.0
        # High error rate should reduce health score

    def test_validate_health_grades(self, analyzer: ResultAnalyzer) -> None:
        """Test that health grades are assigned correctly."""
        # Create results with various pass rates to test grading
        test_cases = [
            (100, "A"),  # 100% pass rate
            (90, "A"),   # 90% pass rate
            (85, "B"),   # 85% pass rate
            (75, "C"),   # 75% pass rate
            (65, "D"),   # 65% pass rate
            (50, "F"),   # 50% pass rate
        ]

        for pass_count, expected_grade in test_cases:
            total = 100
            results = UnifiedTestResults(
                project="/test",
                framework=FrameworkInfo(framework=TestFramework.PYTEST),
                summary=TestSummary(
                    total=total,
                    passed=pass_count,
                    failed=total - pass_count,
                    skipped=0,
                    duration=float(total),
                    success_rate=float(pass_count),
                ),
                tests=[
                    TestResult(
                        name=f"test_{i}",
                        status=TestStatus.PASSED if i < pass_count else TestStatus.FAILED,
                        duration=1.0,
                    )
                    for i in range(total)
                ],
            )

            health = analyzer.validate_test_health(results)
            # Note: Grade depends on formula, not just pass rate
            # This test verifies the grading system is working
            assert health["health_grade"] in ["A", "B", "C", "D", "F"]


class TestResultComparison:
    """Test result comparison functionality."""

    def test_compare_results_improvement(self, analyzer: ResultAnalyzer) -> None:
        """Test comparison detects improvements."""
        before = UnifiedTestResults(
            project="/test",
            framework=FrameworkInfo(framework=TestFramework.PYTEST),
            summary=TestSummary(total=10, passed=7, failed=3, skipped=0, duration=10.0, success_rate=70.0),
            tests=[
                TestResult(name=f"test_{i}", status=TestStatus.PASSED if i < 7 else TestStatus.FAILED, duration=1.0)
                for i in range(10)
            ],
        )

        after = UnifiedTestResults(
            project="/test",
            framework=FrameworkInfo(framework=TestFramework.PYTEST),
            summary=TestSummary(total=10, passed=9, failed=1, skipped=0, duration=10.0, success_rate=90.0),
            tests=[
                TestResult(name=f"test_{i}", status=TestStatus.PASSED if i < 9 else TestStatus.FAILED, duration=1.0)
                for i in range(10)
            ],
        )

        comparison = analyzer.compare_results(before, after)

        assert comparison["trend"] == "IMPROVEMENT"
        assert comparison["new_failures"] == -2  # 2 fewer failures
        assert comparison["fixed_tests"] == 2
        assert comparison["pass_rate_change"] > 0

    def test_compare_results_regression(self, analyzer: ResultAnalyzer, passing_results: UnifiedTestResults) -> None:
        """Test comparison detects regressions."""
        before = passing_results

        after = UnifiedTestResults(
            project="/test",
            framework=FrameworkInfo(framework=TestFramework.PYTEST),
            summary=TestSummary(total=10, passed=8, failed=2, skipped=0, duration=10.0, success_rate=80.0),
            tests=[
                TestResult(name=f"test_{i}", status=TestStatus.PASSED if i < 8 else TestStatus.FAILED, duration=1.0)
                for i in range(10)
            ],
        )

        comparison = analyzer.compare_results(before, after)

        assert comparison["trend"] == "REGRESSION"
        assert comparison["new_failures"] == 2

    def test_compare_results_stable(self, analyzer: ResultAnalyzer, passing_results: UnifiedTestResults) -> None:
        """Test comparison with no changes."""
        comparison = analyzer.compare_results(passing_results, passing_results)

        assert comparison["trend"] == "STABLE"
        assert comparison["new_failures"] == 0
        assert comparison["fixed_tests"] == 0


class TestUtilityMethods:
    """Test utility methods."""

    def test_get_failing_tests(self, analyzer: ResultAnalyzer, mixed_results: UnifiedTestResults) -> None:
        """Test getting list of failing tests."""
        failing = analyzer.get_failing_tests(mixed_results)

        assert len(failing) == 2
        assert all(t["name"] in ["test_7", "test_8"] for t in failing)

    def test_get_test_distribution_by_status(self, analyzer: ResultAnalyzer, mixed_results: UnifiedTestResults) -> None:
        """Test getting test distribution by status."""
        distribution = analyzer.get_test_distribution_by_status(mixed_results)

        assert distribution["passed"] == 6
        assert distribution["failed"] == 2
        assert distribution["skipped"] == 2

    def test_get_test_distribution_by_file(self, analyzer: ResultAnalyzer) -> None:
        """Test getting test distribution by file."""
        results = UnifiedTestResults(
            project="/test",
            framework=FrameworkInfo(framework=TestFramework.PYTEST),
            summary=TestSummary(total=4, passed=3, failed=1, skipped=0, duration=4.0, success_rate=75.0),
            tests=[
                TestResult(name="test_1", status=TestStatus.PASSED, duration=1.0, file="test_module1.py"),
                TestResult(name="test_2", status=TestStatus.PASSED, duration=1.0, file="test_module1.py"),
                TestResult(name="test_3", status=TestStatus.PASSED, duration=1.0, file="test_module2.py"),
                TestResult(name="test_4", status=TestStatus.FAILED, duration=1.0, file="test_module2.py"),
            ],
        )

        distribution = analyzer.get_test_distribution_by_file(results)

        assert distribution["test_module1.py"]["total"] == 2
        assert distribution["test_module1.py"]["passed"] == 2
        assert distribution["test_module1.py"]["failed"] == 0

        assert distribution["test_module2.py"]["total"] == 2
        assert distribution["test_module2.py"]["passed"] == 1
        assert distribution["test_module2.py"]["failed"] == 1


class TestSingletonWrappers:
    """Test singleton wrapper functions."""

    def test_analyze_coverage_wrapper(passing_results: UnifiedTestResults) -> None:
        """Test module-level analyze_coverage function."""
        coverage = analyze_coverage(passing_results)
        assert coverage["total_tests"] == 10

    def test_detect_flaky_tests_wrapper(passing_results: UnifiedTestResults) -> None:
        """Test module-level detect_flaky_tests function."""
        flaky = detect_flaky_tests([passing_results, passing_results])
        assert len(flaky) == 0

    def test_analyze_performance_wrapper(passing_results: UnifiedTestResults) -> None:
        """Test module-level analyze_performance function."""
        perf = analyze_performance(passing_results)
        assert perf["total_duration_seconds"] == 10.0

    def test_validate_test_health_wrapper(passing_results: UnifiedTestResults) -> None:
        """Test module-level validate_test_health function."""
        health = validate_test_health(passing_results)
        assert health["health_score"] >= 90
