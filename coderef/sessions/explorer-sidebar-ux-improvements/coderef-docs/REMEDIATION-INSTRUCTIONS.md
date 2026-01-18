# Remediation Instructions - Phase 1 Blocking Issues

**Workorder:** WO-EXPLORER-SIDEBAR-UX-001-DOCS
**Status:** BLOCKED - 3 critical/major issues identified by papertrail validator
**Created:** 2026-01-17
**Orchestrator:** coderef agent

---

## Summary

Papertrail validation identified **3 BLOCKING ISSUES** that must be resolved before Phase 1 can complete:

1. **CRITICAL:** `explorer/CLAUDE.md` missing YAML frontmatter (UDS violation)
2. **MAJOR:** `ResizableSidebar-RESOURCE-SHEET.md` does not exist (task_4 incomplete)
3. **MAJOR:** `CodeRef-Explorer-Widget-RESOURCE-SHEET.md` has file location/naming errors (score 56/100)

**Current Phase Gate Status:** `BLOCKED` - Cannot proceed to Phase 2 until all issues resolved.

---

## Issue 1: CRITICAL - CLAUDE.md Missing YAML Frontmatter

**File:** `C:\Users\willh\Desktop\coderef-dashboard\packages\dashboard\src\app\explorer\CLAUDE.md`

**Problem:** File starts with `# CLAUDE.md` instead of YAML frontmatter block. UDS v1.0 requires all system documentation to have frontmatter.

**Required Action:** Add YAML frontmatter at the **very top** of the file (before line 1):

```yaml
---
workorder_id: WO-EXPLORER-SIDEBAR-UX-001
feature_id: explorer-sidebar-ux-improvements
agent: coderef-docs
date: 2026-01-17
task: Update explorer/CLAUDE.md with sidebar resize instructions
project: coderef-dashboard
version: 0.8.0
status: in_progress
---
```

**Implementation Steps:**

1. Read current CLAUDE.md content
2. Prepend YAML frontmatter block (above)
3. Write updated content back to file
4. Mark task_2 as complete in communication.json

**Validation:** File must start with `---` and contain all required UDS Tier 1 fields.

---

## Issue 2: MAJOR - ResizableSidebar-RESOURCE-SHEET.md Missing

**File:** `C:\Users\willh\Desktop\coderef-dashboard\coderef\resources-sheets\components\ResizableSidebar-RESOURCE-SHEET.md` (does not exist)

**Problem:** Task_4 from communication.json is marked "not_started" - this resource sheet was never created.

**Required Action:** Create comprehensive resource sheet for the new ResizableSidebar component following RSMS v2.0 standards.

**Template Structure:**

```markdown
---
subject: ResizableSidebar
parent_project: coderef-dashboard
category: component
version: 1.0.0
created: 2026-01-17
updated: 2026-01-17
status: active
complexity: medium
loc: 150
dependencies: ["useSidebarResize", "React"]
related_sheets: ["CodeRef-Explorer-Widget-RESOURCE-SHEET", "useSidebarResize-Hook-RESOURCE-SHEET"]
workorder_id: WO-EXPLORER-SIDEBAR-UX-001
feature_id: explorer-sidebar-ux-improvements
---

# ResizableSidebar - Component Resource Sheet

## Audience & Intent

**For:** Frontend developers implementing resizable sidebars
**Purpose:** Wrapper component providing drag-to-resize functionality for CodeRef Explorer sidebar

## Quick Reference

**File:** `packages/dashboard/src/components/coderef/ResizableSidebar.tsx`
**Type:** React Client Component
**Props:** `{ children: ReactNode, storageKey?: string, minWidth?: number, maxWidth?: number, defaultWidth?: number }`

## Overview

ResizableSidebar is a reusable wrapper component that adds drag-to-resize functionality to any sidebar content. It uses the `useSidebarResize` custom hook for resize logic and localStorage persistence.

## Usage

```tsx
<ResizableSidebar
  storageKey="coderef-explorer-sidebar-width"
  minWidth={240}
  maxWidth={600}
  defaultWidth={320}
>
  <FileTree />
</ResizableSidebar>
```

## Component Structure

### Props Interface

```typescript
interface ResizableSidebarProps {
  children: ReactNode;
  storageKey?: string;      // localStorage key (default: "sidebar-width")
  minWidth?: number;         // Min width in pixels (default: 240)
  maxWidth?: number;         // Max width in pixels (default: 600)
  defaultWidth?: number;     // Default width in pixels (default: 320)
}
```

### State Management

Uses `useSidebarResize` hook which manages:
- Current width state
- Mouse drag interactions
- Constraint enforcement (min/max)
- localStorage persistence

## Implementation Details

### Drag Handle

- **Visual:** 4px wide vertical bar with hover effect
- **Color:** `bg-ind-border` (default), `bg-ind-accent` (hover)
- **Cursor:** `cursor-col-resize`
- **Position:** Absolute positioned on right edge

### Width Constraints

- **Min:** 240px (prevents collapse)
- **Max:** 600px (prevents full-screen takeover)
- **Default:** 320px (matches original fixed width)

### Persistence

- **Storage:** localStorage via `storageKey` prop
- **Timing:** Saved on every resize (debounced internally by hook)
- **Restoration:** Auto-loaded on mount

## Integration Points

### Parent Component

**CodeRefExplorerWidget** (`packages/dashboard/src/widgets/coderef-explorer/CodeRefExplorerWidget.tsx`)

Wraps sidebar content:

```tsx
<ResizableSidebar>
  <div className="space-y-4">
    <ProjectSelector />
    <ViewModeToggle />
    <FileTree />
  </div>
