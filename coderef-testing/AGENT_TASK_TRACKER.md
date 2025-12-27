# Agent Task Tracker - Phase 2 Implementation

**Workorder:** WO-COEREF-TESTING-001
**Phase:** 2 of 4 (Framework Detection & Execution)
**Status:** ⏳ Ready for Agent to Start
**Last Updated:** 2025-12-27

---

## 📊 Task Progress Dashboard

### Phase 1: Setup & Core Architecture ✅ COMPLETE
- [x] SETUP-001: Create project structure
- [x] SETUP-002: Create pyproject.toml
- [x] SETUP-003: Create server.py skeleton
- [x] SETUP-004: Create models.py schemas

**Status:** 4/4 ✅ | **Duration:** ~3 hours | **Code:** ~1,400 lines

---

## 📋 Phase 2: Framework Detection & Execution ⏳ READY

### Detection Tasks (5 tasks)

#### [ ] DETECT-001: pytest detection
- **Status:** Pending → in_progress → completed
- **Duration:** 1 hour
- **Files:** src/framework_detector.py (new)
- **What to Build:**
  - Function: `async def detect_pytest(project_path) -> FrameworkInfo`
  - Check: pyproject.toml, tests/, conftest.py
  - Return: FrameworkInfo with version
- **Reference:** AGENT_ENTRY_POINT.md "Task 1: DETECT-001"
- **Checklist:**
  - [ ] Create src/framework_detector.py
  - [ ] Implement detect_pytest()
  - [ ] Implement detect_frameworks() caller
  - [ ] Update server.py handlers
  - [ ] Test implementation
  - [ ] Mark complete

#### [ ] DETECT-002: jest/vitest detection
- **Status:** Pending
- **Duration:** 1 hour
- **Files:** src/framework_detector.py (extend)
- **What to Build:**
  - Function: `async def detect_jest() + async def detect_vitest()`
  - Check: package.json, jest.config.js, vitest.config.ts
  - Return: FrameworkInfo with version
- **Reference:** AGENT_CONTINUATION_INSTRUCTIONS.md "Step 2"
- **Checklist:**
  - [ ] Add detect_jest() function
  - [ ] Add detect_vitest() function
  - [ ] Test both frameworks
  - [ ] Mark complete

#### [ ] DETECT-003: cargo/mocha detection
- **Status:** Pending
- **Duration:** 0.75 hours
- **Files:** src/framework_detector.py (extend)
- **What to Build:**
  - Function: `async def detect_cargo() + async def detect_mocha()`
  - Check: Cargo.toml, .mocharc.*, mocha config
  - Return: FrameworkInfo with version
- **Reference:** AGENT_CONTINUATION_INSTRUCTIONS.md "Step 2"
- **Checklist:**
  - [ ] Add detect_cargo() function
  - [ ] Add detect_mocha() function
  - [ ] Test both frameworks
  - [ ] Mark complete

#### [ ] DETECT-004: caching & validation
- **Status:** Pending
- **Duration:** 0.5 hours
- **Files:** src/framework_detector.py (enhance)
- **What to Build:**
  - Add caching with 1-hour TTL
  - Add result validation
  - Thread-safe caching
- **Reference:** AGENT_CONTINUATION_INSTRUCTIONS.md "Key Design Patterns"
- **Checklist:**
  - [ ] Implement caching mechanism
  - [ ] Add TTL expiration
  - [ ] Add thread-safety locks
  - [ ] Test cache behavior
  - [ ] Mark complete

#### [ ] DETECT-TEST-001: detection unit tests
- **Status:** Pending
- **Duration:** 1 hour
- **Files:** tests/test_framework_detector.py (new), tests/__init__.py (new)
- **What to Build:**
  - Unit tests for each framework detection
  - Mock filesystem structures
  - Test version extraction
  - Test caching
- **Reference:** AGENT_CONTINUATION_INSTRUCTIONS.md "Step 5"
- **Checklist:**
  - [ ] Create tests/__init__.py
  - [ ] Create tests/test_framework_detector.py
  - [ ] Write tests for pytest detection
  - [ ] Write tests for jest detection
  - [ ] Write tests for vitest detection
  - [ ] Write tests for cargo detection
  - [ ] Write tests for mocha detection
  - [ ] Write tests for caching
  - [ ] Run `pytest tests/test_framework_detector.py -v`
  - [ ] All tests pass
  - [ ] Mark complete

**Subtotal Detection:** 5 tasks | 4.25 hours | ~250 lines code

---

### Execution Tasks (8 tasks)

#### [ ] RUN-001: pytest execution
- **Status:** Pending
- **Duration:** 1.5 hours
- **Files:** src/test_runner.py (new)
- **What to Build:**
  - Function: `async def run_pytest(project_path, **kwargs) -> UnifiedTestResults`
  - Run: pytest --json-report=report.json
  - Parse JSON output
  - Convert to UnifiedTestResults schema
