# coderef-testing Features

**What coderef-testing can do for you**

---

## Purpose

This document showcases all features available in coderef-testing, organized by capability area.

## Overview

coderef-testing provides **14 MCP tools** across **4 categories** for comprehensive test orchestration:

1. **Discovery** - Find and identify tests
2. **Execution** - Run tests with control
3. **Management** - Organize and report results
4. **Analysis** - Gain insights from results

---

## Core Capabilities

### 1. Framework-Agnostic Testing

**What it does:**
Automatically detects and runs tests regardless of programming language or framework.

**Supported Frameworks:**
- ✅ **pytest** (Python)
- ✅ **jest** (JavaScript/TypeScript)
- ✅ **vitest** (Vite/JavaScript)
- ✅ **cargo** (Rust)
- ✅ **mocha** (Node.js)

**Use cases:**
- Test monorepos with multiple languages
- Switch between projects without configuration
- Onboard new frameworks without code changes

**Example:**
```bash
# Works on Python project
/run-tests /path/to/python-app

# Works on JavaScript project
/run-tests /path/to/js-app

# Works on Rust project
/run-tests /path/to/rust-app
```

**Benefits:**
- No manual configuration needed
- Consistent interface across all projects
- Learn once, use everywhere

---

### 2. Parallel Test Execution

**What it does:**
Runs tests concurrently to reduce execution time.

**Features:**
- Configurable worker count (1-20+)
- Auto-detects CPU cores
- Proper test isolation
- Timeout enforcement

**Use cases:**
- Speed up large test suites
- Optimize CI/CD pipelines
- Debug race conditions (use 1 worker)

**Example:**
```bash
# Default (4 workers)
/run-tests /path

# High-performance (16 workers)
/run-parallel /path --workers 16

# Sequential (debugging)
/run-parallel /path --workers 1
```

**Performance gains:**
| Test Count | Sequential | 4 Workers | 16 Workers |
|------------|------------|-----------|------------|
| 100 tests | 12s | 5s | 3s |
| 500 tests | 60s | 18s | 10s |
| 1000 tests | 120s | 35s | 20s |

**Benefits:**
- 3-6x faster test execution
- Better resource utilization
- Configurable per use case

---

### 3. Unified Result Format

**What it does:**
Normalizes results from all frameworks into a single schema.

**Schema:**
```json
{
  "project": "/path",
  "framework": {"framework": "pytest", "version": "7.4.3"},
  "summary": {"total": 247, "passed": 245, "failed": 2},
  "tests": [{"name": "test_foo", "status": "passed", "duration": 0.5}],
  "coverage": {"coverage_percent": 85.0}
}
```

**Use cases:**
- Compare test quality across projects
- Aggregate results from multiple frameworks
- Build custom dashboards

**Example:**
```bash
# Run tests on different frameworks
/run-tests /python-project  # pytest results
/run-tests /js-project      # jest results

# Both produce same result format
# Can compare, aggregate, report uniformly
```

**Benefits:**
- Cross-project comparisons
- Unified reporting
- Framework-agnostic tooling

---

### 4. Comprehensive Analysis

**What it does:**
Analyzes test results across 4 dimensions.

#### Coverage Analysis

**Features:**
- Line coverage percentage
- Missing line identification
- Uncovered file detection
- Improvement recommendations

**Example:**
```bash
/test-coverage /path

# Output:
# Coverage: 85.0%
# Uncovered files:
#   - src/utils.py (50 lines)
#   - src/helpers.py (30 lines)
```

#### Performance Analysis

**Features:**
- Percentile metrics (p50, p95, p99)
- Slow test identification
- Duration trending
- Optimization suggestions

**Example:**
```bash
/test-performance /path --threshold 2.0

# Output:
# Slow tests (>2.0s):
#   - test_db_migration (5.3s)
#   - test_integration (3.2s)
```

#### Flaky Test Detection

**Features:**
- Multi-run analysis
- Flakiness scoring (0-100%)
- Pattern identification
- Fix recommendations

**Example:**
```bash
/detect-flaky /path --runs 10

# Output:
# Flaky tests:
#   - test_async (40% flakiness)
#   - test_race (20% flakiness)
```

#### Health Scoring

**Features:**
- 0-100 score with A-F grading
- 4-component breakdown (correctness, coverage, speed, stability)
- Actionable recommendations
- Trend tracking

**Example:**
```bash
/test-health /path

# Output:
# Health: 92.5 (Grade: A)
# Breakdown:
#   - Correctness: 40/40
#   - Coverage: 25.5/30
#   - Speed: 18/20
#   - Stability: 9/10
```

**Benefits:**
- Single metric for test quality
- Prioritized improvements
- Easy to track over time

---

### 5. Multiple Report Formats

**What it does:**
Generates reports in different formats for different audiences.

**Formats:**
- **Markdown** - For documentation and sharing
- **HTML** - For web dashboards
- **JSON** - For CI/CD integration

**Use cases:**
- Share with stakeholders (HTML)
- Include in docs (Markdown)
- Parse in scripts (JSON)

**Example:**
```bash
# Markdown for README
/test-report /path --format markdown > TEST_REPORT.md

# HTML for dashboard
/test-report /path --format html > dashboard.html

# JSON for scripts
/test-report /path --format json > results.json
```

**Benefits:**
- Flexible output for any workflow
- Beautiful HTML dashboards
- Machine-parseable JSON

---

### 6. Historical Tracking

