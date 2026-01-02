# Testing Module

**Type:** Universal (always included)
**Applies to:** All element types
**Auto-fill:** Existing test files, test coverage
**Manual:** Test strategy, coverage gaps, recommended tests

---

## Section: Testing Strategy

### Existing Test Coverage

{{AUTO_FILL: element.test_files}}

**Test Files:**
{{#each element.tests}}
- `{{this.file}}` - {{this.type}} ({{this.test_count}} tests)
{{/each}}

**Coverage:**
{{AUTO_FILL: element.coverage}}
- **Line coverage:** {{element.coverage.lines}}%
- **Branch coverage:** {{element.coverage.branches}}%
- **Function coverage:** {{element.coverage.functions}}%

{{MANUAL: Summarize what is currently tested - Which scenarios are covered? Which user flows have tests?}}

### Coverage Gaps

{{MANUAL: Identify what is NOT tested:

**Missing Unit Tests:**
- [ ] Edge case: ...
- [ ] Error scenario: ...
- [ ] Boundary condition: ...

**Missing Integration Tests:**
- [ ] Integration with component X
- [ ] End-to-end user flow: ...

**Missing Edge Cases:**
- [ ] Performance: Large datasets (N > 1000)
- [ ] Concurrent access
- [ ] Network failures
- [ ] Browser incompatibilities}}

### Test Strategy

{{MANUAL: Describe the testing approach:

**Unit Tests:**
- What should be unit tested?
- What are the critical functions/methods?
- What mocking strategy is used?

**Integration Tests:**
- What integrations need testing?
- How are dependencies mocked?
- What is the test boundary?

**End-to-End Tests:**
- What user flows need E2E coverage?
- What is the success criteria?

**Performance Tests:**
- What are the performance boundaries?
- What datasets are used for testing?
- What are the performance targets?}}

### Recommended Tests

{{MANUAL: Provide specific test recommendations with examples:

**High Priority (Must Have):**

1. **Test Name:** ...
   - **Type:** Unit / Integration / E2E
   - **Scenario:** ...
   - **Expected Behavior:** ...
   - **Test Code Example:**
   ```typescript
   test('should ...', () => {
     // Arrange
     // Act
     // Assert
   });
   ```

2. **Test Name:** ...
   - **Type:** Unit / Integration / E2E
   - **Scenario:** ...
   - **Expected Behavior:** ...

**Medium Priority (Should Have):**
...

**Low Priority (Nice to Have):**
...}}

### Test Data & Fixtures

{{MANUAL: Document test data requirements:

**Fixtures:**
- Where are test fixtures located?
- What sample data is needed?
- How is test data generated?

**Mocks:**
- What needs to be mocked?
- Where are mock implementations?
- How realistic are mocks?

**Test Environment:**
- What environment setup is required?
- Are there test-specific configurations?
- How is state cleaned up between tests?}}

### Regression Safeguards

{{MANUAL: Identify critical tests that prevent regressions:

**Non-Negotiable Tests:**
- Test that must ALWAYS pass
- Core functionality that cannot break
- Known bugs that must not resurface

**Regression History:**
- Past bugs that occurred
- Tests added to prevent recurrence
- Lessons learned}}

---

## Example Output

### Testing Strategy

#### Existing Test Coverage

**Test Files:**
- `src/components/coderef/FileTree.test.tsx` - Unit tests (12 tests)
- `src/components/coderef/FileTreeNode.test.tsx` - Unit tests (8 tests)
- `src/integration/file-browsing.test.tsx` - Integration tests (5 tests)

**Coverage:**
- **Line coverage:** 78%
- **Branch coverage:** 65%
- **Function coverage:** 82%

**Current Coverage:** State management (favorites, expansion) and localStorage persistence are well-tested. Cross-tab synchronization has integration tests. Basic rendering paths are covered.

#### Coverage Gaps

**Missing Unit Tests:**
- [ ] Edge case: Tree with 1000+ nodes (performance boundary)
- [ ] Error scenario: localStorage quota exceeded
- [ ] Edge case: Corrupt favorites JSON in localStorage
- [ ] Boundary: Empty tree (no files)

**Missing Integration Tests:**
- [ ] Integration with PromptingWorkflow (Add to Prompt action)
- [ ] Context menu positioning at viewport edges
- [ ] Keyboard navigation (arrow keys, Enter, Escape)

**Missing Edge Cases:**
- [ ] Performance: Trees >1000 nodes (no virtualization yet)
- [ ] Concurrent favorites updates from multiple tabs
- [ ] File paths with special characters (spaces, unicode)
- [ ] Mobile viewport (touch events, responsive behavior)

#### Test Strategy

**Unit Tests:**
- Test state management logic in isolation (favorites, expansion)
- Mock FileTreeNode and ContextMenu to test FileTree alone
- Use React Testing Library for user interaction simulation
- Snapshot tests for rendering (carefully - avoid brittle tests)

**Integration Tests:**
- Test FileTree + FileTreeNode + ContextMenu together
- Real localStorage (not mocked) to catch storage bugs
- Test cross-tab sync using multiple JSDOM instances
- Verify data flow from CodeRefExplorerWidget → FileTree → FileViewer

**End-to-End Tests:**
- User clicks file → FileViewer loads content
- User adds favorite → Persists across page reload
- User opens new tab → Favorites sync automatically
- User exceeds localStorage quota → Graceful fallback

**Performance Tests:**
- Render tree with 100 nodes - target <50ms
- Render tree with 500 nodes - target <100ms
- Render tree with 1000 nodes - target <200ms (current limit)
- Benchmark favorites write debouncing (should batch multiple changes)

#### Recommended Tests

**High Priority (Must Have):**

1. **Test localStorage quota exceeded**
   - **Type:** Unit
   - **Scenario:** User has 500 favorites, localStorage is full
   - **Expected Behavior:** Log warning, continue with session-only favorites, UI shows warning banner
   - **Test Code Example:**
   ```typescript
   test('should handle localStorage quota exceeded', () => {
     // Arrange
     const mockSetItem = vi.fn(() => {
       throw new DOMException('QuotaExceededError');
     });
     vi.spyOn(Storage.prototype, 'setItem').mockImplementation(mockSetItem);

     // Act
     render(<FileTree tree={largeTree} onFileSelect={vi.fn()} />);
     fireEvent.click(screen.getByText('Add to Favorites'));

     // Assert
     expect(console.warn).toHaveBeenCalledWith('localStorage quota exceeded');
     expect(screen.getByText('Favorites will not persist')).toBeInTheDocument();
   });
   ```

2. **Test cross-tab synchronization**
   - **Type:** Integration
   - **Scenario:** User adds favorite in Tab A, Tab B should update automatically
   - **Expected Behavior:** Tab B's favorites state updates within 100ms of storage event
   - **Test Code Example:**
   ```typescript
   test('should sync favorites across tabs', async () => {
     // Arrange
     const { rerender } = render(<FileTree tree={tree} onFileSelect={vi.fn()} />);

     // Act - Simulate storage event from another tab
     fireEvent(window, new StorageEvent('storage', {
       key: 'coderef_favorites',
       newValue: JSON.stringify({ file1: true }),
     }));

     // Assert
     await waitFor(() => {
       expect(screen.getByTestId('favorite-file1')).toBeInTheDocument();
     });
   });
   ```

**Medium Priority (Should Have):**

3. **Test keyboard navigation**
   - **Type:** Integration
   - **Scenario:** User navigates tree with arrow keys
   - **Expected Behavior:** Focus moves correctly, Enter opens file, Escape closes menu

4. **Test large tree performance**
   - **Type:** Performance
   - **Scenario:** Render tree with 1000 nodes
   - **Expected Behavior:** Initial render <200ms, no frame drops on scroll

**Low Priority (Nice to Have):**

5. **Test mobile touch events**
   - **Type:** E2E
   - **Scenario:** User taps file on mobile device
   - **Expected Behavior:** File opens, no 300ms click delay

#### Test Data & Fixtures

**Fixtures:**
- `src/fixtures/sample-tree.json` - Sample file tree with 50 nodes
- `src/fixtures/large-tree.json` - Large tree with 1000 nodes for performance testing
- `src/fixtures/favorites.json` - Sample favorites data

**Mocks:**
- `src/mocks/localStorage.ts` - In-memory localStorage mock with quota simulation
- `src/mocks/FileTreeNode.tsx` - Simple node mock for FileTree isolation

**Test Environment:**
- JSDOM for browser APIs (localStorage, storage events)
- Vitest for test runner
- React Testing Library for DOM queries
- State cleanup: Clear localStorage after each test with `afterEach(() => localStorage.clear())`

#### Regression Safeguards

**Non-Negotiable Tests:**
1. **Favorites persist across page reload** - Core feature, tested in integration suite
2. **Cross-tab sync works** - Critical for multi-window workflows
3. **localStorage quota handling** - Must not crash, added after production bug (2025-11-20)
4. **Empty tree renders gracefully** - Must not throw, added after crash bug (2025-10-15)

**Regression History:**
- **2025-11-20:** localStorage quota bug - App crashed when user had 5MB of favorites. Added graceful fallback test.
- **2025-10-15:** Empty tree crash - FileTree threw when tree prop was empty array. Added empty tree test.
- **2025-09-05:** Cross-tab sync race condition - Favorites lost when two tabs updated simultaneously. Added concurrent update test.

---

## Metadata

**Generated by:** Resource Sheet MCP Tool
**Module:** testing (universal)
**Version:** 1.0.0
