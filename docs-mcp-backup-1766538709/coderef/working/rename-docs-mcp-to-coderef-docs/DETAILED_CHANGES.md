# Detailed List of All Changes Required

## docs-mcp → coderef-docs Rename

---

## 1. PYTHON FILES (6 files)

### server.py
```python
Line 3:  "Documentation Generation MCP Server" (no change needed)
Line 62: app = Server("docs-mcp")
         → app = Server("coderef-docs")

Line 6:  "This minimal version contains 11 documentation-focused tools."
         (Search for any "docs-mcp" in docstring)
```

### tool_handlers.py
```python
Search entire file for "docs-mcp" in:
- Error messages
- Logging statements (log_tool_call, log_error, logger.info)
- Comments
- Docstrings

Example changes:
"docs-mcp validation error" → "coderef-docs validation error"
```

### constants.py
- Verify no hardcoded "docs-mcp" strings

### logger_config.py
- Check if logger name includes "docs-mcp"
- Example: logger = logging.getLogger("docs-mcp") → logging.getLogger("coderef-docs")

### validation.py
- Check error messages for "docs-mcp" references

### error_responses.py
- Check error factory messages

---

## 2. CONFIGURATION FILES (2 files)

### pyproject.toml
```toml
[project]
name = "docs-mcp"
→ name = "coderef-docs"

description = "Documentation Generation MCP Server"
(no change needed)

version = "2.0.0"
→ version = "2.0.1" or "2.1.0" (bump version)

[project.urls]
homepage = "https://github.com/anthropics/docs-mcp"
→ "https://github.com/anthropics/coderef-docs"

repository = "https://github.com/anthropics/docs-mcp"
→ "https://github.com/anthropics/coderef-docs"

[tool.poetry]
name = "docs-mcp"
→ name = "coderef-docs"

version = "2.0.0"
→ version = "2.0.1" or "2.1.0"

[tool.poetry.urls]
homepage = "https://..."
repository = "https://..."
(update if present)
```

### .claude/commands.json
```json
Search for "docs-mcp" in server references
Update any command configurations
```

---

## 3. DOCUMENTATION FILES (5+ files)

### README.md
**Lines affected (examples):**
```markdown
# docs-mcp
→ # coderef-docs

**docs-mcp** is a focused MCP server providing...
→ **coderef-docs** is a focused MCP server providing...

The docs-mcp server helps you...
→ The coderef-docs server helps you...

## Installation

To use **docs-mcp**:
→ To use **coderef-docs**:

cd ~/.mcp-servers/docs-mcp
→ cd ~/.mcp-servers/coderef-docs

## Configuration

Add to your MCP settings (e.g., ~/.claude/mcp.json or Claude Desktop config):
{
  "mcpServers": {
    "docs-mcp": {
      "command": "python",
      "args": ["~/.mcp-servers/docs-mcp/server.py"]
    }
  }
}

→ Change "docs-mcp" key to "coderef-docs" and update path

## Tools

All 11 tools from **docs-mcp**
→ All 11 tools from **coderef-docs**

mcp__docs-mcp__list_templates
→ mcp__coderef-docs__list_templates
(for all tool references)
```

### CLAUDE.md (MOST EXTENSIVE - ~3000+ lines)

**Multiple sections with changes:**

1. **Quick Reference (Lines 20-50):**
   ```markdown
   **docs-mcp** is a focused MCP server providing:
   → **coderef-docs** is a focused MCP server providing:
   ```

2. **System Architecture (Lines 52-100):**
   ```
   server.py (374 lines)           # MCP entry point, 11 tool definitions
   (context describes docs-mcp architecture)
   → Update to reference coderef-docs
   ```