- **Reference:** AGENT_CONTINUATION_INSTRUCTIONS.md "Step 3"
- **Checklist:**
  - [ ] Create src/test_runner.py
  - [ ] Implement run_tests() dispatcher
  - [ ] Implement run_pytest() for pytest
  - [ ] Parse pytest JSON output
  - [ ] Convert to UnifiedTestResults
  - [ ] Update server.py handlers (4 execution tools)
  - [ ] Test implementation
  - [ ] Mark complete

#### [ ] RUN-002: jest/vitest execution
- **Status:** Pending
- **Duration:** 1 hour
- **Files:** src/test_runner.py (extend)
- **What to Build:**
  - Function: `async def run_jest() + async def run_vitest()`
  - Run: jest --json, vitest run --reporter=json
  - Parse JSON outputs
  - Convert to UnifiedTestResults
- **Reference:** AGENT_CONTINUATION_INSTRUCTIONS.md "Step 3"
- **Checklist:**
  - [ ] Implement run_jest()
  - [ ] Implement run_vitest()
  - [ ] Parse jest JSON output
  - [ ] Parse vitest JSON output
  - [ ] Convert both to UnifiedTestResults
  - [ ] Test both frameworks
  - [ ] Mark complete

#### [ ] RUN-003: cargo/mocha execution
- **Status:** Pending
- **Duration:** 0.75 hours
- **Files:** src/test_runner.py (extend)
- **What to Build:**
  - Function: `async def run_cargo() + async def run_mocha()`
  - Run: cargo test, mocha --json
  - Parse custom output formats
  - Convert to UnifiedTestResults
- **Reference:** AGENT_CONTINUATION_INSTRUCTIONS.md "Step 3"
- **Checklist:**
  - [ ] Implement run_cargo()
  - [ ] Implement run_mocha()
  - [ ] Parse cargo test output
  - [ ] Parse mocha JSON output
  - [ ] Convert both to UnifiedTestResults
  - [ ] Test both frameworks
  - [ ] Mark complete

#### [ ] RUN-004: async/parallel execution
- **Status:** Pending
- **Duration:** 1.5 hours
- **Files:** src/test_runner.py (enhance)
- **What to Build:**
  - Async execution with asyncio.gather()
  - Worker pool with configurable size
  - Parallel test execution
  - Proper isolation between workers
- **Reference:** AGENT_CONTINUATION_INSTRUCTIONS.md "Step 3"
- **Checklist:**
  - [ ] Design asyncio worker pool
  - [ ] Implement parallel execution
  - [ ] Add configurable worker count
  - [ ] Test parallel execution
  - [ ] Verify no conflicts between workers
  - [ ] Mark complete

#### [ ] RUN-005: timeout/error handling
- **Status:** Pending
- **Duration:** 1 hour
- **Files:** src/test_runner.py (enhance)
- **What to Build:**
  - Function: `async def execute_with_timeout(cmd, timeout)`
  - Handle subprocess timeouts
  - Catch and report errors gracefully
  - Return meaningful error results
- **Reference:** AGENT_CONTINUATION_INSTRUCTIONS.md "Step 3"
- **Checklist:**
  - [ ] Implement execute_with_timeout()
  - [ ] Handle TimeoutError
  - [ ] Handle subprocess errors
  - [ ] Return error results
  - [ ] Test timeout handling
  - [ ] Test error handling
  - [ ] Mark complete

#### [ ] RUN-TEST-001: test_runner unit tests
- **Status:** Pending
- **Duration:** 1 hour
- **Files:** tests/test_runner.py (new)
- **What to Build:**
  - Mock subprocess calls
  - Test schema compliance
  - Test error handling
  - Test parallel execution
- **Reference:** AGENT_CONTINUATION_INSTRUCTIONS.md "Step 5"
- **Checklist:**
  - [ ] Create tests/test_runner.py
  - [ ] Write tests for run_tests()
  - [ ] Write tests for pytest execution
  - [ ] Write tests for schema compliance
  - [ ] Write tests for error handling
  - [ ] Write tests for parallel execution
  - [ ] Run `pytest tests/test_runner.py -v`
  - [ ] All tests pass
  - [ ] Mark complete

#### [ ] RUN-TEST-002: pytest integration tests
- **Status:** Pending
- **Duration:** 1 hour
- **Files:** tests/integration/test_pytest.py (new), tests/integration/__init__.py (new)
- **What to Build:**
  - Real pytest execution on sample project
  - Verify results accuracy
  - Test result normalization
- **Reference:** AGENT_CONTINUATION_INSTRUCTIONS.md "Step 6"
- **Checklist:**
  - [ ] Create tests/integration/__init__.py
  - [ ] Create tests/integration/test_pytest.py
  - [ ] Create sample pytest project
  - [ ] Test actual pytest execution
  - [ ] Verify UnifiedTestResults accuracy
  - [ ] Run `pytest tests/integration/test_pytest.py -v`
  - [ ] All tests pass
  - [ ] Mark complete

