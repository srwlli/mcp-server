# Phase 2 Documentation Instructions - coderef-docs Agent

**Workorder:** WO-EXPLORER-SIDEBAR-UX-001-DOCS-PHASE2
**Parent Session:** WO-EXPLORER-SIDEBAR-UX-001
**Phase:** Phase 2 - Navigation Enhancements
**Agent:** coderef-docs
**Created:** 2026-01-17
**Status:** Ready to execute

---

## Context

Dashboard agent has completed Phase 2 implementation with **3 new features**:

1. **Quick File Search** - Fuzzy matching search with keyboard shortcut (⌘K/Ctrl+K)
2. **Tree Actions Toolbar** - Expand all, collapse all, refresh buttons
3. **Collapsible Sidebar Toggle** - Collapse/expand sidebar with persistence

**New Components:**
- `QuickFileSearch.tsx`
- `TreeActionsToolbar.tsx`
- `fuzzyMatch.ts` (utility)

**Modified Components:**
- `CodeRefExplorerWidget.tsx` (integrated new features)
- `FileTree.tsx` (added search filtering)
- `ResizableSidebar.tsx` (added collapse toggle)

---

## Your Mission

Update all Explorer-related documentation to reflect Phase 2 features, following the same RSMS v2.0 patterns used in Phase 1.

**Target:** 100% documentation coverage for new features
**Standard:** RSMS v2.0 + UDS v1.0 compliance

---

## Tasks

### Task 1: Create QuickFileSearch-RESOURCE-SHEET.md

**File:** `C:\Users\willh\Desktop\coderef-dashboard\coderef\resources-sheets\components\QuickFileSearch-RESOURCE-SHEET.md`

**Required Sections:**
1. **Frontmatter** (RSMS v2.0)
   ```yaml
   ---
   subject: QuickFileSearch
   parent_project: coderef-dashboard
   category: component
   version: 1.0.0
   created: 2026-01-17
   updated: 2026-01-17
   status: active
   complexity: medium
   loc: 120
   dependencies: ["fuzzyMatch", "React"]
   related_sheets: ["FileTree-RESOURCE-SHEET", "CodeRef-Explorer-Widget-RESOURCE-SHEET"]
   workorder_id: WO-EXPLORER-SIDEBAR-UX-001
   feature_id: explorer-sidebar-ux-improvements
   phase: phase_2
   ---
   ```

2. **Executive Summary** - Component purpose and role
3. **Architecture Overview** - File structure, dependencies, design patterns
4. **Component API** - Props interface with detailed explanations
5. **State Management** - Internal state (searchQuery value)
6. **Integration Points** - Parent component integration (CodeRefExplorerWidget)
7. **Keyboard Shortcuts** - ⌘K/Ctrl+K documentation
8. **Performance Considerations** - Debouncing search input (if implemented)
9. **Testing Strategy** - Unit tests, integration tests
10. **Common Pitfalls** - Typical mistakes and solutions
11. **Future Enhancements** - Advanced search features, filters

**Estimated Length:** ~400 lines

---

### Task 2: Create TreeActionsToolbar-RESOURCE-SHEET.md

**File:** `C:\Users\willh\Desktop\coderef-dashboard\coderef\resources-sheets\components\TreeActionsToolbar-RESOURCE-SHEET.md`

**Required Sections:**
1. **Frontmatter** (RSMS v2.0)
   ```yaml
   ---
   subject: TreeActionsToolbar
   parent_project: coderef-dashboard
   category: component
   version: 1.0.0
   created: 2026-01-17
   updated: 2026-01-17
   status: active
   complexity: low
   loc: 80
   dependencies: ["React", "lucide-react"]
   related_sheets: ["FileTree-RESOURCE-SHEET", "CodeRef-Explorer-Widget-RESOURCE-SHEET"]
   workorder_id: WO-EXPLORER-SIDEBAR-UX-001
   feature_id: explorer-sidebar-ux-improvements
   phase: phase_2
   ---
   ```

2. **Executive Summary** - Toolbar purpose and actions
3. **Architecture Overview** - Button composition, icon usage
4. **Component API** - Props (onExpandAll, onCollapseAll, onRefresh)
5. **Integration Points** - FileTree state management
6. **Visual Design** - Icon-only buttons with tooltips
7. **Accessibility** - ARIA labels, keyboard navigation
8. **Testing Strategy** - Click handlers, tooltip display
9. **Future Enhancements** - Additional actions (copy path, open in editor)

**Estimated Length:** ~300 lines

---

### Task 3: Create fuzzyMatch-Utility-RESOURCE-SHEET.md

