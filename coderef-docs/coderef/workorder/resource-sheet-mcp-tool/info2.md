# Explorer Sidebar Documentation Plan

## Overview

Create comprehensive documentation for the Explorer Sidebar (page-specific sidebar in CodeRefExplorerWidget) covering all attributes, characteristics, behaviors, and states.

---

## Deliverables

### 1. Markdown Documentation (coderef/foundation-docs/EXPLORER-SIDEBAR.md)

#### Section 1: Architecture Overview
- Component hierarchy (CodeRefExplorerWidget → FileTree → FileTreeNode → ContextMenu)
- Layout structure (fixed 320px sidebar + responsive main content)
- Integration points with FileViewer, PromptingWorkflow, ProjectSelector

#### Section 2: Attributes & Characteristics
- Fixed dimensions (w-80 min-w-80 max-w-80)
- Overflow handling (overflow-hidden parent, min-w-0 flex fix)
- Styling (border, background, padding)
- Responsive behavior (mobile vs desktop)

#### Section 3: Behaviors
- File selection (click to view, context menu actions)
- Tree expansion/collapse (directory navigation)
- Favorites management (add/remove, group assignment)
- Copy path, add to prompt workflows
- Cross-tab synchronization via localStorage

#### Section 4: States
- View modes (Projects vs CodeRef)
- Project selection state
- Tree expansion state (per-directory)
- Favorites state (per-project persistence)
- File selection state
- Context menu visibility state
- Loading/restoration states

#### Section 5: Integration Points
- ProjectSelector (project switching)
- FileViewer (content display)
- PromptingWorkflow (attachment system)
- ViewModeToggle (view switching)
- localStorage persistence

#### Section 6: Performance Considerations
- Tree rendering optimization (recursive component pattern)
- localStorage quota handling
- Memory usage (favorites data structure)
- Virtualization (future enhancement)

#### Section 7: Accessibility
- Keyboard navigation patterns
- Screen reader support
- ARIA attributes (current gaps)
- Focus management

#### Section 8: Testing Strategy
- Existing test coverage (state, persistence, cross-tab sync)
- Edge cases handled (quota exceeded, corrupt data)
- Integration test scenarios

#### Section 9: Mermaid Diagrams
- State transition diagram (view modes, selection states)
- Component hierarchy tree
- Data flow diagram (localStorage ↔ React state)

---

### 2. JSON Schema (coderef/schemas/explorer-sidebar-schema.json)

- Props interface schemas (FileTreeProps, FileTreeNodeProps, ContextMenuProps)
- State shape schemas (FavoritesData, TreeNode)
- Configuration schema (localStorage keys, data formats)
- Event handler signatures

---

### 3. TypeScript Component Documentation (In-file JSDoc)

- Enhanced JSDoc comments in FileTree.tsx
- Enhanced JSDoc comments in FileTreeNode.tsx
- Enhanced JSDoc comments in ContextMenu.tsx
- Type definitions for all props, states, callbacks

---

## Implementation Steps

1. Analyze existing components (FileTree, FileTreeNode, ContextMenu, CodeRefExplorerWidget)
2. Document current attributes, behaviors, states
3. Create Mermaid diagrams for state transitions and component hierarchy
4. Generate JSON schemas for type validation
5. Add comprehensive JSDoc comments to component files
6. Create markdown reference document
7. Review for completeness and accuracy

---

## Files to Create/Modify

**Create:**
- `coderef/foundation-docs/EXPLORER-SIDEBAR.md`
- `coderef/schemas/explorer-sidebar-schema.json`

**Modify (add JSDoc):**
- `packages/dashboard/src/components/coderef/FileTree.tsx`
- `packages/dashboard/src/components/coderef/FileTreeNode.tsx`
- `packages/dashboard/src/components/coderef/ContextMenu.tsx`
- `packages/dashboard/src/widgets/coderef-explorer/CodeRefExplorerWidget.tsx`

---

## Resource Sheet Template Applied

This documentation plan follows **Template 1: Top-Level Widgets/Pages** from the resource sheet catalog.

### Template Sections Mapped

