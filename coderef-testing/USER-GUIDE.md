# coeref-testing User Guide

Complete guide to using the coeref-testing MCP server with practical examples and use cases.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Discovery Tools](#discovery-tools)
3. [Execution Tools](#execution-tools)
4. [Management Tools](#management-tools)
5. [Analysis Tools](#analysis-tools)
6. [Common Workflows](#common-workflows)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Usage](#advanced-usage)

## Getting Started

### Installation

```bash
cd C:\Users\willh\.mcp-servers\coeref-testing
uv sync
python server.py
```

### First Steps

1. **Discover what tests exist:**
   ```bash
   /discover-tests C:\Users\willh\.mcp-servers\coderef-context
   ```

2. **See what frameworks are used:**
   ```bash
   /list-frameworks C:\Users\willh\.mcp-servers\coderef-context
   ```

3. **Run all tests:**
   ```bash
   /run-tests C:\Users\willh\.mcp-servers\coderef-context
   ```

4. **Check health:**
   ```bash
   /test-health C:\Users\willh\.mcp-servers\coderef-context
   ```

## Discovery Tools

### /discover-tests

Find all tests in a project and auto-detect the test framework.

**Syntax:**
```bash
discover_tests [project_path]
```

**Examples:**

Find tests in CodeRef ecosystem:
```bash
/discover-tests C:\Users\willh\.mcp-servers\coderef-context
```

Output:
```
Framework: pytest
Test Path: /tests
Total Tests Found: 45
Config File: pyproject.toml

Test Files:
- tests/test_models.py (12 tests)
- tests/test_analyzer.py (15 tests)
- tests/integration/test_impact.py (18 tests)
```

**Use Case:** When starting work on a project, get overview of test coverage.

**When to Use:**
- New project onboarding
- Understanding test suite scope
- Before making major changes
- Verifying test discovery is working

---

### /list-frameworks

Show all test frameworks detected in the project.

**Syntax:**
```bash
list_frameworks [project_path]
```

**Examples:**

List frameworks in a multi-language project:
```bash
/list-frameworks C:\Users\willh\.mcp-servers
```

Output:
```
Detected Frameworks:

1. pytest (Python)
   Version: 7.4.2
   Config: pyproject.toml
   Directory: /tests
   Status: ✅ Configured

2. jest (JavaScript)
   Version: 29.5.0
   Config: jest.config.js
   Directory: /test
   Status: ✅ Configured

3. (none for Rust)
   Status: ⚠ Not found (if applicable)
```

**Use Case:** Understand which frameworks a project uses.

**When to Use:**
- Multi-language projects
- Adding new tests with different framework
- Verifying framework setup
- Planning test infrastructure

## Execution Tools

### /run-tests

Execute all tests in a project with automatic framework detection.

**Syntax:**
```bash
run_tests [project_path] [--verbose] [--timeout SECONDS] [--workers N]
```

**Examples:**

Basic test run:
```bash
/run-tests C:\Users\willh\.mcp-servers\coderef-context
```

Output:
```
Running tests for coderef-context...
Framework: pytest
Workers: 8 (auto-detected)
Timeout: 300 seconds

Execution:
[████████████████████] 45/45 completed in 12.4s

Results:
  Passed:  43 (95.6%)
  Failed:  2 (4.4%)
  Skipped: 0 (0%)

Failed Tests:
  ✗ test_invalid_schema (models_test.py:45) - 4.2s
  ✗ test_deployment_check (integration_test.py:128) - 3.1s

Status: FAILING
```

**Detailed run with verbose output:**
```bash
/run-tests C:\Users\willh\.mcp-servers\coderef-context --verbose --workers 4
```

Output includes:
- Each test result individually
- Full error messages
- Stack traces for failures

**Slow test run with increased timeout:**
```bash
/run-tests /path/to/project --timeout 600
```

**Use Cases:**
- Daily development workflow
- Pre-commit checks
- CI/CD pipeline execution
- Validation before deployment

**When to Use:**
- After code changes
- Before pushing commits
- In CI/CD pipelines
- Verifying fixes

---

### /run-test-file

Run a specific test file or set of test files.

**Syntax:**
```bash
run_test_file [project_path] [test_file] [--verbose] [--timeout SECONDS]
```

**Examples:**

Run a single pytest file:
```bash
/run-test-file C:\Users\willh\.mcp-servers\coderef-context tests/test_models.py
```

Output:
```
Running tests/test_models.py (pytest)

Results:
  Total:   12
  Passed:  11
  Failed:  1
  Skipped: 0
  Duration: 2.3s

Failed:
  ✗ test_schema_validation - ValueError at line 45
```

Run a jest test file:
```bash
/run-test-file C:\Users\willh\.mcp-servers\coderef-workflow tests/unit/plan.test.js
```

Run with verbose output for debugging:
```bash
/run-test-file /path tests/test_integration.py --verbose
```

**Use Cases:**
- Testing changes to specific module
- Debugging specific functionality
- Quick feedback during development
- Validating test-driven development

**When to Use:**
- Working on single feature
- Debugging failing test
- Implementing new functionality
- Quick validation cycles

---

### /run-by-pattern

Execute tests matching a specific name pattern.

**Syntax:**
```bash
run_by_pattern [project_path] [pattern] [--verbose] [--timeout SECONDS]
```

**Pattern Syntax:**
- `*` - Wildcard (any characters)
- `?` - Single character
- `test_*` - Prefix matching
- `*_integration` - Suffix matching
- Regex patterns supported

**Examples:**

Run all authentication tests:
```bash
/run-by-pattern C:\Users\willh\.mcp-servers\coderef-context "test_*auth*"
```

Output:
```
Pattern: test_*auth*
Matched: 7 tests
Running: 7 tests

Results:
  test_auth_parse ✓
  test_auth_validate ✓
  test_auth_token_generation ✓
  test_auth_refresh ✓
  test_auth_expiry ✓
  test_unauthorized_access ✗
  test_invalid_credentials ✓

Summary: 6/7 passed (85.7%)
```

Run all database tests:
```bash
/run-by-pattern /path "test_db_*"
```

Run only security tests:
```bash
/run-by-pattern /path "test_security_*" --verbose
```

Run performance tests with longer timeout:
```bash
/run-by-pattern /path "test_perf_*" --timeout 600
```

**Use Cases:**
- Test by category/functionality
- Run tests for specific feature
- Quick validation of related tests
- Testing without running full suite

**When to Use:**
- Testing specific functionality
- Working on feature category
- Rapid feedback on related changes
- Running logical test groups

---

### /run-parallel

Execute tests with specific parallelization settings.

**Syntax:**
```bash
run_parallel [project_path] --workers N [--timeout SECONDS] [--verbose]
```

**Worker Count Recommendations:**

| System | Recommended | Max |
|--------|-------------|-----|
| Laptop (2-4 core) | 2-3 | 4 |
| Desktop (4-8 core) | 4-6 | 8 |
| Workstation (8-16 core) | 8-12 | 16 |
| Server (16+ core) | 12-20 | 32 |

**Examples:**

Run with 4 workers (good for laptops):
```bash
/run-parallel C:\Users\willh\.mcp-servers\coderef-context --workers 4
```

Output:
```
Configuration:
  Workers: 4
  Total Tests: 45
  Timeout: 300s per test

Execution:
Batch 1: [Test 1-4 running...] → 4 passed in 2.1s
Batch 2: [Test 5-8 running...] → 4 passed in 1.9s
Batch 3: [Test 9-12 running...] → 3 passed, 1 failed in 2.4s
... (continues)

Total Duration: 12.4s (vs 45s sequential)
Speedup: 3.6x
```

High parallelization for server:
```bash
/run-parallel /path --workers 16 --verbose
```

Low parallelization for resource-constrained:
```bash
/run-parallel /path --workers 1 --timeout 600
```

**Use Cases:**
- CI/CD with specific hardware
- Optimizing test suite execution
- Resource-constrained environments
- Load testing

**When to Use:**
- Optimizing test execution time
- Testing on specific hardware
- Dealing with resource constraints
- Performance benchmarking

## Management Tools

### /test-results

View previous test execution results.

**Syntax:**
```bash
test_results [project_path] [--format FORMAT] [--limit N] [--framework FRAMEWORK]
```

**Formats:**
- `summary` - High-level overview (default)
- `markdown` - Formatted for documentation
- `json` - Full data

**Examples:**

View latest results:
```bash
/test-results C:\Users\willh\.mcp-servers\coderef-context
```

Output:
```
Latest Test Results: coderef-context

Run 1: 2025-12-27 14:23:45
  Framework: pytest
  Total: 45 | ✓ 43 | ✗ 2 | ⊘ 0
  Duration: 12.4s
  Status: FAILING

Run 2: 2025-12-27 12:10:30
  Framework: pytest
  Total: 45 | ✓ 45 | ✗ 0 | ⊘ 0
  Duration: 11.8s
  Status: HEALTHY

Run 3: 2025-12-27 10:45:15
  Framework: pytest
  Total: 45 | ✓ 44 | ✗ 1 | ⊘ 0
  Duration: 12.1s
  Status: WARNING
```

View last 10 results:
```bash
/test-results /path --limit 10
```

Export as JSON:
```bash
/test-results /path --format json
```

Filter by framework:
```bash
/test-results /path --framework jest --format markdown
```

**Use Cases:**
- Review test history
- Track regression
- Compare recent runs
- Export for analysis

**When to Use:**
- After test run
- Reviewing progress
- Debugging flaky tests
- Trend analysis

---

### /test-report

Generate formatted test reports.

**Syntax:**
```bash
test_report [project_path] [--format FORMAT] [--output FILE] [--include SECTIONS]
```

**Formats:**
- `markdown` - For docs, GitHub, email
- `html` - For web, dashboards
- `json` - For CI/CD

**Sections:**
- `summary` - Overview stats
- `details` - Individual test results
- `metrics` - Performance, coverage
- `trends` - Historical comparison

**Examples:**

Generate markdown report to console:
```bash
/test-report C:\Users\willh\.mcp-servers\coderef-context
```

Output:
```markdown
# Test Report: coderef-context

**Generated:** 2025-12-27 14:25:30

## Summary
- Framework: pytest
- Total: 45 tests
- Passed: 43 (95.6%) ✓
- Failed: 2 (4.4%) ✗
- Skipped: 0 (0%)
- Duration: 12.4 seconds

## Status
🔴 FAILING - 2 test failures detected

## Failed Tests
1. test_invalid_schema (test_models.py:45)
2. test_deployment_check (test_integration.py:128)
...
```

Generate HTML report:
```bash
/test-report /path --format html --output report.html
```

Generate comprehensive JSON:
```bash
/test-report /path --format json --include summary,details,metrics,trends
```

**Use Cases:**
- Share results with team
- Archive for review
- CI/CD integration
- Documentation

**When to Use:**
- Sharing test results
- Team reviews
- Documentation
- Archival

---

### /compare-runs

Compare two test runs to detect regressions or improvements.

**Syntax:**
```bash
compare_runs [project_path] [run1] [run2] [--format FORMAT]
```

**Examples:**

Compare latest with previous:
```bash
/compare-runs C:\Users\willh\.mcp-servers\coderef-context 2025-12-26T10:00:00 latest
```

Output:
```
Comparison: Run 1 vs Run 2

Trend: REGRESSION 🔴
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tests Changed:
  Before: 45 total | 45 passed | 0 failed
  After:  45 total | 43 passed | 2 failed

Changes:
  ❌ 2 new failures
  ✅ 0 fixed
  ± 0 new tests

Failed Tests (NEW):
  - test_invalid_schema
  - test_deployment_check

Performance:
  Before: 12.1s
  After:  12.4s
  Δ: +0.3s (+2.5%)
```

Compare specific runs:
```bash
/compare-runs /path 2025-12-25T14:00 2025-12-26T14:00
```

Detailed comparison:
```bash
/compare-runs /path run1 run2 --format detailed
```

**Use Cases:**
- Detect regressions
- Verify improvements
- Before/after validation
- CI/CD validation

**When to Use:**
- After code changes
- Release validation
- Performance verification
- Regression detection

## Analysis Tools

### /test-coverage

Analyze code coverage metrics.

**Syntax:**
```bash
test_coverage [project_path] [--format FORMAT] [--threshold N]
```

**Examples:**

Check coverage:
```bash
/test-coverage C:\Users\willh\.mcp-servers\coderef-context
```

Output:
```
Code Coverage Analysis

Total Tests: 45
Passed: 43
Coverage: 95.6%

Coverage Status: EXCELLENT ✅

Top Covered Areas:
- Authentication module: 99.2%
- API handlers: 95.1%
- Database layer: 97.5%

Gaps to Address:
- Error handling: 78.3%
- Edge cases: 82.1%
- Legacy code: 61.5%
```

Detailed coverage:
```bash
/test-coverage /path --format detailed
```

Validate threshold (85%):
```bash
/test-coverage /path --threshold 85
```

**Use Cases:**
- Identify untested code
- Track coverage trends
- Requirements validation
- Quality gates

**When to Use:**
- Adding new features
- After test suite changes
- Quality validation
- Compliance checks

---

### /test-performance

Analyze test execution speed and identify bottlenecks.

**Syntax:**
```bash
test_performance [project_path] [--format FORMAT] [--threshold SECONDS] [--count N]
```

**Examples:**

Overall performance:
```bash
/test-performance C:\Users\willh\.mcp-servers\coderef-context
```

Output:
```
Test Performance Analysis

Execution Metrics:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Duration:   12.4 seconds
Average:          0.27 seconds per test
Median (p50):     0.15 seconds
95th Percentile:  1.1 seconds
99th Percentile:  4.2 seconds

Slowest Tests (Top 5):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. test_database_migration (4.2s) - DB operations
2. test_api_integration (3.8s) - HTTP requests
3. test_file_processing (2.9s) - I/O
4. test_deployment_check (2.4s) - System calls
5. test_external_api (2.1s) - Network

Optimization Opportunities:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ 5 tests > 2 seconds (consider optimization)
💡 Mock external APIs instead of HTTP calls
💡 Use in-memory database for tests
💡 Parallelize independent test groups
```

Find slow tests:
```bash
/test-performance /path --threshold 2.0
```

Show top 10 slowest:
```bash
/test-performance /path --count 10
```

**Use Cases:**
- Identify bottlenecks
- Optimize slow tests
- Performance tracking
- CI/CD optimization

**When to Use:**
- Slow test suite
- Performance improvement
- Optimization work
- Benchmarking

---

### /test-trends

Show historical trends in test results.

**Syntax:**
```bash
test_trends [project_path] [--days N] [--metric METRIC] [--format FORMAT]
```

**Metrics:**
- `pass_rate` - Percentage passing
- `failures` - Number failing
- `duration` - Execution time
- `coverage` - Code coverage

**Examples:**

Last week of trends:
```bash
/test-trends C:\Users\willh\.mcp-servers\coderef-context
```

Output:
```
Test Trends: coderef-context (Last 7 days)

Metric: Pass Rate
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Day  Date         Pass Rate  Trend
 1   2025-12-27   95.6%      ↘ -2.2%
 2   2025-12-26   97.8%      ↗ +1.1%
 3   2025-12-25   96.7%      ↘ -2.3%
 4   2025-12-24   99.0%      → Same
 5   2025-12-23   99.0%      ↗ +4.4%
 6   2025-12-22   94.6%      ↗ +1.1%
 7   2025-12-21   93.5%      (baseline)

Analysis:
- Overall Trend: UNSTABLE
- Volatility: High (2-4% swings)
- Recommendation: Investigate recent changes
```

Failure trends:
```bash
/test-trends /path --metric failures --days 14
```

Duration trends:
```bash
/test-trends /path --metric duration --format chart
```

**Use Cases:**
- Spot regressions
- Track improvements
- Quality monitoring
- Trend analysis

**When to Use:**
- Weekly reviews
- Detecting degradation
- Improvement tracking
- Quality monitoring

---

### /detect-flaky

Find intermittently failing tests.

**Syntax:**
```bash
detect_flaky [project_path] [--min-flakiness N] [--runs N] [--format FORMAT]
```

**Examples:**

Find flaky tests:
```bash
/detect-flaky C:\Users\willh\.mcp-servers\coderef-context
```

Output:
```
Flaky Test Detection

Analysis: Last 5 test runs
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Found: 3 Flaky Tests

🔴 CRITICAL (40-60% flaky)
- test_external_api_call (56% flaky)
  Passed: 2/5 | Failed: 3/5
  Pattern: Fails randomly (network timeout)

🟡 WARNING (20-40% flaky)
- test_concurrent_access (28% flaky)
  Passed: 4/5 | Failed: 1/5
  Pattern: Fails under load

Recommendations for test_external_api_call:
  → Mock API responses (no live calls)
  → Add retry logic with exponential backoff
  → Increase timeout to handle slow networks
```

Detailed analysis:
```bash
/detect-flaky /path --runs 10 --format detailed
```

High flakiness threshold:
```bash
/detect-flaky /path --min-flakiness 30
```

**Use Cases:**
- Quality improvement
- Reliability enhancement
- Test maintenance
- Infrastructure improvement

**When to Use:**
- Regular maintenance
- Before releases
- Quality improvements
- Test reliability focus

---

### /test-health

Overall test suite health check.

**Syntax:**
```bash
test_health [project_path] [--detailed]
```

**Examples:**

Quick health check:
```bash
/test-health C:\Users\willh\.mcp-servers\coderef-context
```

Output:
```
Test Suite Health: coderef-context

Health Score: 87/100  Grade: B
Status: HEALTHY ✅

Metrics:
  Pass Rate:   95.6% (43/45)
  Error Rate:  0% (0/45)
  Skip Rate:   4.4% (2/45)

Performance:
  Duration:    12.4 seconds
  Average:     0.27s per test
  p95:         1.1 seconds

Summary:
  • Strong pass rate (95.6%)
  • No critical errors
  • Good performance profile
  • 2 tests skipped (check if intentional)

Recommendations:
  ✓ Passing (no changes needed)
  ⚠ Review skipped tests
  💡 Consider increasing to 98%+
```

Detailed health check:
```bash
/test-health /path --detailed
```

**Use Cases:**
- Status monitoring
- Quality oversight
- Team reporting
- Requirement validation

**When to Use:**
- Daily monitoring
- Team standup
- Progress tracking
- Release validation

## Common Workflows

### Workflow 1: Daily Development

```bash
# 1. Run tests after coding
/run-tests C:\Users\willh\.mcp-servers\coderef-context

# 2. Check health
/test-health C:\Users\willh\.mcp-servers\coderef-context

# 3. If failures, debug with verbose output
/run-test-file C:\Users\willh\.mcp-servers\coderef-context tests/failing_test.py --verbose

# 4. Repeat until passing
```

### Workflow 2: Feature Implementation

```bash
# 1. Discover current state
/discover-tests /path/to/feature

# 2. Run tests for feature category
/run-by-pattern /path "test_feature_*"

# 3. Track progress
/test-results /path --limit 5

# 4. Before commit, full run
/run-tests /path

# 5. Verify health
/test-health /path
```

### Workflow 3: Performance Optimization

```bash
# 1. Get current performance baseline
/test-performance /path

# 2. Identify slow tests
/test-performance /path --threshold 2.0

# 3. Run with more workers
/run-parallel /path --workers 16

# 4. Compare before/after
/compare-runs /path baseline-run latest

# 5. Monitor trends
/test-trends /path --metric duration
```

### Workflow 4: Flaky Test Fix

```bash
# 1. Detect flaky tests
/detect-flaky /path --runs 10

# 2. Analyze specific test
/run-test-file /path tests/flaky_test.py --verbose

# 3. Apply fix

# 4. Verify fix
/run-test-file /path tests/flaky_test.py --verbose

# 5. Monitor to confirm
/test-trends /path --days 3
```

### Workflow 5: Release Validation

```bash
# 1. Full test run
/run-tests /path --verbose

# 2. Health check
/test-health /path --detailed

# 3. Coverage verification
/test-coverage /path --threshold 85

# 4. Regression check
/test-trends /path --days 7

# 5. Generate report
/test-report /path --format html --output release-report.html
```

## Troubleshooting

### Tests Not Found

**Problem:** `/discover-tests` shows 0 tests

**Solutions:**
1. Verify project path is correct
2. Check test directory structure
3. Verify configuration files exist (pyproject.toml, package.json)
4. Check test file naming conventions

**Debug:**
```bash
/list-frameworks /path
```

---

### Timeout Errors

**Problem:** Tests timeout during execution

**Solutions:**
1. Increase timeout: `--timeout 600`
2. Check for network calls or I/O
3. Reduce parallelization: `--workers 2`
4. Profile with `/test-performance`

**Debug:**
```bash
/test-performance /path --count 10
/run-tests /path --timeout 600 --workers 2
```

---

### High Failure Rate

**Problem:** Many tests failing

**Solutions:**
1. Run with verbose output
2. Check health status
3. Look for environment issues
4. Check test dependencies

**Debug:**
```bash
/test-health /path --detailed
/run-tests /path --verbose
/detect-flaky /path --runs 5
```

---

### Flaky Tests

**Problem:** Tests pass sometimes, fail other times

**Solutions:**
1. Run multiple times to confirm
2. Mock external dependencies
3. Add test isolation
4. Use deterministic values

**Debug:**
```bash
/detect-flaky /path --runs 10 --format detailed
/run-test-file /path tests/flaky.py --verbose
```

## Advanced Usage

### Parallel Testing Across Projects

```bash
# Test all CodeRef servers in parallel
/run-tests C:\Users\willh\.mcp-servers\coderef-context --workers 8
/run-tests C:\Users\willh\.mcp-servers\coderef-workflow --workers 8
/run-tests C:\Users\willh\.mcp-servers\coderef-docs --workers 8
```

### Custom Pattern Matching

```bash
# Run only integration tests
/run-by-pattern /path "*integration*"

# Run only security tests
/run-by-pattern /path "test_security_*"

# Run slow tests with more time
/run-by-pattern /path "test_*migration*" --timeout 600
```

### Result Export for CI/CD

```bash
# Export JSON for processing
/test-report /path --format json --output results.json

# Then parse in CI/CD:
# - Check health score >= 80
# - Check coverage >= 85%
# - Check no new failures
```

### Continuous Monitoring

```bash
# Daily health check
/test-health /path --detailed

# Weekly trend review
/test-trends /path --days 7

# Monthly flaky analysis
/detect-flaky /path --runs 30
```

---

**Need Help?** See [README.md](README.md) for overview and [TESTING_GUIDE.md](TESTING_GUIDE.md) for architecture details.
