# @coderef/core Integration Documentation Index

**Navigation guide for coderef-workflow and @coderef/core integration**

---

## 📚 Documentation Files

### 1. **CODEREF_INTEGRATION_GUIDE.md** ← Start here
**For**: Understanding how coderef-workflow uses @coderef/core
- Architecture overview and data flow
- Integration points explained
- Type mappings and conversions
- Performance characteristics
- Troubleshooting guide
- Future integration opportunities

**Read this if you want to**:
- Understand the big picture
- Add new tools/generators to coderef-workflow
- Debug integration issues
- Plan enhancements

---

### 2. **CODEREF_QUICKREF.md** ← Code examples
**For**: Practical code patterns and recipes
- Quick start examples
- Common operations (filtering, traversal, categorization)
- Working with discovered elements
- Working with dependency graphs
- Pattern detection examples
- Fallback patterns
- Performance tips

**Read this if you want to**:
- Copy-paste working code
- Understand usage patterns
- Solve specific problems
- See real examples

---

### 3. **CODEREF_TYPE_REFERENCE.md** ← Type definitions
**For**: Complete type specifications and data structures
- Core data types (ElementData, DependencyGraph, etc.)
- CLI interface specification
- File format specifications (.coderef/ directory)
- Type conversions and mappings
- Error handling
- Query types (future)

**Read this if you want to**:
- Understand exact data structures
- Implement type-safe code
- Work with CLI output directly
- Debug data format issues

---

## 🎯 Quick Navigation by Task

### "I want to add a new feature to coderef-workflow that uses coderef data"
1. Read: **CODEREF_INTEGRATION_GUIDE.md** → "When Adding New Tools/Generators"
2. Copy: Pattern from **CODEREF_QUICKREF.md** → "Checking if Coderef is Available"
3. Reference: **CODEREF_TYPE_REFERENCE.md** → "Core Data Structures"

### "Coderef scanning is not working - let me debug"
1. Check: **CODEREF_INTEGRATION_GUIDE.md** → "Troubleshooting"
2. Verify: CLI command in **CODEREF_TYPE_REFERENCE.md** → "CLI Interface"
3. Test: Debug steps in **CODEREF_QUICKREF.md** → "Debugging"

### "I need to understand how elements are categorized"
1. Learn: **CODEREF_INTEGRATION_GUIDE.md** → "Element Categorization"
2. Example: **CODEREF_QUICKREF.md** → "Categorizing Elements"
3. Reference: **CODEREF_TYPE_REFERENCE.md** → "Categorical Elements"

### "I want to analyze the dependency graph"
1. Overview: **CODEREF_INTEGRATION_GUIDE.md** → "Data Flow Diagram"
2. Examples: **CODEREF_QUICKREF.md** → "Working with Dependency Graph"
3. Types: **CODEREF_TYPE_REFERENCE.md** → "DependencyGraph"

### "How do I handle when coderef is not available?"
1. Pattern: **CODEREF_INTEGRATION_GUIDE.md** → "Integration Points" → "Persisted Index Loading"
2. Code: **CODEREF_QUICKREF.md** → "Fallback Pattern (When Coderef Unavailable)"
3. Types: **CODEREF_TYPE_REFERENCE.md** → "Error Handling"

---

## 📦 File Organization

```
coderef-workflow/
├── CODEREF_DOCS_INDEX.md           ← You are here
├── CODEREF_INTEGRATION_GUIDE.md    ← Architecture & design
├── CODEREF_QUICKREF.md             ← Code examples & patterns
├── CODEREF_TYPE_REFERENCE.md       ← Type definitions
├── server.py                        ← MCP server entry point
├── tool_handlers.py                 ← Tool implementations
├── generators/
│   ├── coderef_foundation_generator.py  ← Main integration point
│   ├── planning_analyzer.py              ← Planning preparation
│   └── ...
└── coderef/
    ├── working/                    ← Active features
    └── archived/                   ← Completed features
```

---

## 🔗 Key Files Referenced in Docs

### In coderef-workflow:

| File | Purpose | Reference |
|------|---------|-----------|
| `generators/coderef_foundation_generator.py` | Main coderef integration | All guides |
| `generators/planning_analyzer.py` | Project analysis for planning | INTEGRATION_GUIDE |
| `server.py` | MCP tool registration | INTEGRATION_GUIDE → Integration Points |
| `tool_handlers.py` | Tool implementations | INTEGRATION_GUIDE → Integration Points |
| `.coderef/index.json` | Persisted element index | TYPE_REFERENCE, QUICKREF |
| `.coderef/graph.json` | Persisted dependency graph | TYPE_REFERENCE, QUICKREF |

### In @coderef/core:

| File | Purpose | Reference |
|------|---------|-----------|
| `src/analyzer/index.ts` | Analyzer module | INTEGRATION_GUIDE → Module Overview |
| `src/context/context-generator.ts` | Context generation | INTEGRATION_GUIDE → Context Generation |
| `src/query/query-executor.ts` | Query engine | TYPE_REFERENCE → Query Types |
| `types.ts` | Type definitions | TYPE_REFERENCE |

---

## 💡 Common Scenarios

### Scenario 1: Running /coderef-foundation-docs for a project
```
User calls /coderef-foundation-docs
  ↓
coderef-workflow MCP receives request
  ↓
CoderefFoundationGenerator initialized
  ↓
_ensure_coderef_index() checks if .coderef/index.json exists
  ├─ YES → skip scan (fast)
  └─ NO → run: node cli.js scan <project> --analyzer ast --json
  ↓
@coderef/core processes:
  - Scanner discovers code elements (functions, classes, etc.)
  - Analyzer builds dependency graph
  - Returns JSON with elements + graph
  ↓
Save to .coderef/index.json and .coderef/graph.json
  ↓
Load and categorize elements (_categorize_elements)
  ↓
Generate docs:
  - ARCHITECTURE.md (with module diagrams)
  - SCHEMA.md (entities, relationships)
  - COMPONENTS.md (if UI project)
  - project-context.json (for AI agents)
  ↓
Return generated files to user
```

