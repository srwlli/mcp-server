# Server Rename Planning Summary

**Workorder:** WO-RENAME-DOCS-MCP-TO-CODEREF-DOCS-001
**Status:** Planning Complete - Ready for Implementation
**Feature:** rename-docs-mcp-to-coderef-docs

---

## Overview

Complete systematic rename of the MCP server from **docs-mcp** to **coderef-docs** across all files, configurations, and documentation.

---

## Key Documents Created

1. **RENAME_CHECKLIST.md** - Detailed checklist organized by phases
2. **DETAILED_CHANGES.md** - Exact line-by-line changes for every file
3. **SUMMARY.md** - This document

---

## Quick Facts

| Metric | Value |
|--------|-------|
| **Files to Change** | 30+ |
| **Find/Replace Operations** | 6 patterns |
| **Python Files** | 6 |
| **Documentation Files** | 5+ |
| **Slash Command Files** | 10+ |
| **Test Files** | 3+ |
| **Configuration Files** | 2 |
| **Total Occurrences of "docs-mcp"** | 300+ |
| **Total Occurrences of "mcp__docs-mcp__"** | 200+ |
| **Estimated Time** | 90-150 minutes |
| **Risk Level** | LOW (systematic, easily reversible) |

---

## Implementation Strategy

### Phase Order (Recommended)

1. **Phase 1:** Update Python Core Files (server.py, tool_handlers.py, etc.)
2. **Phase 2:** Update Configuration Files (pyproject.toml, commands.json)
3. **Phase 3:** Update Documentation (README.md, CLAUDE.md, etc.)
4. **Phase 4:** Update Slash Commands
5. **Phase 5:** Update Tests
6. **Phase 6:** Update Workorder/History Files
7. **Phase 7:** Update Git/CI Config
8. **Phase 8:** Rename Directory
9. **Phase 9:** Verification
10. **Phase 10:** Git Commit & Push

---

## Critical Changes

### Tool Names (Most Important)
Every MCP tool changes from:
```
mcp__docs-mcp__<tool_name>
```
to:
```
mcp__coderef-docs__<tool_name>
```

**All 11 tools affected:**
- list_templates
- get_template
- generate_foundation_docs
- generate_individual_doc
- get_changelog
- add_changelog_entry
- record_changes
- generate_quickref_interactive
- establish_standards
- audit_codebase
- check_consistency

### Configuration Changes
- **pyproject.toml:** `name = "docs-mcp"` → `name = "coderef-docs"`
- **server.py:** `Server("docs-mcp")` → `Server("coderef-docs")`
- **CLAUDE.md:** ~200 tool name references (most extensive)

### Breaking Change
This is a **BREAKING CHANGE** because:
- Old tool names (mcp__docs-mcp__*) will no longer work
- Any hardcoded references must be updated
- MCP server configuration will need updating

---

## Verification Steps

After completing all changes, run these checks:

```bash
# 1. Build succeeds
cd ~/.mcp-servers/coderef-docs
uv build
# Expected: Both .tar.gz and .whl built successfully

# 2. Tool count correct
python -c "import asyncio, server; print(len(asyncio.run(server.list_tools())))"
# Expected: 11

# 3. All tests pass
pytest tests/unit/generators/ -q
# Expected: 318 passed

# 4. Server starts
python server.py
# Expected: "MCP server starting" in logs

# 5. Verify no old references
grep -r "docs-mcp" --include="*.py" --include="*.md" .
# Expected: No matches (except in git history/comments)
```

---

## Find & Replace Patterns

For your text editor (case-sensitive):

```
Pattern 1: docs-mcp (whole word)
→ Replace with: coderef-docs
→ Expected matches: ~100+

Pattern 2: mcp__docs-mcp__
→ Replace with: mcp__coderef-docs__
→ Expected matches: ~200+

Pattern 3: docs_mcp (Python imports)
→ Replace with: coderef_docs
→ Expected matches: ~10+

Pattern 4: "docs-mcp"
→ Replace with: "coderef-docs"
→ Expected matches: ~50+

Pattern 5: 'docs-mcp'
→ Replace with: 'coderef-docs'
→ Expected matches: ~20+
```

