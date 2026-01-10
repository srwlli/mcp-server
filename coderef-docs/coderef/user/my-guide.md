# coderef-docs - Tool Reference

Quick reference for MCP documentation tools and slash commands.

---

## MCP Tools (13 total)

### Documentation Generation
- list_templates - Show all available POWER framework templates
- get_template - Get specific template content by name
- generate_foundation_docs - Generate all 5 foundation docs (README, ARCHITECTURE, API, COMPONENTS, SCHEMA)
- generate_individual_doc - Generate single doc from template

### Resource Sheets
- generate_resource_sheet - Create composable module-based docs (markdown + JSON schema + JSDoc)

### Changelog Management
- add_changelog_entry - Manually add entry to CHANGELOG.json
- record_changes - Smart changelog with git auto-detection and AI confirmation
- generate_quickref_interactive - Interactive quickref generation for any app type

### Standards & Compliance
- establish_standards - Extract coding standards from codebase
- audit_codebase - Check standards compliance (0-100 score)
- check_consistency - Pre-commit gate for staged file changes

### Validation
- validate_document - Validate doc against UDS schema
- check_document_health - Calculate document health score (0-100)

---

## Slash Commands (26 total)

### Documentation
- /generate-docs - Generate all 5 foundation docs
- /generate-user-docs - Generate all 4 user-facing docs
- /list-templates - Show available templates
- /get-template - Get template content

### Resource Sheets
- /generate-resource-sheet - Create module-based documentation

### Changelog
- /add-changelog - Add manual changelog entry
- /record-changes - Smart changelog with git detection

### Standards
- /establish-standards - Extract code standards
- /audit-codebase - Check compliance
- /check-consistency - Pre-commit validation

### Validation
- /validate-doc - Validate against schema
- /check-doc-health - Calculate health score

---

## Quick Start

```
# Generate all foundation docs
/generate-docs

# Generate all user docs
/generate-user-docs

# Extract coding standards
/establish-standards

# Check compliance
/audit-codebase
```

---

**Version:** 3.4.0 | **Server:** coderef-docs | **Protocol:** MCP 1.0
