# DELIVERABLES: remove-obsolete-inventory-tools

**Project**: docs-mcp
**Feature**: remove-obsolete-inventory-tools
**Workorder**: WO-REMOVE-OBSOLETE-INVENTORY-TOOLS-001
**Status**: 🚧 Not Started
**Generated**: 2025-12-19

---

## Executive Summary

**Goal**: Clean up codebase by removing redundant tools whose functionality is now fully covered by coderef_foundation_docs

**Description**: Remove 7 obsolete inventory tools (api_inventory, database_inventory, dependency_inventory, config_inventory, test_inventory, inventory_manifest, documentation_inventory) that have been replaced by the unified coderef_foundation_docs tool

---

## Implementation Phases

### Phase 1: Remove Handler Functions

**Description**: Remove 7 handler functions and registry entries from tool_handlers.py

**Estimated Duration**: TBD

**Deliverables**:
- tool_handlers.py cleaned up
- TOOL_HANDLERS registry updated

### Phase 2: Remove Tool Schemas

**Description**: Remove 7 Tool() definitions from server.py

**Estimated Duration**: TBD

**Deliverables**:
- server.py cleaned up
- Tool count reduced from 32 to 25

### Phase 3: Remove Slash Commands

**Description**: Delete 7 slash command files from .claude/commands/

**Estimated Duration**: TBD

**Deliverables**:
- 7 slash command files deleted

### Phase 4: Update Documentation & Test

**Description**: Update all documentation and verify workflows still work

**Estimated Duration**: TBD

**Deliverables**:
- Documentation updated
- Workflows verified working


---

## Metrics

### Code Changes
- **Lines of Code Added**: TBD
- **Lines of Code Deleted**: TBD
- **Net LOC**: TBD
- **Files Modified**: TBD

### Commit Activity
- **Total Commits**: TBD
- **First Commit**: TBD
- **Last Commit**: TBD
- **Contributors**: TBD

### Time Investment
- **Days Elapsed**: TBD
- **Hours Spent (Wall Clock)**: TBD

---

## Task Completion Checklist

- [ ] [REMOVE-001] Remove handle_api_inventory from tool_handlers.py
- [ ] [REMOVE-002] Remove handle_database_inventory from tool_handlers.py
- [ ] [REMOVE-003] Remove handle_dependency_inventory from tool_handlers.py
- [ ] [REMOVE-004] Remove handle_config_inventory from tool_handlers.py
- [ ] [REMOVE-005] Remove handle_test_inventory from tool_handlers.py
- [ ] [REMOVE-006] Remove handle_inventory_manifest from tool_handlers.py
- [ ] [REMOVE-007] Remove handle_documentation_inventory from tool_handlers.py
- [ ] [REMOVE-008] Remove 7 entries from TOOL_HANDLERS registry in tool_handlers.py
- [ ] [REMOVE-009] Remove api_inventory Tool() definition from server.py
- [ ] [REMOVE-010] Remove database_inventory Tool() definition from server.py
- [ ] [REMOVE-011] Remove dependency_inventory Tool() definition from server.py
- [ ] [REMOVE-012] Remove config_inventory Tool() definition from server.py
- [ ] [REMOVE-013] Remove test_inventory Tool() definition from server.py
- [ ] [REMOVE-014] Remove inventory_manifest Tool() definition from server.py
- [ ] [REMOVE-015] Remove documentation_inventory Tool() definition from server.py
- [ ] [REMOVE-016] Delete .claude/commands/api-inventory.md
- [ ] [REMOVE-017] Delete .claude/commands/database-inventory.md
- [ ] [REMOVE-018] Delete .claude/commands/dependency-inventory.md
- [ ] [REMOVE-019] Delete .claude/commands/config-inventory.md
- [ ] [REMOVE-020] Delete .claude/commands/test-inventory.md
- [ ] [REMOVE-021] Delete .claude/commands/inventory-manifest.md
- [ ] [REMOVE-022] Delete .claude/commands/documentation-inventory.md
- [ ] [DOC-001] Update CLAUDE.md to remove old tool documentation and add migration guide
- [ ] [DOC-002] Update README.md tool count (32 tools → 25 tools)
- [ ] [DOC-003] Update user-guide.md to remove old tool references
- [ ] [TEST-001] Verify coderef_foundation_docs still works after removal
- [ ] [TEST-002] Verify /create-workorder workflow still functions

---

## Files Created/Modified

- **tool_handlers.py** - TBD
- **server.py** - TBD
- **TOOL_HANDLERS registry** - TBD
- **CLAUDE.md** - TBD
- **README.md** - TBD
- **user-guide.md** - TBD

---

## Success Criteria

- All 7 tool handlers removed from tool_handlers.py
- All 7 tool schemas removed from server.py
- All 7 slash commands deleted
- TOOL_HANDLERS registry has exactly 25 entries
- /coderef-foundation-docs works correctly
- /create-workorder workflow completes successfully

---

## Notes

*This deliverables report was automatically generated from plan.json.*
*Use `/update-deliverables` to populate metrics from git history after implementation.*

**Last Updated**: 2025-12-19
