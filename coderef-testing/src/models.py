"""Pydantic models for unified test result schema across all frameworks."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TestStatus(str, Enum):
    """Test execution status."""

    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"
    XFAIL = "xfail"
    XPASS = "xpass"


class TestFramework(str, Enum):
    """Supported test frameworks."""

    PYTEST = "pytest"
    JEST = "jest"
    VITEST = "vitest"
    CARGO = "cargo"
    MOCHA = "mocha"
    UNKNOWN = "unknown"


class FrameworkInfo(BaseModel):
    """Information about detected test framework."""

    framework: TestFramework = Field(..., description="Detected framework type")
    version: Optional[str] = Field(None, description="Framework version if detected")
    config_file: Optional[str] = Field(None, description="Path to framework config file")
    detected_at: datetime = Field(
        default_factory=datetime.utcnow, description="When framework was detected"
    )


class TestResult(BaseModel):
    """Individual test result with timing and status."""

    name: str = Field(..., description="Test name/identifier")
    status: TestStatus = Field(..., description="Test execution status")
    duration: float = Field(..., description="Test duration in seconds")
    file: Optional[str] = Field(None, description="Test file path")
    line: Optional[int] = Field(None, description="Test line number in file")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    error_traceback: Optional[str] = Field(None, description="Full traceback if error")
    stdout: Optional[str] = Field(None, description="Captured stdout")
    stderr: Optional[str] = Field(None, description="Captured stderr")
    markers: Optional[List[str]] = Field(None, description="Test markers/tags")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Framework-specific metadata")


class TestSummary(BaseModel):
    """Aggregated test suite statistics."""

    total: int = Field(..., description="Total test count")
    passed: int = Field(..., description="Number of passed tests")
    failed: int = Field(..., description="Number of failed tests")
    skipped: int = Field(..., description="Number of skipped tests")
    errors: int = Field(default=0, description="Number of test errors")
    xfail: int = Field(default=0, description="Expected failures")
    xpass: int = Field(default=0, description="Unexpected passes")
    duration: float = Field(..., description="Total execution time in seconds")
    success_rate: float = Field(..., description="Percentage of passed tests (0.0-100.0)")

    def calculate_success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total == 0:
            return 100.0
        runnable = self.total - self.skipped
        if runnable == 0:
            return 100.0
        return (self.passed / runnable) * 100.0


class CoverageInfo(BaseModel):
    """Code coverage information."""

    covered_lines: int = Field(..., description="Number of covered lines")
    total_lines: int = Field(..., description="Total number of lines")
    coverage_percent: float = Field(..., description="Coverage percentage (0.0-100.0)")
    missing_lines: Optional[List[int]] = Field(None, description="Line numbers not covered")


class UnifiedTestResults(BaseModel):
    """Unified test results schema - compatible with all frameworks."""

    project: str = Field(..., description="Project path")
    framework: FrameworkInfo = Field(..., description="Framework information")
    summary: TestSummary = Field(..., description="Aggregated statistics")
    tests: List[TestResult] = Field(..., description="Individual test results")
    coverage: Optional[CoverageInfo] = Field(None, description="Code coverage data")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Result collection timestamp"
    )
    environment: Optional[Dict[str, str]] = Field(None, description="Environment info")
    extra: Optional[Dict[str, Any]] = Field(None, description="Framework-specific extras")


class FrameworkDetectionResult(BaseModel):
    """Result of framework detection scan."""

    detected: bool = Field(..., description="Whether frameworks were detected")
    frameworks: List[FrameworkInfo] = Field(default_factory=list, description="Detected frameworks")
    test_files: List[str] = Field(default_factory=list, description="Test file paths found")
    config_files: List[str] = Field(default_factory=list, description="Config files found")


class TestRunRequest(BaseModel):
    """Request to run tests with specific parameters."""

    project_path: str = Field(..., description="Path to project to test")
    framework: Optional[TestFramework] = Field(None, description="Framework to use (auto-detect if None)")
    test_pattern: Optional[str] = Field(None, description="Pattern to filter tests")
    parallel_workers: Optional[int] = Field(default=4, description="Number of parallel workers")
    timeout: Optional[int] = Field(default=300, description="Test timeout in seconds")
    capture_output: bool = Field(default=True, description="Capture stdout/stderr")


class TestAnalysisResult(BaseModel):
    """Result of test analysis (coverage, flaky, performance, health)."""

    analysis_type: str = Field(..., description="Type of analysis performed")
    result_key: str = Field(..., description="Primary result key")
    result_value: float = Field(..., description="Primary numeric result")
    details: Dict[str, Any] = Field(default_factory=dict, description="Detailed results")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Analysis timestamp"
    )
    recommendations: Optional[List[str]] = Field(None, description="Actionable recommendations")
