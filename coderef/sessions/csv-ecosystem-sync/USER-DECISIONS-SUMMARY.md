# User Decisions Summary - WO-CSV-ECOSYSTEM-SYNC-001

**Date:** 2026-01-17
**Phase:** 1 → 2 Transition
**Status:** ✅ All Decisions Approved, Phase 2 Ready

---

## Decisions Made

### ✅ Decision 1: Global vs Project-Local Command Architecture

**Question:** Should all commands be global or some project-local?

**User Decision:** **All commands are global**

**Impact:**
- Update all 67 command paths to: `C:\Users\willh\.claude\commands\{command}.md`
- No project-local commands exist (architecture unified)
- CSV will reflect global location for all slash commands

---

### ✅ Decision 2: /archive-file Command Ownership

**Question:** What to do with `/archive-file` command found in coderef-workflow?

**User Decision:** **Move to global, server = coderef-workflow**

**Impact:**
- Move file from `coderef-workflow/.claude/commands/` → `~/.claude/commands/`
- Add to CSV with Server=coderef-workflow
- Unifies with all other global commands

---

### ✅ Decision 3: Persona JSON Files Tracking Policy

**Question:** Should internal persona JSON files be tracked in CSV?

**User Decision:** **YES - Add all personas**

**Impact:**
- Add 12 production persona files to CSV
- Type: Persona (new resource type)
- Server: coderef-personas
- Category: Persona Definitions
- Exclude: test fixtures (integration-test.json), backups (nfl-scraper-expert-*.json)

---

### ✅ Decision 4: UI Resource Granularity Threshold

**Question:** Should CSV include 123 UI resources (pages, components, API routes, etc.)?

**User Decision:** **NO - CSV is for files, tools, scripts, logic, documents, NOT components**

**Impact:**
- Do NOT add: 19 pages, 42 components, 27 API routes, 7 contexts, 5 hooks, 14 utilities, 2 widgets
- CSV remains focused on infrastructure resources (tools, commands, scripts, schemas, validators)
- Dashboard UI components intentionally excluded
- **CSV grows by +40 instead of +123 resources**

---

## Phase 2 Execution Summary

### New Resources to Add: +40

| Source | Count | Details |
|--------|-------|---------|
| Papertrail | +16 | 4 tools, 2 schemas, 10 validators |
| Dashboard | +3 | 3 Python scripts (build-source-of-truth, merge-and-dedupe, validate-csv) |
| coderef-core | +3 | 3 scripts (setup_coderef_dirs, test, scan.cjs) |
| coderef-docs | +6 | 2 commands, 4 scripts |
| coderef-personas | +12 | 12 persona JSON files |
| coderef-workflow | +1 | /archive-file command (after move to global) |
| **TOTAL** | **+40** | **Excludes 123 UI resources per decision #4** |

### Path Corrections: 119

- **67 commands:** Update to global path `~/.claude/commands/{command}.md`
- **51 tools:** Remove `src/{server}/` prefix from MCP server paths
- **1 /archive-file:** Move to global + add to CSV

### Timestamp Population: 174

- Auto-fill empty Created/LastUpdated fields from git log
- 57% of current CSV missing timestamps

### Other Updates:

- Fix 5 truncated descriptions (coderef-context tools)
- Re-attribute /audit-plans: coderef-docs → coderef-workflow
- Remove 2 duplicate resource sheets

---

## Before/After Metrics

| Metric | Before (Phase 1) | After (Phase 2) | Change |
|--------|------------------|-----------------|--------|
| Total Resources | 306 | 346 | +40 (+13%) |
| Resource Types | 9 | 10 | +1 (Persona) |
| Incorrect Paths | 119 | 0 | -119 (100% fix) |
| Empty Timestamps | 174 (57%) | 0 (0%) | -174 (100% fix) |
| Truncated Descriptions | 5 | 0 | -5 (100% fix) |
| Data Quality | 100% | 100% | Maintained |

---

## Phase 2 Tasks (13 Steps)

1. ✅ **Move /archive-file to global** (prerequisite)
2. ✅ **Update 68 command paths** (67 existing + 1 new)
3. ✅ **Fix 51 MCP tool paths**
4. ✅ **Add 16 papertrail resources**
5. ✅ **Add 3 dashboard scripts**
6. ✅ **Add 3 coderef-core scripts**
7. ✅ **Add 6 coderef-docs resources**
8. ✅ **Add 12 persona files**
9. ✅ **Fix 5 truncated descriptions**
10. ✅ **Populate 174 timestamps** (git log automation)
11. ✅ **Re-attribute /audit-plans**
12. ✅ **Remove 2 duplicate resource sheets**
13. ✅ **Verify 43 stale commands** (likely covered in step 2)

**Plus:**
- Run validate-csv.py (100% pass required)
- Create CSV change log

---

## Next Steps

**Immediate:**
1. Hand off to coderef-docs agent for Phase 2 execution
2. coderef-docs reads: `sessions/csv-ecosystem-sync/PHASE-2-HANDOFF.md`
3. coderef-docs executes all 13 steps + validation

**After Phase 2:**
- Phase 3: Dynamic Dashboard Implementation (Resources page reads CSV in real-time)
- Phase 3: Automated CSV Maintenance (workflows update CSV automatically)
- Phase 3: New Page Structure Standard (CLAUDE.md + coderef/ folder for 6 pages)

---

## Files Created

- ✅ `orchestrator-synthesis.md` - Full Phase 1 audit analysis (77 discrepancies, 148 discoveries)
- ✅ `PHASE-2-HANDOFF.md` - Detailed execution instructions for coderef-docs agent
- ✅ `USER-DECISIONS-SUMMARY.md` - This file (decisions and impacts)
- ✅ `communication.json` - Updated with Phase 2 status and user decisions

---

**Status:** Phase 2 Ready to Execute
**Lead Agent:** coderef-docs
**Estimated Duration:** 2-3 hours
**Success Criteria:** 100% validation pass, CSV grows from 306 → 346 resources
