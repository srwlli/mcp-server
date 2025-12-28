# coderef-testing MCP API Reference

## Purpose

This document provides a complete reference for all 14 MCP tools exposed by the coderef-testing server, including parameters, return values, and usage examples.

## Overview

coderef-testing exposes 14 MCP tools across 4 categories:

| Category | Tools | Purpose |
|----------|-------|---------|
| **Discovery** | 2 | Find tests and detect frameworks |
| **Execution** | 4 | Run tests with various configurations |
| **Management** | 4 | View results, generate reports, compare runs |
| **Analysis** | 4 | Coverage, performance, flaky detection, health |

**Authentication:** None (local MCP server)
**Protocol:** MCP (Model Context Protocol)
**Data Format:** JSON request/response
**Error Handling:** Errors returned as TextContent with error message

## Discovery Tools

### 1. discover_tests

Find all tests in a project and auto-detect test framework.

**Parameters:**
```typescript
{
  project_path: string  // Required: Path to project to scan
}
```

**Returns:**
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
  "test_files": ["tests/test_foo.py", "tests/test_bar.py"],
  "config_files": ["pyproject.toml"]
}
```

**Example:**
```bash
# Via MCP
discover_tests({"project_path": "C:/Users/willh/.mcp-servers/coderef-context"})

# Via slash command
/discover-tests C:/Users/willh/.mcp-servers/coderef-context
```

**Use Cases:**
- Initial project setup - understand what tests exist
- Verify test framework before execution
- List all test files for selective execution

---

### 2. list_test_frameworks

List all detected test frameworks and their versions.

**Parameters:**
```typescript
{
  project_path: string  // Required: Path to project to scan
}
```

**Returns:**
```json
{
  "frameworks": [
    {
      "framework": "pytest",
      "version": "7.4.3",
      "config_file": "pyproject.toml"
    }
  ],
  "primary_framework": "pytest"
}
```

**Example:**
```bash
list_test_frameworks({"project_path": "/path/to/project"})
```

**Use Cases:**
- Verify framework installation
- Check framework versions
- Detect multi-framework projects (pytest + jest in monorepo)

---

## Execution Tools

### 3. run_all_tests

Execute the entire test suite in a project.

**Parameters:**
```typescript
{
  project_path: string       // Required: Path to project
  framework?: string         // Optional: Force framework (pytest/jest/vitest/cargo/mocha)
  parallel_workers?: number  // Optional: Number of workers (default: 4)
  timeout?: number           // Optional: Timeout in seconds (default: 300)
}
```

**Returns:**
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
    "duration": 12.5,
    "success_rate": 99.19
  },
  "tests": [
    {
      "name": "test_foo",
      "status": "passed",
      "duration": 0.5,
      "file": "tests/test_foo.py",
      "line": 10
    }
  ],
  "timestamp": "2025-12-27T12:00:00Z"
}
```

**Example:**
```bash
# Default (auto-detect, 4 workers)
run_all_tests({"project_path": "/path"})

# Force pytest, 8 workers
run_all_tests({"project_path": "/path", "framework": "pytest", "parallel_workers": 8})

# With custom timeout
run_all_tests({"project_path": "/path", "timeout": 600})
```

**Use Cases:**
- Full test suite execution
- CI/CD pipeline integration
- Pre-deployment validation

---

### 4. run_test_file

Run tests from a specific test file.

**Parameters:**
```typescript
{
  project_path: string  // Required: Path to project
  test_file: string     // Required: Path to test file (relative to project)
}
```

**Returns:**
Same as `run_all_tests` but only for specified file.

**Example:**
```bash
run_test_file({
  "project_path": "/path/to/project",
  "test_file": "tests/test_auth.py"
})
```

**Use Cases:**
- Test-driven development (TDD) workflows
- Debug specific test failures
- Selective test execution during development

---

### 5. run_test_category

Run tests matching a pattern or tag.

**Parameters:**
```typescript
{
  project_path: string  // Required: Path to project
  pattern: string       // Required: Pattern (e.g., "test_auth" or "@tag:integration")
}
```

**Returns:**
Same as `run_all_tests` but only for matching tests.

**Example:**
```bash
# Run all auth tests
run_test_category({"project_path": "/path", "pattern": "test_auth"})

# Run integration tests (pytest markers)
run_test_category({"project_path": "/path", "pattern": "@tag:integration"})

# Run slow tests (jest)
run_test_category({"project_path": "/path", "pattern": "@slow"})
```

**Use Cases:**
- Run functional test categories (auth, payment, admin)
- Execute integration vs unit tests separately
- Test specific features in isolation

---

### 6. run_tests_in_parallel

Execute tests with explicit parallelization control.

**Parameters:**
```typescript
{
  project_path: string      // Required: Path to project
  parallel_workers: number  // Required: Number of parallel workers
}
```

