# CodeRef MCP + Context System Integration Analysis

**Date:** December 23, 2025
**Status:** Analysis & Planning
**Objective:** Integrate the 6-phase agentic context generation system with the existing coderef-mcp server

---

## Executive Summary

We have two complementary systems:

1. **@coderef/core** (TypeScript SDK)
   - Scanner: Discovers code elements
   - Analyzer: Builds dependency graphs
   - Context Generation: 6-phase enhancement (Complexity, Task, EdgeCases, Tests, Examples, Agentic)
   - Query Engine, Validator, Exporter

2. **coderef-mcp** (Python MCP Server)
   - Query tool: Search code elements
   - Analyze tool: Impact analysis
   - Validate tool: Reference validation
   - Batch tools, Resources, Prompts

**Gap:** The MCP server doesn't leverage the 6-phase context generation system. Agents can query elements but don't get rich agentic context.

**Solution:** Wire @coderef/core's context system into coderef-mcp as new tools and resources.

---

## Current Architecture

### @coderef/core (TypeScript)

**Location:** `/coderef-system/packages/core/`

**10 Modules:**
```
Module 1: Scanner               (scanCurrentElements)
Module 2: Analyzer              (AnalyzerService + AST analysis)
Module 3: Query Engine          (QueryExecutor)
Module 4: Parser                (CodeRefParser)
Module 5: Validator             (CodeRefValidator)
Module 6: Exporter              (GraphExporter)
Module 7: 6-Phase Context       ← THIS IS THE NEW SYSTEM
  └─ Phase 1: ComplexityScorer
  └─ Phase 2: TaskContextGenerator
  └─ Phase 3: EdgeCaseDetector
  └─ Phase 4: TestPatternAnalyzer
  └─ Phase 5: ExampleExtractor
  └─ Phase 6: AgenticFormatter
Module 8: Integration/RAG
Module 9: Error Handling
Module 10: Types & Utilities
```

**Test Coverage:** demo-all-modules.ts verified all 10 modules working together
- Scans 1,021 elements
- Builds 675-node dependency graph
- Generates agentic-context.json (8.1 KB)
- 6-phase context with confidence scoring

**Key Exports:** All available via `@coderef/core` SDK
```typescript
export {
  ComplexityScorer,
  TaskContextGenerator,
  EdgeCaseDetector,
  TestPatternAnalyzer,
  ExampleExtractor,
  AgenticFormatter,
  // Plus all other 10 modules
} from '@coderef/core';
```

---

### coderef-mcp (Python)

**Location:** `/c/Users/willh/.mcp-servers/coderef-mcp/`

**Architecture:**
```
Server (server.py)
  ├─ 8 MCP Tools
  │  ├─ mcp__coderef__query
  │  ├─ mcp__coderef__analyze
  │  ├─ mcp__coderef__validate
  │  ├─ mcp__coderef__batch_validate
  │  ├─ mcp__coderef__generate_docs
  │  ├─ mcp__coderef__audit
  │  ├─ mcp__coderef__nl_query
  │  └─ mcp__coderef__scan_realtime
  │
  ├─ 4 MCP Resources
  │  ├─ coderef://graph/current
  │  ├─ coderef://stats/summary
  │  ├─ coderef://index/elements
  │  └─ coderef://coverage/test
  │
  └─ Tool Handlers (tool_handlers.py)
     ├─ QueryExecutor
     ├─ DeepAnalysisEngine
     ├─ ReferenceValidator
     └─ BatchValidationProcessor
```

**Current Capabilities:**
- Query code elements by reference
- Analyze impact (what calls/depends on)
- Validate reference format
- Batch validation with parallel processing
- Real-time scanning via CLI integration
- NL query interface (93.3% accuracy)

**Current Data Flow:**
```
User Query
  ↓
MCP Tool Handler
  ↓
Python Generator (QueryExecutor, AnalysisEngine)
  ↓
Results (JSON)
```

---

## Integration Gaps & Analysis

### Gap 1: No Context Generation

**Current State:**
- MCP tools return raw query results
- No complexity metrics in results
- No risk assessment
- No edge case detection
- No confidence scoring

**Needed:**
- 6-phase context generation during analysis
- Confidence metrics in all responses
- Edge case warnings
- Task-specific filtering and prioritization

**Impact:** Agents get raw data but not actionable context

---

### Gap 2: No Python ↔ TypeScript Bridge

**Current State:**
- coderef-mcp is standalone Python service
- Can't call @coderef/core modules
- Duplicate implementation of analysis logic

