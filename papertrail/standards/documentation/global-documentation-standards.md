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
