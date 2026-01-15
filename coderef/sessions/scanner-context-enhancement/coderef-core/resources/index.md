# coderef-core Agent Resources Index

**Agent:** coderef-core (scanner implementation)
**Phase:** Phase 1 - Scanner Quick Wins
**Workorder:** WO-SCANNER-CONTEXT-ENHANCEMENT-001-CODEREF-CORE

---

## 📚 Source Documents

### Primary Roadmap Document
**Location:** `C:\Users\willh\Desktop\coderef-dashboard\packages\coderef-core\coderef\resources-sheets\Scanner-Effectiveness-Improvements-RESOURCE-SHEET.md`

**What it contains:**
- 15 prioritized scanner improvements (accuracy, performance, coverage)
- Current baseline metrics (85% accuracy, 1185ms for 500 files)
- Quick wins section (lines 1069-1093): Your 4 tasks
- Detailed implementation specs with code examples

**Your focus areas:**
- Lines 1069-1093: Quick Wins (4 improvements, 22 hours total)
- Lines 70-116: P1.1 Hybrid AST (Phase 3 preview)
- Lines 1099-1116: Success Metrics

### Quick Win Specifications

#### Quick Win #1: Pattern Ordering (4 hours)
**Location:** Lines 359-413 in Scanner-Effectiveness-Improvements-RESOURCE-SHEET.md

**What to do:**
- Reorder LANGUAGE_PATTERNS by TYPE_PRIORITY
- Add `exclusive` flag for short-circuit matching
- Target: 15% performance improvement

**Target file:** `packages/coderef-core/src/scanner/scanner.ts:18-44`

#### Quick Win #2: Configuration Presets (6 hours)
**Location:** Lines 812-947 in Scanner-Effectiveness-Improvements-RESOURCE-SHEET.md

**What to do:**
- Define 7 presets (nextjs, react, python, monorepo, go, rust, java)
- Implement auto-detection logic
- Add `preset` parameter to ScanOptions

**Target files:**
- `scanner.ts` (new section for presets)
- `types.ts` (add preset to ScanOptions)

#### Quick Win #3: Structured Error Reporting (8 hours)
**Location:** Lines 660-743 in Scanner-Effectiveness-Improvements-RESOURCE-SHEET.md

**What to do:**
- Create ScanError interface (type, severity, file, line, suggestion)
- Add suggestion database for common errors
- Return errors array alongside elements

**Target files:**
- `types.ts` (new ScanError interface)
- `scanner.ts:552` (error handling)

#### Quick Win #4: Python Pattern Expansion (4 hours)
**Location:** Lines 162-212 in Scanner-Effectiveness-Improvements-RESOURCE-SHEET.md

**What to do:**
- Add 4 Python patterns: decorators, properties, static methods, nested classes
- Target: +30% Python coverage (3 patterns → 7 patterns)

**Target file:** `scanner.ts:18-44` (Python patterns section)

---

## 🎯 Task Specifications

### Session Master Plan
**Location:** `C:\Users\willh\Desktop\assistant\scanner-complete-context.md`

**Your section:** Phase 1: Core Enhancements → coderef-dashboard Tasks
- Lines 139-182: Your 4 quick wins with line numbers
- Lines 183-194: Deliverables and success metrics

### Phase 1 Progress Tracker
**Location:** `C:\Users\willh\.mcp-servers\coderef\sessions\scanner-context-enhancement\phase1-progress.md`

**Current status:**
- Scanner quick wins: ⏳ Not started (0/4 tasks)
- Overall Phase 1: 1/11 tasks (9%)

### Session Instructions
**Location:** `C:\Users\willh\.mcp-servers\coderef\sessions\scanner-context-enhancement\instructions.json`

**Your section:** `agent_instructions.phase_1_agents.coderef-dashboard`
- Lines 111-133: Your detailed task list
- Target files with specific line numbers
- Output format requirements
- Success criteria

---

## 🗂️ Your Codebase

### Main Implementation Files
**Location:** `C:\Users\willh\Desktop\coderef-dashboard\packages\coderef-core\`

**Key files for your tasks:**
- `src/scanner/scanner.ts:18-44` - LANGUAGE_PATTERNS (Quick Win #1, #4)
- `src/scanner/scanner.ts:552` - Error handling (Quick Win #3)
- `src/scanner/types.ts` - ElementData, ScanOptions, ScanError interfaces (Quick Win #2, #3)
- `src/fileGeneration/detectPatterns.ts` - Pattern detection logic

**Current scanner characteristics:**
- Engine: Regex-based pattern matching (no AST for most languages yet)
- Processing: Sequential single-threaded (parallel coming in Phase 3)
- Caching: Mtime-based global Map (LRU coming in Phase 3)
- Languages: 10 languages (TypeScript, JavaScript, Python, Go, Rust, Java, C++, C)

---

## 📊 Success Metrics

### Performance Target
**Baseline:** 1185ms for 500 files
**Target after Quick Win #1:** ~1000ms (15% improvement)
**Final Phase 3 target:** 300-400ms (3-5x faster)

### Accuracy Target
**Baseline:** 85% for TypeScript/JavaScript
**Current Python:** 3 patterns
**Target after Quick Win #4:** 7 patterns (+30% Python coverage)
**Final Phase 3 target:** 95% accuracy

### User Experience Target
**Configuration time baseline:** 15-30 minutes (manual glob patterns)
**Target after Quick Win #2:** 30 seconds (presets + auto-detect)

**Error resolution time baseline:** 20 minutes
**Target after Quick Win #3:** 5-7 minutes (structured errors + suggestions)

---

## 🔗 Integration Points

### Phase 2 Dependencies
**Location:** `C:\Users\willh\.mcp-servers\coderef\sessions\scanner-context-enhancement\phase2-integration-targets.md`

**Why you need to know:**
- Lines 116-156: How coderef-docs will use your enhanced scanner
- Your accuracy improvements enable better ARCHITECTURE.md generation
- Your Python patterns enable better API.md generation

**Key insight:**
Your quick wins provide immediate value, while Phase 3 improvements (AST, parallel) come later

---

## 📝 Output Requirements

### What to Create
**Location:** `../outputs/coderef-dashboard-phase1-output.md`

**Format (Markdown):**
```markdown
# coderef-core Phase 1 Output - Scanner Quick Wins

