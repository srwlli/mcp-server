# Workorder Summary: context-docs-integration

**Workorder ID:** WO-CONTEXT-DOCS-INTEGRATION-001
**Project:** coderef-docs
**Feature:** context-docs-integration (Integrate coderef-context for intelligent docs)
**Created:** 2025-12-27
**Status:** ✅ Planning Complete → Ready for Implementation
**Priority:** P1 (Phase 0 Stabilization)
**Source:** PHASE-3-ROADMAP-SYNTHESIS.md (Critical #4)

---

## 🎯 Executive Summary

**Problem:** coderef-docs currently returns placeholder templates. Users must manually write API.md, SCHEMA.md, and COMPONENTS.md with real implementation details.

**Solution:** Integrate coderef-context MCP server into coderef-docs to extract code intelligence and auto-populate documentation with actual API endpoints, database schemas, and component definitions.

**Impact:** 90% reduction in manual documentation time
- Current: 2-3 hours to document a project manually
- Future: 30 minutes with auto-generated documentation
- ROI: 6-8 hours implementation → 10-20 hours saved per project

---

## 📊 Planning Artifacts

All planning artifacts are located in: **coderef-docs/coderef/workorder/context-docs-integration/**

### Files Created

1. **context.json** (82 lines)
   - Feature requirements and context
   - Success criteria
   - Constraints and out-of-scope items

2. **plan.json** (542 lines)
   - Complete 10-section implementation plan
   - 3 phases with 9 total tasks
   - Detailed task breakdowns with effort estimates
   - Risk assessment (LOW risk overall)

3. **DELIVERABLES.md** (201 lines)
   - Progress tracking template
   - Checklist for all 9 tasks
   - Success criteria with validation steps
   - Metrics placeholders (to be filled during implementation)

4. **AGENT_GUIDE.md** (340 lines)
   - Detailed implementation guide for agentic coder
   - Step-by-step instructions for each phase
   - Code examples and patterns
   - Common issues and solutions
   - Testing strategies

---

## 🚀 Implementation Overview

### 3 Phases (6-8 Hours Total)

#### Phase 1: Setup & Integration Point (1 hour)
- SETUP-001: Import coderef-context client library
- SETUP-002: Add health check at startup
- SETUP-003: Create extract_apis(), extract_schemas(), extract_components() stubs

#### Phase 2: Integration with generate_individual_doc (3-4 hours)
- INTEGRATE-001: Implement API endpoint extraction
- INTEGRATE-002: Implement database schema extraction
- INTEGRATE-003: Implement component definition extraction
- INTEGRATE-004: Add error handling + result caching

#### Phase 3: Testing & Validation (2-3 hours)
- TEST-001: Unit tests for extract_* functions
- TEST-002: Integration tests with real coderef-context
- TEST-003: Regression tests (verify backward compatibility)

### Task Breakdown

| Phase | Task | Duration | Complexity |
|-------|------|----------|-----------|
| 1 | SETUP-001 | 15 min | Low |
| 1 | SETUP-002 | 15 min | Low |
| 1 | SETUP-003 | 30 min | Low |
| 2 | INTEGRATE-001 | 1h | Medium |
| 2 | INTEGRATE-002 | 1h | Medium |
| 2 | INTEGRATE-003 | 1h | Medium |
| 2 | INTEGRATE-004 | 30 min | Medium |
| 3 | TEST-001 | 1h | Medium |
| 3 | TEST-002 | 45 min | Medium |
| 3 | TEST-003 | 30 min | Low |
| **TOTAL** | **9 tasks** | **6-8h** | **Moderate** |

---

## 🎓 What Will Be Built

### Input/Output Example

**Before (Current):**
```
User: generate_individual_doc("API", "/project")
Result: Empty API.md with just headers and placeholders
User Action: Manually type API endpoints by hand (30 min+ work)
```

**After (With Integration):**
```
User: generate_individual_doc("API", "/project")
  → coderef-docs calls: coderef_context.coderef_query("api", "/project")
  → coderef-context returns: Real API endpoints from code analysis
  → coderef-docs transforms: Into markdown table format
  → User receives: API.md with 100+ endpoints auto-populated (10 seconds, done!)
```

### Core Functions to Implement

```python
# src/integration/context_extractor.py

async def extract_apis(project_path: str) -> List[Dict]:
    """Extract API endpoints from coderef-context and format for API.md"""
    # Call coderef-context.coderef_query("api", project_path)
    # Transform results to markdown table format
    # Return structured data
    pass

async def extract_schemas(project_path: str) -> List[Dict]:
    """Extract database schemas from coderef-context and format for SCHEMA.md"""
    # Call coderef-context.coderef_scan() for models/schema files
    # Extract entity definitions and relationships
    # Return structured data
    pass

async def extract_components(project_path: str) -> List[Dict]:
    """Extract component definitions from coderef-context and format for COMPONENTS.md"""
    # Call coderef-context.coderef_scan() for component files
    # Extract component hierarchy
    # Return structured data
    pass
```

### Integration Point (in server.py)

```python
# In generate_individual_doc() function:

if template_name == "api":
    extracted_apis = await extract_apis(project_path)
    if extracted_apis:
        # Populate with real data
        return template.render(endpoints=extracted_apis)
    else:
        # Fall back to placeholder
        return template.render(endpoints=[])
```

---

## ✅ Success Criteria

### Functional
- ✅ API.md contains real endpoint signatures from coderef-context
- ✅ SCHEMA.md contains real entity definitions from coderef-context
- ✅ COMPONENTS.md contains real component definitions from coderef-context
- ✅ Graceful fallback to placeholders if coderef-context unavailable

### Quality
- ✅ All unit tests passing (≥90% coverage)
- ✅ All integration tests passing
- ✅ All existing tests still passing (no regressions)
- ✅ Type checking passes (mypy)
- ✅ Code style passes (black, ruff)

### Performance
- ✅ Doc generation <10 seconds per document
- ✅ Results cached/memoized to avoid redundant calls
- ✅ Graceful timeout handling (120s max)

### Integration
- ✅ Health check verifies coderef-context availability at startup
- ✅ Proper error logging when coderef-context fails
- ✅ No new external dependencies added

---

## 📁 File Structure

### New Files to Create
```
coderef-docs/
└── src/integration/
    └── context_extractor.py  (extract_apis, extract_schemas, extract_components)

tests/
├── test_integration_context_docs.py  (unit tests, mocked)
└── integration/
    └── test_context_docs_integration.py  (integration tests, real calls)
```

### Files to Modify
```
coderef-docs/
├── server.py  (add health check, import extractors, call in generate_individual_doc)
└── CLAUDE.md  (document new integration points)
```

---

## 🔗 Dependencies & Integration Points

### coderef-context Integration
- **Tools Used:** coderef_query (for APIs), coderef_scan (for schemas/components)
- **Health Check:** Required - verify coderef-context available at startup
- **Fallback:** Graceful degradation - return placeholders if coderef-context unavailable
- **Caching:** Memoize results to avoid redundant calls

### Backward Compatibility
- ✅ No breaking changes
- ✅ All existing doc generation still works
- ✅ Optional enhancement - doesn't require coderef-context
- ✅ Tests unchanged, no modifications to existing API

---

## 🚨 Risk Assessment

**Overall Risk Level: LOW**

### Identified Risks & Mitigations

| Risk | Severity | Mitigation |
|------|----------|-----------|
| coderef-context unavailable | Medium | Health check + graceful fallback to placeholders |
| coderef-context returns verbose data | Low | Parse carefully, extract only needed fields |
| Doc generation timeout | Low | 120s timeout wrapper, fall back on timeout |
| Backward compatibility broken | Low | Always have placeholder fallback, never require context |
| Large token usage | Low | Cache results, memoize calls, filter verbosity |

---

## 📈 Resource Allocation

**Total Effort:** 6-8 hours

**By Task:**
- Phase 1 (Setup): 1 hour
- Phase 2 (Integration): 3-4 hours
- Phase 3 (Testing): 2-3 hours

**Skills Required:**
- Python programming (intermediate)
- Async/await patterns
- MCP client library usage
- Testing with pytest
- Git/version control

---

## 🎬 Next Steps for Agent

1. **Read** this summary and AGENT_GUIDE.md
2. **Review** plan.json for detailed specs (sections 1-4 for context)
3. **Start** Phase 1: SETUP-001 (import coderef-context client)
4. **Follow** step-by-step guidance in AGENT_GUIDE.md
5. **Test** each phase before moving to next
6. **Mark** tasks complete as you finish them
7. **Update** DELIVERABLES.md with metrics when complete

---

## 📞 For Questions

- **"What are coderef-context tools?"** → Read coderef-context/CLAUDE.md
- **"How do I call MCP tools?"** → Check coderef-context/server.py
- **"What's the exact API?"** → Check AGENT_GUIDE.md "How to Call coderef-context"
- **"How do I test?"** → See AGENT_GUIDE.md "Phase 3: Testing & Validation"
- **"What if X fails?"** → See AGENT_GUIDE.md "Common Issues & Solutions"

---

## 📌 Key Dates & Timeline

| Date | Event |
|------|-------|
| 2025-12-27 | Planning complete, workorder created, committed |
| TBD | Agent implementation begins (Phase 1) |
| TBD | Phase 1 complete, Phase 2 starts |
| TBD | Phase 2 complete, Phase 3 starts |
| TBD | Phase 3 complete, all tests passing |
| TBD | Integration tests pass, ready for merge |
| TBD | Commit + documentation updated |

---

## ✨ Expected Outcome

After 6-8 hours of implementation:

✅ **coderef-docs is now intelligent**
- API.md auto-generated from actual code
- SCHEMA.md auto-generated from actual code
- COMPONENTS.md auto-generated from actual code
- Documentation always in sync with code
- Zero manual doc work (vs 2-3 hours before)

✅ **System is more resilient**
- Graceful degradation if coderef-context unavailable
- Health check at startup
- Proper error logging

✅ **Code quality maintained**
- All tests passing (100%)
- Type checking clean (mypy)
- Code style clean (black, ruff)
- >90% coverage on new code

✅ **Ready for production**
- No breaking changes
- Backward compatible
- Well-tested
- Documented

---

## 🎉 Success Definition

This workorder is successful when:

1. ✅ All 9 tasks marked as "complete" in plan.json
2. ✅ All tests passing (unit + integration + regression)
3. ✅ API.md, SCHEMA.md, COMPONENTS.md contain real data (not placeholders)
4. ✅ Graceful degradation tested (coderef-context unavailable scenario)
5. ✅ DELIVERABLES.md updated with actual metrics (LOC, commits, time)
6. ✅ Code committed to main branch
7. ✅ Feature live in coderef-docs

---

**Planning Status:** ✅ COMPLETE
**Ready for Implementation:** YES
**Assigned To:** Agentic Coder (coderef-docs project)
**Expected Completion:** Within 8 hours of starting Phase 1

Good luck! This is a high-value feature with low risk. 🚀
