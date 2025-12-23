# Changelog Refactor Implementation Plan
## WO-CHANGELOG-REFACTOR-001

**Status:** ✅ Planning Complete - Ready for Implementation
**Validation Score:** 95/100
**Workorder ID:** WO-CHANGELOG-REFACTOR-001
**Feature Directory:** `coderef/working/changelog-refactor/`

---

## TL;DR

**Problem:** 3 tools for changelog management (get_changelog, add_changelog_entry, update_changelog) with manual workflow + critical data quality bugs.

**Solution:** Consolidate to 2 tools with smart agentic flow:
- **New:** `record_changes` - Auto-detects git context, suggests change_type/severity, guides agent confirmation
- **Keep:** `get_changelog` - Read/query (no changes)
- **Remove:** `update_changelog` - Replaced by agentic flow
- **Fix:** Semantic version comparison, breaking change validation, duplicate detection

**Impact:** Reduces agent friction from 3 steps → 1 smart call. Improves data quality with critical bug fixes.

---

## What Gets Fixed

### 1. Critical Bugs (Phase 2)
✅ **Semantic Version Comparison** - String comparison `"2.0.0" < "10.0.0"` fails. Fix: use `packaging.version.parse()`
✅ **Breaking Changes Without Migration** - Can add breaking changes without migration guides. Fix: require migration text
✅ **Duplicate Detection** - Can add same change twice. Fix: detect (version, title) collisions

### 2. New Agentic Tool (Phase 3)
✅ **record_changes** - Single call with auto-detection:
- Auto-detect changed files: `git diff --staged`
- Suggest change_type from commit messages: `feat(...) → feature`
- Calculate severity from scope: `3 files + breaking API → major`
- Show preview to agent for confirmation
- Create entry on approval

### 3. Data Quality (Phase 3)
✅ Enhanced CHANGELOG.json format:
```json
{
  "id": "change-046",
  "type": "feature",
  "auto_detected": {
    "files_from": "git diff --staged",
    "type_from": "commit msg: 'feat(...)'",
    "severity_from": "scope: 3 files = major"
  },
  "agent_confirmed": true,
  "recorded_at": "2025-12-23T18:32:15Z"
}
```

### 4. Tool Consolidation (Phase 3)
✅ From 11 → 10 tools:
- Remove: `update_changelog` (purely instructional)
- Add: `record_changes` (agentic automation)
- Keep: `get_changelog` (read/query unchanged)
- Deprecate: `add_changelog_entry` (replaced by record_changes pattern)

---

## Implementation Phases

| Phase | Name | Duration | Key Deliverables |
|-------|------|----------|------------------|
| **1** | Setup & Analysis | 1-2h | Understand system, document files to modify |
| **2** | Critical Bug Fixes | 2-3h | Semantic version, migration validation, duplicate detection |
| **3** | New Tool Implementation | 4-5h | record_changes tool + enhanced CHANGELOG format |
| **4** | Testing & Validation | 3-4h | Unit/integration tests, manual testing, docs update |
| **Total** | | **10-14h** | Fully working 2-tool changelog system |

---

## Key Implementation Details

### record_changes Tool Signature

```python
async def handle_record_changes(arguments: dict) -> list[TextContent]:
    project_path: str              # Required
    version: str                   # Required: e.g., "2.1.0"
    context: dict = {              # Optional
        "files_changed": [...],    # Auto-detected from git
        "commit_messages": [...],  # From git log
        "feature_name": "...",     # From agent context
        "description": "..."       # Agent provides
    }
    # Returns: {
    #   "change_id": "change-048",
    #   "recorded": true,
    #   "changelog_entry": {...},
    #   "preview": "Agent sees this before confirmation"
    # }
```

### Agents See This Preview

```
📝 CHANGELOG ENTRY PREVIEW
────────────────────────────
Type: feature (from commit msg: 'feat(...)')
Severity: major (3 files changed)
Title: Add smart changelog recording with auto-detection

Files changed: [tool_handlers.py, generators/changelog_generator.py, server.py]

Suggested reason: From commit body - "Replace manual workflow..."
Suggested impact: "Agents record changes with 1 call instead of 2"

✅ Confirm? [Y/n]
Need to change title? [blank/custom text]
Add additional notes? [blank/text]
```

### Git Auto-Detection Works Like This

