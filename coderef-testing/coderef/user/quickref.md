# coderef-testing Quick Reference

**Scannable reference for universal test orchestration**

---

## At a Glance

| What | Value |
|------|-------|
| **Type** | MCP Server / Testing Tool |
| **Purpose** | Universal test orchestration across any framework |
| **Frameworks** | pytest, jest, vitest, cargo, mocha |
| **Tools** | 14 MCP tools |
| **Commands** | 14 slash commands |

---

## Quick Start (30 seconds)

```bash
# 1. Run tests
/run-tests /path/to/project

# 2. Check health
/test-health /path/to/project

# 3. View results
/test-results /path/to/project
```

---

## Essential Commands

### Run Tests
```bash
/run-tests <path>                    # Full suite
/run-test-file <path> <file>         # Single file
/run-parallel <path> --workers 16    # Custom parallelization
```

### View Results
```bash
/test-results <path>                 # Latest results
/test-report <path> --format html    # Generate report
/compare-runs <path> <date1> <date2> # Compare two runs
```

### Analysis
```bash
/test-coverage <path>                # Code coverage
/test-performance <path>             # Find slow tests
/detect-flaky <path> --runs 10       # Find flaky tests
/test-health <path>                  # Health score (0-100)
```

### Discovery
```bash
/discover-tests <path>               # Find all tests
/list-frameworks <path>              # Show detected frameworks
```

---

## Common Workflows

### Development
```bash
# TDD workflow
/run-test-file . tests/test_feature.py
/test-coverage .

# Pre-commit
/test-health .
/detect-flaky .
```

### CI/CD
```bash
# Fast execution
/run-tests . --workers 16

# Generate artifacts
/test-report . --format html --output report.html

# Quality gate
/test-health . --threshold 80
```

### Debugging
```bash
# Sequential execution (easier to debug)
/run-parallel . --workers 1

# Detailed output
/test-results . --verbose

# Find flaky tests
/detect-flaky . --runs 10
```

---

## MCP Tools Reference

### Discovery (2 tools)

**discover_tests**
```json
{"project_path": "/path"}
→ Returns: test files, frameworks, config files
```

**list_test_frameworks**
```json
{"project_path": "/path"}
→ Returns: framework name, version, config
```

### Execution (4 tools)

**run_all_tests**
```json
{
  "project_path": "/path",
  "framework": "pytest",        // optional (auto-detect)
  "parallel_workers": 8,         // optional (default: 4)
  "timeout": 300                 // optional (default: 300)
}
→ Returns: UnifiedTestResults
```

**run_test_file**
```json
{
  "project_path": "/path",
  "test_file": "tests/test_foo.py"
}
→ Returns: UnifiedTestResults (file only)
```

**run_test_category**
```json
{
  "project_path": "/path",
  "pattern": "test_auth"         // or "@tag:integration"
}
→ Returns: UnifiedTestResults (matching only)
```

**run_tests_in_parallel**
```json
{
  "project_path": "/path",
  "parallel_workers": 16
}
→ Returns: UnifiedTestResults
```

### Management (4 tools)

**get_test_results**
```json
{
  "project_path": "/path",
  "date": "2025-12-27"           // optional (default: latest)
}
→ Returns: archived results
```

**aggregate_results**
```json
{"project_path": "/path"}
→ Returns: summary across multiple runs
```

**generate_test_report**
```json
{
  "project_path": "/path",
  "format": "html"               // markdown | html | json
}
→ Returns: formatted report
```

**compare_test_runs**
```json
{
  "project_path": "/path",
  "date1": "2025-12-26",
  "date2": "2025-12-27"
}
→ Returns: diff with trends
```

### Analysis (4 tools)

**analyze_coverage**
```json
{"project_path": "/path"}
→ Returns: coverage %, missing lines, recommendations
```

**detect_flaky_tests**
```json
{
  "project_path": "/path",
  "runs": 10                     // optional (default: 5)
}
→ Returns: flaky tests with scores
```

**analyze_test_performance**
```json
{
  "project_path": "/path",
  "threshold": 2.0               // optional (default: 1.0)
}
→ Returns: slow tests, percentiles
```

**validate_test_health**
```json
{"project_path": "/path"}
→ Returns: health score (0-100), grade (A-F), breakdown
```

---

## Result Schema

### UnifiedTestResults
```json
{
  "project": "/path/to/project",
  "framework": {
    "framework": "pytest",
    "version": "7.4.3",
    "config_file": "pyproject.toml"
  },
  "summary": {
    "total": 247,
    "passed": 245,
    "failed": 2,
    "skipped": 0,
    "duration": 12.5,
    "success_rate": 99.19
  },
  "tests": [
    {
      "name": "test_foo",
      "status": "passed",           // passed | failed | skipped | error
      "duration": 0.5,
      "file": "tests/test_foo.py",
      "line": 10
    }
  ],
  "coverage": {
    "covered_lines": 850,
    "total_lines": 1000,
    "coverage_percent": 85.0
  },
  "timestamp": "2025-12-27T12:00:00Z"
}
```

