# START HERE - Agent Continuation Guide

**Date:** 2025-12-27
**Status:** Phase 1 ✅ Complete | Phase 2 ⏳ Ready
**Workorder:** WO-COEREF-TESTING-001
**Your Next Steps:** 13 Tasks | 8-10 Hours

---

## What Happened (Context Summary)

The agent implementing coeref-testing lost context while working on Phase 1. All foundational work has been restored:

✅ **Phase 1 Complete (4/4 Tasks):**
- Directory structure created (src/, tests/, personas/, .claude/commands/)
- pyproject.toml configured (87 lines with all dependencies)
- server.py skeleton created (350+ lines with 14 MCP tools registered)
- src/models.py created (622 lines with unified Pydantic schemas)

📊 **Project Progress:**
- 4 of 37 tasks complete (11%)
- 1,400 lines of foundation code written
- Phase 2 ready to start immediately

---

## Your Mission: Implement Phase 2 (13 Tasks)

**Goal:** Build framework detection and test execution engine
**Duration:** 8-10 hours
**Output:** 1,400+ lines of production code + tests

### What You'll Build

```
┌─────────────────────────────────────────┐
│ Framework-Agnostic Test Engine          │
│                                         │
│ Input: Any project (pytest, jest, etc)  │
│ ↓                                       │
│ Framework Detector (auto-detect)        │
│ ↓                                       │
│ Test Runner (execute tests)             │
│ ↓                                       │
│ Result Normalizer (unified schema)      │
│ ↓                                       │
│ Output: UnifiedTestResults (JSON)       │
└─────────────────────────────────────────┘
```

### 13 Tasks Breakdown

| # | Task | Type | Duration | Files |
|---|------|------|----------|-------|
| 1 | DETECT-001 | Detection | 1h | framework_detector.py |
| 2 | DETECT-002 | Detection | 1h | (extend) |
| 3 | DETECT-003 | Detection | 0.75h | (extend) |
| 4 | DETECT-004 | Detection | 0.5h | (extend) |
| 5 | DETECT-TEST-001 | Testing | 1h | test_framework_detector.py |
| 6 | RUN-001 | Execution | 1.5h | test_runner.py |
| 7 | RUN-002 | Execution | 1h | (extend) |
| 8 | RUN-003 | Execution | 0.75h | (extend) |
| 9 | RUN-004 | Execution | 1.5h | (extend) |
| 10 | RUN-005 | Execution | 1h | (extend) |
| 11 | RUN-TEST-001 | Testing | 1h | test_runner.py tests |
| 12 | RUN-TEST-002 | Testing | 1h | pytest integration tests |
| 13 | RUN-TEST-003 | Testing | 1h | jest integration tests |

---

## Three Ways to Start (Pick One)

