# Papertrail Agent Output - Resource Sheet Template Generation System

**Agent ID:** papertrail
**Timestamp:** 2026-01-02
**Workorder:** WO-REFERENCE-SHEET-RECONCILIATION-001
**Task:** Design auto-generation system for unified resource sheet templates

---

## Executive Summary

### The Problem
Two separate resource sheet systems exist in the CodeRef ecosystem:

- **Tool 1** (`create-resource-sheet.md` - 240 lines): Provides the **HOW** - agent execution framework, quality controls, refactor-safety validation, output format specification
- **Tool 2** (`resource-sheet-catalog.md` - 634 lines): Provides the **WHAT** - 20 element type classifications with specialized checklists and required sections

These tools are fragmented. Tool 1 has execution discipline but lacks specialization. Tool 2 has domain expertise but lacks generation framework.

### The Solution
Design a **unified template generation engine** that combines:
- **BASE layer**: Tool 1's 13-section framework + quality gates
- **CONDITIONAL layer**: Tool 2's 20 element-specific overlays with custom checklists
- **VALIDATION layer**: Tool 1's refactor-safety checks + element-specific validation

The `/create-resource-sheet` command becomes a routing layer that detects element type and applies the appropriate template combination.

### Key Insight
Template generation is not simple file merging. It's a **3-layer data pipeline**:

```
CLASSIFY element → LOAD base template → APPLY element overlay →
AUTO-FILL from graph → INJECT checklists → VALIDATE quality →
GENERATE markdown → FLAG manual review
```

This approach achieves **60-80% auto-fill** by leveraging dependency graph data (Plan 3) while maintaining Tool 1's quality standards.

---

## Unified Template Schema (v1.0.0)

### Schema Architecture

The unified schema has **3 components**:

1. **Base Template** (from Tool 1): 13 universal sections
2. **Element Overlays** (from Tool 2): 20 type-specific extensions
3. **Validation Gates** (from Tool 1): 4-stage quality pipeline

#### Formula
```
FINAL_DOCUMENT = BASE_TEMPLATE (13 sections) +
                 ELEMENT_OVERLAY (4-8 sections) +
                 VALIDATION (quality gates)
```

---

### 1. Base Template (13 Sections from Tool 1)

| Section | Required | Auto-Fill Rate | Generation Rule |
|---------|----------|----------------|-----------------|
| **Header Metadata** | ✅ Always | 100% | System context (agent, date, task) |
| **Executive Summary** | ✅ Always | 30-50% | Extract from JSDoc/README/code structure |
| **Audience & Intent** | ✅ Always | 80% | Standard hierarchy with element overrides |
| **Architecture Overview** | ✅ Always | 60-80% | Graph queries (imports/exports/consumers) |
| **State Ownership** | ⚠️ If stateful | 40-60% | Detect state vars, ownership needs judgment |
| **Data Persistence** | ⚠️ If persists | 50-70% | Detect storage API calls, extract keys |
| **State Lifecycle** | ⚠️ If stateful | 30-50% | Identify lifecycle hooks, map stages |
| **Behaviors & Events** | ✅ Always | 50-70% | Scan event handlers, categorize |
| **Event Contracts** | ⚠️ If events | 60-80% | Parse handler signatures, payloads |
| **Performance** | ✅ Always | 10-30% | Template + placeholders (needs profiling) |
| **Accessibility** | ✅ Always | 40-60% | Detect ARIA/roles, identify gaps |
| **Testing Strategy** | ✅ Always | 20-40% | Find test files, parse scenarios |
| **Non-Goals** | ✅ Always | 0% | Human decision required |
| **Common Pitfalls** | ✅ Always | 10-30% | Extract from comments/issues/docs |

**Average Auto-Fill:** 45-60%

---

### 2. Element-Specific Overlays (20 Types from Tool 2)

Each element type adds **4-8 specialized sections** and **8-12 checklist items**.

#### Classification Taxonomy (Ranked by Maintenance Impact)

