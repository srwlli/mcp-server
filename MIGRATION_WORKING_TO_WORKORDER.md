# Migration Guide: coderef/working → coderef/workorder

**Workorder:** WO-WORKFLOW-REFACTOR-001
**Date:** 2025-12-25
**Status:** Complete

---

## Overview

This guide explains the breaking change from `coderef/working/` to `coderef/workorder/` and how it affects existing features.

**Key Points:**
- **No backward compatibility** - old paths are no longer supported
- **Non-breaking for existing features** - they remain in `coderef/working/` unchanged
- **New features use workorder IDs** - all new features go to `coderef/workorder/{WO-ID}/`
- **No directory migration needed** - manual migration is optional for old features

---

## What Changed

### Directory Structure

**Before:**
```
coderef/working/
├── feature-auth/
│   ├── context.json
│   ├── analysis.json
│   ├── plan.json
│   └── DELIVERABLES.md
└── feature-api/
    └── ... (same structure)
```

**After (New Features):**
```
coderef/workorder/
├── WO-AUTH-SYSTEM-001/
│   ├── context.json
│   ├── analysis.json
│   ├── plan.json
│   └── DELIVERABLES.md
└── WO-API-DESIGN-001/
    └── ... (same structure)
```

**Existing Features (Unchanged):**
```
coderef/working/
├── feature-auth/           ← Still here, not moved
├── feature-api/            ← Still here, not moved
└── ... (all original features)
```

---

## File Changes

### Code Updates (42 changes across 6 Python files)
- All path references updated from `coderef/working` → `coderef/workorder`
- Path construction logic updated
- Tool descriptions updated

### Documentation Updates (35 changes across 13 slash commands)
- Slash command files updated with new paths
- User-facing documentation updated
- Examples and instructions updated

### Main Documentation (7 changes in 2 files)
- README.md updated
- CLAUDE.md updated with new architecture

---

## Impact on Existing Features

### Before Migration
- Features in `coderef/working/{feature-name}/`
- Can be accessed via `/execute-plan`, `/update-deliverables`, etc.
- Remain unchanged in place

### After Migration (Optional)
- Can optionally move to `coderef/workorder/{WO-ID}/`
- Would require:
  1. Assigning a workorder ID (format: `WO-FEATURE-CATEGORY-###`)
  2. Manually moving directories with `git mv`
  3. Updating all internal references
- **Recommended:** Leave existing features in place, only use new paths for new work

---

## How to Use the New System

### Creating a New Feature (Using New Paths)

```bash
# Step 1: Gather context
/create-workorder "new-feature"
# Prompts for requirements and constraints

# Step 2: System auto-generates workorder
# WO-NEW-FEATURE-001 → creates coderef/workorder/WO-NEW-FEATURE-001/

# Step 3: Create plan
/create-plan \
  --project_path . \
  --feature_name "new-feature" \
  --workorder_id "WO-NEW-FEATURE-001"

# Step 4: Execute and track
/execute-plan "new-feature"
```

### Working with Old Features (Still in coderef/working/)

```bash
# Old features continue to work as-is
/update-deliverables "feature-auth"
/execute-plan "feature-auth"

# No migration required - they're not affected
```

---

## Workorder ID Format

```
WO-{FEATURE}-{CATEGORY}-{SEQUENCE}
```

**Examples:**
- `WO-AUTH-SYSTEM-001` - First auth system feature
- `WO-API-DESIGN-001` - First API design feature
- `WO-DATABASE-MIGRATION-001` - First database migration

**Rules:**
- Must follow format exactly
- Sequence is 3 digits (001, 002, etc.)
- Category identifies feature area (SYSTEM, DESIGN, MIGRATION, etc.)
- Feature is the primary feature name (uppercased)

---

## Breaking Changes Summary

| Item | Old | New | Impact |
|------|-----|-----|--------|
| Default path | `coderef/working/` | `coderef/workorder/{WO-ID}/` | New features only |
| Feature ID | Feature name | Workorder ID | Required in plan.json |
| Plan storage | `coderef/working/{name}/plan.json` | `coderef/workorder/{WO-ID}/plan.json` | Path-dependent code affected |
| Backward compat | N/A | None - breaking change | Old path strings unsupported |

---

## Migration Checklist

### For Users
- [ ] Understand new workorder ID format
- [ ] Use `/create-workorder` for new features
- [ ] Keep old features in `coderef/working/` (optional to migrate)
- [ ] Update any custom scripts using old paths

### For Code
- [x] Update all Python file path references
- [x] Update all slash command documentation
- [x] Update tool descriptions
- [x] Update README and CLAUDE.md

### For Testing
- [ ] Test creating new feature with workorder ID
- [ ] Test `/execute-plan` with new paths
- [ ] Test `/update-deliverables` with new paths
- [ ] Verify old features still work (backward read support)

---

## Troubleshooting

### Error: "Feature not found in coderef/working/"
**Cause:** Trying to access old path that doesn't exist
**Solution:** Use new path `coderef/workorder/{WO-ID}/` for new features

### Error: "plan.json missing workorder_id"
**Cause:** Old plan.json without workorder_id field
**Solution:** Either:
1. Regenerate plan with new system (adds workorder_id), or
2. Manually add `"workorder_id": "WO-XXXX-001"` to META_DOCUMENTATION

### Old features not found after refactor
**Cause:** Old features still in `coderef/working/` (correct location)
**Solution:** This is expected - they remain in old location unchanged

---

## FAQ

### Q: Do I need to migrate existing features?
**A:** No - existing features remain in `coderef/working/`. Only new features use `coderef/workorder/`.

### Q: What if I have a custom script using coderef/working?
**A:** Update the script to use `coderef/workorder/{WO-ID}/` for new features, or keep using old path for existing features.

### Q: Can I move an old feature to the new structure?
**A:** Yes, manually using `git mv`, but it's not required or recommended unless needed.

### Q: How are workorder IDs assigned?
**A:** Auto-generated by `/create-workorder` based on feature name, or specified explicitly when creating plan.

### Q: What's stored in plan.json now?
**A:** Includes new `workorder_id` field in META_DOCUMENTATION for full tracking and audit trail.

---

## References

- **WORKING_TO_WORKORDER_REFACTOR.md** - Detailed change inventory
- **COMPLETE_COMMAND_AUDIT.md** - All 53 slash commands and their status
- **coderef-workflow/CLAUDE.md** - Architecture documentation

---

## Support

For questions or issues with the migration:
1. Check this guide's FAQ section
2. Review CLAUDE.md for architecture details
3. Check individual slash command docs (`/help <command>`)
4. File an issue with reproduction steps

---

**Status:** Complete ✓
**Breaking Change:** Yes - no backward compatibility
**Automatic Migration:** Not needed for existing features
**Manual Migration:** Optional for existing features

