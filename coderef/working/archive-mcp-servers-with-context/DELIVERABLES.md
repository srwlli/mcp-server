# DELIVERABLES: archive-mcp-servers-with-context

**Project**: .mcp-servers
**Feature**: archive-mcp-servers-with-context
**Workorder**: WO-ARCHIVE-MCP-SERVERS-WITH-CONTEXT-001
**Status**: 🚧 Not Started
**Generated**: 2025-12-24

---

## Executive Summary

**Goal**: TBD

**Description**: Streamlines MCP ecosystem by removing redundant servers, reduces startup time, and eliminates maintenance of deprecated tools. Sets foundation for Phase 2 consolidation strategy.

---

## Implementation Phases

### Phase 1: Configuration Update

**Description**: Remove archived servers from .mcp.json auto-loading configuration

**Estimated Duration**: 1 hour

**Deliverables**:
- Updated .mcp.json with 4 active servers only
- Validation report confirming syntax correctness

### Phase 2: Directory Archival

**Description**: Move server directories to archived/ folder with metadata preservation

**Estimated Duration**: 1.5 hours

**Deliverables**:
- archived/coderef-mcp directory with all files
- archived/hello-world-mcp directory with all files
- archived/scriptboard-mcp directory with all files
- archive-metadata.json with server inventory

### Phase 3: Git Commit & Cleanup

**Description**: Update git repository to reflect archival and create audit trail

**Estimated Duration**: 1.25 hours

**Deliverables**:
- Clean git commit with impact analysis
- Archived servers removed from git tracking

### Phase 4: Documentation & Recovery

**Description**: Document archival rationale, recovery procedures, and migration path

**Estimated Duration**: 2.5 hours

**Deliverables**:
- ARCHIVAL_LOG.md with complete documentation
- Migration guide to coderef-context consolidation
- Updated README.md with server inventory


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

- [ ] [PREP-001] Verify all 4 servers have been analyzed and documented
- [ ] [CONFIG-001] Read current .mcp.json and identify entries for removal
- [ ] [CONFIG-002] Remove coderef, hello-world, scriptboard-mcp, chrome-devtools from .mcp.json
- [ ] [CONFIG-003] Validate .mcp.json syntax and remaining servers are correct
- [ ] [ARCHIVE-001] Create archived/ directory structure if it doesn't exist
- [ ] [ARCHIVE-002] Move coderef-mcp directory to archived/ folder
- [ ] [ARCHIVE-003] Move hello-world-mcp directory to archived/ folder
- [ ] [ARCHIVE-004] Move scriptboard-mcp directory to archived/ folder
- [ ] [ARCHIVE-005] Create archive-metadata.json with server info and archival timestamps
- [ ] [GIT-001] Remove archived server directories from git tracking
- [ ] [GIT-002] Stage .mcp.json changes for commit
- [ ] [GIT-003] Create detailed commit with impact analysis and archival rationale
- [ ] [DOCS-001] Create ARCHIVAL_LOG.md documenting rationale and recovery procedures
- [ ] [DOCS-002] Document migration path to coderef-context consolidation (Phase 2)
- [ ] [DOCS-003] Update README.md with current server inventory and archival summary

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
