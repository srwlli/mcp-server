# Slash Command Server Mapping

**Purpose:** Document which slash commands belong in which MCP server based on which server's tools they call.

**Last Updated:** December 24, 2024

---

## Commands That Should Be in coderef-docs (17 commands)

These commands primarily call **coderef-docs** tools:

| Command | Primary Tool Called | Status |
|---------|-------------------|--------|
| `/list-templates` | `list_templates` | ✓ In docs |
| `/get-template` | `get_template` | ✓ In docs |
| `/coderef-foundation-docs` | `coderef_foundation_docs` | ✓ In docs |
| `/generate-foundation-docs` | `generate_foundation_docs` | ✓ In docs |
| `/update-foundation-docs` | `generate_foundation_docs` (regenerate) | ✓ In docs |
| `/generate-user-guide` | `generate_individual_doc` | ✓ In docs |
| `/generate-my-guide` | `generate_individual_doc` | ✓ In docs |
| `/generate-quickref` | `generate_quickref_interactive` | ✓ In docs |
| `/establish-standards` | `establish_standards` | ✓ In docs |
| `/audit-codebase` | `audit_codebase` | ✓ In docs |
| `/check-consistency` | `check_consistency` | ✓ In docs |
| `/add-changelog` | `add_changelog_entry` | ✓ In docs |
| `/get-changelog` | `get_changelog` | ✓ In docs |
| `/update-changelog` | `update_changelog` (meta-tool) | ✓ In docs |
| `/update-docs` | `update_all_documentation` | ✓ In docs |
| `/git-release` | `git_release` | ✓ In docs |
| (PLACEHOLDER) | (Reserved for new doc tools) | - |

---

## Commands That Should Be in coderef-workflow (23 commands)

These commands primarily call **coderef-workflow** tools:

### Planning Phase (6 commands)

| Command | Primary Tool Called | Status |
|---------|-------------------|--------|
| `/gather-context` | `gather_context` | ⚠️ WRONG LOCATION |
| `/analyze-for-planning` | `analyze_project_for_planning` | ⚠️ WRONG LOCATION |
| `/get-planning-template` | `get_planning_template` | ⚠️ WRONG LOCATION |
| `/create-plan` | `create_plan` | ⚠️ WRONG LOCATION |
| `/validate-plan` | `validate_implementation_plan` | ⚠️ WRONG LOCATION |
| `/generate-plan-review` | `generate_plan_review_report` | ⚠️ WRONG LOCATION |

### Orchestration (1 command)

| Command | Primary Tool Called | Status |
|---------|-------------------|--------|
| `/create-workorder` | Orchestrates: gather_context + analyze + create_plan + validate | ⚠️ WRONG LOCATION |

### Execution Phase (5 commands)

| Command | Primary Tool Called | Status |
|---------|-------------------|--------|
| `/execute-plan` | `execute_plan` | ⚠️ WRONG LOCATION |
| `/update-task-status` | `update_task_status` | ⚠️ WRONG LOCATION |
| `/update-deliverables` | `update_deliverables` | ⚠️ WRONG LOCATION |
| `/generate-deliverables` | `generate_deliverables_template` | ⚠️ WRONG LOCATION |
| `/track-agent-status` | `track_agent_status` | ⚠️ WRONG LOCATION |

### Multi-Agent Coordination (5 commands)

| Command | Primary Tool Called | Status |
|---------|-------------------|--------|
| `/generate-agent-communication` | `generate_agent_communication` | ⚠️ WRONG LOCATION |
| `/assign-agent-task` | `assign_agent_task` | ⚠️ WRONG LOCATION |
| `/verify-agent-completion` | `verify_agent_completion` | ⚠️ WRONG LOCATION |
| `/generate-handoff-context` | `generate_handoff_context` | ⚠️ WRONG LOCATION |
| `/aggregate-agent-deliverables` | `aggregate_agent_deliverables` | ⚠️ WRONG LOCATION |

### Archival & Inventory (4 commands)

