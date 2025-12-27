# coderef-context Test Plan

**Project:** coderef-context MCP Server
**Version:** 1.0.0
**Created:** 2025-12-27
**Test Framework:** pytest + coeref-testing MCP
**Status:** Ready for execution

---

## Overview

This document defines the comprehensive test plan for coderef-context, utilizing the **coeref-testing MCP server** for orchestration, execution, and analysis.

### Test Strategy
- **Framework:** pytest (Python testing standard)
- **Orchestration:** coeref-testing MCP (universal test coordinator)
- **Coverage:** All 10 tools (scan, query, impact, complexity, patterns, coverage, context, validate, drift, diagram)
- **Test Categories:** Unit, Integration, Error Handling, Performance

---

## Test Structure

```
coderef-context/
├── tests/
│   ├── __init__.py
│   ├── conftest.py                 # pytest fixtures and configuration
│   ├── test_tools.py               # All 10 tool tests
│   └── (future subdirs)
│       ├── unit/                   # Unit tests
│       ├── integration/            # Integration tests
│       └── performance/            # Performance tests
├── pytest.ini                      # pytest configuration
└── coderef/testing/
    └── TEST_PLAN.md               # This file
```

---

## Test Categories

### 1. Unit Tests (Fast, Isolated)

**Purpose:** Test individual tool handlers in isolation
**Framework:** pytest with mocks
**CLI Required:** No (mocked)
**Timeout:** < 10 seconds each

#### Tools with Unit Tests
- All 10 tools have unit tests verifying:
  - Parameter validation
  - JSON output format validation
  - Error message formatting
  - Output field presence/type

#### Example Unit Test Cases

```python
# coderef_scan
- test_scan_json_output_format()           # Verify JSON structure
- test_scan_elements_have_required_fields() # Check element fields

# coderef_query
- test_query_output_format()               # Verify JSON structure
- test_query_result_is_list()              # Check results type

# coderef_impact
- test_impact_output_format()              # Verify JSON structure
- test_impact_risk_levels()                # Check valid risk levels
```

### 2. Integration Tests (Require CLI)

**Purpose:** Test tools with real @coderef/core CLI
**Framework:** pytest with real subprocess calls
**CLI Required:** Yes (C:/Users/willh/Desktop/projects/coderef-system/packages/cli)
**Timeout:** 30-120 seconds (per tool)

#### Single-Tool Integration Tests
Each tool has integration tests:
1. **coderef_scan** - Scan coderef-context source (5+ test cases)
2. **coderef_query** - Query relationships (6 query types)
3. **coderef_impact** - Impact analysis (3 operation types)
4. **coderef_complexity** - Complexity metrics (functions + classes)
5. **coderef_patterns** - Pattern discovery (with/without filters)
6. **coderef_coverage** - Coverage analysis (if reports exist)
7. **coderef_context** - Comprehensive context (multiple formats)
8. **coderef_validate** - Reference validation (with patterns)
9. **coderef_drift** - Drift detection (with index)
10. **coderef_diagram** - Diagram generation (Mermaid + Graphviz)

#### Multi-Tool Integration Tests
Workflow tests combining tools:
1. **Scan + Query** - Discover elements, then query relationships
2. **Scan + Impact** - Discover elements, then analyze change impact
3. **Query Chain** - Follow dependency chains (A → B → C)
4. **Full Analysis** - Complete workflow: scan → query → impact → complexity

### 3. Error Handling Tests

**Purpose:** Test edge cases and error scenarios
**Test Cases:**
- CLI unavailable / not found
- Invalid project path
- Missing required parameters
- Malformed JSON from CLI
- Timeout enforcement (120s)
- Subprocess crash handling
- Large projects (timeout behavior)

### 4. Performance Tests

**Purpose:** Verify performance characteristics
**Metrics:**
- Scan latency (small project: < 5 seconds)
- Query latency (< 30 seconds)
- Memory usage (< 100MB for typical projects)
- Concurrent request handling

---

## Test Execution with coeref-testing

### Using coeref-testing MCP Server

**Step 1: Discover Tests**
```bash
/discover-tests "C:\Users\willh\.mcp-servers\coderef-context"
```
Expected: Lists all 100+ test cases across 4 categories

**Step 2: Run Full Test Suite**
```bash
/run-tests "C:\Users\willh\.mcp-servers\coderef-context"
```
Expected: Executes pytest with unified result aggregation

**Step 3: Generate Test Report**
```bash
/test-report "C:\Users\willh\.mcp-servers\coderef-context" --format markdown
```
Expected: Creates comprehensive markdown report with:
- Summary (total, passed, failed, skipped)
- Per-tool breakdowns
- Error analysis
- Performance metrics

**Step 4: Analyze Coverage & Performance**
```bash
/test-coverage "C:\Users\willh\.mcp-servers\coderef-context"
/test-performance "C:\Users\willh\.mcp-servers\coderef-context"
```

**Step 5: Detect Flaky Tests**
```bash
/detect-flaky "C:\Users\willh\.mcp-servers\coderef-context" --runs 5
```

### Local Execution (Direct pytest)

```bash
# Install dependencies
cd C:\Users\willh\.mcp-servers\coderef-context
pip install pytest pytest-asyncio pytest-timeout

# Run all tests
pytest tests/ -v

# Run specific category
pytest tests/test_tools.py::TestCoderefScan -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run only unit tests (no CLI required)
pytest tests/ -m "not integration" -v
```

