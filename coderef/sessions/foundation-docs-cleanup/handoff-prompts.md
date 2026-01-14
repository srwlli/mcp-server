# Handoff Prompts - Foundation Docs Cleanup

**Session:** WO-FOUNDATION-DOCS-CLEANUP-001
**Created:** 2026-01-13
**Purpose:** Remove generate_foundation_docs from coderef-context and coderef-workflow

---

## Handoff Prompt 1: coderef-context Agent

**Paste this into coderef-context MCP server chat:**

```
CLEANUP SESSION: WO-FOUNDATION-DOCS-CLEANUP-001

Location: C:\Users\willh\.mcp-servers\coderef\sessions\foundation-docs-cleanup\

CRITICAL: You implemented generate_foundation_docs tool on Jan 13 01:03 as part of WO-CONTEXT-INTEGRATION-001 P2-2. This was BEFORE the scope change. You must now ROLL BACK this implementation.

**Your Task:**

DELETE all generate_foundation_docs code from your server:

1. **Delete from server.py:**
   - Line 408: Tool definition
   - Lines 486-487: Route mapping (elif name == "generate_foundation_docs")
   - Line 57: Import statement (handle_generate_foundation_docs)

2. **Delete from src/handlers_refactored.py:**
   - Line 462+: async def handle_generate_foundation_docs() - ENTIRE FUNCTION

3. **Delete file:**
   - src/foundation_doc_generator.py - ENTIRE FILE (11KB)

4. **Update documentation:**
   - coderef/foundation-docs/API.md - Remove generate_foundation_docs section
   - coderef/foundation-docs/COMPONENTS.md - Remove handle_generate_foundation_docs
   - README.md - Remove from tool list
   - ADD migration note: "Use coderef-docs server for foundation doc generation"

5. **Verify deletion:**
   - Run: grep -r 'generate_foundation_docs' . --include='*.py'
   - Result MUST be empty (no matches)

6. **Create output:**
   - Write deletion report to: C:\Users\willh\.mcp-servers\coderef\sessions\foundation-docs-cleanup\coderef-context-output.md
   - Update communication.json status to "complete"

7. **Git commit:**
   - Commit message: "cleanup(WO-FOUNDATION-DOCS-CLEANUP-001): Remove generate_foundation_docs tool - consolidate to coderef-docs"

**Why:** Foundation doc generation is being consolidated to coderef-docs ONLY. coderef-context provides data, does NOT generate docs.

**Read full instructions:** C:\Users\willh\.mcp-servers\coderef\sessions\foundation-docs-cleanup\instructions.json
```

---

## Handoff Prompt 2: coderef-workflow Agent

**Paste this into coderef-workflow MCP server chat:**

```
CLEANUP SESSION: WO-FOUNDATION-DOCS-CLEANUP-001

Location: C:\Users\willh\.mcp-servers\coderef\sessions\foundation-docs-cleanup\

**Your Task:**

DELETE all generate_foundation_docs code from your server:

1. **Delete from server.py:**
   - Line 89+: Tool definition for generate_foundation_docs

2. **Delete from tool_handlers.py:**
   - handle_generate_foundation_docs function - ENTIRE FUNCTION

3. **Delete file:**
   - generators/coderef_foundation_generator.py - ENTIRE FILE

4. **Update documentation:**
   - coderef/ALL-RESOURCES-LIST.md - Remove /update-foundation-docs entry
   - coderef/ALL-RESOURCES-REFERNCE-SHEET.md - Remove /update-foundation-docs entry
   - coderef/foundation-docs/API.md - Remove generate_foundation_docs section
   - coderef/reference-sheets/SERVER.md - Remove generate_foundation_docs
   - coderef/reference-sheets/TOOL-HANDLERS.md - Remove handle_generate_foundation_docs
   - RESOURCE-SHEET.md - Update note about coderef-docs tools
   - ADD migration note: "Use coderef-docs server for foundation doc generation"

5. **Verify deletion:**
   - Run: grep -r 'generate_foundation_docs' . --include='*.py'
   - Result MUST be empty (no matches)

6. **Create output:**
   - Write deletion report to: C:\Users\willh\.mcp-servers\coderef\sessions\foundation-docs-cleanup\coderef-workflow-output.md
   - Update communication.json status to "complete"

7. **Git commit:**
   - Commit message: "cleanup(WO-FOUNDATION-DOCS-CLEANUP-001): Remove generate_foundation_docs tool - consolidate to coderef-docs"

**Why:** Foundation doc generation is being consolidated to coderef-docs ONLY. coderef-workflow handles planning/execution, does NOT generate docs.

**Read full instructions:** C:\Users\willh\.mcp-servers\coderef\sessions\foundation-docs-cleanup\instructions.json
```

---

## Execution Order

**Parallel Execution (Both can run simultaneously):**
- coderef-context agent (delete from context server)
- coderef-workflow agent (delete from workflow server)

**After Both Complete:**
- Orchestrator verifies deletions
- Orchestrator confirms coderef-docs is sole owner

---

## Success Criteria

**Per Agent:**
- [ ] All 5 deletions complete (tool, route, import, handler, generator)
- [ ] Documentation updated with migration notes
- [ ] grep returns zero results for generate_foundation_docs
- [ ] Git commit created
- [ ] Output file created
- [ ] communication.json status = "complete"

**Overall:**
- [ ] coderef-context has NO generate_foundation_docs
- [ ] coderef-workflow has NO generate_foundation_docs
- [ ] coderef-docs STILL HAS generate_foundation_docs (verified by orchestrator)
- [ ] Users have clear migration path

---

**Orchestrator:** Available to verify deletions and confirm single source of truth established.
