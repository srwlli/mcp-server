# coderef-context Testing

**Comprehensive Test Suite for Code Intelligence Server (10 Tools + 100+ Test Cases)**

---

## Quick Links

- **Test Plan:** `TEST_PLAN.md` - Complete testing strategy & execution guide
- **Central Hub:** `../../../../coderef/testing/INDEX.md`
- **Test Results:** `results/` (organized by date)
- **Test Framework:** pytest + coeref-testing MCP

---

## Test Infrastructure (NEW)

### Files Created

```
coderef-context/
├── tests/
│   ├── __init__.py                  # Test package marker
│   ├── conftest.py                  # pytest fixtures & configuration
│   ├── test_tools.py                # 100+ test cases for all 10 tools
│   └── (future) unit/, integration/, performance/
├── pytest.ini                       # pytest configuration
└── coderef/testing/
    ├── README.md                    # This file (updated)
    ├── TEST_PLAN.md                 # Comprehensive test plan
    ├── test_framework.md            # Testing strategy
    └── results/
        ├── 2025-12-26/              # (initial, placeholder)
        └── 2025-12-27/              # (current test suite)
```

### Test Framework

**Built with:** pytest (Python standard testing framework)
**Orchestrated by:** coeref-testing MCP (universal test coordinator)
**Test Count:** 100+ test cases across 4 categories
**Coverage:** All 10 tools + workflows + error handling + performance

---

## Test Categories & Breakdown

| Category | Count | Type | Duration | CLI Required | Status |
|----------|-------|------|----------|-------------|--------|
| **Unit Tests** | ~60 | Fast, isolated | < 10s each | No | ✅ Ready |
| **Integration Tests** | ~30 | Real CLI, workflows | 30-120s | Yes | ✅ Ready |
| **Error Handling** | ~15 | Edge cases | < 10s each | Varies | ✅ Ready |
| **Performance** | ~5 | Metrics, latency | Varies | Yes | ✅ Ready |
| **TOTAL** | **100+** | Mixed | Varies | Mixed | ✅ Ready |

---

## Tools Tested (10 Total)

| # | Tool | Unit Tests | Integration | Error Cases | Status |
|---|------|-----------|------------|------------|--------|
| 1 | `coderef_scan` | 9 | 5+ | 3 | ✅ Ready |
| 2 | `coderef_query` | 8 | 6+ | 3 | ✅ Ready |
| 3 | `coderef_impact` | 7 | 5+ | 3 | ✅ Ready |
| 4 | `coderef_complexity` | 4 | 3+ | 2 | ✅ Ready |
| 5 | `coderef_patterns` | 3 | 3+ | 2 | ✅ Ready |
| 6 | `coderef_coverage` | 2 | 2+ | 1 | ✅ Ready |
| 7 | `coderef_context` | 3 | 3+ | 2 | ✅ Ready |
| 8 | `coderef_validate` | 2 | 2+ | 1 | ✅ Ready |
| 9 | `coderef_drift` | 2 | 2+ | 1 | ✅ Ready |
| 10 | `coderef_diagram` | 4 | 4+ | 2 | ✅ Ready |

---

## Running Tests

### Using coeref-testing MCP (Recommended)

```bash
# Discover all tests
/discover-tests "C:\Users\willh\.mcp-servers\coderef-context"
# Output: Lists all 100+ test cases

# Run full test suite
/run-tests "C:\Users\willh\.mcp-servers\coderef-context"
# Output: Executes all tests, aggregates results

# Generate markdown report
/test-report "C:\Users\willh\.mcp-servers\coderef-context" --format markdown
# Output: Comprehensive report with summaries per tool

# Analyze coverage
/test-coverage "C:\Users\willh\.mcp-servers\coderef-context"
# Output: Coverage metrics and gaps

# Performance analysis
/test-performance "C:\Users\willh\.mcp-servers\coderef-context"
# Output: Latency, throughput, slow tests

# Detect flaky tests
/detect-flaky "C:\Users\willh\.mcp-servers\coderef-context" --runs 5
# Output: Intermittently failing tests
```

### Direct pytest (Local Execution)

```bash
# Run all tests
cd C:\Users\willh\.mcp-servers\coderef-context
pytest tests/ -v

# Run only unit tests (no CLI required)
pytest tests/ -m "not integration" -v

# Run specific tool
pytest tests/test_tools.py::TestCoderefScan -v

# Generate HTML report
pytest tests/ --html=report.html --self-contained-html

# With coverage
pytest tests/ --cov=src --cov-report=html
```

---

## Test Status (2025-12-27)

### ✅ Infrastructure Complete

- ✅ Test structure created (tests/ directory)
- ✅ conftest.py with fixtures (event_loop, test_project_path, cli_path, mock_results)
- ✅ test_tools.py with 100+ test cases (600+ lines)
- ✅ pytest.ini configuration (asyncio_mode, markers, timeout)
- ✅ TEST_PLAN.md documentation (comprehensive guide)
- ✅ test_framework.md strategy document
- ✅ This README updated

### ⏳ Ready for Execution

**Next Steps:**
1. Run test suite with coeref-testing
2. Generate report and analyze results
3. Fix any failures
4. Archive results in results/2025-12-27/
5. Track trends over time

---

## Test Plan Features

**conftest.py Fixtures:**
- `event_loop` - Async test support
- `test_project_path` - coderef-context source
- `cli_path` - @coderef/core CLI location
- `cli_exists` - CLI availability check
- `mock_results` - Mock data (scan, query, impact results)

**test_tools.py Coverage:**
- TestCoderefScan - 9 unit + 5+ integration + 3 error tests
- TestCoderefQuery - 8 unit + 6+ integration + 3 error tests
- TestCoderefImpact - 7 unit + 5+ integration + 3 error tests
- ... (10 tool test classes total)
- TestIntegration - 4 multi-tool workflow tests
- TestErrorHandling - 4 error scenario tests
- TestPerformance - 4 performance metric tests

**pytest.ini Features:**
- Async test support (`asyncio_mode = auto`)
- Test discovery patterns (test_tools.py, Test* classes)
- Markers for categorization (asyncio, unit, integration, performance)
- Timeout enforcement (300s max)
- Verbosity and output formatting

---

## Success Criteria

✅ All 10 tools execute without crashing
✅ JSON outputs valid and parseable
✅ Async/subprocess handling correct
✅ 120s timeout enforced
✅ Error messages meaningful
✅ Performance < 5s for small projects
✅ No memory leaks on repeated calls

---

## Integration with CodeRef Ecosystem

Works with:
- **coeref-testing MCP** - Test orchestration & reporting
- **coderef-context** - Server being tested (10 tools)
- **coderef-workflow** - Can track test workorders
- **coderef-docs** - Can generate test reports
- **coderef-personas** - Can use testing-expert

---

**Last Updated:** 2025-12-27
**Status:** ✅ Ready for Test Execution
**Maintained by:** willh, Claude Code AI
**Test Framework:** pytest + coeref-testing MCP

