# Breaking Change Detection - Workflow Integration Workorder

**Workorder ID:** WO-BREAKING-CHANGE-INTEGRATION-001  
**Feature:** CR-001 (Breaking Change Detector)  
**Status:** Planning Complete - Ready for Implementation  
**Created:** 2025-12-25

---

## What's in This Workorder

This folder contains the complete integration plan for incorporating the Breaking Change Detector (CR-001) into the coderef-workflow orchestration process.

### Files

1. **stub.json** (Entry point)
   - Structured workorder definition
   - Task breakdown with IDs
   - Integration points summary
   - Dependencies and success criteria

2. **INTEGRATION-GUIDE.md** (High-level overview)
   - Current state assessment
   - 5-stage integration plan
   - Implementation tasks prioritized
   - Timeline and success metrics

3. **TECHNICAL-IMPLEMENTATION.md** (Developer reference)
   - Code examples for each integration point
   - Template updates (plan.json, communication.json)
   - Workflow hooks implementation
   - Test selection strategy
   - CI/CD pipeline setup
   - Complete code samples

4. **README.md** (This file)
   - Workorder overview
   - Quick navigation

---

## Quick Start

### For Project Managers
1. Read: **INTEGRATION-GUIDE.md** (20 min overview)
2. Review: `stub.json` - task breakdown section
3. Use timeline: ~16 hours total effort
4. Prioritize: High priority tasks (phase 2)

### For Developers
1. Read: **INTEGRATION-GUIDE.md** - overview
2. Reference: **TECHNICAL-IMPLEMENTATION.md** - code examples
3. Copy code samples into your implementation
4. Follow task order from stub.json

### For Product Owners
1. Read: **INTEGRATION-GUIDE.md** - summary section
2. Review success criteria in stub.json
3. Timeline: 2-3 weeks for full integration

---

## Integration Overview

### 5 Integration Stages

```
Planning (Phase 0)
    ↓
Agent Handoff Context
    ↓
Implementation Gate (Phase 3)
    ↓
Test Strategy
    ↓
Documentation (Phase 5)
```

### Key Files to Modify

- `packages/generators/src/templates/plan.json` - Add tasks
- `packages/generators/src/templates/communication.json` - Add gates
- `packages/workflow/src/hooks/` - Create 3 new hooks
- `packages/workflow/src/context/handoff-generator.ts` - Update
- `.github/workflows/breaking-change-check.yml` - Create CI/CD

---

## Implementation Tasks

### High Priority (Do First) - 8 hours

- [ ] **WI-002:** Update plan.json template (2h)
- [ ] **WI-003:** Update communication.json template (2h)
- [ ] **WI-004:** Create workflow hooks (4h)

### Medium Priority (Do Next) - 8 hours

- [ ] **WI-005:** Add breaking change context to agent handoff (2h)
- [ ] **WI-006:** Implement test selection strategy (3h)
- [ ] **WI-007:** Generate migration guides (3h)

### Lower Priority (Future) - 2 hours

- [ ] **WI-008:** Create CI/CD pipeline integration (2h)

---

## Success Criteria

✅ All complete when:
- Planning phase includes breaking change risk assessment
- Agent handoff contexts include breaking change guidance
- Verification phase validates no new breaking changes introduced
- Documentation includes migration guides for breaking changes
- CI/CD pipeline gates on breaking changes
- Agents have access to migration suggestions via MCP tool
- Test suite is sized based on affected modules

---

## Current Status of CR-001

✅ **COMPLETED:**
- Signature comparison (parameter, return type, visibility changes)
- Call site detection with confidence scoring
- Multi-factor confidence algorithm (0.3-0.99 range)
- Migration pattern suggestions
- ImpactSimulator integration
- CLI command: `coderef breaking`
- MCP tool: `mcp__coderef_breaking__detect`
- Comprehensive test suite (29 tests)

❌ **NEEDS INTEGRATION:**
- Workflow orchestration hooks
- Agent handoff context
- Automatic test selection
- Migration guide generation
- CI/CD pipeline gates

---

## Next Steps

1. **Review & Approve** this integration plan
2. **Assign Developers** to high-priority tasks
3. **Create Individual Workorders** for WI-002 through WI-008
4. **Execute Phase by Phase** starting with template updates
5. **Test Integration** with real feature implementations

---

## Documentation

- **Overview:** INTEGRATION-GUIDE.md
- **Technical Details:** TECHNICAL-IMPLEMENTATION.md
- **Task List:** stub.json → task_breakdown
- **Dependencies:** stub.json → dependencies

---

## Questions?

Refer to:
- Technical details: `TECHNICAL-IMPLEMENTATION.md`
- Integration points: `INTEGRATION-GUIDE.md` - "Concrete Implementation Tasks"
- Task breakdown: `stub.json` - "task_breakdown" section

---

**Estimated Completion:** 2-3 weeks for full integration  
**Start Date:** Ready to begin  
**Owner:** [Assign after review]