---

## Expected Results

### Overall Summary
- **Total Test Cases:** 100+
- **Unit Tests:** ~60 (fast, no CLI)
- **Integration Tests:** ~30 (require CLI)
- **Error Handling:** ~15 (edge cases)
- **Performance:** ~5 (metrics)

### Success Criteria
✅ All 10 tools execute without crashing
✅ JSON outputs are valid and parseable
✅ Async/subprocess handling works correctly
✅ Timeout enforcement at 120s
✅ Error messages are meaningful
✅ Performance < 5s for small projects
✅ No memory leaks on repeated calls

### Pass Rate Target
- **Unit Tests:** 100% pass (60/60)
- **Integration Tests:** 90%+ pass (27/30+) - some depend on CLI availability
- **Error Handling:** 100% pass (15/15)
- **Performance:** 100% pass (5/5)

---

## Test Files & Organization

### conftest.py
Pytest fixtures and configuration:
- `event_loop` - Async test support
- `test_project_path` - coderef-context source directory
- `cli_path` - @coderef/core CLI path
- `cli_exists` - CLI availability check
- `mock_results` - Mock test data provider

### test_tools.py (600+ lines)
Test classes for all tools:
```
TestCoderefScan (7 async tests + 2 unit tests)
TestCoderefQuery (7 async tests + 1 unit test)
TestCoderefImpact (5 async tests + 2 unit tests)
TestCoderefComplexity (3 async tests + 1 unit test)
TestCoderefPatterns (3 async tests)
TestCoderefCoverage (2 async tests)
TestCoderefContext (3 async tests)
TestCoderefValidate (2 async tests)
TestCoderefDrift (2 async tests)
TestCoderefDiagram (4 async tests)

TestIntegration (4 async workflow tests)
TestErrorHandling (4 async error tests)
TestPerformance (4 async perf tests)
```

### pytest.ini
Configuration:
- Test discovery patterns
- Async mode (asyncio_mode = auto)
- Markers (asyncio, unit, integration, performance)
- Timeout enforcement (300s max)
- Output formatting (verbose, short traceback)

---

## Running Tests

### Quick Start
```bash
# 1. Run fast unit tests only (no CLI required)
pytest tests/ -m "not integration" -v --tb=short

# 2. Run full suite with real CLI
pytest tests/ -v

# 3. Generate HTML report
pytest tests/ --html=report.html --self-contained-html

# 4. Run with coeref-testing
/run-tests "C:\Users\willh\.mcp-servers\coderef-context"
/test-report "C:\Users\willh\.mcp-servers\coderef-context"
```

### Common Commands
```bash
# Run specific test class
pytest tests/test_tools.py::TestCoderefScan -v

# Run with detailed output
pytest tests/ -vv --tb=long

# Run with coverage report
pytest tests/ --cov=src --cov-report=term-missing

# Run parallel (with pytest-xdist)
pytest tests/ -n 4

# Run until first failure
pytest tests/ -x

# Run only failed tests from last run
pytest tests/ --lf
```

---

## CI/CD Integration

### GitHub Actions (Future)
```yaml
name: Test coderef-context
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v --junitxml=results.xml
      - uses: actions/upload-artifact@v2
        with:
          name: test-results
          path: results.xml
```

---

## Test Results Location

Results are stored in:
```
coderef/testing/results/2025-12-27/
├── test-scan-tool.md
├── test-query-tool.md
├── test-impact-tool.md
├── ... (one per tool)
└── summary.md
```

Automated archival via coeref-testing:
- Timestamps: ISO 8601 format
- Formats: Markdown, JSON, HTML
- Retention: All runs preserved for trend analysis

---

## Known Limitations

1. **CLI Dependency:** Integration tests require @coderef/core CLI
2. **No Mocking:** Tests use real subprocess calls (by design)
3. **Project Dependency:** Tests analyze coderef-context source itself
4. **Timeout:** Large projects may exceed 120s timeout
5. **Framework-Specific:** Tests currently pytest-only (could expand to jest/vitest)

---

## Future Enhancements

- [ ] Mock CLI for deterministic testing
- [ ] Parameterized test runner (multiple projects)
- [ ] Performance benchmarking suite
- [ ] Regression test tracking
- [ ] Cross-platform CI/CD (Windows, macOS, Linux)
- [ ] Multi-framework support (jest, vitest for Node projects)
- [ ] Visual test dashboard

---

## Troubleshooting

### "CLI path not found"
Check environment variable: `echo $CODEREF_CLI_PATH`
Verify CLI exists: `ls C:\Users\willh\Desktop\projects\coderef-system\packages\cli\dist\cli.js`

### "Scan timeout (120s exceeded)"
Project too large. Try:
- `use_ast=False` for faster regex-based scan
- Test on smaller subdirectory
- Increase timeout in pytest.ini

### "JSON parse error"
CLI output format mismatch. Check:
- CLI is outputting valid JSON
- JSON parser skips non-JSON lines correctly

---

## Contact & Support

**Test Maintainer:** willh
**Test Framework:** pytest + coeref-testing MCP
**Status:** Ready for execution
**Last Updated:** 2025-12-27
