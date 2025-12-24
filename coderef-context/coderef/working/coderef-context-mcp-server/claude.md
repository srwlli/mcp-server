# Agent Handoff Context - CodeRef Context MCP Server

**Workorder ID:** WO-CODEREF-CONTEXT-MCP-SERVER-001
**Feature:** coderef-context-mcp-server
**Generated:** 2025-12-23
**Technology:** TypeScript (not Python)

---

## Quick Overview

You are building a **new TypeScript MCP server** called `coderef-context` that directly uses the entire `@coderef/core` system (all 10 modules) and exposes them as MCP tools.

**What this means:**
- **Old approach:** coderef-mcp had its own Python code duplicating analysis logic
- **New approach:** coderef-context is a TypeScript MCP server that directly imports and uses @coderef/core modules
- **Result:** Single source of truth, maximum performance, native type safety

---

## Key Files to Read First

1. **Context & Requirements:**
   - `context.json` - Feature description, requirements, constraints, decisions
   - `analysis.json` - Project structure analysis (mostly empty since this is new)

2. **Implementation Plan:**
   - `plan.json` - Complete 10-section implementation plan with 4 phases, 18 tasks
   - `DELIVERABLES.md` - Task checklist and success metrics

3. **Reference Documentation:**
   - `C:\Users\willh\Desktop\projects\coderef-system\CLAUDE.md` - Complete CodeRef system documentation
   - `C:\Users\willh\Desktop\projects\coderef-system\packages\core\demo-all-modules.ts` - Shows all 10 modules working

---

## The 10 Modules You're Exposing