```python
# Step 1: Get staged files
changed_files = subprocess.run(
    ["git", "diff", "--staged", "--name-only"],
    capture_output=True
).stdout.decode().split('\n')
# Result: ["tool_handlers.py", "generators/changelog_generator.py", ...]

# Step 2: Get recent commits
commits = subprocess.run(
    ["git", "log", "-10", "--oneline"],
    capture_output=True
).stdout.decode()
# Pattern match: 'feat(...)', 'fix(...)', 'BREAKING CHANGE:'
# Result: change_type = "feature", severity = "major"

# Step 3: Suggest severity from scope
if len(changed_files) > 5 or breaking_api:
    severity = "major"
elif len(changed_files) > 2:
    severity = "minor"
else:
    severity = "patch"
```

---

## Files to Modify

| File | Changes | Complexity |
|------|---------|------------|
| `tool_handlers.py` | Add `handle_record_changes()`, fix semver comparison, add migration validation, remove `handle_update_changelog` | High |
| `generators/changelog_generator.py` | Fix line 241 (semver), add migration required validation, add duplicate detection | Medium |
| `server.py` | Add `record_changes` tool def, remove `update_changelog`, update docstring | Low |
| `validation.py` | Add migration field validation | Low |
| `CLAUDE.md` | Update tool count (11→10), document record_changes agentic pattern | Low |
| **New:** `tests/unit/handlers/test_record_changes_handler.py` | Unit tests for git detection, suggestions | Medium |
| **New:** `tests/unit/generators/test_changelog_generator_fixes.py` | Tests for semver, migration, duplicates | Medium |

---

## Success Criteria (18 Tasks)

### Phase 1 (2 tasks) ✓
- [ ] Understand current system
- [ ] Document all files to modify

### Phase 2 (3 tasks) ✓
- [ ] Fix semantic version comparison
- [ ] Add breaking change migration validation
- [ ] Implement duplicate detection

### Phase 3 (4 tasks) ✓
- [ ] Create `handle_record_changes()` with git auto-detection
- [ ] Enhance CHANGELOG.json format with metadata
- [ ] Update server.py (add tool, remove tool)
- [ ] Register in TOOL_HANDLERS and update CLAUDE.md

### Phase 4 (9 tasks) ✓
- [ ] Write comprehensive unit tests
- [ ] Write integration tests (backward compat, build)
- [ ] Manual testing on real repo
- [ ] Verify all tests passing
- [ ] Build succeeds (uv build)
- [ ] Verify tool discovery works

---

## Testing Strategy

### Unit Tests (5 files)
1. **Semantic Version Comparison** - Test 2.0.0 vs 10.0.0, etc
2. **Migration Validation** - Breaking without migration fails
3. **Duplicate Detection** - Same change detected, prevented
4. **record_changes Handler** - Git detection, suggestions, preview
5. **Backward Compatibility** - Old CHANGELOG.json still works

### Integration Tests
1. **End-to-End record_changes** - Full workflow on real repo
2. **Build & Discovery** - `uv build` succeeds, tool discoverable
3. **Backward Compat** - Existing entries still queryable

### Manual Tests
1. Real git repo with actual changes
2. Agent confirmation flow with preview
3. Entry created and queryable via `get_changelog`
4. With/without git context

---

## Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Breaking changes to add_changelog_entry | Medium | High | Support both tools temporarily, deprecation notice |
| Git commands fail in non-git environments | Low | Medium | Wrap in try/except, support optional context |
| Version comparison fix causes inconsistency | Low | Medium | Comprehensive tests, clear migration guide |
| Difficulty detecting change_type | Medium | Low | Simple patterns, allow agent override, log misdetections |

---

## Related Features (Future)

- **Phase 2:** Update/delete operations for changelog maintenance
- **Enhancement:** Compound filtering by multiple criteria
- **Optimization:** Performance improvements for large changelogs

---

## Next Steps

1. **Review this plan** - Ensure all requirements captured
2. **Execute Phase 1** - Run `/execute-plan` to generate task checklist
3. **Implement Phases 2-4** - Follow task list, update task status with `/update-task-status`
4. **After completion** - Run `/update-deliverables` to capture metrics
5. **Archive feature** - Run `/archive-feature` when done

---

## Workorder Tracking

```
Workorder: WO-CHANGELOG-REFACTOR-001
Created: 2025-12-23T22:44:14Z
Status: Ready for Implementation
Files:
  - context.json (requirements gathered)
  - analysis.json (project analyzed)
  - plan.json (implementation plan created)
  - DELIVERABLES.md (tracking template)
```

**Logged to:**
- Local: `coderef/workorder-log.txt`
- Orchestrator: `~/.mcp-servers/coderef/workorder-log.txt`

---

## Questions?

Review the detailed plan at: `coderef/working/changelog-refactor/plan.json`

Review the gap analysis at: `coderef/CHANGELOG_TOOLS_REVIEW.md`

Ready to `/execute-plan` when you are!
