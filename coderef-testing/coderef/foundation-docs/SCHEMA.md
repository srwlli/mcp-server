# coderef-testing Data Schemas

## Purpose

This document provides comprehensive documentation of all data models, schemas, and data structures used in coderef-testing, including field descriptions, validation rules, and example payloads.

## Overview

coderef-testing uses Pydantic models for data validation and serialization. All schemas are defined in `src/models.py` and enforce strict type checking, field validation, and automatic JSON serialization.

**Schema Categories:**
1. **Test Results** - TestResult, TestSummary, UnifiedTestResults
2. **Framework Info** - TestFramework, FrameworkInfo, FrameworkDetectionResult
3. **Execution** - TestRunRequest
4. **Analysis** - TestAnalysisResult, CoverageInfo
5. **Status Enums** - TestStatus

---

## Core Schemas

### 1. UnifiedTestResults

The primary result container that aggregates test execution data across all frameworks.

**Purpose:** Provide framework-agnostic test results with summary, individual tests, coverage, and metadata.

**Schema:**
```python
class UnifiedTestResults(BaseModel):
    project: str                             # Project path
    framework: FrameworkInfo                 # Framework metadata
    summary: TestSummary                     # Aggregated statistics
    tests: List[TestResult]                  # Individual test results
    coverage: Optional[CoverageInfo]         # Code coverage data (if available)
    timestamp: datetime                      # Result collection timestamp (UTC)
    environment: Optional[Dict[str, str]]    # Environment info (OS, Python version)
    extra: Optional[Dict[str, Any]]          # Framework-specific extras
    error: Optional[str]                     # Error message if execution failed
```

**Field Details:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| project | str | Yes | Absolute path to project |
| framework | FrameworkInfo | Yes | Framework metadata (type, version, config) |
| summary | TestSummary | Yes | Aggregated counts and stats |
| tests | List[TestResult] | Yes | Individual test results (can be empty) |
| coverage | CoverageInfo | No | Coverage data if available |
| timestamp | datetime | Yes | When results were collected (UTC) |
| environment | Dict[str, str] | No | OS, Python version, framework version |
| extra | Dict[str, Any] | No | Framework-specific data (e.g., pytest markers) |
| error | str | No | Error message if execution failed |

**Example:**
```json
{
  "project": "/path/to/project",
  "framework": {
    "framework": "pytest",
    "version": "7.4.3",
    "config_file": "pyproject.toml",
    "detected_at": "2025-12-27T12:00:00Z"
  },
  "summary": {
    "total": 247,
    "passed": 245,
    "failed": 2,
    "skipped": 0,
    "errors": 0,
    "xfail": 0,
    "xpass": 0,
    "duration": 12.5,
    "success_rate": 99.19
  },
  "tests": [
    {
      "name": "test_foo",
      "status": "passed",
      "duration": 0.5,
      "file": "tests/test_foo.py",
      "line": 10,
      "error_message": null,
      "error_traceback": null,
      "stdout": null,
      "stderr": null,
      "markers": ["unit"],
      "metadata": {}
    }
  ],
  "coverage": {
    "covered_lines": 850,
    "total_lines": 1000,
    "coverage_percent": 85.0,
    "missing_lines": [45, 67, 89]
  },
  "timestamp": "2025-12-27T12:00:00Z",
  "environment": {
    "os": "Windows 11",
    "python_version": "3.11.5",
    "framework_version": "pytest 7.4.3"
  },
  "extra": {
    "pytest_markers": ["unit", "integration"],
    "platform": "win32"
  },
  "error": null
}
```

**Validation Rules:**
- `project` must be non-empty string
- `timestamp` defaults to UTC now if not provided
- `summary.success_rate` calculated automatically
- `tests` can be empty list if no tests found

**Use Cases:**
- Primary return value from all test execution tools
- Archived in JSON format for historical tracking
- Serialized to CSV/HTML for reporting

---

### 2. TestResult

Individual test result with timing, status, and error information.

