# CodeRef Ecosystem - Quick Reference & Comparison

**Date:** December 26, 2025
**Purpose:** Visual comparison of all 4 MCP servers

---

## At a Glance

```
┌─────────────────────────────────────────────────────────────────┐
│                    4-SERVER ECOSYSTEM                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  coderef-context     coderef-workflow    coderef-docs          │
│  ┌─────────────┐     ┌──────────────┐    ┌──────────────┐      │
│  │ CODE        │     │ PLANNING &   │    │ DOCS &       │      │
│  │ INTELLIGENCE│────▶│ ORCHESTRATION│───▶│ CHANGELOG    │      │
│  │ (10 tools)  │     │ (23 tools)   │    │ (11 tools)   │      │
│  └─────────────┘     └──────────────┘    └──────────────┘      │
│  Version: NONE       Version: 1.1.0      Version: 3.1.0        │
│  CLAUDE.md: ❌       CLAUDE.md: ✅       CLAUDE.md: ✅         │
│                            ▲                                    │
│                            │                                    │
│                      coderef-personas                           │
│                      ┌──────────────┐                           │
│                      │ AGENT        │                           │
│                      │ PERSONAS     │                           │
│                      │ (5 personas) │                           │
│                      └──────────────┘                           │
│                      Version: 1.4.0                             │
│                      CLAUDE.md: ✅                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Server Profiles

### 1️⃣ coderef-context
**Status:** ⚠️ UNDOCUMENTED (no CLAUDE.md)

| Metric | Value |
|--------|-------|
| **Version** | ❌ NONE |
| **CLAUDE.md Lines** | ❌ 0 (MISSING) |
| **Tools** | 10 (scan, query, impact, patterns, coverage, complexity, validate, drift, diagram, context) |
| **Purpose** | Code intelligence via AST analysis and dependency tracking |
| **Wraps** | @coderef/core CLI (TypeScript, separate project) |
| **Key Clients** | coderef-workflow (for planning intelligence) |
| **mcp.json Metadata** | ✅ Full (description + tools list) |
| **Status** | 🟡 FUNCTIONAL but UNDOCUMENTED |

**What It Does:**
- Scans codebases with AST analysis
- Analyzes dependency graphs (what-calls, what-imports)
- Detects code patterns
- Identifies breaking change impacts
- Calculates code complexity
- Provides comprehensive code intelligence

---

### 2️⃣ coderef-workflow
**Status:** ✅ WELL-DOCUMENTED

| Metric | Value |
|--------|-------|
| **Version** | 1.1.0 |
| **CLAUDE.md Lines** | 659 |
| **Tools** | 23 (planning, execution, archival, coordination) |
| **Purpose** | Feature lifecycle orchestration and planning |
| **Depends On** | coderef-context (for code intelligence during planning) |
| **Key Clients** | AI agents implementing features |
| **mcp.json Metadata** | ❌ Minimal |
| **Status** | ✅ PRODUCTION - Well-integrated |

**What It Does:**
- Gathers feature requirements (gather_context)
- Analyzes projects for planning (calls coderef-context)
- Creates 10-section implementation plans
- Validates plan quality (0-100 score)
- Executes plans and tracks tasks
- Archives completed features
- Manages workorder IDs for audit trail

**Latest Update (v1.1.0):**
- Workorder ID tracking
- Bug fixes in plan generation
- Status lifecycle improvements

---

### 3️⃣ coderef-docs
**Status:** ✅ WELL-DOCUMENTED (Lean)

| Metric | Value |
|--------|-------|
| **Version** | 3.1.0 |
| **CLAUDE.md Lines** | 245 (Lean, focused) |
| **Tools** | 11 (docs generation, changelog, standards, quickref) |
| **Purpose** | Documentation generation and standards enforcement |
| **Depends On** | coderef-workflow (for feature context) |
| **Framework** | POWER (Purpose, Overview, What/Why/When, Examples, References) |
| **mcp.json Metadata** | ❌ Minimal |
| **Status** | ✅ PRODUCTION - Focused, efficient |

**What It Does:**
- Generates foundation documentation (README, ARCHITECTURE, SCHEMA, API, COMPONENTS)
- Manages CHANGELOG with git auto-detection (agentic recording)
- Establishes coding standards from codebase analysis
- Audits codebase for standards compliance
- Generates interactive quickref guides for any app type

**Latest Update (v3.1.0):**
- Smart changelog recording with git integration
- Standards audit system (establish → audit → check consistency)
- Interactive quickref generation

**Efficiency:** 93% reduction from v2.0.0 (3,250 → 245 lines) - maximally focused

---

### 4️⃣ coderef-personas
**Status:** ✅ WELL-DOCUMENTED

| Metric | Value |
|--------|-------|
| **Version** | 1.4.0 |
| **CLAUDE.md Lines** | 552 |
| **Personas** | 5 (mcp-expert, lloyd, ava, marcus, quinn) |
| **Purpose** | Expert agent personas with specialized knowledge |
| **Can Call** | Other MCP tools (with persona expertise applied) |
| **Key Innovation** | Personas use other tools with specialized knowledge |
| **mcp.json Metadata** | ❌ Minimal |
| **Status** | ✅ PRODUCTION - Optimized |

**What It Does:**
- Provides expert MCP protocol knowledge (mcp-expert)
- Coordinates multi-agent workflows (lloyd - orchestrator)
- Specializes for frontend (ava), backend (marcus), testing (quinn)
- Each persona can call coderef-workflow, coderef-docs tools with expert knowledge
- Personas are independent, no hierarchical dependencies

**Latest Update (v1.4.0):**
- Lloyd persona optimized (1,017 → 153 lines, 85% reduction)
- Reference documentation extracted to external docs

---

## Side-by-Side Comparison

### Documentation Quality

```
Lines          Tool Count        Maturity          Status
coderef-workflow:  659 lines      23 tools          ✅ Mature          ✅ Production
coderef-personas:  552 lines      5 personas        ✅ Mature          ✅ Production
coderef-docs:      245 lines      11 tools          ✅ Lean & focused   ✅ Production
coderef-context:   0 lines        10 tools          ❌ UNDOCUMENTED     ⚠️ Functional
```

### Version Distribution

```
coderef-context:   v? (NONE)
coderef-workflow:  v1.1.0  (workorder-centric, production)
coderef-docs:      v3.1.0  (mature documentation focus)
coderef-personas:  v1.4.0  (optimized agents)
```

### Configuration in Global mcp.json

```json
// coderef-context: FULL metadata
"coderef-context": {
  "command": "python",
  "args": [...],
  "cwd": "...",
  "env": { "CODEREF_CLI_PATH": "..." },      // ← Has env config
  "description": "...",                       // ← Has description
  "tools": [...]                              // ← Lists all tools
}

