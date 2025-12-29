# DELIVERABLES - uds-integration

**Workorder:** WO-UDS-INTEGRATION-001
**Feature:** Universal Document Standard (UDS) Integration
**Status:** IN_PROGRESS
**Started:** 2025-12-28

---

## Feature Summary

Implement Universal Document Standard (UDS) system that adds YAML frontmatter headers/footers to all workorder-generated documents (plan.json, DELIVERABLES.md, context.json, analysis.json, claude.md) with workorder_id, feature_id, status, timestamps, and review dates for better tracking, lifecycle management, and traceability.

---

## Implementation Phases

### Phase 1: UDS Template Creation ✓ COMPLETE
**Duration:** 30 minutes

- [x] SETUP-001: Create templates/uds/ directory structure
- [x] SETUP-002: Create templates/uds/header.yaml
- [x] SETUP-003: Create templates/uds/footer.yaml

### Phase 2: Helper Function Implementation
**Duration:** 45 minutes

- [ ] IMPL-001: Create uds_helpers.py with generate_uds_header()
- [ ] IMPL-002: Implement generate_uds_footer()
- [ ] IMPL-003: Implement get_server_version()

### Phase 3: Generator Integration
**Duration:** 1 hour

- [ ] IMPL-004: Update handle_gather_context() for context.json
- [ ] IMPL-005: Update planning_generator.py for plan.json
- [ ] IMPL-006: Update handle_generate_deliverables_template() for DELIVERABLES.md
- [ ] IMPL-007: Update handoff_generator.py for claude.md
- [ ] IMPL-008: Update handle_analyze_for_planning() for analysis.json

### Phase 4: Testing & Validation
**Duration:** 30 minutes

- [ ] TEST-001: Test generate_uds_header() with various inputs
- [ ] TEST-002: Test generate_uds_footer() with date calculations
- [ ] TEST-003: Integration test - Create full workorder with UDS
- [ ] TEST-004: Backward compatibility test

### Phase 5: Documentation Updates
**Duration:** 30 minutes

- [ ] DOC-001: Add UDS example to CLAUDE.md or create UDS-GUIDE.md
- [ ] DOC-002: Update CHANGELOG.json with UDS feature entry
- [ ] DOC-003: Update README.md to mention UDS in features

---

## Success Criteria

### Functional
- [ ] All workorder docs include UDS headers/footers
- [ ] UDS metadata includes all required fields
- [ ] Helper functions generate valid YAML
- [ ] Existing workorder workflows continue working
- [ ] /create-workorder produces UDS-enhanced documents

### Quality
- [ ] YAML validates without errors
- [ ] Timestamps use ISO 8601 format
- [ ] Status values use controlled vocabulary
- [ ] Review dates calculated correctly
- [ ] Server version detection works

### Documentation
- [ ] UDS templates documented with field descriptions
- [ ] Integration guide for adding UDS to new docs
- [ ] Example UDS-enhanced documents available
- [ ] CHANGELOG entry with version bump

---

## Metrics (To be updated after implementation)

**Lines of Code:** TBD
**Files Modified:** TBD
**Commits:** TBD
**Contributors:** TBD
**Time Spent:** TBD
**Completion Date:** TBD

---

**Next Steps:**
1. Implement Phase 2 (Helper Functions)
2. Run tests after each phase
3. Update this document with metrics using /update-deliverables
4. Update CHANGELOG and docs using /update-docs
5. Archive feature using /archive-feature
