# Document Report: coderef-system

**Agent ID:** coderef-system
**Agent Path:** C:\Users\willh\Desktop\projects\coderef-system
**Workorder:** WO-CODEREF-IO-INVENTORY-002
**Generated:** 2026-01-02

---

## Complete Document List

| Filename | Type | I/O | Source/Destination | Notes |
|----------|------|-----|-------------------|-------|
| `.coderef/index.json` | coderef_output | both | Self-generated/consumed | Element inventory from scan |
| `.coderef/context.md` | coderef_output | both | Self-generated/consumed | Human-readable analysis |
| `.coderef/context.json` | coderef_output | output | → Other MCP servers | Machine-readable context |
| `.coderef/graph.json` | coderef_output | both | Self-generated/consumed | Complete dependency graph |
| `.coderef/config.json` | config | both | User settings/CLI init | User preferences & scan settings |
| `.coderef/.gitignore` | config | output | → Git | Ignore .coderef/ from version control |
| `.coderef/reports/patterns.json` | coderef_output | both | Self-generated/consumed | Code pattern analysis |
| `.coderef/reports/coverage.json` | coderef_output | both | Self-generated/consumed | Test coverage metrics |
| `.coderef/reports/complexity.json` | coderef_output | both | Self-generated/consumed | Complexity metrics by element |
| `.coderef/diagrams/dependencies.mmd` | coderef_output | output | → Visualization tools | Mermaid dependency diagram |
| `.coderef/diagrams/dependencies.dot` | coderef_output | output | → Graphviz | Graphviz dependency diagram |
| `.coderef/exports/graph.json` | coderef_output | both | Self-generated/consumed | Exported graph (JSON format) |
| `.coderef/exports/graph.graphql` | coderef_output | output | → GraphQL consumers | Exported graph (GraphQL schema) |
| `.coderef/exports/graph.jsonld` | coderef_output | output | → Semantic web tools | Exported graph (JSON-LD format) |
| `.coderef/rag/state.json` | coderef_output | both | Self-generated/consumed | RAG indexer incremental state |
| `.coderef/vector-store.json` | coderef_output | both | Self-generated/consumed | Vector embeddings for RAG |
| `coderef/foundation-docs/README.md` | foundation_doc | output | → Developers/agents | Auto-generated project overview |
| `coderef/foundation-docs/ARCHITECTURE.md` | foundation_doc | output | → Developers/agents | Auto-generated architecture docs |
| `coderef/foundation-docs/API.md` | foundation_doc | output | → Developers/agents | Auto-generated API reference |
| `coderef/foundation-docs/COMPONENTS.md` | foundation_doc | output | → UI projects | Auto-generated component hierarchy |
| `coderef/foundation-docs/SCHEMA.md` | foundation_doc | output | → Developers/agents | Auto-generated data schema docs |
| `coderef/foundation-docs/JS-AST-ANALYSIS.md` | foundation_doc | output | → Developers | AST analysis insights |
| `coderef/foundation-docs/PERFORMANCE-GUIDE.md` | foundation_doc | output | → Developers | Performance recommendations |
| `coderef/foundation-docs/USER-GUIDE.md` | foundation_doc | output | → End users | User documentation |
| `src/**/*.{ts,tsx,js,jsx,py}` | other | both | User projects/CLI tool | Source code scanning + tag injection |
| `tests/**/*.{ts,tsx,js,jsx,py}` | other | input | User projects | Test files for coverage analysis |
| `package.json` | config | input | Node.js/npm | Dependency checks in tests |
| `tsconfig.json` | config | input | TypeScript compiler | TypeScript configuration |
| `packages/cli/src/dashboard/index.html` | other | input | CLI package | Dashboard template |
| `packages/cli/src/dashboard/styles.css` | other | input | CLI package | Dashboard styles |
| `packages/cli/src/dashboard/dashboard.js` | other | input | CLI package | Dashboard script |
| `{custom-output-path}` | coderef_output | output | → User-specified | CLI --output flag destination |
| `dashboard.html` | other | output | → Web browsers | Interactive dashboard visualization |
| `breaking-changes-report.{json,md,html}` | coderef_output | output | → Developers/agents | Breaking change detection report |
| `drift-report.{json,md}` | coderef_output | output | → Developers/agents | Stale reference detection |
| `validation-report.{json,md}` | coderef_output | output | → Developers/agents | CodeRef tag validation |