| Module | Purpose | MCP Tool Name |
|--------|---------|---------------|
| 1. Scanner | Discover code elements (functions, classes, etc) | `scan_elements` |
| 2. Analyzer | Build dependency graph with nodes/edges | `analyze_codebase` |
| 3. Query Engine | Traverse graph for relationships | `query_graph` |
| 4. Parser | Parse CodeRef tag format (@Fn/path#element:line) | `parse_tag` |
| 5. Validator | Check references against codebase | `validate_reference` |
| 6. Exporter | Serialize graphs to JSON/other formats | `export_graph` |
| 7. Context (6-phase) | Generate agentic context with confidence | `generate_context` |
| 8. Integration/RAG | Semantic search and Q&A over codebase | `rag_ask_question` |
| 9. Error Handling | Graceful error handling (internal) | N/A |
| 10. Types & Utilities | Type system and helpers (internal) | N/A |

---

## Architecture Overview

```
User Question via Claude
        ↓
MCP Protocol Handler (server.ts)
        ↓
Tool Handler (tools/*.ts)
        ↓
Direct Import: @coderef/core Modules
        ↓
Scanner, Analyzer, Query, Parser, Validator, Exporter
Context Generator (6-phase), RAG, Error Handler, Types
        ↓
Returns Native TypeScript Objects
        ↓
CacheManager (cache-manager.ts) ← Store & Retrieve
        ↓
Format as MCP Response
        ↓
Return to Claude
```

**Key points:**
- All communication with @coderef/core is direct TypeScript imports (zero subprocess overhead)
- Responses cached in-memory (5-minute TTL, LRU eviction with max 100 entries)
- TypeScript provides native type safety (no JSON parsing needed)
- Runs in same Node.js process as @coderef/core for maximum performance
- Each tool is idempotent and can be called repeatedly

---

## Implementation Phases

### Phase 1: Setup & Infrastructure (2 weeks)
**Status:** Not started
**Tasks:** SETUP-001, SETUP-002, BRIDGE-001, BRIDGE-002
**Goal:** Get foundation working (server startup, bridge communication, caching)

Start here. You need:
- Project structure (directories, files, dependencies)
- MCP server that listens and handles protocol
- CodeRefCoreBridge that executes `pnpm start` commands
- CacheManager with TTL/LRU

### Phase 2: Core Analysis Tools (2.5 weeks)
**Status:** Not started (depends on Phase 1)
**Tasks:** SCANNER-001, ANALYZER-001, QUERY-001, PARSER-001
**Goal:** Implement 4 main analysis tools

### Phase 3: Validation & Export (1.5 weeks)
**Status:** Not started (depends on Phase 2)
**Tasks:** VALIDATOR-001, EXPORTER-001
**Goal:** Add validation and export capabilities

### Phase 4: Advanced Features & Polish (2.5 weeks)
**Status:** Not started (depends on Phase 3)
**Tasks:** CONTEXT-001, RAG-001, TYPES-001, ERROR-001, TEST-001, PERF-001, DOCS-001
**Goal:** Complete system with context generation, RAG, full testing, documentation

---

## Success Criteria

### Must Have (Blocking)
- [ ] All 10 @coderef/core modules working via MPC tools
- [ ] <5 second response time for most queries (cached)
- [ ] 90%+ test coverage
- [ ] Zero crashes or unhandled errors
- [ ] Windows & Unix path handling working

### Should Have (Important)
- [ ] Performance: <1s for cached queries
- [ ] Caching: >70% hit rate
- [ ] Full documentation
- [ ] Integration with real projects

### Nice to Have (Polish)
- [ ] Advanced performance optimizations
- [ ] Detailed troubleshooting guide
- [ ] Example scripts for each tool

---

## Critical Implementation Details

### Direct Module Import Pattern

```typescript
// Direct imports from @coderef/core (same workspace)
import {
  scanCurrentElements,
  AnalyzerService,
  QueryExecutor,
  CodeRefParser,
  CodeRefValidator,
  GraphExporter,
  ComplexityScorer,
  TaskContextGenerator,
  EdgeCaseDetector,
  TestPatternAnalyzer,
  ExampleExtractor,
  AgenticFormatter,
  type ElementData,
  type DependencyGraph,
  type AnalysisResult,
} from '@coderef/core';

// Usage - direct function calls, no subprocess overhead
const elements = await scanCurrentElements('./src', ['ts', 'tsx']);
const analyzer = new AnalyzerService('./src');
const analysis = await analyzer.analyzeCodebase('./src', ['ts', 'tsx']);

// Full type safety - TypeScript compiler catches errors
```

**Critical points:**
- All imports are direct (no subprocess calls needed)
- Full TypeScript type safety (no runtime type checking needed)
- Same workspace monorepo means they evolve together
- Zero serialization overhead - native objects passed between modules
- Errors are typed and caught at compile time

### Caching Strategy

```typescript
import LRU from 'lru-cache';

// Create typed cache with TTL
const cache = new LRU<string, any>({
  max: 100,              // Max 100 entries
  ttl: 1000 * 60 * 5,   // 5 minutes TTL
});

// Cache key from inputs
const cacheKey = `${toolName}:${JSON.stringify(inputs)}:${sourceDir}`;

// Check cache before expensive operations
const cached = cache.get(cacheKey);
if (cached) {
  return cached;  // Hit - fast path
}

// Cache miss - run operation
const result = await expensiveOperation();
cache.set(cacheKey, result);
return result;
```

### Type Safety with Zod Validation

```typescript
import { z } from 'zod';

// Runtime validation schema (matches @coderef/core types)
const ElementDataSchema = z.object({
  type: z.enum(['function', 'class', 'method', 'interface', 'type', 'hook']),
  name: z.string(),
  file: z.string(),
  line: z.number().positive(),
  exported: z.boolean().optional(),
});

const ScanResponseSchema = z.object({
  elements: z.array(ElementDataSchema),
  statistics: z.object({}).passthrough(),
  execution_time: z.number(),
});

// Use for runtime validation
const result = ScanResponseSchema.parse(data);
```

---

## Common Pitfalls to Avoid

1. **Circular Dependencies**
   - ❌ Don't: Import from MCP SDK in type definitions
   - ✅ Do: Use type-only imports when needed

2. **Async/Await**
   - ❌ Don't: Forget `await` on async @coderef/core functions
   - ✅ Do: Always await, handle Promise rejections

3. **Type Safety**
   - ❌ Don't: Use `any` type without good reason
   - ✅ Do: Leverage TypeScript compiler, use proper types

4. **Cache Keys**
   - ❌ Don't: Include mutable objects in cache keys
   - ✅ Do: Use stable JSON strings with sorted keys

5. **Error Handling**
   - ❌ Don't: Let TypeScript errors crash the server
   - ✅ Do: Catch errors, validate inputs, return MCP error responses

6. **Memory Management**
   - ❌ Don't: Cache huge graphs indefinitely
   - ✅ Do: Use LRU eviction, set TTL, monitor memory usage

7. **Testing**
   - ❌ Don't: Test against non-existent directories
   - ✅ Do: Use coderef-system itself as test subject (1000+ elements)

---

## Development Workflow

### 1. Start with Phase 1 Boilerplate
```bash
cd C:\Users\willh\Desktop\projects\coderef-system

# Add new @coderef-context package to monorepo
mkdir packages/context
cd packages/context

# Create TypeScript project structure
mkdir -p src/{tools,cache,types,error,__tests__}

# Install dependencies (done at monorepo level)
pnpm install
pnpm add -D vitest @vitest/ui

# Start server (will fail until tools ready, that's OK)
pnpm dev
```

### 2. Set Up Direct Imports
- Import and test all 10 @coderef/core modules
- Verify type definitions work
- Test basic Scanner/Analyzer calls
- Validate error types

### 3. Test with Real Codebase
Use this for testing:
```
C:\Users\willh\Desktop\projects\coderef-system\src
```

This has:
- 1,000+ TypeScript elements
- Real dependency graph
- Multiple file types (ts, tsx)
- Good test subject for all tools

### 4. Add Tests First
Write tests before implementation (TDD approach):
```typescript
// src/__tests__/tools.test.ts
import { describe, it, expect } from 'vitest';
import { scanCurrentElements } from '@coderef/core';

describe('Scanner Tool', () => {
  it('should return array of elements', async () => {
    const elements = await scanCurrentElements('./src', ['ts']);
    expect(Array.isArray(elements)).toBe(true);
    expect(elements.length).toBeGreaterThan(0);
    expect(elements[0]).toHaveProperty('type');
    expect(elements[0]).toHaveProperty('name');
  });
});
```

### 5. Performance Tuning
Once functional, optimize:
- Profile with vitest
- Ensure cache hit rate >70%
- Verify all response times <2s (direct imports are fast!)

---

## Key Environment Variables

```
# Cache TTL (milliseconds)
CODEREF_CACHE_TTL=300000  # 5 minutes

# Max cache entries (LRU eviction)
CODEREF_CACHE_MAX_ENTRIES=100

# Debug mode
CODEREF_DEBUG=false

# MCP Server port (if running standalone)
MCP_SERVER_PORT=5000

# Log level
LOG_LEVEL=info  # debug|info|warn|error
```

**Note:** No need for CODEREF_CLI_PATH since we're using direct imports in the same monorepo!

---

## Questions to Answer During Implementation

1. **Async/Await:** How will you handle async operations in MCP tools?
   → Use async tool handlers. MCP SDK supports async/await natively.

2. **Cache Invalidation:** When should cache be cleared?
   → TTL-based only (5 minutes). No explicit invalidation needed.

3. **Monorepo Integration:** How will you ensure @coderef/core is available?
   → TypeScript workspace dependencies. Add to package.json: `"@coderef/core": "workspace:*"`

4. **Error Types:** How should you handle @coderef/core errors?
   → Import error types from @coderef/core. Wrap in MCP-compatible error responses.

5. **Type Validation:** How strict should Zod validation be?
   → Strict. Validate all MCP tool inputs. Use strict mode for schemas. Fail fast on schema mismatch.

6. **Resource Management:** How to prevent memory leaks with caching?
   → LRU eviction handles it. Monitor memory with Node.js profiling tools. Test with large codebases.

---

## Next Steps

1. **Read the full plan.json** - Understand all 18 tasks
2. **Set up Python project** - Create structure, install deps
3. **Start Phase 1** - Implement SETUP-001 and SETUP-002
4. **Build bridge** - Implement BRIDGE-001 and BRIDGE-002
5. **Write tests** - Test each component as you go
6. **Implement Phase 2** - Scanner, Analyzer, Query, Parser tools
7. **Continue Phases 3-4** - Validator, Exporter, Context, RAG

---

## Resources

**Documentation:**
- `plan.json` - Full implementation plan
- `context.json` - Requirements and constraints
- `DELIVERABLES.md` - Task checklist

**Reference Code:**
- `C:\Users\willh\.mcp-servers\coderef-mcp\server.py` - Current MCP implementation
- `C:\Users\willh\.mcp-servers\coderef-mcp\tool_handlers.py` - Current tool handlers
- `C:\Users\willh\Desktop\projects\coderef-system\packages\core\demo-all-modules.ts` - All 10 modules demo

**TypeScript API Reference:**
- Export list: `C:\Users\willh\Desktop\projects\coderef-system\packages\core\src\index.ts`
- All module types: `C:\Users\willh\Desktop\projects\coderef-system\packages\core\src\types\types.ts`
- CLI docs: `C:\Users\willh\Desktop\projects\coderef-system\CLAUDE.md`

---

## Questions? Issues?

Update this document as you discover:
- [ ] New design decisions
- [ ] Architectural changes
- [ ] Performance findings
- [ ] Testing strategies
- [ ] Integration patterns

**Current Status:** 🚧 Ready for Phase 1 implementation

**Agent Assignment:** Awaiting assignment
**Start Date:** TBD
**Estimated Completion:** 8-10 weeks from start
