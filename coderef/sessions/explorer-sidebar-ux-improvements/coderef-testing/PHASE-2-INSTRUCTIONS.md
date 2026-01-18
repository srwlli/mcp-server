# Phase 2 Testing Instructions - coderef-testing Agent

**Workorder:** WO-EXPLORER-SIDEBAR-UX-001-TESTING-PHASE2
**Parent Session:** WO-EXPLORER-SIDEBAR-UX-001
**Phase:** Phase 2 - Navigation Enhancements
**Agent:** coderef-testing
**Created:** 2026-01-17
**Status:** Ready to execute

---

## Context

Dashboard agent has completed Phase 2 implementation with **3 new components**:

1. **QuickFileSearch.tsx** - Search input with fuzzy matching
2. **TreeActionsToolbar.tsx** - Expand all/collapse all/refresh buttons
3. **fuzzyMatch.ts** - Fuzzy matching utility functions

**Files Modified:**
- CodeRefExplorerWidget.tsx (integrated new components)
- FileTree.tsx (added search filtering logic)
- ResizableSidebar.tsx (added collapse toggle functionality)

---

## Your Mission

Create comprehensive test coverage for Phase 2 features following the same patterns used in Phase 1.

**Target Coverage:** 80%+ for new components
**Test Types:** Unit tests + Integration tests

---

## Tasks

### Task 1: Create QuickFileSearch.test.tsx

**File:** `packages/dashboard/src/components/coderef/__tests__/QuickFileSearch.test.tsx`

**Test Coverage:**
- ✅ Component renders with search input
- ✅ Search icon displays
- ✅ Clear button appears when input has value
- ✅ Clear button hidden when input is empty
- ✅ onChange callback fires when typing
- ✅ Clear button clears input and calls onChange with empty string
- ✅ Keyboard shortcut hint displays (⌘K or Ctrl+K based on platform)
- ✅ Input has proper placeholder text
- ✅ Tailwind styling applies correctly (ind-* tokens)

**Template:**
```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import QuickFileSearch from '../QuickFileSearch';

describe('QuickFileSearch', () => {
  it('renders search input', () => {
    const onSearch = jest.fn();
    render(<QuickFileSearch searchQuery="" onSearchChange={onSearch} />);
    expect(screen.getByPlaceholderText(/search files/i)).toBeInTheDocument();
  });

  it('calls onSearchChange when typing', () => {
    const onSearch = jest.fn();
    render(<QuickFileSearch searchQuery="" onSearchChange={onSearch} />);
    const input = screen.getByPlaceholderText(/search files/i);
    fireEvent.change(input, { target: { value: 'test' } });
    expect(onSearch).toHaveBeenCalledWith('test');
  });

  // Add remaining tests...
});
```

---

### Task 2: Create fuzzyMatch.test.ts

**File:** `packages/dashboard/src/lib/coderef/__tests__/fuzzyMatch.test.ts`

**Test Coverage:**
- ✅ Exact matches return true
- ✅ Case-insensitive matches work
- ✅ Substring matches work
- ✅ Non-matches return false
- ✅ Empty query matches everything
- ✅ File path matching works correctly
- ✅ Special characters handled properly
- ✅ Edge cases (null, undefined, empty strings)

**Template:**
```typescript
import { fuzzyMatch, fuzzyMatchPath } from '../fuzzyMatch';

describe('fuzzyMatch', () => {
  it('matches exact strings', () => {
    expect(fuzzyMatch('test', 'test')).toBe(true);
  });

  it('matches case-insensitively', () => {
    expect(fuzzyMatch('Test', 'test')).toBe(true);
    expect(fuzzyMatch('TEST', 'test')).toBe(true);
  });

  it('matches substrings', () => {
    expect(fuzzyMatch('testfile.tsx', 'file')).toBe(true);
  });

  it('returns false for non-matches', () => {
    expect(fuzzyMatch('test', 'xyz')).toBe(false);
  });

  it('handles empty query (matches all)', () => {
    expect(fuzzyMatch('anything', '')).toBe(true);
  });

  // Add remaining tests...
});

describe('fuzzyMatchPath', () => {
  it('matches file paths correctly', () => {
    expect(fuzzyMatchPath('src/components/Button.tsx', 'button')).toBe(true);
    expect(fuzzyMatchPath('src/components/Button.tsx', 'comp/but')).toBe(true);
  });

  // Add remaining tests...
});
```

---

### Task 3: Create TreeActionsToolbar.test.tsx

**File:** `packages/dashboard/src/components/coderef/__tests__/TreeActionsToolbar.test.tsx`

**Test Coverage:**
- ✅ Toolbar renders with 3 buttons
- ✅ Expand All button calls onExpandAll
- ✅ Collapse All button calls onCollapseAll
- ✅ Refresh button calls onRefresh
- ✅ Buttons have proper tooltips
- ✅ Icons render correctly
- ✅ Tailwind styling applies (ind-* tokens)
- ✅ Hover states work