// coderef-workflow: MINIMAL
"coderef-workflow": {
  "command": "python",
  "args": [...],
  "cwd": "..."
  // NO description, tools list, or env config
}

// coderef-docs: MINIMAL
"coderef-docs": {
  "command": "python",
  "args": [...],
  "cwd": "..."
  // NO description, tools list, or env config
}

// coderef-personas: MINIMAL
"coderef-personas": {
  "command": "python",
  "args": [...],
  "cwd": "..."
  // NO description, tools list, or env config
}
```

---

## Feature Matrix

| Feature | context | workflow | docs | personas |
|---------|---------|----------|------|----------|
| **Code Analysis** | ✅ | — | — | — |
| **Planning** | — | ✅ | — | — |
| **Documentation** | — | — | ✅ | — |
| **Agent Expertise** | — | — | — | ✅ |
| **Workorder Tracking** | — | ✅ | — | — |
| **Changelog Management** | — | — | ✅ | — |
| **Standards Auditing** | — | — | ✅ | — |
| **Persona Switching** | — | — | — | ✅ |

---

## Data Flow

### Feature Lifecycle (How Servers Work Together)

```
1. User calls /stub (in ~/.claude/commands/)
   ↓
2. User calls /create-workorder
   ↓
3. coderef-workflow: gather_context()
   ↓
4. coderef-workflow: analyze_project_for_planning()
   ├─→ Calls coderef-context: coderef_scan() [gets inventory]
   └─→ Calls coderef-context: coderef_query() [gets dependencies]
   ↓
5. coderef-workflow: create_plan()
   ├─→ Calls coderef-context: coderef_impact() [breaking changes]
   └─→ Calls coderef-context: coderef_patterns() [code patterns]
   ↓
6. coderef-workflow: validate_implementation_plan()
   ├─→ Generates plan.json (10 sections)
   └─→ Generates DELIVERABLES.md template
   ↓
