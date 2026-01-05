# CodeRef Document Reports Resource Sheet

**Generated:** 2026-01-03
**Source:** `coderef-io-inventory/document-reports` analysis
**Scope:** 9 Agents/Components

---

## 1. Agent Roles & Document Interactions

| Agent | Primary Role | Key Inputs | Key Outputs |
| :--- | :--- | :--- | :--- |
| **assistant** | Orchestrator & Workorder Manager | `plan.json`, `DELIVERABLES.md`, `CLAUDE.md`, `projects.md` | `context.json`, `communication.json`, `workorders.json`, `dashboard/index.html` |
| **coderef-context** | Code Intelligence Producer | `CLAUDE.md`, `src/**/*` (Source Code) | `.coderef/index.json`, `.coderef/graph.json`, `.coderef/reports/*.json`, `coderef/foundation-docs/*.md` |
| **coderef-dashboard** | Visualization & Aggregation | `plan.json`, `.coderef/index.json`, `DELIVERABLES.md`, `projects.config.json` | `plan.json` (creation), Build Artifacts |
| **coderef-docs** | Documentation Generator | `.coderef/*` outputs, `plan.json`, `context.json`, templates | `coderef/foundation-docs/*.md`, `coderef/user/*.md`, `coderef/standards/*.md`, `CHANGELOG.json` |
| **coderef-personas** | Persona Manager & Lloyd Host | `plan.json`, `CLAUDE.md`, `lloyd.json`, custom persona definitions | `personas/custom/*.json`, `plan.json` (status updates) |
| **coderef-system** | Core Analysis Engine | Source Code (`src/`, `tests/`), `.coderef/*` (re-analysis) | All `.coderef/*` outputs (index, graph, reports, diagrams, exports), `foundation-docs` |
| **coderef-testing** | Test Automation & Validation | `plan.json`, `.coderef/drift.json`, Test Configs (`jest.config.js` etc.) | `{feature}-testing-proof.md`, `.test-archive/*.json` |
| **coderef-workflow** | Workflow Orchestrator | `.coderef/index.json`, `.coderef/graph.json`, `context.json` | `plan.json`, `DELIVERABLES.md`, `communication.json`, `claude.md`, `workorder-log.txt` |
| **papertrail** | Validation & Transformation Layer | Internal Schemas, `plan.json`, Arbitrary Markdown/JSON | Validated Documents (with UDS headers), `coderef/context/*-health.json` |

---

## 2. Critical Ecosystem Documents

These documents form the backbone of agent interoperability.

| Filename Pattern | Type | Producer(s) | Consumer(s) | Description |
| :--- | :--- | :--- | :--- | :--- |
| **`plan.json`** | Workflow | `coderef-workflow`, `coderef-dashboard` | `assistant`, `coderef-docs`, `coderef-personas`, `coderef-testing`, `papertrail` | The central implementation plan. Driving force for execution agents. |
| **`context.json`** | Workflow | `assistant`, `coderef-workflow` | `coderef-workflow`, `coderef-dashboard`, `coderef-docs` | Structured feature requirements and goals. |
| **`DELIVERABLES.md`** | Workflow | `coderef-workflow` | `assistant`, `coderef-dashboard` | Checklist of required outputs and verification steps. |
| **`communication.json`** | Workflow | `assistant`, `coderef-workflow` | All Agents | Multi-agent coordination and status tracking. |
| **`.coderef/index.json`** | Analysis | `coderef-context`, `coderef-system` | `coderef-workflow`, `coderef-dashboard`, `coderef-docs`, `coderef-testing` | Complete codebase element inventory. Primary source of code truth. |
| **`.coderef/graph.json`** | Analysis | `coderef-context`, `coderef-system` | `coderef-workflow`, `coderef-docs` | Dependency graph for impact analysis and visualization. |
| **`.coderef/reports/patterns.json`** | Analysis | `coderef-context`, `coderef-system` | `coderef-docs`, `coderef-personas` | AST-based code patterns for standards and persona context. |
| **`coderef/foundation-docs/*.md`** | Foundation | `coderef-docs`, `coderef-system` | All Agents | Core project documentation (README, ARCHITECTURE, API, etc.). |
| **`CLAUDE.md`** | Foundation | Human / Template | `assistant`, `coderef-context`, `coderef-dashboard`, `coderef-docs`, `coderef-personas`, `coderef-testing` | Primary context document for AI agents (rules, commands, style). |
| **`workorders.json`** | Workflow | `assistant` | `assistant` | Central tracking of all active and completed workorders. |

---

## 3. Data Flow Patterns

### Workorder Lifecycle Flow
1.  **Initiation**: `assistant` or `coderef-dashboard` gathers requirements into `context.json`.
2.  **Planning**: `coderef-workflow` consumes `context.json` and `.coderef/index.json` to generate `plan.json`.
3.  **Coordination**: `assistant` or `coderef-workflow` initializes `communication.json` for multi-agent tasks.
4.  **Execution**: `coderef-personas` (Lloyd/Ava/Marcus) read `plan.json` to execute tasks.
5.  **Tracking**: `coderef-personas` update `plan.json` status; `coderef-dashboard` reads `plan.json` and `DELIVERABLES.md` to visualize progress.
6.  **Verification**: `coderef-testing` reads `plan.json` (testing strategy) to generate `{feature}-testing-proof.md`.
7.  **Completion**: `coderef-workflow` finalizes `DELIVERABLES.md` and archives the workorder.

### Documentation Generation Flow
1.  **Analysis**: `coderef-system` scans source code and produces `.coderef/*` outputs (index, graph, reports).
2.  **Synthesis**: `coderef-docs` consumes `.coderef/*` outputs and templates.
3.  **Generation**: `coderef-docs` generates `coderef/foundation-docs/*.md` and `coderef/user/*.md`.
4.  **Consumption**: All other agents read `foundation-docs` to understand the project context.

### Analysis & Intelligence Flow
1.  **Scan**: `coderef-system` (or `coderef-context`) runs AST scan on source files.
2.  **Output**: Generates `.coderef/index.json` (Inventory) and `.coderef/graph.json` (Relationships).
3.  **Intelligence**:
    *   `coderef-workflow` uses inventory for smart planning.
    *   `coderef-testing` uses drift (from context) for impact-based testing.
    *   `coderef-dashboard` uses inventory for stats and visualization.
    *   `coderef-personas` uses patterns for context-aware coding.

---

## 4. Summary Statistics

| Category | Count |
| :--- | :--- |
| **Total Agents Analyzed** | 9 |
| **Total Unique Documents** | ~100+ (across all reports) |
| **Primary Workflow Documents** | 4 (`plan.json`, `context.json`, `DELIVERABLES.md`, `communication.json`) |
| **Primary Analysis Documents** | 3 (`index.json`, `graph.json`, `context.md`) |
| **Most Connected Agent** | `coderef-workflow` (Integrates with almost all other agents via plan/context) |
| **Most Consumed Output** | `.coderef/index.json` & `plan.json` |

---

**Document Version:** 1.0.0
**Last Updated:** 2026-01-03
**Maintained By:** CodeRef Team
