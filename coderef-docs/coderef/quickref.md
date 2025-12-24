# docs-mcp Quick Reference

**Version 1.8.0** | 18 MCP Tools | 12 Slash Commands

---

## At a Glance

**docs-mcp provides:**
- 📝 Documentation Generation (POWER framework)
- 📋 Changelog Management (JSON with validation)
- 🔍 Consistency Management (extract standards + audit)
- 📊 Planning Workflow (AI-assisted with validation)
- 📦 Project Inventory (files, dependencies, APIs, databases)

---

## Slash Commands (Type These)

| Command | Purpose | Speed |
|---------|---------|-------|
| `/generate-docs` | Generate 5 foundation docs | 6-15 min |
| `/generate-user-guide` | Generate USER-GUIDE.md only | 4-8 min |
| `/generate-quickref` | Generate quickref.md via interview | 2-4 min |
| `/establish-standards` | Extract UI/behavior/UX standards (run once) | 3-5 min |
| `/audit-codebase` | Full compliance audit with score | 1-5 sec |
| `/check-consistency` | Quick check on modified files only | <1 sec |
| `/gather-context` | Gather feature requirements before planning | 1-3 min |
| `/analyze-for-planning` | Discover project context | 80ms |
| `/get-planning-template` | Get planning template | 5ms |
| `/validate-plan` | Validate plan quality (0-100) | 18ms |
| `/generate-plan-review` | Generate markdown report | 5ms |
| `/database-inventory` | Discover database schemas | 1-5 sec |

---

## MCP Tools (Direct Calls)

### Documentation (5)

| Tool | Required Params | Returns |
|------|----------------|---------|
| `list_templates` | None | Template names |
| `get_template` | template_name | Template content |
| `generate_foundation_docs` | project_path | 5 templates + plan |
| `generate_individual_doc` | project_path, template_name | Single doc |
| `generate_quickref_interactive` | project_path | Interview questions |

**Templates**: readme, architecture, api, components, schema, user-guide

---

### Changelog (3)

| Tool | Type | Required Params | Optional Params |
|------|------|----------------|-----------------|
| `get_changelog` | READ | project_path | version, change_type, breaking_only |
| `add_changelog_entry` | WRITE | project_path, version, change_type, severity, title, description, files, reason, impact | breaking, migration, summary, contributors |
| `update_changelog` | META | project_path, version | None (returns instructions) |

**Change Types**: bugfix, enhancement, feature, breaking_change, deprecation, security
**Severities**: critical, major, minor, patch

---

### Consistency (3)

| Tool | Purpose | Required Params | Optional Params |
|------|---------|----------------|-----------------|
| `establish_standards` | Extract patterns | project_path | scan_depth, focus_areas |
| `audit_codebase` | Audit compliance | project_path | standards_dir, severity_filter, scope, generate_fixes |
| `check_consistency` | Check modified files | project_path | files, scope, severity_threshold, fail_on_violations |

**Scan Depths**: quick (~1-2min), standard (~3-5min), deep (~10-15min)
**Focus Areas**: ui_components, behavior_patterns, ux_flows, all
**Outputs**: 4 standards docs (UI-STANDARDS.md, BEHAVIOR-STANDARDS.md, UX-PATTERNS.md, COMPONENT-INDEX.md)

---

### Planning (4)

| Tool | Purpose | Speed | Required Params |
|------|---------|-------|----------------|
| `get_planning_template` | Get template | 5ms | None (optional: section) |
| `analyze_project_for_planning` | Discover context | 80ms | project_path |
| `validate_implementation_plan` | Validate plan | 18ms | project_path, plan_file_path |
| `generate_plan_review_report` | Format report | 5ms | project_path, plan_file_path, output_path |

**Validation Scores**: PASS (≥90), PASS_WITH_WARNINGS (≥85), NEEDS_REVISION (≥70), FAIL (<70)

---

### Project Inventory (4)

| Tool | Purpose | Required Params | Optional Params |
|------|---------|----------------|-----------------|
| `inventory_manifest` | File inventory | project_path | analysis_depth, exclude_dirs, max_file_size |
| `dependency_inventory` | Dependencies + security | project_path | scan_security, ecosystems, include_transitive |
| `api_inventory` | API endpoints | project_path | frameworks, include_graphql, scan_documentation |
| `database_inventory` | Database schemas | project_path | database_systems, include_migrations |

**Analysis Depths**: quick (~1-2s), standard (~3-5s), deep (~10-15s)
**Ecosystems**: npm, pip, cargo, composer, all
**API Frameworks**: fastapi, flask, express, graphql, all
**Database Systems**: postgresql, mysql, mongodb, sqlite, all
**Outputs**: manifest.json, dependencies.json, api.json, database.json

---

## Common Workflows

### Complete Project Setup
```
1. /generate-docs               → Create 5 foundation docs (README, ARCHITECTURE, API, COMPONENTS, SCHEMA)
2. /establish-standards         → Extract coding standards
3. /audit-codebase             → Baseline compliance check
```

