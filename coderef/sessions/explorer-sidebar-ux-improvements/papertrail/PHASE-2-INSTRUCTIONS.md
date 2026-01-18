# Phase 2 Validation Instructions - papertrail Agent

**Workorder:** WO-EXPLORER-SIDEBAR-UX-001-PAPERTRAIL-PHASE2
**Parent Session:** WO-EXPLORER-SIDEBAR-UX-001
**Phase:** Phase 2 - Navigation Enhancements
**Agent:** papertrail
**Created:** 2026-01-17
**Status:** Ready to execute (wait for coderef-docs completion)

---

## Context

This is the **second validation cycle** for the Explorer Sidebar UX improvements session.

**Phase 1 Validation Results:**
- Initial: 0% pass rate (3 BLOCKING ISSUES)
- After remediation: 100% pass rate ✅

**Phase 2 Documentation Deliverables (from coderef-docs):**

**New Resource Sheets:**
1. QuickFileSearch-RESOURCE-SHEET.md (~400 lines)
2. TreeActionsToolbar-RESOURCE-SHEET.md (~300 lines)
3. fuzzyMatch-Utility-RESOURCE-SHEET.md (~250 lines)

**Updated Resource Sheets:**
1. CodeRef-Explorer-Widget-RESOURCE-SHEET.md (v1.0.0 → v1.1.0)
2. FileTree-RESOURCE-SHEET.md (v1.0.0 → v1.1.0)
3. ResizableSidebar-RESOURCE-SHEET.md (v1.0.0 → v1.1.0)

**Updated System Docs:**
1. explorer/CLAUDE.md (updated with Phase 2 features)
2. resource-sheet-index.md (13 total sheets, up from 10)

---

## Your Mission

Validate all Phase 2 documentation deliverables against UDS v1.0 and RSMS v2.0 standards.

**Target:** 100% validation pass rate (8/8 documents)
**Standard:** No CRITICAL or MAJOR errors

---

## Tasks

### Task 1: Validate QuickFileSearch-RESOURCE-SHEET.md

**File:** `C:\Users\willh\Desktop\coderef-dashboard\coderef\resources-sheets\components\QuickFileSearch-RESOURCE-SHEET.md`

**Validation Tool:** `mcp__papertrail__validate_resource_sheet`

**Check:**
- ✅ RSMS v2.0 frontmatter structure (snake_case fields)
- ✅ Required fields present: subject, parent_project, category, version
- ✅ Filename ends with `-RESOURCE-SHEET.md`
- ✅ Subject matches filename pattern
- ✅ Recommended sections present (Executive Summary, Architecture, API, etc.)
- ✅ workorder_id and feature_id fields populated
- ✅ phase field = "phase_2"

**Success Criteria:** Score ≥ 80/100, no CRITICAL errors

---

### Task 2: Validate TreeActionsToolbar-RESOURCE-SHEET.md

**File:** `C:\Users\willh\Desktop\coderef-dashboard\coderef\resources-sheets\components\TreeActionsToolbar-RESOURCE-SHEET.md`

**Validation Tool:** `mcp__papertrail__validate_resource_sheet`

**Check:**
- ✅ RSMS v2.0 compliance (same as Task 1)
- ✅ Component category correct
- ✅ Dependencies listed accurately
- ✅ Related sheets referenced

**Success Criteria:** Score ≥ 80/100, no CRITICAL errors

---

### Task 3: Validate fuzzyMatch-Utility-RESOURCE-SHEET.md

**File:** `C:\Users\willh\Desktop\coderef-dashboard\coderef\resources-sheets\utilities\fuzzyMatch-Utility-RESOURCE-SHEET.md`

**Validation Tool:** `mcp__papertrail__validate_resource_sheet`

**Check:**
- ✅ RSMS v2.0 compliance
- ✅ Category = "utility" (not "component")
- ✅ File in correct subdirectory (`utilities/`)
- ✅ API documentation complete

**Success Criteria:** Score ≥ 80/100, no CRITICAL errors

---

### Task 4: Re-validate CodeRef-Explorer-Widget-RESOURCE-SHEET.md

**File:** `C:\Users\willh\Desktop\coderef-dashboard\coderef\resources-sheets\components\CodeRef-Explorer-Widget-RESOURCE-SHEET.md`

**Validation Tool:** `mcp__papertrail__validate_resource_sheet`

**Check:**
- ✅ Version bumped to v1.1.0
- ✅ Updated date changed to 2026-01-17
- ✅ Phase 2 features documented
- ✅ New dependencies added (QuickFileSearch, TreeActionsToolbar)
- ✅ Previous Phase 1 score: 56/100 → Target: 80+/100

**Success Criteria:** Score improvement from Phase 1, ≥ 80/100

---

### Task 5: Re-validate FileTree-RESOURCE-SHEET.md

**File:** `C:\Users\willh\Desktop\coderef-dashboard\coderef\resources-sheets\components\FileTree-RESOURCE-SHEET.md`

**Validation Tool:** `mcp__papertrail__validate_resource_sheet`

**Check:**
- ✅ Version bumped to v1.1.0
- ✅ searchQuery prop documented
- ✅ Search filtering logic explained
- ✅ Integration with QuickFileSearch documented

