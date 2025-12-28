# API Reference - coderef-workflow

**Generated:** 2025-12-28
**Version:** 1.1.0
**Project:** coderef-workflow MCP Server

---

## Purpose

This document provides a complete reference for the **coderef-workflow** MCP (Model Context Protocol) tool endpoints. These tools orchestrate the feature development lifecycle including context gathering, planning, execution tracking, and archiving.

## Overview

coderef-workflow exposes **23 MCP tools** organized into 6 functional categories:

1. **Planning & Analysis** - Context gathering and plan creation
2. **Execution & Tracking** - Task management and progress monitoring
3. **Deliverables & Documentation** - Metrics capture and doc updates
4. **Risk & Integration** - Risk assessment and multi-agent coordination
5. **Archival & Inventory** - Feature archiving and inventory management
6. **Workorder Tracking** - Global workorder audit trail

All tools follow async/await patterns and return structured JSON responses or text content via MCP `TextContent` objects.

---

## What: Tool Categories

### 1. Planning & Analysis Phase

Tools for gathering requirements and creating implementation plans.

#### `gather_context`

Collect feature requirements and constraints through interactive workflow.

**Parameters:**
```json
{
  "project_path": "string (required) - Absolute path to project directory",
  "feature_name": "string (required) - Feature name (alphanumeric, hyphens, underscores)",
  "description": "string (required) - What the feature does",
  "goal": "string (required) - Why this feature is needed",
  "requirements": "array<string> (required) - Must-have requirements",
  "out_of_scope": "array<string> (optional) - Explicitly excluded features",
  "constraints": "array<string> (optional) - Technical or business constraints"
}
```

**Returns:**
```json
{
  "status": "success",
  "feature_name": "string",
  "context_file": "string - Path to context.json"
}
```

**Example:**
```bash
# Called via MCP
mcp__coderef_workflow__gather_context({
  "project_path": "/path/to/project",
  "feature_name": "user-authentication",
  "description": "JWT-based authentication system",
  "goal": "Secure user login and session management",
  "requirements": ["JWT tokens", "Refresh token rotation", "Password hashing"],
  "constraints": ["Must integrate with existing user table"]
})
```

---

#### `analyze_project_for_planning`

Scan codebase for architecture patterns and existing implementations.

**Parameters:**
```json
{
  "project_path": "string (required) - Absolute path to project directory",
  "feature_name": "string (optional) - Feature name for saving analysis"
}
```

**Returns:**
```json
{
  "analysis": {
    "foundation_docs": ["ARCHITECTURE.md", "SCHEMA.md"],
    "coding_standards": ["Python 3.10+", "async/await"],
    "tech_stack": ["FastAPI", "SQLAlchemy", "pytest"],
    "key_patterns": ["Decorator-based handlers", "MCP protocol"],
    "project_structure": {
      "src/": "Tool implementations",
      "generators/": "Plan generators"
    }
  },
  "analysis_file": "string - Path to analysis.json"
}
```

---

#### `create_plan`

Generate complete 10-section implementation plan from context and analysis.

**Parameters:**
```json
{
  "project_path": "string (required) - Absolute path to project directory",
  "feature_name": "string (required) - Feature name",
  "workorder_id": "string (optional) - Workorder ID (e.g., WO-AUTH-001)"
}
```

**Returns:**
```json
{
  "status": "success",
  "feature_name": "string",
  "workorder_id": "string",
  "plan_file": "string - Path to plan.json",
  "deliverables_file": "string - Path to DELIVERABLES.md",
  "phase_count": "number",
  "task_count": "number"
}
```

---

#### `validate_implementation_plan`

Score plan quality (0-100) and identify issues.

**Parameters:**
```json
{
  "project_path": "string (required)",
  "plan_file_path": "string (required) - Relative path to plan.json"
}
```

**Returns:**
```json
{
  "score": 92,
  "approved": true,
  "issues": {
    "critical": [],
    "major": [],
    "minor": ["Short description in IMPL-003"]
  },
  "checklist_results": {
    "total": 15,
    "passed": 14,
    "failed": 1
  }
}
```

---

###  2. Execution & Tracking Phase

Tools for task management and progress monitoring.

#### `execute_plan`

Align plan with TodoWrite task list for tracking. **Note:** Tool is still named `execute_plan` internally but maps to `/align-plan` slash command.

**Parameters:**
```json
{
  "project_path": "string (required)",
  "feature_name": "string (required)"
}
```

