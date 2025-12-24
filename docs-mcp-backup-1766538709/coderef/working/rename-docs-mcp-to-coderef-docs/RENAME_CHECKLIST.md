# Server Rename: docs-mcp → coderef-docs

**Workorder:** WO-RENAME-DOCS-MCP-TO-CODEREF-DOCS-001
**Status:** Planning Complete
**Scope:** Systematic rename across all files and systems

---

## Phase 1: Python Core Files (High Priority)

### [ ] 1.1 server.py
- **Line 1-13:** Update module docstring "docs-mcp" → "coderef-docs"
- **Line 62:** Change `Server("docs-mcp")` → `Server("coderef-docs")`
- **Lines 16, 20, 22:** Update version references if needed

### [ ] 1.2 tool_handlers.py
- Search for any hardcoded "docs-mcp" strings in:
  - Error messages
  - Logging statements
  - Comments/docstrings

### [ ] 1.3 constants.py
- Check if any constants reference "docs-mcp"
- Update any path configurations

### [ ] 1.4 logger_config.py
- Check logger initialization for server name references

### [ ] 1.5 validation.py
- Update any error messages referencing "docs-mcp"

### [ ] 1.6 error_responses.py
- Check for server name references in error handling

---

## Phase 2: Configuration Files (High Priority)

### [ ] 2.1 pyproject.toml
- **[project]:** `name = "coderef-docs"` (was "docs-mcp")
- **[project.scripts]:** Update entry points if any reference "docs-mcp"
- **[tool.poetry]:** Update name and any references
- Check `homepage`, `repository`, `documentation` URLs

### [ ] 2.2 pyproject.toml version bump
- Update version (e.g., 2.0.0 → 2.0.1 or 2.1.0)
- Add entry to changelog

---

## Phase 3: Generator & Tool Files (Medium Priority)

### [ ] 3.1 generators/*.py
- Search for "docs-mcp" in:
  - generators/foundation_generator.py
  - generators/changelog_generator.py
  - generators/inventory_generators.py
  - generators/audit_generator.py

### [ ] 3.2 handler files
- tool_handlers.py (already checked in Phase 1)
- handler_decorators.py
- handler_helpers.py

---

## Phase 4: Documentation (High Priority)

### [ ] 4.1 README.md
- Update all references to "docs-mcp"
- Update installation instructions
- Update MCP server name in examples
- Update any links to coderef/docs-mcp/

### [ ] 4.2 CLAUDE.md (EXTENSIVE - ~3000+ lines)
- **Quick Reference:** "11 specialized tools for docs-mcp" → "11 specialized tools for coderef-docs"
- **System Architecture:** "docs-mcp" tool definitions → "coderef-docs"
- **Tool List:** Update `mcp__docs-mcp__*` references to `mcp__coderef-docs__*` throughout:
  - `mcp__docs-mcp__list_templates` → `mcp__coderef-docs__list_templates`
  - `mcp__docs-mcp__get_template` → `mcp__coderef-docs__get_template`
  - (14 total tool names to update)
- **Available in tool palette:** Update tool names
- **Slash Commands:** Update references in command descriptions
- **Tool Catalog:** Update all tool descriptions that reference "docs-mcp"
- **Examples:** Update code examples with new tool names
- **Usage Patterns:** Update examples
- **Design Patterns:** Update any references
- **Version Information:** Update "Current Version" and "Maintainers" section

### [ ] 4.3 user-guide.md
- Update all references to "docs-mcp"
- Update tool names in examples
- Update any installation/setup instructions

### [ ] 4.4 my-guide.md (if exists)
- Update references

### [ ] 4.5 ARCHITECTURE.md (if exists)
- Update references

---

## Phase 5: Slash Commands & Global Resources (Medium Priority)

### [ ] 5.1 .claude/commands/*.md
- Update command descriptions that mention "docs-mcp"
- Search for "docs-mcp" in all command files
- Update any references in command bodies

### [ ] 5.2 .claude/commands.json
- Update server references in commands registry
- Update any paths or configurations

### [ ] 5.3 Global Slash Commands (if deployed)
- Files in `~/.claude/commands/` that reference this server
- These would reference `mcp__docs-mcp__*` → `mcp__coderef-docs__*`

### [ ] 5.4 MCP Server Configuration
- Check `~/.mcp-servers/` configuration files
- Check `~/.claude/` configuration files
- Update any server discovery configurations

---

## Phase 6: Tests (Medium Priority)

### [ ] 6.1 conftest.py
- Update any fixtures or configurations referencing "docs-mcp"

### [ ] 6.2 tests/unit/
- Search all test files for "docs-mcp" references
- Update in:
  - test_server.py
  - test_tool_handlers.py
  - Any other test files

### [ ] 6.3 tests/integration/
- Update integration test references

---

## Phase 7: Workorder & History Files (Low-Medium Priority)

### [ ] 7.1 coderef/workorder-log.txt
- Update any existing entries that mention "docs-mcp"

### [ ] 7.2 coderef/CHANGELOG.json
- Update any changelog entries that reference "docs-mcp"
- Consider adding a new entry documenting the rename

### [ ] 7.3 coderef/CHANGELOG_TOOLS_REVIEW.md
- Update references if this file exists

---

## Phase 8: Git & Repository (Low Priority)

