# coderef-testing User Guide

**Complete tutorial for universal test orchestration**

---

## Purpose

This guide helps you use coderef-testing to run, analyze, and report on tests across any project, regardless of programming language or test framework.

## Overview

coderef-testing is an MCP server that provides:
- **Framework-agnostic** test execution (pytest, jest, vitest, cargo, mocha)
- **Unified results** across all frameworks
- **Comprehensive analysis** (coverage, performance, flaky detection, health scoring)
- **Multiple report formats** (markdown, HTML, JSON)

---

## Prerequisites

### Required
- **Claude Code** with MCP support
- **Python 3.11+** (for the MCP server)
- **Test framework** installed in your project:
  - Python: pytest
  - JavaScript: jest, vitest, or mocha
  - Rust: cargo

### Optional
- **Node.js** (for JavaScript project testing)
- **Rust** (for Rust project testing)

---

## Installation

### Step 1: Install the MCP Server

```bash
cd C:/Users/willh/.mcp-servers/coderef-testing
uv sync
```

### Step 2: Configure MCP

Add to `~/.mcp.json`:

```json
{
  "mcpServers": {
    "coderef-testing": {
      "command": "python",
      "args": ["C:/Users/willh/.mcp-servers/coderef-testing/server.py"],
      "disabled": false
    }
  }
}
```

### Step 3: Restart Claude Code

Close and reopen Claude Code to load the MCP server.

### Step 4: Verify Installation

```bash
/discover-tests C:/path/to/your/project
```

If you see test files listed, installation succeeded!

---

## How It Works

### Architecture

```
Your Project
    ↓
Framework Detection (auto-detect pytest/jest/cargo)
    ↓
Test Execution (parallel with configurable workers)
    ↓
Result Normalization (unified JSON schema)
    ↓
Analysis & Reporting
    ↓
Archive with Timestamp
```

### Unified Result Schema

All frameworks produce the same result structure:

```json
{
  "project": "/path/to/project",
  "framework": {"framework": "pytest", "version": "7.4.3"},
  "summary": {
    "total": 247,
    "passed": 245,
    "failed": 2,
    "success_rate": 99.19
  },
  "tests": [
    {"name": "test_foo", "status": "passed", "duration": 0.5}
  ],
  "coverage": {"coverage_percent": 85.0}
}
```

This enables cross-project comparisons and unified reporting.

---

## Getting Started

### Tutorial 1: Run Your First Test

**Goal:** Execute tests on a Python project

```bash
# Step 1: Discover tests
/discover-tests /path/to/python-project

# Expected output:
# ✅ Detected: pytest 7.4.3
# Found 25 test files in tests/

# Step 2: Run tests
/run-tests /path/to/python-project

# Expected output:
# ✅ 245 passed, 2 failed (99.19% success)
# Duration: 12.5s

# Step 3: View results
/test-results /path/to/python-project
```

**What happened:**
1. Framework auto-detected (pytest)
2. Tests executed in parallel (4 workers by default)
3. Results normalized and archived
4. Summary displayed

### Tutorial 2: Analyze Test Coverage

**Goal:** Find untested code

```bash
# Run tests with coverage
/run-tests /path/to/project

# Analyze coverage
/test-coverage /path/to/project

# Expected output:
# Coverage: 85.0%
# Covered: 850 lines
# Missing: 150 lines
# Recommendations:
#   - Add tests for src/utils.py (50 uncovered lines)
#   - Cover error paths in src/auth.py
```

**Action items:**
1. Review missing lines
2. Write tests for uncovered code
3. Re-run to verify improvement

### Tutorial 3: Optimize Test Speed

**Goal:** Make tests run faster

```bash
# Step 1: Identify slow tests
/test-performance /path/to/project --threshold 1.0

# Expected output:
# Slow tests (>1.0s):
#   - test_db_migration (5.3s)
#   - test_integration (3.2s)
#   - test_external_api (2.1s)

# Step 2: Run with more workers
/run-parallel /path/to/project --workers 16

# Before: 60s (4 workers)
# After:  18s (16 workers)
# Improvement: 3.3x faster
```