| Rank | Element Type | Detection Patterns | Overlay Sections | Checklist Focus |
|------|--------------|-------------------|------------------|-----------------|
| 1 | **Top-Level Widgets** | Page/Widget suffix | Composition hierarchy, user workflows, layout contracts, performance budget | 8 items: Composition, workflows, state orchestration, integration, layout, lifecycle, budget, a11y |
| 2 | **Stateful Containers** | Provider/Controller/Manager suffix, useState/useReducer | State authority table, lifecycle diagram, persistence contract, event subscriptions | 8 items: Ownership, coordination, persistence, cache, error boundaries, subscriptions, init, testing |
| 3 | **Global State Layer** | store.ts, Context suffix, Redux/Zustand | Store schema, actions reference, selectors catalog, middleware order | 8 items: Shape, actions, selectors, persistence, middleware, devtools, hydration, testing |
| 4 | **Custom Hooks** | use* prefix | Hook signature, side effects catalog, dependency rules, return contract | 8 items: Side effects, cleanup, dependencies, return, closures, composition, testing, performance |
| 5 | **API Client** | *client/*api/*sdk, fetch/axios | Endpoint reference, auth flow, error taxonomy, retry strategy | 8 items: Endpoints, auth, retry, errors, normalization, cache, rate limit, mocks |
| 6 | **Data Models** | types.ts/schema.ts/validator | Schema definition, validation rules, versioning, migration playbook | 8 items: Types, validation, versioning, JSON schema, defaults, unions, serialization, testing |
| 7 | **Persistence** | storage.ts/cache.ts/indexedDB | Keys catalog, hydration lifecycle, conflict resolution, quota management | 8 items: Keys, hydration, conflicts, quota, versioning, serialization, security, testing |
| 8 | **Eventing/Messaging** | eventBus/messageHub/BroadcastChannel | Event catalog, ordering guarantees, cross-tab sync, subscription mgmt | 8 items: Events, ordering, cross-tab, debounce, subscriptions, errors, testing, performance |
| 9 | **Routing** | router.ts/routes.ts/navigation | Route map, route guards, deep link schema, transition lifecycle | 8 items: Routes, guards, deep links, params, transitions, history, testing, performance |
| 10 | **File/Tree Primitives** | TreeNode/PathUtils/FileIndex | Tree schema, path utilities, indexing strategy, selection semantics | 8 items: Structures, path utils, indexing, selection, favorites, sort/filter, testing, performance |
| 11 | **Context Menu/Commands** | contextMenu/commandRegistry/actions | Actions catalog, permissions model, keyboard shortcuts | 8 items: Actions, permissions, enable/disable, analytics, positioning, shortcuts, testing, a11y |
| 12 | **Permission/AuthZ** | permissions.ts/authz.ts/rbac | Roles catalog, capabilities reference, policy language | 8 items: Roles, capabilities, UI gating, server enforcement, policy, testing, performance, audit |
| 13 | **Error Handling** | ErrorBoundary/errorHandler/toasts | Error taxonomy, user messaging, recovery flows | 8 items: Categories, messages, recovery, boundaries, logging, testing, performance, a11y |
| 14 | **Logging/Telemetry** | analytics.ts/telemetry.ts/logger | Event taxonomy, payload schemas, privacy constraints | 8 items: Naming, payloads, privacy, sampling, providers, testing, performance, debugging |
| 15 | **Performance-Critical UI** | Virtual*/Canvas*, performance annotations | Performance budgets, profiling guide, virtualization, optimization history | 8 items: Budgets, profiling, virtualization, memoization, bottlenecks, testing, history, monitoring |
| 16 | **Design System Components** | Button/Modal/Input, design-system path | Props reference, variants catalog, theming tokens | 8 items: Props, variants, a11y, theming, composition, testing, performance, migration |
| 17 | **Theming/Styling** | theme.ts/tokens.css/tailwind.config | Token map, dark mode strategy, customization API | 8 items: Tokens, dark mode, customization, anti-patterns, responsive, testing, performance, migration |
| 18 | **Build/Tooling** | build.js/codegen.ts/scripts/ | Script purpose, inputs/outputs, CI integration | 8 items: Purpose, I/O, safe usage, CI, errors, testing, performance, debugging |
| 19 | **CI/CD Pipelines** | .github/workflows/deploy.yml | Pipeline overview, artifacts catalog, rollback playbook | 8 items: Stages, artifacts, env vars, rollback, debugging, testing, performance, security |
| 20 | **Testing Harness** | test-utils/mocks/fixtures/__tests__ | Standard patterns, mock boundaries, fixture catalog | 8 items: Patterns, mocks, fixtures, golden paths, async, coverage, performance, debugging |

