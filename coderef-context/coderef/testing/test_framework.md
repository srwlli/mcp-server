# coderef-context Test Framework

**Version:** 1.0.0
**Created:** 2025-12-27
**Purpose:** Comprehensive testing strategy for all 10 coderef-context tools

---

## Overview

This test framework defines:
- Unit test cases for each tool
- Integration test scenarios
- Error handling and edge cases
- Performance/timeout expectations
- Mock CLI behavior

---

## Test Categories

### 1. Unit Tests (Per Tool)
Each tool has isolated tests covering:
- Happy path (valid inputs)
- Edge cases (empty results, timeouts)
- Error handling (missing params, invalid JSON)
- Parameter validation

### 2. Integration Tests
Combinations of tools:
- scan → query (discover elements, then query relationships)
- scan → impact (discover, then analyze change impact)
- query → query (chain dependency queries)

### 3. Async/Subprocess Tests
- Proper async handling (no blocking)
- Timeout enforcement (120s)
- Process cleanup on timeout
- stderr/stdout parsing

### 4. Performance Tests
- Latency expectations (1-5s small projects, longer for large)
- Memory usage (no memory leaks on repeated calls)
- Caching verification (each call is independent, no caching)

---

## CLI Availability Assumption

Tests assume @coderef/core CLI is available at:
```
C:\Users\willh\Desktop\projects\coderef-system\packages\cli\dist\cli.js
```

If CLI unavailable, all tests will fail with "CLI path not found" errors.

---

## Test Execution Strategy

### Phase 1: Tool-by-Tool (Jan 2025)
1. coderef_scan - Code element discovery
2. coderef_query - Relationship queries
3. coderef_impact - Impact analysis
4. coderef_complexity - Complexity metrics
5. coderef_patterns - Pattern discovery
6. coderef_coverage - Test coverage
7. coderef_context - Comprehensive context
8. coderef_validate - Reference validation
9. coderef_drift - Index drift detection
10. coderef_diagram - Diagram generation

### Phase 2: Integration Tests (Late Jan 2025)
- Tool combinations
- Multi-step workflows
- Real feature planning workflows

### Phase 3: Performance & Stress (Feb 2025)
- Large codebase handling
- Repeated query optimization
- Memory/resource usage

---

## Test Project Requirements

Tests need a real TypeScript project to analyze:
- **Current:** Using coderef-context's own source (`C:\Users\willh\.mcp-servers\coderef-context`)
- **Minimal:** At least 2-3 files with functions/classes
- **Ideal:** 50-100 elements for comprehensive testing

---

## Expected Tool Behavior

### coderef_scan
```
Input: project_path, languages, use_ast
Output: JSON with success, elements_found, elements array
Timeout: 120s
Errors: "Scan timeout", JSON parse errors
```

### coderef_query
```
Input: project_path, query_type, target, max_depth
Output: JSON with query_type, target, results array
Timeout: 120s
Errors: "Query timeout", "target parameter is required"
```

### coderef_impact
```
Input: project_path, element, operation, max_depth
Output: JSON with element, operation, impact data
Timeout: 120s
Errors: "element parameter is required", impact analysis errors
```

### (Continue for remaining 7 tools...)

---

## Test Result Format

Each test generates a markdown report:
```markdown
# Test: coderef_scan

**Status:** ✅ PASS | ⚠️ PARTIAL | ❌ FAIL

**Setup:**
- Project: coderef-context source
- Elements discovered: 23
- CLI time: 2.3s

**Test Cases:**
1. Valid scan (AST mode) - ✅ PASS
2. Valid scan (regex mode) - ✅ PASS
3. Empty language list - ⚠️ PARTIAL (returns default langs)
4. Invalid project path - ❌ FAIL (should return error, crashes instead)

**Performance:**
- Avg latency: 2.1s
- Memory: 45MB

**Recommendations:**
- Invalid path handling needs improvement
- Consider caching for repeated queries
```

---

## Success Criteria

- ✅ All 10 tools can execute without crashing
- ✅ JSON output is valid and parseable
- ✅ Timeout enforcement works (kills at 120s)
- ✅ Error handling returns meaningful messages
- ✅ Performance < 5s for small projects
- ✅ No memory leaks on repeated calls

---

## Known Limitations

1. **No Real CLI:** Tests assume @coderef/core CLI is available and working
2. **No Mocking:** Not using mock CLI, tests use real subprocess calls
3. **Project Dependency:** Tests need the coderef-context source itself as test project
4. **No Caching:** Each tool call spawns new subprocess (by design)
5. **No Fallback:** If CLI unavailable, all tests fail

---

## Future Enhancements

- [ ] Mock CLI for deterministic testing
- [ ] Parameterized test runner (run against multiple projects)
- [ ] Performance benchmarking suite
- [ ] Regression test suite (capture baseline behavior)
- [ ] CI/CD integration (automated test runs)