**What it does:**
Archives all results with timestamps for trend analysis.

**Features:**
- ISO 8601 timestamps
- Organized by date (YYYY-MM-DD)
- Automatic archival
- Query by date range

**Storage:**
```
coderef/testing/results/
├── 2025-12-26/
│   ├── 10-30-00.json
│   └── 15-45-00.json
└── 2025-12-27/
    ├── 09-00-00.json
    └── 14-30-00.json
```

**Use cases:**
- Track test quality over time
- Detect regressions
- Measure improvement

**Example:**
```bash
# Compare today vs yesterday
/compare-runs /path 2025-12-26 2025-12-27

# Output:
# Success rate: 98.5% → 99.19% (+0.69%)
# Duration: 15.2s → 12.5s (-2.7s)
# New failures: 1
# Fixed tests: 6
```

**Benefits:**
- Complete test history
- Regression detection
- Progress tracking

---

## Feature Comparison

### vs Manual Test Execution

| Feature | Manual | coderef-testing |
|---------|--------|-----------------|
| Framework support | One at a time | All frameworks |
| Parallel execution | Manual setup | Automatic |
| Result format | Framework-specific | Unified |
| Analysis | Manual | Automated |
| Historical tracking | Manual | Automatic |
| Report generation | Manual | One command |

### vs pytest-only / jest-only

| Feature | Framework-specific | coderef-testing |
|---------|-------------------|-----------------|
| Multi-language | ❌ | ✅ |
| Universal API | ❌ | ✅ |
| Cross-project comparison | ❌ | ✅ |
| Unified reports | ❌ | ✅ |
| Health scoring | ❌ | ✅ |

---

## Benefits by User Type

### For Developers

**What you get:**
- ✅ Fast feedback (parallel execution)
- ✅ Easy debugging (flaky test detection)
- ✅ Quality metrics (health scoring)
- ✅ Simple commands (no config needed)

**Example workflow:**
```bash
# During development
/run-test-file . tests/test_feature.py

# Before commit
/test-health .

# After fix
/detect-flaky .
```

### For QA Engineers

**What you get:**
- ✅ Comprehensive analysis (coverage, performance, flakiness)
- ✅ Detailed reports (HTML dashboards)
- ✅ Trend tracking (historical data)
- ✅ Multi-project testing (monorepos)

**Example workflow:**
```bash
# Daily health check
/test-health /all/projects

# Weekly analysis
/test-trends . --days 7

# Monthly report
/test-report . --format html --output qa-report.html
```

### For DevOps / CI/CD

**What you get:**
- ✅ CI/CD integration (JSON output)
- ✅ Parallel execution (faster pipelines)
- ✅ Quality gates (health scoring)
- ✅ Artifact generation (HTML reports)

**Example workflow:**
```yaml
# GitHub Actions
- run: /run-tests . --workers 16 --format json
- run: /test-report . --format html
- run: /test-health . --threshold 80
```

### For Team Leads / Managers

**What you get:**
- ✅ Quality metrics (0-100 health score)
- ✅ Trend visualization (improvement over time)
- ✅ Multi-project overview (entire codebase)
- ✅ Stakeholder reports (HTML dashboards)

**Example workflow:**
```bash
# Monthly review
/test-trends /all/projects --days 30
/test-report /all/projects --format html
```

---

## Advanced Features

### Selective Test Execution

**What it does:**
Run subsets of tests based on patterns or tags.

**Example:**
```bash
# Run only auth tests
/run-test-category . "test_auth"

# Run integration tests
/run-test-category . "@tag:integration"

# Run slow tests
/run-test-category . "@slow"
```

**Benefits:**
- Faster feedback loops
- Test specific features
- Category-based CI/CD

### Test File Targeting

**What it does:**
Run tests from a specific file.

**Example:**
```bash
/run-test-file . tests/integration/test_api.py
```

**Benefits:**
- TDD workflow
- Debug specific failures
- Incremental testing

### Result Comparison

**What it does:**
Diff results between two test runs.

**Example:**
```bash
/compare-runs . 2025-12-26 2025-12-27

# Output:
# Total: 247 → 247 (no change)
# Passed: 240 → 245 (+5)
# Failed: 7 → 2 (-5)
# New failures: test_foo
# Fixed tests: test_bar, test_baz, ...
```

**Benefits:**
- Regression detection
- Progress tracking
- Change impact analysis

---

## Feature Roadmap

### v1.0 (Current) ✅
- Framework auto-detection
- Parallel execution
- Unified results
- Coverage/performance/flaky/health analysis
- Multiple report formats
- Historical tracking

### v1.1 (Planned)
- Real-time test streaming
- Smart test selection (run only affected tests)
- Custom analysis plugins
- Web dashboard UI

### v2.0 (Future)
- Distributed execution (multi-machine)
- Cloud test execution (AWS Lambda, Cloud Run)
- Machine learning for flaky prediction
- Test generation from code

---

## Summary

coderef-testing provides **everything you need** for professional test orchestration:

✅ **14 tools** for discovery, execution, management, and analysis
✅ **5 frameworks** supported out of the box
✅ **4 analysis types** (coverage, performance, flaky, health)
✅ **3 report formats** (markdown, HTML, JSON)
✅ **Unlimited historical tracking** with automatic archival

**Get started today:**
```bash
/run-tests /path/to/your/project
```

---

*Version: 1.0.0 | Last Updated: 2025-12-27*
