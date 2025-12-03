# DELIVERABLES: MCP Server Pattern Routing Fix

**Workorder:** WO-MCP-SERVER-PATTERN-ROUTING-FIX-001
**Status:** 🚧 Not Started
**Created:** 2025-12-03

---

## Executive Summary

Fix request format normalization in the unified MCP gateway to properly route tool calls to MCP Server pattern servers (personas-mcp, coderef-mcp).

**Problem:** Gateway receives `{"method": "tool", "params": {}}` but MCP Server pattern expects `{"name": "tool", "arguments": {}}`

**Solution:** Add request normalization layer before routing

---

## Phase 1: Request Normalization

| Task | Description | Status |
|------|-------------|--------|
| NORM-001 | Add `normalize_mcp_request()` function | [ ] |
| NORM-002 | Update `/mcp` endpoint to normalize requests | [ ] |

**Files:** `docs-mcp/http_server.py`

---

## Phase 2: Routing Update

| Task | Description | Status |
|------|-------------|--------|
| ROUTE-001 | Update `_route_tool_call()` for normalized format | [ ] |

**Files:** `docs-mcp/http_server.py`

---

## Phase 3: Testing & Verification

| Task | Description | Status |
|------|-------------|--------|
| TEST-001 | Update `test_mcp_list_personas` test | [ ] |
| TEST-002 | Run full test suite - all 14 pass | [ ] |

**Files:** `railway/test/test_railway_mcp.py`

---

## Metrics

| Metric | Value |
|--------|-------|
| LOC Added | TBD |
| LOC Deleted | TBD |
| Commits | TBD |
| Time Elapsed | TBD |

---

## Success Criteria

- [ ] All 54 tools callable via `/mcp` endpoint
- [ ] Test suite: 14/14 tests pass
- [ ] Backward compatibility maintained
- [ ] `list_personas` returns valid response

---

## Notes

_Implementation notes will be added here during development._
