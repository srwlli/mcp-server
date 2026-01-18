# Resources Index - coderef-dashboard Agent

## Session Documents
- [Master Communication](../../../csv-ecosystem-sync/communication.json)
- [Master Instructions](../../../csv-ecosystem-sync/instructions.json)
- [Agent Communication](../communication.json)
- [Agent Instructions](../instructions.json)

## Primary CSV
- **Source of Truth:** `C:\Users\willh\Desktop\coderef-dashboard\packages\dashboard\src\app\resources\coderef\tools-and-commands.csv`
- **Current State:** 306 resources, 9 types, 7 servers, 100% data quality
- **Last Updated:** 2026-01-17

## Dashboard Project Scope
- **Includes:** All of `C:\Users\willh\Desktop\coderef-dashboard\`
- **EXCLUDES:** `packages/coderef-core/` (handled by coderef-core agent)

## Known Issues (Pre-Audit Context)

### Critical Gaps Already Identified

**1. Timestamp Fields (Major Issue)**
- 174 out of 306 resources (57%) have empty Created/LastUpdated timestamps
- Only ResourceSheets (29) and some Scripts have timestamps populated
- Commands and Tools have NO timestamps

**2. Missing Resource Types in UI**

The page currently does NOT display:
- ✗ ResourceSheets (29 resources) - Documented in RESOURCE-SHEET-INDEX.md but not shown in UI
- ✗ Schemas (27 resources) - JSON validation schemas
- ✗ Validators (17 resources) - Papertrail validation scripts
- ✗ Scripts (53 resources) - Scripts tab exists but shows hardcoded content, not CSV data

**3. Server Coverage Mismatch**

In CSV but not in UI:
- papertrail (4 tools)

In UI but not in CSV:
- chrome-devtools (11 tools)

**4. Data Source Disconnect**

- UI uses hardcoded TypeScript constants in tab components
- CSV is NOT read by the page - page.tsx doesn't import or parse the CSV
- No integration between CSV and UI display

### Existing Recommendations

1. **Populate Timestamps**
   - Run timestamp extraction for all 174 resources missing Created/LastUpdated
   - Prioritize Commands and Tools (110 resources)

2. **Integrate CSV with UI**
   - Modify page.tsx to read from coderef/tools-and-commands.csv
   - Replace hardcoded tab data with CSV parsing
   - Enable real-time filtering and search

3. **Add Missing Resource Types**
   - Create tabs for ResourceSheets, Schemas, Validators
   - Or add them to existing tabs with type badges

4. **Sync Missing Servers**
   - Add chrome-devtools tools to CSV (11 resources)
   - Ensure papertrail tools appear in UI (4 resources)

5. **Remove Hardcoded Data**
   - Delete TypeScript constants from CommandsTab.tsx, ToolsTab.tsx
   - Use single source of truth (CSV)

---

## Phase 1 Audit Tasks

Your audit should verify/update the above findings and add any new discoveries:

1. Scan dashboard project for ALL resources (commands, scripts, tabs, pages, components, widgets)
2. Compare against CSV current state
3. Document:
   - Confirmed gaps (timestamps, UI integration, missing types)
   - New discrepancies discovered
   - Additional missing resources
4. Create comprehensive audit report

## Phase 2 & 3 Tasks

After all agents complete Phase 1:
- **Phase 2:** Update CSV with all audit findings
- **Phase 3:** Implement dynamic dashboard + new page structure standard

---

**Agent Home:** `C:\Users\willh\Desktop\coderef-dashboard`
**Session Path:** `C:\Users\willh\.mcp-servers\coderef\sessions\csv-ecosystem-sync\coderef-dashboard`
**Phases:** 1, 2, 3
