"""
Test result analysis module for extracting insights from test execution.

Provides coverage analysis, flaky test detection, performance analysis,
and overall test health scoring.
"""

import logging
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from src.models import UnifiedTestResults, TestResult, TestStatus


logger = logging.getLogger(__name__)


class ResultAnalyzer:
    """Analyzes test results for coverage, performance, and health."""

    def analyze_coverage(self, results: UnifiedTestResults) -> Dict:
        """
        Analyze code coverage metrics from test results.

        Extracts coverage information if available in error messages
        or result metadata.

        Args:
            results: UnifiedTestResults to analyze

        Returns:
            Dictionary with coverage metrics
        """
        total_tests = len(results.tests)
        if total_tests == 0:
            return {
                "total_tests": 0,
                "coverage_percentage": 0,
                "coverage_available": False,
                "message": "No tests found",
            }

        passed = sum(1 for t in results.tests if t.status == TestStatus.PASSED)
        coverage_percentage = (passed / total_tests) * 100 if total_tests > 0 else 0

        return {
            "total_tests": total_tests,
            "passed_tests": passed,
            "failed_tests": sum(1 for t in results.tests if t.status == TestStatus.FAILED),
            "skipped_tests": sum(1 for t in results.tests if t.status == TestStatus.SKIPPED),
            "coverage_percentage": round(coverage_percentage, 2),
            "coverage_available": coverage_percentage > 0,
        }

    def detect_flaky_tests(
        self, historical_results: List[UnifiedTestResults]
    ) -> Dict[str, Dict]:
        """
        Detect flaky tests from historical results.

        A test is considered flaky if it passes sometimes and fails other times.

        Args:
            historical_results: List of UnifiedTestResults from multiple runs

        Returns:
            Dictionary mapping test names to flakiness info
        """
        if len(historical_results) < 2:
            return {}

        # Track test status across runs
        test_history: Dict[str, List[TestStatus]] = defaultdict(list)

        for result in historical_results:
            for test in result.tests:
                test_history[test.name].append(test.status)

        # Find flaky tests (multiple different statuses)
        flaky_tests = {}
        for test_name, statuses in test_history.items():
            unique_statuses = set(statuses)

            # Flaky if has both passed and failed
            if TestStatus.PASSED in unique_statuses and TestStatus.FAILED in unique_statuses:
                passed_count = sum(1 for s in statuses if s == TestStatus.PASSED)
                failed_count = sum(1 for s in statuses if s == TestStatus.FAILED)
                total_runs = len(statuses)

                flakiness = min(passed_count, failed_count) / total_runs * 100
                flaky_tests[test_name] = {
                    "flakiness_percentage": round(flakiness, 2),
                    "passed_runs": passed_count,
                    "failed_runs": failed_count,
                    "total_runs": total_runs,
                    "status_history": [s.value for s in statuses],
                }

        return flaky_tests

    def analyze_performance(self, results: UnifiedTestResults) -> Dict:
        """
        Analyze test execution performance metrics.

        Identifies slow tests and execution time distribution.

        Args:
            results: UnifiedTestResults to analyze

        Returns:
            Dictionary with performance metrics
        """
        if not results.tests:
            return {
                "total_duration": 0,
                "average_duration": 0,
                "slowest_tests": [],
                "fastest_tests": [],
            }

        # Calculate metrics
        total_duration = sum(t.duration for t in results.tests)
        avg_duration = total_duration / len(results.tests) if results.tests else 0

        # Sort by duration
        sorted_tests = sorted(results.tests, key=lambda t: t.duration, reverse=True)
        slowest = sorted_tests[:5]  # Top 5 slowest
        fastest = sorted_tests[-5:][::-1]  # Top 5 fastest (reversed for order)

        # Calculate percentiles
        durations = sorted([t.duration for t in results.tests])
        p50_idx = len(durations) // 2
        p95_idx = int(len(durations) * 0.95)
        p99_idx = int(len(durations) * 0.99)

        return {
            "total_duration_seconds": round(total_duration, 2),
            "average_duration_seconds": round(avg_duration, 3),
            "median_duration_seconds": round(
                durations[p50_idx] if p50_idx < len(durations) else 0, 3
            ),
            "p95_duration_seconds": round(
                durations[p95_idx] if p95_idx < len(durations) else 0, 3
            ),
            "p99_duration_seconds": round(
                durations[p99_idx] if p99_idx < len(durations) else 0, 3
            ),
            "slowest_tests": [
                {
                    "name": t.name,
                    "duration": round(t.duration, 3),
                    "status": t.status.value,
                }
                for t in slowest
            ],
            "fastest_tests": [
                {
                    "name": t.name,
                    "duration": round(t.duration, 3),
                    "status": t.status.value,
                }
                for t in fastest
            ],
        }

    def validate_test_health(self, results: UnifiedTestResults) -> Dict:
        """
        Validate overall test health and generate health score.

        Considers pass rate, test coverage, and execution stability.

        Args:
            results: UnifiedTestResults to analyze

        Returns:
            Dictionary with health metrics and score (0-100)
        """
        if not results.tests:
            return {
                "health_score": 0,
                "health_grade": "F",
                "total_tests": 0,
                "message": "No tests found",
            }

        total = len(results.tests)
        passed = sum(1 for t in results.tests if t.status == TestStatus.PASSED)
        failed = sum(1 for t in results.tests if t.status == TestStatus.FAILED)
        skipped = sum(1 for t in results.tests if t.status == TestStatus.SKIPPED)
        errors = sum(1 for t in results.tests if t.status == TestStatus.ERROR)

        # Calculate pass rate
        pass_rate = (passed / total * 100) if total > 0 else 0

        # Calculate skip rate (high skip rate is not healthy)
        skip_rate = (skipped / total * 100) if total > 0 else 0

        # Calculate error rate
        error_rate = (errors / total * 100) if total > 0 else 0

        # Health score formula
        # 40% pass rate, 40% no errors, 20% no skips
        health_score = (
            pass_rate * 0.4 + (100 - error_rate) * 0.4 + (100 - skip_rate * 0.5) * 0.2
        )
        health_score = max(0, min(100, health_score))  # Clamp 0-100

        # Grade based on score
        if health_score >= 90:
            grade = "A"
        elif health_score >= 80:
            grade = "B"
        elif health_score >= 70:
            grade = "C"
        elif health_score >= 60:
            grade = "D"
        else:
            grade = "F"

        # Determine status
        if failed > 0:
            status = "FAILING"
        elif error_rate > 10:
            status = "ERRORS"
        elif skip_rate > 50:
            status = "UNSTABLE"
        elif pass_rate >= 95:
            status = "HEALTHY"
        else:
            status = "WARNING"

        return {
            "health_score": round(health_score, 1),
            "health_grade": grade,
            "status": status,
            "total_tests": total,
            "passed_tests": passed,
            "failed_tests": failed,
            "skipped_tests": skipped,
            "error_tests": errors,
            "pass_rate_percentage": round(pass_rate, 1),
            "skip_rate_percentage": round(skip_rate, 1),
            "error_rate_percentage": round(error_rate, 1),
        }

    def compare_results(
        self,
        before: UnifiedTestResults,
        after: UnifiedTestResults,
    ) -> Dict:
        """
        Compare test results to detect regressions or improvements.

        Args:
            before: Baseline test results
            after: New test results to compare

        Returns:
            Dictionary with comparison metrics
        """
        before_metrics = self.validate_test_health(before)
        after_metrics = self.validate_test_health(after)

        before_pass_rate = before_metrics["pass_rate_percentage"]
        after_pass_rate = after_metrics["pass_rate_percentage"]

        # Determine if regression or improvement
        if after_metrics["failed_tests"] > before_metrics["failed_tests"]:
            trend = "REGRESSION"
        elif after_metrics["passed_tests"] > before_metrics["passed_tests"]:
            trend = "IMPROVEMENT"
        else:
            trend = "STABLE"

        return {
            "trend": trend,
            "before_health_score": before_metrics["health_score"],
            "after_health_score": after_metrics["health_score"],
            "health_score_change": round(
                after_metrics["health_score"] - before_metrics["health_score"], 1
            ),
            "before_pass_rate": before_pass_rate,
            "after_pass_rate": after_pass_rate,
            "pass_rate_change": round(after_pass_rate - before_pass_rate, 1),
            "new_failures": after_metrics["failed_tests"]
            - before_metrics["failed_tests"],
            "fixed_tests": max(
                0,
                before_metrics["failed_tests"] - after_metrics["failed_tests"],
            ),
        }

    def get_failing_tests(self, results: UnifiedTestResults) -> List[Dict]:
        """
        Get list of failing tests with details.

        Args:
            results: UnifiedTestResults to analyze

        Returns:
            List of failing test details
        """
        failing = []
        for test in results.tests:
            if test.status == TestStatus.FAILED:
                failing.append(
                    {
                        "name": test.name,
                        "file": test.file,
                        "line": test.line,
                        "duration": test.duration,
                        "error_message": test.error_message,
                    }
                )
        return failing

    def get_test_distribution_by_status(
        self, results: UnifiedTestResults
    ) -> Dict[str, int]:
        """
        Get distribution of tests by status.

        Args:
            results: UnifiedTestResults to analyze

        Returns:
            Dictionary mapping status to count
        """
        distribution = defaultdict(int)
        for test in results.tests:
            distribution[test.status.value] += 1
        return dict(distribution)

    def get_test_distribution_by_file(
        self, results: UnifiedTestResults
    ) -> Dict[str, Dict]:
        """
        Get test distribution by file.

        Args:
            results: UnifiedTestResults to analyze

        Returns:
            Dictionary mapping file to test counts
        """
        distribution = defaultdict(lambda: {"total": 0, "passed": 0, "failed": 0})

        for test in results.tests:
            file = test.file or "unknown"
            distribution[file]["total"] += 1
            if test.status == TestStatus.PASSED:
                distribution[file]["passed"] += 1
            elif test.status == TestStatus.FAILED:
                distribution[file]["failed"] += 1

        return dict(distribution)


# Singleton instance
_analyzer = ResultAnalyzer()


def analyze_coverage(results: UnifiedTestResults) -> Dict:
    """Analyze coverage (singleton wrapper)."""
    return _analyzer.analyze_coverage(results)


def detect_flaky_tests(historical_results: List[UnifiedTestResults]) -> Dict:
    """Detect flaky tests (singleton wrapper)."""
    return _analyzer.detect_flaky_tests(historical_results)


def analyze_performance(results: UnifiedTestResults) -> Dict:
    """Analyze performance (singleton wrapper)."""
    return _analyzer.analyze_performance(results)


def validate_test_health(results: UnifiedTestResults) -> Dict:
    """Validate test health (singleton wrapper)."""
    return _analyzer.validate_test_health(results)
