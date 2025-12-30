"""Comprehensive unit tests for models.py - Phase 1: Setup & Architecture.

Tests all Pydantic models, enums, validation, and schema constraints.
"""

from datetime import datetime
from typing import Any, Dict
import pytest
from pydantic import ValidationError

from src.models import (
    TestStatus,
    TestFramework,
    FrameworkInfo,
    TestResult,
    TestSummary,
    CoverageInfo,
    UnifiedTestResults,
    FrameworkDetectionResult,
    TestRunRequest,
    TestAnalysisResult,
)


class TestEnums:
    """Test enum definitions."""

    def test_test_status_values(self) -> None:
        """Test TestStatus enum has correct values."""
        assert TestStatus.PASSED.value == "passed"
        assert TestStatus.FAILED.value == "failed"
        assert TestStatus.SKIPPED.value == "skipped"
        assert TestStatus.ERROR.value == "error"
        assert TestStatus.XFAIL.value == "xfail"
        assert TestStatus.XPASS.value == "xpass"

    def test_test_framework_values(self) -> None:
        """Test TestFramework enum has correct values."""
        assert TestFramework.PYTEST.value == "pytest"
        assert TestFramework.JEST.value == "jest"
        assert TestFramework.VITEST.value == "vitest"
        assert TestFramework.CARGO.value == "cargo"
        assert TestFramework.MOCHA.value == "mocha"
        assert TestFramework.UNKNOWN.value == "unknown"

    def test_enum_membership(self) -> None:
        """Test enum membership checks."""
        assert TestStatus.PASSED in TestStatus
        assert TestFramework.PYTEST in TestFramework


class TestFrameworkInfo:
    """Test FrameworkInfo model."""

    def test_framework_info_creation(self) -> None:
        """Test basic FrameworkInfo creation."""
        info = FrameworkInfo(framework=TestFramework.PYTEST)
        assert info.framework == TestFramework.PYTEST
        assert info.version is None
        assert info.config_file is None
        assert isinstance(info.detected_at, datetime)

    def test_framework_info_with_version(self) -> None:
        """Test FrameworkInfo with version."""
        info = FrameworkInfo(framework=TestFramework.JEST, version="29.0.0")
        assert info.version == "29.0.0"

    def test_framework_info_with_config(self) -> None:
        """Test FrameworkInfo with config file path."""
        info = FrameworkInfo(
            framework=TestFramework.PYTEST, config_file="pytest.ini"
        )
        assert info.config_file == "pytest.ini"

    def test_framework_info_missing_framework_fails(self) -> None:
        """Test FrameworkInfo requires framework field."""
        with pytest.raises(ValidationError):
            FrameworkInfo()  # type: ignore


class TestTestResult:
    """Test TestResult model."""

    def test_test_result_minimal(self) -> None:
        """Test TestResult with minimal required fields."""
        result = TestResult(
            name="test_example", status=TestStatus.PASSED, duration=0.5
        )
        assert result.name == "test_example"
        assert result.status == TestStatus.PASSED
        assert result.duration == 0.5
        assert result.file is None
        assert result.line is None
        assert result.error_message is None

    def test_test_result_with_file_and_line(self) -> None:
        """Test TestResult with file and line number."""
        result = TestResult(
            name="test_example",
            status=TestStatus.FAILED,
            duration=1.2,
            file="tests/test_module.py",
            line=42,
        )
        assert result.file == "tests/test_module.py"
        assert result.line == 42

    def test_test_result_with_error_details(self) -> None:
        """Test TestResult with error message and traceback."""
        result = TestResult(
            name="test_failing",
            status=TestStatus.FAILED,
            duration=0.1,
            error_message="AssertionError: 1 != 2",
            error_traceback="Traceback (most recent call last)...",
        )
        assert result.error_message == "AssertionError: 1 != 2"
        assert result.error_traceback is not None

    def test_test_result_with_markers(self) -> None:
        """Test TestResult with pytest markers/tags."""
        result = TestResult(
            name="test_slow",
            status=TestStatus.PASSED,
            duration=5.0,
            markers=["slow", "integration"],
        )
        assert result.markers == ["slow", "integration"]

    def test_test_result_with_metadata(self) -> None:
        """Test TestResult with custom metadata."""
        metadata: Dict[str, Any] = {"retry_count": 2, "custom_field": "value"}
        result = TestResult(
            name="test_example",
            status=TestStatus.PASSED,
            duration=0.5,
            metadata=metadata,
        )
        assert result.metadata == metadata

    def test_test_result_missing_required_fields_fails(self) -> None:
        """Test TestResult validation fails without required fields."""
        with pytest.raises(ValidationError):
            TestResult(name="test")  # type: ignore Missing status and duration

        with pytest.raises(ValidationError):
            TestResult(status=TestStatus.PASSED, duration=0.5)  # type: ignore Missing name