**Template:**
```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import TreeActionsToolbar from '../TreeActionsToolbar';

describe('TreeActionsToolbar', () => {
  it('renders all action buttons', () => {
    const mockExpand = jest.fn();
    const mockCollapse = jest.fn();
    const mockRefresh = jest.fn();

    render(
      <TreeActionsToolbar
        onExpandAll={mockExpand}
        onCollapseAll={mockCollapse}
        onRefresh={mockRefresh}
      />
    );

    expect(screen.getByTitle(/expand all/i)).toBeInTheDocument();
    expect(screen.getByTitle(/collapse all/i)).toBeInTheDocument();
    expect(screen.getByTitle(/refresh/i)).toBeInTheDocument();
  });

  it('calls onExpandAll when expand button clicked', () => {
    const mockExpand = jest.fn();
    render(<TreeActionsToolbar onExpandAll={mockExpand} onCollapseAll={jest.fn()} onRefresh={jest.fn()} />);

    fireEvent.click(screen.getByTitle(/expand all/i));
    expect(mockExpand).toHaveBeenCalled();
  });

  // Add remaining tests...
});
```

---

### Task 4: Create FileTree Integration Tests for Search

**File:** `packages/dashboard/src/components/coderef/__tests__/FileTree.search.test.tsx`

**Test Coverage:**
- ✅ FileTree filters nodes based on searchQuery prop
- ✅ Matching files show in results
- ✅ Non-matching files are hidden
- ✅ Parent directories with matching children remain visible
- ✅ Empty search query shows all files
- ✅ Search is case-insensitive
- ✅ Search updates when query changes

**Template:**
```typescript
import { render, screen } from '@testing-library/react';
import FileTree from '../FileTree';

const mockFileTree = [
  { id: '1', name: 'src', type: 'directory', children: [
    { id: '2', name: 'Button.tsx', type: 'file' },
    { id: '3', name: 'Input.tsx', type: 'file' }
  ]},
  { id: '4', name: 'README.md', type: 'file' }
];

describe('FileTree Search', () => {
  it('shows all files when search is empty', () => {
    render(<FileTree files={mockFileTree} searchQuery="" onFileSelect={jest.fn()} />);
    expect(screen.getByText('Button.tsx')).toBeInTheDocument();
    expect(screen.getByText('Input.tsx')).toBeInTheDocument();
    expect(screen.getByText('README.md')).toBeInTheDocument();
  });

  it('filters files based on search query', () => {
    render(<FileTree files={mockFileTree} searchQuery="button" onFileSelect={jest.fn()} />);
    expect(screen.getByText('Button.tsx')).toBeInTheDocument();
    expect(screen.queryByText('Input.tsx')).not.toBeInTheDocument();
  });

  // Add remaining tests...
});
```

---

### Task 5: Create ResizableSidebar Collapse Tests

**File:** `packages/dashboard/src/components/coderef/__tests__/ResizableSidebar.collapse.test.tsx`

**Test Coverage:**
- ✅ Collapse button renders
- ✅ Clicking collapse toggles sidebar visibility
- ✅ Collapsed state persists to localStorage
- ✅ Sidebar width saved before collapse
- ✅ Previous width restored on expand
- ✅ Collapse animation plays smoothly
- ✅ Drag handle disabled when collapsed

**Template:**
```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import ResizableSidebar from '../ResizableSidebar';

describe('ResizableSidebar Collapse', () => {
  it('renders collapse toggle button', () => {
    render(<ResizableSidebar><div>Content</div></ResizableSidebar>);
    expect(screen.getByTitle(/collapse sidebar/i)).toBeInTheDocument();
  });

  it('collapses sidebar when toggle clicked', () => {
    render(<ResizableSidebar><div>Content</div></ResizableSidebar>);
    const toggle = screen.getByTitle(/collapse sidebar/i);

    fireEvent.click(toggle);

    // Sidebar should have width: 0 or be hidden
    const sidebar = screen.getByTestId('resizable-sidebar');
    expect(sidebar).toHaveStyle({ width: '0px' });
  });

  // Add remaining tests...
});
```

---

## Execution Steps

1. **Read dashboard Phase 2 output** to understand implementation details
2. **Create test files** in order (Tasks 1-5)
3. **Run tests:** `npm test` to verify all pass
4. **Check coverage:** `npm run test:coverage` to verify 80%+ on new files
5. **Update communication.json:**
   - Add all test files to `files_created` array
   - Mark each task status='complete'
   - Add test metrics (files created, coverage %)
6. **Create output summary:** `outputs/coderef-testing-phase2-output.md`
7. **Mark status='complete'** with timestamp

---

## Success Criteria

- ✅ 5 test files created
- ✅ All tests passing (`npm test`)
- ✅ 80%+ coverage on new Phase 2 components
- ✅ Integration tests validate search filtering
- ✅ Collapse functionality fully tested
- ✅ communication.json updated with all files

---

## Expected Output Files

1. `QuickFileSearch.test.tsx` (~150 lines)
2. `fuzzyMatch.test.ts` (~200 lines)
3. `TreeActionsToolbar.test.tsx` (~100 lines)
4. `FileTree.search.test.tsx` (~150 lines)
5. `ResizableSidebar.collapse.test.tsx` (~120 lines)

**Total:** ~720 lines of test code

---

## Phase Gate Contribution

Your completion of these tests is **required** for Phase 2 gate approval. The orchestrator will not approve Phase 2 until:
- All test files created
- All tests passing
- Coverage targets met

---

**Ready to execute?** Follow the steps above and update your communication.json as you progress!