**Returns:**
Same as `run_all_tests`.

**Example:**
```bash
# Use 16 workers for faster execution
run_tests_in_parallel({"project_path": "/path", "parallel_workers": 16})

# Single worker (no parallelization)
run_tests_in_parallel({"project_path": "/path", "parallel_workers": 1})
```

**Use Cases:**
- Performance optimization (scale workers to CPU cores)
- Debug race conditions (use 1 worker)
- CI/CD performance tuning

**Performance Guidelines:**
- 1-4 workers: Standard laptops
- 4-8 workers: Developer workstations
- 8-16 workers: CI/CD servers
- 16+ workers: High-performance build machines

---

## Management Tools

### 7. get_test_results

Retrieve stored test results from archive.

**Parameters:**
```typescript
{
  project_path: string  // Required: Path to project
  date?: string         // Optional: Date (YYYY-MM-DD), default: latest
}
```

**Returns:**
```json
{
  "results": [
    {
      "timestamp": "2025-12-27T12:00:00Z",
      "summary": { "total": 247, "passed": 245, "failed": 2 },
      "file_path": "coderef/testing/results/2025-12-27/12-00-00.json"
    }
  ]
}
```

**Example:**
```bash
# Get latest results
get_test_results({"project_path": "/path"})

# Get results from specific date
get_test_results({"project_path": "/path", "date": "2025-12-26"})
```

**Use Cases:**
- Review historical test runs
- Investigate regressions
- Track test trends over time

---

### 8. aggregate_results

Aggregate results across multiple test runs.

**Parameters:**
```typescript
{
  project_path: string  // Required: Path to project
}
```

**Returns:**
```json
{
  "total_runs": 15,
  "avg_success_rate": 98.5,
  "avg_duration": 13.2,
  "trend": "improving",
  "summary": {
    "total_tests": 247,
    "avg_passed": 243,
    "avg_failed": 4
  }
}
```

**Example:**
```bash
aggregate_results({"project_path": "/path"})
```

**Use Cases:**
- Calculate average success rates
- Track performance trends
- Generate summary reports

---

### 9. generate_test_report

Generate test report in specified format (markdown/HTML/JSON).

**Parameters:**
```typescript
{
  project_path: string   // Required: Path to project
  format?: string        // Optional: "markdown" | "html" | "json" (default: markdown)
}
```

**Returns (markdown):**
```markdown
# Test Report: My Project

**Date:** 2025-12-27
**Framework:** pytest 7.4.3
**Duration:** 12.5s
**Success Rate:** 99.19%

## Summary
- Total: 247
- Passed: 245 ✅
- Failed: 2 ❌
- Skipped: 0

## Failed Tests
1. test_auth_invalid_token (tests/test_auth.py:45) - 0.2s
2. test_payment_refund (tests/test_payment.py:102) - 1.3s
```

**Example:**
```bash
# Markdown report
generate_test_report({"project_path": "/path", "format": "markdown"})

# HTML report (for dashboards)
generate_test_report({"project_path": "/path", "format": "html"})

# JSON export (for CI/CD)
generate_test_report({"project_path": "/path", "format": "json"})
```

**Use Cases:**
- Generate reports for stakeholders
- Create HTML dashboards
- Export data for external systems

---

### 10. compare_test_runs

Compare results between two test runs.

**Parameters:**
```typescript
{
  project_path: string  // Required: Path to project
  date1: string         // Required: First date (YYYY-MM-DD)
  date2: string         // Required: Second date (YYYY-MM-DD)
}
```

**Returns:**
```json
{
  "comparison": {
    "date1": "2025-12-26",
    "date2": "2025-12-27",
    "total_change": 0,
    "passed_change": +5,
    "failed_change": -5,
    "duration_change": -2.3,
    "new_failures": ["test_foo"],
    "fixed_tests": ["test_bar", "test_baz"],
    "trend": "improving"
  }
}
```

**Example:**
```bash
compare_test_runs({
  "project_path": "/path",
  "date1": "2025-12-26",
  "date2": "2025-12-27"
})
```

**Use Cases:**
- Detect regressions between commits
- Track improvements after bug fixes
- Monitor test suite evolution

---

## Analysis Tools

### 11. analyze_coverage

Analyze code coverage metrics and gaps.

**Parameters:**
```typescript
{
  project_path: string  // Required: Path to project
}
```

**Returns:**
```json
{
  "analysis_type": "coverage",
  "result_key": "coverage_percent",
  "result_value": 85.0,
  "details": {
    "covered_lines": 850,
    "total_lines": 1000,
    "missing_lines": [45, 67, 89, 102],
    "uncovered_files": ["src/utils.py", "src/helpers.py"]
  },
  "recommendations": [
    "Add tests for src/utils.py (50 uncovered lines)",
    "Cover error paths in src/auth.py"
  ]
}
```