| Template Section | Explorer Sidebar Section |
|-----------------|-------------------------|
| Role in UX | Architecture Overview |
| Component Hierarchy | Architecture Overview (visual tree) |
| State Ownership Table | States (canonical table format) |
| Layout Contracts | Attributes & Characteristics |
| Event Flow Diagram | Mermaid Diagrams |
| Performance Characteristics | Performance Considerations |
| Accessibility Guarantees | Accessibility |
| Common Integration Pitfalls | Integration Points + Common Pitfalls (TBD) |

### Focus Areas Checklist (Template 1)

- [x] **Composition hierarchy** — FileTree → FileTreeNode → ContextMenu
- [x] **User workflows** — File viewing, favorites management, prompting
- [x] **State orchestration** — View mode, selection, expansion, favorites
- [x] **Integration points** — ProjectSelector, FileViewer, localStorage
- [x] **Layout contracts** — Fixed 320px, min-w-0 flex fix
- [x] **Lifecycle events** — localStorage restoration, cross-tab sync
- [x] **Performance budget** — Tree rendering, localStorage quota
- [x] **Accessibility root** — Keyboard nav gaps, ARIA attributes

---

## Documentation Quality Targets

### Refactor Safety
- ✅ State ownership explicitly defined (prevents conflicts)
- ✅ Integration contracts documented (enables safe component swaps)
- ✅ Failure modes covered (localStorage quota, corrupt data)
- ✅ Recovery paths specified (fallback to defaults)

### Onboarding Optimization
- ✅ Progressive disclosure (summary → architecture → details)
- ✅ Visual aids (3 Mermaid diagrams)
- ✅ Multiple entry points (code JSDoc, markdown guide, JSON schema)

### Maintenance Focus
- ✅ Common pitfalls documented (min-w-0 CSS fix, quota handling)
- ✅ Performance limits tested (up to 500 nodes)
- ✅ Accessibility gaps tracked with priority
- ✅ Non-goals explicit (no virtualization yet)

---

## Example Output Quality

**This plan generates the same quality documentation shown in info.md:**

- **22 KB markdown** with 9 comprehensive sections + 3 diagrams
- **12 KB JSON schema** with validation rules
- **Enhanced JSDoc** in 4 source files with @example, @remarks, @see tags

**Authority Hierarchy:**
```
TypeScript Code = Runtime truth
JSDoc = Inline reference
JSON Schema = Validation truth
Markdown = Architectural truth
```

---

## Lessons Learned (From Example)

### What Worked
- State ownership table prevented localStorage authority confusion
- Mermaid diagrams reduced cognitive load during onboarding
- Failure modes section documented edge cases (quota, corrupt data)
- Performance budgets set clear expectations (500 nodes tested)

### What Was Challenging
- Extracting implicit knowledge (min-w-0 CSS fix not documented)
- Testing coverage unclear without comprehensive test suite
- Accessibility audit required manual WCAG review

### What Could Be Automated
- Props extraction from TypeScript interfaces
- State detection from useState/useReducer hooks
- Integration points from import statements
- Performance profiling from React DevTools

---

## Future Automation (Post WO-RESOURCE-SHEET-MCP-001)

Once the MCP tool is implemented:

**Current Manual Process (3-4 hours):**
1. Read 4 component files
2. Analyze architecture, state, behaviors
3. Follow template checklist
4. Write markdown, schema, JSDoc

**Future Automated Process (30-45 min):**
1. Run `coderef_scan` on component directory
2. Call `generate_resource_sheet` with element_type="top-level-widget"
3. Tool auto-fills 60-70% (state, props, integration)
4. Developer reviews and fills manual sections (rationale, pitfalls)
5. Tool generates markdown + schema + JSDoc suggestions

---

## Ready to Proceed?

This plan provides a **reusable blueprint** for documenting any top-level widget using the resource sheet methodology.

**Next Documentation Targets:**
- ProjectSelector (stateful container - Template 2)
- FileViewer (performance-critical UI - Template 15)
- PromptingWorkflow (command system - Template 11)
- localStorage utilities (persistence subsystem - Template 7)

Each follows the same rigor but uses element-specific templates from the catalog.

---

**Created:** 2026-01-02
**Purpose:** Planning document for Explorer Sidebar comprehensive documentation
**Template Applied:** Resource Sheet Template 1 (Top-Level Widgets/Pages)
**Element Type:** Top-Level Widget
**Estimated Effort:** 3-4 hours (manual) → 30-45 min (automated with MCP tool)
