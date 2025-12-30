"""Comprehensive unit tests for test_aggregator.py - Phase 3: Result Processing & Analysis.

Tests result aggregation, archival, export, comparison, and history tracking.
"""

import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Generator
import pytest

from src.test_aggregator import TestAggregator, aggregate_results, archive_results
from src.models import (
    UnifiedTestResults,
    FrameworkInfo,
    TestSummary,
    TestResult,
    TestStatus,
    TestFramework,
)


@pytest.fixture
def temp_archive_dir() -> Generator[Path, None, None]:
    """Create temporary archive directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def aggregator(temp_archive_dir: Path) -> TestAggregator:
    """Create aggregator with temporary archive directory."""
    return TestAggregator(archive_dir=str(temp_archive_dir))


@pytest.fixture
def sample_test_results() -> UnifiedTestResults:
    """Create sample test results for testing."""
    return UnifiedTestResults(
        project="/test/project",
        framework=FrameworkInfo(framework=TestFramework.PYTEST),
        summary=TestSummary(
            total=5,
            passed=4,
            failed=1,
            skipped=0,
            duration=5.0,
            success_rate=80.0,
        ),
        tests=[
            TestResult(name="test_1", status=TestStatus.PASSED, duration=1.0),
            TestResult(name="test_2", status=TestStatus.PASSED, duration=1.0),
            TestResult(name="test_3", status=TestStatus.PASSED, duration=1.0),
            TestResult(name="test_4", status=TestStatus.PASSED, duration=1.0),
            TestResult(name="test_5", status=TestStatus.FAILED, duration=1.0, error_message="AssertionError"),
        ],
    )


class TestAggregation:
    """Test result aggregation functionality."""

    def test_aggregate_single_result(self, aggregator: TestAggregator, sample_test_results: UnifiedTestResults) -> None:
        """Test aggregating a single result returns it unchanged."""
        aggregated = aggregator.aggregate_results([sample_test_results])
        assert aggregated.summary.get("total") == 5
        assert aggregated.summary.get("passed") == 4
        assert aggregated.summary.get("failed") == 1
        assert len(aggregated.tests) == 5

    def test_aggregate_multiple_results(self, aggregator: TestAggregator) -> None:
        """Test aggregating multiple test results."""
        results1 = UnifiedTestResults(
            project="/test/project",
            framework=FrameworkInfo(framework=TestFramework.PYTEST),
            summary=TestSummary(
                total=3, passed=2, failed=1, skipped=0, duration=3.0, success_rate=66.7
            ),
            tests=[
                TestResult(name="test_1", status=TestStatus.PASSED, duration=1.0),
                TestResult(name="test_2", status=TestStatus.PASSED, duration=1.0),
                TestResult(name="test_3", status=TestStatus.FAILED, duration=1.0),
            ],
        )

        results2 = UnifiedTestResults(
            project="/test/project",
            framework=FrameworkInfo(framework=TestFramework.JEST),
            summary=TestSummary(
                total=4, passed=3, failed=0, skipped=1, duration=4.0, success_rate=100.0
            ),
            tests=[
                TestResult(name="test_a", status=TestStatus.PASSED, duration=1.0),
                TestResult(name="test_b", status=TestStatus.PASSED, duration=1.0),
                TestResult(name="test_c", status=TestStatus.PASSED, duration=1.0),
                TestResult(name="test_d", status=TestStatus.SKIPPED, duration=0.0),
            ],
        )

        aggregated = aggregator.aggregate_results([results1, results2])

        # Total should be sum of all tests
        assert aggregated.summary.get("total") == 7
        assert aggregated.summary.get("passed") == 5
        assert aggregated.summary.get("failed") == 1
        assert aggregated.summary.get("skipped") == 1
        assert len(aggregated.tests) == 7

    def test_aggregate_empty_list(self, aggregator: TestAggregator) -> None:
        """Test aggregating empty list returns empty result."""
        aggregated = aggregator.aggregate_results([])
        assert aggregated.summary.get("total") == 0
        assert aggregated.summary.get("passed") == 0
        assert aggregated.summary.get("failed") == 0
        assert len(aggregated.tests) == 0

    def test_aggregate_with_optional_fields(self, aggregator: TestAggregator) -> None:
        """Test aggregation includes optional fields like errors, xfail, xpass."""
        results = UnifiedTestResults(
            project="/test/project",
            framework=FrameworkInfo(framework=TestFramework.PYTEST),
            summary=TestSummary(
                total=7,
                passed=3,
                failed=1,
                skipped=1,
                errors=1,
                xfail=1,
                xpass=0,
                duration=7.0,
                success_rate=60.0,
            ),
            tests=[
                TestResult(name="test_1", status=TestStatus.PASSED, duration=1.0),
                TestResult(name="test_2", status=TestStatus.PASSED, duration=1.0),
                TestResult(name="test_3", status=TestStatus.PASSED, duration=1.0),
                TestResult(name="test_4", status=TestStatus.FAILED, duration=1.0),
                TestResult(name="test_5", status=TestStatus.SKIPPED, duration=0.0),
                TestResult(name="test_6", status=TestStatus.ERROR, duration=0.0),
                TestResult(name="test_7", status=TestStatus.XFAIL, duration=1.0),
            ],
        )

        aggregated = aggregator.aggregate_results([results])
        assert aggregated.summary.get("error") == 1
        assert aggregated.summary.get("xfail") == 1


class TestArchival:
    """Test result archival functionality."""

    def test_archive_results(
        self, aggregator: TestAggregator, sample_test_results: UnifiedTestResults, temp_archive_dir: Path
    ) -> None:
        """Test archiving test results."""
        archive_path = aggregator.archive_results(sample_test_results)

        assert archive_path.exists()
        assert archive_path.parent == temp_archive_dir

        # Verify archived content
        data = json.loads(archive_path.read_text())
        assert data["project"] == "/test/project"
        assert data["framework"] == "pytest"
        assert data["summary"]["total"] == 5
        assert len(data["tests"]) == 5

    def test_archive_with_custom_timestamp(
        self, aggregator: TestAggregator, sample_test_results: UnifiedTestResults
    ) -> None:
        """Test archiving with custom timestamp."""
        custom_time = datetime(2025, 1, 1, 12, 0, 0)
        archive_path = aggregator.archive_results(sample_test_results, timestamp=custom_time)

        assert archive_path.exists()
        assert "2025-01-01T12-00-00" in archive_path.name

    def test_archive_with_run_name(
        self, aggregator: TestAggregator, sample_test_results: UnifiedTestResults
    ) -> None:
        """Test archiving with run name."""
        archive_path = aggregator.archive_results(sample_test_results, run_name="ci-build-123")

        assert archive_path.exists()
        assert "ci-build-123" in archive_path.name

        # Verify run name in archived data
        data = json.loads(archive_path.read_text())
        assert data["run_name"] == "ci-build-123"

    def test_archive_preserves_error_details(
        self, aggregator: TestAggregator
    ) -> None:
        """Test that archival preserves error messages and details."""
        results = UnifiedTestResults(
            project="/test/project",
            framework=FrameworkInfo(framework=TestFramework.PYTEST),
            summary=TestSummary(
                total=1, passed=0, failed=1, skipped=0, duration=1.0, success_rate=0.0
            ),
            tests=[
                TestResult(
                    name="test_failing",
                    status=TestStatus.FAILED,
                    duration=1.0,
                    file="test_module.py",
                    line=42,
                    error_message="AssertionError: expected 1, got 2",
                )
            ],
        )

        archive_path = aggregator.archive_results(results)
        data = json.loads(archive_path.read_text())

        test_data = data["tests"][0]
        assert test_data["name"] == "test_failing"
        assert test_data["status"] == "failed"
        assert test_data["error_message"] == "AssertionError: expected 1, got 2"
        assert test_data["file"] == "test_module.py"
        assert test_data["line"] == 42


class TestRetrievingArchivedResults:
    """Test retrieving archived results."""

    def test_get_archived_results_all(
        self, aggregator: TestAggregator, sample_test_results: UnifiedTestResults
    ) -> None:
        """Test retrieving all archived results."""
        # Archive multiple results
        aggregator.archive_results(sample_test_results, run_name="run1")
        aggregator.archive_results(sample_test_results, run_name="run2")

        results = aggregator.get_archived_results()
        assert len(results) >= 2

    def test_get_archived_results_by_framework(
        self, aggregator: TestAggregator
    ) -> None:
        """Test filtering archived results by framework."""
        pytest_results = UnifiedTestResults(
            project="/test",
            framework=FrameworkInfo(framework=TestFramework.PYTEST),
            summary=TestSummary(total=1, passed=1, failed=0, skipped=0, duration=1.0, success_rate=100.0),
            tests=[TestResult(name="test_1", status=TestStatus.PASSED, duration=1.0)],
        )

        jest_results = UnifiedTestResults(
            project="/test",
            framework=FrameworkInfo(framework=TestFramework.JEST),
            summary=TestSummary(total=1, passed=1, failed=0, skipped=0, duration=1.0, success_rate=100.0),
            tests=[TestResult(name="test_a", status=TestStatus.PASSED, duration=1.0)],
        )

        aggregator.archive_results(pytest_results)
        aggregator.archive_results(jest_results)

        pytest_archived = aggregator.get_archived_results(framework="pytest")
        jest_archived = aggregator.get_archived_results(framework="jest")

        assert all(r["framework"] == "pytest" for r in pytest_archived)
        assert all(r["framework"] == "jest" for r in jest_archived)

    def test_get_latest_result(
        self, aggregator: TestAggregator, sample_test_results: UnifiedTestResults
    ) -> None:
        """Test retrieving latest archived result."""
        aggregator.archive_results(sample_test_results, run_name="old")
        import time
        time.sleep(0.01)  # Small delay to ensure different timestamps
        aggregator.archive_results(sample_test_results, run_name="new")

        latest = aggregator.get_latest_result()
        assert latest is not None
        assert latest["run_name"] == "new"

    def test_get_latest_result_empty(self, aggregator: TestAggregator) -> None:
        """Test getting latest result when no archives exist."""
        latest = aggregator.get_latest_result()
        assert latest is None


class TestComparison:
    """Test result comparison functionality."""

    def test_compare_results_basic(self, aggregator: TestAggregator) -> None:
        """Test basic result comparison."""
        result1 = UnifiedTestResults(
            project="/test",
            framework=FrameworkInfo(framework=TestFramework.PYTEST),
            summary=TestSummary(total=10, passed=8, failed=2, skipped=0, duration=10.0, success_rate=80.0),
            tests=[
                TestResult(name=f"test_{i}", status=TestStatus.PASSED if i < 8 else TestStatus.FAILED, duration=1.0)
                for i in range(10)
            ],
        )

        result2 = UnifiedTestResults(
            project="/test",
            framework=FrameworkInfo(framework=TestFramework.PYTEST),
            summary=TestSummary(total=10, passed=9, failed=1, skipped=0, duration=10.0, success_rate=90.0),
            tests=[
                TestResult(name=f"test_{i}", status=TestStatus.PASSED if i < 9 else TestStatus.FAILED, duration=1.0)
                for i in range(10)
            ],
        )

        comparison = aggregator.compare_results(result1, result2)

        assert comparison["total_change"] == 0  # Same number of tests
        assert comparison["passed_change"] == 1  # One more passed
        assert comparison["failed_change"] == -1  # One fewer failed
        assert comparison["improvement"] is True

    def test_compare_detects_regression(self, aggregator: TestAggregator) -> None:
        """Test that comparison detects regressions."""
        result1 = UnifiedTestResults(
            project="/test",
            framework=FrameworkInfo(framework=TestFramework.PYTEST),
            summary=TestSummary(total=5, passed=5, failed=0, skipped=0, duration=5.0, success_rate=100.0),
            tests=[TestResult(name=f"test_{i}", status=TestStatus.PASSED, duration=1.0) for i in range(5)],
        )

        result2 = UnifiedTestResults(
            project="/test",
            framework=FrameworkInfo(framework=TestFramework.PYTEST),
            summary=TestSummary(total=5, passed=3, failed=2, skipped=0, duration=5.0, success_rate=60.0),
            tests=[
                TestResult(name="test_0", status=TestStatus.PASSED, duration=1.0),
                TestResult(name="test_1", status=TestStatus.PASSED, duration=1.0),
                TestResult(name="test_2", status=TestStatus.PASSED, duration=1.0),
                TestResult(name="test_3", status=TestStatus.FAILED, duration=1.0),
                TestResult(name="test_4", status=TestStatus.FAILED, duration=1.0),
            ],
        )

        comparison = aggregator.compare_results(result1, result2)
        assert comparison["regression"] is True

    def test_compare_tracks_status_changes(self, aggregator: TestAggregator) -> None:
        """Test that comparison tracks individual test status changes."""
        result1 = UnifiedTestResults(
            project="/test",
            framework=FrameworkInfo(framework=TestFramework.PYTEST),
            summary=TestSummary(total=3, passed=2, failed=1, skipped=0, duration=3.0, success_rate=66.7),
            tests=[
                TestResult(name="test_a", status=TestStatus.PASSED, duration=1.0),
                TestResult(name="test_b", status=TestStatus.FAILED, duration=1.0),
                TestResult(name="test_c", status=TestStatus.PASSED, duration=1.0),
            ],
        )

        result2 = UnifiedTestResults(
            project="/test",
            framework=FrameworkInfo(framework=TestFramework.PYTEST),
            summary=TestSummary(total=3, passed=2, failed=1, skipped=0, duration=3.0, success_rate=66.7),
            tests=[
                TestResult(name="test_a", status=TestStatus.FAILED, duration=1.0),  # Changed to failed
                TestResult(name="test_b", status=TestStatus.PASSED, duration=1.0),  # Changed to passed
                TestResult(name="test_c", status=TestStatus.PASSED, duration=1.0),
            ],
        )

        comparison = aggregator.compare_results(result1, result2)
        assert len(comparison["status_changes"]) == 2
        assert "test_a" in comparison["status_changes"]
        assert "test_b" in comparison["status_changes"]

    def test_compare_detects_new_and_removed_tests(self, aggregator: TestAggregator) -> None:
        """Test comparison detects new and removed tests."""
        result1 = UnifiedTestResults(
            project="/test",
            framework=FrameworkInfo(framework=TestFramework.PYTEST),
            summary=TestSummary(total=2, passed=2, failed=0, skipped=0, duration=2.0, success_rate=100.0),
            tests=[
                TestResult(name="test_a", status=TestStatus.PASSED, duration=1.0),
                TestResult(name="test_b", status=TestStatus.PASSED, duration=1.0),
            ],
        )

        result2 = UnifiedTestResults(
            project="/test",
            framework=FrameworkInfo(framework=TestFramework.PYTEST),
            summary=TestSummary(total=2, passed=2, failed=0, skipped=0, duration=2.0, success_rate=100.0),
            tests=[
                TestResult(name="test_b", status=TestStatus.PASSED, duration=1.0),
                TestResult(name="test_c", status=TestStatus.PASSED, duration=1.0),  # New test
            ],
        )

        comparison = aggregator.compare_results(result1, result2)
        assert "test_c" in comparison["new_tests"]
        assert "test_a" in comparison["removed_tests"]


class TestExport:
    """Test result export functionality."""

    def test_export_json(
        self, aggregator: TestAggregator, sample_test_results: UnifiedTestResults, temp_archive_dir: Path
    ) -> None:
        """Test exporting results to JSON."""
        export_path = temp_archive_dir / "export.json"
        result_path = aggregator.export_results(sample_test_results, str(export_path), format="json")

        assert result_path.exists()
        data = json.loads(result_path.read_text())
        assert data["framework"] == "pytest"
        assert data["summary"]["total"] == 5
        assert len(data["tests"]) == 5

    def test_export_csv(
        self, aggregator: TestAggregator, sample_test_results: UnifiedTestResults, temp_archive_dir: Path
    ) -> None:
        """Test exporting results to CSV."""
        export_path = temp_archive_dir / "export.csv"
        result_path = aggregator.export_results(sample_test_results, str(export_path), format="csv")

        assert result_path.exists()
        content = result_path.read_text()
        assert "test_name,status,duration_seconds,file,line" in content
        assert "test_1,passed" in content

    def test_export_html(
        self, aggregator: TestAggregator, sample_test_results: UnifiedTestResults, temp_archive_dir: Path
    ) -> None:
        """Test exporting results to HTML."""
        export_path = temp_archive_dir / "export.html"
        result_path = aggregator.export_results(sample_test_results, str(export_path), format="html")

        assert result_path.exists()
        content = result_path.read_text()
        assert "<!DOCTYPE html>" in content
        assert "test_1" in content
        assert "passed" in content.lower()

    def test_export_creates_parent_directory(
        self, aggregator: TestAggregator, sample_test_results: UnifiedTestResults, temp_archive_dir: Path
    ) -> None:
        """Test that export creates parent directories if they don't exist."""
        export_path = temp_archive_dir / "subdir" / "nested" / "export.json"
        result_path = aggregator.export_results(sample_test_results, str(export_path), format="json")

        assert result_path.exists()
        assert result_path.parent.parent.name == "subdir"

    def test_export_invalid_format_raises_error(
        self, aggregator: TestAggregator, sample_test_results: UnifiedTestResults, temp_archive_dir: Path
    ) -> None:
        """Test that unsupported export format raises ValueError."""
        export_path = temp_archive_dir / "export.xml"
        with pytest.raises(ValueError, match="Unsupported export format"):
            aggregator.export_results(sample_test_results, str(export_path), format="xml")