**Returns:**
```json
{
  "feature_name": "string",
  "workorder_id": "string",
  "task_count": 27,
  "tasks": [
    {
      "content": "CORE-001: server.py:778 - Rename tool registration",
      "activeForm": "Renaming tool registration",
      "status": "pending"
    }
  ],
  "plan_file": "string",
  "timestamp": "ISO 8601 timestamp"
}
```

**Usage Note:** This tool generates TodoWrite-formatted task lists that are printed to the CLI terminal for tracking during implementation.

---

#### `update_task_status`

Update individual task status in plan.json.

**Parameters:**
```json
{
  "project_path": "string (required)",
  "feature_name": "string (required)",
  "task_id": "string (required) - Task ID (e.g., SETUP-001)",
  "status": "string (required) - pending|in_progress|completed|blocked",
  "notes": "string (optional) - Status change notes"
}
```

**Returns:**
```json
{
  "status": "success",
  "task_id": "SETUP-001",
  "new_status": "completed",
  "progress_summary": {
    "total": 27,
    "completed": 5,
    "in_progress": 1,
    "pending": 21,
    "percent": 18.5
  }
}
```

---

### 3. Deliverables & Documentation

Tools for capturing metrics and updating documentation.

#### `update_deliverables`

Update DELIVERABLES.md with git metrics (LOC, commits, time).

**Parameters:**
```json
{
  "project_path": "string (required)",
  "feature_name": "string (required)"
}
```

**Returns:**
```json
{
  "status": "success",
  "metrics": {
    "lines_of_code": 450,
    "files_modified": 8,
    "commits": 12,
    "time_spent_hours": 6.5,
    "contributors": ["willh", "Claude"]
  },
  "deliverables_file": "string"
}
```

---

#### `update_all_documentation`

Agentic workflow to update README/CHANGELOG/CLAUDE.md with version bumping.

**Parameters:**
```json
{
  "project_path": "string (required)",
  "change_type": "string (required) - breaking_change|feature|enhancement|bugfix|security|deprecation",
  "feature_description": "string (required) - What changed",
  "workorder_id": "string (required) - WO-{FEATURE}-### format",
  "files_changed": "array<string> (optional) - Modified files",
  "version": "string (optional) - Manual version override"
}
```

**Returns:**
```json
{
  "status": "success",
  "version": "1.2.0",
  "files_updated": ["README.md", "CLAUDE.md", "CHANGELOG.json"],
  "changelog_entry_added": true
}
```

---

### 4. Risk & Integration

Tools for risk assessment and multi-agent coordination.

#### `assess_risk`

AI-powered risk assessment across 5 dimensions.

**Parameters:**
```json
{
  "project_path": "string (required)",
  "proposed_change": {
    "description": "string (required) - Human-readable change description",
    "change_type": "string (required) - create|modify|delete|refactor|migrate",
    "files_affected": "array<string> (required) - File paths to modify"
  },
  "options": "array<object> (optional) - Alternative approaches (max 5)",
  "threshold": "number (optional) - Risk score threshold 0-100 (default: 50)",
  "feature_name": "string (optional) - For assessment filename"
}
```

**Returns:**
```json
{
  "risk_score": 35,
  "recommendation": "go",
  "dimensions": {
    "breaking_changes": 10,
    "security": 5,
    "performance": 15,
    "maintainability": 3,
    "reversibility": 2
  },
  "issues": ["Potential N+1 query in user lookup"],
  "mitigations": ["Add database index on user_id"],
  "assessment_file": "string"
}
```

---

#### `generate_agent_communication`

Generate communication.json for multi-agent coordination.

**Parameters:**
```json
{
  "project_path": "string (required)",
  "feature_name": "string (required)"
}
```

**Returns:**
```json
{
  "status": "success",
  "agent_count": 3,
  "communication_file": "string",
  "tasks_generated": 45,
  "forbidden_files_per_agent": {
    "agent_1": ["src/backend.py"],
    "agent_2": ["src/frontend.tsx"]
  }
}
```

---

### 5. Archival & Inventory

Tools for feature archiving and inventory management.

#### `archive_feature`

Move completed feature from workorder/ to archived/.

**Parameters:**
```json
{
  "project_path": "string (required)",
  "feature_name": "string (required) - Feature folder name",
  "force": "boolean (optional) - Skip confirmation (default: false)"
}
```

**Returns:**
```json
{
  "status": "success",
  "feature_name": "string",
  "archived_path": "string - Path in coderef/archived/",
  "archive_index_updated": true
}
```

