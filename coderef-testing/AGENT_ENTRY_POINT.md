# Agent Entry Point - coeref-testing Phase 2 Implementation

**Workorder:** WO-COEREF-TESTING-001
**Phase:** 2 of 4 (Framework Detection & Execution)
**Status:** Ready to Start
**Entry Time:** 2025-12-27

---

## 🎯 Your Mission

Build the framework detection and test execution engine for the universal MCP testing server.

**Input:** Any project (Python, JavaScript, Rust, etc)
**Output:** Unified test results in standardized JSON schema
**Duration:** 8-10 hours
**Tasks:** 13 sequential subtasks

---

## ⚡ Quick Start (2 Minutes)

### Right Now
1. You are **Agent** implementing **coeref-testing**
2. **Phase 1** (4 tasks) is ✅ COMPLETE
3. **Phase 2** (13 tasks) is ⏳ READY FOR YOU
4. You have **8-10 hours** to complete Phase 2

### Your First Action (Do This First)
```bash
# Mark your first task as in_progress
mcp__coderef_workflow__update_task_status(
  project_path="C:\Users\willh\.mcp-servers",
  feature_name="coeref-testing",
  task_id="DETECT-001",
  status="in_progress"
)
```

### Then
1. Create file: `C:\Users\willh\.mcp-servers\coderef-testing\src\framework_detector.py`
2. Implement: `async def detect_pytest(project_path: str)` (see below for spec)
3. Test it
4. Mark complete
5. Move to next task

---

## 📋 The 13 Tasks (High-Level View)

```
Phase 2: Framework Detection & Execution
├─ Detection (5 tasks, 4.25h)
│  ├─ DETECT-001: pytest detection (1h) ← START HERE
│  ├─ DETECT-002: jest/vitest detection (1h)
│  ├─ DETECT-003: cargo/mocha detection (0.75h)
│  ├─ DETECT-004: caching & validation (0.5h)
│  └─ DETECT-TEST-001: unit tests (1h)
│
├─ Execution (8 tasks, 8.75h)
│  ├─ RUN-001: pytest execution (1.5h)
│  ├─ RUN-002: jest/vitest execution (1h)
│  ├─ RUN-003: cargo/mocha execution (0.75h)
│  ├─ RUN-004: async/parallel (1.5h)
│  ├─ RUN-005: timeout/error handling (1h)
│  ├─ RUN-TEST-001: test_runner unit tests (1h)
│  ├─ RUN-TEST-002: pytest integration tests (1h)
│  └─ RUN-TEST-003: jest integration tests (1h)
```

---

## 🚀 Task 1: DETECT-001 (Pytest Detection)

### What You Need to Build

**File:** `C:\Users\willh\.mcp-servers\coderef-testing\src\framework_detector.py`

**Function:** `async def detect_pytest(project_path: str) -> Optional[FrameworkInfo]`

### Implementation Spec

```python
from pathlib import Path
from typing import Optional
import json
from src.models import FrameworkInfo, TestFramework

async def detect_pytest(project_path: str) -> Optional[FrameworkInfo]:
    """
    Detect pytest test framework in a project.

    Pytest indicators:
    1. pyproject.toml with [tool.pytest] section
    2. tests/ directory exists
    3. conftest.py file exists anywhere

    Returns FrameworkInfo with framework, version, config_file
    Returns None if not detected
    """
    project = Path(project_path)

    # Check indicator 1: pyproject.toml with [tool.pytest]
    pyproject = project / "pyproject.toml"
    has_pytest_config = False
    if pyproject.exists():
        content = pyproject.read_text()
        if "[tool.pytest]" in content:
            has_pytest_config = True

    # Check indicator 2: tests/ directory
    tests_dir = project / "tests"
    has_tests_dir = tests_dir.is_dir()

    # Check indicator 3: conftest.py
    conftest = project / "conftest.py"
    has_conftest = conftest.exists()

    # At least one indicator must be present
    if not (has_pytest_config or has_tests_dir or has_conftest):
        return None

    # Detect version
    version = await get_version("pytest", project_path)

    # Determine config file
    config_file = None
    if pyproject.exists():
        config_file = str(pyproject)

    return FrameworkInfo(
        framework=TestFramework.PYTEST,
        version=version,
        config_file=config_file
    )
```

