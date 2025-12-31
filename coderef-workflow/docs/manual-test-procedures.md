# Manual Test Procedures

## WO-BUG-FIXES-TESTING-001

### Manual Test 1: Large Codebase (>50k LOC)

**Setup:**
1. Create project with >50,000 lines of code
2. Run /create-workorder workflow

**Expected Result:**
- Step 3 completes without timeout
- Foundation docs generated successfully
- Progress markers [1/5], [2/5], etc. displayed

**Verification:**
- Check foundation docs exist in coderef/foundation-docs/
- Verify no timeout errors in output

---

### Manual Test 2: Non-Git Repository Workflow

**Setup:**
1. Create project directory without .git folder
2. Run /create-workorder workflow

**Expected Result:**
- Step 1 detects missing git
- User prompted to continue or abort
- Step 11 skips gracefully if continued

**Verification:**
- Check for git detection warning
- Verify Step 11 shows "Git unavailable - skipped"

---

### Manual Test 3: Validation Loop with Bad Context

**Setup:**
1. Create context.json with empty required fields
2. Run plan validation

**Expected Result:**
- Validation fails with score <90
- After 3 iterations, user gets choice (save/restart/abort)

**Verification:**
- Check validation shows specific missing fields
- Verify user choice prompt after 3 failures