---

## Cross-Agent Dependencies

### Documents Consumed FROM coderef-system

**Primary Consumers:** coderef-workflow, coderef-docs, coderef-context, coderef-personas

| Document | Consumer Agents | Usage |
|----------|----------------|-------|
| `.coderef/index.json` | coderef-workflow, coderef-docs, coderef-personas | Element inventory for planning/docs/analysis |
| `.coderef/context.md` | coderef-workflow, coderef-docs | Human-readable context for agents |
| `.coderef/context.json` | coderef-workflow | Machine-readable context for orchestration |
| `.coderef/graph.json` | coderef-workflow, coderef-context | Dependency analysis for planning |
| `.coderef/reports/patterns.json` | coderef-docs, coderef-personas | Code patterns for standards/personas |
| `.coderef/reports/coverage.json` | coderef-workflow, coderef-testing | Test coverage for risk assessment |
| `.coderef/reports/complexity.json` | coderef-workflow | Complexity metrics for planning |
| `coderef/foundation-docs/*.md` | All agents | Project context for all workflows |

### Documents Provided TO coderef-system

**None** - coderef-system is a pure producer. It scans source code and generates analysis outputs but does not consume documents from other MCP servers.

---

## External Sources

### Input Sources (Origin: Outside CodeRef Ecosystem)

| Source Type | Files | Origin |
|-------------|-------|--------|
| User source code | `src/**/*.{ts,tsx,js,jsx,py}` | Developer codebases being analyzed |
| User test files | `tests/**/*.{ts,tsx,js,jsx,py}` | Developer test suites |
| Node.js ecosystem | `package.json` | npm/yarn package management |
| TypeScript compiler | `tsconfig.json` | TypeScript configuration |
| CLI package internals | `packages/cli/src/dashboard/*` | coderef-system's own dashboard assets |

### Output Destinations (Outside CodeRef Ecosystem)

| Destination | Files | Purpose |
|-------------|-------|---------|
| Web browsers | `dashboard.html` | Interactive visualization |
| Graphviz tools | `.coderef/diagrams/dependencies.dot` | Dependency visualization |
| Mermaid renderers | `.coderef/diagrams/dependencies.mmd` | Dependency diagrams |
| GraphQL consumers | `.coderef/exports/graph.graphql` | GraphQL schema integration |
| Semantic web tools | `.coderef/exports/graph.jsonld` | Linked data applications |
| Developer IDEs | `breaking-changes-report.*`, `drift-report.*`, `validation-report.*` | Code quality feedback |

---

## Notes

### Primary Role
**coderef-system** is the foundational analysis engine - it's a **PRODUCER**, not a consumer. It reads source code and generates all .coderef/ outputs consumed by other MCP servers.

### Data Flow Pattern
```
User Source Code
    ↓ (scan)
coderef-system CLI
    ↓ (generate)
.coderef/ outputs
    ↓ (consume)
Other MCP Servers (workflow, docs, personas, testing)
    ↓ (orchestrate)
Agent-driven development
```

### Key Characteristics
- **17 inputs:** Primarily source code and .coderef/ files (for re-analysis)
- **30 outputs:** Comprehensive .coderef/ analysis files + foundation docs
- **Both directions:** Some files (index.json, graph.json, reports/*) are both generated and re-read for incremental analysis
- **No upstream dependencies:** Does not consume documents from other MCP servers
- **Pure producer:** All other servers depend on coderef-system's outputs

### Generation Tools
- **TypeScript CLI** (packages/cli/): Commands like `scan`, `context`, `query`, `impact`, `diagram`
- **Python scripts** (scripts/): Foundation doc generators that read .coderef/ outputs
- **Core library** (packages/core/): Analysis engine with AST parsing, graph building, complexity scoring

---

**Total Documents:** 36 unique file patterns
**Inputs:** 17
**Outputs:** 30
**Both:** 11 (files that are generated and later consumed)
