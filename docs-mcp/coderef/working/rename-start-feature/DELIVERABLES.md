# DELIVERABLES: rename-start-feature

**Project**: docs-mcp
**Feature**: rename-start-feature
**Workorder**: WO-RENAME-START-FEATURE-001
**Status**: 🚧 Not Started
**Generated**: 2025-12-18

---

## Executive Summary

**Goal**: Ensure consistent naming across all documentation, personas, and references. The term 'workorder' better reflects the orchestrator pattern and aligns with the workorder-log tracking system.

**Description**: Rename /start-feature slash command references to /create-workorder for clearer intent and alignment with orchestrator terminology. This is a documentation/reference cleanup - the actual /create-workorder command already exists and is fully implemented.

---

## Implementation Phases

### Phase 1: Research and Planning

**Description**: Identify all files requiring updates

**Estimated Duration**: TBD

**Deliverables**:
- List of files with start-feature references

### Phase 2: Core Updates

**Description**: Update Lloyd persona and primary documentation

**Estimated Duration**: TBD

**Deliverables**:
- Updated lloyd.json
- Updated LLOYD-REFERENCE.md
- Updated MCP-ECOSYSTEM-REFERENCE.md

### Phase 3: Documentation Sweep

**Description**: Update remaining documentation files

**Estimated Duration**: TBD

**Deliverables**:
- Updated user-guide.md
- Updated supporting docs

### Phase 4: Verification

**Description**: Verify all references updated correctly

**Estimated Duration**: TBD

**Deliverables**:
- Verification report confirming no remaining references


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

- [ ] [SEARCH-001] Search for all 'start-feature' references in codebase
- [ ] [LLOYD-001] Update lloyd.json expertise list: change '/start-feature workflow orchestration' to '/create-workorder workflow orchestration'
- [ ] [LLOYD-002] Update lloyd.json system_prompt: replace all '/start-feature' with '/create-workorder'
- [ ] [DOCS-001] Update LLOYD-REFERENCE.md: replace all '/start-feature' with '/create-workorder'
- [ ] [DOCS-002] Update MCP-ECOSYSTEM-REFERENCE.md: replace all '/start-feature' with '/create-workorder'
- [ ] [DOCS-003] Update user-guide.md: replace all '/start-feature' with '/create-workorder'
- [ ] [DOCS-004] Update QUICK-START.md, my-guide.md, and other docs-mcp markdown files
- [ ] [VERIFY-001] Run grep to verify no remaining 'start-feature' references (except archived/working folders)

---

## Files Created/Modified

- **personas-mcp/personas/base/lloyd.json** - TBD
- **personas-mcp/docs/LLOYD-REFERENCE.md** - TBD
- **personas-mcp/docs/MCP-ECOSYSTEM-REFERENCE.md** - TBD
- **docs-mcp/user-guide.md** - TBD
- **docs-mcp/QUICK-START.md** - TBD
- **docs-mcp/my-guide.md** - TBD
- **docs-mcp/COMPREHENSIVE-review.md** - TBD
- **docs-mcp/.claude/commands.json** - TBD
- **docs-mcp/coderef/working/README.md** - TBD

---

## Success Criteria

- No success criteria defined

---

## Notes

*This deliverables report was automatically generated from plan.json.*
*Use `/update-deliverables` to populate metrics from git history after implementation.*

**Last Updated**: 2025-12-18