**Pro tips:**
- Scale workers to CPU cores (8-core = 8-16 workers)
- Mock external dependencies in slow tests
- Use in-memory databases

### Tutorial 4: Find Flaky Tests

**Goal:** Detect intermittent failures

```bash
# Run tests multiple times
/detect-flaky /path/to/project --runs 10

# Expected output:
# Flaky tests found: 2
#   - test_async_timeout (fails 40% of time)
#   - test_race_condition (fails 20% of time)
# Recommendations:
#   - Add proper async cleanup
#   - Fix shared state issues
```

**Fixing flaky tests:**
1. Add `await` for async operations
2. Reset global state in teardown
3. Use deterministic values (no random data)
4. Mock time-dependent logic

### Tutorial 5: Health Check Before Deployment

**Goal:** Ensure test suite quality

```bash
# Full health check
/test-health /path/to/project

# Expected output:
# Health Score: 92.5 (Grade: A)
# Breakdown:
#   - Correctness: 40/40 (99.19% pass rate)
#   - Coverage: 25.5/30 (85% coverage)
#   - Speed: 18/20 (avg 0.05s per test)
#   - Stability: 9/10 (95% stability)
# Recommendations:
#   - Improve coverage to 90%
#   - Fix 2 flaky tests
```

**Grading scale:**
- A (90-100): Excellent, ready to ship
- B (80-89): Good, minor improvements
- C (70-79): Acceptable, needs work
- D (60-69): Poor, major issues
- F (<60): Failing, do not deploy

---

## Use Cases

### Use Case 1: Daily Development

**Scenario:** You're developing a feature and want fast feedback.

```bash
# Run only related tests
/run-test-file /path/to/project tests/test_auth.py

# Check if you broke anything
/test-results /path/to/project --latest
```

**Best practices:**
- Run tests locally before pushing
- Use `/run-test-file` for TDD workflow
- Check coverage on new code

### Use Case 2: Pre-Commit Hook

**Scenario:** Ensure quality before committing.

```bash
# Add to .git/hooks/pre-commit
/test-health /path/to/project --threshold 80

# Fails if health score < 80
# Prevents commits with failing/slow/flaky tests
```

### Use Case 3: CI/CD Pipeline

**Scenario:** Run tests in GitHub Actions.

```yaml
# .github/workflows/test.yml
- name: Run tests
  run: /run-tests . --workers 16 --format json --output results.json

- name: Generate report
  run: /test-report . --format html --output test-report.html

- name: Upload results
  uses: actions/upload-artifact@v3
  with:
    name: test-results
    path: test-report.html
```

### Use Case 4: Multi-Project Testing

**Scenario:** Test all 4 CodeRef servers simultaneously.

```bash
# Run tests on multiple projects
/run-tests C:/Users/willh/.mcp-servers/coderef-context
/run-tests C:/Users/willh/.mcp-servers/coderef-workflow
/run-tests C:/Users/willh/.mcp-servers/coderef-docs
/run-tests C:/Users/willh/.mcp-servers/coderef-personas

# Compare results
/compare-runs coderef-context 2025-12-26 2025-12-27
```

### Use Case 5: Debugging Test Failures

**Scenario:** Tests are failing intermittently.

```bash
# Step 1: Identify flaky tests
/detect-flaky /path/to/project --runs 10

# Step 2: Run single worker (easier to debug)
/run-parallel /path/to/project --workers 1

# Step 3: Check detailed output
/test-results /path/to/project --verbose
```

---

## Best Practices

### DO ✅

**Run tests frequently**
```bash
# During development
/run-test-file . tests/test_feature.py

# Before commit
/test-health .
```

**Use appropriate workers**
```bash
# Development laptop (4 cores)
/run-tests . --workers 4

# CI server (16 cores)
/run-tests . --workers 16
```

**Track trends over time**
```bash
/test-trends . --days 7
```

