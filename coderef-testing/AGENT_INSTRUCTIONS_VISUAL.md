# Agent Instructions - Visual Guide

**Context Restored ✅** | **Phase 1 Complete ✅** | **Phase 2 Ready to Start ⏳**

---

## Your Mission (Next 8-10 Hours)

```
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 2: Framework Detection & Execution (13 Tasks)            │
│                                                                 │
│  Detection (5 tasks)    Execution (8 tasks)    Expected Result  │
│  ┌──────────────────┐   ┌──────────────────┐   ┌─────────────┐ │
│  │ DETECT-001       │→→→│ RUN-001          │→→→│ All Tests   │ │
│  │ (pytest)         │   │ (pytest exec)    │   │ Passing ✅  │ │
│  ├──────────────────┤   ├──────────────────┤   └─────────────┘ │
│  │ DETECT-002       │→→→│ RUN-002          │   Framework-      │
│  │ (jest/vitest)    │   │ (jest/vitest)    │   agnostic        │
│  ├──────────────────┤   ├──────────────────┤   results         │
│  │ DETECT-003       │→→→│ RUN-003          │   normalized      │
│  │ (cargo/mocha)    │   │ (cargo/mocha)    │   to unified      │
│  ├──────────────────┤   ├──────────────────┤   schema ✨       │
│  │ DETECT-004       │→→→│ RUN-004          │                   │
│  │ (caching)        │   │ (parallel exec)  │                   │
│  ├──────────────────┤   ├──────────────────┤                   │
│  │ DETECT-TEST-001  │→→→│ RUN-005          │                   │
│  │ (unit tests)     │   │ (timeouts)       │                   │
│  │                  │   ├──────────────────┤                   │
│  │                  │→→→│ RUN-TEST-001     │                   │
│  │                  │   │ (test unit tests)│                   │
│  │                  │   ├──────────────────┤                   │
│  │                  │→→→│ RUN-TEST-002     │                   │
│  │                  │   │ (pytest integ)   │                   │
│  │                  │   ├──────────────────┤                   │
│  │                  │→→→│ RUN-TEST-003     │                   │
│  │                  │   │ (jest integ)     │                   │
│  │                  │   └──────────────────┘                   │
│  └─────────────────────────────────────────────────────────────┘
```

---

## Step-by-Step Execution Path

### Step 1: Start DETECT-001 (Right Now!)
```
┌──────────────────────────────────────────┐
│ Task: DETECT-001 - pytest detection       │
│ Duration: 1 hour                          │
│ Files to Create: src/framework_detector.py│
│ Lines of Code: ~250                       │
└──────────────────────────────────────────┘

Action 1: Mark task as in_progress
  mcp__coderef_workflow__update_task_status(
    project_path="C:\Users\willh\.mcp-servers",
    feature_name="coeref-testing",
    task_id="DETECT-001",
    status="in_progress"
  )

Action 2: Create src/framework_detector.py
  - Implement: async def detect_frameworks(project_path)
  - Implement: async def detect_pytest(project_path)
  - Reference: TESTING_GUIDE.md "Framework Detection"

Action 3: Update server.py handlers
  - handle_discover_tests() → call framework_detector
  - handle_list_frameworks() → call framework_detector

Action 4: Mark task as completed
  mcp__coderef_workflow__update_task_status(
    project_path="C:\Users\willh\.mcp-servers",
    feature_name="coeref-testing",
    task_id="DETECT-001",
    status="completed"
  )
```

### Steps 2-4: Continue Detection (DETECT-002 → DETECT-004)
```
DETECT-002: jest/vitest detection     (1 hour)
  → Add to framework_detector.py
  → Same pattern as pytest

DETECT-003: cargo/mocha detection     (0.75 hours)
  → Add to framework_detector.py
  → Same pattern as pytest

DETECT-004: caching & validation      (0.5 hours)
  → Add @cache decorator
  → Add 1-hour TTL
  → Validate results before returning
```

### Step 5: Test Detection Implementation
```
DETECT-TEST-001: Unit tests            (1 hour)
  → Create tests/test_framework_detector.py
  → Mock filesystem with framework markers
  → Test detection of each framework
  → Test version extraction
  → Test cache behavior

Run tests:
  pytest tests/test_framework_detector.py -v
```

### Step 6: Start Execution (RUN-001)
```
RUN-001: pytest execution              (1.5 hours)
  → Create src/test_runner.py
  → Implement: async def run_pytest(project_path, **kwargs)
  → Use pytest --json-report flag
  → Parse JSON output
  → Convert to UnifiedTestResults
```

