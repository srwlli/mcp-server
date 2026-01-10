# Papertrail Repositioning Plan: Validation/QA/Standards Engine

**Date:** 2026-01-04
**Status:** Planning

---

## Current State

**Scattered validation across projects:**
- `sessions/communication-schema.json` - Session file validation
- `sessions/validate-sessions.ps1` - Session validator script
- `sessions/README-VALIDATION.md` - Validation docs
- `.claude/commands/create-resource-sheet.md` - Resource sheet standards (in command)
- No centralized standards repository

**Current 3-server model:**
- **coderef-docs:** Generates documentation
- **coderef-workflow:** Orchestrates workflows
- **papertrail:** Logs/tracks workorders

---

## New Architecture

**Papertrail becomes the Standards & Validation Hub:**

```
papertrail/
├── schemas/                              # JSON Schemas (validation contracts)
│   ├── communication-schema.json         # ← Move from sessions/
│   ├── instructions-schema.json          # ← Create new
│   ├── resource-sheet-metadata-schema.json  # ← Create new
│   ├── workorder-schema.json             # ← Create new
│   └── plan-schema.json                  # ← Create new
│
├── validators/                           # Validation scripts
│   ├── validate-sessions.ps1             # ← Move from sessions/
│   ├── validate-resource-sheets.ps1      # ← Create new
│   ├── validate-workorders.ps1           # ← Create new
│   └── validate-all.ps1                  # ← Master validator
│
├── standards/                            # UDS (Universal Documentation Standards)
│   ├── naming-conventions.md             # ← Create new
│   ├── resource-sheet-standards.md       # ← Extract from /create-resource-sheet
│   ├── documentation-quality-gates.md    # ← Create new
│   └── file-organization-standards.md    # ← Create new
│
├── logs/                                 # Existing tracking (unchanged)
│   └── workorder-log.txt
│
└── README.md                             # Updated role definition
```

---

## Responsibilities Matrix

| Function | Before | After |
|----------|--------|-------|
| **Generate docs** | coderef-docs | coderef-docs (unchanged) |
| **Execute workflows** | coderef-workflow | coderef-workflow (unchanged) |
| **Track history** | papertrail | papertrail (unchanged) |
| **Validate schemas** | ❌ Scattered | ✅ papertrail/schemas/ |
| **Enforce standards** | ❌ Ad-hoc | ✅ papertrail/standards/ |
| **Run QA checks** | ❌ Manual | ✅ papertrail/validators/ |

---

## Files to Create

**1. Schemas (5 files)**
- `schemas/communication-schema.json` - Move existing
- `schemas/instructions-schema.json` - Define session instructions format
- `schemas/resource-sheet-metadata-schema.json` - Front matter validation
- `schemas/workorder-schema.json` - Workorder structure
- `schemas/plan-schema.json` - Implementation plan format

**2. Validators (4 files)**
- `validators/validate-sessions.ps1` - Move existing
- `validators/validate-resource-sheets.ps1` - Check naming, front matter, sections
- `validators/validate-workorders.ps1` - Verify workorder structure
- `validators/validate-all.ps1` - Run all validators

**3. Standards (4 files)**
- `standards/naming-conventions.md` - Filenames, IDs, paths
- `standards/resource-sheet-standards.md` - What makes a valid resource sheet
- `standards/documentation-quality-gates.md` - Required sections, completeness checks
- `standards/file-organization-standards.md` - Where files should live

**4. Documentation (1 file)**
- `README.md` - Papertrail's expanded role

---

## Migration Steps

### Phase 1: Create Structure
1. Create `papertrail/schemas/`, `papertrail/validators/`, `papertrail/standards/`
2. Move `communication-schema.json` from sessions/ to papertrail/schemas/
3. Move `validate-sessions.ps1` from sessions/ to papertrail/validators/
4. Update paths in moved files

### Phase 2: Create New Standards
1. Extract resource sheet standards from `/create-resource-sheet` command
2. Document naming conventions (WO-XXX-001, SESSIONS-RESOURCE-SHEET.md, etc.)
3. Define quality gates (required sections, metadata requirements)

### Phase 3: Create New Validators
1. `validate-resource-sheets.ps1` - Check all `*RESOURCE-SHEET.md` files
2. `validate-workorders.ps1` - Verify workorder structure
3. `validate-all.ps1` - Master script

### Phase 4: Integration
1. Update sessions/ to reference papertrail/schemas/
2. Add pre-commit hooks calling papertrail validators
3. Update documentation to reflect new architecture

---

## Clear Separation of Concerns

### coderef-docs
- ✅ GENERATES resource sheets (via MCP tool)
- ✅ PROVIDES templates
- ❌ Does NOT validate

### papertrail
- ✅ VALIDATES all documentation
- ✅ ENFORCES standards
- ✅ TRACKS compliance
- ❌ Does NOT generate

### coderef-workflow
- ✅ ORCHESTRATES processes
- ✅ EXECUTES plans
- ❌ Does NOT validate or generate

---

## Benefits

1. **Single source of truth** - All standards in one place
2. **Reusable validators** - Any project can call papertrail validation
3. **Clear ownership** - Papertrail owns quality enforcement
4. **Easier maintenance** - Update standards once, applies everywhere
5. **Better DX** - Developers know where to find standards

---

## Next Steps

1. Review this plan with team
2. Get approval for architectural change
3. Execute Phase 1 (create structure + move existing files)
4. Execute Phase 2 (document standards)
5. Execute Phase 3 (create new validators)
6. Execute Phase 4 (integrate across ecosystem)

---

**Created:** 2026-01-04
**Maintained by:** coderef orchestrator
