# DELIVERABLES: archive-mcp-servers

**Project**: .mcp-servers
**Feature**: archive-mcp-servers
**Workorder**: WO-ARCHIVE-MCP-SERVERS-001
**Status**: 🚧 Not Started
**Generated**: 2025-12-24

---

## Executive Summary

**Goal**: TBD

**Description**: Reduces maintenance burden by removing deprecated servers and consolidating around core servers

---

## Implementation Phases

### Phase 1: Configuration & Validation

**Description**: Update .mcp.json and verify no hidden dependencies

**Estimated Duration**: TBD

**Deliverables**:
- Updated .mcp.json with 4 active servers
- Dependency search report

### Phase 2: Directory Archival

**Description**: Move server directories to archived/ folder

**Estimated Duration**: TBD

**Deliverables**:
- archived/ folder with all server directories
- Integrity verification report

### Phase 3: Git Commit

**Description**: Update git repository with archival

**Estimated Duration**: TBD

**Deliverables**:
- Clean git commit with archival changes


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

- [ ] [CONFIG-001] Read current .mcp.json and identify entries for removal
- [ ] [CONFIG-002] Remove archived server entries from .mcp.json
- [ ] [CONFIG-003] Validate .mcp.json syntax
- [ ] [SEARCH-001] Search codebase for references to archived servers
- [ ] [ARCHIVE-001] Create archived/ directory structure
- [ ] [ARCHIVE-002] Move server directories to archived/
- [ ] [ARCHIVE-003] Verify all files archived correctly
- [ ] [GIT-001] Remove archived directories from git tracking
- [ ] [GIT-002] Create commit with archival message

---

## Files Created/Modified

- **C:\Users\willh\.claude\.mcp.json** - Remove: coderef, hello-world, scriptboard-mcp, chrome-devtools

---

## Success Criteria

- No success criteria defined

---

## Notes

*This deliverables report was automatically generated from plan.json.*
*Use `/update-deliverables` to populate metrics from git history after implementation.*

**Last Updated**: 2025-12-24
