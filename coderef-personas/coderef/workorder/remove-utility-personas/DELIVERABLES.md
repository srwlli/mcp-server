# Deliverables: Remove Utility Personas

**Workorder ID:** WO-REMOVE-UTILITY-PERSONAS-001
**Feature:** remove-utility-personas
**Status:** 🚧 Not Started
**Created:** 2025-12-25

---

## Phase 1: Preparation (15 min)

**Tasks:**
- [ ] PREP-001: Verify persona files exist
- [ ] PREP-002: Search codebase for references

**Deliverables:**
- Confirmed 4 personas exist
- Identified all references in codebase
- Verified backups exist

---

## Phase 2: Deletion (10 min)

**Tasks:**
- [ ] IMPL-001: Delete devon.json
- [ ] IMPL-002: Delete coderef-expert.json
- [ ] IMPL-003: Delete docs-expert.json
- [ ] IMPL-004: Delete widget-architect.json

**Deliverables:**
- 4 persona files deleted
- File system verified clean
- No broken references

---

## Phase 3: Documentation Update (25 min)

**Tasks:**
- [ ] DOCS-001: Update CLAUDE.md
- [ ] DOCS-002: Update my-guide.md

**Deliverables:**
- CLAUDE.md updated
- my-guide.md updated
- All references consistent

---

## Phase 4: Verification & Commit (15 min)

**Tasks:**
- [ ] TEST-001: Verify remaining personas load
- [ ] GIT-001: Create git commit

**Deliverables:**
- All 7 personas verified functional
- Git commit created
- Repository clean

---

## Metrics

| Metric | Target | Actual |
|--------|--------|--------|
| Files Deleted | 4 | TBD |
| Lines of Code Changed | 50-100 | TBD |
| Git Commits | 1 | TBD |
| Time Spent | ~65 min | TBD |

---

## Success Criteria

✅ All 4 personas deleted
✅ 7 core personas remain functional
✅ No broken references in codebase
✅ Documentation updated
✅ Git commit created with clear message

---

## Notes

- Feature branches are NOT needed for this refactor (direct to main)
- Backups should exist in personas/backups/ before deletion
- All 7 remaining personas: lloyd, ava, marcus, quinn, taylor, research-scout, +1 undocumented