### How to Implement DETECT-001

**Step 1:** Create the file with function stubs for all 5 frameworks
```python
async def detect_frameworks(project_path: str) -> FrameworkDetectionResult:
    """Main entry point"""
    pass

async def detect_pytest(project_path: str) -> Optional[FrameworkInfo]:
    """Detect pytest"""
    pass

async def detect_jest(project_path: str) -> Optional[FrameworkInfo]:
    """Detect jest"""
    pass

# ... repeat for vitest, cargo, mocha
```

**Step 2:** Implement each detection function (see spec above)

**Step 3:** Implement `detect_frameworks()` to call all detectors and collect results

**Step 4:** Update server.py handlers:
```python
async def handle_discover_tests(args: Dict[str, Any]) -> List[TextContent]:
    """Handle discover_tests tool call."""
    project_path = args.get("project_path")

    from src.framework_detector import detect_frameworks
    result = await detect_frameworks(project_path)

    return [TextContent(type="text", text=json.dumps(result.dict()))]
```

**Step 5:** Mark task complete

---

## 📚 Where to Find Everything

### Reference Documentation (In This Project)
- **TESTING_GUIDE.md** (502 lines) - Architecture & framework patterns
- **CLAUDE.md** (347 lines) - Project overview & tool specs
- **START_HERE.md** (350 lines) - How to start
- **PHASE_2_QUICKSTART.md** (250 lines) - Quick reference
- **AGENT_CONTINUATION_INSTRUCTIONS.md** (300 lines) - Detailed steps

### Code Files (Already Exist)
- **server.py** (350 lines) - MCP server with 14 tool definitions
- **src/models.py** (622 lines) - All Pydantic schemas
- **pyproject.toml** (87 lines) - Dependencies configured

### What You Build
- **src/framework_detector.py** (NEW - ~250 lines) ← Start here
- **src/test_runner.py** (NEW - ~350 lines) ← Build after detection
- **tests/test_framework_detector.py** (NEW - ~200 lines)
- **tests/test_runner.py** (NEW - ~250 lines)
- **tests/integration/test_pytest.py** (NEW - ~100 lines)
- **tests/integration/test_jest.py** (NEW - ~100 lines)

---

## ✅ Success Criteria for Phase 2

When complete, all of these must pass:

```bash
# 1. All 13 tasks marked as completed
mcp__coderef_workflow__update_task_status(..., status="completed")

# 2. All unit tests passing
pytest tests/ -v
# Expected: 100% pass rate

# 3. Type checking passes
mypy src/ --ignore-missing-imports
# Expected: No errors

# 4. Code style passes
black src/ tests/
ruff check src/ tests/
# Expected: No violations

# 5. Server starts without errors
python server.py
# Expected: "Server running - listening for requests"

# 6. All 5 frameworks detected
# Expected: pytest, jest, vitest, cargo, mocha all detected correctly

# 7. All frameworks execute tests
# Expected: Results in UnifiedTestResults schema for all 5 frameworks
```

---

## 🗂️ Project Structure (You'll Create)

```
coderef-testing/
├── src/
│   ├── __init__.py ✅
│   ├── models.py ✅ (622 lines)
│   ├── framework_detector.py ← YOU BUILD (250 lines)
│   ├── test_runner.py ← YOU BUILD (350 lines)
│   ├── test_aggregator.py (Phase 3)
│   ├── result_analyzer.py (Phase 3)
│   └── test_coordinator.py (Phase 3)
│
├── tests/
│   ├── __init__.py ← YOU CREATE (empty)
│   ├── test_framework_detector.py ← YOU CREATE (200 lines)
│   ├── test_runner.py ← YOU CREATE (250 lines)
│   └── integration/
│       ├── __init__.py ← YOU CREATE (empty)
│       ├── test_pytest.py ← YOU CREATE (100 lines)
│       └── test_jest.py ← YOU CREATE (100 lines)
│
├── server.py ✅ (350 lines - modify handlers)
├── pyproject.toml ✅ (87 lines)
└── [documentation files]
```

