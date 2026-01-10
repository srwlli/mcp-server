# Performance Module

**Type:** Universal (always included)
**Applies to:** All element types
**Auto-fill:** Complexity metrics, performance profiling data
**Manual:** Performance budgets, bottlenecks, optimization recommendations

---

## Section: Performance Considerations

### Performance Budgets

{{MANUAL: Define performance targets for this element:

**Metrics to Track:**
- Execution time
- Memory usage
- Network requests
- Bundle size
- Time to Interactive (TTI)
- First Contentful Paint (FCP)
- etc.

**Targets:**
- [Metric 1]: < X ms/MB/requests
- [Metric 2]: < Y ms/MB/requests

**Current Performance:**
- [Metric 1]: Z ms/MB/requests (within/outside budget)
- [Metric 2]: W ms/MB/requests (within/outside budget)}}

### Tested Limits

{{AUTO_FILL: element.performance_tests}}

{{MANUAL: Document what performance boundaries have been tested:

**Load Testing:**
- Tested with: [describe dataset size]
- Result: [performance measurement]
- Limit: [maximum before degradation]

**Stress Testing:**
- Tested scenario: [describe stress condition]
- Result: [behavior under stress]
- Breaking point: [when does it fail?]

**Concurrency Testing:**
- Tested scenario: [concurrent operations]
- Result: [performance under concurrency]

**Example:**
- **Tree size:** Tested up to 500 nodes, renders in <100ms
- **localStorage:** Handles 5MB favorites data
- **Memory:** ~2MB per project with favorites
- **Concurrent updates:** Tested 10 simultaneous tab updates, no data loss}}

### Bottlenecks

{{MANUAL: Identify performance bottlenecks:

**Known Bottlenecks:**

1. **[Bottleneck Name]**
   - **Location:** [file:line or function name]
   - **Issue:** [what causes the bottleneck]
   - **Impact:** [how much does it slow things down]
   - **Workaround:** [temporary solution if any]

2. **[Bottleneck Name]**
   ...

**Profiling Evidence:**
- [Include profiling data if available]
- [Chrome DevTools screenshots]
- [Flame graphs]

**Example:**
1. **Recursive FileTreeNode Rendering**
   - **Location:** FileTreeNode.tsx:45
   - **Issue:** No virtualization - renders all 500 nodes on mount
   - **Impact:** 100ms initial render, 2MB DOM memory
   - **Workaround:** None - acceptable for <1000 nodes}}

### Optimization Opportunities

{{MANUAL: Recommend performance improvements:

**Quick Wins (Low Effort, High Impact):**
1. [Optimization 1]
   - **Benefit:** [expected improvement]
   - **Effort:** [time estimate]
   - **Risk:** [low/medium/high]

2. [Optimization 2]
   ...

**Long-Term Optimizations (High Effort, High Impact):**
1. [Optimization 1]
   - **Benefit:** [expected improvement]
   - **Effort:** [time estimate]
   - **Risk:** [low/medium/high]

**Not Worth It (Low Impact or High Risk):**
1. [Optimization 1]
   - **Reason:** [why not worth pursuing]

**Example Quick Win:**
1. **Debounce localStorage writes**
   - **Benefit:** Reduce writes by 90% (batch multiple favorites changes)
   - **Effort:** 30 minutes
   - **Risk:** Low - standard pattern

**Example Long-Term:**
1. **Implement virtual scrolling**
   - **Benefit:** Handle 10,000+ nodes without performance degradation
   - **Effort:** 2-3 days
   - **Risk:** Medium - complex logic, affects all tree interactions}}

### Memory Management

{{MANUAL: Document memory usage patterns:

**Memory Footprint:**
- **Idle:** [memory when doing nothing]
- **Active:** [memory during typical use]
- **Peak:** [maximum memory observed]

**Memory Leaks:**
- [ ] Event listeners cleaned up?
- [ ] Intervals/timeouts cleared?
- [ ] Large objects released?
- [ ] Closures holding references?

**Garbage Collection:**
- How frequently does GC trigger?
- Are there GC pauses noticeable to users?
- Any long-lived objects preventing GC?

**Example:**
- **Idle:** 1MB (tree structure + state)
- **Active:** 2MB (+ favorites data + expanded nodes)
- **Peak:** 5MB (500 nodes + 1000 favorites)
- **Leaks:** ✅ Storage event listener cleaned up on unmount
- **GC:** No noticeable pauses, typical GC every 30 seconds}}