3. **Tool References (CRITICAL - ~200 occurrences):**
   ```markdown
   mcp__docs-mcp__list_templates
   → mcp__coderef-docs__list_templates

   mcp__docs-mcp__get_template
   → mcp__coderef-docs__get_template

   mcp__docs-mcp__generate_foundation_docs
   → mcp__coderef-docs__generate_foundation_docs

   mcp__docs-mcp__generate_individual_doc
   → mcp__coderef-docs__generate_individual_doc

   mcp__docs-mcp__get_changelog
   → mcp__coderef-docs__get_changelog

   mcp__docs-mcp__add_changelog_entry
   → mcp__coderef-docs__add_changelog_entry

   mcp__docs-mcp__record_changes
   → mcp__coderef-docs__record_changes

   mcp__docs-mcp__generate_quickref_interactive
   → mcp__coderef-docs__generate_quickref_interactive

   mcp__docs-mcp__establish_standards
   → mcp__coderef-docs__establish_standards

   mcp__docs-mcp__audit_codebase
   → mcp__coderef-docs__audit_codebase

   mcp__docs-mcp__check_consistency
   → mcp__coderef-docs__check_consistency
   ```

4. **Examples & Code Blocks (50+ instances):**
   ```python
   await mcp__docs-mcp__list_templates()
   → await mcp__coderef-docs__list_templates()

   mcp__docs-mcp__get_changelog(project_path="...")
   → mcp__coderef-docs__get_changelog(project_path="...")
   (all similar function calls)
   ```

5. **Slash Commands Section:**
   ```markdown
   Use these tools when:
   - User asks to "generate documentation" or "create a README"
   - ...

   Available in your tool palette as:
   - `mcp__docs-mcp__list_templates`
   (all 11 tool names)
   → Update all to mcp__coderef-docs__*
   ```

6. **Version Information (Line ~3800+):**
   ```markdown
   **Current Version**: 2.9.0
   **Maintainers**: willh, Claude Code AI

   When referencing docs-mcp:
   → When referencing coderef-docs:
   ```

### user-guide.md
- Search for all "docs-mcp" references
- Update tool names (mcp__docs-mcp__* → mcp__coderef-docs__*)

### my-guide.md (if exists)
- Search for "docs-mcp"
- Update tool names

### ARCHITECTURE.md (if exists)
- Search for "docs-mcp"
- Update references

---

## 4. SLASH COMMANDS (.claude/commands/*.md) (10+ files)

Each command file that mentions the server:

```markdown
/list-templates
→ Ensure description doesn't hardcode "docs-mcp"

/generate-docs
→ Update any "docs-mcp" references in command body

/create-plan
→ Change mcp__docs-mcp__ references to mcp__coderef-docs__

... (for all ~10-15 command files)
```

### .claude/commands.json
```json
Update server configuration object for "docs-mcp"
→ Change to "coderef-docs"
```

---

## 5. TEST FILES (3+ files)

### conftest.py
```python
Search for "docs-mcp" in:
- Fixture names
- Configuration
- Setup/teardown code
```

### tests/unit/test_server.py
```python
Example changes:
def test_server_initialization():
    from server import app
    # If there's a reference to "docs-mcp", update it
```

### Other test files
- Search all test files in tests/ for "docs-mcp"
- Update any hardcoded server names in assertions

---

## 6. WORKORDER & HISTORY FILES (2 files)

### coderef/workorder-log.txt
```
Example line:
WO-SOMETHING-001 | docs-mcp | Some work | 2025-12-23T...

→ WO-SOMETHING-001 | coderef-docs | Some work | 2025-12-23T...
```

### coderef/CHANGELOG.json
```json
{
  "entries": [
    {
      "version": "2.0.0",
      "changes": [
        {
          "title": "Changelog Refactor for docs-mcp",
          "description": "..."
        }
      ]
    }
  ]
}

→ Update "docs-mcp" references to "coderef-docs"
→ Add new entry for the rename at top:
  {
    "version": "2.0.1",
    "date": "2025-12-23",
    "changes": [{
      "type": "breaking_change",
      "severity": "major",
      "title": "Rename MCP server from docs-mcp to coderef-docs",
      "description": "Server renamed from 'docs-mcp' to 'coderef-docs' for better clarity",
      "files": ["server.py", "pyproject.toml", "CLAUDE.md", ...],
      "reason": "Better naming to reflect code documentation focus",
      "impact": "Tool names change from mcp__docs-mcp__* to mcp__coderef-docs__*",
      "breaking": true,
      "migration": "Update any hardcoded references from mcp__docs-mcp__* to mcp__coderef-docs__*"
    }]
  }
```

