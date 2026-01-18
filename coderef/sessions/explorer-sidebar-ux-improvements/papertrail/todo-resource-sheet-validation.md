# Resource Sheet Validation - Todo List

**Date:** 2026-01-17
**Session:** WO-EXPLORER-SIDEBAR-UX-001
**Agent:** papertrail
**Issue:** RSMS v2.0 Schema Mismatch

---

## Invalid Fields Table

| Field Name | Present in QuickFileSearch | Allowed by RSMS v2.0 Schema | Error Type | Why Invalid |
|------------|---------------------------|----------------------------|------------|-------------|
| `agent` | ✅ Yes | ✅ Yes (line 10-16) | - | Valid |
| `date` | ✅ Yes | ✅ Yes (line 17-22) | - | Valid |
| `task` | ✅ Yes | ✅ Yes (line 29-34) | - | Valid |
| `subject` | ✅ Yes | ✅ Yes (line 35-41) | - | Valid |
| `parent_project` | ✅ Yes | ✅ Yes (line 42-48) | - | Valid |
| `category` | ✅ Yes | ✅ Yes (line 49-54) | - | Valid |
| `version` | ✅ Yes | ✅ Yes (line 55-60) | - | Valid |
| `related_files` | ✅ Yes | ✅ Yes (line 61-72) | - | Valid |
| `created` | ✅ Yes | ❌ No | MAJOR | Additional property not allowed |
| `updated` | ✅ Yes | ❌ No | MAJOR | Additional property not allowed |
| `status` | ✅ Yes (value: "active") | ⚠️ Yes, but wrong value (line 110-115) | MAJOR | Must be DRAFT/REVIEW/APPROVED/ARCHIVED |
| `complexity` | ✅ Yes | ❌ No | MAJOR | Additional property not allowed |
| `loc` | ✅ Yes | ❌ No | MAJOR | Additional property not allowed |
| `dependencies` | ✅ Yes | ❌ No | MAJOR | Additional property not allowed |
| `related_sheets` | ✅ Yes | ❌ No (has `related_docs`) | MAJOR | Additional property not allowed (similar to `related_docs` but different name) |
| `workorder_id` | ✅ Yes | ❌ No (has `workorder`) | MAJOR | Additional property not allowed (schema has `workorder` not `workorder_id`) |
| `feature_id` | ✅ Yes | ❌ No | MAJOR | Additional property not allowed |
| `phase` | ✅ Yes | ❌ No | MAJOR | Additional property not allowed |

---

## Summary

**Valid Fields:** 8
**Invalid Fields:** 10
- 9 additional properties not in schema
- 1 field with wrong enum value (`status: active` instead of DRAFT/REVIEW/APPROVED/ARCHIVED)

**Schema Constraint:** `"additionalProperties": false` (line 117) - rejects ANY field not explicitly defined

---

## Impact

**Documents Affected:** 7 resource sheets
- QuickFileSearch-RESOURCE-SHEET.md (Score: 16/100)
- TreeActionsToolbar-RESOURCE-SHEET.md (Score: 16/100)
- fuzzyMatch-Utility-RESOURCE-SHEET.md (Score: 16/100)
- CodeRef-Explorer-Widget-RESOURCE-SHEET.md (Score: 36/100)
- FileTree-RESOURCE-SHEET.md (Score: 36/100)
- ResizableSidebar-RESOURCE-SHEET.md (Score: 36/100)
- Plus 7 more existing sheets (not yet validated)

**Total Errors:** 21+ MAJOR errors across 6 validated sheets

**Pass Rate:** 0% (0/8 documents pass Phase 2 validation)

---

## Solution Options

### Option A: Allow Additional Properties
**Change:** Set `additionalProperties: true` in schema
**Effort:** 5 minutes
**Pros:** Quick fix, all sheets pass immediately
**Cons:** Loses schema strictness, any typo becomes valid

### Option B: Remove Additional Fields
**Change:** Remove all 10 invalid fields from all resource sheets
**Effort:** 2-3 hours (13+ sheets to update)
**Pros:** Perfect schema compliance
**Cons:** **BREAKS WORKORDER TRACEABILITY**, loses lifecycle tracking

### Option C: Extended Schema Variant (RECOMMENDED)
**Change:** Create `rsms-workorder-v2.0.json` extending base schema
**Effort:** 2-3 hours (new schema + validator + docs)
**Pros:** Preserves traceability, strict validation, supports both use cases
**Cons:** Two schemas to maintain