**Needed:**
- Inter-process communication (IPC)
- Spawn child process for TypeScript analysis
- Call @coderef/core from Python
- Share results between systems

**Options:**
1. **Shell execution** - Simplest (pnpm start [command])
2. **HTTP server** - More robust (run @coderef/core as HTTP API)
3. **Direct Node.js binding** - Python node-ffi bindings

---

### Gap 3: Index/Cache Mismatch

**Current State:**
- coderef-mcp maintains its own index
- @coderef/core maintains separate analysis cache
- Could be out of sync

**Needed:**
- Unified index format
- Single source of truth
- Cache invalidation strategy

---

### Gap 4: No Agentic Context Output Format

**Current State:**
- Query results are element-focused
- No AgenticContext structure (workorderId, confidence, metadata)
- Missing 6-phase breakdown

**Needed:**
- Return AgenticContext JSON from tools
- Include 6-phase data in analysis results
- Standardized agentic output format

---

## Proposed Integration Architecture

### High-Level Design

```
┌──────────────────────────────────────────────────────────┐
│              MCP Client (Claude, Agents)                 │
└────────────────────┬─────────────────────────────────────┘
                     │ MCP Protocol
┌────────────────────▼─────────────────────────────────────┐
│         coderef-mcp Server (Python)                      │
├──────────────────────────────────────────────────────────┤
│  Tool Handlers                                           │
│  ├─ query_with_context         ← NEW                    │
│  ├─ analyze_with_context       ← ENHANCED              │
│  ├─ generate_agentic_context   ← NEW                   │
│  ├─ validate_references        ← EXISTING              │
│  └─ [existing tools...]                                 │
├──────────────────────────────────────────────────────────┤
│  Context Bridge Layer            ← NEW                  │
│  ├─ TypeScript Executor Process                         │
│  ├─ CLI Integration (@coderef/core)                    │
│  └─ Result Aggregation                                 │
├──────────────────────────────────────────────────────────┤
│  Unified Index & Cache                                  │
│  ├─ Persisted Analysis Data                             │
│  ├─ Metadata Store                                      │
│  └─ Agentic Context Store                              │
└──────────────┬───────────────────────────────────────────┘
               │ Subprocess IPC
┌──────────────▼───────────────────────────────────────────┐
│  @coderef/core SDK (TypeScript/Node.js)                 │
├──────────────────────────────────────────────────────────┤
│  1. Scanner        - Code element discovery             │
│  2. Analyzer       - Dependency graph                   │
│  3. Query Engine   - Element relationships              │
│  4. Parser         - CodeRef tag parsing                │
│  5. Validator      - Reference validation               │
│  6. Exporter       - Graph serialization                │
│  7. 6-Phase Context ← PRIMARY INTEGRATION POINT        │
│     ├─ Complexity Scorer                               │
│     ├─ Task Context Generator                          │
│     ├─ Edge Case Detector                              │
│     ├─ Test Pattern Analyzer                           │
│     ├─ Example Extractor                               │
│     └─ Agentic Formatter                               │
│  8. Integration/RAG                                     │
│  9. Error Handling                                      │
│  10. Types & Utilities                                 │
└──────────────────────────────────────────────────────────┘
```

### New MCP Tools

#### Tool 1: `mcp__coderef__generate_agentic_context` (NEW)

**Purpose:** Generate complete 6-phase context for agents

**Input:**
```json
{
  "workorder_id": "WO-AUTH-REFACTOR-001",
  "task_description": "Refactor authentication module",
  "source_dir": "./src",
  "languages": ["ts", "tsx"],
  "filter_criteria": {
    "keywords": ["auth", "login", "token"],
    "max_complexity": 8
  }
}
```

**Process:**
1. Call @coderef/core scanner → Find 1000+ elements
2. Call @coderef/core analyzer → Build graph
3. Call ComplexityScorer → Phase 1 metrics
4. Call TaskContextGenerator → Phase 2 filtering
5. Call EdgeCaseDetector → Phase 3 risks
6. Call TestPatternAnalyzer → Phase 4 coverage
7. Call ExampleExtractor → Phase 5 patterns
8. Call AgenticFormatter → Phase 6 output
9. Return complete AgenticContext JSON

