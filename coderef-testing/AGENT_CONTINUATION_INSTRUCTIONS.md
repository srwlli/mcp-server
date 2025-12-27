# Agent Continuation Instructions - coeref-testing Implementation

**Workorder:** WO-COEREF-TESTING-001
**Project:** coeref-testing (Universal MCP Testing Server)
**Current Status:** Phase 1 Complete → Ready for Phase 2
**Date:** 2025-12-27

---

## Context Restoration Summary

Phase 1 (Setup & Core Architecture) has been successfully completed with the following deliverables:

### ✅ Phase 1 Complete (4/4 Tasks)

| Task | Status | Deliverable |
|------|--------|-------------|
| SETUP-001 | ✅ Completed | Directory structure (src/, tests/, personas/, .claude/commands/) |
| SETUP-002 | ✅ Completed | pyproject.toml (full Python package config) |
| SETUP-003 | ✅ Completed | server.py (350+ line MCP server skeleton with 14 tools) |
| SETUP-004 | ✅ Completed | src/models.py (622 lines of Pydantic schemas) |

### Files Created in Phase 1

```
coderef-testing/
├── pyproject.toml                    # Project metadata & dependencies
├── server.py                         # MCP server (350+ lines)
├── src/
│   ├── __init__.py                   # Package initialization
│   └── models.py                     # Pydantic schemas (622 lines)
├── tests/
│   └── integration/                  # (empty, ready for Phase 2 tests)
├── personas/                         # (empty, ready for Phase 4 persona)
├── .claude/
│   └── commands/                     # (empty, ready for Phase 4 commands)
└── coderef/
    ├── workorder/coeref-testing/
    │   ├── plan.json                 # Implementation plan (37 tasks)
    │   ├── DELIVERABLES.md           # Progress tracking
    │   └── execution-log.json         # Task status log
    ├── foundation-docs/              # (created in planning)
    └── testing/                      # (for test results)
```

---

## Your Next Task: Phase 2 - Framework Detection & Execution

### Phase Overview

**Duration:** 8-10 hours (13 tasks)
**Dependencies:** Phase 1 (✅ Complete)
**Deliverables:**
- Framework detection for pytest, jest, vitest, cargo, mocha
- Test execution engine with async/parallel support
- Unit and integration tests
- All tests passing

### Phase 2 Tasks (13 Total)

**Detection Implementation (5 tasks):**
```
DETECT-001: Implement pytest detection (1h)
DETECT-002: Add jest/vitest detection (1h)
DETECT-003: Add cargo/mocha detection (0.75h)
DETECT-004: Implement caching/validation (0.5h)
DETECT-TEST-001: Create unit tests (1h)
```

**Execution Implementation (8 tasks):**
```
RUN-001: pytest execution (1.5h)
RUN-002: jest/vitest execution (1h)
RUN-003: cargo/mocha execution (0.75h)
RUN-004: async/parallel execution (1.5h)
RUN-005: timeout/error handling (1h)
RUN-TEST-001: test_runner unit tests (1h)
RUN-TEST-002: pytest integration tests (1h)
RUN-TEST-003: jest integration tests (1h)
```

---

## Step-by-Step Instructions

### Step 1: Update Task Status (Mark Starting)

Run this command to mark the first Phase 2 task as in_progress:

```bash
mcp__coderef_workflow__update_task_status(
  project_path="C:\Users\willh\.mcp-servers",
  feature_name="coeref-testing",
  task_id="DETECT-001",
  status="in_progress"
)
```

### Step 2: Create framework_detector.py

**File:** `C:\Users\willh\.mcp-servers\coderef-testing\src\framework_detector.py`

**Purpose:** Auto-detect test frameworks in any project

**Requirements:**
- Detect pytest via: pyproject.toml (has [tool.pytest]), tests/ dir, conftest.py
- Detect jest via: package.json (has jest config), jest.config.js, .jest.json
- Detect vitest via: vite.config.ts, vitest.config.ts, package.json (has vitest)
- Detect cargo via: Cargo.toml (has [dev-dependencies])
- Detect mocha via: .mocharc.*, mocha.opts, package.json (has mocha)
- Return list of FrameworkInfo objects with version detection
- Implement caching (cache results for 1 hour)