### Caching Strategy

{{MANUAL: Describe what is cached and why:

**What is Cached:**
- [Data/computation 1] - [cache duration/invalidation]
- [Data/computation 2] - [cache duration/invalidation]

**Cache Invalidation:**
- When is cache cleared?
- How is stale data detected?
- What triggers cache refresh?

**Cache Size:**
- How much memory/storage does cache use?
- Are there cache size limits?
- What happens when cache is full?

**Example:**
- **Favorites data:** Cached in localStorage indefinitely (user-controlled deletion)
- **Tree expansion state:** Cached in React state (session-only)
- **File icons:** Memoized with React.useMemo (cache key: file extension)
- **Invalidation:** Favorites cache cleared when user clicks "Clear All"
- **Size:** No cache size limit (relies on browser localStorage quota)}}

### Lazy Loading & Code Splitting

{{MANUAL: Document lazy loading strategy:

**What is Lazy Loaded:**
- [Component/module 1] - [when is it loaded]
- [Component/module 2] - [when is it loaded]

**Bundle Size:**
- **Initial bundle:** [size in KB]
- **Lazy chunks:** [sizes of lazy-loaded chunks]
- **Total:** [total size if all loaded]

**Loading Strategy:**
- Route-based splitting?
- Component-based splitting?
- Dynamic imports?

**Example:**
- **ContextMenu:** Lazy-loaded on first right-click (reduces initial bundle by 15KB)
- **Initial bundle:** 45KB (FileTree + FileTreeNode)
- **Lazy chunks:** 15KB (ContextMenu), 8KB (FavoritesManager)
- **Total:** 68KB if all features used
- **Strategy:** Component-based splitting with React.lazy()}}

---

## Example Output

### Performance Considerations

#### Performance Budgets

**Metrics to Track:**
- Initial render time (tree mount)
- Interaction latency (expand/collapse, select file)
- Memory usage (DOM + React state)
- localStorage write frequency

**Targets:**
- **Initial render:** <100ms for 500 nodes
- **Interaction:** <16ms (60fps) for expand/collapse
- **Memory:** <5MB total (tree + state + favorites)
- **localStorage writes:** <10/minute (debounced)

**Current Performance:**
- **Initial render:** 85ms for 500 nodes ✅ within budget
- **Interaction:** 8ms average for expand/collapse ✅ within budget
- **Memory:** 3.2MB for 500 nodes + 1000 favorites ✅ within budget
- **localStorage writes:** 2-3/minute ✅ within budget (debouncing works)

#### Tested Limits

**Load Testing:**
- **Tested with:** Tree with 500 nodes (nested 5 levels deep)
- **Result:** 85ms initial render, 60fps interactions
- **Limit:** Performance degrades at 1000 nodes (150ms render, occasional frame drops)

**Stress Testing:**
- **Tested scenario:** 100 rapid expand/collapse actions in 10 seconds
- **Result:** No frame drops, smooth 60fps
- **Breaking point:** No breaking point observed - interactions are fast enough

**Memory Testing:**
- **Tested scenario:** 1000 favorites across 10 projects
- **Result:** 4.8MB memory usage, no leaks over 1 hour
- **Breaking point:** localStorage quota (5MB in some browsers) - graceful fallback works

**Concurrency Testing:**
- **Tested scenario:** 10 tabs simultaneously adding favorites
- **Result:** All tabs sync correctly within 100ms
- **Issue:** Occasional race condition if two tabs update same favorite simultaneously (last write wins)

#### Bottlenecks

**Known Bottlenecks:**

1. **Recursive Rendering (No Virtualization)**
   - **Location:** FileTreeNode.tsx:45-80
   - **Issue:** Renders all tree nodes on mount, no virtual scrolling
   - **Impact:** 85ms for 500 nodes, 150ms for 1000 nodes
   - **Workaround:** None - acceptable for <1000 nodes, document as limit

