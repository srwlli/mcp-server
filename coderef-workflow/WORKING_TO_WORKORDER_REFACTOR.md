# Refactor: coderef/working → coderef/workorder

**Workorder:** WO-WORKFLOW-REFACTOR-001
**Phase:** 3 - Comprehensive Search & 4 - Batch Rename
**Status:** In Progress

---

## Summary

This document lists all files that reference `coderef/working` and need to be updated to use `coderef/workorder` instead. The refactoring is a breaking change with no backward compatibility.

**Key Point:** No directory renaming needed. Only new files will go to `coderef/workorder/`. Existing files in `coderef/working/` remain as-is.

---

## Python Files with References (6 files)

### 1. tool_handlers.py
**Lines:** Multiple occurrences
**Pattern:** `coderef/working/{feature_name}`
**Example:** `Output: coderef/working/{feature_name}/plan.json`
**Change:** Update all paths to `coderef/workorder/{workorder_id}`

### 2. server.py
**Lines:** Multiple occurrences
**Pattern:** `coderef/working/`
**Change:** Update all tool descriptions and paths

### 3. generators/planning_generator.py
**Lines:** Multiple occurrences
**Pattern:** `coderef/working/`
**Change:** Update default path and documentation

### 4. generators/features_inventory_generator.py
**Lines:** Multiple occurrences
**Pattern:** `coderef/working/`
**Change:** Update inventory generation logic

### 5. plan_format_validator.py
**Lines:** Multiple occurrences
**Pattern:** `coderef/working/`
**Change:** Update validation paths

### 6. handler_helpers.py
**Lines:** Multiple occurrences
**Pattern:** `coderef/working/`
**Change:** Update helper functions and paths

---

## Slash Command Files (.md) with References (13 files)

### Planning Phase
1. **create-plan.md** - References to path structure and output locations
2. **create-workorder.md** - Orchestration command for creating workorders
3. **gather-context.md** - Context gathering with path references
4. **analyze-for-planning.md** - Analysis output paths
5. **generate-plan-review.md** - Review report generation paths

### Execution Phase
6. **update-deliverables.md** - Deliverables template path
7. **generate-deliverables.md** - Deliverables generation paths
8. **archive-feature.md** - Archival from `coderef/working/` to `coderef/archived/`

### Documentation
9. **generate-handoff-context.md** - Handoff context from workorder paths
10. **update-changelog.md** (if present) - Changelog with workorder context
11. **generate-plan-review.md** - Review generation

### Inventory & Status
12. **features-inventory.md** - Inventory listing of active features
13. **audit-plans.md** - Plan auditing with path discovery

### Utility
14. **fix.md** - Fix command with path references
15. **stub.md** - Stub command with path references

---

## Data Files (if present)

### coderef/working/ directory structure
- Feature directories (e.g., `coderef/working/fix-workflow-bugs-and-rename/`)
- Associated JSON files:
  - `context.json`
  - `analysis.json`
  - `plan.json`
  - `communication.json`
  - `DELIVERABLES.md`
  - `execution-log.json`

**Note:** These should NOT be moved. They remain in `coderef/working/`. Only NEW features will use `coderef/workorder/` with workorder IDs.

---

## Documentation Files (outside coderef-workflow)

### Global files in ~/.mcp-servers/
1. **COMPLETE_COMMAND_AUDIT.md** - References to `coderef/working/` paths
2. **command-map-latest.md** - May reference paths
3. **SLASH_COMMAND_MAPPING.md** - May reference paths

---

## Refactoring Plan

### Phase 4: Batch Rename Implementation

#### REFACTOR-104: Update all .py files (6 files)
- [ ] tool_handlers.py - Update all path references
- [ ] server.py - Update tool descriptions
- [ ] generators/planning_generator.py - Update default paths
- [ ] generators/features_inventory_generator.py - Update inventory logic
- [ ] plan_format_validator.py - Update validation paths
- [ ] handler_helpers.py - Update helper functions

#### REFACTOR-105: Update all .md slash commands (13 files)
- [ ] create-plan.md
- [ ] create-workorder.md
- [ ] gather-context.md
- [ ] analyze-for-planning.md
- [ ] generate-plan-review.md
- [ ] update-deliverables.md
- [ ] generate-deliverables.md
- [ ] archive-feature.md
- [ ] generate-handoff-context.md
- [ ] features-inventory.md
- [ ] audit-plans.md
- [ ] fix.md
- [ ] stub.md

#### REFACTOR-106: Update documentation (outside coderef-workflow)
- [ ] COMPLETE_COMMAND_AUDIT.md - Update path references
- [ ] README.md (if applicable) - Update paths
- [ ] CLAUDE.md (if applicable) - Update paths

---

## Implementation Strategy

### Approach: Search & Replace + Context

1. **For Python files:**
   - Use global find/replace for `coderef/working` → `coderef/workorder`
   - But preserve context - only replace path strings, not variable names
   - Update comments and docstrings

2. **For Markdown files:**
   - Update user-facing documentation
   - Update example code blocks
   - Update command descriptions

3. **Important Notes:**
   - Do NOT rename the physical `coderef/working/` directory
   - Do NOT move existing feature directories
   - New features created with `/create-workorder` will use `coderef/workorder/{WO-ID}`
   - Existing features stay in `coderef/working/`

---

## Testing After Refactor

### BUGFIX-003: Test generate_deliverables_template
- [ ] Create new workorder with workorder ID
- [ ] Verify plan.json created in correct location
- [ ] Verify no crashes with deliverables template

### BUGFIX-004: Test plan creation
- [ ] Create plan and verify status is "planning"
- [ ] Verify workorder_id stored in META_DOCUMENTATION
- [ ] Test both new and existing feature paths

---

## Success Criteria

✓ All 6 Python files updated
✓ All 13 slash command files updated
✓ All external documentation updated
✓ No hardcoded paths in code
✓ Tests pass with new paths
✓ Workorder IDs properly tracked

---

## Files Summary

| Category | Count | Files |
|----------|-------|-------|
| Python files | 6 | tool_handlers, server, planning_generator, features_inventory, validator, helpers |
| Slash commands | 13 | create-plan, create-workorder, gather-context, analyze-for-planning, etc. |
| Documentation | 3+ | COMPLETE_COMMAND_AUDIT.md, README.md, CLAUDE.md |
| **Total** | **22+** | All require updates |

---

**Last Updated:** 2025-12-25
**Created By:** Claude Code (REFACTOR-103 Task)
**Status:** Ready for Phase 4 batch refactor