class TestTestSummary:
    """Test TestSummary model."""

    def test_test_summary_minimal(self) -> None:
        """Test TestSummary with minimal fields."""
        summary = TestSummary(
            total=10, passed=8, failed=2, skipped=0, duration=5.0, success_rate=80.0
        )
        assert summary.total == 10
        assert summary.passed == 8
        assert summary.failed == 2
        assert summary.skipped == 0
        assert summary.duration == 5.0
        assert summary.success_rate == 80.0

    def test_test_summary_with_optional_fields(self) -> None:
        """Test TestSummary with optional error/xfail/xpass fields."""
        summary = TestSummary(
            total=15,
            passed=10,
            failed=2,
            skipped=1,
            errors=1,
            xfail=1,
            xpass=0,
            duration=10.5,
            success_rate=71.4,
        )
        assert summary.errors == 1
        assert summary.xfail == 1
        assert summary.xpass == 0

    def test_calculate_success_rate_normal(self) -> None:
        """Test success rate calculation with normal values."""
        summary = TestSummary(
            total=10,
            passed=7,
            failed=3,
            skipped=0,
            duration=5.0,
            success_rate=0.0,  # Will be calculated
        )
        rate = summary.calculate_success_rate()
        assert rate == 70.0

    def test_calculate_success_rate_with_skipped(self) -> None:
        """Test success rate excludes skipped tests."""
        summary = TestSummary(
            total=10,
            passed=7,
            failed=1,
            skipped=2,
            duration=5.0,
            success_rate=0.0,
        )
        rate = summary.calculate_success_rate()
        # (7 passed / 8 runnable) * 100 = 87.5%
        assert rate == 87.5

    def test_calculate_success_rate_zero_tests(self) -> None:
        """Test success rate with zero tests returns 100%."""
        summary = TestSummary(
            total=0,
            passed=0,
            failed=0,
            skipped=0,
            duration=0.0,
            success_rate=0.0,
        )
        rate = summary.calculate_success_rate()
        assert rate == 100.0

    def test_calculate_success_rate_all_skipped(self) -> None:
        """Test success rate with all skipped tests returns 100%."""
        summary = TestSummary(
            total=5,
            passed=0,
            failed=0,
            skipped=5,
            duration=0.0,
            success_rate=0.0,
        )
        rate = summary.calculate_success_rate()
        assert rate == 100.0


class TestCoverageInfo:
    """Test CoverageInfo model."""

    def test_coverage_info_creation(self) -> None:
        """Test CoverageInfo basic creation."""
        coverage = CoverageInfo(
            covered_lines=80, total_lines=100, coverage_percent=80.0
        )
        assert coverage.covered_lines == 80
        assert coverage.total_lines == 100
        assert coverage.coverage_percent == 80.0
        assert coverage.missing_lines is None

    def test_coverage_info_with_missing_lines(self) -> None:
        """Test CoverageInfo with missing line numbers."""
        coverage = CoverageInfo(
            covered_lines=75,
            total_lines=100,
            coverage_percent=75.0,
            missing_lines=[10, 15, 20, 25, 30],
        )
        assert coverage.missing_lines == [10, 15, 20, 25, 30]