### 🚀 FAST START (5 minutes)
1. Read this file ✓ (you're here)
2. Jump to "Immediate Next Steps" below
3. Start DETECT-001

### 📖 BALANCED START (15 minutes)
1. Read this file ✓
2. Read: PHASE_2_QUICKSTART.md
3. Read: AGENT_CONTINUATION_INSTRUCTIONS.md "Step 2-3"
4. Start DETECT-001

### 🎓 COMPREHENSIVE START (40 minutes)
1. Read: CLAUDE.md (project overview, 347 lines)
2. Read: TESTING_GUIDE.md (architecture & vision, 502 lines)
3. Read: AGENT_CONTINUATION_INSTRUCTIONS.md (full guide)
4. Read: PHASE_2_QUICKSTART.md (reference)
5. Start DETECT-001

**Recommended:** BALANCED START (15 min) - gives you enough context without being overwhelming

---

## Immediate Next Steps (Right Now!)

### Step 1: Mark Task as In Progress (2 min)
Run this command to record that you're starting DETECT-001:

```bash
mcp__coderef_workflow__update_task_status(
  project_path="C:\Users\willh\.mcp-servers",
  feature_name="coeref-testing",
  task_id="DETECT-001",
  status="in_progress"
)
```

### Step 2: Read Quick Reference (3 min)
Read **PHASE_2_QUICKSTART.md** sections:
- "The 13 Tasks Ahead" (1 min)
- "What You Need to Build" (2 min)

### Step 3: Create framework_detector.py (45 min)

**Location:** `C:\Users\willh\.mcp-servers\coderef-testing\src\framework_detector.py`

**Key Function Signatures:**
```python
from typing import Optional, List
from pathlib import Path
from src.models import FrameworkInfo, FrameworkDetectionResult, TestFramework

async def detect_frameworks(project_path: str) -> FrameworkDetectionResult:
    """Detect all frameworks in project"""
    pass

async def detect_pytest(project_path: str) -> Optional[FrameworkInfo]:
    """Detect pytest: pyproject.toml, tests/, conftest.py"""
    pass

async def detect_jest(project_path: str) -> Optional[FrameworkInfo]:
    """Detect jest: package.json, jest.config.js"""
    pass

async def detect_vitest(project_path: str) -> Optional[FrameworkInfo]:
    """Detect vitest: vitest.config.ts, package.json"""
    pass

async def detect_cargo(project_path: str) -> Optional[FrameworkInfo]:
    """Detect cargo: Cargo.toml with [dev-dependencies]"""
    pass

async def detect_mocha(project_path: str) -> Optional[FrameworkInfo]:
    """Detect mocha: .mocharc.*, package.json"""
    pass

async def get_version(framework: str, project_path: str) -> Optional[str]:
    """Get framework version"""
    pass
```

**Reference Documentation:**
- See: TESTING_GUIDE.md "Framework Detection" section
- See: AGENT_CONTINUATION_INSTRUCTIONS.md "Step 2"
- See: plan.json section "6_implementation_phases.phases[1].tasks[0]"

### Step 4: Mark Task Complete (1 min)

```bash
mcp__coderef_workflow__update_task_status(
  project_path="C:\Users\willh\.mcp-servers",
  feature_name="coeref-testing",
  task_id="DETECT-001",
  status="completed"
)
```

### Step 5: Continue (Repeat Steps 1-4 for next task)

---

## File Reference Guide

### 📋 Documentation Files (Read These)

| File | Purpose | Read Time | When |
|------|---------|-----------|------|
| **START_HERE.md** | This file - quick start | 5 min | NOW |
| **PHASE_2_QUICKSTART.md** | Quick reference for Phase 2 | 3 min | After Step 1 |
| **AGENT_CONTINUATION_INSTRUCTIONS.md** | Detailed next steps | 15 min | Before coding |
| **CLAUDE.md** | Project overview | 10 min | For context |
| **TESTING_GUIDE.md** | Architecture & vision | 20 min | For deep understanding |
| **CURRENT_STATUS.md** | Project status dashboard | 5 min | For reference |
| **AGENT_INSTRUCTIONS_VISUAL.md** | Visual guide & timeline | 10 min | Optional |

### 💻 Code Files (Reference These)

| File | Purpose | Lines | Status |
|------|---------|-------|--------|
| server.py | MCP server skeleton | 350+ | ✅ Complete |
| src/models.py | Pydantic schemas | 622 | ✅ Complete |
| src/framework_detector.py | Framework detection | ~250 | → YOU build |
| src/test_runner.py | Test execution | ~350 | → YOU build |
| pyproject.toml | Dependencies | 87 | ✅ Complete |

### 📊 Planning Files (Track Progress)

| File | Purpose | Format |
|------|---------|--------|
| plan.json | Complete task plan | 10-section JSON |
| DELIVERABLES.md | Progress tracker | Markdown checklist |
| execution-log.json | Task status log | JSON array |

---

## The 13 Tasks in Order

### Detection Phase (5 tasks, ~4.25 hours)

**DETECT-001** - pytest detection
- Check: pyproject.toml, tests/, conftest.py
- Return: FrameworkInfo with version
- Effort: 1h

**DETECT-002** - jest/vitest detection
- Check: package.json, jest.config.js, vitest.config.ts
- Return: FrameworkInfo with version
- Effort: 1h

**DETECT-003** - cargo/mocha detection
- Check: Cargo.toml, .mocharc.*, mocha config
- Return: FrameworkInfo with version
- Effort: 0.75h

**DETECT-004** - caching & validation
- Add: 1-hour cache with TTL
- Add: Result validation
- Effort: 0.5h

**DETECT-TEST-001** - detection unit tests
- Test: Each framework detection
- Mock: Filesystem structures
- Effort: 1h

### Execution Phase (8 tasks, ~8.75 hours)

**RUN-001** - pytest execution
- Run: pytest --json-report
- Parse: JSON output
- Return: UnifiedTestResults
- Effort: 1.5h

**RUN-002** - jest/vitest execution
- Run: jest --json, vitest run
- Parse: JSON output
- Return: UnifiedTestResults
- Effort: 1h

**RUN-003** - cargo/mocha execution
- Run: cargo test, mocha --json
- Parse: Custom formats
- Return: UnifiedTestResults
- Effort: 0.75h

**RUN-004** - async/parallel execution
- Implement: asyncio.gather() for parallel
- Implement: Worker pool with configurable size
- Effort: 1.5h

**RUN-005** - timeout/error handling
- Add: execute_with_timeout() function
- Handle: subprocess errors gracefully
- Return: Meaningful error results
- Effort: 1h

**RUN-TEST-001** - test_runner unit tests
- Mock: Subprocess calls
- Test: Schema compliance
- Test: Error handling
- Effort: 1h

**RUN-TEST-002** - pytest integration tests
- Real: pytest execution
- Real: Result parsing
- Real: Schema compliance
- Effort: 1h

**RUN-TEST-003** - jest integration tests
- Real: jest execution
- Real: Result parsing
- Real: Schema compliance
- Effort: 1h

---

## Success Metrics

### By Task Completion
- ✅ Task 1-5: Detection working for all 5 frameworks
- ✅ Task 6-10: Execution working for all 5 frameworks
- ✅ Task 11-13: All tests passing

### Final Validation
```bash
# All tests pass
pytest tests/ -v

# Type checking passes
mypy src/ --ignore-missing-imports

# Code style passes
black src/ tests/
ruff check src/ tests/

# Server starts without errors
python server.py
```

---

## Troubleshooting Quick Guide

| Problem | Solution |
|---------|----------|
| "Don't know how to start" | Read PHASE_2_QUICKSTART.md + follow "Start Here" |
| "Need framework details" | Check TESTING_GUIDE.md "Framework Detection" section |
| "Schema mismatch" | Reference src/models.py for UnifiedTestResults |
| "Tests failing" | Run `pytest tests/ -v` to see errors |
| "Lost context again" | Read AGENT_CONTINUATION_INSTRUCTIONS.md |
| "Don't know next task" | Check PHASE_2_QUICKSTART.md checklist |
| "Need visual guide" | Read AGENT_INSTRUCTIONS_VISUAL.md |

---

## Key Commands You'll Use

### Task Tracking
```bash
# Mark task starting
mcp__coderef_workflow__update_task_status(
  project_path="C:\Users\willh\.mcp-servers",
  feature_name="coeref-testing",
  task_id="DETECT-001",
  status="in_progress"
)

# Mark task complete
mcp__coderef_workflow__update_task_status(
  project_path="C:\Users\willh\.mcp-servers",
  feature_name="coeref-testing",
  task_id="DETECT-001",
  status="completed"
)
```

### Testing & Validation
```bash
# Run all tests
cd C:\Users\willh\.mcp-servers\coderef-testing
pytest tests/ -v

# Type checking
mypy src/ --ignore-missing-imports

# Code formatting
black src/ tests/
ruff check src/ tests/
```

---

## Timeline

```
Hour 1 ← YOU START HERE (DETECT-001)
Hour 1-2: DETECT-001 & DETECT-002
Hour 2-3: DETECT-003 & DETECT-004
Hour 3-4: DETECT-TEST-001 + unit tests pass
Hour 4-5.5: RUN-001 (pytest execution)
Hour 5.5-6.5: RUN-002 (jest/vitest execution)
Hour 6.5-7.25: RUN-003 (cargo/mocha execution)
Hour 7.25-8.75: RUN-004 + RUN-005 (parallel & timeout)
Hour 8.75-9.75: RUN-TEST-001 (test_runner unit tests)
Hour 9.75-11: RUN-TEST-002 + RUN-TEST-003 (integration tests)
Hour 11: DONE! Phase 2 complete ✅
```

---

## What Happens After Phase 2

Once all 13 tasks complete:

1. **Agent (or you) moves to Phase 3:**
   - Result aggregation & analysis
   - Coverage metrics
   - Flaky test detection
   - Performance analysis
   - 6 tasks, 7-9 hours

2. **Then Phase 4:**
   - Complete MCP tool implementations
   - 12+ slash commands
   - testing-expert persona
   - Documentation & release
   - 14 tasks, 9-11 hours

3. **Final state:**
   - Complete coeref-testing server
   - All 14 MCP tools functional
   - All 37 tasks complete
   - Ready to use with CodeRef ecosystem & any project

---

## Questions?

### "Where do I find X?"
- Framework detection details → TESTING_GUIDE.md "Framework Detection"
- Pydantic schemas → src/models.py
- Task specifications → plan.json section 6.1.2
- Tool specs → CLAUDE.md section "Tools Catalog"

### "How do I do Y?"
- Implement pytest detection → AGENT_CONTINUATION_INSTRUCTIONS.md Step 2
- Create unit tests → PHASE_2_QUICKSTART.md section "Pattern 1"
- Update task status → This file above
- Run tests → Key Commands section above

### "I'm stuck on Z"
- Framework detection → Check TESTING_GUIDE.md examples
- Schema compliance → Check src/models.py structure
- Test execution → Check existing handlers in server.py
- Async/parallel → Check Python asyncio documentation

---

## Final Checklist Before Starting

- [ ] Read this file (START_HERE.md) ✓
- [ ] Understand Phase 1 is complete ✓
- [ ] Know what Phase 2 requires (13 tasks) ✓
- [ ] Have PHASE_2_QUICKSTART.md open ✓
- [ ] Know how to mark tasks in/complete ✓
- [ ] Ready to start DETECT-001 ✓

---

## Go Time! 🚀

**You have:**
- ✅ Complete foundation (Phase 1)
- ✅ Clear specifications (plan.json, TESTING_GUIDE.md)
- ✅ Detailed instructions (AGENT_CONTINUATION_INSTRUCTIONS.md)
- ✅ Quick reference (PHASE_2_QUICKSTART.md)
- ✅ Everything you need to succeed

**Next action:**
1. Mark DETECT-001 as in_progress
2. Create src/framework_detector.py
3. Update server.py handlers
4. Mark DETECT-001 as completed
5. Move to DETECT-002

**Estimated time to Phase 2 completion: 8-10 hours**

Let's build this! 💪

---

**Last Updated:** 2025-12-27
**Status:** Ready to Implement ✅
**Next Task:** DETECT-001 (pytest detection)
**Expected Completion:** Within 10 hours
