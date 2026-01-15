# Foundation Docs Generation Consolidation - Scope Changes

**Date:** 2026-01-13
**Source:** User clarification on consolidation strategy
**Session:** WO-DOCS-CONSOLIDATION-001

---

## Strategic Decision

**Single Source of Truth:** All foundation documentation generation will be consolidated into **coderef-docs server** only.

**Rationale:**
- Eliminates confusion about which tool to use
- Reduces maintenance burden (one implementation instead of three)
- Clear ownership and responsibility
- Simplifies user experience

---

## Scope Changes Applied

### 1. WO-CONTEXT-INTEGRATION-001 (coderef-context)

**REMOVED:**
- ❌ P2-2: "Add generate_foundation_docs tool (auto-doc generation capability)"
  - Rationale in original plan: "coderef-context has all data needed but no doc generation capability"
  - **Why removed:** Violates single source of truth principle - all doc generation belongs in coderef-docs

**Changes Made:**
- Updated context.json: Reduced scope from 7 to 6 enhancements
- Updated context.json description to note removal
- Updated deliverables list (removed generate_foundation_docs)
- Added communication_log entry notifying agent of scope change
- P2 tasks now renumbered: P2-1 (quickref), P2-2 (validate_coderef_outputs)

**Agent Action Required:**
- Update plan.json to remove P2-2 tasks (generate_foundation_docs implementation)
- Reduce task count from 27 to approximately 20 tasks
- Update DELIVERABLES.md to reflect 6 enhancements instead of 7

---

### 2. WO-GENERATION-ENHANCEMENT-001 (coderef-docs)

**EXPANDED:**
- ✅ P2-1: Now includes removing generate_foundation_docs from **coderef-workflow server**
  - Original scope: Consolidate 3 tools within coderef-docs only
  - **Expanded scope:** Also remove duplicate tool from coderef-workflow

**Changes Made:**
- Updated context.json P2-1 title: "Consolidate foundation doc tools **and remove from coderef-workflow**"
- Updated rationale: Documents that foundation docs scattered across coderef-docs AND coderef-workflow
- Updated implementation: Added Phase 2 (coderef-workflow removal)
- Updated success criteria: Added 4 new criteria for coderef-workflow cleanup
- Updated impact statement: "Eliminates duplication in coderef-workflow"
- Added communication_log entry notifying agent of scope expansion

**New Success Criteria Added:**
1. coderef-workflow: generate_foundation_docs tool removed from server.py
2. coderef-workflow: handle_generate_foundation_docs deleted from tool_handlers.py
3. coderef-workflow: generators/coderef_foundation_generator.py deleted
4. coderef-workflow: API.md, reference sheets updated (removal documented)

**Agent Action Required:**
- Update plan.json P2-1 to include coderef-workflow removal tasks
- Add tasks for deleting files in coderef-workflow server
- Add tasks for updating coderef-workflow documentation
- Create migration guide pointing users from coderef-workflow to coderef-docs

---

### 3. WO-VALIDATION-ENHANCEMENT-001 (papertrail)

**NO CHANGES:**
- Papertrail workorder unaffected by consolidation
- Continues with original 7 enhancements (2 P0, 2 P1, 3 P2)

---

## Files Modified by Orchestrator

| File | Change | Reason |
|------|--------|--------|
| C:\Users\willh\.mcp-servers\coderef-context\coderef\workorder\context-integration-001\context.json | Removed P2-2, updated description and deliverables | Scope reduction |
| C:\Users\willh\.mcp-servers\coderef-context\coderef\workorder\context-integration-001\communication.json | Added scope change notification | Agent notification |
| C:\Users\willh\.mcp-servers\coderef-docs\coderef\workorder\generation-enhancement-001\context.json | Expanded P2-1 with coderef-workflow removal | Scope expansion |
| C:\Users\willh\.mcp-servers\coderef-docs\coderef\workorder\generation-enhancement-001\communication.json | Added scope expansion notification | Agent notification |

---

## Implementation Impact

### coderef-context Agent
- **Reduced Complexity:** From 7 enhancements to 6
- **Reduced LOC:** From 2000-2500 to approximately 1500-2000 new lines
- **Reduced Files:** From 15-20 files to approximately 12-15 files
- **Phases Unchanged:** Still 4 phases (P0, P1, P2, Testing)

### coderef-docs Agent
- **Increased Complexity:** P2-1 now has cross-server cleanup responsibilities
- **New Files to Delete:** 3 files in coderef-workflow server
- **New Documentation Updates:** coderef-workflow API.md, reference sheets
- **Migration Responsibility:** Must create guide for users migrating from coderef-workflow tool

### Overall Project Impact
- **Better Separation of Concerns:**
  - coderef-context = Code analysis and data generation
  - coderef-docs = Documentation generation (sole owner)
  - coderef-workflow = Planning and execution tracking
- **Clearer Tool Boundaries:** No overlap between servers
- **User Clarity:** Only one place to generate foundation docs

---

## Next Steps

1. **coderef-context agent:** Revise plan.json to remove P2-2 tasks
2. **coderef-docs agent:** Create plan.json with expanded P2-1 scope
3. **Orchestrator:** Review revised plans before approving implementation
4. **coderef-docs agent:** Execute P2-1 Phase 2 (coderef-workflow cleanup) after internal consolidation complete

---

## Verification Checklist

After implementation, verify:

- [ ] coderef-context does NOT have generate_foundation_docs tool
- [ ] coderef-docs HAS generate_foundation_docs as primary tool
- [ ] coderef-workflow does NOT have generate_foundation_docs tool
- [ ] Migration guide exists pointing users to coderef-docs
- [ ] All documentation updated to reflect single source of truth
- [ ] Users can only generate foundation docs via coderef-docs server

---

**Orchestrator Note:** This consolidation aligns with the principle of "each server owns one concern." coderef-context provides data, coderef-docs generates documentation from that data. No server should duplicate capabilities.
