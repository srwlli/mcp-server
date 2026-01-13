# Papertrail Schema Samples

**Purpose:** Sample files for Papertrail team to design schemas for WO-PAPERTRAIL-SCHEMA-ADDITIONS-001

**Workorder:** WO-PAPERTRAIL-UDS-ALIGNMENT-002 → WO-PAPERTRAIL-SCHEMA-ADDITIONS-001
**Created:** 2026-01-10
**Provider:** coderef-workflow agent

---

## Sample Files Provided

### analysis.json (3 samples)

**Purpose:** Project analysis output from `analyze_project_for_planning` tool

**Files:**
- `analysis-sample-1.json` - From coderef-context-integration workorder
- `analysis-sample-2.json` - From coderef-context-usage-verification workorder
- `analysis-sample-3.json` - From complete-workorder-command workorder

**Expected Schema Fields:**
```json
{
  "required": [
    "foundation_docs",
    "dependencies",
    "inventory",
    "patterns",
    "reference_components",
    "test_inventory"
  ],
  "structure": "Nested objects with arrays of project analysis data"
}
```

**Usage:** Used by `create_plan` tool to generate implementation plans from project analysis

---

### execution-log.json (3 samples)

**Purpose:** Task execution tracking output from `execute_plan` tool

**Files:**
- `execution-log-sample-1.json` - From coderef-context-integration workorder
- `execution-log-sample-2.json` - From coderef-context-usage-verification workorder
- `execution-log-sample-3.json` - From execute-plan-rename workorder

**Expected Schema Fields:**
```json
{
  "required": [
    "timestamp",
    "workorder_id",
    "feature_name",
    "task_count",
    "tasks"
  ],
  "tasks_structure": {
    "content": "string",
    "activeForm": "string",
    "status": "pending|in_progress|completed"
  }
}
```

**Cross-Validation:** Task IDs in execution-log.json should reference task IDs in corresponding plan.json

**Usage:** Tracks TodoWrite task execution progress for workorders

---

## Schema Design Requirements

**From WO-PAPERTRAIL-SCHEMA-ADDITIONS-001:**

1. **analysis-json-schema.json**
   - Location: `papertrail/schemas/workflow/`
   - Validator: `AnalysisValidator` in `papertrail/validators/analysis.py`
   - Inherits from: `BaseUDSValidator`
   - Score threshold: >= 90

2. **execution-log-json-schema.json**
   - Location: `papertrail/schemas/workflow/`
   - Validator: `ExecutionLogValidator` in `papertrail/validators/execution_log.py`
   - Inherits from: `BaseUDSValidator`
   - Score threshold: >= 90
   - Cross-validation: Verify task_ids reference plan.json tasks

3. **ValidatorFactory Updates**
   - Add pattern detection for `analysis.json`
   - Add pattern detection for `execution-log.json`
   - Auto-detect validator based on file path

---

## Integration Timeline

**Week 1:** Papertrail creates schemas (WO-PAPERTRAIL-SCHEMA-ADDITIONS-001)
**Week 2:** coderef-workflow integrates validators (WO-CODEREF-WORKFLOW-UDS-COMPLIANCE-001)

**Blocked Tasks Until Schemas Complete:**
- GAP-003: analysis.json validation (3 hours)
- GAP-007: execution-log.json validation (3 hours)

---

**Contact:** coderef-workflow agent
**Samples Location:** `C:\Users\willh\.mcp-servers\coderef\sessions\papertrail-schema-samples\`