**Example:**
```bash
analyze_coverage({"project_path": "/path"})
```

**Use Cases:**
- Identify untested code
- Improve test coverage
- Meet coverage requirements (e.g., 80% minimum)

---

### 12. detect_flaky_tests

Find tests that fail intermittently.

**Parameters:**
```typescript
{
  project_path: string  // Required: Path to project
  runs?: number         // Optional: Number of runs to analyze (default: 5)
}
```

**Returns:**
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
  "recommendations": [
    "Fix test_async_timeout - fails 40% of time",
    "Add proper async cleanup in test_race_condition"
  ]
}
```

**Example:**
```bash
# Default (5 runs)
detect_flaky_tests({"project_path": "/path"})

# Custom run count
detect_flaky_tests({"project_path": "/path", "runs": 10})
```

**Use Cases:**
- Debug intermittent failures
- Improve test reliability
- Identify timing-dependent tests

---

### 13. analyze_test_performance

Analyze test execution speed and identify slow tests.

**Parameters:**
```typescript
{
  project_path: string  // Required: Path to project
  threshold?: number    // Optional: Slowness threshold in seconds (default: 1.0)
}
```

**Returns:**
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
      {
        "name": "test_db_migration",
        "duration": 5.3,
        "file": "tests/test_db.py"
      }
    ],
    "total_duration": 12.5
  },
  "recommendations": [
    "Optimize test_db_migration (5.3s)",
    "Mock external API in test_integration (3.2s)"
  ]
}
```

**Example:**
```bash
# Default (1.0s threshold)
analyze_test_performance({"project_path": "/path"})

# Custom threshold (flag tests >2s)
analyze_test_performance({"project_path": "/path", "threshold": 2.0})
```

**Use Cases:**
- Find slow tests
- Optimize test execution time
- Meet performance budgets

---

### 14. validate_test_health

Perform overall test suite health check (0-100 score).

**Parameters:**
```typescript
{
  project_path: string  // Required: Path to project
}
```

**Returns:**
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
      "correctness": 40,
      "coverage": 25.5,
      "speed": 18,
      "stability": 9
    }
  },
  "recommendations": [
    "Improve coverage to 90% (currently 85%)",
    "Fix 2 flaky tests to reach 100% stability"
  ]
}
```

**Scoring Formula:**
```
health_score = (0.4 * success_rate) + (0.3 * coverage) + (0.2 * speed_score) + (0.1 * stability)

Grades:
A: 90-100
B: 80-89
C: 70-79
D: 60-69
F: <60
```

**Example:**
```bash
validate_test_health({"project_path": "/path"})
```

**Use Cases:**
- Overall test suite assessment
- Track quality metrics
- Set improvement goals

---

## Error Handling

All tools return errors in standard format:

```json
{
  "error": "Framework not detected. Ensure pytest/jest/cargo config exists.",
  "details": {
    "project_path": "/path",
    "scanned_files": ["pyproject.toml", "package.json"],
    "detected_frameworks": []
  }
}
```

**Common Errors:**

| Error | Cause | Solution |
|-------|-------|----------|
| Framework not detected | No test framework config | Install pytest/jest/cargo |
| Test timeout | Tests exceed timeout | Increase timeout parameter |
| Parse error | Invalid framework output | Check framework version compatibility |
| Permission denied | Cannot access project | Verify path permissions |
| No tests found | Empty test suite | Create test files |

---

## Integration Examples

### CI/CD Pipeline (GitHub Actions)

```yaml
name: Test with coderef-testing

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run tests
        run: |
          run_all_tests '{"project_path": ".", "parallel_workers": 8}'

      - name: Generate report
        run: |
          generate_test_report '{"project_path": ".", "format": "html"}'

      - name: Check health
        run: |
          validate_test_health '{"project_path": "."}'
```

### Python Script

```python
import asyncio
from mcp.client import Client

async def run_tests():
    client = Client("coderef-testing")

    # Discover tests
    discovery = await client.call_tool("discover_tests", {
        "project_path": "/path/to/project"
    })

    # Run tests
    results = await client.call_tool("run_all_tests", {
        "project_path": "/path/to/project",
        "parallel_workers": 8
    })

    # Analyze
    health = await client.call_tool("validate_test_health", {
        "project_path": "/path/to/project"
    })

    print(f"Health Score: {health['result_value']}")

asyncio.run(run_tests())
```

---

## References

- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture details
- [SCHEMA.md](SCHEMA.md) - Data models and schemas
- [COMPONENTS.md](COMPONENTS.md) - Component implementation
- [README.md](../../README.md) - User guide
- [MCP Specification](https://spec.modelcontextprotocol.io/) - Protocol reference

---

*Generated: 2025-12-27*
*Version: 1.0.0*
