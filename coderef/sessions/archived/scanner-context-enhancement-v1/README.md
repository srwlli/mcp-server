# Scanner & Context Enhancement Session

**Workorder ID:** WO-SCANNER-CONTEXT-ENHANCEMENT-001
**Created:** 2026-01-14
**Status:** Ready to Execute
**Duration:** 8-10 weeks (3 phases)

---

## Overview

This session implements comprehensive enhancements to the scanner and context systems, then integrates those improvements into workflow and docs MCP servers.

**Key Goals:**
- Enhance coderef_context tool (40% → 95% context quality)
- Improve scanner accuracy (85% → 95%) and performance (3-5x faster)
- Integrate enhancements into workflow planning and docs generation
- Validate all improvements with comprehensive testing

---

## Session Structure

### Phase 1: Core Enhancements (Week 1-2)
**Lead Agents:** coderef-context, coderef-dashboard

**Deliverables:**
- Enhanced `coderef_context` tool exposing 100% of `.coderef/` resources
- 4 scanner quick wins: pattern ordering, presets, error reporting, Python patterns
- Populated reports: patterns.json, validation.json, complexity.json

**Success Metrics:**
- Context tool calls: 6 → 1
- Context quality: 40% → 95%
- Scanner performance: +15%
- Python coverage: +30%

### Phase 2: Integration (Week 3-4)
**Lead Agents:** coderef-workflow, coderef-docs

**Deliverables:**
- Workflow planning using enhanced context (single MCP call vs 5 file reads)
- Docs generation using enhanced scanner (95% accuracy)
- Integration test suite with 95%+ pass rate

**Success Metrics:**
- Planning speed: 6x faster
- Docs accuracy: 85% → 95%
- Integration tests: 95%+ pass

### Phase 3: Advanced Improvements (Week 5-10)
**Lead Agents:** coderef-dashboard, coderef-testing

**Deliverables:**
- Hybrid AST + Regex scanner (95% accuracy)
- Parallel file processing (3-5x faster)
- LRU caching (50MB memory cap)
- Reintegration validation

**Success Metrics:**
- Scanner accuracy: 85% → 95%
- Scan speed (500 files): 1185ms → 300-400ms
- Memory usage: Unbounded → 50MB

---

## Files

```
C:\Users\willh\.mcp-servers\coderef\sessions\scanner-context-enhancement\
├── README.md (this file)
├── communication.json (agent roster with 3-phase tracking)
├── instructions.json (orchestrator + agent instructions)
└── [outputs created during execution]
```

---

## Source Documents

- **Session Plan:** `C:\Users\willh\Desktop\assistant\scanner-complete-context.md`
- **Context Analysis:** `C:/Users/willh/.mcp-servers/coderef-context/CONTEXT-LEVERAGE-ANALYSIS.md`
- **Scanner Roadmap:** `C:\Users\willh\Desktop\coderef-dashboard\packages\coderef-core\coderef\resources-sheets\Scanner-Effectiveness-Improvements-RESOURCE-SHEET.md`

---

## Agent Participation

**All Phases:**
- coderef-assistant (coordination)
- coderef-personas (expertise)
- coderef-system (orchestration)
- papertrail (validation)

**Phase 1:**
- coderef-context (lead) - Enhance MCP tools
- coderef-dashboard (lead) - Scanner quick wins

**Phase 2:**
- coderef-workflow (lead) - Planning integration
- coderef-docs (lead) - Docs integration
- coderef-testing (lead) - Integration tests

**Phase 3:**
- coderef-dashboard (lead) - Scanner accuracy + performance
- coderef-testing (lead) - Benchmarks + validation
- coderef-workflow - Reintegration testing
- coderef-docs - Reintegration testing

---

## Execution Instructions

### For Orchestrator (coderef MCP)

1. **Phase 1:** Monitor context + dashboard agents, validate 95% context quality
2. **Phase 2:** Coordinate workflow + docs integration, validate 95%+ test pass rate
3. **Phase 3:** Monitor accuracy + performance, synthesize final results

### For Agents

1. READ `communication.json` to find your agent_id entry
2. READ `instructions.json` for your specific tasks
3. READ `scanner-complete-context.md` for detailed specifications
4. EXECUTE your phase tasks
5. CREATE output at designated path
6. UPDATE status in communication.json

---

## Success Criteria

**Phase 1 Gate:** Must achieve 95% context quality before Phase 2
**Phase 2 Gate:** Must achieve 95%+ integration test pass rate before Phase 3
**Phase 3 Gate:** Must achieve 95% scanner accuracy and 3-5x speedup

**Overall Success:** All 3 phases complete with no regressions between phases

---

## Key Integration Points

### coderef-context → coderef-workflow
- Workflow replaces 5 file reads with 1 `coderef_context` call
- Gets diagrams, patterns, complexity automatically
- 6x faster planning

### coderef-core scanner → coderef-docs
- Docs use enhanced scanner (95% vs 85% accuracy)
- Detects interfaces, decorators, Python patterns
- 3-5x faster with parallel processing

### coderef-context → coderef-docs
- Docs call `coderef_context` for architecture overview
- Pre-digested context in ARCHITECTURE.md

---

## Timeline

- **Week 1-2:** Phase 1 (Core enhancements)
- **Week 3-4:** Phase 2 (Integration)
- **Week 5-7:** Phase 3A (Scanner accuracy)
- **Week 8-10:** Phase 3B (Scanner performance + reintegration)

**Total:** 10 weeks

---

**Status:** ✅ Session files created and ready for execution
**Next Step:** Begin Phase 1 execution with coderef-context and coderef-dashboard agents
