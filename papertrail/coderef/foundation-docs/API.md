---
agent: Claude Sonnet 4.5
date: "2026-01-13"
task: CREATE
workorder_id: WO-FOUNDATION-DOCS-001
generated_by: Claude Code
feature_id: foundation-documentation
doc_type: api
---

# Papertrail MCP Server API

## Endpoints

### validate_document
Validate any document against UDS schemas with auto-detection.

### check_all_docs
Batch validate all documents in a directory recursively.

### validate_resource_sheet  
Validate resource sheets against RSMS v2.0 standards.

### check_all_resource_sheets
Batch validate all resource sheets in a directory.

### validate_schema_completeness
Verify JSON schema has required_sections for all doc_types.

### validate_all_schemas
Batch validate all JSON schemas in schemas/documentation/.

### validate_stub
Validate stub.json files for feature idea tracking.

## Authentication

Not required - MCP tools available to authorized MCP clients.

## Request/Response Examples

See full documentation for detailed examples.

## Error Codes

- FILE_NOT_FOUND: File path does not exist
- INVALID_NAMING: Filename doesn't match convention  
- MISSING_FRONTMATTER: No YAML frontmatter found
- SCHEMA_VALIDATION_FAILED: JSON schema validation errors

---

**Last Updated:** 2026-01-13
**Maintained by:** Papertrail Team