**Schema:**
```python
class TestResult(BaseModel):
    name: str                               # Test name/identifier
    status: TestStatus                      # Execution status (passed/failed/skipped/error)
    duration: float                         # Duration in seconds
    file: Optional[str]                     # Test file path
    line: Optional[int]                     # Line number in file
    error_message: Optional[str]            # Error message if failed
    error_traceback: Optional[str]          # Full traceback if error
    stdout: Optional[str]                   # Captured stdout
    stderr: Optional[str]                   # Captured stderr
    markers: Optional[List[str]]            # Test markers/tags (e.g., ["unit", "slow"])
    metadata: Optional[Dict[str, Any]]      # Framework-specific metadata
```

**Field Details:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | str | Yes | Test identifier (e.g., "test_foo" or "tests/test_foo.py::test_bar") |
| status | TestStatus | Yes | One of: passed, failed, skipped, error, xfail, xpass |
| duration | float | Yes | Execution time in seconds (0.0 if not measured) |
| file | str | No | Relative path to test file |
| line | int | No | Line number where test is defined |
| error_message | str | No | Short error message (e.g., "AssertionError: 1 != 2") |
| error_traceback | str | No | Full traceback for debugging |
| stdout | str | No | Captured stdout during test execution |
| stderr | str | No | Captured stderr during test execution |
| markers | List[str] | No | Pytest markers or Jest tags (e.g., ["unit", "integration"]) |
| metadata | Dict | No | Framework-specific data (e.g., retry count) |

**Example:**
```json
{
  "name": "tests/test_auth.py::test_login_success",
  "status": "passed",
  "duration": 0.523,
  "file": "tests/test_auth.py",
  "line": 45,
  "error_message": null,
  "error_traceback": null,
  "stdout": "Login successful\n",
  "stderr": null,
  "markers": ["unit", "auth"],
  "metadata": {
    "retries": 0,
    "setup_duration": 0.012
  }
}
```

**Failed Test Example:**
```json
{
  "name": "tests/test_payment.py::test_refund",
  "status": "failed",
  "duration": 1.234,
  "file": "tests/test_payment.py",
  "line": 102,
  "error_message": "AssertionError: Refund amount 50.00 != expected 55.00",
  "error_traceback": "Traceback (most recent call last):\n  File \"tests/test_payment.py\", line 110, in test_refund\n    assert refund.amount == 55.00\nAssertionError: Refund amount 50.00 != expected 55.00",
  "stdout": "Processing refund...\n",
  "stderr": null,
  "markers": ["integration", "payment"],
  "metadata": {}
}
```

**Validation Rules:**
- `name` must be non-empty
- `duration` must be >= 0.0
- `line` must be positive integer if provided

**Use Cases:**
- Identify specific test failures
- Track test performance over time
- Debug failing tests with traceback

---

### 3. TestSummary

Aggregated test suite statistics.

**Schema:**
```python
class TestSummary(BaseModel):
    total: int                              # Total test count
    passed: int                             # Number of passed tests
    failed: int                             # Number of failed tests
    skipped: int                            # Number of skipped tests
    errors: int                             # Number of test errors (default: 0)
    xfail: int                              # Expected failures (default: 0)
    xpass: int                              # Unexpected passes (default: 0)
    duration: float                         # Total execution time in seconds
    success_rate: float                     # Percentage of passed tests (0.0-100.0)
```

**Field Details:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| total | int | Yes | - | Total tests executed |
| passed | int | Yes | - | Tests that passed |
| failed | int | Yes | - | Tests that failed |
| skipped | int | Yes | - | Tests that were skipped |
| errors | int | No | 0 | Tests with errors (setup/teardown failures) |
| xfail | int | No | 0 | Expected failures (pytest xfail) |
| xpass | int | No | 0 | Unexpected passes (pytest xfail that passed) |
| duration | float | Yes | - | Total execution time in seconds |
| success_rate | float | Yes | - | (passed / (total - skipped)) * 100 |

**Example:**
```json
{
  "total": 247,
  "passed": 245,
  "failed": 2,
  "skipped": 0,
  "errors": 0,
  "xfail": 1,
  "xpass": 0,
  "duration": 12.5,
  "success_rate": 99.19
}
```

**Success Rate Calculation:**
```python
def calculate_success_rate(self) -> float:
    if self.total == 0:
        return 100.0
    runnable = self.total - self.skipped
    if runnable == 0:
        return 100.0
    return (self.passed / runnable) * 100.0
```