class TestHistory:
    """Test result history tracking."""

    def test_get_result_history(
        self, aggregator: TestAggregator, sample_test_results: UnifiedTestResults
    ) -> None:
        """Test retrieving result history."""
        for i in range(5):
            aggregator.archive_results(sample_test_results, run_name=f"run{i}")

        history = aggregator.get_result_history(limit=3)
        assert len(history) == 3
        assert all("run_name" in h for h in history)
        assert all("summary" in h for h in history)

    def test_history_sorted_by_date(
        self, aggregator: TestAggregator, sample_test_results: UnifiedTestResults
    ) -> None:
        """Test that history is sorted by date (newest first)."""
        import time
        for i in range(3):
            aggregator.archive_results(sample_test_results, run_name=f"run{i}")
            time.sleep(0.01)  # Small delay

        history = aggregator.get_result_history()
        # Most recent should be run2
        assert history[0]["run_name"] == "run2"


class TestCleanup:
    """Test archive cleanup functionality."""

    def test_cleanup_old_archives(
        self, aggregator: TestAggregator, sample_test_results: UnifiedTestResults
    ) -> None:
        """Test cleaning up old archived results."""
        # Archive a result
        archive_path = aggregator.archive_results(sample_test_results)

        # Manually set file modification time to 31 days ago
        import os
        old_time = (datetime.utcnow() - timedelta(days=31)).timestamp()
        os.utime(archive_path, (old_time, old_time))

        # Cleanup archives older than 30 days
        deleted = aggregator.cleanup_old_archives(keep_days=30)
        assert deleted == 1
        assert not archive_path.exists()

    def test_cleanup_keeps_recent_archives(
        self, aggregator: TestAggregator, sample_test_results: UnifiedTestResults
    ) -> None:
        """Test that cleanup keeps recent archives."""
        archive_path = aggregator.archive_results(sample_test_results)

        # Cleanup archives older than 30 days (this archive is fresh)
        deleted = aggregator.cleanup_old_archives(keep_days=30)
        assert deleted == 0
        assert archive_path.exists()


class TestSingletonWrappers:
    """Test singleton wrapper functions."""

    def test_aggregate_results_wrapper() -> None:
        """Test module-level aggregate_results function."""
        results = UnifiedTestResults(
            project="/test",
            framework=FrameworkInfo(framework=TestFramework.PYTEST),
            summary=TestSummary(total=1, passed=1, failed=0, skipped=0, duration=1.0, success_rate=100.0),
            tests=[TestResult(name="test_1", status=TestStatus.PASSED, duration=1.0)],
        )

        aggregated = aggregate_results([results])
        assert aggregated.summary.get("total") == 1

    def test_archive_results_wrapper(temp_archive_dir: Path) -> None:
        """Test module-level archive_results function."""
        results = UnifiedTestResults(
            project="/test",
            framework=FrameworkInfo(framework=TestFramework.PYTEST),
            summary=TestSummary(total=1, passed=1, failed=0, skipped=0, duration=1.0, success_rate=100.0),
            tests=[TestResult(name="test_1", status=TestStatus.PASSED, duration=1.0)],
        )

        # Note: singleton uses default archive dir, so we can't easily control it
        # This test just verifies the function works
        archive_path = archive_results(results)
        assert archive_path.exists()