**File:** `C:\Users\willh\Desktop\coderef-dashboard\coderef\resources-sheets\utilities\fuzzyMatch-Utility-RESOURCE-SHEET.md`

**Required Sections:**
1. **Frontmatter** (RSMS v2.0)
   ```yaml
   ---
   subject: fuzzyMatch
   parent_project: coderef-dashboard
   category: utility
   version: 1.0.0
   created: 2026-01-17
   updated: 2026-01-17
   status: active
   complexity: low
   loc: 50
   dependencies: []
   related_sheets: ["QuickFileSearch-RESOURCE-SHEET"]
   workorder_id: WO-EXPLORER-SIDEBAR-UX-001
   feature_id: explorer-sidebar-ux-improvements
   phase: phase_2
   ---
   ```

2. **Executive Summary** - Fuzzy matching utility purpose
3. **API Reference** - Function signatures (fuzzyMatch, fuzzyMatchPath)
4. **Algorithm Details** - How matching works (substring, case-insensitive)
5. **Usage Examples** - Code examples for common use cases
6. **Performance** - Time complexity, optimization opportunities
7. **Testing Strategy** - Edge cases, special characters
8. **Future Enhancements** - Advanced fuzzy algorithms (Levenshtein distance)

**Estimated Length:** ~250 lines

---

### Task 4: Update CodeRef-Explorer-Widget-RESOURCE-SHEET.md

**File:** `C:\Users\willh\Desktop\coderef-dashboard\coderef\resources-sheets\components\CodeRef-Explorer-Widget-RESOURCE-SHEET.md`

**Updates Required:**

1. **Component Hierarchy Section** - Add QuickFileSearch and TreeActionsToolbar
   ```markdown
   CodeRefExplorerWidget
   ├── ResizableSidebar
   │   ├── QuickFileSearch (NEW - Phase 2)
   │   ├── TreeActionsToolbar (NEW - Phase 2)
   │   ├── ProjectSelector
   │   ├── ViewModeToggle
   │   └── FileTree (enhanced with search filtering)
   └── FileViewer
   ```

2. **Design Rationale** - Add Phase 2 UX improvements
   - Quick file search for large file trees
   - Tree actions toolbar for bulk operations
   - Collapsible sidebar for focus mode

3. **Dependencies** - Add new dependencies
   - QuickFileSearch
   - TreeActionsToolbar
   - fuzzyMatch utility

4. **State Management** - Add new state variables
   - `searchQuery: string` - Current search filter
   - `isCollapsed: boolean` - Sidebar collapse state

5. **localStorage Keys** - Add new keys
   - `coderef-explorer-sidebar-collapsed` - Collapse state persistence

6. **Phase 2 Features Section** (new)
   - Quick file search with ⌘K shortcut
   - Tree actions toolbar (expand/collapse all, refresh)
   - Sidebar collapse toggle

7. **Update frontmatter version** - Bump to v1.1.0

---

### Task 5: Update FileTree-RESOURCE-SHEET.md

**File:** `C:\Users\willh\Desktop\coderef-dashboard\coderef\resources-sheets\components\FileTree-RESOURCE-SHEET.md`

**Updates Required:**

1. **Props Interface** - Add searchQuery prop
   ```typescript
   interface FileTreeProps {
     files: FileNode[];
     searchQuery?: string; // NEW - Phase 2
     onFileSelect: (file: FileNode) => void;
   }
   ```

2. **Search Filtering Logic** (new section)
   - Recursive tree filtering algorithm
   - Auto-expansion of nodes with matches
   - Highlight matched text (if implemented)

3. **Performance Considerations** - Search filtering optimization
   - Memoization of filtered results
   - Debouncing search input

4. **Integration with QuickFileSearch** - Data flow diagram

5. **Update frontmatter version** - Bump to v1.1.0

---

### Task 6: Update ResizableSidebar-RESOURCE-SHEET.md

**File:** `C:\Users\willh\Desktop\coderef-dashboard\coderef\resources-sheets\components\ResizableSidebar-RESOURCE-SHEET.md`

**Updates Required:**

1. **Props Interface** - Add collapse-related props (if any)
   ```typescript
   interface ResizableSidebarProps {
     children: ReactNode;
     storageKey?: string;
     minWidth?: number;
     maxWidth?: number;
     defaultWidth?: number;
     collapsible?: boolean; // NEW - Phase 2 (if implemented)
   }
   ```

2. **Collapse Toggle Feature** (new section)
   - Collapse button UI
   - Collapse/expand animation
   - Width restoration logic
   - localStorage persistence

3. **localStorage Keys** - Add collapse state key
   - `{storageKey}-collapsed` - Boolean collapse state

4. **State Management** - Add collapse state
   - `isCollapsed: boolean`

