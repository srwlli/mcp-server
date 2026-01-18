# Universal Agent Handoff - CSV Ecosystem Sync

**Session:** WO-CSV-ECOSYSTEM-SYNC-001
**Your Role:** Phase 1 Project Audit
**Pattern:** Hierarchical (your workspace is isolated)

---

## Your Task

You are participating in a multi-agent session to establish **tools-and-commands.csv** as the single source of truth for the entire CodeRef ecosystem.

**Your Phase 1 Mission:**
1. Audit YOUR project against the current CSV
2. Report all discrepancies (missing resources, outdated paths, incorrect metadata)
3. Identify new resources not yet in CSV
4. Create audit report in your outputs/ directory

---

## Step-by-Step Instructions

### 1. Navigate to Your Workspace

Your workspace is in the session directory under your agent ID:

```
C:\Users\willh\.mcp-servers\coderef\sessions\csv-ecosystem-sync\{YOUR-AGENT-ID}\
```

**Agent ID Mapping:**
- Assistant project → `coderef-assistant`
- coderef-context MCP → `coderef-context`
- coderef-workflow MCP → `coderef-workflow`
- coderef-docs MCP → `coderef-docs`
- coderef-personas MCP → `coderef-personas`
- coderef-testing MCP → `coderef-testing`
- papertrail MCP → `papertrail`
- coderef-core package → `coderef-core`
- coderef-dashboard project → `coderef-dashboard`

### 2. Read Your Instructions

**Three files to read:**

```
# Start here - links to all resources
resources/index.md

# Your task list (4 tasks)
communication.json

# Detailed execution steps
instructions.json
```

### 3. Access the CSV

**CSV Location (single source of truth):**
```
C:\Users\willh\Desktop\coderef-dashboard\packages\dashboard\src\app\resources\coderef\tools-and-commands.csv
```

**Current State:** 306 resources, 9 types, 7 servers, 100% data quality

### 4. Execute Your Audit

**Task 1:** Scan your project for ALL resources
- Tools (if MCP server: server.py)
- Commands (.claude/commands/)
- Scripts (scripts/)
- Validators (if papertrail: validators/)
- Schemas (if papertrail or docs: schemas/)
- Other resource types specific to your project

**Task 2:** Compare your findings against CSV
- Check each resource: Is it in CSV?
- Verify metadata: Type, Server, Name, Path, Description
- Identify discrepancies:
  - Missing from CSV (new resources)
  - In CSV but wrong metadata (incorrect category, outdated path, wrong description)
  - In CSV but doesn't exist in project (stale entries)

**Task 3:** Document your findings

Create structured report with:
- **Discrepancies:** Array of {type, resource_name, current_csv_value, actual_value, recommendation}
- **New Resources:** Array of {type, name, description, path, server, category}

**Task 4:** Create audit report

```
outputs/{your-agent-id}-audit-report.json
```

Follow the template in session instructions.json `phase_1_output_template`

### 5. Update Communication.json

After EACH task completion, update your `communication.json`:

```json
{
  "tasks": [
    {
      "task_id": "task_1",
      "status": "complete"  // Change from "not_started" to "complete"
    }
  ]
}
```

### 6. Phase Gate Checklist

Before marking yourself complete, verify:
- [ ] All 4 tasks status='complete'
- [ ] Audit report created in outputs/
- [ ] JSON valid and follows template
- [ ] communication.json updated
- [ ] All discrepancies documented
- [ ] All new resources have complete metadata

---

## Output Format

Your audit report must be valid JSON following this structure:

```json
{
  "agent_id": "{your-agent-id}",
  "project_path": "{your-project-path}",
  "audit_date": "2026-01-17",
  "csv_baseline": {
    "resources_in_csv": 306,
    "resource_types": ["Tool", "Command", "Script", "etc"]
  },
  "audit_results": {
    "resources_found": 50,
    "discrepancies": [
      {
        "type": "missing_from_csv",
        "resource_name": "/my-new-command",
        "current_csv_value": null,
        "actual_value": "exists in .claude/commands/",
        "recommendation": "Add to CSV with Type=Command, Category=Documentation"
      }
    ],
    "new_resources": [
      {
        "type": "Command",
        "name": "/my-new-command",
        "description": "Does something useful",
        "path": "C:\\path\\to\\.claude\\commands\\my-new-command.md",
        "server": "coderef-docs",
        "category": "Documentation"
      }
    ]
  },
  "summary": {
    "total_discrepancies": 5,
    "total_new_resources": 3,
    "csv_update_required": true
  }
}
```

---

## Important Notes

**Scope Boundaries:**
- **coderef-dashboard agent:** Audit ENTIRE dashboard project EXCEPT packages/coderef-core/
- **coderef-core agent:** Audit ONLY packages/coderef-core/ (dashboard agent handles rest)
- **All other agents:** Audit your full project scope

**Don't Skip:**
- Read resources/index.md first (has project-specific context)
- Update communication.json after each task
- Validate your JSON output before submitting

**Questions?**
- Check your instructions.json for detailed execution steps
- Check session instructions.json for templates and examples

---

## What Happens After Phase 1?

Once all 9 agents complete Phase 1:
- **Orchestrator** synthesizes all audit reports
- **Phase 2:** coderef-docs agent integrates findings into CSV (session work)
- **Phase 3:**
  - **Resources Page Agent** (working directly in `~\Desktop\coderef-dashboard\packages\dashboard\src\app\resources`) implements dynamic dashboard
  - **coderef-workflow agent** (session work) updates workflow instructions

**Note:** Phase 1 audit is done in session context. Phase 2/3 implementation is done by agents working directly in their project codebases with full context.

Your Phase 1 work enables the entire ecosystem to have an accurate, living CSV as single source of truth!

---

**Ready to start?** Navigate to your workspace and begin with `resources/index.md`

**Session Path:** `C:\Users\willh\.mcp-servers\coderef\sessions\csv-ecosystem-sync\`
