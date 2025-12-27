# DELIVERABLES: context-docs-integration

**Project:** coderef-docs
**Feature:** context-docs-integration (Integrate coderef-context for intelligent doc generation)
**Workorder:** WO-CONTEXT-DOCS-INTEGRATION-001
**Status:** 🚧 In Progress (Phase 1 Complete)
**Generated:** 2025-12-27
**Last Updated:** 2025-12-27

---

## Executive Summary

**Goal:** Integrate coderef-context MCP server into coderef-docs to enable intelligent code analysis for automatic documentation generation (API.md, SCHEMA.md, COMPONENTS.md).

**Description:** Currently coderef-docs returns placeholder templates. This feature enables coderef-docs to call coderef-context tools to extract real API endpoints, database schemas, and component definitions from code, then auto-populate documentation templates.

---

## Implementation Phases

### Phase 1: Setup & Integration Point

**Description:** Prepare infrastructure for coderef-context integration

**Estimated Duration:** 1 hour

**Deliverables:**
- coderef-context client library imported in server.py
- Health check at server startup to verify coderef-context availability
- extract_apis(), extract_schemas(), extract_components() function stubs with error handling

### Phase 2: Integration with generate_individual_doc

**Description:** Implement code intelligence extraction and template population

**Estimated Duration:** 3-4 hours

**Deliverables:**
- API endpoint extraction logic (via coderef_context.coderef_query)
- Database schema extraction logic (via coderef_context.coderef_scan)
- Component definition extraction logic (via coderef_context.coderef_scan)
- Error handling + graceful degradation
- Result caching/memoization for performance

### Phase 3: Testing & Validation

**Description:** Test integration, verify quality, ensure backward compatibility

**Estimated Duration:** 2-3 hours

**Deliverables:**
- Unit tests for extract_* functions (mocked coderef-context calls)
- Integration tests with real coderef-context calls
- Regression tests confirming existing docs functionality unchanged
- Type checking (mypy), style checks (black/ruff), coverage ≥90%

---

## Metrics

### Code Changes
- **Lines of Code Added:** TBD
- **Lines of Code Deleted:** TBD
- **Net LOC:** TBD
- **Files Modified:** TBD
- **Files Created:** TBD

### Commit Activity
- **Total Commits:** TBD
- **First Commit:** TBD
- **Last Commit:** TBD
- **Contributors:** TBD

### Time Investment
- **Days Elapsed:** TBD
- **Hours Spent (Wall Clock):** TBD

---

## Task Completion Checklist

### Phase 1: Setup ✅ COMPLETE
- [x] SETUP-001: Create subprocess utilities in cli_utils.py (run_coderef_command, get_cli_path, validate_cli_available)
- [x] SETUP-002: Add CLI health check to server.py (health_check function, CODEREF_CONTEXT_AVAILABLE flag)
- [x] SETUP-003: Create extract_apis(), extract_schemas(), extract_components() function stubs in extractors.py

### Phase 2: Integration
- [ ] INTEGRATE-001: Implement API endpoint extraction logic
- [ ] INTEGRATE-002: Implement database schema extraction logic
- [ ] INTEGRATE-003: Implement component definition extraction logic
- [ ] INTEGRATE-004: Add error handling + result caching

### Phase 3: Testing
- [ ] TEST-001: Unit tests for extract_* functions
- [ ] TEST-002: Integration tests with real coderef-context
- [ ] TEST-003: Regression tests (verify existing functionality unchanged)

### Quality
- [ ] Code: mypy passes, black formatted, ruff clean
- [ ] Coverage: ≥90% for new code
- [ ] Docs: Docstrings added to new functions

### Validation
- [ ] API.md correctly populated with real endpoints
- [ ] SCHEMA.md correctly populated with real entities
- [ ] COMPONENTS.md correctly populated with real components
- [ ] Graceful degradation tested (coderef-context unavailable)
- [ ] All existing tests still passing

---

## Files Created/Modified

**New Files:**
- `cli_utils.py` (6.2K) - Subprocess utilities for calling @coderef/core CLI (SETUP-001)
- `extractors.py` (8.2K) - Code intelligence extractors (stubs for Phase 1, implementation in Phase 2) (SETUP-003)
- ~~`tests/test_integration_context_docs.py`~~ - Unit tests (Phase 3)
- ~~`tests/integration/test_context_docs_integration.py`~~ - Integration tests (Phase 3)

**Modified Files:**
- `server.py` - Added health_check function, CODEREF_CONTEXT_AVAILABLE global flag, CLI imports (SETUP-002)
- `tool_handlers.py` - Added CODEREF_CONTEXT_AVAILABLE flag, set_coderef_context_available setter (SETUP-002)
- ~~`CLAUDE.md`~~ - Document new integration points (Phase 2)
- ~~`README.md`~~ - Update to mention coderef-context dependency (Phase 2)

---

## Success Criteria

✅ **Functional Requirements:**
- API.md contains real endpoint signatures from coderef-context
- SCHEMA.md contains real entity definitions from coderef-context
- COMPONENTS.md contains real component definitions from coderef-context
- Graceful fallback to placeholders if coderef-context unavailable

✅ **Quality Requirements:**
- All new code has ≥90% test coverage
- All existing tests still passing (no regressions)
- Type checking passes (mypy)
- Code style passes (black, ruff)

✅ **Performance Requirements:**
- Doc generation <10s per document
- coderef-context calls memoized to avoid redundant work
- Graceful timeout handling (120s max)

✅ **Integration Requirements:**
- Health check verifies coderef-context availability at startup
- Proper error logging when coderef-context fails
- No new external dependencies added

---

## Notes

*This deliverables report was automatically generated from plan.json.*
*Use `/update-deliverables` to populate metrics from git history after implementation.*

**Last Updated:** 2025-12-27
