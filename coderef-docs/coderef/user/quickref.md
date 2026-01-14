# coderef-docs Quick Reference

Fast scannable reference for all 16 MCP tools with v4.0.0 enhancements.

---

## MCP Tools (16)

### Documentation (5 tools)
```
list_templates              Show templates + MCP status 🆕
get_template NAME           Get template content
generate_foundation_docs    Generate 5 docs + drift check 🆕
generate_individual_doc     Generate single doc [INTERNAL] 🆕
coderef_foundation_docs     [DEPRECATED] Use generate_foundation_docs
```

### User Docs (4 tools - NEW v4.0.0) 🆕
```
generate_my_guide           Auto developer quick-start (75%+ auto-fill)
generate_user_guide         10-section comprehensive guide
generate_features           Feature inventory + workorder tracking
generate_quickref_interactive  Interactive quickref builder
```

### Resource Sheets (1 tool)
```
generate_resource_sheet     Module-based docs (MD + JSON + JSDoc)
```

### Changelog (2 tools)
```
add_changelog_entry         Manual changelog entry
record_changes              Smart git-based changelog ⭐
```

### Standards (3 tools - ENHANCED v4.0.0) 🆕
```
establish_standards         Extract patterns + MCP semantic analysis 🆕
audit_codebase              Check compliance (0-100)
check_consistency           Pre-commit gate ⭐
```

### Validation (2 tools)
```
validate_document           Validate against UDS schema
check_document_health       Calculate health score (0-100)
```

---

## Slash Commands (26+)

### Documentation
```
/generate-docs              Generate all 5 foundation docs
/generate-user-docs         Generate all 4 user docs
/list-templates             Show available templates
/get-template NAME          Get specific template
```

### Resource Sheets
```
/generate-resource-sheet    Create module-based docs
```

### Changelog
```
/add-changelog              Add manual entry
/record-changes             Smart git changelog
```

### Standards
```
/establish-standards        Extract patterns
/audit-codebase             Check compliance
/check-consistency          Pre-commit check
```

### Validation
```
/validate-doc               Validate document
/check-doc-health           Check health score
```

---

## Common Workflows

### New Project
```bash
1. /generate-docs              # Foundation docs (2-5 min)
2. /generate-user-docs         # User docs (3-7 min)
3. /establish-standards        # Extract standards (5-10 sec)
```

### After Feature
```bash
git add .
/record-changes                # Update changelog (30 sec)
/generate-docs                 # Update docs if API changed
```

### Pre-Commit
```bash
git add modified_files.py
/check-consistency             # Validate (10-30 sec)
# Fix violations if any
git commit -m "feat: ..."
```

---

## File Locations

```
README.md                      Project root
coderef/foundation-docs/       Technical docs (API, SCHEMA, etc.)
coderef/user/                  User-facing docs
coderef/standards/             Coding standards
coderef/CHANGELOG.json         Change history
```

---

## Template Names

```
readme          Project README
architecture    System design
api             API reference
components      Module structure
schema          Data models
user-guide      Tutorial
my-guide        Tool reference
```

---

## Quick Tips

💡 Use `.coderef/` data for 10x faster standards  
💡 Call `/record-changes` after every feature  
💡 Run `/check-consistency` in pre-commit hooks  
💡 Combine with coderef-context for real code intelligence  

---

## Performance

```
With .coderef/              Without .coderef/
-------------------         -------------------
Standards: ~50ms            Standards: ~5-60s
Docs: Real data             Docs: Regex fallback
Audit: Fast                 Audit: Slower
```

---

## Error Quick Fixes

```
"Template not found"        → /list-templates
"Standards not established" → /establish-standards
"Invalid parameters"        → /get-template NAME
Slow standards             → Generate .coderef/ first
```

---

**Version:** 4.0.0 🆕
**Tools:** 16 MCP tools (13 active, 1 [INTERNAL], 1 [DEPRECATED])
**Commands:** 26+ slash commands
**Tests:** 185 tests (95%+ pass rate) 🆕
**Status:** ✅ Production Ready

**v4.0.0 Highlights:**
- 🆕 MCP orchestration with drift detection + semantic patterns
- 🆕 User docs automation (75%+ auto-fill)
- 🆕 Standards enhancement (55% → 80%+ quality)
- 🆕 Tool consolidation ([INTERNAL], [DEPRECATED] markings)