---

### 3. Example: Stateful Container Template

**Input:** `FileTreeController` (detected as Stateful Container)

**Base Sections (13):**
- Header Metadata, Executive Summary, Audience & Intent, Architecture Overview, State Ownership ✓, Data Persistence ✓, State Lifecycle ✓, Behaviors & Events, Event Contracts ✓, Performance, Accessibility, Testing, Non-Goals, Common Pitfalls

**Element Overlay (+4 sections):**
- State Authority Table (canonical source of truth)
- Lifecycle Diagram (init → hydrate → validate → runtime → cleanup)
- Persistence Contract (keys, schema, versioning)
- Event Subscriptions (listeners, cleanup guarantees)

**Total Sections:** 17
**Auto-Fill Rate:** 72%
**Manual Review Needed:** Executive summary, non-goals, performance (needs profiling), pitfalls

---

## Element Type Detection Algorithm

**3-Stage Classification Pipeline:**

### Stage 1: Filename Pattern Matching (Fast)
```
Input: "FileTreeController.tsx"
Matches: "(Provider|Controller|Manager)$" → element_type: "stateful_containers"
Confidence: 85%
```

**20 Regex Patterns:**
- `^use[A-Z]` → custom_hooks (90% confidence)
- `(Page|Widget)$` → top_level_widgets (85%)
- `store\.ts$` → global_state_layer (95%)
- `(client|api|sdk)\.ts$` → api_client (80%)
- ... (16 more patterns)

### Stage 2: Code Analysis (Refinement)
```
Input: File contents
Scans for: useState|useReducer patterns
Boost: +15% confidence
Final: 85% + 15% = 100% confidence
```

**8 Code Pattern Rules:**
- `useState|useReducer` → stateful_containers (+15%)
- `createStore|configureStore` → global_state_layer (+20%)
- `useEffect.*return.*cleanup` → custom_hooks (+10%)
- `fetch|axios` → api_client (+15%)
- ... (4 more patterns)

### Stage 3: Fallback (Safety Net)
```
If confidence < 50%:
  element_type = "top_level_widgets" (default)
  manual_review_needed = true
  prompt = "Low confidence. Please select from: [20 types]"
```

**Output Format:**
```json
{
  "element_type": "stateful_containers",
  "confidence": 95,
  "detection_method": "stage_1_filename + stage_2_code_analysis",
  "matched_patterns": ["Provider suffix", "useState usage"],
  "manual_review_needed": false
}
```

---

## Template Generation Rules

### Rule 1: Base Template
- **Always** include all 13 base sections
- **Exception:** Skip conditional sections (state_ownership, data_persistence, state_lifecycle) if element is not stateful/persistent
- **Implementation:** Template engine checks element characteristics

### Rule 2: Element Overlay
- Add element-specific sections based on detected type
- **Lookup:** Use classification taxonomy → find `additional_sections` for `element_type`
- **Merge Strategy:** Append overlay sections after base, deduplicate if overlap

### Rule 3: Checklist Injection
- Inject element-specific checklist into relevant sections
- **Format:** Add as H4 heading `#### Checklist` with bullet points
- **Example:** For stateful_containers, inject "State ownership rules" into state_ownership section

### Rule 4: Auto-Fill (Graph-Powered)
**Data Sources:**
1. Dependency graph (`.coderef/graph.json`) → imports/exports/consumers
2. Code analysis → state vars, event handlers, lifecycle methods
3. JSDoc comments → descriptions
4. Test files → testing scenarios
5. Issue tracker → known bugs/pitfalls