**Validation Rules:**
- `total` = `passed + failed + skipped + errors`
- `success_rate` automatically calculated
- All counts must be >= 0

**Use Cases:**
- High-level test suite health
- Track success rates over time
- CI/CD pass/fail decisions

---

### 4. CoverageInfo

Code coverage information extracted from test runs.

**Schema:**
```python
class CoverageInfo(BaseModel):
    covered_lines: int                      # Number of covered lines
    total_lines: int                        # Total number of lines
    coverage_percent: float                 # Coverage percentage (0.0-100.0)
    missing_lines: Optional[List[int]]      # Line numbers not covered
```

**Example:**
```json
{
  "covered_lines": 850,
  "total_lines": 1000,
  "coverage_percent": 85.0,
  "missing_lines": [45, 67, 89, 102, 156]
}
```

**Validation Rules:**
- `covered_lines` <= `total_lines`
- `coverage_percent` = (covered_lines / total_lines) * 100

**Use Cases:**
- Identify untested code paths
- Track coverage improvements
- Enforce coverage requirements (e.g., 80% minimum)

---

## Framework Schemas

### 5. TestFramework (Enum)

Supported test frameworks.

**Schema:**
```python
class TestFramework(str, Enum):
    PYTEST = "pytest"
    JEST = "jest"
    VITEST = "vitest"
    CARGO = "cargo"
    MOCHA = "mocha"
    UNKNOWN = "unknown"
```

**Valid Values:**
- `"pytest"` - Python testing framework
- `"jest"` - JavaScript testing framework
- `"vitest"` - Vite-based testing framework
- `"cargo"` - Rust testing framework
- `"mocha"` - Node.js testing framework
- `"unknown"` - Framework not detected

**Use Cases:**
- Framework auto-detection
- Command building
- Result parsing

---

### 6. FrameworkInfo

Information about detected test framework.

**Schema:**
```python
class FrameworkInfo(BaseModel):
    framework: TestFramework                # Detected framework type
    version: Optional[str]                  # Framework version (e.g., "7.4.3")
    config_file: Optional[str]              # Path to framework config file
    detected_at: datetime                   # When framework was detected (UTC)
```

**Example:**
```json
{
  "framework": "pytest",
  "version": "7.4.3",
  "config_file": "pyproject.toml",
  "detected_at": "2025-12-27T12:00:00Z"
}
```

**Validation Rules:**
- `detected_at` defaults to UTC now
- `version` can be None if not detectable

**Use Cases:**
- Framework detection results
- Metadata in UnifiedTestResults
- Version compatibility checks

---

### 7. FrameworkDetectionResult

Result of framework detection scan.

**Schema:**
```python
class FrameworkDetectionResult(BaseModel):
    detected: bool                          # Whether frameworks were detected
    frameworks: List[FrameworkInfo]         # Detected frameworks (can be multiple)
    test_files: List[str]                   # Test file paths found
    config_files: List[str]                 # Config files found
```

**Example:**
```json
{
  "detected": true,
  "frameworks": [
    {
      "framework": "pytest",
      "version": "7.4.3",
      "config_file": "pyproject.toml",
      "detected_at": "2025-12-27T12:00:00Z"
    }
  ],
  "test_files": [
    "tests/test_foo.py",
    "tests/test_bar.py",
    "tests/integration/test_api.py"
  ],
  "config_files": ["pyproject.toml"]
}
```

**Multi-Framework Example (Monorepo):**
```json
{
  "detected": true,
  "frameworks": [
    {
      "framework": "pytest",
      "version": "7.4.3",
      "config_file": "backend/pyproject.toml",
      "detected_at": "2025-12-27T12:00:00Z"
    },
    {
      "framework": "jest",
      "version": "29.5.0",
      "config_file": "frontend/package.json",
      "detected_at": "2025-12-27T12:00:00Z"
    }
  ],
  "test_files": [
    "backend/tests/test_api.py",
    "frontend/src/__tests__/App.test.js"
  ],
  "config_files": ["backend/pyproject.toml", "frontend/package.json"]
}
```

