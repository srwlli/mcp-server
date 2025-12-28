# coderef-docs Quick Reference

Fast lookup for all 11 MCP tools and slash commands.

---

## Documentation Generation

### generate_foundation_docs
Generate 5 foundation docs with code intelligence

**Usage:**
```json
{
  "tool": "generate_foundation_docs",
  "arguments": {
    "project_path": "/path/to/project"
  }
}
```

**Slash:** `/generate-docs`

**Output:** 
- README.md (project root)
- ARCHITECTURE.md, API.md, SCHEMA.md, COMPONENTS.md (coderef/foundation-docs/)

**Time:** ~2 minutes

---

### generate_individual_doc
Generate single doc from template

**Usage:**
```json
{
  "tool": "generate_individual_doc",
  "arguments": {
    "project_path": "/path/to/project",
    "template_name": "api"
  }
}
```

**Templates:** readme, architecture, api, schema, components

**Output:** Single markdown file

---

### generate_quickref_interactive
Interactive quickref guide generation

**Usage:**
```json
{
  "tool": "generate_quickref_interactive",
  "arguments": {
    "project_path": "/path/to/project",
    "app_type": "cli"
  }
}
```

**Slash:** `/generate-quickref`

**App Types:** cli, web, api, desktop, library

**Output:** quickref.md (150-250 lines)

---

### list_templates
Show available templates

**Usage:**
```json
{
  "tool": "list_templates",
  "arguments": {}
}
```

**Slash:** `/list-templates`

**Returns:** List of template names

---

### get_template
Get specific template content

**Usage:**
```json
{
  "tool": "get_template",
  "arguments": {
    "template_name": "readme"
  }
}
```

**Slash:** `/get-template`

**Returns:** Template content with POWER framework

---

## Changelog Management

### record_changes
Smart changelog with git auto-detection

**Usage:**
```json
{
  "tool": "record_changes",
  "arguments": {
    "project_path": "/path/to/project",
    "version": "3.2.0"
  }
}
```

**Slash:** `/record-changes`

**Behavior:**
1. Auto-detects changed files via git
2. Suggests change_type from commits
3. Calculates severity from scope
4. Shows preview for confirmation
5. Creates CHANGELOG entry

**Output:** CHANGELOG.json entry

**Time:** ~30 seconds

---

### add_changelog_entry
Manual changelog entry

**Usage:**
```json
{
  "tool": "add_changelog_entry",
  "arguments": {
    "project_path": "/path/to/project",
    "version": "3.2.0",
    "change_type": "feature",
    "severity": "minor",
    "title": "Add context injection",
    "description": "Sequential generation with CLI integration",
    "files": ["tool_handlers.py", "extractors.py"],
    "reason": "Improve documentation accuracy",
    "impact": "Generated docs reflect actual code"
  }
}
```

**Slash:** `/add-changelog`

**Required:** project_path, version, change_type, severity, title, description, files, reason, impact

**Optional:** breaking, migration, contributors, summary

---

### get_changelog
Query changelog by version or type

**Usage:**
```json
{
  "tool": "get_changelog",
  "arguments": {
    "project_path": "/path/to/project",
    "version": "3.2.0",
    "change_type": "feature",
    "breaking_only": false
  }
}
```

**Slash:** `/get-changelog`

**Returns:** Filtered changelog entries

---

## Standards & Compliance

### establish_standards
Extract UI/UX/behavior patterns from codebase

**Usage:**
```json
{
  "tool": "establish_standards",
  "arguments": {
    "project_path": "/path/to/project",
    "focus_areas": ["ui_components", "behavior_patterns"],
    "scan_depth": "standard"
  }
}
```

**Slash:** `/establish-standards`

**Focus Areas:** ui_components, behavior_patterns, ux_flows, all

**Scan Depth:** quick, standard, deep

**Output:** 4 files in coderef/standards/
- ui-patterns.md
- behavior-patterns.md
- ux-patterns.md
- standards-index.md

**Time:** ~3-5 minutes

---

### audit_codebase
Check compliance with standards (0-100 score)