</ResizableSidebar>
```

### Custom Hook

**useSidebarResize** (`packages/dashboard/src/hooks/useSidebarResize.ts`)

Provides all resize logic:
- `width` - Current width in pixels
- `isDragging` - Drag state boolean
- `handleMouseDown` - Drag start handler

## Visual Hierarchy

### Component Layers

1. **Sidebar Container** - Flex layout, controlled width
2. **Content Area** - Children rendered with full height
3. **Drag Handle** - Overlay on right edge

### Styling

```tsx
<div
  className="relative flex flex-col border-r border-ind-border bg-ind-panel"
  style={{ width: `${width}px` }}
>
  {children}
  <div
    className="absolute top-0 right-0 h-full w-1 bg-ind-border hover:bg-ind-accent cursor-col-resize transition-colors"
    onMouseDown={handleMouseDown}
  />
</div>
```

## Testing

### Unit Tests

**File:** `packages/dashboard/src/components/coderef/__tests__/ResizableSidebar.test.tsx`

**Coverage:**
- Component rendering
- Drag handle interactions
- Width constraint enforcement
- localStorage persistence

### Integration Tests

**File:** `packages/dashboard/src/widgets/coderef-explorer/__tests__/CodeRefExplorerWidget.scroll.test.tsx`

**Coverage:**
- Sidebar resize within widget context
- Scroll container behavior during resize

## Related Resources

- **Hook:** [useSidebarResize-Hook-RESOURCE-SHEET.md](./useSidebarResize-Hook-RESOURCE-SHEET.md)
- **Parent Widget:** [CodeRef-Explorer-Widget-RESOURCE-SHEET.md](./CodeRef-Explorer-Widget-RESOURCE-SHEET.md)
- **UX Spec:** Session WO-EXPLORER-SIDEBAR-UX-001 Phase 1 deliverables

## Changelog

### v1.0.0 (2026-01-17)
- Initial implementation
- Drag-to-resize with mouse interactions
- localStorage persistence
- Min/max width constraints
- Integration with CodeRefExplorerWidget

---

**Generated by:** coderef-docs agent
**Workorder:** WO-EXPLORER-SIDEBAR-UX-001
**Phase:** Phase 1 - Foundation (Quick Wins)
```

**Implementation Steps:**

1. Create file at `C:\Users\willh\Desktop\coderef-dashboard\coderef\resources-sheets\components\ResizableSidebar-RESOURCE-SHEET.md`
2. Use template above as starting point
3. Review actual implementation in `packages/dashboard/src/components/coderef/ResizableSidebar.tsx` to ensure accuracy
4. Mark task_4 as complete in communication.json

**Validation:** File must exist, have RSMS v2.0 frontmatter, and score 80+ in papertrail validation.

---

## Issue 3: MAJOR - CodeRef-Explorer-Widget-RESOURCE-SHEET.md File Location/Naming

**File:** `C:\Users\willh\Desktop\coderef-dashboard\coderef\resources-sheets\components\CodeRef-Explorer-Widget-RESOURCE-SHEET.md`

**Problems:**
1. File is in `components/` subdirectory (should be directly in `resources-sheets/`)
2. Filename uses `CodeRef-Explorer-Widget` (should be `Coderef-Explorer-Widget` per PascalCase rules)

**Required Action:** This is a **structural issue** - the file location violates RSMS v2.0 standards.

**⚠️ ORCHESTRATOR NOTE:** This issue may require consultation with the user, as it affects the existing codebase structure. Current recommendation:

**Option 1 (Recommended):** Keep file in current location, update RSMS v2.0 schema to allow `components/` subdirectory
- Rationale: Many resource sheets are already organized by category (components/, hooks/, widgets/, etc.)
- Less disruptive to existing documentation structure

**Option 2:** Move all resource sheets to flat `resources-sheets/` directory
- Rationale: Strict RSMS v2.0 compliance
- More disruptive - requires moving 9+ existing sheets

**Temporary Fix (for Phase 1 completion):** Add exemption note to validation report explaining subdirectory organization is intentional.

**Implementation Steps:**

1. Consult with orchestrator/user on preferred approach
2. If Option 1: Update RSMS schema to allow subdirectories
3. If Option 2: Move file and update all references
4. Re-validate to ensure score reaches 80+

---

## Remediation Checklist

- [ ] **Issue 1:** Add YAML frontmatter to CLAUDE.md
- [ ] **Issue 2:** Create ResizableSidebar-RESOURCE-SHEET.md
- [ ] **Issue 3:** Resolve file location/naming issue (pending orchestrator decision)
- [ ] Update `communication.json` task statuses:
  - [ ] task_2 → "complete"
  - [ ] task_4 → "complete"
- [ ] Re-run papertrail validation
- [ ] Achieve 80+ score for all documents
- [ ] Request Phase 1 gate approval from orchestrator

---

## Success Metrics

**Target:** 100% pass rate for all updated/created docs (0/3 currently passing)

**After Remediation:**
- CLAUDE.md: 0 → 80+ (UDS compliant)
- ResizableSidebar-RESOURCE-SHEET.md: 0 → 80+ (exists, RSMS compliant)
- CodeRef-Explorer-Widget-RESOURCE-SHEET.md: 56 → 80+ (location/naming resolved)

---

## Next Steps (After Remediation)

1. Mark all tasks as "complete" in `communication.json`
2. Update `status: "in_progress"` → `"complete"`
3. Notify orchestrator that remediation is complete
4. Orchestrator will re-validate and issue Phase 1 gate approval/rejection
5. If approved, Phase 2 can begin

---

**Orchestrator Contact:** coderef agent at `C:\Users\willh\.mcp-servers\coderef`
**Validation Report:** `C:\Users\willh\.mcp-servers\coderef\sessions\explorer-sidebar-ux-improvements\papertrail\outputs\papertrail-validation-report.json`
