# coderef-context Agent Resources Index

**Agent:** coderef-context
**Phase:** Phase 1 - Core Enhancements
**Workorder:** WO-SCANNER-CONTEXT-ENHANCEMENT-001-CODEREF-CONTEXT

---

## 📚 Source Documents

### Primary Analysis Document
**Location:** `C:\Users\willh\.mcp-servers\coderef-context\CONTEXT-LEVERAGE-ANALYSIS.md`

**What it contains:**
- Current .coderef/ resource inventory (17 files, 5 categories)
- Tool-by-tool usage analysis (13 tools, 40% utilization)
- Priority 1 enhancements (diagram inclusion, element breakdown, docs exposure)
- Implementation roadmap with code examples

**Your focus areas:**
- Lines 172-245: Priority 1 enhancements (enhance coderef_context)
- Lines 246-290: Priority 2 (populate empty reports)
- Lines 291-315: Priority 3 (expose generated docs)

### Proof of First Enhancement
**Location:** `C:\Users\willh\.mcp-servers\coderef-context\PROOF-OF-ENHANCEMENT.md`

**What it contains:**
- Completed Task 1: visual_architecture auto-inclusion (commit 69aafd0)
- Before/after response comparison
- Code changes made (handlers_refactored.py, coderef_reader.py)
- Verification checklist

**Why you need this:**
- Shows the pattern for adding fields to coderef_context response
- Demonstrates how to add CodeRefReader methods
- Provides baseline for your remaining tasks

---

## 🎯 Task Specifications

### Session Master Plan
**Location:** `C:\Users\willh\Desktop\assistant\scanner-complete-context.md`

**Your section:** Phase 1: Core Enhancements → coderef-context Tasks
- Lines 78-108: Your 7 tasks (1 complete, 6 remaining)
- Lines 109-137: Success metrics and deliverables

### Phase 1 Progress Tracker
**Location:** `C:\Users\willh\.mcp-servers\coderef\sessions\scanner-context-enhancement\phase1-progress.md`

**Current status:**
- Task 1: ✅ Complete (visual_architecture)
- Tasks 2-7: ⏳ Not started
- Overall: 1/11 Phase 1 tasks (9%)

### Session Instructions
**Location:** `C:\Users\willh\.mcp-servers\coderef\sessions\scanner-context-enhancement\instructions.json`

**Your section:** `agent_instructions.phase_1_agents.coderef-context`
- Lines 87-110: Your detailed task list
- Target files specified
- Output format requirements
- Success criteria

---

## 🗂️ Your Codebase

### Main Implementation Files
**Location:** `C:\Users\willh\.mcp-servers\coderef-context\`

**Key files for your tasks:**
- `src/handlers_refactored.py:119-244` - handle_coderef_context function
- `src/coderef_reader.py` - CodeRefReader class (add methods here)
- `server.py:224` - Tool description (update when adding features)

**Pattern to follow:**
1. Load data in handle_coderef_context (lines 226-231 example)
2. Add to response dictionary (line 239 example)
3. Add convenience method to CodeRefReader if needed (lines 163-172 example)
4. Update tool description in server.py

---

## 📊 Success Metrics

### Context Quality Target
**Baseline:** 40% of .coderef/ resources exposed
**Current:** ~55% (after Task 1)
**Target:** 95%

**What you need to add:**
- elements_by_type breakdown (function: 89, class: 12, etc.)
- complexity_hotspots array (high-complexity files)
- documentation_summary (from generated-docs/README.md)
- Populated patterns.json, validation.json, complexity.json

### Performance Target
**Tool calls:** Currently 5 → Target 1
**Response time:** Currently 0.05s → Target ≤0.1s (room to add more data)

---

## 🔗 Integration Points

### Phase 2 Dependencies
**Location:** `C:\Users\willh\.mcp-servers\coderef\sessions\scanner-context-enhancement\phase2-integration-targets.md`

**Why you need to know:**
- Lines 9-68: How coderef-workflow will use your enhanced context
- Lines 70-114: How coderef-docs will use your enhancements
- Your work enables 5 downstream integrations in Phase 2

**Key insight:**
Your enhancements eliminate redundant MCP calls in workflow planning (2 calls → 1 call)

---

## 📝 Output Requirements

### What to Create
**Location:** `../outputs/coderef-context-phase1-output.json`

**Format:**
```json
{
  "agent_id": "coderef-context",
  "phase": "phase_1",
  "tasks_completed": [
    {
      "task_id": "task_2",
      "description": "Add elements_by_type breakdown",
      "status": "complete",
      "implementation": {
        "files_modified": ["src/handlers_refactored.py"],
        "lines_changed": "226-231, 239",
        "commit": "abc123"
      },
      "validation": {
        "response_includes_field": true,
        "field_name": "elements_by_type",
        "sample_output": {"function": 89, "class": 12}
      }
    }
  ],
  "before_after_comparison": {
    "baseline_response": {...},
    "enhanced_response": {...}
  },
  "success_metrics": {
    "context_quality": "40% → 70%",
    "tool_calls_eliminated": 1,
    "response_time": "0.05s"
  }
}
```

---

## 🚀 Execution Steps

1. **READ** this index to understand all resources
2. **READ** CONTEXT-LEVERAGE-ANALYSIS.md (your primary spec)
3. **READ** PROOF-OF-ENHANCEMENT.md (pattern to follow)
4. **RUN** `/create-workorder` using `../context.json`
5. **EXECUTE** tasks following generated plan.json
6. **CREATE** outputs in `../outputs/`
7. **UPDATE** `../communication.json` status

---

## 🆘 Questions or Issues?

**Session orchestrator:** Assistant agent at `C:\Users\willh\Desktop\assistant`
**Session directory:** `C:\Users\willh\.mcp-servers\coderef\sessions\scanner-context-enhancement\`
**Your directory:** `C:\Users\willh\.mcp-servers\coderef\sessions\scanner-context-enhancement\coderef-context\`

---

**Last Updated:** 2026-01-14
**Status:** Resources indexed, ready for agent execution