---

#### `generate_features_inventory`

List all active and archived features with status.

**Parameters:**
```json
{
  "project_path": "string (required)",
  "format": "string (optional) - json|markdown (default: json)",
  "include_archived": "boolean (optional) - Include archived features (default: true)",
  "save_to_file": "boolean (optional) - Save to coderef/features-inventory.json (default: false)"
}
```

**Returns:**
```json
{
  "active_features": [
    {
      "name": "execute-plan-rename",
      "workorder_id": "WO-EXECUTE-PLAN-RENAME-001",
      "status": "planning",
      "progress": "0/27 tasks",
      "created": "2025-12-27"
    }
  ],
  "archived_features": [
    {
      "name": "fix-workflow-bugs",
      "workorder_id": "WO-WORKFLOW-REFACTOR-001",
      "status": "complete",
      "completed": "2025-12-25"
    }
  ],
  "summary": {
    "total_active": 6,
    "total_archived": 3
  }
}
```

---

### 6. Workorder Tracking

Tools for global workorder audit trail.

#### `log_workorder`

Add entry to global workorder log file.

**Parameters:**
```json
{
  "project_path": "string (required)",
  "workorder_id": "string (required) - WO-{FEATURE}-###",
  "project_name": "string (required) - Short project identifier",
  "description": "string (required) - Brief workorder description (max 50 chars)",
  "timestamp": "string (optional) - ISO 8601 timestamp (auto-generated if omitted)"
}
```

**Returns:**
```json
{
  "status": "success",
  "workorder_id": "WO-AUTH-001",
  "log_file": "string - Path to workorder-log.txt"
}
```

---

#### `get_workorder_log`

Query global workorder log file.

**Parameters:**
```json
{
  "project_path": "string (required)",
  "project_name": "string (optional) - Filter by project (partial match)",
  "workorder_pattern": "string (optional) - Filter by WO-ID pattern (e.g., WO-AUTH)",
  "limit": "number (optional) - Max entries to return"
}
```

**Returns:**
```json
{
  "entries": [
    {
      "workorder_id": "WO-AUTH-001",
      "project": "coderef-workflow",
      "description": "Implement JWT authentication",
      "timestamp": "2025-12-28T10:30:00Z"
    }
  ],
  "total_count": 45,
  "filtered_count": 3
}
```

---

## Why: Design Decisions

### MCP Protocol Choice
coderef-workflow uses the Model Context Protocol instead of traditional REST/GraphQL because:
- **AI-First:** Designed for AI agent interactions, not human HTTP clients
- **Tool Discovery:** MCP provides automatic tool schema discovery
- **Async Native:** Built-in async/await support for long-running operations
- **Type Safety:** JSON Schema validation for all inputs/outputs