---

## 📖 The Framework Detection Pattern

All 5 frameworks follow the same pattern:

### Pattern 1: pytest
```python
async def detect_pytest(project_path: str) -> Optional[FrameworkInfo]:
    project = Path(project_path)

    # Check for pytest indicators
    has_pyproject = (project / "pyproject.toml").exists() and \
                    "[tool.pytest]" in (project / "pyproject.toml").read_text()
    has_tests = (project / "tests").is_dir()
    has_conftest = (project / "conftest.py").exists()

    if not (has_pyproject or has_tests or has_conftest):
        return None

    version = await get_version("pytest", project_path)
    return FrameworkInfo(
        framework=TestFramework.PYTEST,
        version=version,
        config_file=str(project / "pyproject.toml") if (project / "pyproject.toml").exists() else None
    )
```

### Pattern 2: jest
```python
async def detect_jest(project_path: str) -> Optional[FrameworkInfo]:
    project = Path(project_path)

    # Check for jest indicators
    package_json = project / "package.json"
    has_jest_config = False
    if package_json.exists():
        content = json.loads(package_json.read_text())
        has_jest_config = "jest" in content

    has_config_file = (project / "jest.config.js").exists() or \
                      (project / "jest.config.json").exists()

    if not (has_jest_config or has_config_file):
        return None

    version = await get_version("jest", project_path)
    return FrameworkInfo(
        framework=TestFramework.JEST,
        version=version,
        config_file=str(project / "jest.config.js") if (project / "jest.config.js").exists() else None
    )
```

**Use this pattern for vitest, cargo, mocha too.**

---

## 🔄 Workflow for Each Task

For each of the 13 tasks:

1. **Mark In Progress:**
   ```bash
   mcp__coderef_workflow__update_task_status(
     project_path="C:\Users\willh\.mcp-servers",
     feature_name="coeref-testing",
     task_id="DETECT-001",  # Update task ID each time
     status="in_progress"
   )
   ```

2. **Implement:** Code the feature (follow specs in AGENT_CONTINUATION_INSTRUCTIONS.md)

3. **Test:** Run `pytest tests/ -v` (for test tasks)

4. **Mark Complete:**
   ```bash
   mcp__coderef_workflow__update_task_status(
     project_path="C:\Users\willh\.mcp-servers",
     feature_name="coeref-testing",
     task_id="DETECT-001",  # Update task ID
     status="completed"
   )
   ```

5. **Next Task:** Repeat with DETECT-002

---

## ⏱️ Expected Timeline

```
Hour 1:  DETECT-001 (pytest detection) ← YOU START HERE
Hour 2:  DETECT-002 (jest/vitest detection)
Hour 3:  DETECT-003 + DETECT-004 (cargo/mocha + caching)
Hour 4:  DETECT-TEST-001 (unit tests)
Hour 5.5: RUN-001 (pytest execution)
Hour 6.5: RUN-002 (jest/vitest execution)
Hour 7.25: RUN-003 (cargo/mocha execution)
Hour 8.75: RUN-004 + RUN-005 (parallel + timeout)
Hour 9.75: RUN-TEST-001 (test runner unit tests)
Hour 11:  RUN-TEST-002 + RUN-TEST-003 (integration tests)
Hour 11:  DONE! ✅ Phase 2 complete
```

---

## 🎓 Reference Schema

All results must conform to this schema (from src/models.py):