**Output:**
```json
{
  "status": "success",
  "workorder_id": "WO-AUTH-REFACTOR-001",
  "task_description": "Refactor authentication module",
  "complexity": {
    "functionsByComplexity": [...],
    "stats": { "min": 1, "max": 8, "avg": 4.2, "median": 4 }
  },
  "context": {
    "functionsToModify": 10,
    "impactedFunctions": 5,
    "riskLevel": "medium"
  },
  "edgeCases": {
    "criticalIssues": 2,
    "highSeverityIssues": 3,
    "allIssues": [...]
  },
  "testing": {
    "coveragePercentage": 87.5,
    "recommendedPatterns": [...],
    "testFiles": 12
  },
  "examples": {
    "patternExamples": [...],
    "antiPatternsToAvoid": [...]
  },
  "metadata": {
    "confidence": {
      "extractionQuality": 0.95,
      "patternConsistency": 0.82,
      "dataCompleteness": 0.88,
      "overall": 0.88,
      "level": "high"
    },
    "processingStats": {
      "elementsAnalyzed": 1021,
      "edgeCasesDetected": 5,
      "patternsFound": 12,
      "processingTimeMs": 2341
    }
  }
}
```

---

#### Tool 2: `mcp__coderef__query_with_context` (ENHANCED)

**Enhancement:** Add context-aware filtering and ranking

**Input:**
```json
{
  "query": "@Fn/auth/*#*",
  "filter": {
    "min_complexity": 5,
    "max_complexity": 10,
    "status": "active"
  },
  "rank_by": "complexity",  // or "risk", "coverage", "usage"
  "include_context": true   // NEW: Include complexity/risk data
}
```

**Output includes:**
```json
{
  "elements": [
    {
      "reference": "@Fn/auth/login#authenticate:24",
      "complexity": {
        "score": 7.2,
        "riskLevel": "high",
        "metrics": {
          "lines": 45,
          "branches": 8,
          "nesting": 3
        }
      },
      "impact": {
        "dependents": 12,
        "dependencies": 5,
        "transitiveImpact": 34
      },
      "edgeCases": [
        {"type": "race_condition", "severity": "high", "description": "..."}
      ],
      "testCoverage": 0.92,
      "confidence": 0.88
    }
  ]
}
```

---

#### Tool 3: `mcp__coderef__analyze_with_context` (ENHANCED)

**Enhancement:** Include 6-phase data in impact analysis

**Output includes:**
```json
{
  "analysis_type": "impact",
  "reference": "@Fn/auth/login#authenticate:24",
  "affectedElements": [...],
  "contextData": {
    "complexity": { "score": 7.2, "riskLevel": "high" },
    "edgeCases": 3,
    "testCoverage": 0.92,
    "confidence": 0.88
  }
}
```

---

### New MCP Resources

#### Resource 1: `coderef://context/agentic` (NEW)

**Purpose:** Access cached agentic context without regenerating

**Content:**
```json
{
  "workorders": [
    {
      "workorder_id": "WO-AUTH-001",
      "context": { /* full AgenticContext */ },
      "generated_at": "2025-12-23T12:00:00Z",
      "cached": true,
      "ttl_seconds": 3600
    }
  ]
}
```

---

#### Resource 2: `coderef://stats/context` (NEW)

**Purpose:** Summary of context generation statistics

**Content:**
```json
{
  "contexts_generated": 5,
  "total_elements_analyzed": 5105,
  "avg_complexity": 4.2,
  "avg_confidence": 0.82,
  "common_edge_cases": ["race_condition", "null_pointer", "state_mutation"],
  "last_update": "2025-12-23T12:00:00Z"
}
```

---

## Implementation Strategy

### Phase 1: Bridge Layer (1-2 weeks)

**Goal:** Create inter-process bridge between Python and TypeScript

**Components:**
1. **ContextBridge.py** - Manages subprocess execution
   ```python
   class ContextBridge:
     async def generate_agentic_context(self, params):
       # 1. Build @coderef/core CLI command
       # 2. Execute as subprocess
       # 3. Parse JSON output
       # 4. Return Python objects
   ```

2. **CLI Integration** - Use existing @coderef/core CLI
   ```bash
   pnpm start rag-context-generation \
     --source-dir ./src \
     --task "Refactor auth module" \
     --output json
   ```

3. **Result Parser** - Convert CLI JSON to AgenticContext
   ```python
   async def parse_context_output(json_str):
     # Convert JSON string to Python dict
     # Validate against schema
     # Return AgenticContext model instance
   ```

**Deliverables:**
- [ ] ContextBridge.py module (150 lines)
- [ ] CLI command implementation in @coderef/core
- [ ] Error handling and retry logic
- [ ] Result caching (5-minute TTL)