**Key Methods:**
```python
async def detect_frameworks(project_path: str) -> FrameworkDetectionResult
async def detect_pytest(project_path: str) -> Optional[FrameworkInfo]
async def detect_jest(project_path: str) -> Optional[FrameworkInfo]
async def detect_vitest(project_path: str) -> Optional[FrameworkInfo]
async def detect_cargo(project_path: str) -> Optional[FrameworkInfo]
async def detect_mocha(project_path: str) -> Optional[FrameworkInfo]
async def get_version(framework: str, project_path: str) -> Optional[str]
```

**Reference:** See TESTING_GUIDE.md "Framework Detection" section for detailed approach

### Step 3: Create test_runner.py

**File:** `C:\Users\willh\.mcp-servers\coderef-testing\src\test_runner.py`

**Purpose:** Execute tests for any framework and normalize results

**Requirements:**
- Execute tests using detected framework's native CLI
- Convert all outputs to UnifiedTestResults schema
- Support parallel execution with asyncio worker pool
- Handle timeouts and errors gracefully
- Capture stdout/stderr
- Parse framework-specific output (pytest JSON, jest JSON, cargo output)

**Key Methods:**
```python
async def run_tests(request: TestRunRequest) -> UnifiedTestResults
async def run_pytest(project_path: str, **kwargs) -> UnifiedTestResults
async def run_jest(project_path: str, **kwargs) -> UnifiedTestResults
async def run_vitest(project_path: str, **kwargs) -> UnifiedTestResults
async def run_cargo(project_path: str, **kwargs) -> UnifiedTestResults
async def run_mocha(project_path: str, **kwargs) -> UnifiedTestResults
async def execute_with_timeout(cmd: List[str], timeout: int) -> Tuple[str, str, int]
```

**Reference:** See TESTING_GUIDE.md "Test Execution" section

### Step 4: Update server.py Tool Handlers

**File:** `C:\Users\willh\.mcp-servers\coderef-testing\server.py`

Replace the placeholder implementations with actual calls to framework_detector and test_runner:

**Discovery handlers (complete):**
- `handle_discover_tests()` - Call framework_detector.detect_frameworks() + list files
- `handle_list_frameworks()` - Call framework_detector.detect_frameworks()

**Execution handlers (complete):**
- `handle_run_all_tests()` - Call test_runner.run_tests() with no filter
- `handle_run_test_file()` - Call test_runner with file filter
- `handle_run_test_category()` - Call test_runner with pattern filter
- `handle_run_tests_parallel()` - Call test_runner with parallel_workers setting

### Step 5: Create Unit Tests

**File:** `C:\Users\willh\.mcp-servers\coderef-testing\tests\test_framework_detector.py`

**Test Coverage:**
- Test detection of each framework (pytest, jest, vitest, cargo, mocha)
- Test version extraction
- Test caching mechanism
- Test missing framework returns None
- Test with sample project structures

**Example test:**
```python
@pytest.mark.asyncio
async def test_detect_pytest():
    # Create temp project with pytest markers
    # Call detect_frameworks()
    # Assert pytest detected with correct version
    pass
```

**File:** `C:\Users\willh\.mcp-servers\coderef-testing\tests\test_runner.py`

**Test Coverage:**
- Mock test execution
- Verify UnifiedTestResults schema compliance
- Test timeout handling
- Test error handling
- Test parallel execution

### Step 6: Create Integration Tests

**File:** `C:\Users\willh\.mcp-servers\coderef-testing\tests\integration/test_pytest.py`

**Purpose:** Test actual pytest execution on real sample project

**File:** `C:\Users\willh\.mcp-servers\coderef-testing\tests/integration/test_jest.py`

**Purpose:** Test actual jest execution on real sample project

### Step 7: Create __init__.py Files

```bash
# tests/__init__.py (empty)
# tests/integration/__init__.py (empty)
```

### Step 8: Run Tests and Fix Failures

```bash
cd C:\Users\willh\.mcp-servers\coderef-testing
python -m pytest tests/ -v
```

**If tests pass:** Mark DETECT-TEST-001, RUN-TEST-001, RUN-TEST-002, RUN-TEST-003 as completed

**If tests fail:** Fix issues and re-run

---

## Key Design Patterns to Follow

### 1. Framework Detection Pattern

```python
async def detect_frameworks(project_path: str) -> FrameworkDetectionResult:
    """Auto-detect all frameworks in project."""
    detected = []

    # Check each framework
    pytest_info = await detect_pytest(project_path)
    if pytest_info:
        detected.append(pytest_info)

    # ... repeat for jest, vitest, cargo, mocha

    return FrameworkDetectionResult(
        detected=len(detected) > 0,
        frameworks=detected,
        test_files=[...],
        config_files=[...]
    )
```