## Implementation Summary

**Agent:** coderef-core
**Phase:** Phase 1
**Tasks Completed:** 4/4

---

## Quick Win #1: Pattern Ordering

**Status:** ✅ Complete
**Commit:** abc123
**Files Modified:**
- src/scanner/scanner.ts:18-44 (LANGUAGE_PATTERNS reordered)

**Implementation:**
- Reordered patterns by TYPE_PRIORITY: constant → component → hook → class → method → function
- Added exclusive flag to 3 patterns (constant, component, hook)

**Testing:**
- Benchmark: 1185ms → 1005ms (15.2% improvement)
- Verified no elements missed (deduplication still works)

---

## Quick Win #2: Configuration Presets

**Status:** ✅ Complete
**Commit:** def456
**Files Modified:**
- src/scanner/scanner.ts (added ScanPresets object)
- src/scanner/types.ts (added preset to ScanOptions)

**Implementation:**
- 7 presets defined: nextjs, react, python, monorepo, go, rust, java
- Auto-detection logic: detects package.json, pyproject.toml, Cargo.toml, go.mod, etc.

**Testing:**
- Configuration time: 15-30 min → 30 sec
- Auto-detection accuracy: 95%

---

## Quick Win #3: Structured Error Reporting
[... similar format ...]

## Quick Win #4: Python Pattern Expansion
[... similar format ...]

---

## Success Metrics Summary

| Metric | Baseline | Achieved | Target | Status |
|--------|----------|----------|--------|--------|
| Scan speed (500 files) | 1185ms | 1005ms | ~1000ms | ✅ |
| Configuration time | 15-30 min | 30 sec | 30 sec | ✅ |
| Error resolution | 20 min | 5-7 min | 5-7 min | ✅ |
| Python patterns | 3 | 7 | 7 | ✅ |

---

## Test Results

**Performance Benchmark:**
- 500 files: 1185ms → 1005ms (15% improvement)
- 1000 files: [results]
- 5000 files: [results]

**Accuracy Tests:**
- Python decorator detection: 100% (20/20 test cases)
- Python property detection: 100% (15/15 test cases)
- Python static method detection: 100% (10/10 test cases)
- Python nested class detection: 95% (19/20 test cases)

**Preset Tests:**
- Auto-detection: 95% accuracy (19/20 projects)
- Preset exclusions: 100% (all expected files excluded)

**Error Reporting Tests:**
- Suggestion database: 100% coverage (all common errors have suggestions)
- Non-throwing errors: 100% (partial results returned on error)

---

## Next Steps

**Phase 2 Integration:**
- coderef-docs will use enhanced scanner for foundation docs
- 95% accuracy for element detection in ARCHITECTURE.md
- +30% Python coverage in API.md

**Phase 3 Enhancements:**
- Hybrid AST + Regex (85% → 95% accuracy)
- Parallel processing (3-5x faster)
- LRU caching (50MB memory cap)
```

---

## 🚀 Execution Steps

1. **READ** this index to understand all resources
2. **READ** Scanner-Effectiveness-Improvements-RESOURCE-SHEET.md (your primary spec)
3. **READ** scanner-complete-context.md (session master plan)
4. **RUN** `/create-workorder` using `../context.json`
5. **EXECUTE** 4 quick wins following generated plan.json
6. **TEST** each quick win (performance, accuracy, UX)
7. **CREATE** output markdown in `../outputs/`
8. **UPDATE** `../communication.json` status

---

## 🧪 Testing Requirements

### Quick Win #1: Pattern Ordering
- [ ] Benchmark: 500, 1000, 5000 files (verify 15% improvement)
- [ ] Verify no elements missed (compare before/after element counts)
- [ ] Test deduplication still works (no duplicate elements)

### Quick Win #2: Configuration Presets
- [ ] Test all 7 presets with real projects
- [ ] Test auto-detection on 10+ diverse projects
- [ ] Verify exclusion patterns work correctly
- [ ] Measure configuration time (should be ~30 seconds)

### Quick Win #3: Structured Error Reporting
- [ ] Test all error types (read, parse, permission, encoding)
- [ ] Verify suggestions are accurate and helpful
- [ ] Ensure partial results returned on error
- [ ] Measure error resolution time improvement

### Quick Win #4: Python Pattern Expansion
- [ ] Test with 10+ Python fixtures (decorators, properties, static methods, nested classes)
- [ ] Compare element counts before/after (should be +30%)
- [ ] Verify no false positives
- [ ] Integration test with mixed TS/Python projects

---

## 🆘 Questions or Issues?

**Session orchestrator:** Assistant agent at `C:\Users\willh\Desktop\assistant`
**Session directory:** `C:\Users\willh\.mcp-servers\coderef\sessions\scanner-context-enhancement\`
**Your directory:** `C:\Users\willh\.mcp-servers\coderef\sessions\scanner-context-enhancement\coderef-core\`

---

**Last Updated:** 2026-01-14
**Status:** Resources indexed, ready for agent execution
