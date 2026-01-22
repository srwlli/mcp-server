# Universal Context Menu System - Session

**Workorder ID:** WO-UNIVERSAL-CTX-MENU-001
**Created:** 2026-01-20
**Status:** Ready to Execute
**Pattern:** Hierarchical Multi-Agent Session

---

## Overview

Consolidate 3+ fragmented right-click context menu implementations into a truly universal context menu system that works with ANY target (boards, prompts, notes, sessions, favorites, future targets).

**Problem:** AddFileToBoardMenu (files), BoardContextMenu (stubs/workorders), and inline menus create maintenance burden with inconsistent caching, eager loading, missing card-level actions. Board-only design limits extensibility.

**Solution:** EntityContextMenu<TEntity, TTarget> component + EntityConverter<TEntity, TTarget> interface + TargetAdapter pattern with pluggable adapters for any target type.

---

## Session Structure

```
universal-context-menu-system/
├── communication.json (session-level agent roster)
├── instructions.json (orchestrator coordination)
├── ANALYSIS.md (full problem analysis)
├── README.md (this file)
│
├── coderef-dashboard/ (Phase 1: Implementation)
│   ├── communication.json (8 tasks, success metrics)
│   ├── instructions.json (step-by-step execution)
│   ├── resources/index.md (links to specs)
│   └── outputs/ (implementation-report.md)
│
├── coderef-docs/ (Phase 2: Documentation)
│   ├── communication.json (3 tasks)
│   ├── instructions.json
│   ├── resources/index.md
│   └── outputs/ (documentation-report.md)
│
└── papertrail/ (Phase 2: Validation)
    ├── communication.json (3 tasks)
    ├── instructions.json
    ├── resources/index.md
    └── outputs/ (validation-report.md)
```

---

## Phases

### Phase 1: Implementation (coderef-dashboard)
**Agent:** coderef-dashboard
**Tasks:** 14 tasks
**Deliverables:**
- EntityContextMenu<TEntity, TTarget> component (target-agnostic)
- EntityConverter<TEntity, TTarget> interface
- TargetAdapter interface for pluggable targets
- BoardTargetAdapter (full implementation)
- 4 proof-of-concept adapters (Prompt, Session, Note, Favorite)
- 6 multi-target converters (file→board, file→prompt, stub→board, stub→session, workorder→board, workorder→session)
- Refactored AddFileToBoardMenu using BoardTargetAdapter
- Updated StubCard and WorkorderCard with multi-target right-click (boards + sessions)
- Unit tests (80%+ coverage, 75+ tests)

**Phase Gate:**
- All 14 tasks complete
- Tests passing (75+ tests)
- No regressions in file-to-board functionality
- BoardTargetAdapter fully functional (replaces useBoardsCache)
- At least 2 proof-of-concept adapters working
- Multi-target converters tested
- TypeScript compiles

### Phase 2: Documentation & Validation (coderef-docs + papertrail)
**Agents:** coderef-docs, papertrail
**Tasks:** 7 tasks total (4 docs + 3 validation)
**Deliverables:**
- UNIVERSAL-CONTEXT-MENU.md migration guide with examples for boards, prompts, notes, sessions, favorites
- EntityContextMenu-RESOURCE-SHEET.md
- EntityConverter-RESOURCE-SHEET.md
- TargetAdapter-RESOURCE-SHEET.md
- Validation report (schema compliance, tests, multi-target proof of concepts working)

**Phase Gate:**
- Documentation complete
- All validations pass
- Migration guide includes examples

---

## Agent Execution Instructions

### For coderef-dashboard Agent

1. Navigate to `coderef-dashboard/` subdirectory
2. READ `resources/index.md` → Access analysis and existing code
3. READ `instructions.json` → Follow step-by-step execution plan
4. RUN `/create-workorder` in coderef-dashboard home
5. UPDATE `communication.json` with workorder details
6. EXECUTE 8 tasks sequentially, update status after each
7. CREATE `outputs/implementation-report.md`
8. VALIDATE phase gate checklist

### For coderef-docs Agent

1. Navigate to `coderef-docs/` subdirectory
2. WAIT for Phase 1 completion
3. READ `resources/index.md` → Access implementation outputs
4. GENERATE 3 documentation files using MCP tools
5. UPDATE `communication.json` after each task
6. CREATE `outputs/documentation-report.md`

### For papertrail Agent

1. Navigate to `papertrail/` subdirectory
2. WAIT for Phase 2 documentation completion
3. READ `resources/index.md` → Identify validation targets
4. VALIDATE all communication.json files
5. VALIDATE all resource sheets
6. RUN TypeScript compilation check
7. CREATE `outputs/validation-report.md`

---

## Success Criteria

- ✅ Single universal context menu system working with ANY target (boards, prompts, notes, sessions, favorites)
- ✅ Type-safe EntityConverter and TargetAdapter pattern
- ✅ Pluggable target system (5 adapters: Board full impl + 4 proof of concepts)
- ✅ Multi-target converters (6 converters supporting boards, prompts, sessions)
- ✅ Consistent caching (30s TTL for BoardTargetAdapter)
- ✅ Lazy loading enforced (no eager pre-fetching)
- ✅ Card-level actions for board targets
- ✅ No regressions in file-to-board functionality
- ✅ Documentation with multi-target migration examples
- ✅ 100% validation pass rate

---

## Key Files

**Session-Level:**
- `communication.json` - Agent roster and phase tracking
- `instructions.json` - Orchestrator coordination steps
- `ANALYSIS.md` - Full problem analysis (created in coderef-dashboard/coderef/working/)

**Agent-Level:**
- Each agent has isolated `communication.json`, `instructions.json`, `resources/`, `outputs/`

**Implementation Outputs (coderef-dashboard):**
- `packages/dashboard/src/components/coderef/EntityContextMenu.tsx` (NEW - target-agnostic)
- `packages/dashboard/src/lib/boards/entity-converters.ts` (NEW - 6 multi-target converters)
- `packages/dashboard/src/lib/boards/target-adapters.ts` (NEW - 5 adapters)
- `packages/dashboard/src/components/coderef/AddFileToBoardMenu.tsx` (REFACTORED - uses BoardTargetAdapter)
- `packages/dashboard/src/components/StubCard/index.tsx` (UPDATED - multi-target support)
- `packages/dashboard/src/components/WorkorderCard/index.tsx` (UPDATED - multi-target support)

**Documentation Outputs (coderef-docs):**
- `packages/dashboard/docs/UNIVERSAL-CONTEXT-MENU.md` (migration guide with multi-target examples)
- `packages/dashboard/docs/EntityContextMenu-RESOURCE-SHEET.md`
- `packages/dashboard/docs/EntityConverter-RESOURCE-SHEET.md`
- `packages/dashboard/docs/TargetAdapter-RESOURCE-SHEET.md`

---

## Execution Order

1. **coderef-dashboard** executes Phase 1 (implementation)
2. **coderef-docs** executes Phase 2 tasks (documentation)
3. **papertrail** executes Phase 2 tasks (validation)
4. **Orchestrator** synthesizes results and validates phase gates

---

**Session Created:** 2026-01-20
**Created By:** Claude Sonnet 4.5
**Pattern:** Hierarchical Multi-Agent Session
