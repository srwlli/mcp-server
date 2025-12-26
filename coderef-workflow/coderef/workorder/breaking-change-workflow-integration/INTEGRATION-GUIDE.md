# Breaking Change Detection - Workflow Integration Guide

**Status:** Planning & Documentation Complete
**Feature:** CR-001 (Breaking Change Detector)
**Workorder ID:** WO-BREAKING-CHANGE-INTEGRATION-001
**Created:** 2025-12-25

---

## Quick Overview

The Breaking Change Detector (CR-001) needs to be integrated into the coderef-workflow orchestration process at **5 key stages**:

1. **Planning Phase** - Risk assessment before implementation
2. **Agent Handoff** - Provide breaking change context to agents
3. **Implementation Gate** - Verify no new breaking changes
4. **Test Strategy** - Select tests based on affected modules
5. **Documentation** - Generate migration guides

---

## Current State

✅ **READY FOR INTEGRATION:**
- `mcp__coderef_breaking__detect` MCP tool is exposed and working
- Breaking change detection is production-ready with 29 tests
- All detection, confidence scoring, and migration patterns are implemented

❌ **NEEDS INTEGRATION:**
- Workflow templates (plan.json, communication.json) don't include breaking change tasks
- Agent handoff (claude.md) doesn't mention breaking changes
- No automated hooks to check breaking changes during workflows
- No migration guide generation
- CI/CD pipelines don't gate on breaking changes

---

## Integration Implementation

### Step 1: Add to Planning (Phase 0)

**What:** Detect existing breaking changes before starting implementation

**Tool Call:**
```
mcp__coderef_breaking__detect(baseRef='main', headRef='current-branch')
```

**Output:** Risk assessment added to `plan.json` risks section

**Impact:** Agents know what breaking changes already exist before they start coding

---

### Step 2: Add to Agent Handoff (claude.md)

**What:** Include breaking change context in agent briefing

**Additions to claude.md:**
```markdown
## Breaking Changes (CR-001)

### Current Breaking Changes
[Auto-populated from risk assessment]

### Migration Patterns Available
- **Wrap**: Create new version alongside old (safest)
- **Rename**: Rename + provide adapter (for few call sites)
- **Adapter**: Create wrapper for compatibility (flexible)
- **Default Params**: Add optional parameters (for parameter addition)
- **Options Object**: Convert params to options (for complex signatures)

### Your Responsibility
After implementing your feature:
1. Run: `coderef breaking main --format table`
2. Review confidence scores (>85% = high certainty)
3. Implement suggested migration patterns
4. Verify all impacted call sites can be updated
```

**Impact:** Agents understand what breaking changes are and how to handle them

---

### Step 3: Add Verification Gate (Phase 3)

**What:** Validate that agent didn't introduce new breaking changes

**Tool Call (runs after agent completes work):**
```
newReport = mcp__coderef_breaking__detect(baseRef='main', useWorktree=true)
newBreakingChanges = newReport.summary.breakingCount - baseline.summary.breakingCount

if (newBreakingChanges > 0) {
  status = "BREAKING_CHANGES_DETECTED"
  action = "REQUIRE_MIGRATION_PATTERNS_OR_ROLLBACK"
}
```

**Impact:** System automatically detects if agent introduced breaking changes

---

### Step 4: Intelligent Test Selection

**What:** Use breaking change impact to determine which tests to run

**Logic:**
```typescript
const report = mcp__coderef_breaking__detect(baseRef='main', useWorktree=true);

// Extract affected modules
const affectedModules = new Set(
  report.changes.map(c => c.element.file.split('/')[0])
);

// Select tests only for affected modules
const testsToRun = allTests.filter(t =>
  affectedModules.has(extractModule(t.file))
);
```

**Impact:** Faster feedback loop - only run relevant tests

---

### Step 5: Documentation Generation

**What:** Automatically generate migration guides from breaking change reports

**Output:** Markdown migration guide with:
- List of breaking changes
- Confidence scores for each
- Affected call sites
- Suggested fixes
- Before/after code examples

**Impact:** Users get clear migration path when breaking changes occur

---

## Concrete Implementation Tasks

### High Priority (Do First)

1. **Update plan.json template** (2 hours)
   - Add PREP-BREAKING-001: Analyze existing breaking changes
   - Add VERIFY-BREAKING-001: Detect new breaking changes
   - Add gates that fail if new breaking changes > threshold

2. **Create workflow hooks** (4 hours)
   - Pre-implementation: Baseline breaking changes
   - Post-implementation: Detect new breaking changes
   - Fail gate if new breaking changes introduced

3. **Update claude.md generation** (2 hours)
   - Auto-include breaking change context in agent handoff
   - List known breaking changes
   - Provide migration pattern guidance

### Medium Priority (Do Next)

4. **Test selection strategy** (3 hours)
   - Implement breaking-change-aware test selector
   - Use impacted modules to filter test suite

5. **Migration guide generation** (3 hours)
   - Create BreakingChangeDocumentationGenerator
   - Generate markdown with code examples

6. **CI/CD integration** (2 hours)
   - Add GitHub Actions workflow for breaking change checks
   - Gate merges on breaking changes