---

## Recommended Fix: Option C Implementation

### Step 1: Create Extended Schema (30 min)
**File:** `schemas/documentation/rsms-workorder-v2.0.json`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Resource Sheet Workorder Extension (RSMS Workorder v2.0)",
  "description": "Extends RSMS v2.0 for workorder-tracked resource sheets",
  "version": "2.0.0",
  "allOf": [
    {
      "$ref": "./resource-sheet-metadata-schema.json"
    },
    {
      "type": "object",
      "properties": {
        "workorder_id": {
          "type": "string",
          "pattern": "^WO-[A-Z0-9-]+-\\d{3}$",
          "description": "Workorder ID tracking this feature"
        },
        "feature_id": {
          "type": "string",
          "description": "Feature identifier for multi-agent coordination"
        },
        "phase": {
          "type": "string",
          "enum": ["phase_1", "phase_2", "phase_3"],
          "description": "Development phase this was created/updated in"
        },
        "complexity": {
          "type": "string",
          "enum": ["trivial", "low", "medium", "high", "very_high"],
          "description": "Code complexity rating"
        },
        "dependencies": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Package/library dependencies (not source files)"
        },
        "related_sheets": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Related resource sheet documentation"
        },
        "created": {
          "type": "string",
          "format": "date",
          "description": "Creation date (YYYY-MM-DD)"
        },
        "updated": {
          "type": "string",
          "format": "date",
          "description": "Last update date (YYYY-MM-DD)"
        },
        "loc": {
          "type": "integer",
          "minimum": 0,
          "description": "Lines of code in the component"
        }
      }
    }
  ]
}
```

### Step 2: Update Validator Logic (1 hour)
**File:** `papertrail/validators/resource_sheet.py`

```python
def get_schema_for_resource_sheet(frontmatter: dict) -> dict:
    """Auto-detect which schema to use based on frontmatter fields."""

    # If workorder tracking fields present, use extended schema
    if "workorder_id" in frontmatter or "feature_id" in frontmatter:
        return load_schema("rsms-workorder-v2.0.json")

    # Otherwise use base schema
    return load_schema("resource-sheet-metadata-schema.json")
```

### Step 3: Update Documentation (30 min)
**Files to update:**
- `standards/documentation/resource-sheet-standards.md`
- `README.md` (add schema variant explanation)
- `RSMS-SPECIFICATION.md` (document extended variant)

**Content:**
- When to use base vs extended schema
- Examples of both schema types
- Migration guide for existing sheets

### Step 4: Fix Status Enum Values (15 min)
**Change in all Phase 2 sheets:**
```yaml
# Before
status: active

# After
status: APPROVED
```

**Files to update:**
- QuickFileSearch-RESOURCE-SHEET.md
- TreeActionsToolbar-RESOURCE-SHEET.md
- fuzzyMatch-Utility-RESOURCE-SHEET.md

### Step 5: Re-validate All Documents (15 min)
Run papertrail validation on all 8 documents

**Expected Result:**
- 100% pass rate (8/8 documents)
- Average score: 85-95/100
- 0 CRITICAL errors
- 0 MAJOR errors
- Phase 2 gate UNBLOCKED

---

## Total Effort Estimate

| Task | Time |
|------|------|
| Create extended schema | 30 min |
| Update validator logic | 1 hour |
| Update documentation | 30 min |
| Fix status enum values | 15 min |
| Re-validate all docs | 15 min |
| **TOTAL** | **~2.5 hours** |

---

## Next Steps

1. ✅ **COMPLETE:** Fix CLAUDE.md frontmatter (CRITICAL error resolved, score 0 → 98/100)
2. ⏳ **PENDING:** Implement Option C (Extended Schema Variant)
3. ⏳ **PENDING:** Re-validate all Phase 2 documents
4. ⏳ **PENDING:** Achieve 100% pass rate
5. ⏳ **PENDING:** Unblock Phase 2 gate

---

## Current Blocking Issues

1. ✅ ~~CRITICAL: CLAUDE.md missing frontmatter~~ **FIXED**
2. ❌ MAJOR: RSMS v2.0 schema mismatch (21+ errors across 6 sheets)
3. ❌ MAJOR: 0% validation pass rate (0/8 documents)

**Phase 2 Gate Status:** BLOCKED until schema issue resolved
