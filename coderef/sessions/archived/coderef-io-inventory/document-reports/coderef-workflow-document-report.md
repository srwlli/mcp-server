# Document Report - coderef-workflow

**Agent:** coderef-workflow
**Workorder:** WO-CODEREF-IO-INVENTORY-002
**Step:** 2 - Complete File List with Source/Destination Tracking
**Generated:** 2026-01-02

---

## Complete Document List

| Filename | Type | I/O | Source/Destination | Notes |
|----------|------|-----|-------------------|-------|
| README.md | foundation_doc | both | Project root | Generate overview / read context |
| ARCHITECTURE.md | foundation_doc | input | Project root OR coderef/foundation-docs/ | Planning context extraction |
| API.md | foundation_doc | both | Project root OR coderef/foundation-docs/ | Generate/read API endpoints |
| COMPONENTS.md | foundation_doc | both | Project root OR coderef/foundation-docs/ | Generate/read component hierarchy |
| SCHEMA.md | foundation_doc | both | Project root OR coderef/foundation-docs/ | Generate/read database schema |
| USER-GUIDE.md | foundation_doc | input | Project root | Planning context extraction |
| project-context.json | foundation_doc | output | coderef/foundation-docs/ | Structured planning context |
| BEHAVIOR-STANDARDS.md | standard_doc | input | coderef/standards/ | Existence check during planning |
| COMPONENT-PATTERN.md | standard_doc | input | coderef/standards/ | Existence check during planning |
| UI-STANDARDS.md | standard_doc | input | coderef/standards/ | Existence check during planning |
| UX-PATTERNS.md | standard_doc | input | coderef/standards/ | Existence check during planning |
| COMPONENT-INDEX.md | standard_doc | input | coderef/standards/ | Existence check during planning |
| plan.json | workflow_doc | both | coderef/workorder/{feature}/ | Generate 10-section plan / load plan |
| context.json | workflow_doc | both | coderef/workorder/{feature}/ | Save requirements / load context |
| analysis.json | workflow_doc | both | coderef/workorder/{feature}/ | Save project analysis / load for planning |
| DELIVERABLES.md | workflow_doc | both | coderef/workorder/{feature}/ | Generate template / read metrics |
| communication.json | workflow_doc | both | coderef/workorder/{feature}/ | Generate multi-agent / read coordination |
| claude.md | workflow_doc | output | coderef/workorder/{feature}/ | Generate agent handoff context |
| index.json | coderef_output | input | .coderef/ | Priority 1: Fast inventory read |
| graph.json | coderef_output | input | .coderef/ | Dependency graph for diagrams |
| context.md | coderef_output | input | .coderef/ | Human-readable context |
| patterns.json | coderef_output | input | .coderef/reports/ | AST-based pattern detection |
| coverage.json | coderef_output | input | .coderef/reports/ | Test coverage gap analysis |
| complexity.json | coderef_output | input | .coderef/reports/ | Code complexity metrics |
| workorder-log.txt | other | both | coderef/ | Append workorder entries / read history |
| archive-index.json | other | both | coderef/archived/ | Update archive metadata / read archive |
| manifest.json | other | input | coderef/inventory/ | Priority 3: Legacy inventory fallback |
| api.json | other | input | coderef/inventory/ | Legacy API inventory fallback |
| database.json | other | input | coderef/inventory/ | Legacy DB inventory fallback |
| dependencies.json | other | input | coderef/inventory/ | Legacy dependency fallback |
| config.json | other | input | coderef/inventory/ | Legacy config inventory fallback |
| tests.json | other | input | coderef/inventory/ | Legacy test inventory fallback |
| documentation.json | other | input | coderef/inventory/ | Legacy doc inventory fallback |
| package.json | config | input | Project root | Tech stack detection (Node.js) |
| requirements.txt | config | input | Project root | Tech stack detection (Python) |
| pyproject.toml | config | input | Project root | Tech stack detection (Python) |
| go.mod | config | input | Project root | Tech stack detection (Go) |
| Cargo.toml | config | input | Project root | Tech stack detection (Rust) |
| review-{feature}-{timestamp}.md | other | output | coderef/planning-reviews/ | Plan validation reports |
| risk-{feature}-{timestamp}.json | other | output | coderef/risk-assessments/ | Risk assessment reports |
| audit-{timestamp}.md | other | output | coderef/audits/ | Plan audit reports |
| features-inventory.json | other | output | coderef/ | Feature inventory (JSON) |
| features-inventory.md | other | output | coderef/ | Feature inventory (Markdown) |

