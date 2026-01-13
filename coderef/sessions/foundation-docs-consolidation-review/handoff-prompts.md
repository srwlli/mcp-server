# Handoff Prompts for WO-DOCS-CONSOLIDATION-001 Implementation

Generated: 2026-01-12
Source Session: WO-DOCS-CONSOLIDATION-001 (foundation-docs-consolidation-review)

---

## Handoff Prompt 1: coderef-context Agent

**Paste this into coderef-context MCP server chat:**

```
NEW WORKORDER: WO-CONTEXT-INTEGRATION-001

Location: C:\Users\willh\.mcp-servers\coderef-context\coderef\workorder\context-integration-001\

Review context.json for detailed requirements covering 7 enhancements:

**P0 - Critical (Blocking coderef-docs):**
1. Enhance SCHEMA.md with complete .coderef/ file format definitions (index.json, graph.json, context.json structures)
2. Create INTEGRATION.md with coderef-docs usage examples (how to call our tools, populate templates, handle errors)

**P1 - High Priority:**
3. Add incremental scan support via drift detection (10-100x faster for small changes)
4. Support Python code scanning (currently TypeScript only - can't scan ourselves)

**P2 - Medium Priority:**
5. Add quickref.md for tool reference (cheat sheet for 12 tools)
6. Add generate_foundation_docs tool (auto-doc generation capability)
7. Validate .coderef/ outputs against Papertrail schemas

**Your Task:**
1. READ context.json at workorder location
2. RUN /create-plan to generate implementation plan.json
3. UPDATE communication.json status to "plan_submitted"
4. WAIT for approval before implementing

**Priority:** P0 items are CRITICAL - coderef-docs is waiting on INTEGRATION.md examples to implement their tool orchestration.

**Dependencies:** None - you can start immediately.
```

---

## Handoff Prompt 2: coderef-docs Agent

**Paste this into coderef-docs MCP server chat:**

```
NEW WORKORDER: WO-GENERATION-ENHANCEMENT-001

Location: C:\Users\willh\.mcp-servers\coderef-docs\coderef\workorder\generation-enhancement-001\

Review context.json for detailed requirements covering 7 enhancements:

**P0 - Critical:**
1. Add coderef-context tool orchestration to generate_foundation_docs (call coderef_query, coderef_patterns, coderef_complexity, coderef_coverage, coderef_impact)
2. Integrate Papertrail validation into doc generation workflow (auto-validate before writing files)

**P1 - High Priority:**
3. Add drift detection before doc generation (warn users about stale .coderef/ data)
4. Upgrade user docs to use .coderef/ data (my-guide, user-guide, quickref with real examples)
5. Replace regex-based pattern detection with coderef_patterns semantic analysis (standards docs)

**P2 - Medium Priority:**
6. Consolidate 3 foundation doc tools → 1 unified tool (reduce user confusion)
7. Add coderef-context health check at initialization (fail fast if dependency missing)

**Your Task:**
1. READ context.json at workorder location
2. RUN /create-plan to generate implementation plan.json
3. UPDATE communication.json status to "plan_submitted"
4. WAIT for approval before implementing

**Priority:** This is the CORE workorder - transforms doc generation from hybrid to fully code-driven.

**Dependencies:**
- P0-1 depends on WO-CONTEXT-INTEGRATION-001 (need INTEGRATION.md examples)
- P0-2 depends on WO-VALIDATION-ENHANCEMENT-001 (need POWER framework schemas)

**Target Quality:** Foundation 70%→85%, User 40%→75%, Standards 55%→80%
```

---

## Handoff Prompt 3: Papertrail Agent

**Paste this into Papertrail MCP server chat:**

```
NEW WORKORDER: WO-VALIDATION-ENHANCEMENT-001

Location: C:\Users\willh\.mcp-servers\papertrail\coderef\workorder\validation-enhancement-001\

Review context.json for detailed requirements covering 7 enhancements:

**P0 - Critical (Blocking coderef-docs):**
1. Add POWER framework section validation to foundation doc schemas (enforce Purpose, Overview, Examples, References sections)
2. Add code example validation using coderef-context (verify examples match actual code)

**P1 - High Priority:**
3. Create schema-template synchronization tool (eliminate drift between templates and schemas)
4. Extend validation coverage to user docs and resource sheets (72%→100%)

**P2 - Medium Priority:**
5. Add pattern validation for standards docs (verify documented patterns match discovered patterns)
6. Add completeness percentage metric to validation results (coverage metric, not just quality score)
7. Create pre-commit hook template for automatic validation (CI/CD integration)

**Your Task:**
1. READ context.json at workorder location
2. RUN /create-plan to generate implementation plan.json
3. UPDATE communication.json status to "plan_submitted"
4. WAIT for approval before implementing

**Priority:** P0 items are CRITICAL - coderef-docs is waiting on POWER framework schemas to integrate validation.

**Dependencies:**
- P0-2 depends on WO-CONTEXT-INTEGRATION-001 (need coderef-context for code example validation)

**Target Coverage:** Validation coverage 72% (13/18) → 100% (18/18)
```

---

## Execution Order Recommendation

### Phase 1: Planning (All agents in parallel)
- All 3 agents create plan.json simultaneously
- No dependencies at planning stage

### Phase 2: P0 Implementation (Sequence matters)
1. **Start P0-1 in parallel:**
   - coderef-context: SCHEMA.md + INTEGRATION.md
   - Papertrail: POWER framework schemas
2. **Then P0-2 coderef-docs (after dependencies ready):**
   - Requires: INTEGRATION.md from coderef-context
   - Requires: POWER schemas from Papertrail
   - Implements: Tool orchestration + validation integration

### Phase 3: P1 Implementation (Parallel where possible)
- coderef-context: Incremental scan + Python scanning
- coderef-docs: Drift detection + user docs + semantic standards
- Papertrail: Schema sync + coverage expansion

### Phase 4: P2 Implementation (Parallel)
- All agents can implement P2 items independently

---

## Success Criteria (Overall)

**Quality Improvements:**
- Foundation docs: 70% → 85%+
- User docs: 40% → 75%+
- Standards docs: 55-60% → 80%+
- Validation coverage: 72% → 100%

**Integration Milestones:**
- ✅ coderef-docs calls coderef-context MCP tools (not just file reads)
- ✅ Papertrail validation integrated into doc generation
- ✅ POWER framework sections enforced
- ✅ Code examples validated against actual code
- ✅ Zero schema-template drift

**Deliverables (21 total):**
- 7 from coderef-context
- 7 from coderef-docs
- 7 from Papertrail

---

**Orchestrator:** Available to answer questions, verify deliverables, and coordinate dependencies.
