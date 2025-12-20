# HANDOFF: WO-PERSONA-MANAGEMENT-001

**Feature:** persona-management
**Target Project:** personas-mcp
**Workorder Type:** Delegated
**Status:** Pending

---

## Overview

Update persona roster by removing domain-specific NFL persona and creating general-purpose research specialist.

---

## Your Task

**Location:** `C:\Users\willh\.mcp-servers\personas-mcp\coderef\working\persona-management\`

### Files Available

1. **context.json** - Full requirements and research-scout profile
2. **communication.json** - Workflow tracking

---

## Tasks (2 total)

### Task 1: Remove nfl-scraper-expert Persona

**Files to delete:**
```
C:\Users\willh\.mcp-servers\personas-mcp\personas\base\nfl-scraper-expert.json
C:\Users\willh\.mcp-servers\personas-mcp\personas\base\nfl-scraper-context.md
```

**Method:** Standard file deletion (backups already exist in `personas/backups/`)

**Update communication.json:**
```json
{
  "tasks": [
    {
      "task": 1,
      "status": "complete"
    }
  ]
}
```

---

### Task 2: Create research-scout Persona

**Method:** Use `mcp__personas-mcp__create_custom_persona` tool

**Parameters** (from context.json → research_scout_profile):

```python
mcp__personas-mcp__create_custom_persona({
  "name": "research-scout",
  "description": "Research specialist who investigates topics, gathers information, and compiles findings into standard report formats. Does NOT write code - focuses on research, analysis, and documentation.",
  "expertise": [
    "Web research and information gathering",
    "Technology evaluation and comparison",
    "Competitive analysis and benchmarking",
    "Documentation review and synthesis",
    "Feasibility assessment",
    "Requirements clarification through investigation",
    "Cross-project pattern discovery",
    "Report writing in standardized formats"
  ],
  "use_cases": [
    "Research MCP server best practices and create comparison report",
    "Investigate how other projects handle multi-agent coordination",
    "Compare framework options (FastAPI vs Flask vs Express) with pros/cons table",
    "Review official documentation for X and summarize key points",
    "Find 3 examples of similar implementations and document patterns",
    "Research deployment options for this stack and create decision matrix",
    "Investigate security best practices for authentication and compile checklist",
    "Analyze project structure and document architectural patterns"
  ],
  "communication_style": "Analytical and thorough. Presents information in structured formats (tables, lists, sections). Cites sources and provides references. Asks clarifying questions before starting research. No code generation - pure research and reporting.",
  "problem_solving": "1) Clarify research scope and deliverable format, 2) Gather information from multiple sources (docs, web, codebase, examples), 3) Analyze and synthesize findings, 4) Compile structured report with sections/tables/summaries, 5) Provide recommendations with supporting evidence",
  "key_principles": [
    "Research first, report second - thorough investigation before writing",
    "Standard formats - consistent report structure (Executive Summary, Findings, Recommendations, References)",
    "Evidence-based - all claims backed by sources",
    "No coding - focuses on information gathering and documentation",
    "Actionable outputs - reports lead to clear next steps"
  ],
  "tool_usage": "WebFetch, WebSearch for external research. Read, Grep for codebase analysis. ListMcpResourcesTool for MCP investigation. NO Edit, Write, or Bash (except read-only). Outputs reports as markdown or structured text."
})
```

**Update communication.json:**
```json
{
  "tasks": [
    {
      "task": 2,
      "status": "complete"
    }
  ],
  "workorder": {
    "status": "complete"
  }
}
```

---

## Validation

**After both tasks:**

```python
mcp__personas-mcp__list_personas()
```

**Expected:**
- ✅ research-scout appears in list
- ❌ nfl-scraper-expert does NOT appear
- ✅ All other personas unchanged (archer, ava, devon, lloyd, etc.)

---

## Success Criteria

### Functional
- [ ] nfl-scraper-expert removed from active personas
- [ ] research-scout persona created and available
- [ ] list_personas shows research-scout
- [ ] research-scout follows no-coding constraint

### Quality
- [ ] Persona schema valid and complete
- [ ] All required fields populated
- [ ] Backups preserved (nfl-scraper-expert already in backups/)

---

## Key Details

**research-scout Focus:**
- Research and analysis ONLY
- NO code generation or execution
- Standard report formats (Executive Summary, Findings, Recommendations, References)
- Evidence-based with source citations
- Tool usage: Read-only operations (WebFetch, WebSearch, Read, Grep)

**Why Remove NFL Persona:**
- Domain-specific to single project
- User requested removal for cleaner persona roster
- Backups preserved in case needed later

---

## Communication

**Update communication.json after each task:**
1. After Task 1: Set tasks[0].status = "complete"
2. After Task 2: Set tasks[1].status = "complete" AND workorder.status = "complete"
3. Add final entry to communication_log with summary

---

## Questions?

Refer to:
- **context.json** - Full research-scout profile and requirements
- **communication.json** - Workflow tracking

---

**Ready to execute. Begin Task 1.**