---

### Phase 2: New MCP Tools (2-3 weeks)

**Goal:** Implement 3 new MCP tools + handlers

**Components:**
1. **generate_agentic_context handler** (250 lines)
   - Calls ContextBridge
   - Returns AgenticContext JSON
   - Handles errors gracefully

2. **query_with_context handler** (200 lines)
   - Enhanced query with context filtering
   - Adds complexity metrics to results
   - Supports rank_by parameter

3. **analyze_with_context handler** (150 lines)
   - Wraps existing analysis
   - Adds 6-phase context data
   - Includes confidence metrics

**Deliverables:**
- [ ] Update server.py with 3 new tool schemas
- [ ] Implement handlers in tool_handlers.py
- [ ] Add to TOOL_HANDLERS export

---

### Phase 3: Resources & Caching (1-2 weeks)

**Goal:** Implement context-aware resources

**Components:**
1. **Agentic Context Resource** (100 lines)
   - GET coderef://context/agentic
   - Caches recent contexts
   - Expires old entries

2. **Context Stats Resource** (100 lines)
   - GET coderef://stats/context
   - Aggregates context data
   - Auto-updates on cache hits

3. **Cache Manager Enhancement** (150 lines)
   - context-specific TTL policies
   - LRU eviction (max 10 contexts)
   - Staleness detection

**Deliverables:**
- [ ] Enhanced resource_cache.py
- [ ] New resource handlers
- [ ] Cache invalidation logic

---

### Phase 4: Integration & Testing (1-2 weeks)

**Goal:** Wire everything together + comprehensive testing

**Components:**
1. **Integration Tests** (200 lines)
   - Test context generation end-to-end
   - Test context-aware queries
   - Test resource access
   - Test cache behavior

2. **Performance Testing**
   - Benchmark context generation time
   - Measure cache hit rates
   - Profile memory usage

3. **Error Scenarios**
   - subprocess timeout
   - CLI not found
   - Invalid context parameters
   - Concurrent context generation

**Deliverables:**
- [ ] test_context_integration.py
- [ ] Performance benchmarks
- [ ] Error handling guide

---

### Phase 5: Documentation (1 week)

**Goal:** Document new capabilities

**Deliverables:**
- [ ] Update README.md with context tools
- [ ] Add context examples to API.md
- [ ] Create context usage guide
- [ ] Update IMPLEMENTATION-GUIDE.md

---

## Technical Details

### Context Bridge Implementation

**File:** `/c/Users/willh/.mcp-servers/coderef-mcp/coderef/bridge/context_bridge.py`

```python
import asyncio
import json
import subprocess
from typing import Dict, Any
from pathlib import Path

class ContextBridge:
    """Bridge between Python MCP server and TypeScript @coderef/core context system."""

    def __init__(self, coderef_cli_path: str):
        self.cli_path = Path(coderef_cli_path)
        self._context_cache = {}

    async def generate_agentic_context(
        self,
        source_dir: str,
        task_description: str,
        keywords: list[str],
        max_complexity: int = 10
    ) -> Dict[str, Any]:
        """Generate agentic context using @coderef/core 6-phase system."""

        # Build CLI command
        cmd = [
            "pnpm", "start", "context-generation",
            "--source-dir", source_dir,
            "--task", task_description,
            "--keywords", ",".join(keywords),
            "--max-complexity", str(max_complexity),
            "--output", "json"
        ]

        try:
            # Execute subprocess with timeout
            result = await asyncio.wait_for(
                asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=self.cli_path.parent
                ),
                timeout=30.0
            )

            stdout, stderr = await asyncio.wait_for(
                result.communicate(),
                timeout=30.0
            )

            if result.returncode != 0:
                raise RuntimeError(f"CLI error: {stderr.decode()}")

            # Parse JSON output
            context_json = json.loads(stdout.decode())

            # Cache the result
            cache_key = f"{source_dir}:{task_description}"
            self._context_cache[cache_key] = context_json

            return context_json

        except asyncio.TimeoutError:
            raise TimeoutError("Context generation timeout (30s)")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON output: {e}")
```

---

### New CLI Command in @coderef/core

**File:** `/coderef-system/packages/cli/src/commands/context-generation.ts`