```python
class FrameworkInfo(BaseModel):
    framework: TestFramework  # pytest, jest, vitest, cargo, mocha, unknown
    version: Optional[str]    # "7.4.0"
    config_file: Optional[str]  # "/path/to/pyproject.toml"
    detected_at: datetime     # Auto-set to now

class FrameworkDetectionResult(BaseModel):
    detected: bool            # True if any framework found
    frameworks: List[FrameworkInfo]  # List of detected frameworks
    test_files: List[str]     # List of test file paths
    config_files: List[str]   # List of config file paths

class UnifiedTestResults(BaseModel):
    project: str              # Project path
    framework: FrameworkInfo  # Which framework was used
    summary: TestSummary      # Aggregated stats
    tests: List[TestResult]   # Individual test results
    timestamp: datetime       # When results were collected
```

---

## 💻 Commands You'll Use

### Task Tracking
```bash
# Start a task
mcp__coderef_workflow__update_task_status(
  project_path="C:\Users\willh\.mcp-servers",
  feature_name="coeref-testing",
  task_id="DETECT-001",
  status="in_progress"
)

# Complete a task
mcp__coderef_workflow__update_task_status(
  project_path="C:\Users\willh\.mcp-servers",
  feature_name="coeref-testing",
  task_id="DETECT-001",
  status="completed"
)
```

### Testing
```bash
# Run all tests
cd C:\Users\willh\.mcp-servers\coderef-testing
pytest tests/ -v

# Run specific test
pytest tests/test_framework_detector.py -v

# Type check
mypy src/ --ignore-missing-imports

# Format code
black src/ tests/
ruff check src/ tests/
```

---

## 🆘 If You Get Stuck

| Problem | Solution |
|---------|----------|
| "Don't know how to start DETECT-001" | Read: AGENT_CONTINUATION_INSTRUCTIONS.md "Step 2" |
| "Don't know pytest detection markers" | Read: TESTING_GUIDE.md "Framework Detection" section |
| "Schema doesn't match" | Check: src/models.py FrameworkInfo class |
| "Tests are failing" | Run: `pytest tests/ -v` to see exact errors |
| "Don't know what's next" | Read: PHASE_2_QUICKSTART.md checklist |
| "Need visual timeline" | Read: AGENT_INSTRUCTIONS_VISUAL.md |
| "Lost context" | Read: START_HERE.md or CURRENT_STATUS.md |

---

## 🎯 Your Goal Right Now

**Do this in the next 5 minutes:**

1. ✅ Open `C:\Users\willh\.mcp-servers\coderef-testing\src\framework_detector.py` (create new file)

2. ✅ Paste this function stub:
   ```python
   from pathlib import Path
   from typing import Optional
   from src.models import FrameworkInfo, FrameworkDetectionResult, TestFramework

   async def detect_frameworks(project_path: str) -> FrameworkDetectionResult:
       """Detect all frameworks in project"""
       pass

   async def detect_pytest(project_path: str) -> Optional[FrameworkInfo]:
       """Detect pytest framework"""
       pass

   async def detect_jest(project_path: str) -> Optional[FrameworkInfo]:
       """Detect jest framework"""
       pass

   async def detect_vitest(project_path: str) -> Optional[FrameworkInfo]:
       """Detect vitest framework"""
       pass

   async def detect_cargo(project_path: str) -> Optional[FrameworkInfo]:
       """Detect cargo test framework"""
       pass

   async def detect_mocha(project_path: str) -> Optional[FrameworkInfo]:
       """Detect mocha framework"""
       pass

   async def get_version(framework: str, project_path: str) -> Optional[str]:
       """Get framework version"""
       pass
   ```

3. ✅ Start implementing `detect_pytest()` using the spec above

4. ✅ Test it

5. ✅ Mark DETECT-001 as completed

**You've got this! Go build! 🚀**

---

**Status:** Ready to Code
**Assigned To:** Agent
**Task:** DETECT-001 (pytest detection)
**Estimated Duration:** 8-10 hours to complete Phase 2
**Expected Completion:** Within 11 hours

Good luck! 💪