7. AI Agent (with coderef-personas persona)
   ↓
8. coderef-workflow: execute_plan()
   ├─→ Generate TodoWrite task list
   └─→ Track progress
   ↓
9. coderef-docs: record_changes()
   ├─→ Auto-detects git changes
   └─→ Updates CHANGELOG.json with workorder tracking
   ↓
10. coderef-workflow: archive_feature()
    └─→ Move to coderef/archived/ (historical reference)
```

---

## Integration Points

### coderef-context ← Used By

- **coderef-workflow** (during planning phase)
  - gather_context() calls coderef_scan
  - create_plan() calls coderef_query, coderef_impact, coderef_patterns
  - validate_implementation_plan() optionally uses impact analysis

### coderef-workflow ← Used By

- **AI Agents** (with coderef-personas persona)
  - execute_plan() for task execution
  - Agents track progress in DELIVERABLES.md

### coderef-docs ← Used By

- **coderef-workflow** (at feature completion)
  - record_changes() to update CHANGELOG
  - generate_foundation_docs() to create initial docs
  - archive_feature() triggers documentation

### coderef-personas ← Used By

- **AI Agents**
  - use_persona('lloyd') for orchestration
  - use_persona('ava') for frontend expertise
  - use_persona('marcus') for backend expertise
  - use_persona('quinn') for testing expertise

---

## Critical Gaps

### Gap 1: Missing coderef-context Documentation
```
coderef-context is FUNCTIONAL but has NO CLAUDE.md

Impact: AI agents cannot quickly understand what tools are available
        or how to use them effectively.

Fix: Create coderef-context/CLAUDE.md (~350 lines)
     Document: 10 tools, use cases, architecture, integration patterns
```

### Gap 2: Inconsistent mcp.json Metadata
```
Only coderef-context has metadata in .mcp.json
Other servers have minimal configuration

Question: Should all servers have detailed metadata or none?
Decision needed: Standardize approach
```

### Gap 3: No coderef-context Version
```
All servers have versions (1.1.0, 3.1.0, 1.4.0) except coderef-context

Recommendation: Define v2.0.0 for coderef-context
(v1.x suggests immature; coderef-context is stable and mature)
```

---

## Consistency Checklist

- [x] All servers registered in ~/.mcp.json
- [x] All servers have server.py entry point
- [x] All servers follow global deployment rule
- [ ] ❌ All servers have CLAUDE.md (coderef-context missing)
- [ ] ❌ All servers have version (coderef-context missing)
- [ ] ❌ All servers have consistent mcp.json metadata

**Completion:** 4/7 items (57%)

---

## Key Insights

### 1. Clear Division of Responsibility
- **coderef-context**: Intelligence
- **coderef-workflow**: Orchestration
- **coderef-docs**: Documentation
- **coderef-personas**: Expertise

No overlap, well-designed separation of concerns.

### 2. Mature Integration Points
The servers integrate smoothly:
- coderef-context provides intelligence to coderef-workflow
- coderef-workflow orchestrates and calls coderef-context
- coderef-docs documents coderef-workflow outputs
- coderef-personas enhance AI agent behavior across all tools

### 3. Global-First Architecture
All configuration is global (`~/.mcp.json`, `~/.claude/commands/`)
No local mcp.json files in any server
Follows "single source of truth" principle correctly.

### 4. Documentation Quality Variance
- coderef-workflow: Comprehensive (659 lines)
- coderef-personas: Detailed (552 lines)
- coderef-docs: Lean & efficient (245 lines)
- coderef-context: Missing (0 lines) ← CRITICAL

### 5. Version Maturity Pattern
- v1.1.0 (workflow): Enterprise-grade, workorder-centric
- v3.1.0 (docs): Mature documentation focus
- v1.4.0 (personas): Optimized through iterations
- v?.?.? (context): UNKNOWN - needs version definition

---

## Recommendations Summary

| Priority | Action | Impact |
|----------|--------|--------|
| 🔴 CRITICAL | Create coderef-context/CLAUDE.md | Unblock documentation, enable understanding |
| 🟡 MEDIUM | Standardize mcp.json metadata | Improve consistency across ecosystem |
| 🟡 MEDIUM | Define coderef-context version | Complete version alignment |
| 🟠 MINOR | Add integration examples | Improve usability documentation |

---

**Report Date:** December 26, 2025
**Status:** ✅ Review Complete - Ready for action items