5. **Update frontmatter version** - Bump to v1.1.0

---

### Task 7: Update explorer/CLAUDE.md

**File:** `C:\Users\willh\Desktop\coderef-dashboard\packages\dashboard\src\app\explorer\CLAUDE.md`

**Updates Required:**

1. **Component Reference** - Add new components
   - QuickFileSearch
   - TreeActionsToolbar
   - fuzzyMatch utility

2. **Common Tasks** - Add Phase 2 tasks
   - "Using Quick File Search (⌘K/Ctrl+K)"
   - "Expanding/Collapsing All Tree Nodes"
   - "Collapsing Sidebar for Focus Mode"

3. **Keyboard Shortcuts** (new section)
   - ⌘K / Ctrl+K: Focus file search

4. **localStorage Keys** - Add new keys
   - `coderef-explorer-sidebar-collapsed`

5. **Performance Notes** - Search filtering considerations

6. **Update frontmatter** - Update `updated` date to 2026-01-17

---

### Task 8: Update resource-sheet-index.md

**File:** `C:\Users\willh\Desktop\coderef-dashboard\packages\dashboard\src\app\explorer\resource-sheet-index.md`

**Updates Required:**

1. **Total Count** - Update from 10 to 13 resource sheets

2. **Core Explorer Components** - Add 3 new entries
   - #11: QuickFileSearch (~400 lines)
   - #12: TreeActionsToolbar (~300 lines)

3. **Supporting Utilities** - Add fuzzyMatch
   - #13: fuzzyMatch Utility (~250 lines)

4. **Summary Table** - Add 3 new rows

5. **Component Dependency Graph** - Update to show:
   - QuickFileSearch → fuzzyMatch
   - TreeActionsToolbar → FileTree
   - CodeRefExplorerWidget → QuickFileSearch, TreeActionsToolbar

6. **Recent Updates** - Add Phase 2 entry
   ```markdown
   ### 2026-01-17 - Phase 2: Navigation Enhancements
   - Added QuickFileSearch component with fuzzy matching
   - Added TreeActionsToolbar with expand/collapse/refresh actions
   - Added fuzzyMatch utility for search filtering
   - Updated CodeRefExplorerWidget with Phase 2 integrations
   - Updated FileTree with search filtering logic
   - Updated ResizableSidebar with collapse toggle
   ```

7. **Last Updated** - Change to 2026-01-17

---

## Execution Steps

1. **Read dashboard Phase 2 output** to understand implementation details
2. **Create new resource sheets** (Tasks 1-3)
3. **Update existing resource sheets** (Tasks 4-6)
4. **Update CLAUDE.md** (Task 7)
5. **Update resource-sheet-index.md** (Task 8)
6. **Validate all docs** with Papertrail (optional self-check)
7. **Update communication.json:**
   - Add all files to `files_created` / `files_modified` arrays
   - Mark each task status='complete'
   - Add metrics (files created: 3, files modified: 5)
8. **Create output summary:** `outputs/coderef-docs-phase2-output.md`
9. **Mark status='complete'** with timestamp

---

## Success Criteria

- ✅ 3 new resource sheets created (QuickFileSearch, TreeActionsToolbar, fuzzyMatch)
- ✅ 3 existing resource sheets updated (CodeRef-Explorer-Widget, FileTree, ResizableSidebar)
- ✅ CLAUDE.md updated with Phase 2 features
- ✅ resource-sheet-index.md updated with new entries
- ✅ All docs follow RSMS v2.0 standards
- ✅ Frontmatter versions bumped appropriately
- ✅ communication.json updated with all files

---

## Expected Output Files

**Created:**
1. `QuickFileSearch-RESOURCE-SHEET.md` (~400 lines)
2. `TreeActionsToolbar-RESOURCE-SHEET.md` (~300 lines)
3. `fuzzyMatch-Utility-RESOURCE-SHEET.md` (~250 lines)

**Modified:**
1. `CodeRef-Explorer-Widget-RESOURCE-SHEET.md` (add ~150 lines)
2. `FileTree-RESOURCE-SHEET.md` (add ~100 lines)
3. `ResizableSidebar-RESOURCE-SHEET.md` (add ~80 lines)
4. `explorer/CLAUDE.md` (add ~50 lines)
5. `resource-sheet-index.md` (add ~60 lines)

**Total:** ~1,390 lines of documentation

---

## Phase Gate Contribution

Your completion of these docs is **required** for Phase 2 gate approval. The orchestrator will not approve Phase 2 until:
- All resource sheets created
- All updates complete
- Papertrail validation passes (100% pass rate)

---

**Ready to execute?** Follow the steps above and update your communication.json as you progress!