**Usage:**
```json
{
  "tool": "audit_codebase",
  "arguments": {
    "project_path": "/path/to/project",
    "scope": ["all"],
    "severity_filter": "all",
    "generate_fixes": true
  }
}
```

**Slash:** `/audit-codebase`

**Scope:** ui_patterns, behavior_patterns, ux_patterns, all

**Severity Filter:** critical, major, minor, all

**Output:** Compliance report with score, violations, fix suggestions

**Time:** ~5-10 minutes

---

### check_consistency
Pre-commit gate for staged changes

**Usage:**
```json
{
  "tool": "check_consistency",
  "arguments": {
    "project_path": "/path/to/project",
    "files": ["src/component.py"],
    "scope": ["ui_patterns"],
    "severity_threshold": "major",
    "fail_on_violations": true
  }
}
```

**Slash:** `/check-consistency`

**Files:** Array of file paths (auto-detects git changes if omitted)

**Severity Threshold:** critical, major, minor

**Output:** Pass/fail + violations

**Time:** ~10 seconds

---

## Common Workflows

### New Project Setup
```
1. /generate-docs
   → 5 foundation docs

2. /generate-quickref
   → quickref.md

3. /establish-standards
   → Extract patterns
```

**Time:** ~10 minutes total

---

### Feature Completion
```
1. Code your feature
   [Your work]

2. /record-changes
   → Auto-detects changes

3. /check-consistency
   → Verify standards

4. git commit
```

**Time:** ~2 minutes (doc part)

---

### Pre-commit Check
```
1. git add .

2. /check-consistency
   → Pass/fail

3. If pass: git commit
   If fail: Fix issues
```

**Time:** ~30 seconds

---

## Error Codes

| Error | Cause | Solution |
|-------|-------|----------|
| Invalid project_path | Path doesn't exist | Check path is correct |
| Template not found | Invalid template name | Use list_templates |
| Git repository required | Not a git repo | Initialize git first |
| Standards directory missing | No standards established | Run establish_standards |
| Version format invalid | Wrong version format | Use x.y.z format |

---

## File Locations

**Generated by coderef-docs:**
- `README.md` → Project root
- `ARCHITECTURE.md` → coderef/foundation-docs/
- `API.md` → coderef/foundation-docs/
- `SCHEMA.md` → coderef/foundation-docs/
- `COMPONENTS.md` → coderef/foundation-docs/
- `my-guide.md` → coderef/user/
- `USER-GUIDE.md` → coderef/user/
- `FEATURES.md` → coderef/user/
- `quickref.md` → coderef/user/
- `CHANGELOG.json` → coderef/changelog/
- `ui-patterns.md` → coderef/standards/
- `behavior-patterns.md` → coderef/standards/
- `ux-patterns.md` → coderef/standards/
- `standards-index.md` → coderef/standards/

---

## Context Injection

**When @coderef/core CLI is available:**

✅ **API.md** - Real API endpoints extracted
✅ **SCHEMA.md** - Real data models extracted
✅ **COMPONENTS.md** - Real UI components extracted

**When CLI is NOT available:**

⚠️ **All templates** - Placeholders used
⚠️ **Still useful** - POWER framework structure maintained

**To enable:**
```bash
npm install -g @coderef/core
# Restart Claude Code
```

---

## Quick Tips

💡 **Tip 1:** Run `/generate-docs` at project start, not end

💡 **Tip 2:** Add `/check-consistency` to pre-commit hooks

💡 **Tip 3:** Use `/record-changes` instead of manual changelog entries

💡 **Tip 4:** Run `/establish-standards` once per project

💡 **Tip 5:** README.md goes in root, everything else in coderef/

---

## More Information

- **Complete Tutorial:** [USER-GUIDE.md](USER-GUIDE.md)
- **Tool Catalog:** [my-guide.md](my-guide.md)
- **Feature Details:** [FEATURES.md](FEATURES.md)
- **API Reference:** [API.md](../foundation-docs/API.md)
- **Architecture:** [ARCHITECTURE.md](../foundation-docs/ARCHITECTURE.md)

---

*Last Updated: 2025-12-27 | Version: 3.2.0*