### Scenario 2: Planning a new feature
```
User calls /gather_context → /analyze_project_for_planning
  ↓
PlanningAnalyzer initializes
  ↓
Run analysis methods:
  - scan_foundation_docs() → find existing docs
  - scan_coding_standards() → find BEHAVIOR-STANDARDS.md, etc.
  - detect_technology_stack() → identify frameworks
  - identify_patterns() → find code patterns
  - identify_gaps_and_risks() → risk assessment
  ↓
If coderef data available:
  - Load .coderef/index.json
  - Enhance pattern detection with AST-accurate elements
  ↓
Build PreparationSummaryDict (section 0 of plan)
  ↓
Return context for planning
```

### Scenario 3: Generating AI context for a task
```
Agent needs context for implementation
  ↓
Load project-context.json generated earlier
  ↓
Optionally enrich with:
  - ComplexityScorer (from @coderef/core context module)
  - Impact simulation (what breaks if we change X?)
  - Edge case detection
  ↓
Return agentic context (optimized for LLM)
```

---

## ⚙️ How Integration Works (Simplified)

```
┌─────────────────────────────────────────┐
│  coderef-workflow (Python MCP)          │
│  └─ Orchestration & planning            │
└────────────┬────────────────────────────┘
             │ subprocess call
             ├─→ "node cli.js scan"
             │
┌────────────▼────────────────────────────┐
│  @coderef/core (TypeScript)             │
│  ├─ Scanner (AST-based)      [99% acc]  │
│  ├─ Analyzer (dependency graph)          │
│  ├─ Query Engine                         │
│  └─ Context Generator                    │
└────────────┬────────────────────────────┘
             │ JSON output
             │
┌────────────▼────────────────────────────┐
│  .coderef/ (Persistent Cache)           │
│  ├─ index.json (elements)                │
│  └─ graph.json (relationships)           │
└────────────┬────────────────────────────┘
             │ Load & use
             │
┌────────────▼────────────────────────────┐
│  Generated Outputs                       │
│  ├─ ARCHITECTURE.md                      │
│  ├─ SCHEMA.md                            │
│  ├─ COMPONENTS.md                        │
│  ├─ project-context.json                 │
│  └─ Implementation plans                 │
└─────────────────────────────────────────┘
```

---

## 🚀 Getting Started

### Step 1: Understand the Architecture
- Read: **CODEREF_INTEGRATION_GUIDE.md** (20 min read)
- Skim: Data Flow Diagram section

### Step 2: See Real Code Examples
- Read: **CODEREF_QUICKREF.md** (10 min read)
- Try: Quick Start example
- Copy: Fallback pattern for your code

### Step 3: Know the Data Structures
- Reference: **CODEREF_TYPE_REFERENCE.md** (lookup as needed)
- Understand: ElementData, DependencyGraph
- Check: CLI output format

### Step 4: Implement Something
- Choose a scenario from "Common Scenarios"
- Use patterns from QUICKREF
- Reference types from TYPE_REFERENCE
- Check INTEGRATION_GUIDE for troubleshooting

---

## 📊 Documentation Statistics

| Document | Length | Time to Read | Best For |
|----------|--------|--------------|----------|
| INTEGRATION_GUIDE | 15 KB | 20-30 min | Understanding |
| QUICKREF | 12 KB | 10-15 min | Implementation |
| TYPE_REFERENCE | 18 KB | 15-25 min | Reference |
| DOCS_INDEX | 6 KB | 5 min | Navigation |

**Total**: ~51 KB, ~50-75 minutes to fully understand

---

## ❓ FAQ

### Q: Do I need to install @coderef/core in coderef-workflow?
**A**: No. coderef-workflow calls @coderef/core via subprocess (CLI), not direct import. The core library must be installed separately in the coderef-system/packages/cli.

### Q: What if Node.js is not installed?
**A**: coderef-workflow gracefully falls back to regex-based detection (~85% accuracy instead of 99%).

### Q: Can I use coderef data offline?
**A**: Yes! Once scanned, `.coderef/index.json` is cached. Subsequent runs don't need to re-scan.

### Q: How often should I re-scan?
**A**: Only when code changes significantly. For CI/CD, add a step to delete `.coderef/` to force fresh scans.

### Q: Is the dependency graph always generated?
**A**: The graph is optional. It's larger than the index but provides relationship information. Check if `graph.json` exists.

### Q: How do I contribute enhancements?
**A**: See "Future Integration Opportunities" in INTEGRATION_GUIDE for planned enhancements.

---

## 🔄 Document Update History

| Date | Version | Changes |
|------|---------|---------|
| 2025-12-23 | 1.0 | Initial documentation set created |

---

## 📖 See Also

- [coderef-workflow README.md](./README.md) - MCP server overview
- [@coderef/core guide-to-coderef-core.md](../../packages/core/guide-to-coderef-core.md) - Core library documentation
- [coderef-system overview](../../README.md) - Ecosystem architecture

---

## 💬 Questions or Issues?

When you encounter questions:

1. **First check**: Type or concept from TYPE_REFERENCE
2. **Then check**: Common pattern from QUICKREF
3. **Then check**: Architecture explanation from INTEGRATION_GUIDE
4. **Still stuck?**: See Troubleshooting in INTEGRATION_GUIDE

---

**Last Updated**: 2025-12-23
**Status**: ✅ Complete
**Coverage**: All integration points documented
