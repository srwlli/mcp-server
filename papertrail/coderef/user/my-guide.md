---
agent: Claude Sonnet 4.5
date: "2026-01-13"
task: CREATE
workorder_id: WO-VALIDATION-ENHANCEMENT-001
feature_id: user-docs-generation
doc_type: user-facing
version: "1.0.0"
status: APPROVED
---

# Papertrail - Quick Tool Reference

**Universal Documentation Standards (UDS) Validation MCP Server**

---

## MCP Tools

### Document Validation
- validate_document - Auto-detect and validate any document against UDS schemas (0-100 score)
- validate_stub - Validate stub.json files with optional auto-fill
- validate_resource_sheet - Validate resource sheets against RSMS v2.0 standards

### Batch Validation
- check_all_docs - Validate all documents in a directory recursively
- check_all_resource_sheets - Validate all resource sheets in a directory

### Schema Validation
- validate_schema_completeness - Check if schema has required_sections for all doc_types
- validate_all_schemas - Validate all JSON schemas in schemas/documentation/

---

## Categories

### Validation Tools
Tools for validating individual documents and returning detailed reports with errors, warnings, and scores.

### Batch Tools
Tools for validating multiple documents at once and generating summary reports with pass/fail counts.

### Schema Tools
Tools for validating the JSON schemas themselves to ensure completeness and consistency.

---

## Common Workflows

**Single Document Validation**
1. Call validate_document with file_path
2. Review score (0-100) and errors
3. Fix issues and re-validate

**Batch Validation**
1. Call check_all_docs with directory path
2. Review summary with pass/fail counts
3. Address failed documents individually

**Schema Sync Check**
1. Call validate_schema_completeness with schema_name
2. Review required_sections coverage
3. Update schema if gaps found

---

## Quick Reference

Total MCP Tools: 7
- 3 single document validators
- 2 batch validators
- 2 schema validators

All tools return validation results with:
- Score (0-100)
- Errors by severity (CRITICAL, MAJOR, MINOR, WARNING)
- Completeness percentage (for foundation docs)

---

**For complete API reference, see:** `coderef/foundation-docs/API.md`
**For comprehensive tutorial, see:** `coderef/user/USER-GUIDE.md`