---

## Safety Precautions

1. **Keep old directory until verification complete**
   - Don't delete ~/.mcp-servers/docs-mcp/ immediately
   - After successful verification, safe to remove

2. **Commit to git before making changes**
   - Easy to revert if needed
   - All changes tracked in git history

3. **Run tests after each major phase**
   - Identify issues early
   - Don't wait until end to discover problems

4. **Verify on actual MCP client**
   - Test with Claude Code or other MCP client
   - Ensure tools are discoverable and functional

---

## Migration Guide for Users

When users upgrade from docs-mcp to coderef-docs:

### MCP Client Configuration

**Before (docs-mcp):**
```json
{
  "mcpServers": {
    "docs-mcp": {
      "command": "python",
      "args": ["~/.mcp-servers/docs-mcp/server.py"]
    }
  }
}
```

**After (coderef-docs):**
```json
{
  "mcpServers": {
    "coderef-docs": {
      "command": "python",
      "args": ["~/.mcp-servers/coderef-docs/server.py"]
    }
  }
}
```

### Tool References

**Before:**
```python
mcp__docs-mcp__get_changelog(...)
mcp__docs-mcp__add_changelog_entry(...)
```

**After:**
```python
mcp__coderef-docs__get_changelog(...)
mcp__coderef-docs__add_changelog_entry(...)
```

---

## Timeline

| Phase | Duration | Cumulative |
|-------|----------|-----------|
| Phase 1 (Python) | 10-15 min | 10-15 min |
| Phase 2 (Config) | 5 min | 15-20 min |
| Phase 3 (Docs) | 30-45 min | 45-65 min |
| Phase 4 (Commands) | 10 min | 55-75 min |
| Phase 5 (Tests) | 10 min | 65-85 min |
| Phase 6 (History) | 5 min | 70-90 min |
| Phase 7 (Git) | 5 min | 75-95 min |
| Phase 8 (Directory) | 2 min | 77-97 min |
| Phase 9 (Verify) | 10 min | 87-107 min |
| Phase 10 (Commit) | 5 min | 92-112 min |

**Total: 90-150 minutes (1.5-2.5 hours)**

---

## Files Included in Planning

1. **coderef/working/rename-docs-mcp-to-coderef-docs/context.json** - Requirements & constraints
2. **coderef/working/rename-docs-mcp-to-coderef-docs/RENAME_CHECKLIST.md** - Phase-by-phase checklist
3. **coderef/working/rename-docs-mcp-to-coderef-docs/DETAILED_CHANGES.md** - Exact file-by-file changes
4. **coderef/working/rename-docs-mcp-to-coderef-docs/SUMMARY.md** - This document

---

## Next Steps

When ready to proceed:

1. Review the **RENAME_CHECKLIST.md** to understand all phases
2. Review **DETAILED_CHANGES.md** for specific changes needed
3. Execute phases in order, using this summary as a guide
4. Run verification checks after each major phase
5. Once all changes complete and verified, rename directory
6. Commit all changes to git
7. Push to remote

---

## Questions/Clarifications

Before starting implementation, confirm:

1. ✓ Directory path: ~/.mcp-servers/docs-mcp → ~/.mcp-servers/coderef-docs
2. ✓ Server name in code: docs-mcp → coderef-docs
3. ✓ Tool names: mcp__docs-mcp__* → mcp__coderef-docs__*
4. ✓ Scope: All files in directory + related configs (~30+ files)
5. ✓ Breaking change: Yes, old tool names won't work
6. ✓ Backward compatibility: No, clean rename (better approach)
7. ✓ Git handling: Keep full history (no force push)
8. ✓ Delete old directory after: Yes (after verification)

---

## Ready Status

✅ **Planning Complete**
- All changes identified
- All files documented
- All phases structured
- Timeline estimated
- Verification plan ready

**Ready to execute on your go-ahead!**