#### [ ] RUN-TEST-003: jest integration tests
- **Status:** Pending
- **Duration:** 1 hour
- **Files:** tests/integration/test_jest.py (new)
- **What to Build:**
  - Real jest execution on sample project
  - Verify results accuracy
  - Test result normalization
- **Reference:** AGENT_CONTINUATION_INSTRUCTIONS.md "Step 6"
- **Checklist:**
  - [ ] Create tests/integration/test_jest.py
  - [ ] Create sample jest project
  - [ ] Test actual jest execution
  - [ ] Verify UnifiedTestResults accuracy
  - [ ] Run `pytest tests/integration/test_jest.py -v`
  - [ ] All tests pass
  - [ ] Mark complete

**Subtotal Execution:** 8 tasks | 8.75 hours | ~350 lines code

---

## 📈 Phase 2 Summary

| Item | Count | Hours | Lines |
|------|-------|-------|-------|
| Detection Tasks | 5 | 4.25h | ~250 |
| Execution Tasks | 8 | 8.75h | ~350 |
| **TOTAL** | **13** | **8-10h** | **~1,400** |

**Files to Create:**
- src/framework_detector.py (NEW)
- src/test_runner.py (NEW)
- tests/__init__.py (NEW)
- tests/test_framework_detector.py (NEW)
- tests/test_runner.py (NEW)
- tests/integration/__init__.py (NEW)
- tests/integration/test_pytest.py (NEW)
- tests/integration/test_jest.py (NEW)

**Files to Modify:**
- server.py (replace placeholder handlers)

---

## 🎯 How to Use This Tracker

### Before Starting a Task
1. Find task in checklist above
2. Read "What to Build" section
3. Check reference document
4. Mark task as [ ] (pending)

### While Working on a Task
1. Mark task as **in_progress** in plan.json
2. Check off subtasks as you complete them
3. Run tests frequently
4. Reference documentation as needed

### When Completing a Task
1. Run full test suite: `pytest tests/ -v`
2. Run type checking: `mypy src/`
3. Mark all subtasks complete: [x]
4. Call update_task_status() with "completed"
5. Move to next task

---

## ✅ Task Status Legend

| Status | Meaning | Action |
|--------|---------|--------|
| [ ] | Pending - not started | Ready to begin |
| [WIP] | In Progress - actively working | Continue work |
| [x] | Completed - finished & tested | Move to next |
| [BLOCKED] | Blocked - waiting on something | Resolve blocker |

---

## 📍 Quick Navigation

### Finding Your Next Task
1. Scroll to "Detection Tasks" or "Execution Tasks"
2. Find first unchecked [ ] item
3. Click reference link
4. Start coding

### When You Get Stuck
- **"What do I build?"** → See "What to Build" section above
- **"How do I implement?"** → See "Reference" section above
- **"Which file?"** → See "Files" section above
- **"Detailed steps?"** → Read AGENT_CONTINUATION_INSTRUCTIONS.md

### Marking Tasks Complete
```bash
mcp__coderef_workflow__update_task_status(
  project_path="C:\Users\willh\.mcp-servers",
  feature_name="coeref-testing",
  task_id="DETECT-001",  # Change this for each task
  status="completed"
)
```

---

## 🏁 Phase 2 Success Criteria

When all 13 tasks are complete:

✅ **Framework Detection:**
- pytest detected correctly
- jest detected correctly
- vitest detected correctly
- cargo detected correctly
- mocha detected correctly
- Version extraction working
- Caching working

✅ **Test Execution:**
- pytest execution returns UnifiedTestResults
- jest execution returns UnifiedTestResults
- vitest execution returns UnifiedTestResults
- cargo execution returns UnifiedTestResults
- mocha execution returns UnifiedTestResults
- Parallel execution working
- Timeout handling working
- Error handling working

✅ **Testing:**
- All unit tests passing
- All integration tests passing
- Type checking passes
- Code style passes

✅ **Task Tracking:**
- All 13 tasks marked as "completed"
- No "pending" tasks remaining
- DELIVERABLES.md updated with metrics

---

## 🚀 Start Now!

**Your first task:** DETECT-001 (pytest detection)

**Quick start:**
1. Read AGENT_ENTRY_POINT.md (5 min)
2. Create src/framework_detector.py
3. Implement detect_pytest()
4. Test & mark complete
5. Continue to DETECT-002

**Expected completion:** 8-10 hours for all 13 tasks

**You've got everything you need. Let's build! 💪**

---

Last Updated: 2025-12-27
Status: Ready for Agent
Next Task: DETECT-001 (pytest detection)
Estimated Duration: 8-10 hours to Phase 2 completion