class TestUnifiedTestResults:
    """Test UnifiedTestResults model."""

    def test_unified_results_minimal(self) -> None:
        """Test UnifiedTestResults with minimal required fields."""
        framework_info = FrameworkInfo(framework=TestFramework.PYTEST)
        summary = TestSummary(
            total=1,
            passed=1,
            failed=0,
            skipped=0,
            duration=0.5,
            success_rate=100.0,
        )
        tests = [
            TestResult(name="test_example", status=TestStatus.PASSED, duration=0.5)
        ]

        results = UnifiedTestResults(
            project="/path/to/project",
            framework=framework_info,
            summary=summary,
            tests=tests,
        )

        assert results.project == "/path/to/project"
        assert results.framework.framework == TestFramework.PYTEST
        assert results.summary.total == 1
        assert len(results.tests) == 1
        assert isinstance(results.timestamp, datetime)

    def test_unified_results_with_coverage(self) -> None:
        """Test UnifiedTestResults with coverage data."""
        framework_info = FrameworkInfo(framework=TestFramework.PYTEST)
        summary = TestSummary(
            total=1,
            passed=1,
            failed=0,
            skipped=0,
            duration=0.5,
            success_rate=100.0,
        )
        tests = [
            TestResult(name="test_example", status=TestStatus.PASSED, duration=0.5)
        ]
        coverage = CoverageInfo(
            covered_lines=50, total_lines=100, coverage_percent=50.0
        )

        results = UnifiedTestResults(
            project="/path/to/project",
            framework=framework_info,
            summary=summary,
            tests=tests,
            coverage=coverage,
        )

        assert results.coverage is not None
        assert results.coverage.coverage_percent == 50.0

    def test_unified_results_with_error(self) -> None:
        """Test UnifiedTestResults with execution error."""
        framework_info = FrameworkInfo(framework=TestFramework.UNKNOWN)
        summary = TestSummary(
            total=0,
            passed=0,
            failed=0,
            skipped=0,
            duration=0.0,
            success_rate=0.0,
        )

        results = UnifiedTestResults(
            project="/path/to/project",
            framework=framework_info,
            summary=summary,
            tests=[],
            error="Framework not found",
        )

        assert results.error == "Framework not found"
        assert len(results.tests) == 0

    def test_unified_results_with_environment(self) -> None:
        """Test UnifiedTestResults with environment info."""
        framework_info = FrameworkInfo(framework=TestFramework.PYTEST)
        summary = TestSummary(
            total=1,
            passed=1,
            failed=0,
            skipped=0,
            duration=0.5,
            success_rate=100.0,
        )
        tests = [
            TestResult(name="test_example", status=TestStatus.PASSED, duration=0.5)
        ]
        environment = {"python_version": "3.11", "os": "linux"}

        results = UnifiedTestResults(
            project="/path/to/project",
            framework=framework_info,
            summary=summary,
            tests=tests,
            environment=environment,
        )

        assert results.environment == environment


class TestFrameworkDetectionResult:
    """Test FrameworkDetectionResult model."""

    def test_detection_result_with_frameworks(self) -> None:
        """Test detection result when frameworks are found."""
        frameworks = [
            FrameworkInfo(framework=TestFramework.PYTEST, config_file="pytest.ini")
        ]
        test_files = ["tests/test_module.py", "tests/test_other.py"]
        config_files = ["pytest.ini", "pyproject.toml"]

        result = FrameworkDetectionResult(
            detected=True,
            frameworks=frameworks,
            test_files=test_files,
            config_files=config_files,
        )

        assert result.detected is True
        assert len(result.frameworks) == 1
        assert len(result.test_files) == 2
        assert len(result.config_files) == 2

    def test_detection_result_no_frameworks(self) -> None:
        """Test detection result when no frameworks found."""
        result = FrameworkDetectionResult(detected=False)
        assert result.detected is False
        assert result.frameworks == []
        assert result.test_files == []
        assert result.config_files == []


