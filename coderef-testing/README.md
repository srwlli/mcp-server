# coeref-testing - Universal MCP Testing Server

**Framework-agnostic test orchestration and reporting for any project**

## Overview

`coeref-testing` is an MCP server that brings unified test execution, analysis, and reporting to any project, regardless of programming language or test framework.

### What It Does

- **Auto-detects** test frameworks (pytest, jest, vitest, cargo, mocha)
- **Executes** tests in parallel with configurable workers
- **Aggregates** results from different frameworks into unified format
- **Analyzes** coverage, performance, flakiness, and health
- **Reports** results in markdown, HTML, or JSON formats
- **Tracks** trends and regressions over time

### Supported Frameworks

| Framework | Language | Support |
|-----------|----------|---------|
| **pytest** | Python | ✅ Full |
| **jest** | JavaScript/TypeScript | ✅ Full |
| **vitest** | Vite/JavaScript | ✅ Full |
| **cargo test** | Rust | ✅ Full |
| **mocha** | Node.js/JavaScript | ✅ Full |

## Quick Start

### Installation

```bash
# Navigate to project
cd C:\Users\willh\.mcp-servers\coeref-testing

# Install dependencies
uv sync

# Start the MCP server
python server.py
```

### First Run

Discover and run tests:

```bash
/discover-tests C:\Users\willh\.mcp-servers\coderef-context
/run-tests C:\Users\willh\.mcp-servers\coderef-context
/test-health C:\Users\willh\.mcp-servers\coderef-context
```

## 14 MCP Tools

### Discovery (2 tools)
- `/discover-tests` - Find all tests and auto-detect framework
- `/list-frameworks` - Show detected test frameworks

### Execution (4 tools)
- `/run-tests` - Execute full test suite
- `/run-test-file` - Run specific test file
- `/run-by-pattern` - Run tests matching pattern
- `/run-parallel` - Run with custom parallelization

### Management (4 tools)
- `/test-results` - View previous test results
- `/test-report` - Generate formatted report
- `/compare-runs` - Compare two test runs
- Plus result archival and export in JSON/CSV/HTML

### Analysis (4 tools)
- `/test-coverage` - Analyze code coverage
- `/test-performance` - Find slow tests
- `/test-trends` - Show historical trends
- `/detect-flaky` - Find flaky tests
- `/test-health` - Overall test suite health

## Key Features

### ⚡ Fast Parallel Execution
- Auto-detects CPU cores, scales workers accordingly
- Default 8 workers, configurable from 1-20+
- Proper test isolation prevents flakiness

### 📊 Unified Results Format
All frameworks output to standard JSON schema with:
- Test name, status, duration, file, line number
- Summary counts (passed, failed, skipped, errors)
- Framework metadata

### 📈 Comprehensive Analysis
- **Coverage Gaps** - Identify what's untested
- **Performance Profiling** - Find slow tests (p50, p95, p99)
- **Flaky Detection** - Track intermittent failures
- **Health Scoring** - 0-100 with A-F grades
- **Trend Analysis** - Spot regressions early

### 💾 Automatic Archival
Test results automatically saved with ISO 8601 timestamps for:
- Historical tracking
- Trend analysis
- Regression detection
- Performance comparison

### 📑 Multiple Report Formats
- **Markdown** - For documentation and sharing
- **HTML** - For web dashboards
- **JSON** - For CI/CD integration

## Usage Examples

### Quick Test Run
```bash
/run-tests C:\Users\willh\.mcp-servers\coderef-context
```

### Find and Fix Flaky Tests
```bash
/detect-flaky /path --runs 5 --format detailed
```

### Speed Optimization
```bash
/test-performance /path --threshold 2.0
/run-parallel /path --workers 16
```

### Coverage Improvement
```bash
/test-coverage /path --threshold 85
```

### Health Monitoring
```bash
/test-health /path --detailed
/test-trends /path --days 7
/compare-runs /path run1 latest
```

## Documentation

- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Architecture, design decisions, roadmap
- **[CLAUDE.md](CLAUDE.md)** - AI context for agents
- **[.claude/commands/](​.claude/commands/)** - Command reference documentation

## Architecture

### Core Components

| Component | Purpose |
|-----------|---------|
| `framework_detector.py` | Auto-detect pytest/jest/cargo/mocha/vitest |
| `test_runner.py` | Execute tests with async/parallel support |
| `test_aggregator.py` | Normalize results, archive with timestamps |
| `result_analyzer.py` | Coverage, performance, flaky, health analysis |
| `test_coordinator.py` | Multi-project orchestration |
| `server.py` | MCP tool registration and handlers |

### Data Flow

```
User Project
    ↓
Framework Detection
    ↓
Test Execution (Parallel)
    ↓
Result Aggregation (Unified Schema)
    ↓
Analysis & Reporting
    ↓
Archive with Timestamp
```

## Integration

### With CodeRef Ecosystem (Optional)

Works standalone but integrates optionally with:
- **coderef-context** - Analyze test dependencies
- **coderef-workflow** - Track as workorders
- **coderef-docs** - Generate documentation
- **coderef-personas** - Use testing-expert

### With CI/CD Pipelines

Export JSON results for integration:

```bash
test_report /path --format json --output results.json
```

### Direct Python API

```python
from src.test_runner import TestRunner, TestRunRequest

runner = TestRunner()
req = TestRunRequest(project_path="/path")
result = await runner.run_tests(req)
```

## Testing

Run the test suite:

```bash
# All tests
pytest tests/ -v

# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v --timeout=300

# Type check
mypy src/
```

**Test Coverage:**
- 27+ unit tests for framework detection
- 30+ unit tests for test execution
- 12+ integration tests for pytest
- 15+ integration tests for jest
- Plus tests for aggregation, analysis, coordination

## Performance Tips

**Speed Up Tests:**
- Use `--workers N` with higher count
- Mock external dependencies
- Use in-memory databases for tests

**Improve Coverage:**
- Focus on critical paths first
- Test happy path + error cases
- Use coverage reports for gaps

**Fix Flaky Tests:**
- Mock external services
- Add proper test isolation
- Avoid shared state
- Use deterministic values

## Status

**Version:** 1.0.0
**Status:** ✅ Production Ready

**Implementation Complete:**
- ✅ Phase 1: Setup & Architecture
- ✅ Phase 2: Framework Detection & Execution
- ✅ Phase 3: Result Processing & Analysis
- ✅ Phase 4: Tools, Commands, Documentation

**Ready for:**
- Testing on CodeRef ecosystem (4 servers)
- Testing on any Python/JavaScript/Rust project
- Integration with CI/CD pipelines
- Production test infrastructure

---

**Maintained by:** willh, Claude Code AI

**Project:** coeref-testing MCP Server
**License:** MIT
**Repository:** C:\Users\willh\.mcp-servers\coderef-testing