# CSV Ecosystem Sync - Orchestrator Synthesis Report

**Session:** WO-CSV-ECOSYSTEM-SYNC-001
**Orchestrator:** coderef agent
**Report Date:** 2026-01-17
**Phase 1 Status:** ✅ COMPLETE (9/9 agents)

---

## Executive Summary

Phase 1 audit successfully completed across all 9 agents. **Total findings: 77 discrepancies, 148 new resources discovered.** CSV contains 306 resources but **massive structural issue uncovered**: global command architecture not reflected in CSV, causing path discrepancies for 67+ commands.

**Critical Discovery:** All slash commands have migrated to global `~/.claude/commands/` directory, but CSV still references project-local `.claude/commands/` paths. This affects 6/9 MCP servers.

**CSV Update Required:** YES - High priority, comprehensive updates needed across all resource types.

---

## Phase 1 Completion Status

| Agent ID | Status | Resources Scanned | Discrepancies | New Resources | Accuracy |
|----------|--------|-------------------|---------------|---------------|----------|
| coderef-assistant | ✅ Complete | 3 | 0 | 0 | 100% |
| coderef-context | ✅ Complete | 16 | 5 | 0 | 96.9% |
| coderef-workflow | ✅ Complete | 38 | 6 | 0 | 84.2% |
| coderef-docs | ✅ Complete | 54 | 19 | 6 | 64.8% |
| coderef-personas | ✅ Complete | 23 | 13 | 15 | 43.5% |
| coderef-testing | ✅ Complete | 15 | 29 | 1 | 0% |
| papertrail | ✅ Complete | 66 | 16 | 16 | 75.8% |
| coderef-core | ✅ Complete | 3 | 3 | 3 | 0% |
| coderef-dashboard | ✅ Complete | 184 | 13 | 123 | 92.9% |
| **TOTAL** | **9/9** | **402** | **77** | **148** | **73.2%** |

**Phase 1 Gate Criteria:**
- ✅ All 9 agents completed project audit
- ✅ Each agent created audit report in outputs/
- ✅ Discrepancies documented with recommendations
- ✅ Missing resources identified with complete metadata
- ✅ Communication.json files updated by all agents

---

## Cross-Project Patterns and Findings

### Pattern 1: Global Commands Migration (CRITICAL)

