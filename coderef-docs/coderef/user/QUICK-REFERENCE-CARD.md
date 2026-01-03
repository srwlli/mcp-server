# Resource Sheet Quick Reference Card

**Version:** 1.0.0 | **Updated:** 2026-01-03 | **WO:** WO-RESOURCE-SHEET-CONSOLIDATION-001

---

## Command Syntax

```bash
/create-resource-sheet <target> [element-type] [options]
```

**Examples:**
```bash
/create-resource-sheet src/auth/AuthService.ts
/create-resource-sheet Button.tsx design-system
/create-resource-sheet useHook.ts custom-hook --format markdown,schema
```

---

## Common Options

| Option | Values | Description |
|--------|--------|-------------|
| `element-type` | `top-level-widget`, `stateful-container`, `custom-hook`, etc. | Override auto-detection (20 types available) |
| `--mode` | `reverse-engineer`, `template`, `refresh` | Generation mode (default: reverse-engineer) |
| `--format` | `markdown`, `schema`, `jsdoc`, `all` | Output formats (default: all) |
| `--modules` | Module names (comma-separated) | Force specific modules |

---

## Top 10 Element Types (Quick Reference)

| Rank | Type | Detection Pattern | Use When |
|------|------|-------------------|----------|
| 1 | `top-level-widgets` | `Page$`, `Widget$`, `Dashboard$` | Entry components, route targets |
| 2 | `stateful-containers` | `Provider$`, `Controller$`, `Manager$` | State coordination |
| 3 | `global-state-layer` | `store.ts`, `Context$` | Redux/Zustand/Context |
| 4 | `custom-hooks` | `^use[A-Z]` | Reusable hooks |
| 5 | `api-client` | `client.ts`, `api.ts`, `sdk.ts` | HTTP clients |
| 6 | `data-models` | `types.ts`, `schema.ts`, `validator` | Type definitions |
| 7 | `persistence-subsystem` | `storage.ts`, `cache.ts` | localStorage/indexedDB |
| 8 | `eventing-messaging` | `eventBus`, `messageHub` | Event systems |
| 9 | `routing-navigation` | `router.ts`, `routes.ts` | Router config |
| 10 | `file-tree-primitives` | `TreeNode`, `PathUtils` | Tree structures |

**See full list:** [ELEMENT-TYPE-CATALOG.md](../foundation-docs/ELEMENT-TYPE-CATALOG.md)

---

## Module Selection Cheat Sheet

### Universal Modules (Always Included)
1. **Architecture** - Component hierarchy, integration points
2. **Integration** - External dependencies, contracts
3. **Testing** - Test strategy (stub - manual fill)
4. **Performance** - Performance notes (stub - manual fill)

### Conditional Modules (Selected by Element Type)
- **UI Modules:** `composition`, `events`, `accessibility`
- **State Modules:** `management`, `lifecycle`, `persistence`
- **Network Modules:** `endpoints`, `auth`, `retry`, `errors`
- **Hooks Modules:** `signature`, `side_effects`

---

## Auto-Fill Rates (Expected Completion %)

| Section | Auto-Fill % | Source |
|---------|-------------|--------|
| Header Metadata | 100% | System |
| Architecture Overview | 70-90% | Graph |
| Dependencies | 90% | Graph imports |
| Public API | 95% | Graph exports |
| Event Contracts | 60-80% | TypeScript types |
| State Ownership | 40-60% | Code analysis |
| Testing Scenarios | 20-40% | Test files |
| Executive Summary | 30-50% | Synthesis |
| Non-Goals | 0% | Manual |
| Performance Limits | 10-30% | Manual |

**Overall Target:** 60-80% auto-fill

---

## Quality Gate Checklist (Pre-Submission)

Before finalizing, verify:

- [ ] **Structural:** Header, summary, required sections present
- [ ] **Content:** No placeholders in critical sections
- [ ] **Element-Specific:** All type requirements met
- [ ] **Refactor-Safe:** State ownership, failure recovery, contracts defined
- [ ] **Auto-Fill:** >= 60% completion rate

**Validation Statuses:**
- ✅ **APPROVED:** All checks pass
- ⚠️ **APPROVED_WITH_WARNINGS:** ≤2 major issues
- ❌ **REJECTED:** Critical failures

---

## Troubleshooting (Quick Fixes)

### Issue: "Low auto-fill rate (<60%)"
**Fix:** Regenerate `.coderef/index.json`
```bash
python scripts/populate-coderef.py /path/to/project
```

### Issue: "Element type detection ambiguous"
**Fix:** Manually specify type
```bash
/create-resource-sheet file.ts custom-hook
```

### Issue: "Missing state ownership table"
**Fix:** Add table manually:
```markdown
| State | Owner | Type | Persistence | Source of Truth |
|-------|-------|------|-------------|-----------------|
```

### Issue: "Validation failed - hedging detected"
**Fix:** Replace "should probably" → "must", "might" → "will"

---

## Output Locations

| Format | Location | Use Case |
|--------|----------|----------|
| Markdown | `coderef/workorder/{feature}/docs/` | Human-readable docs |
| JSON Schema | `coderef/workorder/{feature}/schemas/` | Validation, tooling |
| JSDoc | Inline in source code | IDE autocomplete |

---

## Performance Benchmarks

| Operation | Target Time | Typical Time |
|-----------|-------------|--------------|
| Element type detection | <100ms | 50-80ms |
| Graph loading | <500ms | 100-300ms |
| Graph queries (4 parallel) | <50ms | 20-40ms |
| Template generation | <2s | 1-1.5s |
| Validation pipeline | <1s | 500-800ms |
| **Total end-to-end** | **<3s** | **2-2.5s** |

**Speedup vs manual:** 150-300x faster (5 min vs 30-60 min)

---

## Quick Links

- **User Guide:** [RESOURCE-SHEET-USER-GUIDE.md](RESOURCE-SHEET-USER-GUIDE.md)
- **Module Reference:** [MODULE-REFERENCE.md](../foundation-docs/MODULE-REFERENCE.md)
- **Element Catalog:** [ELEMENT-TYPE-CATALOG.md](../foundation-docs/ELEMENT-TYPE-CATALOG.md)