| Command | Primary Tool Called | Status |
|---------|-------------------|--------|
| `/archive-feature` | `archive_feature` | ⚠️ WRONG LOCATION |
| `/features-inventory` | `generate_features_inventory` | ⚠️ WRONG LOCATION |
| `/audit-plans` | `audit_plans` | ⚠️ WRONG LOCATION |
| `/log-workorder` | `log_workorder` | ⚠️ WRONG LOCATION |

### Workorder Tracking (2 commands)

| Command | Primary Tool Called | Status |
|---------|-------------------|--------|
| `/get-workorder-log` | `get_workorder_log` | ⚠️ WRONG LOCATION |

---

## Summary of Required Changes

### Move FROM coderef-docs TO coderef-workflow (23 commands)

```bash
# Create .claude/commands directory in coderef-workflow
mkdir -p ~/.mcp-servers/coderef-workflow/.claude/commands

# Move these commands:
mv ~/.mcp-servers/coderef-docs/.claude/commands/gather-context.md \
   ~/.mcp-servers/coderef-workflow/.claude/commands/

mv ~/.mcp-servers/coderef-docs/.claude/commands/analyze-for-planning.md \
   ~/.mcp-servers/coderef-workflow/.claude/commands/

mv ~/.mcp-servers/coderef-docs/.claude/commands/get-planning-template.md \
   ~/.mcp-servers/coderef-workflow/.claude/commands/

mv ~/.mcp-servers/coderef-docs/.claude/commands/create-plan.md \
   ~/.mcp-servers/coderef-workflow/.claude/commands/

mv ~/.mcp-servers/coderef-docs/.claude/commands/validate-plan.md \
   ~/.mcp-servers/coderef-workflow/.claude/commands/

mv ~/.mcp-servers/coderef-docs/.claude/commands/generate-plan-review.md \
   ~/.mcp-servers/coderef-workflow/.claude/commands/

mv ~/.mcp-servers/coderef-docs/.claude/commands/create-workorder.md \
   ~/.mcp-servers/coderef-workflow/.claude/commands/

mv ~/.mcp-servers/coderef-docs/.claude/commands/execute-plan.md \
   ~/.mcp-servers/coderef-workflow/.claude/commands/

mv ~/.mcp-servers/coderef-docs/.claude/commands/update-task-status.md \
   ~/.mcp-servers/coderef-workflow/.claude/commands/

mv ~/.mcp-servers/coderef-docs/.claude/commands/update-deliverables.md \
   ~/.mcp-servers/coderef-workflow/.claude/commands/

mv ~/.mcp-servers/coderef-docs/.claude/commands/generate-deliverables.md \
   ~/.mcp-servers/coderef-workflow/.claude/commands/

mv ~/.mcp-servers/coderef-docs/.claude/commands/track-agent-status.md \
   ~/.mcp-servers/coderef-workflow/.claude/commands/

mv ~/.mcp-servers/coderef-docs/.claude/commands/generate-agent-communication.md \
   ~/.mcp-servers/coderef-workflow/.claude/commands/

mv ~/.mcp-servers/coderef-docs/.claude/commands/assign-agent-task.md \
   ~/.mcp-servers/coderef-workflow/.claude/commands/

mv ~/.mcp-servers/coderef-docs/.claude/commands/verify-agent-completion.md \
   ~/.mcp-servers/coderef-workflow/.claude/commands/

mv ~/.mcp-servers/coderef-docs/.claude/commands/generate-handoff-context.md \
   ~/.mcp-servers/coderef-workflow/.claude/commands/

mv ~/.mcp-servers/coderef-docs/.claude/commands/aggregate-agent-deliverables.md \
   ~/.mcp-servers/coderef-workflow/.claude/commands/

mv ~/.mcp-servers/coderef-docs/.claude/commands/archive-feature.md \
   ~/.mcp-servers/coderef-workflow/.claude/commands/

mv ~/.mcp-servers/coderef-docs/.claude/commands/features-inventory.md \
   ~/.mcp-servers/coderef-workflow/.claude/commands/

mv ~/.mcp-servers/coderef-docs/.claude/commands/audit-plans.md \
   ~/.mcp-servers/coderef-workflow/.claude/commands/

mv ~/.mcp-servers/coderef-docs/.claude/commands/log-workorder.md \
   ~/.mcp-servers/coderef-workflow/.claude/commands/

mv ~/.mcp-servers/coderef-docs/.claude/commands/get-workorder-log.md \
   ~/.mcp-servers/coderef-workflow/.claude/commands/
```