---

## 7. GIT & CI/CD (if applicable)

### .gitignore
- Verify no "docs-mcp" specific patterns

### .github/workflows/ (if exists)
```yaml
- name: Test docs-mcp
  → - name: Test coderef-docs

  working-directory: ./docs-mcp
  → working-directory: ./coderef-docs
```

---

## 8. DIRECTORY RENAME (FINAL STEP)

```bash
# Current structure:
~/.mcp-servers/
├── docs-mcp/               ← RENAME THIS
│   ├── server.py
│   ├── pyproject.toml
│   ├── .claude/
│   ├── coderef/
│   └── ...
├── coderef-mcp/
├── personas-mcp/
└── ...

# Target structure:
~/.mcp-servers/
├── coderef-docs/           ← NEW NAME
│   ├── server.py
│   ├── pyproject.toml
│   ├── .claude/
│   ├── coderef/
│   └── ...
├── coderef-mcp/
├── personas-mcp/
└── ...
```

---

## 9. QUICK REFERENCE: Find & Replace

Use your editor's find & replace (case-sensitive):

| Find | Replace | Count |
|------|---------|-------|
| `docs-mcp` | `coderef-docs` | ~100+ |
| `mcp__docs-mcp__` | `mcp__coderef-docs__` | ~200+ |
| `docs_mcp` | `coderef_docs` | ~10+ |
| `"docs-mcp"` | `"coderef-docs"` | ~50+ |
| `'docs-mcp'` | `'coderef-docs'` | ~20+ |

---

## 10. VERIFICATION CHECKLIST

After making all changes:

- [ ] `uv build` succeeds
- [ ] `python -c "import server; import asyncio; tools = asyncio.run(server.list_tools()); print(len(tools))"` outputs 11
- [ ] `pytest tests/unit/generators/ -q` shows 318 passed
- [ ] Server starts: `python server.py` (no errors)
- [ ] All tool names are `mcp__coderef-docs__*`
- [ ] README.md reflects new name
- [ ] CLAUDE.md has no `mcp__docs-mcp__` references
- [ ] pyproject.toml has `name = "coderef-docs"`
- [ ] All documentation updated
- [ ] Git status shows only intended changes

---

## 11. FILES SUMMARY

**Total files affected: 30+**

### By Phase:
- Phase 1 (Python): 6 files
- Phase 2 (Config): 2 files
- Phase 3 (Generators): 4 files (contained in phase 1-2)
- Phase 4 (Docs): 5 files
- Phase 5 (Commands): 10+ files
- Phase 6 (Tests): 3+ files
- Phase 7 (History): 2 files
- Phase 8 (Git): 2-3 files
- Phase 9 (Directory): 1 (directory move)

### By Impact:
- **CRITICAL** (must change): server.py, pyproject.toml, CLAUDE.md, README.md, .claude/commands/
- **HIGH** (should change): All Python files, all documentation, all tests
- **MEDIUM** (should verify): Git config, CI/CD, workorder logs
- **LOW** (nice to have): Version bump, changelog entry

---

## Estimated Effort

- **File Search & Identify:** 10 min
- **Python Changes:** 10-15 min
- **Config Changes:** 5 min
- **Documentation:** 30-45 min (mostly CLAUDE.md)
- **Commands:** 10 min
- **Tests:** 10 min
- **Verification:** 10 min
- **Git Commit & Push:** 5 min

**Total: 90-150 minutes**
