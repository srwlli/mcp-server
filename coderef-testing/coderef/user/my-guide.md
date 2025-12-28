# coderef-testing - My Tool Guide

**Quick reference for all MCP tools and slash commands**

---

## Discovery Tools

**discover_tests** - Find all tests and auto-detect framework
**list_test_frameworks** - Show detected frameworks with versions

## Execution Tools

**run_all_tests** - Execute entire test suite
**run_test_file** - Run specific test file
**run_test_category** - Run tests matching pattern/tag
**run_tests_in_parallel** - Execute with custom worker count

## Management Tools

**get_test_results** - Retrieve archived results
**aggregate_results** - Summary across multiple runs
**generate_test_report** - Create report (markdown/HTML/JSON)
**compare_test_runs** - Diff between two test runs

## Analysis Tools

**analyze_coverage** - Code coverage metrics and gaps
**detect_flaky_tests** - Find intermittent failures
**analyze_test_performance** - Identify slow tests
**validate_test_health** - Overall suite health (0-100 score)

---

## Slash Commands

### Test Execution
- `/run-tests` - Run full test suite
- `/run-server-tests` - Run specific category
- `/run-test-file` - Execute single file

### Results & Reporting
- `/test-results` - View latest results
- `/test-report` - Generate report
- `/test-coverage` - Show coverage
- `/test-trends` - Historical trends
- `/compare-runs` - Compare two runs

### Analysis
- `/test-performance` - Analyze speed
- `/detect-flaky` - Find flaky tests
- `/test-health` - Health check

### Discovery
- `/discover-tests` - List all tests
- `/list-frameworks` - Show frameworks

---

## Quick Examples

```bash
# Run tests
/run-tests /path/to/project

# Get coverage
/test-coverage /path/to/project

# Find slow tests
/test-performance /path/to/project --threshold 2.0

# Health check
/test-health /path/to/project
```

---

## Common Workflows

**Daily Development:**
```bash
/run-tests .
/test-results .
```

**Pre-Commit:**
```bash
/test-health .
/detect-flaky .
```

**CI/CD:**
```bash
/run-tests . --workers 16
/test-report . --format html
```

---

*Version: 1.0.0 | Total Tools: 14 | Total Commands: 14*
