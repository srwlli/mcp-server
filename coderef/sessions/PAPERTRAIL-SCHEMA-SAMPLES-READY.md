# ✅ Schema Samples Ready for Papertrail

**Date:** 2026-01-10
**From:** coderef-workflow agent
**To:** Papertrail team
**Workorder:** WO-PAPERTRAIL-SCHEMA-ADDITIONS-001

---

## Samples Provided

I've prepared **6 sample files** (3 of each type) for schema design:

### Location
```
C:\Users\willh\.mcp-servers\coderef\sessions\papertrail-schema-samples\
```

### Files

**analysis.json (3 samples):**
- `analysis-sample-1.json` (6.8K) - coderef-context-integration
- `analysis-sample-2.json` (6.8K) - coderef-context-usage-verification
- `analysis-sample-3.json` (2.8K) - complete-workorder-command

**execution-log.json (3 samples):**
- `execution-log-sample-1.json` (3.4K) - coderef-context-integration
- `execution-log-sample-2.json` (3.4K) - coderef-context-usage-verification
- `execution-log-sample-3.json` (5.9K) - execute-plan-rename

---

## Next Steps for Papertrail

### 1. Create analysis-json-schema.json
**Location:** `papertrail/schemas/workflow/analysis-json-schema.json`

**Key Fields to Capture:**
- `foundation_docs` (object)
- `dependencies` (object)
- `inventory` (array of code elements)
- `patterns` (array of coding conventions)
- `reference_components` (array)
- `test_inventory` (object)

### 2. Create execution-log-json-schema.json
**Location:** `papertrail/schemas/workflow/execution-log-json-schema.json`

**Key Fields to Capture:**
- `timestamp` (ISO 8601 string)
- `workorder_id` (string, pattern: `WO-[A-Z0-9-]+-\d{3}`)
- `feature_name` (string)
- `task_count` (integer)
- `tasks` (array of task objects)
  - `content` (string)
  - `activeForm` (string)
  - `status` (enum: pending, in_progress, completed)

**Cross-Validation Required:**
- Verify task IDs in execution-log match task IDs in corresponding plan.json
- Ensure workorder_id format matches standard pattern

### 3. Create Validators
**AnalysisValidator:** `papertrail/validators/analysis.py`
**ExecutionLogValidator:** `papertrail/validators/execution_log.py`

Both must:
- Inherit from `BaseUDSValidator`
- Score threshold >= 90
- Follow JSON Schema Draft-07

### 4. Update ValidatorFactory
Add detection patterns for:
- `**/analysis.json` → AnalysisValidator
- `**/execution-log.json` → ExecutionLogValidator

---

## Timeline

**Week 1 Priority:** execution-log.json schema (P1) - Required for workflow resumption
**Week 3 Priority:** analysis.json schema (P2) - Less critical

**Blocked Workorders:**
- WO-CODEREF-WORKFLOW-UDS-COMPLIANCE-001 cannot complete GAP-003 and GAP-007 until schemas ready

---

## Reference Documentation

See `C:\Users\willh\.mcp-servers\coderef\sessions\papertrail-schema-samples\README.md` for:
- Detailed schema requirements
- Usage patterns
- Integration timeline

---

**Ready for WO-PAPERTRAIL-SCHEMA-ADDITIONS-001 to begin!**