**Fix flaky tests immediately**
```bash
/detect-flaky . --runs 5
# Address flaky tests before they spread
```

### DON'T ❌

**Don't ignore failing tests**
```bash
# ❌ BAD
# Commenting out failing tests

# ✅ GOOD
# Fix the test or the code
```

**Don't skip coverage checks**
```bash
# ❌ BAD
# Merging code without coverage

# ✅ GOOD
/test-coverage . --threshold 80
```

**Don't use too many workers**
```bash
# ❌ BAD (CPU thrashing)
/run-tests . --workers 100

# ✅ GOOD (match CPU cores)
/run-tests . --workers 8
```

### TIPS 💡

**Parallel testing gotchas:**
- Tests must be isolated (no shared state)
- Database tests need separate schemas
- File I/O tests need unique temp files

**Speed optimization:**
- Mock external APIs
- Use in-memory databases
- Parallelize at file level, not test level

**Coverage targets:**
- Critical paths: 100%
- Business logic: 90%
- UI components: 70%
- Overall: 80%

---

## Troubleshooting

### Issue: Framework Not Detected

**Symptom:** `No test framework detected`

**Solutions:**
1. Check config file exists:
   ```bash
   # Python: pyproject.toml with [tool.pytest]
   # JavaScript: package.json with jest/vitest
   # Rust: Cargo.toml with [dev-dependencies]
   ```

2. Install framework:
   ```bash
   # Python
   pip install pytest

   # JavaScript
   npm install jest
   ```

### Issue: Tests Timeout

**Symptom:** `Test execution exceeded timeout`

**Solutions:**
```bash
# Increase timeout
/run-tests . --timeout 600  # 10 minutes

# Or reduce test scope
/run-test-category . "unit"
```

### Issue: Flaky Tests on CI But Not Locally

**Common causes:**
- Timing differences (CI is slower)
- Parallel execution issues
- Environment variables

**Solution:**
```bash
# Run with same config as CI
/run-tests . --workers 16 --timeout 300
```

### Issue: Coverage Too Low

**Strategy:**
1. Find gaps:
   ```bash
   /test-coverage . --detailed
   ```

2. Prioritize critical paths

3. Write tests incrementally

4. Track improvement:
   ```bash
   /test-trends . --metric coverage
   ```

---

## Quick Reference

### Common Commands

| Task | Command |
|------|---------|
| Run all tests | `/run-tests /path` |
| Run one file | `/run-test-file /path tests/test_foo.py` |
| Check coverage | `/test-coverage /path` |
| Find slow tests | `/test-performance /path` |
| Health check | `/test-health /path` |
| Compare runs | `/compare-runs /path 2025-12-26 2025-12-27` |

### Framework Detection

| Framework | Config File | Test Directory |
|-----------|-------------|----------------|
| pytest | pyproject.toml | tests/ |
| jest | package.json | __tests__/ or *.test.js |
| vitest | vitest.config.ts | *.test.ts |
| cargo | Cargo.toml | tests/ |
| mocha | package.json | test/ |

### Result Archive

All results saved to:
```
coderef/testing/results/YYYY-MM-DD/HH-MM-SS.json
```

Access with:
```bash
/test-results /path --date 2025-12-27
```

---

## Next Steps

1. **Run your first test suite**
   ```bash
   /run-tests /path/to/your/project
   ```

2. **Check test health**
   ```bash
   /test-health /path/to/your/project
   ```

3. **Set up CI/CD integration**
   - Add to GitHub Actions
   - Generate HTML reports
   - Track trends over time

4. **Optimize test speed**
   - Find slow tests
   - Increase parallelization
   - Mock external dependencies

5. **Improve coverage**
   - Identify gaps
   - Write missing tests
   - Track improvement

---

## Support

- **Documentation:** `coderef/foundation-docs/`
- **Tool Reference:** `coderef/user/my-guide.md`
- **Quick Reference:** `coderef/user/quickref.md`
- **Examples:** See "Use Cases" section above

---

*Version: 1.0.0 | Last Updated: 2025-12-27*