### 2. Test Execution Pattern

```python
async def run_tests(request: TestRunRequest) -> UnifiedTestResults:
    """Execute tests and normalize results."""

    # Auto-detect framework if not specified
    if not request.framework:
        result = await detect_frameworks(request.project_path)
        if not result.frameworks:
            raise ValueError("No test framework detected")
        request.framework = result.frameworks[0].framework

    # Execute with appropriate runner
    if request.framework == TestFramework.PYTEST:
        return await run_pytest(request.project_path, **request.dict())
    # ... repeat for other frameworks
```

### 3. Result Normalization Pattern

```python
def normalize_pytest_output(raw_output: str) -> UnifiedTestResults:
    """Convert pytest JSON output to UnifiedTestResults."""
    pytest_json = json.loads(raw_output)

    tests = [
        TestResult(
            name=test["nodeid"],
            status=TestStatus(test["outcome"]),
            duration=test["duration"],
            # ... map all fields
        )
        for test in pytest_json["tests"]
    ]

    return UnifiedTestResults(
        project=...,
        framework=FrameworkInfo(framework=TestFramework.PYTEST, ...),
        summary=TestSummary(...),
        tests=tests,
        timestamp=datetime.utcnow()
    )
```

---

## Important Notes for Agent

### ✅ What Already Exists (Don't Recreate)
- server.py with tool registration and MCP infrastructure
- src/models.py with all Pydantic schemas
- pyproject.toml with dependencies
- Directory structure
- execution-log.json for task tracking

### ❌ What You Need to Implement
- src/framework_detector.py (NEW)
- src/test_runner.py (NEW)
- Complete server.py tool handlers (MODIFY existing file)
- tests/test_framework_detector.py (NEW)
- tests/test_runner.py (NEW)
- tests/integration/test_pytest.py (NEW)
- tests/integration/test_jest.py (NEW)
- tests/__init__.py (NEW)
- tests/integration/__init__.py (NEW)

### 📋 Task Tracking

After completing each task, call:
```bash
mcp__coderef_workflow__update_task_status(
  project_path="C:\Users\willh\.mcp-servers",
  feature_name="coeref-testing",
  task_id="DETECT-001",  # Replace with actual task ID
  status="completed"
)
```

### 🔍 Reference Documents

- **TESTING_GUIDE.md** - Vision and architecture details
- **CLAUDE.md** - Project overview and context
- **plan.json** - Full 37-task plan with all details
- **AGENT_IMPLEMENTATION_STATUS.md** - Phase breakdown

### 🚀 Success Criteria for Phase 2

- ✅ All 5 frameworks detected correctly (pytest, jest, vitest, cargo, mocha)
- ✅ Tests execute successfully with results normalized to UnifiedTestResults
- ✅ Parallel execution works without conflicts
- ✅ All unit and integration tests pass
- ✅ Tool handlers in server.py functional (not placeholders)

---

## Commands to Execute

### Prepare Environment

```bash
cd C:\Users\willh\.mcp-servers\coderef-testing
python -m pip install -e .
```

### Run Tests During Development

```bash
# Unit tests only
pytest tests/test_framework_detector.py -v
pytest tests/test_runner.py -v

# Integration tests (requires actual frameworks installed)
pytest tests/integration/ -v

# All tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=src
```

### Type Checking

```bash
mypy src/ --ignore-missing-imports
```

### Code Style

```bash
black src/ tests/
ruff check src/ tests/
```

---

## What Happens After Phase 2

Once Phase 2 completes:

1. **Phase 3 (Agent 3):** Result Processing & Analysis
   - Result aggregation and archival
   - Coverage, flaky, performance, health analysis
   - 6 tasks, 7-9 hours

2. **Phase 4 (Agent 4):** Tools, Commands, Persona, Docs & Release
   - Complete MCP tool implementations
   - 12+ slash commands
   - testing-expert persona
   - Documentation and release
   - 14 tasks, 9-11 hours

---

## Questions?

Refer to:
- **TESTING_GUIDE.md** (lines 1-502) for detailed architecture
- **plan.json** section `6_implementation_phases.phases[1]` for Phase 2 details
- **CLAUDE.md** section "Tools Catalog" for tool specifications

---

**Status:** Phase 1 ✅ Complete | Phase 2 → Ready to Start
**Next Task:** DETECT-001 - Implement pytest detection
**Estimated Duration:** 0.5-1 hour for DETECT-001

**Begin with Step 1 above to mark DETECT-001 as in_progress, then implement framework_detector.py**