**Issue:** Commands have migrated to `C:\Users\willh\.claude\commands\` (global) but CSV still references project-local paths.

**Affected Servers:**
- coderef-docs: 12 commands (100% incorrect paths)
- coderef-workflow: 26 commands missing from project (CSV shows local paths)
- coderef-personas: 13 commands missing from project (CSV shows local paths)
- coderef-testing: 15 commands missing from project (CSV shows local paths)

**Evidence:** Found 67 global commands in `~/.claude/commands/`, ZERO in project-local `.claude/commands/` directories.

**Recommendation:** Phase 2 must update ALL command paths to global location. Add new column "Location" (global vs project-local).

### Pattern 2: Tool Path Prefix Errors

**Issue:** CSV paths include non-existent `src/{server-name}/` subdirectory for MCP tools.

**Affected Servers:**
- coderef-workflow: 37 tools (Path: `...src\coderef_workflow\server.py` → should be `...\server.py`)
- coderef-testing: 14 tools (Path: `...src\coderef_testing\server.py` → should be `...\server.py`)

**Impact:** 51 tool entries have incorrect paths (16.7% of CSV)

**Recommendation:** Bulk update CSV paths - remove `src/{server}/` prefix for all MCP server tools.

### Pattern 3: CSV Description Truncation

**Issue:** Descriptions with embedded commas (in parenthetical lists) are truncated by CSV parser.

**Affected Servers:**
- coderef-context: 5 tools (descriptions cut off mid-sentence)

**Examples:**
- `"Export coderef data in various formats (JSON"` → missing ", JSON-LD, Mermaid, DOT)"
- `"Query code relationships (what-calls"` → missing ", what-imports, shortest-path, etc)"

**Recommendation:** Escape commas in CSV descriptions or use double-quotes properly.

### Pattern 4: Missing Validators and Schemas

**Issue:** papertrail has significant validator/schema infrastructure not tracked in CSV.

**Findings:**
- 4 MCP tools missing (validate_stub, validate_schema_completeness, validate_all_schemas, validate_communication)
- 2 schemas missing (communication-schema.json, plan.schema.json)
- 10 validators missing (3 PowerShell, 7 Python)
- **Impact:** 33% of papertrail's validation infrastructure invisible in CSV

**Recommendation:** Add all validation resources with new Category values: "UDS Validation", "Session", "Workflow", "Core"

### Pattern 5: Dashboard UI Resources Not Tracked

**Issue:** coderef-dashboard has massive UI infrastructure (pages, components, API routes) not in CSV.

**Missing Resource Types:**
- 19 Next.js pages (entire navigation structure)
- 42 major UI components
- 27 API routes
- 7 context providers
- 5 custom hooks
- 14 library utilities

**Total Gap:** 123 resources (40% increase to CSV size)

**Decision Needed:** What granularity threshold for UI resources? Track all components or only "major" ones?

### Pattern 6: Timestamp Fields Empty

**Issue:** 174/306 resources (57%) have empty Created/LastUpdated timestamps.

**Affected Resources:**
- Dashboard tabs (6 entries)
- /widget-architect command
- Majority of tools and commands across all servers

**Recommendation:** Phase 2 automation to extract timestamps from git log (first commit = Created, last commit = LastUpdated).

---

## Critical Issues (Blockers for Phase 2)

### Issue 1: Global vs Project-Local Command Architecture Undefined

**Problem:** CSV doesn't distinguish between global commands (accessible in all projects) and project-local commands (specific to one project).

**Current State:**
- 67 global commands exist in `~/.claude/commands/`
- CSV references project-local paths for most commands
- No indication which commands should be global vs local

**Required Decision:**
1. Should all commands be global? (current reality)
2. Or should some commands remain project-local?
3. How to represent this in CSV? (new "Location" column vs path prefix)

**Blocker Impact:** Cannot update CSV paths without this decision.

### Issue 2: /archive-file Command Ownership Conflict

**Problem:** `/archive-file` exists in `coderef-workflow/.claude/commands/archive-file.md` but CSV doesn't list it anywhere.

**Context:**
- File describes archiving to `assistant/coderef/archived/{project}/`
- Related tool `archive_feature` exists in coderef-workflow server.py (correctly owned by workflow)
- But `/archive-file` command is in coderef-workflow project-local directory

**Conflict:** Should this command be:
1. Moved to global commands (like all others)?
2. Moved to assistant project (since it archives to assistant/)?
3. Deleted (if duplicate of `/archive-feature`)?

**Blocker Impact:** Cannot finalize coderef-workflow CSV entries without resolution.

### Issue 3: Persona JSON Files - Should They Be Tracked?

**Problem:** 15 persona definition files (`.json`) discovered in coderef-personas, not in CSV.

**Context:**
- These are internal data files (ava.json, lloyd.json, marcus.json, etc.)
- Not user-facing resources (users invoke via commands like `/ava`, not by reading JSON)
- But represent significant project assets

**Question:** Should internal data files be tracked in CSV, or only user-facing resources (tools, commands, scripts)?

**Decision Impact:** If YES, add 15 resources. If NO, document policy for future.

### Issue 4: UI Resource Granularity Threshold

**Problem:** coderef-dashboard has 114 UI resources (pages, components, routes, contexts, hooks, utilities). Adding all would increase CSV by 37%.

**Decision Needed:**
1. Track ALL UI resources? (comprehensive but CSV becomes huge)
2. Track "major" resources only? (requires defining "major")
3. Track by type (pages YES, components NO)?
4. Separate CSV for UI resources?

**Blocker Impact:** Cannot complete dashboard CSV updates without granularity policy.

---

## CSV Update Requirements (Phase 2)

### High Priority Updates (Must Complete)

**1. Command Paths - ALL COMMANDS (67 entries)**
- Update: Change all project-local paths to global path: `C:\Users\willh\.claude\commands\{command}.md`
- Affected Servers: coderef-docs (12), coderef-workflow (26), coderef-personas (13), coderef-testing (15), papertrail (1)
- Verification: Check if command exists globally before updating path

**2. Tool Paths - MCP Servers (51 entries)**
- Update: Remove `src\{server}\` prefix from all MCP tool paths
- Affected: coderef-workflow (37 tools), coderef-testing (14 tools)
- New Path Format: `C:\Users\willh\.mcp-servers\{server}\server.py`

**3. CSV Description Fixes (5 entries)**
- Update: Add full descriptions for coderef-context tools (currently truncated)
- Affected: coderef_context, coderef_export, coderef_incremental_scan, coderef_query, coderef_scan
- Fix: Properly escape commas in parenthetical lists

**4. Papertrail Resources (16 new entries)**
- Add: 4 MCP tools, 2 schemas, 10 validators
- Categories: UDS Validation, Session, Workflow, Core, Documentation
- Priority: HIGH - validation infrastructure must be discoverable

**5. Dashboard Python Scripts (3 new entries)**
- Add: build-source-of-truth.py, merge-and-dedupe.py, validate-csv.py
- Server: coderef-dashboard
- Categories: Scanners, Utilities, Validators

**6. coderef-core Scripts (3 new entries)**
- Add: setup_coderef_dirs.py, test_setup_coderef_dirs.py, scan.cjs
- Server: coderef-core
- Categories: Setup, Testing, Scanners

**7. coderef-docs Resources (6 new entries)**
- Add: /coderef-foundation-docs, /features-inventory (commands)
- Add: consistency_checker.py, validation_pipeline.py, user_guide_generator.py, remove-emojis.py (scripts)
- Server: coderef-docs
- Categories: Documentation, Utilities

### Medium Priority Updates (Phase 2 Recommended)

**8. Timestamps Automation (174 entries)**
- Update: Extract Created and LastUpdated from git log
- Scope: All resources with empty timestamp fields
- Automation: Script to run `git log` for each file path, extract first/last commit dates

**9. Server Re-attribution (1 entry)**
- Update: `/audit-plans` command - change Server from coderef-docs to coderef-workflow
- Reason: Planning audit belongs to workflow server, not docs

**10. Duplicate Resource Sheets Cleanup (2 entries)**
- Remove: Root-level Electron-IPC-Analysis and Notifications-UX-Review
- Keep: Subdirectory versions in coderef/resources-sheets/analysis/
- Update CSV: Reflect single canonical path per resource sheet

### Low Priority / Decision Required

**11. Dashboard UI Resources (123 new entries)**
- **DECISION REQUIRED:** Granularity threshold policy
- **IF approved:** Add pages (19), components (42), API routes (27), contexts (7), hooks (5), utilities (14), widgets (2), resource sheets (2)
- **Categories:** UI Navigation, UI Components, Workflow, System, API, Component
- **Impact:** CSV grows from 306 to 429 resources (40% increase)

**12. Persona JSON Files (15 potential entries)**
- **DECISION REQUIRED:** Should internal data files be tracked?
- **IF YES:** Add 12 production persona files (exclude test fixtures and backups)
- **Server:** coderef-personas
- **Category:** Persona Definitions

**13. Remove Stale Commands (43 entries)**
- **VERIFY FIRST:** Are these commands intentionally deleted or CSV outdated?
- Affected: coderef-workflow (26), coderef-personas (13), coderef-testing (15)
- **IF deleted:** Remove from CSV
- **IF moved to global:** Already covered in High Priority #1

---

## Recommendations for Phase 2

### Immediate Actions (Next Steps)

1. **Resolve Critical Decisions** (USER INPUT REQUIRED):
   - [ ] Global vs project-local command architecture policy
   - [ ] /archive-file ownership (move to global, assistant, or delete)
   - [ ] Persona JSON files tracking policy (YES/NO)
   - [ ] UI resource granularity threshold (ALL, MAJOR, TYPE-BASED, or SEPARATE-CSV)

2. **Execute High Priority CSV Updates** (25 new resources, 123 path corrections):
   - [ ] Update all 67 command paths to global location
   - [ ] Fix 51 MCP tool paths (remove src/{server}/ prefix)
   - [ ] Fix 5 truncated descriptions (coderef-context)
   - [ ] Add 16 papertrail resources
   - [ ] Add 3 dashboard Python scripts
   - [ ] Add 3 coderef-core scripts
   - [ ] Add 6 coderef-docs resources

3. **Validate CSV Updates**:
   - [ ] Run validate-csv.py after all updates
   - [ ] Verify 100% data quality maintained
   - [ ] Check for duplicate entries or path conflicts
   - [ ] Confirm all new resources have complete metadata (Type, Server, Category, Description, Status, Path)

4. **Automate Timestamp Population**:
   - [ ] Create script to extract git log timestamps for 174 resources
   - [ ] Run script and update CSV with Created/LastUpdated fields
   - [ ] Validate timestamp format (ISO 8601 or CSV-friendly)

### Phase 2 Agent Assignments

**coderef-docs** (Lead for CSV Integration):
- Integrate all audit findings into CSV
- Execute High Priority updates 1-7
- Run validation and verify 100% data quality
- Create CSV change log with before/after metrics

**coderef-dashboard** (Lead for UI Resources):
- After decision on granularity threshold:
  - Add approved UI resources to CSV
  - Update resource sheet index
  - Create UI resource taxonomy documentation

**coderef-workflow** (Phase 3 preparation):
- Review workflow instructions for CSV maintenance
- Identify all workflows that add/modify resources
- Prepare workflow update plan (Phase 3 dependency)

### Phase 3 Preparation Notes

**Dynamic Dashboard Implementation:**
- Requires: CSV path standardization (completed in Phase 2)
- Requires: UI resource taxonomy decision (decision needed)
- Implementation: Resources page reads CSV dynamically with file watching or polling

**Automated CSV Maintenance:**
- All workflows that create/modify resources must update CSV
- Target workflows:
  - /create-workorder → add workorder to CSV
  - /archive-feature → update CSV status
  - /create-plan → check CSV for existing resources
  - generate_foundation_docs → update CSV with new docs
  - generate_resource_sheet → add to CSV automatically

**New Page Structure Standard:**
- Each dashboard page: CLAUDE.md + coderef/ folder + resource-sheet-index.md
- Rollout to: resources/, explorer/, workflows/, personas/, documentation/, testing/
- Template creation needed before Phase 3 implementation

---

## Metrics and Impact Analysis

### Current CSV State
- Total Resources: 306
- Resource Types: 9 (Tool, Command, Script, Validator, Schema, Workflow, Output, ResourceSheet, Tab)
- Servers Covered: 7 (assistant, coderef-context, coderef-workflow, coderef-docs, coderef-personas, coderef-testing, coderef-dashboard)
- Data Quality: 100% (no schema violations)
- Timestamp Completeness: 43% (132/306 have timestamps)

### After Phase 2 (Projected)
- Total Resources: 331 → 454 (if UI resources approved)
- New Resource Types: +7 (Component, Page, APIRoute, Context, Hook, Utility, Widget, Persona)
- Timestamp Completeness: 100% (all 454 with git-extracted timestamps)
- Path Accuracy: 100% (all global/project-local paths corrected)
- Description Completeness: 100% (all truncations fixed)
- Server Coverage: +1 (papertrail now fully represented, chrome-devtools identified as gap)

### Known Gaps (Not Addressed in Phase 1)
1. **chrome-devtools MCP server:** Found reference in dashboard UI, not in CSV, no audit performed (9th server?)
2. **Resource sheet duplicates:** 2 duplicates found in dashboard, may exist elsewhere
3. **Test coverage:** Only 1 test script tracked (coderef-core), testing infrastructure may be underrepresented

---

## Audit Report Artifacts

All 9 agent audit reports available at:
```
csv-ecosystem-sync/
├── coderef-assistant/outputs/coderef-assistant-audit-report.json
├── coderef-context/outputs/coderef-context-audit-report.json
├── coderef-workflow/outputs/coderef-workflow-audit-report.json
├── coderef-docs/outputs/coderef-docs-audit-report.json
├── coderef-personas/outputs/coderef-personas-audit-report.json
├── coderef-testing/outputs/coderef-testing-audit-report.json
├── papertrail/outputs/papertrail-audit-report.json
├── coderef-core/outputs/coderef-core-audit-report.json
└── coderef-dashboard/outputs/coderef-dashboard-audit-report.json
```

**Total Audit Data:** 9 JSON files, ~2,500 lines of structured findings

---

## Next Steps

**Orchestrator Actions:**
1. Present this synthesis to user
2. Request decisions on 4 critical blockers
3. Once decisions received, trigger Phase 2 handoff to coderef-docs + coderef-dashboard

**Phase 2 Trigger Criteria:**
- ✅ All 4 critical decisions resolved
- ✅ User approves proceeding to CSV integration
- ✅ coderef-docs and coderef-dashboard agents ready

**Estimated Phase 2 Duration:** 2-4 hours (depending on UI resource granularity decision)

---

**Report Generated By:** coderef orchestrator
**Report Status:** Final - Phase 1 Complete
**Next Milestone:** Phase 2 Handoff (pending user decisions)