```typescript
import { AnalyzerService, TaskContextGenerator, AgenticFormatter } from '@coderef/core';

export async function contextGeneration(options: {
  sourceDir: string;
  task: string;
  keywords: string[];
  maxComplexity: number;
  output: 'json' | 'markdown';
}) {
  // 1. Scan source directory
  const analyzer = new AnalyzerService(options.sourceDir);
  const analysis = await analyzer.analyzeCodebase(
    options.sourceDir,
    ['ts', 'tsx', 'js', 'jsx']
  );

  // 2. Generate task context
  const contextGen = new TaskContextGenerator();
  const taskContext = contextGen.generateTaskContext(
    'WO-CONTEXT-001',
    options.task,
    analysis.elements.slice(0, 100),
    {
      keywords: options.keywords,
      maxComplexity: options.maxComplexity
    }
  );

  // 3. Run 6-phase processing
  const scorer = new ComplexityScorer();
  const complexity = scorer.scoreElements(analysis.elements.slice(0, 50));

  const edgeCaseDetector = new EdgeCaseDetector();
  const edgeCases = edgeCaseDetector.detectEdgeCases(analysis.elements);

  const testAnalyzer = new TestPatternAnalyzer();
  const testPatterns = testAnalyzer.analyzeTestPatterns(analysis.elements);

  const exampleExtractor = new ExampleExtractor();
  const examples = exampleExtractor.extractExamples();

  // 4. Format for agents
  const formatter = new AgenticFormatter();
  const agenticContext = formatter.formatContext(
    'WO-CONTEXT-001',
    options.task,
    complexity,
    taskContext,
    edgeCases,
    testPatterns,
    examples
  );

  // 5. Output
  if (options.output === 'json') {
    console.log(JSON.stringify(agenticContext, null, 2));
  } else {
    console.log(formatter.formatAsSummary(agenticContext));
  }
}
```

---

### Unified Index Schema

**File:** `/c/Users/willh/.mcp-servers/coderef-mcp/coderef/models.py`

```python
from pydantic import BaseModel
from typing import Dict, List, Any
from datetime import datetime

class AgenticContext(BaseModel):
    """Complete agentic context from 6-phase system."""
    workorder_id: str
    task_description: str

    # Phase 1: Complexity
    complexity: Dict[str, Any]

    # Phase 2: Task Context
    context: Dict[str, Any]

    # Phase 3: Edge Cases
    edge_cases: Dict[str, Any]

    # Phase 4: Test Patterns
    testing: Dict[str, Any]

    # Phase 5: Code Examples
    examples: Dict[str, Any]

    # Phase 6: Metadata
    metadata: Dict[str, Any]

    # Timestamps & status
    generated_at: datetime
    source_dir: str
    languages: List[str]

class CachedContext(BaseModel):
    """Cached agentic context with TTL."""
    context: AgenticContext
    created_at: datetime
    ttl_seconds: int = 3600
    hit_count: int = 0

    def is_expired(self) -> bool:
        elapsed = (datetime.utcnow() - self.created_at).total_seconds()
        return elapsed > self.ttl_seconds
```

---

## Integration Points & Data Flow

### Complete Data Flow: Query → Context → Response

```
Agent Query
  ↓
MCP Server receives query
  ↓
Check if context exists in cache
  ├─ YES: Return cached context + query results
  └─ NO: Generate fresh context
       ↓
       ContextBridge.generate_agentic_context()
         ├─ Execute: pnpm start context-generation
         ├─ @coderef/core 6-phase processing
         ├─ Return JSON
         └─ Cache result (TTL: 1 hour)
       ↓
Merge context + query results
  ├─ Add complexity metrics
  ├─ Add edge cases
  ├─ Add confidence scores
  └─ Add recommendation
       ↓
Return AgenticContext JSON to MCP client
  ↓
Agent uses context for implementation planning
```

---

## Success Criteria

### Phase 1: Bridge Layer
- [ ] ContextBridge executes @coderef/core CLI successfully
- [ ] Timeout handling works (30s limit)
- [ ] Error cases handled gracefully
- [ ] Results cached in memory

### Phase 2: New Tools
- [ ] generate_agentic_context tool works end-to-end
- [ ] query_with_context returns context data
- [ ] analyze_with_context includes 6-phase data
- [ ] All tools follow MCP tool response format

### Phase 3: Resources
- [ ] coderef://context/agentic accessible
- [ ] coderef://stats/context populated
- [ ] Cache invalidation works
- [ ] Resource data fresh (<5 min old)

### Phase 4: Integration
- [ ] End-to-end test: Query → Context → Response
- [ ] Performance: Context generation <5s (with cache)
- [ ] Memory: Cache stays <100MB (max 10 contexts)
- [ ] Concurrency: Multiple concurrent contexts handled

