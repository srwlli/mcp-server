# coderef-docs Direct Validation Integration - START HERE

**Workorder:** WO-CODEREF-DOCS-DIRECT-VALIDATION-001
**Estimated Effort:** 3-4 hours
**Status:** Ready to start

---

## Quick Summary

**What:** Add direct validation integration to coderef-docs that writes validation metadata to markdown frontmatter `_uds` sections.

**Why:** User decision - downstream tools need machine-readable validation metadata, AND users need transparency through instruction-based validation. Both patterns should coexist.

**Key Constraint:** DO NOT break existing instruction-based validation (WO-UDS-COMPLIANCE-CODEREF-DOCS-001 complete, 12 tests passing). This is additive, not replacement.

---

## What You're Building

### Before (Current State - Instruction-Based Only)
```markdown
---
agent: Claude Code
date: 2026-01-10
---

# README

[Content...]

VALIDATION (WO-UDS-COMPLIANCE-CODEREF-DOCS-001):
```python
from papertrail.validators.foundation import FoundationDocValidator
validator = FoundationDocValidator()
result = validator.validate_file(Path('README.md'))
```
```

### After (Both Patterns Coexist)
```markdown
---
agent: Claude Code
date: 2026-01-10
_uds:
  validation_score: 95
  validation_errors: []
  validation_warnings: ["Missing API examples section"]
  validated_at: 2026-01-10T14:30:00Z
  validator: FoundationDocValidator
---

# README

[Content...]

VALIDATION (WO-UDS-COMPLIANCE-CODEREF-DOCS-001):
```python
from papertrail.validators.foundation import FoundationDocValidator
validator = FoundationDocValidator()
result = validator.validate_file(Path('README.md'))
```
```

**Notice:** Both patterns run. Instruction-based provides user transparency, direct integration provides machine-readable metadata.

---

## 8-Step Implementation Plan

### Step 1: Understand Current State (30 min)
- Read `coderef/workorder/uds-compliance-coderef-docs/COMPLETION-SUMMARY.md`
- Review `tool_handlers.py` lines 346-366 (foundation) and 799-821 (standards)
- Review existing tests: `tests/test_validator_integration.py`, `tests/test_integration_e2e.py`
- Confirm: 12/12 tests passing, 72% coverage

### Step 2: Design Frontmatter Structure (30 min)
**Frontmatter `_uds` Section:**
```yaml
_uds:
  validation_score: 95              # integer 0-100
  validation_errors: []             # array of error objects
  validation_warnings: ["..."]      # array of warning strings
  validated_at: 2026-01-10T14:30:00Z  # ISO 8601 timestamp
  validator: FoundationDocValidator # string (class name)
```

### Step 3: Create Validation Helper (1 hour)
**File:** `utils/validation_helpers.py`
**Function:** `write_validation_metadata_to_frontmatter(file_path: Path, validation_result: ValidationResult)`

**Implementation:**
1. Read file and extract frontmatter
2. Add `_uds` section with validation metadata
3. Write updated frontmatter back to file
4. Handle edge cases: missing frontmatter, invalid YAML, write errors

**Tests:** Unit tests for helper function

### Step 4: Integrate with Foundation Docs (1 hour)
**File:** `tool_handlers.py` (handle_generate_individual_doc)
**Templates:** readme, architecture, api, schema, components

**After saving file, add:**
```python
from papertrail.validators.foundation import FoundationDocValidator
from utils.validation_helpers import write_validation_metadata_to_frontmatter

validator = FoundationDocValidator()
result = validator.validate_file(output_path)
write_validation_metadata_to_frontmatter(output_path, result)
logger.info(f'Validation score: {result.score}/100')

# Existing instruction-based output continues unchanged
```

### Step 5: Integrate with Standards Docs (45 min)
**File:** `tool_handlers.py` (handle_establish_standards)
**Standards:** ui-patterns, behavior-patterns, ux-patterns

**After saving files, add:**
```python
from papertrail.validators.standards import StandardsDocValidator
from utils.validation_helpers import write_validation_metadata_to_frontmatter

validator = StandardsDocValidator()
for file_path in generated_files:
    result = validator.validate_file(file_path)
    write_validation_metadata_to_frontmatter(file_path, result)
    logger.info(f'{file_path}: Score {result.score}/100')

# Existing instruction-based output continues unchanged
```

### Step 6: Add Tests (45 min)
**File:** `tests/test_direct_validation.py` (CREATE NEW)

**4 Test Cases:**
1. `test_foundation_doc_has_validation_metadata_in_frontmatter` - Verify _uds in README
2. `test_standards_doc_has_validation_metadata_in_frontmatter` - Verify _uds in all 3 standards
3. `test_instruction_based_validation_still_outputs` - Verify instruction code still appears
4. `test_both_patterns_coexist` - Verify both patterns run without conflicts

**Regression Check:** Run existing 12 tests, ensure all pass

**Expected:** 16/16 tests passing (12 existing + 4 new)

### Step 7: Update Documentation (30 min)
**Files to Update:**
- `CLAUDE.md` → v3.7.0 (add direct validation section)
- `README.md` → update validation section (explain both patterns)
- `COMPLETION-SUMMARY.md` → create for this workorder

**Document:**
- Why both patterns exist (user transparency + machine metadata)
- When each pattern runs (both run for all docs)
- Frontmatter structure
- No breaking changes

### Step 8: Verify and Complete (30 min)
**Verification:**
1. Run `pytest tests/ -v` (expect 16/16 passing)
2. Manually generate README, inspect frontmatter (_uds present?)
3. Manually generate standards, inspect all 3 files (_uds present?)
4. Verify tool output still shows instruction-based validation code
5. Confirm no breaking changes

**Complete:**
- Update `communication.json` status to 'complete'
- Create implementation report
- Notify orchestrator

---

## Success Criteria

✅ Frontmatter `_uds` metadata appears in all generated docs (8 total: 5 foundation + 3 standards)
✅ Instruction-based validation still outputs (no breaking changes)
✅ Both patterns run successfully without conflicts
✅ 16/16 tests passing (12 existing + 4 new)
✅ No regression in existing functionality
✅ Documentation explains both patterns clearly

---

## Reference Files

**Read These First:**
1. `context.json` - Requirements and constraints
2. `instructions.json` - Detailed task breakdown
3. `coderef/workorder/uds-compliance-coderef-docs/COMPLETION-SUMMARY.md` - Existing implementation

**Validators to Use:**
- `from papertrail.validators.foundation import FoundationDocValidator`
- `from papertrail.validators.standards import StandardsDocValidator`

**Existing Code Locations:**
- Foundation docs: `tool_handlers.py` lines 346-366
- Standards docs: `tool_handlers.py` lines 799-821
- Existing tests: `tests/test_validator_integration.py`, `tests/test_integration_e2e.py`

---

## Key Reminders

⚠️ **DO NOT break existing instruction-based validation** - keep all existing code that outputs validation instructions
⚠️ **Both patterns must run** - direct integration is additive, not replacement
⚠️ **Test after each step** - run tests frequently to catch regressions early
⚠️ **Handle edge cases** - missing frontmatter, invalid YAML, file write errors

---

**Ready to start?** Begin with Step 1: Read the existing implementation to understand what you're building on top of.

**Estimated Time:** 3-4 hours total

**Session Location:** `C:\Users\willh\.mcp-servers\coderef\sessions\coderef-docs-direct-validation\`
