# Archived Specifications

**Archive Date:** 2026-01-04
**Archived By:** Assistant (Orchestrator)

---

## Archived Items

### `resource-sheet-typescript-spec/` (TypeScript Design Specification)

**Original Location:** `modules/resource-sheet/`
**Original Workorder:** WO-RESOURCE-SHEET-MCP-TOOL-001
**Archive Reason:** Superseded by Python implementation
**Active Implementation:** `resource_sheet/` (Python)

#### Why Archived?

The TypeScript specification was the **original design document** for the Resource Sheet MCP Tool. During implementation, the team discovered that **MCP servers must be written in Python**, not TypeScript.

The design was **migrated to Python** and evolved into the current production system at:
- **Active location:** `coderef-docs/resource_sheet/` (Python)
- **Active workorder:** WO-RESOURCE-SHEET-CONSOLIDATION-001
- **Status:** Production (Phase 1 complete, 13/13 tests passing)

#### Why Preserved?

The TypeScript specification contains **valuable design documentation**:
- Comprehensive system architecture (880-line README)
- Manual workflow guides for AI agents
- Category classification guide (24 element categories)
- Module catalog with auto-fill specifications
- Design rationale and examples

This documentation informed the Python implementation and remains useful as a **reference specification**.

#### Key Files Preserved

```
resource-sheet-typescript-spec/
├── README.md (880 lines) - Complete system guide
├── RESOURCE-SHEET-SYSTEM.md - Manual workflow guide
├── MODULE-CATEGORIES-GUIDE.md - Category classification
├── types.ts - TypeScript type definitions
├── index.ts - Main orchestrator specification
├── detection/ - analyzer, classifier, selector specs
├── composition/ - composer spec
├── output/ - markdown/schema/jsdoc generator specs
├── _universal/ - 4 universal module templates
└── conditional/ - 11 conditional module templates
```

#### Migration Summary

| Aspect | TypeScript Spec (Archived) | Python Implementation (Active) |
|--------|---------------------------|-------------------------------|
| **Language** | TypeScript | Python ✅ |
| **Status** | Design document | Production |
| **Tests** | None (spec only) | 13/13 passing ✅ |
| **Integration** | Not used | MCP Tool #13 ✅ |
| **Workorder** | WO-RESOURCE-SHEET-MCP-TOOL-001 | WO-RESOURCE-SHEET-CONSOLIDATION-001 |
| **Location** | `archived/specifications/` | `resource_sheet/` ✅ |

---

## Guidelines for Archived Specifications

**DO:**
- Reference for design rationale
- Study architecture patterns
- Understand evolution of system

**DON'T:**
- Import or execute (language mismatch)
- Treat as active implementation
- Modify (historical artifact)

---

**For Active Development:** See `resource_sheet/` (Python implementation)
**For Questions:** Refer to WO-RESOURCE-SHEET-CONSOLIDATION-001
