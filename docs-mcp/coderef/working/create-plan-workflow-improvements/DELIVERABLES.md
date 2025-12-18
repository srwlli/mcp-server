# DELIVERABLES: create-plan-workflow-improvements

**Project**: docs-mcp
**Feature**: create-plan-workflow-improvements
**Workorder**: WO-CREATE-PLAN-WORKFLOW-IMPROVEMENTS-001
**Status**: 🚧 Not Started
**Generated**: 2025-12-17

---

## Executive Summary

**Goal**: Make the create-plan workflow robust, consistent, and fully trackable from start (gather-context) to finish (archive-feature) with proper enforcement, progress tracking, git integration, and standardized feature documentation

**Description**: TBD

---

## Implementation Phases

### Phase 1: Foundation - Timestamps & Enforcement

**Description**: Add timestamps to all outputs and create plan format validation

**Estimated Duration**: TBD

**Deliverables**:
- Timestamp wrapper function
- All tool outputs include timestamp field
- plan_format_validator.py created
- Lloyd strict_mode flag added
- CLAUDE.md updated with enforcement rules

### Phase 2: Progress Tracking & Audit

**Description**: Enable task status tracking and plan audit capabilities

**Estimated Duration**: TBD

**Deliverables**:
- update_task_status tool working
- Plan template includes progress instructions
- audit_plans tool scans all plans
- /audit-plans slash command available

### Phase 3: Git Workflow & Testing

**Description**: Add git integration and optional incremental testing

**Estimated Duration**: TBD

**Deliverables**:
- /start-feature commits planning artifacts
- /git-release command available
- verify_step field in task schema

### Phase 4: Handoff & Inventory

**Description**: Standardize multi-agent handoff and create features inventory

**Estimated Duration**: TBD

**Deliverables**:
- Handoff prompt template in communication.json
- Handoff protocol documented
- features_inventory_generator working
- features.md template created
- generate_features_inventory tool available

### Phase 5: Documentation & Polish

**Description**: Final documentation and naming considerations

**Estimated Duration**: TBD

**Deliverables**:
- Complete workflow documentation in CLAUDE.md
- Naming considerations documented for future


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

- [ ] [TS-001] Add timestamp wrapper function to tool_handlers.py
- [ ] [TS-002] Update all handler responses to include timestamp field
- [ ] [ENF-001] Create plan_format_validator.py with validate_plan_format()
- [ ] [ENF-002] Update Lloyd persona with strict_mode flag
- [ ] [ENF-003] Document plan.json enforcement in CLAUDE.md
- [ ] [PROG-001] Add update_task_status tool to tool_handlers.py
- [ ] [PROG-002] Register update_task_status in server.py
- [ ] [PROG-003] Add progress tracking instructions to plan template
- [ ] [AUDIT-001] Create audit_plans tool to scan all plan.json files
- [ ] [AUDIT-002] Register audit_plans in server.py
- [ ] [AUDIT-003] Create /audit-plans slash command
- [ ] [GIT-001] Update /start-feature to commit planning artifacts
- [ ] [GIT-002] Create /git-release slash command
- [ ] [TEST-001] Add verify_step optional field to task schema
- [ ] [HAND-001] Add handoff_prompt_template to communication.json schema
- [ ] [HAND-002] Document standard handoff protocol in CLAUDE.md
- [ ] [INV-001] Create features_inventory_generator.py
- [ ] [INV-002] Create features.md.template
- [ ] [INV-003] Add generate_features_inventory tool to tool_handlers.py
- [ ] [INV-004] Register generate_features_inventory in server.py
- [ ] [DOC-001] Update CLAUDE.md with complete workflow documentation
- [ ] [DOC-002] Document naming considerations for future (STUB-041)

---

## Files Created/Modified

- **docs-mcp/generators/features_inventory_generator.py** - Generate features.md for projects
- **docs-mcp/templates/features.md.template** - Template for features.md generation
- **docs-mcp/.claude/commands/git-release.md** - Git workflow slash command
- **docs-mcp/.claude/commands/audit-plans.md** - Plan audit slash command
- **docs-mcp/validation/plan_format_validator.py** - Validate plan.json format enforcement
- **docs-mcp/tool_handlers.py** - TBD
- **docs-mcp/server.py** - TBD
- **docs-mcp/CLAUDE.md** - TBD
- **docs-mcp/generators/planning_generator.py** - TBD
- **personas-mcp/personas/base/lloyd.json** - TBD
- **docs-mcp/.claude/commands/start-feature.md** - TBD
- **docs-mcp/context/planning-template-for-ai.json** - TBD

---

## Success Criteria

- No success criteria defined

---

## Notes

*This deliverables report was automatically generated from plan.json.*
*Use `/update-deliverables` to populate metrics from git history after implementation.*

**Last Updated**: 2025-12-17
