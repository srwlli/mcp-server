# Papertrail Document Report

**Agent:** papertrail
**Workorder:** WO-CODEREF-IO-INVENTORY-002
**Generated:** 2026-01-02
**Source I/O Inventory:** C:\Users\willh\.mcp-servers\coderef\sessions\coderef-io-inventory\io-reports\papertrail-io.json

---

## Complete Document List

| Filename | Type | I/O | Source/Destination | Notes |
|----------|------|-----|-------------------|-------|
| `papertrail/schemas/plan.json` | config | input | papertrail (internal) | Plan.json validation schema |
| `papertrail/schemas/deliverables.json` | config | input | papertrail (internal) | DELIVERABLES.md validation schema |
| `papertrail/schemas/architecture.json` | config | input | papertrail (internal) | ARCHITECTURE.md validation schema |
| `papertrail/schemas/readme.json` | config | input | papertrail (internal) | README.md validation schema |
| `papertrail/schemas/api.json` | config | input | papertrail (internal) | API.md validation schema |
| `coderef/workorder/{feature}/plan.json` | workflow_doc | input | coderef-workflow | Plan metadata for Workflow extension |
| `coderef/context/{feature}-{type}-health.json` | other | both | papertrail ↔ filesystem | Load/store document health scores |
| `{any_document_path}.md` | other | input | any agent | Arbitrary documents to validate |
| `{any_document_path}.json` | other | input | any agent | JSON documents to validate |
| `{template_dir}/*.md` | other | input | any agent | Jinja2 template files |
| `{output_path}.md` | other | output | papertrail → any agent | Generated docs with UDS headers/footers |
| `DEMO_OUTPUT.md` | other | output | papertrail → filesystem | Demo script output (testing only) |

**Total:** 12 unique document patterns (10 inputs, 2 outputs, 1 both)

---

## Cross-Agent Dependencies

### Documents READ from Other Agents

1. **plan.json** ← `coderef-workflow`
   - Path: `coderef/workorder/{feature}/plan.json`
   - Purpose: Workflow extension reads plan metadata for template rendering
   - Frequency: Often (template-based workflows)

### Documents WRITTEN for Other Agents

1. **{output_path}.md** → `any agent`
   - Path: Variable (specified by caller)
   - Purpose: Generated documents with UDS headers/footers for validation and traceability
   - Frequency: Always (primary output)

2. **coderef/context/{feature}-{type}-health.json** → `filesystem`
   - Path: `coderef/context/{feature}-{type}-health.json`
   - Purpose: Document health scores for monitoring and reporting
   - Frequency: Often (validation workflows)

---

## External Sources

### Template Sources
- **{template_dir}/*.md** - External template files provided by users for Jinja2 rendering
- Source: Any agent or external system
- Format: Markdown with Jinja2 syntax

### Validation Targets
- **{any_document_path}.md** - Any markdown document requiring UDS validation
- **{any_document_path}.json** - Any JSON document requiring schema validation
- Source: Any agent (coderef-workflow, coderef-docs, coderef-personas, etc.)
- Format: Markdown or JSON

---

## Document Flow Summary

### Primary Role: Validation & Transformation Layer

**Input Flow:**
```
Internal Schemas (5 JSON files)
    ↓
Papertrail Validator
    ↓
Validation Results (0-100 score)
```

**Cross-Agent Flow:**
```
coderef-workflow (plan.json)
    ↓
Papertrail Workflow Extension
    ↓
Template Rendering with Plan Data
```

**Output Flow:**
```
Raw Document
    ↓
Papertrail Template Engine
    ↓
UDS Headers/Footers Injected
    ↓
Validated Output → Any Agent
```

---

## Notes

- **Validation-Centric Architecture**: Papertrail primarily operates as a library/validator - it doesn't have fixed input/output files. It validates/transforms whatever documents are passed to it.
- **Dynamic Paths**: Most document paths are dynamic (e.g., `{any_document_path}.md`, `{output_path}.md`) because papertrail is a service layer, not a document producer.
- **Schema Repository**: Maintains 5 internal JSON schemas for validating plan, deliverables, architecture, readme, and API documents.
- **Health Score Persistence**: Reads and writes health scores to `coderef/context/` for tracking document quality over time.
- **Template Extensions**: Supports Jinja2 templates with CodeRef extensions (git, workflow, coderef-context integrations).