### [ ] 8.1 .gitignore
- Check for any patterns specific to "docs-mcp"

### [ ] 8.2 .github/ workflows (if any)
- Update any CI/CD references to "docs-mcp"

### [ ] 8.3 Remote configuration (if published)
- Update repository URLs if applicable

---

## Phase 9: Directory Rename (Critical - Do Last)

### [ ] 9.1 Move directory
```bash
# Option 1: Rename in place
mv ~/.mcp-servers/docs-mcp ~/.mcp-servers/coderef-docs

# Option 2: Copy, test, then delete
cp -r ~/.mcp-servers/docs-mcp ~/.mcp-servers/coderef-docs
# ... verify everything works ...
rm -rf ~/.mcp-servers/docs-mcp
```

### [ ] 9.2 Update any symlinks
- Check for any symlinks pointing to old directory

### [ ] 9.3 Update shell configurations
- Check .bashrc, .zshrc, etc. for any hardcoded paths

---

## Phase 10: Verification (Critical)

### [ ] 10.1 Build Test
```bash
cd ~/.mcp-servers/coderef-docs
uv build
```
✓ Both .tar.gz and .whl should build successfully

### [ ] 10.2 Server Discovery Test
```bash
python -c "import server; import asyncio; print(len(asyncio.run(server.list_tools())))"
```
✓ Should output: 11 tools

### [ ] 10.3 Tool Check
```bash
python -c "
import asyncio, server
tools = asyncio.run(server.list_tools())
names = [t.name for t in tools]
print('record_changes' in names)  # Should be True
print('update_changelog' in names)  # Should be False
"
```

### [ ] 10.4 Test Suite
```bash
pytest tests/unit/generators/ -q
```
✓ Should pass: 318 tests

### [ ] 10.5 MCP Server Start
```bash
python server.py
```
✓ Should start without errors
✓ Should log: "MCP server starting"

### [ ] 10.6 Check MCP Tool Names
Tools should be discoverable as:
- `mcp__coderef-docs__list_templates`
- `mcp__coderef-docs__get_template`
- `mcp__coderef-docs__generate_foundation_docs`
- `mcp__coderef-docs__generate_individual_doc`
- `mcp__coderef-docs__get_changelog`
- `mcp__coderef-docs__add_changelog_entry`
- `mcp__coderef-docs__record_changes`
- `mcp__coderef-docs__generate_quickref_interactive`
- `mcp__coderef-docs__establish_standards`
- `mcp__coderef-docs__audit_codebase`
- `mcp__coderef-docs__check_consistency`

---

## Phase 11: Git Commit & Push (Final)

### [ ] 11.1 Stage all changes
```bash
cd ~/.mcp-servers/coderef-docs
git add -A
```

### [ ] 11.2 Commit with message
```bash
git commit -m "refactor: Rename MCP server from docs-mcp to coderef-docs

BREAKING: Server name changed from 'docs-mcp' to 'coderef-docs'
- Updated all Python imports and references
- Updated documentation and examples
- Updated tool names (mcp__docs-mcp__* → mcp__coderef-docs__*)
- Updated configuration files
- All tests passing (318/318)
- All tools discoverable with new names

Migration:
- Old tool names (mcp__docs-mcp__*) no longer available
- Update any hardcoded references to use mcp__coderef-docs__*
- Update any MCP server configurations

Workorder: WO-RENAME-DOCS-MCP-TO-CODEREF-DOCS-001

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### [ ] 11.3 Push to remote
```bash
git push
```

---

## Summary of Changes

| Category | Count | Files |
|----------|-------|-------|
| Python files | 6+ | server.py, tool_handlers.py, constants.py, logger_config.py, validation.py, error_responses.py |
| Documentation | 5+ | README.md, CLAUDE.md, user-guide.md, my-guide.md, ARCHITECTURE.md |
| Configuration | 2 | pyproject.toml, .claude/commands.json |
| Tests | 3+ | conftest.py, test_server.py, test files with "docs-mcp" refs |
| Commands | 10+ | .claude/commands/*.md files |
| Workorder files | 2+ | workorder-log.txt, CHANGELOG.json |
| **Total files to update:** | **30+** | |

---

## Timeline Estimate

- **Phase 1 (Python):** 10-15 min
- **Phase 2 (Config):** 5 min
- **Phase 3 (Generators):** 5 min
- **Phase 4 (Documentation):** 30-45 min (CLAUDE.md is large)
- **Phase 5 (Slash Commands):** 10 min
- **Phase 6 (Tests):** 10 min
- **Phase 7 (History):** 5 min
- **Phase 8 (Git):** 5 min
- **Phase 9 (Directory):** 2 min
- **Phase 10 (Verification):** 10 min
- **Phase 11 (Commit):** 5 min

**Total: 90-150 minutes (1.5-2.5 hours)**

---

## Rollback Plan

If anything goes wrong:
1. Keep old `docs-mcp` directory until verification complete
2. If issues found, delete `coderef-docs` and rename back
3. Identify issue and retry
4. All changes in git, so easy to revert if needed

---

## Notes

- ✅ All 318 tests passing before rename
- ✅ Server version will be updated in CLAUDE.md
- ✅ Backward compatibility note in BREAKING section
- ✅ Clear migration path for users
- ❌ Old server name will NOT be available after rename (breaking change)

Ready to execute when you give the go-ahead!
