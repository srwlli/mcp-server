# CodeRef MCP + Context System Integration - Planning Documents

**Last Updated:** December 23, 2025

This directory now contains comprehensive analysis and planning documents for integrating the 6-phase agentic context system with the coderef-mcp server.

## Available Documents

### 1. **CODEREF_INTEGRATION_SUMMARY.txt** (9.2 KB)
**Quick Reference - START HERE**
- Executive summary of the integration problem
- Visual architecture diagrams
- 5-phase implementation timeline
- Key files to create/modify
- Expected outcomes

**Best for:** Quick overview, planning meetings, understanding the scope

### 2. **CODEREF_MCP_CONTEXT_INTEGRATION_ANALYSIS.md** (28 KB)
**Detailed Technical Analysis - COMPREHENSIVE GUIDE**
- Complete system architecture comparison
- Gap analysis (5 specific gaps identified)
- Proposed integration architecture with diagrams
- 5 new MCP tools/resources specification
- Complete implementation strategy (5 phases)
- Technical details with code examples
- Success criteria
- Risk mitigation strategies
- Configuration guidelines
- Appendix with usage examples

**Best for:** Implementation planning, architecture review, development

---

## Quick Navigation

### For Project Managers / Decision Makers
1. Read: CODEREF_INTEGRATION_SUMMARY.txt
2. Review: "IMPLEMENTATION PHASES" section (4-6 weeks timeline)
3. Check: "EXPECTED OUTCOMES" section

### For Architects / Senior Engineers
1. Read: CODEREF_MCP_CONTEXT_INTEGRATION_ANALYSIS.md (entire document)
2. Focus on: "Integration Gap & Analysis" section
3. Review: "Proposed Integration Architecture" section
4. Evaluate: "Technical Details" section

### For Developers
1. Start: CODEREF_INTEGRATION_SUMMARY.txt (Key Files to Create/Modify)
2. Deep dive: CODEREF_MCP_CONTEXT_INTEGRATION_ANALYSIS.md
3. Code examples: Appendix section
4. Implementation: Phase 1 (Bridge Layer)

---

## Key Findings Summary

### The Problem
- @coderef/core has complete 6-phase context generation system
- coderef-mcp doesn't use it - returns raw query results
- Agents can't get agentic context needed for planning
- Two systems duplicate analysis logic

### The Solution
- Create ContextBridge.py (subprocess IPC layer)
- Add 3 new MCP tools with context awareness
- Add 2 new MCP resources for cached contexts
- Wire @coderef/core's 6-phase system into MCP server

### The Impact
✅ Agents get complete agentic context
✅ Complexity metrics in all responses
✅ Risk assessments and edge case warnings
✅ Confidence scores for decision-making
✅ No more duplicate analysis logic
✅ Single source of truth for context data

---

## Implementation Phases

| Phase | Duration | Component | Status |
|-------|----------|-----------|--------|
| 1 | 1-2 wks | ContextBridge.py | Planning |
| 2 | 2-3 wks | 3 New MCP Tools | Planning |
| 3 | 1-2 wks | 2 New MCP Resources | Planning |
| 4 | 1-2 wks | Integration & Testing | Planning |
| 5 | 1 wk | Documentation | Planning |

**Total Timeline:** 4-6 weeks

---

## Files to Create/Modify

### New Files (600 lines total)
```
/coderef-mcp/coderef/bridge/context_bridge.py       (250 lines)
/coderef/packages/cli/src/commands/context-generation.ts (150 lines)
/coderef-mcp/tests/test_context_integration.py      (200 lines)
```

### Modified Files (1000+ lines total)
```
/coderef-mcp/server.py                      (add 3 tool schemas)
/coderef-mcp/tool_handlers.py               (add 3 handlers, ~600 lines)
/coderef-mcp/coderef/models.py              (add AgenticContext models)
/coderef-mcp/coderef/utils/resource_cache.py (enhance cache)
/coderef/packages/cli/src/cli.ts            (add context command)
```

---

## Next Steps

1. **Review Phase (This Week)**
   - [ ] Read CODEREF_INTEGRATION_SUMMARY.txt
   - [ ] Read CODEREF_MCP_CONTEXT_INTEGRATION_ANALYSIS.md
   - [ ] Discuss findings with team
   - [ ] Approve high-level architecture

2. **Planning Phase (Next Week)**
   - [ ] Finalize Phase 1 requirements
   - [ ] Assign team members
   - [ ] Create detailed task breakdown
   - [ ] Set milestone dates

3. **Implementation Phase (Weeks 3-6)**
   - [ ] Phase 1: Bridge Layer
   - [ ] Phase 2: MCP Tools
   - [ ] Phase 3: Resources & Caching
   - [ ] Phase 4: Integration Testing
   - [ ] Phase 5: Documentation

---

## Key Configuration

### Environment Variables to Add
```bash
CODEREF_CLI_PATH=/path/to/coderef-system/packages/cli
CONTEXT_CACHE_MAX_SIZE=10
CONTEXT_CACHE_TTL_SECONDS=3600
CONTEXT_SUBPROCESS_TIMEOUT=30
```

### New MCP Tools
```
mcp__coderef__generate_agentic_context   ← Generate 6-phase context
mcp__coderef__query_with_context         ← Enhanced query with context
mcp__coderef__analyze_with_context       ← Enhanced analysis with context
```

### New MCP Resources
```
coderef://context/agentic                ← Cached agentic contexts
coderef://stats/context                  ← Context generation stats
```

---

## Success Criteria

Phase 1:
- [ ] ContextBridge executes @coderef/core CLI
- [ ] Timeout handling works (30s limit)
- [ ] Results cached in memory
- [ ] Error cases handled

Phase 2:
- [ ] generate_agentic_context tool works end-to-end
- [ ] query_with_context returns context data
- [ ] analyze_with_context includes 6-phase data
- [ ] All tools follow MCP format

Phase 3:
- [ ] Resources accessible and cached
- [ ] Cache invalidation works
- [ ] Resource data fresh (<5 min old)

Phase 4:
- [ ] End-to-end tests pass
- [ ] Performance <5s (cached)
- [ ] Memory stays <100MB
- [ ] Concurrent contexts handled

Phase 5:
- [ ] Documentation complete
- [ ] Examples provided
- [ ] Integration guide published

---

## Related Documentation

- **README.md** - Current coderef-mcp overview
- **API.md** - Current API documentation
- **IMPLEMENTATION-GUIDE.md** - Phase 1-4 completion guide (existing)
- **TESTING-GUIDE.md** - Testing approach

---

## Contact & Questions

For questions about this integration analysis:
1. Review the corresponding section in the detailed analysis document
2. Check the "Risk Mitigation" section
3. Refer to "Technical Details" for implementation guidance

---

**Next Action:** Review CODEREF_INTEGRATION_SUMMARY.txt and schedule architecture review meeting.