class TestTestRunRequest:
    """Test TestRunRequest model."""

    def test_run_request_minimal(self) -> None:
        """Test TestRunRequest with minimal required fields."""
        request = TestRunRequest(project_path="/path/to/project")
        assert request.project_path == "/path/to/project"
        assert request.framework is None
        assert request.test_pattern is None
        assert request.parallel_workers == 4
        assert request.timeout == 300
        assert request.capture_output is True

    def test_run_request_with_framework(self) -> None:
        """Test TestRunRequest with specific framework."""
        request = TestRunRequest(
            project_path="/path/to/project", framework=TestFramework.PYTEST
        )
        assert request.framework == TestFramework.PYTEST

    def test_run_request_with_pattern(self) -> None:
        """Test TestRunRequest with test pattern filter."""
        request = TestRunRequest(
            project_path="/path/to/project", test_pattern="test_integration*"
        )
        assert request.test_pattern == "test_integration*"

    def test_run_request_custom_workers_and_timeout(self) -> None:
        """Test TestRunRequest with custom parallel workers and timeout."""
        request = TestRunRequest(
            project_path="/path/to/project", parallel_workers=8, timeout=600
        )
        assert request.parallel_workers == 8
        assert request.timeout == 600


class TestTestAnalysisResult:
    """Test TestAnalysisResult model."""

    def test_analysis_result_basic(self) -> None:
        """Test TestAnalysisResult basic creation."""
        result = TestAnalysisResult(
            analysis_type="coverage",
            result_key="coverage_percent",
            result_value=85.5,
        )
        assert result.analysis_type == "coverage"
        assert result.result_key == "coverage_percent"
        assert result.result_value == 85.5
        assert result.details == {}
        assert isinstance(result.timestamp, datetime)
        assert result.recommendations is None

    def test_analysis_result_with_details(self) -> None:
        """Test TestAnalysisResult with details dictionary."""
        details = {"covered_lines": 85, "total_lines": 100, "missing_files": []}
        result = TestAnalysisResult(
            analysis_type="coverage",
            result_key="coverage_percent",
            result_value=85.0,
            details=details,
        )
        assert result.details == details

    def test_analysis_result_with_recommendations(self) -> None:
        """Test TestAnalysisResult with recommendations."""
        recommendations = [
            "Add tests for module X",
            "Increase coverage for file Y",
        ]
        result = TestAnalysisResult(
            analysis_type="coverage",
            result_key="coverage_percent",
            result_value=65.0,
            recommendations=recommendations,
        )
        assert result.recommendations == recommendations


class TestModelValidation:
    """Test Pydantic validation edge cases."""

    def test_invalid_framework_type_fails(self) -> None:
        """Test that invalid framework type raises ValidationError."""
        with pytest.raises(ValidationError):
            FrameworkInfo(framework="invalid_framework")  # type: ignore

    def test_invalid_status_type_fails(self) -> None:
        """Test that invalid status type raises ValidationError."""
        with pytest.raises(ValidationError):
            TestResult(
                name="test", status="invalid_status", duration=0.5  # type: ignore
            )

    def test_negative_duration_allowed(self) -> None:
        """Test that negative duration is allowed (for backwards compatibility)."""
        # This might be a bug - consider adding validation
        result = TestResult(name="test", status=TestStatus.PASSED, duration=-1.0)
        assert result.duration == -1.0

    def test_empty_test_name_allowed(self) -> None:
        """Test that empty test name is allowed (might want to add validation)."""
        result = TestResult(name="", status=TestStatus.PASSED, duration=0.0)
        assert result.name == ""

    def test_none_values_in_optional_fields(self) -> None:
        """Test that None is valid for optional fields."""
        result = TestResult(
            name="test",
            status=TestStatus.PASSED,
            duration=0.5,
            file=None,
            line=None,
            error_message=None,
        )
        assert result.file is None
        assert result.line is None
        assert result.error_message is None