**Success Criteria:** Score ≥ 80/100, no CRITICAL errors

---

### Task 6: Re-validate ResizableSidebar-RESOURCE-SHEET.md

**File:** `C:\Users\willh\Desktop\coderef-dashboard\coderef\resources-sheets\components\ResizableSidebar-RESOURCE-SHEET.md`

**Validation Tool:** `mcp__papertrail__validate_resource_sheet`

**Check:**
- ✅ Version bumped to v1.1.0
- ✅ Collapse toggle feature documented
- ✅ Previous Phase 1 score: 54/100 → Target: 80+/100

**Success Criteria:** Score improvement from Phase 1, ≥ 80/100

---

### Task 7: Re-validate explorer/CLAUDE.md

**File:** `C:\Users\willh\Desktop\coderef-dashboard\packages\dashboard\src\app\explorer\CLAUDE.md`

**Validation Tool:** `mcp__papertrail__validate_document` (UDS validation)

**Check:**
- ✅ YAML frontmatter still present (Phase 1 fix)
- ✅ Updated date changed to 2026-01-17
- ✅ Phase 2 components documented
- ✅ Keyboard shortcuts section added
- ✅ No broken links

**Success Criteria:** Score ≥ 80/100, no CRITICAL errors

---

### Task 8: Validate resource-sheet-index.md

**File:** `C:\Users\willh\Desktop\coderef-dashboard\packages\dashboard\src\app\explorer\resource-sheet-index.md`

**Manual Check (no specific tool):**

**Check:**
- ✅ Total count updated to 13 sheets
- ✅ New entries added (QuickFileSearch, TreeActionsToolbar, fuzzyMatch)
- ✅ Summary table accurate
- ✅ Recent Updates section includes Phase 2 entry
- ✅ Last Updated date = 2026-01-17
- ✅ All links valid

**Success Criteria:** No errors, all content accurate

---

### Task 9: Generate Phase 2 Validation Report

**File:** `outputs/papertrail-phase2-validation-report.json`

**Report Structure:**
```json
{
  "workorder_id": "WO-EXPLORER-SIDEBAR-UX-001-PAPERTRAIL-PHASE2",
  "parent_session": "WO-EXPLORER-SIDEBAR-UX-001",
  "validation_date": "2026-01-17",
  "validator": "papertrail",
  "phase": "phase_2",

  "summary": {
    "total_documents": 8,
    "new_documents": 3,
    "updated_documents": 5,
    "passed": 0,
    "failed": 0,
    "average_score": 0,
    "critical_errors": 0,
    "major_errors": 0,
    "warnings": 0
  },

  "phase_1_comparison": {
    "phase_1_pass_rate": "100% (after remediation)",
    "phase_2_pass_rate": "TBD",
    "quality_trend": "TBD"
  },

  "documents": [
    {
      "file": "QuickFileSearch-RESOURCE-SHEET.md",
      "type": "resource_sheet",
      "validation_standard": "RSMS v2.0",
      "score": 0,
      "status": "pass|fail",
      "errors": [],
      "warnings": []
    },
    // ... remaining docs
  ],

  "recommendations": [],

  "phase_gate_status": {
    "all_tasks_complete": true,
    "all_validations_pass": false,
    "no_critical_errors": false,
    "validation_report_generated": true,
    "recommendations_provided": true,
    "overall_status": "PENDING|APPROVED|BLOCKED"
  },

  "next_steps": []
}
```

---

## Execution Steps

1. **WAIT for coderef-docs agent to complete** all Phase 2 documentation tasks
2. **Read coderef-docs Phase 2 output** to identify all files to validate
3. **Validate new resource sheets** (Tasks 1-3)
4. **Re-validate updated resource sheets** (Tasks 4-6)
5. **Re-validate system docs** (Tasks 7-8)
6. **Generate validation report** (Task 9)
7. **Update communication.json:**
   - Add all validation results
   - Mark each task status='complete'
   - Add validation metrics (pass/fail counts, average score)
8. **Create output summary:** `outputs/papertrail-phase2-output.md`
9. **Mark status='complete'** with timestamp

---

## Success Criteria

- ✅ All 8 documents validated
- ✅ 100% pass rate (8/8 passing)
- ✅ Average score ≥ 80/100
- ✅ 0 CRITICAL errors
- ✅ 0 MAJOR errors
- ✅ Validation report generated
- ✅ Phase 1 vs Phase 2 comparison included

---

## Phase Gate Contribution

Your completion of validation is **required** for Phase 2 gate approval. The orchestrator will not approve Phase 2 until:
- All documents validated
- 100% pass rate achieved
- No CRITICAL/MAJOR errors
- Validation report complete

---

## Special Notes

**Phase 1 Lessons Applied:**
- Check for YAML frontmatter in all docs (prevent UDS violations)
- Validate file naming conventions early
- Ensure version numbers bumped correctly
- Verify workorder_id and feature_id fields populated

**Expected Timeline:**
- coderef-docs completion: ~1-2 hours
- Your validation work: ~30-45 minutes
- Total Phase 2 validation: <1 hour

---

**Ready to execute?** Monitor coderef-docs agent progress and execute validation when they complete!