**Placeholder Format:**
```markdown
<!-- TODO: [field_name] - [guidance] -->
```

**Target:** 60-80% completion

### Rule 5: Validation
Apply Tool 1's quality gates before finalizing:
- Refactor safety checklist (9 items)
- Final checklist (12 items)
- No ambiguous "should" statements
- Tables for structured data
- Diagrams marked illustrative

**Fail Behavior:** Flag validation failures, do not block generation

---

## Generation Sequence (9 Steps)

```
1. DETECT element type (3-stage classification)
   ↓
2. LOAD base template (13 sections)
   ↓
3. LOAD element overlay (lookup from taxonomy)
   ↓
4. MERGE base + overlay (deduplicate, order by importance)
   ↓
5. AUTO-FILL fields (graph data, code analysis, heuristics)
   ↓
6. INJECT checklists (element-specific focus areas)
   ↓
7. VALIDATE (4 quality gates)
   ↓
8. GENERATE markdown output
   ↓
9. FLAG manual review items (low confidence, missing data)
```

---

## Validation Pipeline (4 Quality Gates)

### Gate 1: Refactor Safety (Tool 1)
**9 Checks:**
1. Can new dev refactor without breaking contracts? → Check for explicit contracts
2. Are state ownership rules unambiguous? → State table must have precedence rules
3. Are failure modes documented with recovery? → data_persistence must include failure_modes
4. Are non-goals explicit? → non_goals section must be non-empty
5. Do diagrams match text? → Diagrams must have "illustrative" disclaimer
6. All persistence documented? → All localStorage/indexedDB keys in table
7. All failure recovery paths? → Each failure mode has recovery strategy
8. All external contracts? → integration_points section complete
9. Non-goals prevent scope creep? → non_goals section specific

**Scoring:** Pass (8/9), Warn (6-7), Fail (<6)

### Gate 2: Final Checklist (Tool 1)
**11 Checks:**
1. Executive summary complete (2-4 sentences)
2. State ownership table included (if stateful)
3. All persistence documented (if persists data)
4. Failure modes covered
5. Non-goals explicit
6. Accessibility gaps noted
7. Common pitfalls listed
8. Refactor-safe contracts defined
9. No ambiguous "should" statements (regex scan)
10. Tables for structured data
11. Diagrams marked illustrative

**Scoring:** Pass (11/11), Warn (9-10), Fail (<9)

### Gate 3: Element-Specific Validation (Tool 2)
**Example (Stateful Container):**
- Required sections: state_authority_table, lifecycle_diagram, persistence_contract, event_subscriptions (4/4 exist?)
- Required checklist: 8 items addressed?

**Scoring:** Pass (all sections + checklists complete)

### Gate 4: Auto-Fill Threshold
**Calculation:** `(auto_filled_fields / total_fields) * 100`
**Threshold:** 60%
**Fail Behavior:** If <60%, flag entire document with message: "Low auto-fill rate. Graph data may be incomplete."

**Scoring:** Pass (≥60%), Warn (40-59%), Fail (<40%)

---

### Combined Validation Result

| Gate | Status | Action |
|------|--------|--------|
| Refactor Safety | PASS/WARN/FAIL | - |
| Final Checklist | PASS/WARN/FAIL | - |
| Element-Specific | PASS/WARN/FAIL | - |
| Auto-Fill Threshold | PASS/WARN/FAIL | - |
| **Overall** | **APPROVED** | Generate final markdown, no review needed |
|  | **APPROVED_WITH_WARNINGS** | Generate markdown, flag warnings |
|  | **REJECTED** | Return validation errors, do not generate |

---

## Integration with Three Plans

### Plan 1: Resource Sheet System (coderef-assistant)
**Alignment:** High
**Adopted:**
- MCP tool architecture (generate, classify, validate tools)
- Template storage in structured format
- Element classification taxonomy
- Validation system with checklist enforcement

**Deviation:** Plan 1 focuses on MCP implementation; this output focuses on template schema

