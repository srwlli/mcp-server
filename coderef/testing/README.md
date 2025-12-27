# CodeRef Ecosystem Testing

**Central Hub for All MCP Server Testing**

This directory contains test results, documentation, and test suites for the entire CodeRef ecosystem.

---

## Quick Navigation

**First Time Here?**
- Start with [INDEX.md](INDEX.md) - Complete test catalog and navigation guide
- Read [TESTING-GUIDE.md](TESTING-GUIDE.md) - How to run tests

**Latest Results**
- All test results stored in `results/LATEST/` (symlink to current date)
- Timestamped folders: `results/2025-12-26/`, `results/2025-12-25/`, etc.

**Per-Server Tests**
- **coderef-context:** `../../coderef-context/coderef/testing/`
- **coderef-workflow:** `../../coderef-workflow/coderef/testing/`
- **coderef-docs:** `../../coderef-docs/coderef/testing/`
- **coderef-personas:** `../../coderef-personas/coderef/testing/`

---

## Structure

```
coderef/testing/
├── README.md (this file)
├── INDEX.md (complete catalog)
├── TESTING-GUIDE.md (how to run tests)
├── TESTING-ARCHITECTURE.md (design docs)
├── TEST-SETUP-CHECKLIST.md (checklist)
│
├── results/
│   ├── 2025-12-26/ (latest)
│   │   ├── ecosystem-proof-results.md
│   │   ├── injection-test-results.md
│   │   └── workorder-test-results.md
│   ├── 2025-12-25/
│   └── LATEST/ → symlink to 2025-12-26/
│
├── proof-tests/
│   ├── CODEREF_INJECTION_PROOF.md
│   ├── ECOSYSTEM_PROOF_COMPLETE.md
│   └── PROFESSIONAL_TESTING_REVIEW.md
│
└── architecture/
    └── test-planning-docs.md
```

---

## Test Categories

### 1. Proof Tests (Ecosystem-Wide)
- **Location:** `proof-tests/`
- **Purpose:** Demonstrate coderef ecosystem works end-to-end
- **What They Test:** Code intelligence injection, planning workflows, documentation generation
- **Results:** `results/2025-12-26/ecosystem-proof-results.md`

### 2. Injection Tests (Cross-Server)
- **Location:** Results in `results/2025-12-26/injection-test-results.md`
- **Purpose:** Prove coderef-context injects correctly into workflow/personas
- **What They Test:**
  - test-coderef-context-injection
  - test-coderef-docs-injection
  - test-coderef-personas-injection
- **Status:** All 3 completed ✅

### 3. Workorder Tests (Planning System)
- **Location:** Results in `results/2025-12-26/workorder-test-results.md`
- **Purpose:** Validate /create-workorder workflow
- **What They Test:** Planning, analysis, validation, task generation
- **Results:** WO-WORKFLOW-REFACTOR-001 (16/16 tasks complete)

### 4. Per-Server Unit Tests
- **Location:** `../../{server}/coderef/testing/`
- **Purpose:** Test individual server tools
- **What They Test:**
  - coderef-context: scan, query, impact, complexity, patterns (tools)
  - coderef-workflow: planning, validation, orchestration
  - coderef-docs: doc generation, changelog, standards
  - coderef-personas: persona activation, custom persona creation

---

## Running Tests

### Quick Start

```bash
# View latest results
cat coderef/testing/results/LATEST/ecosystem-proof-results.md

# View all proof test docs
ls coderef/testing/proof-tests/

# View per-server tests
ls coderef-context/coderef/testing/results/LATEST/
```

### Full Test Suite

See [TESTING-GUIDE.md](TESTING-GUIDE.md) for detailed instructions.

---

## Test Status Summary

| Test Type | Status | Last Run | Location |
|-----------|--------|----------|----------|
| Ecosystem Proof | ✅ Complete | 2025-12-26 | `proof-tests/` |
| Injection (3x) | ✅ Complete | 2025-12-26 | `results/2025-12-26/` |
| Workorder | ✅ Complete | 2025-12-26 | `results/2025-12-26/` |
| coderef-context | ⏳ Pending | - | `../../coderef-context/coderef/testing/` |
| coderef-workflow | ✅ Partial | 2025-12-26 | `../../coderef-workflow/coderef/testing/` |
| coderef-docs | ⏳ Pending | - | `../../coderef-docs/coderef/testing/` |
| coderef-personas | ✅ Partial | 2025-12-26 | `../../coderef-personas/coderef/testing/` |

---

## Key Documents

- **[INDEX.md](INDEX.md)** - Complete test catalog with all test files listed
- **[TESTING-GUIDE.md](TESTING-GUIDE.md)** - Instructions for running tests
- **[TESTING-ARCHITECTURE.md](TESTING-ARCHITECTURE.md)** - Design and architecture docs
- **[TEST-SETUP-CHECKLIST.md](TEST-SETUP-CHECKLIST.md)** - Verification checklist

---

## Adding New Tests

When you add a new test:

1. **Create test file** in appropriate location:
   - Ecosystem-wide: `proof-tests/` or `results/{DATE}/`
   - Per-server: `../../{server}/coderef/testing/results/{DATE}/`

2. **Follow naming convention:**
   - Test results: `test-{feature}-results.md`
   - Proof tests: `{DESCRIPTION}_PROOF.md`
   - Examples: `test-scan-tool-results.md`, `CODEREF_INJECTION_PROOF.md`

3. **Update timestamped folder:**
   - Add results to `results/{TODAY'S_DATE}/`
   - Update symlink: `results/LATEST/`

4. **Update INDEX.md** with new test entry

---

**Last Updated:** 2025-12-26
**Maintained by:** willh, Claude Code AI
**System Status:** ✅ Testing infrastructure organized and ready