**Use Cases:**
- Tool: `discover_tests` return value
- Tool: `list_test_frameworks` return value
- Pre-execution framework verification

---

## Execution Schemas

### 8. TestRunRequest

Request to run tests with specific parameters.

**Schema:**
```python
class TestRunRequest(BaseModel):
    project_path: str                       # Path to project to test
    framework: Optional[TestFramework]      # Framework (auto-detect if None)
    test_pattern: Optional[str]             # Pattern to filter tests
    parallel_workers: Optional[int]         # Number of parallel workers (default: 4)
    timeout: Optional[int]                  # Test timeout in seconds (default: 300)
    capture_output: bool                    # Capture stdout/stderr (default: True)
```

**Example:**
```json
{
  "project_path": "/path/to/project",
  "framework": "pytest",
  "test_pattern": "test_auth",
  "parallel_workers": 8,
  "timeout": 600,
  "capture_output": true
}
```

**Field Details:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| project_path | str | Yes | - | Absolute path to project |
| framework | TestFramework | No | None | Force framework (auto-detect if None) |
| test_pattern | str | No | None | Filter pattern (e.g., "test_auth" or "@tag:integration") |
| parallel_workers | int | No | 4 | Number of parallel workers (1-20) |
| timeout | int | No | 300 | Timeout in seconds (max: 3600) |
| capture_output | bool | No | True | Capture stdout/stderr |

**Validation Rules:**
- `project_path` must be non-empty
- `parallel_workers` must be 1-20
- `timeout` must be 1-3600 seconds

**Use Cases:**
- Input to `run_all_tests`, `run_test_file`, etc.
- Configurable test execution

---

## Analysis Schemas

### 9. TestAnalysisResult

Result of test analysis (coverage, flaky, performance, health).

**Schema:**
```python
class TestAnalysisResult(BaseModel):
    analysis_type: str                      # Type of analysis ("coverage"/"flaky"/"performance"/"health")
    result_key: str                         # Primary result key (e.g., "coverage_percent")
    result_value: float                     # Primary numeric result
    details: Dict[str, Any]                 # Detailed results (varies by analysis type)
    timestamp: datetime                     # Analysis timestamp (UTC)
    recommendations: Optional[List[str]]    # Actionable recommendations
```

**Coverage Analysis Example:**
```json
{
  "analysis_type": "coverage",
  "result_key": "coverage_percent",
  "result_value": 85.0,
  "details": {
    "covered_lines": 850,
    "total_lines": 1000,
    "missing_lines": [45, 67, 89],
    "uncovered_files": ["src/utils.py"]
  },
  "timestamp": "2025-12-27T12:00:00Z",
  "recommendations": [
    "Add tests for src/utils.py (50 uncovered lines)",
    "Cover error paths in src/auth.py"
  ]
}
```

**Performance Analysis Example:**
```json
{
  "analysis_type": "performance",
  "result_key": "avg_duration",
  "result_value": 0.05,
  "details": {
    "p50": 0.02,
    "p95": 0.15,
    "p99": 1.2,
    "slow_tests": [
      {"name": "test_db_migration", "duration": 5.3, "file": "tests/test_db.py"}
    ],
    "total_duration": 12.5
  },
  "timestamp": "2025-12-27T12:00:00Z",
  "recommendations": [
    "Optimize test_db_migration (5.3s)",
    "Mock external API in test_integration (3.2s)"
  ]
}
```

**Flaky Test Analysis Example:**
```json
{
  "analysis_type": "flaky",
  "result_key": "flaky_test_count",
  "result_value": 3,
  "details": {
    "flaky_tests": [
      {
        "name": "test_async_timeout",
        "file": "tests/test_async.py",
        "flakiness_score": 0.4,
        "failures": 2,
        "total_runs": 5
      }
    ]
  },
  "timestamp": "2025-12-27T12:00:00Z",
  "recommendations": [
    "Fix test_async_timeout - fails 40% of time",
    "Add proper async cleanup in test_race_condition"
  ]
}
```

