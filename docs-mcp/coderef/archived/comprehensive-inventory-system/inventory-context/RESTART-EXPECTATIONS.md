# Restart Expectations - /create-plan Fix Verification

## What We Fixed (Commit: 2cfa102)

### Problem
`/create-plan` failed with error:
```
Planning template not found: C:\Users\willh\.mcp-servers\docs-mcp\context\planning-template-for-ai.json
```

Template actually exists at: `C:\Users\willh\.mcp-servers\docs-mcp\coderef\context\planning-template-for-ai.json`

### Root Cause
Path constants missing `coderef/` directory prefix.

### Files Changed
1. **constants.py** - Fixed `PlanningPaths.TEMPLATE_AI_PATH` to include `coderef/context/`
2. **planning_generator.py** - Updated `context_dir` path construction
3. **tool_handlers.py** - Corrected error messages (2 locations)
4. **CLAUDE.md** - Updated documentation
5. **gather-context.md** - Enhanced interview instructions
6. **QUICK-START.md** - Added complete reference

### Commit Details
- Hash: `2cfa102`
- Branch: `main`
- Status: ✅ Committed and pushed to origin

---

## Expected Behavior After Restart

### Test Command
```bash
/create-plan comprehensive-inventory-system
```

### Expected Success Output
```json
{
  "plan_path": "coderef/working/comprehensive-inventory-system/plan.json",
  "feature_name": "comprehensive-inventory-system",
  "sections_completed": [
    "0_preparation",
    "1_executive_summary",
    "2_risk_assessment",
    "3_current_state_analysis",
    "4_key_features",
    "5_task_id_system",
    "6_implementation_phases",
    "7_testing_strategy",
    "8_success_criteria",
    "9_implementation_checklist"
  ],
  "has_context": false,
  "has_analysis": false,
  "status": "complete",
  "next_steps": [
    "Validate plan with /validate-plan",
    "Review plan score and refine until >= 90",
    "Generate review report with /generate-plan-review"
  ],
  "success": true
}
```

### Expected Plan Quality

#### ❌ OLD (Before Fix) - Skeleton with TODOs
```json
{
  "1_executive_summary": {
    "purpose": "Implement comprehensive-inventory-system feature",
    "value_proposition": "TODO: Define value proposition",
    "real_world_analogy": "TODO: Add real-world analogy",
    ...
  }
}
```

#### ✅ NEW (After Fix) - Complete Plan
```json
{
  "1_executive_summary": {
    "purpose": "Implement comprehensive inventory system with 8 category types",
    "value_proposition": "Automated project health analysis providing actionable insights for maintenance, refactoring, and documentation",
    "real_world_analogy": "Like a building inspector's comprehensive report - evaluates structure (files), utilities (dependencies), compliance (APIs), foundation (database), systems (config), documentation, safety (tests), and aesthetics (assets)",
    "use_case": "Developer runs /inventory → receives 8 category reports → identifies high-risk files → prioritizes refactoring → tracks health over time",
    "output": [
      "coderef/inventory/inventory_manifest.json",
      "coderef/inventory/project_inventory_report.md",
      "8 category-specific JSON files",
      "Unified health score (0-10)",
      "Actionable refactoring recommendations"
    ]
  }
}
```

### Key Differences
- **Before**: Generic placeholders, no specific content
- **After**: Feature-specific details, actionable information, real examples

---

## Verification Steps

### 1. Check Template Location (Pre-flight)
```bash
# Should exist and be readable
ls C:\Users\willh\.mcp-servers\docs-mcp\coderef\context\planning-template-for-ai.json
```

### 2. Run /create-plan
```bash
/create-plan comprehensive-inventory-system
```

### 3. Verify Success Indicators
- ✅ No "template not found" error
- ✅ Status: "complete" (not "partial")
- ✅ All 10 sections in `sections_completed` array
- ✅ `success: true`

### 4. Inspect Generated Plan
```bash
# Read the generated plan
cat C:\Users\willh\.mcp-servers\docs-mcp\coderef\working\comprehensive-inventory-system\plan.json
```

**Look for**:
- ❌ NO "TODO:" strings (indicates skeleton generation)
- ✅ Real feature descriptions
- ✅ Specific task IDs (e.g., "SETUP-001: Create inventory module structure")
- ✅ Detailed implementation phases
- ✅ Concrete success criteria

### 5. Validate Plan Quality
```bash
/validate-plan comprehensive-inventory-system
```

**Expected score**: 70-85 (initial generation)
- Plans generated without context.json or analysis typically score 70-80
- This is normal - refine based on validation feedback
- Target: 90+ after refinement

---

## Warnings Expected

### Missing Context Warning
```
⚠️ Warning: No context.json found
Best results require feature context from /gather-context
```

**Why**: We didn't run `/gather-context` to collect requirements
**Impact**: Plan will be based on template defaults + feature name inference
**Action**: Accept for now, can gather context later if needed

### Missing Analysis Warning
```
⚠️ Warning: No project analysis found
Best results require analysis from /analyze-for-planning
```

**Why**: We didn't run `/analyze-for-planning` to discover project structure
**Impact**: Section 0 (Preparation) will have generic/empty foundation docs list
**Action**: Accept for now, analysis can be run separately

---

## If It Still Fails

### Scenario 1: Same "template not found" error
**Diagnosis**: Server didn't reload updated code
**Fix**:
1. Verify git commit is on disk: `git log -1 --oneline`
2. Check file contents: `cat constants.py | grep TEMPLATE_AI_PATH`
3. Fully restart computer (as planned)
4. Retry

### Scenario 2: Template found but plan still has TODOs
**Diagnosis**: Meta-tool pattern fix from previous session didn't apply
**Fix**:
1. Check if `planning_generator.py` has meta-tool pattern code
2. May need to re-implement meta-tool pattern fix
3. Document what's actually in the generator

### Scenario 3: Different error
**Diagnosis**: New issue uncovered
**Fix**:
1. Read full error message
2. Check logs if available
3. Debug from error details

---

## Success Criteria Summary

| Check | Expected | Actual |
|-------|----------|--------|
| Template found | ✅ Yes | ___ |
| Plan generated | ✅ Complete | ___ |
| No TODO strings | ✅ None | ___ |
| Sections completed | ✅ 10/10 | ___ |
| Has specific details | ✅ Yes | ___ |
| Validation score | 70-85 | ___ |

---

## Next Steps After Success

1. **Validate the plan**
   ```bash
   /validate-plan comprehensive-inventory-system
   ```

2. **Review validation issues**
   - Identify critical/major/minor issues
   - Prioritize fixes

3. **Generate review report**
   ```bash
   /generate-plan-review comprehensive-inventory-system
   ```

4. **Refine plan** (iterative)
   - Fix critical issues
   - Fix major issues
   - Re-validate until score >= 90

5. **Get approval**
   - Present plan + review report
   - Discuss implementation approach
   - Proceed with Phase 0 integration (existing inventory → /analyze-for-planning)

---

## Context

**Feature**: comprehensive-inventory-system
**Goal**: Automated project health analysis with 8 inventory categories
**Priority**: High (inventory system proves valuable based on manual creation)
**Reference Docs**:
- `inventory-categories-log.md` - 8 categories + 6 phases
- `inventory_manifest.json` - Current manual inventory (95 files)
- `project_inventory_report.md` - Current health report (8.2/10)

**Strategic Value**:
- Automates manual inventory creation
- Expands from file-only to 8 categories
- Integrates with planning workflow
- Provides programmatic MCP tool access

---

**Generated**: 2025-10-14
**Commit**: 2cfa102
**Status**: Ready for restart verification
