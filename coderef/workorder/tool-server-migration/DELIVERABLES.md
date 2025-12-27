# Tool Server Migration - DELIVERABLES

**Workorder**: WO-TOOL-MIGRATION-001
**Feature**: tool-server-migration
**Status**: Planning
**Created**: 2025-12-26

---

## Project Scope

Migrate 18 tools from coderef-docs (deprecated) to coderef-workflow (correct home), keeping 5 agent coordination tools in coderef-docs. Update all 65+ command files to reference correct server.

---

## Phase Progress

### Phase 1: Planning Tools (8/8)
- [ ] PLAN-001: get_planning_template
- [ ] PLAN-002: analyze_project_for_planning
- [ ] PLAN-003: gather_context
- [ ] PLAN-004: create_plan
- [ ] PLAN-005: validate_implementation_plan
- [ ] PLAN-006: generate_plan_review_report
- [ ] PLAN-007: generate_deliverables_template
- [ ] PLAN-008: generate_handoff_context

**Progress**: 0/8 (0%)

### Phase 2: Execution Tools (2/2)
- [ ] EXEC-001: execute_plan
- [ ] EXEC-002: update_task_status

**Progress**: 0/2 (0%)

### Phase 3: Archive Tools (1/1)
- [ ] ARCH-001: archive_feature

**Progress**: 0/1 (0%)

### Phase 4: Admin Tools (6/6)
- [ ] ADMIN-001: log_workorder
- [ ] ADMIN-002: get_workorder_log
- [ ] ADMIN-003: update_all_documentation
- [ ] ADMIN-004: audit_plans
- [ ] ADMIN-005: coderef_foundation_docs
- [ ] ADMIN-006: generate_features_inventory

**Progress**: 0/6 (0%)

### Phase 5: Command Updates (4/4)
- [ ] CMD-001: Audit all command files
- [ ] CMD-002: Create replacement plan
- [ ] CMD-003: Execute bulk updates
- [ ] CMD-004: Verify no malformed references

**Progress**: 0/4 (0%)

### Phase 6: Testing (3/3)
- [ ] TEST-001: Tool invocation tests
- [ ] TEST-002: Verify no duplicates
- [ ] TEST-003: End-to-end workflow test

**Progress**: 0/3 (0%)

### Phase 7: Documentation (2/2)
- [ ] DOC-001: Update coderef-docs comments
- [ ] DOC-002: Update coderef-workflow comments

**Progress**: 0/2 (0%)

### Phase 8: Final (1/1)
- [ ] FINAL-001: Commit and push

**Progress**: 0/1 (0%)

---

## Overall Progress

**Total Tasks**: 27
**Completed**: 0
**In Progress**: 0
**Remaining**: 27
**Completion Rate**: 0%

---

## Metrics

### Code Changes
- **Tools to migrate**: 18
- **Command files to update**: ~40+
- **Lines of code modified**: (To be tracked)
- **Git commits**: ~18-20 (one per tool + bulk updates)

### Time Tracking
- **Start Date**: 2025-12-26
- **Estimated Completion**: (To be updated)
- **Total Time Spent**: 0 hours
- **Current Phase**: Planning

---

## Key Deliverables

- [ ] All 18 tools migrated to correct servers
- [ ] All 65+ command files use correct server references
- [ ] Zero duplicate tool registrations
- [ ] All tools tested and functional
- [ ] Updated server.py documentation
- [ ] Clean git history with clear commits
- [ ] /create-plan and /create-workorder working without duplicates

---

## Notes

- One tool at a time (not bulk migration)
- Test each tool after migration
- Keep agent coordination tools in coderef-docs
- Update command files as tools are moved
- Clear git commit trail for audit trail

---

**Generated**: 2025-12-26 19:30:00Z
**Version**: 1.0.0