### Phase 5: Documentation
- [ ] README updated with context tools
- [ ] Examples show context-aware queries
- [ ] Integration guide provided
- [ ] Error scenarios documented

---

## Configuration

**Environment Variables** (add to coderef-mcp):
```bash
# Path to @coderef/core CLI
CODEREF_CLI_PATH=C:\Users\willh\Desktop\projects\coderef-system\packages\cli

# Context cache settings
CONTEXT_CACHE_MAX_SIZE=10          # Max 10 cached contexts
CONTEXT_CACHE_TTL_SECONDS=3600     # 1 hour cache
CONTEXT_SUBPROCESS_TIMEOUT=30      # 30s timeout

# Complexity filters
DEFAULT_MAX_COMPLEXITY=10
DEFAULT_MIN_CONFIDENCE=0.6
```

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Subprocess crashes | Timeout + error handling + retry logic |
| CLI not found | Check PATH, validate CODEREF_CLI_PATH at startup |
| Memory leak (cache) | LRU eviction, max 10 contexts, auto-expire |
| Concurrent access | Async locks, task-based isolation |
| Data mismatch | Unified schema, version tracking |
| Performance degradation | Cache aggressively, async processing, metrics |

---

## Next Steps

1. **Immediate:**
   - [ ] Review this analysis with team
   - [ ] Approve high-level architecture
   - [ ] Plan Phase 1 timeline

2. **Phase 1 (1-2 weeks):**
   - [ ] Create ContextBridge.py
   - [ ] Implement CLI command in @coderef/core
   - [ ] Test subprocess execution

3. **Phase 2 (2-3 weeks):**
   - [ ] Add MCP tool schemas
   - [ ] Implement handlers
   - [ ] Integration testing

4. **Phase 3-5:**
   - [ ] Resources, caching, documentation
   - [ ] Performance optimization
   - [ ] Full system testing

---

## Appendix: Code Examples

### Example: Using query_with_context

```python
# Request
{
  "query": "@Fn/auth/*",
  "include_context": true,
  "rank_by": "complexity"
}

# Response
{
  "elements": [
    {
      "reference": "@Fn/auth/login#authenticate:24",
      "complexity_score": 7.2,
      "risk_level": "high",
      "edge_cases": [
        {"type": "race_condition", "severity": "high"}
      ],
      "dependents": 12,
      "test_coverage": 0.92,
      "confidence": 0.88,
      "recommendation": "High complexity function with race condition risk. Recommend breaking into smaller functions."
    }
  ]
}
```

### Example: Using generate_agentic_context

```python
# Request
{
  "workorder_id": "WO-AUTH-REFACTOR-001",
  "task_description": "Refactor authentication module",
  "source_dir": "./src",
  "languages": ["ts", "tsx"],
  "filter_criteria": {
    "keywords": ["auth", "login", "token"],
    "max_complexity": 8
  }
}

# Response
{
  "workorder_id": "WO-AUTH-REFACTOR-001",
  "task_description": "Refactor authentication module",
  "complexity": {
    "functionsByComplexity": [
      {
        "name": "authenticateUser",
        "complexity": 7.2,
        "lines": 45,
        "riskLevel": "high"
      },
      ...
    ],
    "stats": {
      "min": 1,
      "max": 8,
      "avg": 4.2,
      "median": 4
    }
  },
  "context": {
    "functionsToModify": 10,
    "impactedFunctions": 5,
    "riskLevel": "medium"
  },
  "edgeCases": {
    "criticalIssues": 2,
    "issues": [...]
  },
  "testing": {
    "coveragePercentage": 87.5,
    "testFiles": 12
  },
  "examples": {
    "patternExamples": [...],
    "antiPatternsToAvoid": [...]
  },
  "metadata": {
    "confidence": {
      "overall": 0.88,
      "level": "high"
    },
    "processingStats": {
      "elementsAnalyzed": 1021,
      "edgeCasesDetected": 5,
      "processingTimeMs": 2341
    }
  }
}
```

---

## Conclusion

This integration transforms coderef-mcp from a query-and-validate tool into an **agentic context provider**. By wiring the 6-phase context system into the MCP server, agents will receive:

✅ Complexity metrics
✅ Risk assessments
✅ Edge case warnings
✅ Test coverage data
✅ Code examples & anti-patterns
✅ Confidence scores
✅ Actionable recommendations

This enables agents to make informed decisions during implementation, reducing bugs and improving code quality.