### Workorder-Centric Architecture
Every feature gets a unique workorder ID (WO-{FEATURE}-###) for:
- Complete audit trail across feature lifecycle
- Multi-agent coordination with unique task IDs
- Historical tracking and recovery
- Cross-project workorder visibility

### Context Injection Pattern
Tools like `analyze_project_for_planning` and `create_plan` integrate with **coderef-context** to inject real code intelligence:
- AST-based code analysis (not regex)
- Dependency graphs and impact analysis
- Pattern detection for consistency
- Graceful fallback when coderef-context unavailable

---

## When: Usage Patterns

### Typical Feature Workflow

```
1. /create-workorder
   ├─ gather_context()
   ├─ analyze_project_for_planning()
   ├─ create_plan()
   ├─ validate_implementation_plan()
   ├─ execute_plan() [/align-plan command]
   └─ [Git commit]

2. Implementation Phase
   ├─ update_task_status() (as work progresses)
   └─ [Agent or developer codes]

3. Documentation Phase
   ├─ update_deliverables()
   ├─ update_all_documentation()
   └─ [Manual doc updates]

4. Archival
   └─ archive_feature()
```

### Multi-Agent Workflow

```
1. create_plan() with multi_agent: true
2. generate_agent_communication()
3. assign_agent_task() for each agent (1-N)
4. Agents work in parallel, updating communication.json
5. verify_agent_completion() for each agent
6. aggregate_agent_deliverables()
7. archive_feature()
```

---

## Examples

### Example 1: Create and Validate Plan

```python
# Step 1: Gather context
response = await mcp_client.call_tool("gather_context", {
    "project_path": "/workspace/my-app",
    "feature_name": "dark-mode",
    "description": "Toggle between light and dark UI themes",
    "goal": "Improve accessibility and reduce eye strain",
    "requirements": [
        "Theme persistence in localStorage",
        "System preference detection",
        "Smooth transitions"
    ]
})

# Step 2: Analyze project
response = await mcp_client.call_tool("analyze_project_for_planning", {
    "project_path": "/workspace/my-app",
    "feature_name": "dark-mode"
})

# Step 3: Create plan
response = await mcp_client.call_tool("create_plan", {
    "project_path": "/workspace/my-app",
    "feature_name": "dark-mode"
})

# Step 4: Validate plan
response = await mcp_client.call_tool("validate_implementation_plan", {
    "project_path": "/workspace/my-app",
    "plan_file_path": "coderef/workorder/dark-mode/plan.json"
})

print(f"Plan score: {response['score']}/100")
if response['approved']:
    print("✅ Plan ready for execution")
```

---

### Example 2: Track Task Progress

```python
# Mark task as in progress
await mcp_client.call_tool("update_task_status", {
    "project_path": "/workspace/my-app",
    "feature_name": "dark-mode",
    "task_id": "IMPL-001",
    "status": "in_progress"
})

# ... implement the task ...

# Mark task as completed
response = await mcp_client.call_tool("update_task_status", {
    "project_path": "/workspace/my-app",
    "feature_name": "dark-mode",
    "task_id": "IMPL-001",
    "status": "completed",
    "notes": "Theme toggle component created with tests"
})

print(f"Progress: {response['progress_summary']['percent']}%")
```

---

### Example 3: Risk Assessment

```python
response = await mcp_client.call_tool("assess_risk", {
    "project_path": "/workspace/my-app",
    "proposed_change": {
        "description": "Refactor AuthService to use dependency injection",
        "change_type": "refactor",
        "files_affected": [
            "src/auth/service.py",
            "src/auth/decorators.py",
            "tests/test_auth.py"
        ]
    },
    "threshold": 50
})

if response['recommendation'] == 'go':
    print(f"✅ Low risk ({response['risk_score']}/100)")
    print(f"Mitigations: {response['mitigations']}")
else:
    print(f"⚠️ High risk ({response['risk_score']}/100)")
    print(f"Issues: {response['issues']}")
```

---

## Error Handling

All tools return structured errors via MCP:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Feature name must be alphanumeric with hyphens/underscores",
    "details": {
      "field": "feature_name",
      "provided": "my feature!",
      "expected": "my-feature"
    }
  }
}
```

**Common Error Codes:**
- `VALIDATION_ERROR` - Invalid input parameters
- `NOT_FOUND` - Feature or file not found
- `ALREADY_EXISTS` - Feature already exists
- `DEPENDENCY_ERROR` - Required tool unavailable (e.g., coderef-context)
- `EXECUTION_ERROR` - Tool execution failed

---

## Rate Limits & Performance

### No Rate Limits
MCP tools run locally - no external API rate limits apply.

### Performance Notes
- `analyze_project_for_planning`: 5-30 seconds (depends on project size)
- `create_plan`: 10-60 seconds (includes LLM generation)
- `validate_implementation_plan`: 2-5 seconds (JSON validation)
- `execute_plan`: < 1 second (task list generation)
- `update_task_status`: < 1 second (JSON update)

### Caching
- `analyze_project_for_planning` caches results in analysis.json
- `create_plan` reuses cached analysis when available
- No explicit cache invalidation - regenerate when needed

---

## Authentication & Authorization

**Not applicable** - MCP tools run in local process context. Security is handled by:
- File system permissions (tools read/write to project directories)
- MCP server configuration (who can connect to the server)
- No API keys or tokens required

---

## Versioning

API follows semantic versioning tied to coderef-workflow releases:
- **Current:** v1.1.0
- **Breaking changes:** Major version bump (e.g., 1.x.x → 2.0.0)
- **New tools:** Minor version bump (e.g., 1.1.x → 1.2.0)
- **Bug fixes:** Patch version bump (e.g., 1.1.0 → 1.1.1)

---

## References

- **ARCHITECTURE.md** - System architecture and design patterns
- **SCHEMA.md** - Data models (plan.json, context.json, etc.)
- **CLAUDE.md** - Complete AI context documentation
- **MCP Specification** - https://modelcontextprotocol.io

---

**For AI agents:** This API provides complete feature lifecycle management. Start with `gather_context` → `create_plan` → `execute_plan`, then track progress with `update_task_status`. Always validate plans before execution. Use `assess_risk` for major refactorings.
