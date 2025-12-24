# Known Issues Log

Track recurring issues encountered during development for quick reference.

---

## Format

```markdown
### ISSUE-XXX: Short Title
**Category:** Test | Build | Runtime | Integration
**Severity:** Low | Medium | High
**First Seen:** YYYY-MM-DD
**Status:** Open | Resolved | Workaround

**Symptom:**
What happens when this issue occurs.

**Root Cause:**
Why it happens (if known).

**Resolution/Workaround:**
How to fix or work around it.

**Files Affected:**
- path/to/file.py
```

---

## Active Issues

### ISSUE-001: Test assertion mismatch for files_generated paths
**Category:** Test
**Severity:** Low
**First Seen:** 2025-12-15
**Status:** Resolved

**Symptom:**
Test expects `'API.md' in result['files_generated']` but implementation returns full path `'coderef/foundation-docs/API.md'`.

**Root Cause:**
After adding README.md to project root, files_generated now returns full relative paths for clarity.

**Resolution:**
Use `any('API.md' in f for f in result['files_generated'])` instead of exact match.

**Files Affected:**
- tests/unit/generators/test_coderef_foundation_generator.py

---

### ISSUE-002: Symlink tests skipped on Windows
**Category:** Test
**Severity:** Low
**First Seen:** 2025-12-15
**Status:** Workaround

**Symptom:**
`test_symlinks_handled` skipped with "Symlinks not supported on this platform".

**Root Cause:**
Windows requires admin privileges to create symlinks without developer mode.

**Resolution/Workaround:**
Test is properly skipped with `pytest.skip()`. No action needed.

**Files Affected:**
- tests/unit/generators/test_coderef_foundation_generator.py:781

---

### ISSUE-003: PytestReturnNotNoneWarning in review_formatter tests
**Category:** Test
**Severity:** Low
**First Seen:** 2025-12-15
**Status:** Open

**Symptom:**
Warning: "Test functions should return None, but returned <class 'str'>".

**Root Cause:**
Three test functions in test_review_formatter.py have `return` statements instead of assertions.

**Resolution:**
Change `return result` to `assert result is not None` or remove return statements.

**Files Affected:**
- tests/unit/generators/test_review_formatter.py

---

## Resolved Issues

(Move resolved issues here after verification)

---

## Issue Categories

| Category | Description |
|----------|-------------|
| Test | Unit/integration test failures or warnings |
| Build | Build system, dependencies, packaging |
| Runtime | Errors during tool execution |
| Integration | MCP protocol, tool communication issues |

## Severity Levels

| Severity | Description |
|----------|-------------|
| Low | Cosmetic, warnings, non-blocking |
| Medium | Functionality impacted but workaround exists |
| High | Critical functionality broken, no workaround |