2. **localStorage Synchronous API**
   - **Location:** FileTree.tsx:120
   - **Issue:** localStorage.setItem is blocking (synchronous I/O)
   - **Impact:** <1ms typically, but can cause 16ms jank if browser is busy
   - **Workaround:** Debounced writes (500ms) reduce frequency

**Profiling Evidence:**
- Chrome DevTools Performance panel shows 85ms in "Rendering" phase
- React DevTools Profiler shows FileTreeNode re-renders on every expand/collapse
- Memory snapshot: 3.2MB retained size (expected for dataset)

#### Optimization Opportunities

**Quick Wins (Low Effort, High Impact):**

1. **Memoize FileTreeNode with React.memo**
   - **Benefit:** Reduce re-renders by 80% when parent updates
   - **Effort:** 15 minutes (add React.memo wrapper)
   - **Risk:** Low - standard React optimization

2. **Debounce localStorage writes to 500ms**
   - **Benefit:** ✅ Already implemented - reduced writes by 90%
   - **Status:** COMPLETE

**Long-Term Optimizations (High Effort, High Impact):**

1. **Implement virtual scrolling (react-window)**
   - **Benefit:** Handle 10,000+ nodes with constant performance
   - **Effort:** 2-3 days (complex integration with recursive structure)
   - **Risk:** Medium - affects keyboard navigation, accessibility

2. **Move favorites to IndexedDB**
   - **Benefit:** Async I/O (no jank), larger storage limit (50MB+)
   - **Effort:** 1-2 days (migration + backward compatibility)
   - **Risk:** Low - well-established pattern

**Not Worth It (Low Impact or High Risk):**

1. **Web Worker for tree processing**
   - **Reason:** Overhead of serialization/deserialization outweighs benefit for <1000 nodes
   - **Risk:** High complexity for minimal gain

#### Memory Management

**Memory Footprint:**
- **Idle:** 1.2MB (tree structure + empty favorites)
- **Active:** 3.2MB (500 nodes + 1000 favorites + expanded state)
- **Peak:** 4.8MB (stress test with rapid expand/collapse)

**Memory Leaks:**
- ✅ Storage event listener cleaned up in useEffect cleanup
- ✅ Debounce timeout cleared on unmount
- ✅ No circular references in tree structure
- ✅ ContextMenu refs released when menu closes

**Garbage Collection:**
- **Frequency:** GC runs every 20-30 seconds during active use
- **Pauses:** <5ms GC pauses (not noticeable to users)
- **Long-lived objects:** Tree structure and favorites (intentionally retained)

#### Caching Strategy

**What is Cached:**
- **Favorites data:** localStorage (persists across sessions)
- **Tree expansion state:** React state (session-only, cleared on unmount)
- **File icons:** Memoized based on file extension (React.useMemo)
- **Tree structure:** Passed as prop (not cached internally)

**Cache Invalidation:**
- **Favorites:** Cleared on "Clear All Favorites" button
- **Expansion state:** Reset on project change
- **File icons:** Cache key is extension (never stale)

**Cache Size:**
- **Favorites:** No size limit (up to localStorage quota ~5MB)
- **Expansion state:** Grows with tree size (~1KB per 100 nodes)
- **File icons:** Fixed size (~50 entries for common extensions)
- **Overflow:** localStorage quota exceeded handled gracefully (fallback to session-only)

#### Lazy Loading & Code Splitting

**What is Lazy Loaded:**
- **ContextMenu:** Loaded on first right-click (React.lazy)
- **FavoritesManager:** Loaded when user opens favorites panel

**Bundle Size:**
- **Initial bundle:** 45KB (FileTree + FileTreeNode + useLocalStorage)
- **Lazy chunks:** 15KB (ContextMenu), 8KB (FavoritesManager)
- **Total:** 68KB if all features used

**Loading Strategy:**
- Component-based code splitting with React.lazy()
- ContextMenu loaded on-demand (most users never right-click)
- Suspense boundary shows loading spinner during chunk load (<50ms)

**Loading Performance:**
- **ContextMenu first load:** 35ms (network + parse)
- **Cached load:** <5ms (browser cache)
- **User perception:** Feels instant (below 100ms perception threshold)

---

## Metadata

**Generated by:** Resource Sheet MCP Tool
**Module:** performance (universal)
**Version:** 1.0.0