---

## Framework Detection

| Framework | Indicators | Config File |
|-----------|-----------|-------------|
| **pytest** | tests/, conftest.py | pyproject.toml, pytest.ini |
| **jest** | \_\_tests\_\_/, *.test.js | package.json, jest.config.js |
| **vitest** | *.test.ts | vitest.config.ts |
| **cargo** | tests/ | Cargo.toml |
| **mocha** | test/ | package.json, .mocharc.json |

---

## Performance Tips

### Speed Up Tests
```bash
# Use more workers (scale to CPU cores)
/run-tests . --workers 16

# Mock external dependencies
# Use in-memory databases
# Parallelize at file level
```

### Optimize Coverage
```bash
# Find gaps
/test-coverage . --detailed

# Prioritize critical paths
# Test happy path + error cases
# Track improvement over time
```

### Fix Flaky Tests
```bash
# Identify
/detect-flaky . --runs 10

# Common fixes:
# - Add proper async/await
# - Reset shared state in teardown
# - Use deterministic values (no random)
# - Mock time-dependent logic
```

---

## Health Scoring

### Formula
```
health_score = (0.4 × success_rate) +
               (0.3 × coverage) +
               (0.2 × speed_score) +
               (0.1 × stability)
```

### Grading
| Score | Grade | Meaning |
|-------|-------|---------|
| 90-100 | A | Excellent - ready to ship |
| 80-89 | B | Good - minor improvements |
| 70-79 | C | Acceptable - needs work |
| 60-69 | D | Poor - major issues |
| <60 | F | Failing - do not deploy |

---

## Troubleshooting

### Framework Not Detected
```bash
# Check config file exists
ls pyproject.toml  # pytest
ls package.json    # jest/vitest/mocha
ls Cargo.toml      # cargo

# Install framework
pip install pytest
npm install jest
```

### Tests Timeout
```bash
# Increase timeout
/run-tests . --timeout 600

# Or reduce scope
/run-test-category . "unit"
```

### High Memory Usage
```bash
# Reduce workers
/run-parallel . --workers 4

# Run sequentially
/run-parallel . --workers 1
```

---

## File Locations

### Results Archive
```
coderef/testing/results/
├── 2025-12-27/
│   ├── 10-00-00.json
│   └── 14-30-00.json
```

### Documentation
```
coderef/user/
├── my-guide.md          # This file
├── USER-GUIDE.md        # Comprehensive tutorial
├── FEATURES.md          # Feature overview
└── quickref.md          # Quick reference

coderef/foundation-docs/
├── ARCHITECTURE.md      # System design
├── API.md               # MCP tool reference
├── COMPONENTS.md        # Implementation details
└── SCHEMA.md            # Data models
```

---

## CI/CD Integration

### GitHub Actions
```yaml
- name: Run tests
  run: |
    /run-tests . --workers 16 --format json

- name: Generate report
  run: |
    /test-report . --format html --output test-report.html

- name: Health check (quality gate)
  run: |
    /test-health . --threshold 80
```

### GitLab CI
```yaml
test:
  script:
    - /run-tests . --workers 16
    - /test-report . --format html
    - /test-health . --threshold 80
  artifacts:
    paths:
      - test-report.html
```

---

## Examples by Language

### Python (pytest)
```bash
/run-tests /path/to/python-project
# Auto-detects pytest
# Uses pyproject.toml or pytest.ini
```

### JavaScript (jest)
```bash
/run-tests /path/to/js-project
# Auto-detects jest
# Uses package.json or jest.config.js
```

### TypeScript (vitest)
```bash
/run-tests /path/to/ts-project
# Auto-detects vitest
# Uses vitest.config.ts
```

### Rust (cargo)
```bash
/run-tests /path/to/rust-project
# Auto-detects cargo
# Uses Cargo.toml
```

---

## Best Practices

✅ **DO**
- Run tests frequently during development
- Use appropriate worker count for your system
- Track trends over time
- Fix flaky tests immediately
- Review coverage gaps regularly

❌ **DON'T**
- Ignore failing tests
- Skip coverage checks
- Use too many workers (causes thrashing)
- Commit code without testing
- Let flaky tests accumulate

---

## Quick Wins

**5-Minute Setup:**
```bash
# 1. Run tests
/run-tests .

# 2. Check what failed
/test-results .

# 3. Fix issues
# (edit code)

# 4. Verify
/test-health .
```

**10-Minute Optimization:**
```bash
# 1. Find slow tests
/test-performance . --threshold 1.0

# 2. Increase parallelization
/run-tests . --workers 16

# 3. Verify improvement
/compare-runs . <before> <after>
```

**15-Minute Quality Boost:**
```bash
# 1. Check coverage
/test-coverage .

# 2. Find flaky tests
/detect-flaky . --runs 10

# 3. Get health score
/test-health .

# 4. Address top issues
```

---

*Version: 1.0.0 | Lines: 245 | Last Updated: 2025-12-27*