### Planning Workflow
```
1. /gather-context (optional)  → Capture WHAT user wants → saves to coderef/working/{feature}/context.json
2. /analyze-for-planning       → Discover project context (80ms)
3. /get-planning-template      → Get template structure
4. AI creates plan JSON        → saves to coderef/working/{feature}/plan.json
5. /validate-plan              → Score plan (18ms)
6. Fix issues, re-validate until ≥90
7. /generate-plan-review       → Generate report (5ms)
8. User approves → Implement
```

### Pre-Commit Check
```
/check-consistency             → Check modified files only (<1s)
```

### Regular Maintenance
```
/audit-codebase                → Full compliance audit (1-5s)
```

---

## Tool Call Format

### MCP Tools (Full Names)
```
mcp__docs-mcp__list_templates()
mcp__docs-mcp__get_template(template_name="readme")
mcp__docs-mcp__generate_foundation_docs(project_path="C:/path")
mcp__docs-mcp__generate_individual_doc(project_path="C:/path", template_name="api")
mcp__docs-mcp__generate_quickref_interactive(project_path="C:/path", app_type="cli")
mcp__docs-mcp__get_changelog(project_path="C:/path")
mcp__docs-mcp__add_changelog_entry(project_path="C:/path", version="1.0.3", ...)
mcp__docs-mcp__update_changelog(project_path="C:/path", version="1.0.3")
mcp__docs-mcp__establish_standards(project_path="C:/path")
mcp__docs-mcp__audit_codebase(project_path="C:/path")
mcp__docs-mcp__check_consistency(project_path="C:/path")
mcp__docs-mcp__get_planning_template(section="all")
mcp__docs-mcp__analyze_project_for_planning(project_path="C:/path")
mcp__docs-mcp__validate_implementation_plan(project_path="C:/path", plan_file_path="plan.json")
mcp__docs-mcp__generate_plan_review_report(project_path="C:/path", plan_file_path="plan.json", output_path="report.md")
mcp__docs-mcp__inventory_manifest(project_path="C:/path", analysis_depth="standard")
mcp__docs-mcp__dependency_inventory(project_path="C:/path", scan_security=true, ecosystems=["all"])
mcp__docs-mcp__api_inventory(project_path="C:/path", frameworks=["all"], scan_documentation=true)
mcp__docs-mcp__database_inventory(project_path="C:/path", database_systems=["all"], include_migrations=true)
```

---

## Output Locations

| Type | Location | Files |
|------|----------|-------|
| Foundation Docs | `coderef/foundation-docs/` | README.md, ARCHITECTURE.md, API.md, COMPONENTS.md, SCHEMA.md (5 core) |
| Optional Docs | `coderef/foundation-docs/` | USER-GUIDE.md (generated separately) |
| Quickref | `coderef/` | quickref.md (scannable 150-250 lines) |
| Changelog | `coderef/changelog/` | CHANGELOG.json, schema.json |
| Standards | `coderef/standards/` | UI-STANDARDS.md, BEHAVIOR-STANDARDS.md, UX-PATTERNS.md, COMPONENT-INDEX.md |
| Audits | `coderef/audits/` | audit-YYYYMMDD-HHMMSS.md |
| Working Features | `coderef/working/<feature-name>/` | context.json, plan.json, review.json |
| Inventory | `coderef/inventory/` | manifest.json, dependencies.json, api.json, database.json, schema.json |

---

## Key Concepts

**Meta-Tool Pattern**: `update_changelog` returns instructions for AI instead of executing directly

**Consistency Trilogy**:
1. `establish_standards` - Extract patterns from code
2. `audit_codebase` - Check compliance (0-100 score)
3. Fix violations - Iterative improvement

**Planning Workflow**:
1. Analyze (80ms) → 2. Plan → 3. Validate (18ms) → 4. Review (5ms) → 5. Approve → 6. Implement

**Performance**:
- Planning analysis: ~80ms (750x faster than 60s manual)
- Plan validation: ~18ms (111x faster than 2s target)
- Review generation: ~5ms (600x faster than 3s target)

---

## Summary

| Category | Count | Tools |
|----------|-------|-------|
| Slash Commands | 12 | Fast shortcuts for common tasks |
| Documentation | 5 | list_templates, get_template, generate_foundation_docs, generate_individual_doc, generate_quickref_interactive |
| Changelog | 3 | get_changelog, add_changelog_entry, update_changelog |
| Consistency | 3 | establish_standards, audit_codebase, check_consistency |
| Planning | 4 | get_planning_template, analyze_project_for_planning, validate_implementation_plan, generate_plan_review_report |
| Project Inventory | 4 | inventory_manifest, dependency_inventory, api_inventory, database_inventory |

**Total**: 18 MCP tools + 12 slash commands

---

**For detailed usage**: See `user-guide.md`
**For AI context**: See `CLAUDE.md`
**For architecture**: See `ARCHITECTURE.md`