### Steps 7-9: Continue Execution (RUN-002 → RUN-003)
```
RUN-002: jest/vitest execution         (1 hour)
  → Add: async def run_jest()
  → Add: async def run_vitest()
  → Use --json flag
  → Same normalization pattern

RUN-003: cargo/mocha execution         (0.75 hours)
  → Add: async def run_cargo()
  → Add: async def run_mocha()
  → Parse custom output formats
```

### Step 10: Advanced Execution Features
```
RUN-004: async/parallel execution      (1.5 hours)
  → Implement asyncio.gather() for parallel runs
  → Use ThreadPoolExecutor for subprocess calls
  → Configurable worker pool size

RUN-005: timeout & error handling      (1 hour)
  → Add: async def execute_with_timeout(cmd, timeout)
  → Catch TimeoutError
  → Catch subprocess errors
  → Return graceful error responses
```

### Steps 11-13: Test the Execution Layer
```
RUN-TEST-001: test_runner unit tests   (1 hour)
  → Create tests/test_runner.py
  → Mock subprocess calls
  → Test schema compliance
  → Test error handling

RUN-TEST-002: pytest integration       (1 hour)
  → Create tests/integration/test_pytest.py
  → Run REAL pytest on sample project
  → Verify results accuracy

RUN-TEST-003: jest integration         (1 hour)
  → Create tests/integration/test_jest.py
  → Run REAL jest on sample project
  → Verify results accuracy
```

---

## File Creation Timeline

```
Hour 1: DETECT-001 (pytest detection)
  ├─ src/framework_detector.py (start)
  └─ server.py (update 2 handlers)

Hour 2: DETECT-002 (jest/vitest)
  └─ src/framework_detector.py (extend)

Hour 3: DETECT-003 + DETECT-004 (cargo/mocha + caching)
  └─ src/framework_detector.py (finish)

Hour 4: DETECT-TEST-001 (detection tests)
  ├─ tests/__init__.py (create)
  ├─ tests/test_framework_detector.py (create)
  └─ Verify tests pass

Hour 5.5: RUN-001 (pytest execution)
  ├─ src/test_runner.py (start)
  └─ server.py (update 4 execution handlers)

Hour 6.5: RUN-002 (jest/vitest execution)
  └─ src/test_runner.py (extend)

Hour 7.25: RUN-003 (cargo/mocha execution)
  └─ src/test_runner.py (extend)

Hour 8.75: RUN-004 + RUN-005 (parallel + timeout)
  └─ src/test_runner.py (finish)

Hour 9.75: RUN-TEST-001 (test_runner unit tests)
  └─ tests/test_runner.py (create)

Hour 10.75: RUN-TEST-002 + RUN-TEST-003 (integration tests)
  ├─ tests/integration/__init__.py (create)
  ├─ tests/integration/test_pytest.py (create)
  └─ tests/integration/test_jest.py (create)

Hour 11: Final testing and fixes
  ├─ pytest tests/ -v
  ├─ mypy src/
  └─ Fix any failures
```

---

## The Code You Need to Write

### Framework Detector (250 lines)
```python
# src/framework_detector.py

async def detect_frameworks(project_path: str) -> FrameworkDetectionResult:
    """Main entry point - detect all frameworks"""
    detected = []

    # Check each framework in order
    for detector in [
        detect_pytest,
        detect_jest,
        detect_vitest,
        detect_cargo,
        detect_mocha
    ]:
        result = await detector(project_path)
        if result:
            detected.append(result)

    return FrameworkDetectionResult(
        detected=len(detected) > 0,
        frameworks=detected,
        test_files=[...],
        config_files=[...]
    )

async def detect_pytest(project_path: str) -> Optional[FrameworkInfo]:
    """Check for pytest markers: pyproject.toml, tests/, conftest.py"""
    # Implement

async def detect_jest(project_path: str) -> Optional[FrameworkInfo]:
    """Check for jest markers: package.json, jest.config.js"""
    # Implement

# ... repeat for vitest, cargo, mocha
```

### Test Runner (350 lines)
```python
# src/test_runner.py

async def run_tests(request: TestRunRequest) -> UnifiedTestResults:
    """Execute tests for detected/specified framework"""
    # Auto-detect if needed
    # Call appropriate runner (run_pytest, run_jest, etc)
    # Return UnifiedTestResults

async def run_pytest(project_path: str, **kwargs) -> UnifiedTestResults:
    """Execute pytest and normalize results"""
    # Build: pytest --json-report=report.json
    # Execute with timeout
    # Parse JSON output
    # Return UnifiedTestResults

async def run_jest(project_path: str, **kwargs) -> UnifiedTestResults:
    """Execute jest and normalize results"""
    # Build: jest --json
    # Execute with timeout
    # Parse JSON output
    # Return UnifiedTestResults

# ... repeat for vitest, cargo, mocha
```