**Health Analysis Example:**
```json
{
  "analysis_type": "health",
  "result_key": "health_score",
  "result_value": 92.5,
  "details": {
    "grade": "A",
    "success_rate": 99.19,
    "coverage": 85.0,
    "avg_speed": 0.05,
    "stability": 95.0,
    "breakdown": {
      "correctness": 39.676,
      "coverage": 25.5,
      "speed": 18.0,
      "stability": 9.5
    }
  },
  "timestamp": "2025-12-27T12:00:00Z",
  "recommendations": [
    "Improve coverage to 90% (currently 85%)",
    "Fix 2 flaky tests to reach 100% stability"
  ]
}
```

**Use Cases:**
- Return value from analysis tools
- Actionable recommendations for improvement
- Metric tracking over time

---

## Status Enums

### 10. TestStatus (Enum)

Test execution status.

**Schema:**
```python
class TestStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"
    XFAIL = "xfail"      # Expected failure (pytest)
    XPASS = "xpass"      # Unexpected pass (pytest)
```

**Valid Values:**

| Status | Description | Common Causes |
|--------|-------------|---------------|
| `passed` | Test passed successfully | - |
| `failed` | Test assertion failed | AssertionError, wrong output |
| `skipped` | Test was skipped | @pytest.mark.skip, test.skip() |
| `error` | Test had error during execution | Setup/teardown failure, syntax error |
| `xfail` | Expected failure (pytest) | Known bug, @pytest.mark.xfail |
| `xpass` | Unexpected pass (pytest) | Expected to fail but passed |

**Use Cases:**
- TestResult.status field
- Filtering tests by status
- Summary calculations

---

## JSON Schema Export

All Pydantic models support automatic JSON schema generation:

```python
from src.models import UnifiedTestResults

# Get JSON schema
schema = UnifiedTestResults.model_json_schema()

# Example output:
{
  "title": "UnifiedTestResults",
  "type": "object",
  "properties": {
    "project": {"type": "string"},
    "framework": {"$ref": "#/$defs/FrameworkInfo"},
    "summary": {"$ref": "#/$defs/TestSummary"},
    "tests": {"items": {"$ref": "#/$defs/TestResult"}, "type": "array"},
    ...
  },
  "required": ["project", "framework", "summary", "tests", "timestamp"]
}
```

**Use Cases:**
- API documentation generation
- Client library schema validation
- TypeScript type generation

---

## Validation Examples

### Valid UnifiedTestResults
```python
from src.models import UnifiedTestResults, FrameworkInfo, TestSummary, TestFramework

result = UnifiedTestResults(
    project="/path/to/project",
    framework=FrameworkInfo(framework=TestFramework.PYTEST, version="7.4.3"),
    summary=TestSummary(total=10, passed=10, failed=0, skipped=0, duration=5.0, success_rate=100.0),
    tests=[],
    timestamp=datetime.utcnow()
)
# ✅ Valid
```

### Invalid Examples

**Missing required fields:**
```python
result = UnifiedTestResults(
    project="/path"
    # Missing framework, summary, tests, timestamp
)
# ❌ ValidationError: 4 fields missing
```

**Invalid success_rate:**
```python
summary = TestSummary(
    total=10, passed=15, failed=0, skipped=0, duration=5.0, success_rate=100.0
)
# ❌ ValidationError: passed (15) > total (10)
```

**Invalid enum value:**
```python
framework = FrameworkInfo(framework="unknown_framework")
# ❌ ValidationError: "unknown_framework" not in TestFramework enum
```

---

## Migration Guide

### From v0.x to v1.0

**Breaking Changes:**
1. `TestSummary.success_rate` is now required (auto-calculated)
2. `UnifiedTestResults.timestamp` defaults to UTC (not local time)
3. `TestStatus.ERROR` added (separate from FAILED)

**Migration:**
```python
# v0.x
summary = TestSummary(total=10, passed=10, failed=0, skipped=0, duration=5.0)
# Missing success_rate

# v1.0
summary = TestSummary(
    total=10, passed=10, failed=0, skipped=0, duration=5.0,
    success_rate=100.0  # Now required
)
```

---

## References

- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [API.md](API.md) - MCP tool reference
- [COMPONENTS.md](COMPONENTS.md) - Component implementation
- [models.py](../../src/models.py) - Source code

---

*Generated: 2025-12-27*
*Version: 1.0.0*