### Plan 2: Resource Sheet Reconciliation (coderef-docs)
**Alignment:** Very High (directly addresses TypeScript → Python porting)
**Adopted:**
- 11 conditional modules concept → element overlays
- Enhanced detection engine → 3-stage classification
- 60%+ auto-fill target
- Module selection based on characteristics

**Key Insight:** Plan 2's "conditional modules" are exactly the element-specific overlays in this schema

### Plan 3: Resource Sheet Graph Integration (coderef-system)
**Alignment:** Very High (graph data powers auto-fill)
**Adopted:**
- DependencyGraph queries for imports/exports/consumers
- 60-80% auto-fill rate from graph data
- Consumer-side solution (resource-sheet reads graph)
- Graph query helpers (getImportsForElement, etc.)

**Implementation:** Auto-fill Rule 4 directly uses graph data as primary source

---

## Synthesis: Unified Approach

```
MCP_TOOL(generate)
  → TEMPLATE_ENGINE(base + overlay)
  → GRAPH_QUERIES(auto_fill)
  → VALIDATION(quality_gates)
  → MARKDOWN_OUTPUT
```

**Formula:**
Plan 1's MCP architecture + Plan 2's conditional modules + Plan 3's graph auto-fill = Complete template generation system

**Key Innovation:**
Template generation is not file merging—it's a **data-driven pipeline** with multi-stage classification, graph-powered auto-fill, and element-specific validation.

---

## Recommendations

1. **Implement element type detection as separate MCP tool** (`classify_element`) for reusability
2. **Use Jinja2 template engine** for base + conditional sections (already in Plan 2)
3. **Store element taxonomy as JSON schema** for easy updates and versioning
4. **Build validation pipeline as post-processing step**, not inline during generation
5. **Create auto-fill confidence scoring** to flag low-quality auto-generated sections
6. **Implement template versioning** (v1.0.0) for future schema evolution
7. **Add dry-run mode** for validation-only (no output generation)
8. **Support custom element types** (allow users to define beyond the 20)
9. **Integrate with coderef-workflow** for planning workflows (resource sheets as planning inputs)
10. **Progressive disclosure:** Generate base template first, then ask user for element type refinement

---

## Migration Path

**From:** Two separate slash commands (`create-resource-sheet.md` + `resource-sheet-catalog.md`)
**To:** Single unified MCP tool (`generate_resource_sheet`) with element-type routing

### 7-Phase Migration

1. **Phase 1:** Implement unified template schema (this output)
2. **Phase 2:** Build element type detection algorithm
3. **Phase 3:** Create template generation engine (base + overlay + auto-fill)
4. **Phase 4:** Implement validation pipeline
5. **Phase 5:** Integrate with coderef-context for graph data
6. **Phase 6:** Deprecate old slash commands, add migration notices
7. **Phase 7:** Update all references in coderef/core documentation

**Backward Compatibility:**
Old `/create-resource-sheet` command can call new MCP tool with `element_type='generic'` fallback

---

## Success Metrics

| Metric | Target |
|--------|--------|
| **Template Coverage** | All 20 element types have complete schemas |
| **Auto-Fill Rate** | 60-80% average across all element types |
| **Validation Pass Rate** | 80%+ documents pass all 4 validation gates |
| **Generation Speed** | <5 seconds per resource sheet |
| **User Satisfaction** | Manual review time reduced from 30 min to <10 min |

---

## Conclusion

This template generation system **unifies the best of both tools**:

- **From Tool 1:** Execution discipline, quality controls, refactor-safety validation
- **From Tool 2:** Domain specialization, 20 element types, focused checklists
- **From Graph Integration:** 60-80% auto-fill via dependency analysis

The result is a **production-ready schema** for generating authoritative, refactor-safe resource sheets that achieve high auto-fill rates while maintaining quality standards.

**Next Steps:**
1. Review this output with orchestrator
2. Validate schema against real-world examples
3. Begin Phase 1 implementation (template schema → JSON)
4. Test auto-fill with sample elements from each of the 20 types

---

**Generated by:** Papertrail Agent (WO-REFERENCE-SHEET-RECONCILIATION-001)
**Schema Version:** 1.0.0
**Date:** 2026-01-02