---

## Success Metrics by Hour

```
Hour 1  ✅ DETECT-001 complete, framework_detector.py started
Hour 2  ✅ DETECT-002 complete, jest detection working
Hour 3  ✅ DETECT-004 complete, caching implemented
Hour 4  ✅ DETECT-TEST-001 complete, unit tests passing
Hour 5  ✅ RUN-001 complete, pytest execution working
Hour 6  ✅ RUN-002 complete, jest execution working
Hour 7  ✅ RUN-003 complete, cargo/mocha execution working
Hour 8  ✅ RUN-004 + RUN-005 complete, parallel & timeout working
Hour 9  ✅ RUN-TEST-001 complete, test_runner tests passing
Hour 10 ✅ RUN-TEST-002 + RUN-TEST-003 complete, integration tests passing
Hour 11 ✅ All 13 tasks complete, all tests passing, Phase 2 done
```

---

## Decision Tree: What to Do When...

```
Problem: "Don't know how to detect pytest"
→ Read TESTING_GUIDE.md "Framework Detection" section
→ Look for: pyproject.toml, tests/, conftest.py

Problem: "Tests failing"
→ Run: pytest tests/ -v
→ Check: stderr for actual error
→ Fix: implementation based on error

Problem: "Schema doesn't match"
→ Check: UnifiedTestResults in src/models.py
→ Verify: all required fields populated
→ Reference: example in TESTING_GUIDE.md

Problem: "Don't know next task"
→ Check: PHASE_2_QUICKSTART.md checklist
→ Next task = first unchecked item
→ Mark as in_progress before starting

Problem: "Need to reference something"
→ Check: CURRENT_STATUS.md "Key Files to Reference"
→ Find: relevant file + section
```

---

## Quick Command Reference

### Task Status
```bash
# Start task
mcp__coderef_workflow__update_task_status(..., status="in_progress")

# Complete task
mcp__coderef_workflow__update_task_status(..., status="completed")
```

### Testing
```bash
# Run all tests
cd C:\Users\willh\.mcp-servers\coderef-testing
pytest tests/ -v

# Run specific test file
pytest tests/test_framework_detector.py -v

# Type checking
mypy src/ --ignore-missing-imports

# Code style
black src/ tests/
ruff check src/ tests/
```

---

## Files You're About to Create

```
✓ Phase 1 Files (Already created)
  ├─ server.py ✅
  ├─ src/__init__.py ✅
  ├─ src/models.py ✅
  └─ pyproject.toml ✅

→ Phase 2 Files (You'll create next)
  ├─ src/framework_detector.py (NEW - 250 lines)
  ├─ src/test_runner.py (NEW - 350 lines)
  ├─ tests/__init__.py (NEW - empty)
  ├─ tests/test_framework_detector.py (NEW - 200 lines)
  ├─ tests/test_runner.py (NEW - 250 lines)
  ├─ tests/integration/__init__.py (NEW - empty)
  ├─ tests/integration/test_pytest.py (NEW - 100 lines)
  ├─ tests/integration/test_jest.py (NEW - 100 lines)
  └─ server.py (MODIFY - replace placeholder handlers)

= Total Phase 2 Lines = ~1,400 lines of implementation
= Total Project (Phases 1+2) = ~2,800 lines
```

---

## Current Time Investment

```
Phase 1: ~2 hours (✅ Complete)
Phase 2: ~8-10 hours (⏳ Starting now)
Phase 3: ~7-9 hours (⏳ After Phase 2)
Phase 4: ~9-11 hours (⏳ After Phase 3)

Total: ~27-34 hours

Parallel Speedup: With 4 agents = ~9-11 hours total
Sequential Completion: ~27-34 hours

You are Agent 1 (or continuing solo)
Your work: Phase 2 = 8-10 hours
```

---

## Go! 🚀

**Right now:** Read PHASE_2_QUICKSTART.md (2 min)
**Then:** Start DETECT-001 (follow "Start Here" section)
**Every hour:** Mark task completed, move to next task
**After 11 hours:** Phase 2 complete, ready for Phase 3

**You've got this! Phase 1 is done, foundation is solid. Now build the engine.** ⚙️

---

Last Updated: 2025-12-27
Workorder: WO-COEREF-TESTING-001
Ready: YES ✅
