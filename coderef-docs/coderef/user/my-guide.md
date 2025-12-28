# coderef-docs - Tool Reference

Quick reference for MCP documentation tools.

## Documentation Generation

- **list_templates** - Show available templates (readme, architecture, api, schema, components)
- **get_template** - Get specific template content
- **generate_foundation_docs** - Generate 5 docs with code intelligence (API, Schema, Components, Architecture, README)
- **generate_individual_doc** - Generate single doc from template
- **generate_quickref_interactive** - Create quick reference guide for any app type

## Changelog Management

- **get_changelog** - Retrieve changelog by version or type
- **add_changelog_entry** - Add changelog entry with full metadata
- **record_changes** - Auto-detect git changes and create changelog entry

## Standards & Compliance

- **establish_standards** - Extract UI/UX/behavior patterns from codebase
- **audit_codebase** - Check compliance with standards (0-100 score)
- **check_consistency** - Pre-commit gate for staged changes

## Slash Commands

**Documentation:**
- `/generate-docs` - Generate 5 foundation docs
- `/generate-quickref` - Interactive quickref generation

**Changelog:**
- `/record-changes` - Smart changelog with git detection
- `/add-changelog` - Manual changelog entry

**Standards:**
- `/establish-standards` - Extract coding standards
- `/audit-codebase` - Compliance check
- `/check-consistency` - Pre-commit check

## Common Workflows

**Generate complete documentation:**
```
/generate-docs
```

**Record feature completion:**
```
/record-changes → Auto-detects changes → Creates entry
```

**Enforce code standards:**
```
/establish-standards → /audit-codebase → /check-consistency
```

## Output Locations

- README.md → Project root
- Foundation docs → coderef/foundation-docs/
- User docs → coderef/user/
- CHANGELOG.json → coderef/changelog/
- Standards → coderef/standards/

## More Information

- Complete API reference: [API.md](../foundation-docs/API.md)
- Comprehensive tutorial: [USER-GUIDE.md](USER-GUIDE.md)
- Quick reference: [quickref.md](quickref.md)
- Architecture details: [ARCHITECTURE.md](../foundation-docs/ARCHITECTURE.md)
