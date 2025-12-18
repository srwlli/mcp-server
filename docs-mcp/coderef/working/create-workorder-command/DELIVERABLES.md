# DELIVERABLES: create-workorder-command

**Project**: docs-mcp
**Feature**: create-workorder-command
**Workorder**: WO-CREATE-WORKORDER-COMMAND-001
**Status**: 🚧 Not Started
**Generated**: 2025-12-17

---

## Executive Summary

**Goal**: Rename command for clarity and add automatic logging to both local project AND orchestrator's workorder-log.txt for central tracking

**Description**: TBD

---

## Implementation Phases

### Phase 1: Rename & Constants

**Description**: Rename command and add orchestrator path constant

**Estimated Duration**: TBD

**Deliverables**:
- create-workorder.md exists
- OrchestratorPaths in constants.py

### Phase 2: Dual Logging

**Description**: Modify log_workorder for dual logging and call in create_plan

**Estimated Duration**: TBD

**Deliverables**:
- log_workorder writes to both paths
- create_plan calls log_workorder

### Phase 3: Documentation

**Description**: Update all references in CLAUDE.md

**Estimated Duration**: TBD

**Deliverables**:
- CLAUDE.md updated


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

- [ ] [CMD-001] Rename start-feature.md to create-workorder.md
- [ ] [CMD-002] Add OrchestratorPaths class to constants.py with ROOT path
- [ ] [CMD-003] Modify handle_log_workorder() to also write to orchestrator path
- [ ] [CMD-004] Add log_workorder call in handle_create_plan() after plan.json creation
- [ ] [CMD-005] Update CLAUDE.md references from /start-feature to /create-workorder

---

## Files Created/Modified

- **.claude/commands/start-feature.md** - TBD
- **constants.py** - TBD
- **tool_handlers.py** - TBD
- **CLAUDE.md** - TBD

---

## Success Criteria

- /create-workorder command works
- Workorder logged to local coderef/workorder-log.txt
- Workorder logged to orchestrator coderef/workorder-log.txt

---

## Notes

*This deliverables report was automatically generated from plan.json.*
*Use `/update-deliverables` to populate metrics from git history after implementation.*

**Last Updated**: 2025-12-17
