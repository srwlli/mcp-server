---
agent: 'Lloyd (Planning Assistant)'
date: '2026-01-04'
task: UPDATE
scope: 'All documentation across CodeRef ecosystem'
version: '1.0.0'
enforcement: 'Automated validators + manual review'
category: documentation
title: 'Global Documentation Standards'
---

# Global Documentation Standards

**Version:** 1.0.0
**Scope:** All documentation across CodeRef ecosystem
**Enforcement:** Automated validators + manual review

---

## 1. Headers

All documentation files must include structured headers at the top of the file.

### YAML Front Matter (Required)

All markdown documents must start with YAML front matter delimited by `---`:

```yaml
---
agent: {agent-name}
date: YYYY-MM-DD
task: CREATE|UPDATE|REVIEW|DOCUMENT|CONSOLIDATE
---
```

### Required Fields

| Field | Type | Format | Example |
|-------|------|--------|---------|
| agent | string | Any string | `Claude Sonnet 4.5` |
| date | string | YYYY-MM-DD | `2026-01-04` |
| task | enum | One of 5 values | `CREATE` |

### Task Enum Values

- `CREATE` - New document creation
- `UPDATE` - Updating existing content
- `REVIEW` - Reviewing/auditing content
- `DOCUMENT` - Documenting existing code/features
- `CONSOLIDATE` - Merging multiple documents


### Universal Documentation Standards (UDS) - 3-Tier Hierarchy

**Effective:** 2026-01-10
**Implementation:** WO-UDS-SYSTEM-001

All documentation follows a 3-tier metadata hierarchy:

#### Tier 1: Base UDS (Required for ALL markdown)
```yaml
---
agent: {agent-name}
date: YYYY-MM-DD
task: CREATE|UPDATE|REVIEW|DOCUMENT|CONSOLIDATE|MIGRATE|ARCHIVE
---
```

#### Tier 2: Category Extensions (Required for specific doc types)

**Foundation Docs** (README, ARCHITECTURE, API, SCHEMA, COMPONENTS):
- `workorder_id` - Workorder tracking ID
- `generated_by` - MCP server (must start with "coderef-docs")
- `feature_id` - Feature identifier (kebab-case)
- `doc_type` - Document type enum

**Workorder Docs** (plan.json, DELIVERABLES.md, context.json):
- `workorder_id` - Workorder tracking ID
- `generated_by` - MCP server (must start with "coderef-workflow")
- `feature_id` - Feature identifier
- `doc_type` - Document type enum
- `status` - Workorder status enum

**System Docs** (CLAUDE.md, SESSION-INDEX.md):
- `project` - Project name
- `version` - System version
- `status` - System status

**Standards Docs** (global-documentation-standards.md, resource-sheet-standards.md):
- `scope` - Scope of standards
- `version` - Standards version
- `enforcement` - Enforcement method

#### Tier 3: Type-Specific Fields (Optional)
- `title` - Document title
- `version` - Document version (semver)
- `timestamp` - ISO 8601 timestamp
- `status` - Document status
- Category-specific fields as defined in schemas

### Timestamp Standards

**Policy:** ALL timestamp generation MUST use `coderef-docs/utils/timestamp.py`

**Formats:**
- `date` field: YYYY-MM-DD format (from `get_date()`)
- `timestamp` field: ISO 8601 with timezone (from `get_timestamp()`)
- Plan.json timestamps: ISO 8601 UTC (from `get_iso_timestamp()`)

**Example:**
```python
from utils.timestamp import get_date, get_timestamp

# In YAML frontmatter
date: {get_date()}          # "2026-01-10"
timestamp: {get_timestamp()}  # "2026-01-10T14:30:45Z"
```

**Rationale:** Ensures consistency across all generated documentation and schema validation compliance.

### Optional Fields

Additional fields may be included based on document type:

**For Resource Sheets:**
- `subject` - Component/topic name
- `parent_project` - Parent project name
- `category` - Classification (service, controller, model, etc.)
- `version` - Semver version
- `related_files` - Array of related source files
- `related_docs` - Array of related documentation files

**For Implementation Plans:**
- `workorder_id` - Workorder tracking ID
- `feature_name` - Feature identifier
- `status` - Implementation status

---

## 2. Footers

All documentation files should include metadata at the bottom.

### Standard Footer Format

```markdown
---

**Last Updated:** YYYY-MM-DD
**Version:** X.Y.Z
**Maintained by:** {team-or-person}
```

### Required Elements

- `Last Updated` - Date of last modification (YYYY-MM-DD format)
- `Version` - Semantic version number (if applicable)
- `Maintained by` - Team or individual responsible

### Example

```markdown
---

**Last Updated:** 2026-01-04
**Version:** 1.0.0
**Maintained by:** CodeRef Team
```

---

## 3. No Emojis

Documentation must not contain emoji characters.

### Rule

All documentation files must be free of emoji characters including:
- Emoticons (😀, 😊, etc.)
- Symbols and pictographs (🔍, 📊, etc.)
- Status indicators (✅, ❌, ⚠️, etc.)
- Decorative elements (🎉, 🚀, etc.)

### Text Alternatives

Use standardized text markers instead:

| Instead of | Use |
|------------|-----|
| ✅ | [PASS] |
| ❌ | [FAIL] |
| ⚠️ | [WARN] |
| 💡 | [INFO] |
| 🚫 | [DEPRECATED] |
| 🔄 | [IN PROGRESS] |
| ⏳ | [PENDING] |

### Rationale

- **Consistency**: Text markers are consistent across all platforms
- **Accessibility**: Screen readers handle text better than emojis
- **Git diffs**: Text changes are clearer in version control
- **Professional tone**: Text markers maintain professional documentation standards

### Auto-Fix

Use the emoji removal script to clean existing documents:

```bash
python scripts/remove-emojis.py {file-or-directory} --recursive
```

---

## Validation

### Automated Checks

Validators enforce these standards:

1. **Resource Sheet Validator** - `validators/resource-sheets/validate.ps1`
   - Checks YAML front matter structure
   - Validates required fields
   - Detects emojis
   - Verifies naming conventions

2. **Script Frontmatter Validator** - `validators/scripts/validate.py`
   - Validates script/test YAML frontmatter
   - Checks triangular bidirectional references

### Manual Review

Standards not yet automated:
- Footer format and completeness
- Content tone and professionalism
- Document structure and organization

---

## Exceptions

### When Standards Don't Apply

These standards do NOT apply to:
- Code files (source code, tests)
- Configuration files (JSON, YAML, TOML)
- Build artifacts
- Third-party documentation

### Deprecated Files

Existing files may not fully comply. When updating:
1. Bring headers into compliance
2. Add footer if missing
3. Remove emojis
4. Update `date` field in YAML front matter

---

## Enforcement

### Validation Workflow

1. Run validator before committing documentation
2. Fix any failures reported
3. Commit only after validation passes

### Pre-Commit Checks

Recommended git hooks:
```bash
# .git/hooks/pre-commit
pwsh validators/resource-sheets/validate.ps1 -Path .
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-04 | Initial global standards (headers, footers, no emojis) |

---

**Maintained by:** Papertrail Standards Team
**Schema:** `papertrail/schemas/documentation/global-standards-schema.json`
**Validators:** `papertrail/validators/`