### Deploy to Global Locations

```bash
# After moving, deploy workflow commands globally
cp ~/.mcp-servers/coderef-workflow/.claude/commands/*.md ~/.claude/commands/

# Keep docs commands in their current global location
cp ~/.mcp-servers/coderef-docs/.claude/commands/*.md ~/.claude/commands/
```

---

## Rationale

### Why This Separation?

1. **Single Responsibility**: Each server owns its own slash commands
   - `coderef-docs` = Documentation commands
   - `coderef-workflow` = Planning/execution commands

2. **Clarity**: Users understand which server a command uses
   - No confusion about where to find help
   - CLI help can reference correct server name

3. **Maintenance**: Easier to update commands when server tools change
   - Workflow-related commands stay in workflow directory
   - Don't need to update docs commands when workflow tools change

4. **Decoupling**: Servers are loosely coupled via MCP, not filesystem
   - Commands can call tools from ANY server
   - But should logically group together

### Example Workflow After Reorganization

```
coderef-docs/.claude/commands/
├── list-templates.md
├── get-template.md
├── generate-foundation-docs.md
├── establish-standards.md
├── audit-codebase.md
├── check-consistency.md
├── add-changelog.md
├── get-changelog.md
├── update-changelog.md
├── update-docs.md
├── git-release.md
└── (11 more docs-related commands)
   → Total: 17 commands

coderef-workflow/.claude/commands/
├── gather-context.md
├── analyze-for-planning.md
├── get-planning-template.md
├── create-plan.md
├── validate-plan.md
├── generate-plan-review.md
├── create-workorder.md
├── execute-plan.md
├── update-task-status.md
├── generate-deliverables.md
├── update-deliverables.md
├── track-agent-status.md
├── generate-agent-communication.md
├── assign-agent-task.md
├── verify-agent-completion.md
├── generate-handoff-context.md
├── aggregate-agent-deliverables.md
├── archive-feature.md
├── features-inventory.md
├── audit-plans.md
├── log-workorder.md
└── get-workorder-log.md
   → Total: 23 commands
```

---

## Implementation Steps

1. **Create coderef-workflow commands directory**
   ```bash
   mkdir -p ~/.mcp-servers/coderef-workflow/.claude/commands
   ```

2. **Move 23 workflow commands** (use bash script or manual mv commands above)

3. **Deploy globally**
   ```bash
   cp ~/.mcp-servers/coderef-workflow/.claude/commands/*.md ~/.claude/commands/
   ```

4. **Verify no duplicates**
   ```bash
   ls ~/.claude/commands/*.md | wc -l  # Should be ~40 total
   ```

5. **Commit changes** to both servers
   ```bash
   cd ~/.mcp-servers/coderef-docs && git add -A && git commit -m "refactor: Move 23 workflow commands to coderef-workflow"
   cd ~/.mcp-servers/coderef-workflow && git add -A && git commit -m "feat: Add 23 slash commands for workflow orchestration"
   ```

6. **Update documentation**
   - Update CLAUDE.md in both servers
   - Update README.md files
   - Update command counts

7. **Reload Claude Code**
   - `Ctrl+Shift+P` → "Developer: Reload Window"
   - Commands should update automatically

---

## Notes

- **Backward Compatibility**: Users can still type `/create-plan` - command name doesn't change
- **Global Deployment**: Both directories deploy to `~/.claude/commands/` globally
- **No Code Changes**: This is purely organizational (moving .md files)
- **Tool Implementation**: Tools remain in their respective servers

---