**Total Documents:** 42 unique filenames
**Inputs:** 28
**Outputs:** 19
**Both:** 9

---

## Cross-Agent Dependencies

### Inputs FROM Other Agents

| Source Agent | Document | Purpose |
|--------------|----------|---------|
| coderef-context | .coderef/index.json | Code element inventory (3-tier priority) |
| coderef-context | .coderef/graph.json | Dependency graph for architecture diagrams |
| coderef-context | .coderef/context.md | Human-readable codebase summary |
| coderef-context | .coderef/reports/patterns.json | AST-based pattern detection (99% accuracy) |
| coderef-context | .coderef/reports/coverage.json | Test coverage gap analysis |
| coderef-context | .coderef/reports/complexity.json | Code complexity metrics |
| coderef-docs | coderef/standards/*.md | Standards documents (existence checking) |
| User/Agent | coderef/workorder/{feature}/context.json | Requirements gathered by user/agent |
| User/Agent | coderef/workorder/{feature}/plan.json | Implementation plans (for reading/updating) |

### Outputs TO Other Agents

| Destination Agent | Document | Purpose |
|-------------------|----------|---------|
| coderef-docs | coderef/foundation-docs/*.md | Foundation docs for documentation system |
| coderef-docs | coderef/workorder/{feature}/DELIVERABLES.md | Metrics tracking for changelog generation |
| All Agents | coderef/workorder/{feature}/plan.json | 10-section implementation plan |
| All Agents | coderef/workorder/{feature}/communication.json | Multi-agent coordination file |
| All Agents | coderef/workorder/{feature}/claude.md | Agent handoff context |
| All Agents | coderef/workorder-log.txt | Global workorder audit trail |
| coderef-personas | coderef/workorder/{feature}/plan.json | Task assignments for persona activation |

---

## External Sources

### Generated FROM External Tools

| Tool/Source | Document | How Generated |
|-------------|----------|---------------|
| coderef_scan (MCP) | .coderef/index.json | Called when .coderef/ unavailable (Priority 2) |
| coderef_patterns (MCP) | .coderef/reports/patterns.json | AST-based pattern detection |
| coderef_coverage (MCP) | .coderef/reports/coverage.json | Test coverage analysis |
| User Input | coderef/workorder/{feature}/context.json | Gathered via /gather-context command |
| Git History | coderef/workorder/{feature}/DELIVERABLES.md | Metrics populated from git log |

### Consumed BY External Tools

| Tool/Consumer | Document | How Used |
|---------------|----------|----------|
| coderef-docs generators | coderef/foundation-docs/*.md | Source for POWER framework docs |
| CI/CD pipelines | coderef/workorder-log.txt | Audit trail for deployments |
| Agents | coderef/workorder/{feature}/plan.json | Execution guidance |
| Dashboard UI | coderef/features-inventory.json | Visual feature tracking |

---

## 3-Tier Priority System

coderef-workflow uses a sophisticated fallback system for code intelligence:

**Priority 1 (FASTEST):** Read `.coderef/index.json` if available
↓ Falls back to...
**Priority 2 (LIVE SCAN):** Call `coderef_scan` MCP tool for real-time AST analysis
↓ Falls back to...
**Priority 3 (LEGACY):** Read `coderef/inventory/*.json` manifests

This ensures graceful degradation when .coderef/ outputs are unavailable or stale.

---

## Dual-Location Strategy

Foundation documents are checked in **two locations** to maximize flexibility:

1. **Project Root:** README.md, ARCHITECTURE.md, API.md, etc.
2. **coderef/foundation-docs/:** Centralized documentation directory

Planning workflows read from either location, with root taking precedence.

---

## Key Insights

1. **Most Integrated Server:** coderef-workflow has the highest document utilization (42 unique files, 90% ecosystem integration)
2. **Smart Fallbacks:** 3-tier priority system prevents failures when .coderef/ unavailable
3. **Dual Consumers:** Reads .coderef/ outputs from coderef-context AND generates foundation docs for coderef-docs
4. **Legacy Support:** Maintains compatibility with coderef/inventory/ manifests (7 legacy files)
5. **Complete Lifecycle:** Orchestrates entire feature workflow from context → plan → execution → deliverables → archive

---

**Report Complete:** 2026-01-02
**Next Step:** Aggregate all agent reports for ecosystem-wide document map