### Lower Priority (Future Enhancements)

7. **Auto-apply migration patterns** (5 hours)
   - Agent can request automatic wrap/rename/adapter application

8. **Compatibility layers** (5 hours)
   - Auto-generate compatibility shims for breaking changes

---

## File Changes Required

### 1. Templates (packages/generators)
```
- src/templates/plan.json
  + Add PREP-BREAKING-001 and VERIFY-BREAKING-001 tasks

- src/templates/communication.json
  + Add breaking-change-validation shared gate
```

### 2. Workflow Hooks (packages/workflow - NEW)
```
- src/hooks/breaking-change-baseline.ts
  + Record breaking changes before implementation

- src/hooks/breaking-change-verification.ts
  + Detect new breaking changes after implementation

- src/hooks/breaking-change-documentation.ts
  + Generate migration guides
```

### 3. Context Generation
```
- src/context/handoff-generator.ts
  + Include breaking change analysis in claude.md
```

### 4. Test Strategy
```
- src/test-strategy/breaking-change-aware-selector.ts
  + Use breaking changes to select affected tests
```

### 5. Documentation
```
- src/documentation/migration-guide-generator.ts
  + Generate markdown migration guides from reports
```

### 6. CI/CD
```
- .github/workflows/breaking-change-check.yml
  + Gate on breaking changes before merge
```

---

## Usage Examples

### For Feature Teams

```bash
# Before starting implementation
coderef breaking main

# After implementation, before merging
coderef breaking main --format table

# If breaking changes detected, review migration patterns
coderef breaking main --verbose
```

### For CI/CD

```bash
#!/bin/bash
# .github/workflows/breaking-change-check.yml

- name: Check for breaking changes
  run: |
    REPORT=$(npm run coderef breaking main -- --format json)
    BREAKING_COUNT=$(echo $REPORT | jq '.summary.breakingCount')

    if [ $BREAKING_COUNT -gt 0 ]; then
      echo "❌ Breaking changes detected - merge blocked"
      echo $REPORT | jq '.'
      exit 1
    fi
```

### For Agents

When agent receives task:
```markdown
## Context: Breaking Changes

### Current Breaking Changes (3)
1. authenticate() - callback removed (HIGH severity, 23 call sites)
2. processPayment() - required param added (HIGH severity, 5 call sites)
3. validateUser() - params reordered (MEDIUM severity, 3 call sites)

### What You Must Do
- Implement migration patterns for all changes
- Verify all affected call sites are updated
- Ensure confidence scores > 85%

### Available Tools
- `mcp__coderef_breaking__detect` - Run this after implementation
- Suggested patterns provided in migration hints
```

---

## Success Metrics

**Integration is complete when:**
- ✅ All feature plans include breaking change detection tasks
- ✅ Agent handoff contexts include breaking change guidance
- ✅ Verification gates prevent new breaking changes
- ✅ Test selection is optimized for affected modules
- ✅ Migration guides are auto-generated
- ✅ CI/CD pipelines gate on breaking changes
- ✅ 100% of breaking changes have migration patterns
- ✅ Zero production incidents from breaking changes

---

## Timeline

| Phase | Task | Time | Status |
|-------|------|------|--------|
| 1 | Document integration (this file) | DONE | ✅ |
| 2 | Update templates | 2 hrs | ⏳ |
| 2 | Implement workflow hooks | 4 hrs | ⏳ |
| 2 | Update agent handoff | 2 hrs | ⏳ |
| 3 | Test selection strategy | 3 hrs | ⏳ |
| 3 | Migration guide generation | 3 hrs | ⏳ |
| 3 | CI/CD integration | 2 hrs | ⏳ |
| **Total** | | **16 hrs** | |

---

## Related Documentation

- **CR-001 Implementation:** `packages/core/src/context/breaking-change-detector.ts`
- **CLI Documentation:** `packages/cli/src/commands/breaking.ts`
- **MCP Tool:** `packages/coderef-rag-mcp/src/tools/breaking-change-handler.ts`
- **Context Reference:** `CLAUDE.md` - Breaking Change Detection section
- **Capabilities Reference:** `current-capabilities.json`

---

## Questions & Decisions

### Q: Should we block merges if breaking changes exist?
**A:** Yes for breaking changes to public APIs/exports, no for internal refactoring. This should be configurable per module.

### Q: How do we handle unavoidable breaking changes?
**A:** They must have:
1. Clear migration patterns (wrap, adapter, etc.)
2. High confidence scores (>85%)
3. Migration guide in changelog
4. Deprecation warning in release notes

### Q: What if there are too many breaking changes?
**A:** Split feature into smaller pieces that don't break public APIs, or plan a major version bump with comprehensive migration guide.

### Q: Can agents auto-apply migration patterns?
**A:** Not yet, but it's in the roadmap. For now, agents implement patterns based on suggestions.

---

## Next Actions

1. **Review this guide** with team to validate approach
2. **Prioritize tasks** in the task breakdown
3. **Create workorders** for each high-priority task
4. **Assign developers** to implementation tasks
5. **Execute phase by phase** - templates first, then hooks, then generators

**Estimated completion:** 2-3 weeks for full integration
