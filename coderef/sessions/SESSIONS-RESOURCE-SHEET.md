---
Agent: Claude Sonnet 4.5
Date: 2026-01-04
Task: DOCUMENT
---

# Sessions System — Authoritative Documentation

## Executive Summary

The **Sessions System** is a multi-agent coordination protocol that enables parallel, autonomous work across the CodeRef ecosystem. Sessions define structured workorders where an orchestrator agent delegates tasks to multiple specialized agents, each producing independent outputs that are later synthesized. The system provides state tracking, handoff protocols, and progress aggregation through standardized JSON contracts (`communication.json` + `instructions.json`).

## Audience & Intent

- **Markdown (this document):** Architectural truth for session structure, state lifecycle, coordination protocols
- **communication.json:** Runtime state authority for agent status, progress tracking, output file paths
- **instructions.json:** Task contract authority for orchestrator/agent responsibilities, output templates
- **SESSION-INDEX.md:** Historical record of completed and active sessions

## 1. Architecture Overview

### Role in Larger System
The Sessions System sits within the **coderef orchestrator** (`C:\Users\willh\.mcp-servers\coderef\`) and coordinates work across:
- **3 core projects:** assistant, coderef-system, coderef-dashboard
- **6 MCP servers:** coderef-context, coderef-workflow, coderef-docs, coderef-personas, coderef-testing, papertrail

### Component Hierarchy

```
coderef/
 sessions/
     SESSION-INDEX.md                    # Master tracking document
     ORCHESTRATOR-README.md              # Orchestrator role definition
     workflow.txt                        # Global workflow state
     workorder-log.txt                   # Append-only workorder log
    
     {session-name}/                     # Session directory
         communication.json              # Agent roster + status tracking
         instructions.json               # Orchestrator + agent task specs
         orchestrator-{output}.{ext}     # Orchestrator synthesis output
         {agent-id}-{output}.{ext}       # Agent outputs (1 per agent)
         (optional session-specific files)
```

### Key Integration Points

| Integration | Direction | Contract |
|-------------|-----------|----------|
| Orchestrator → Agents | Handoff prompts | instructions.json template |
| Agents → Orchestrator | Status updates | communication.json state changes |
| Agents → Session | Output delivery | File writes to output_file paths |
| Orchestrator → Session | Synthesis | Reads all agent outputs, writes unified result |

## 2. State Ownership & Source of Truth (Canonical)

| State | Owner | Type | Persistence | Source of Truth |
|-------|-------|------|-------------|-----------------|
| `workorder_id` | Orchestrator | Session | communication.json | Immutable on creation |
| `feature_name` | Orchestrator | Session | communication.json | Immutable on creation |
| `status` (session) | Orchestrator | Session | communication.json | Orchestrator writes |
| `orchestrator.status` | Orchestrator | Agent | communication.json | Orchestrator writes |
| `agents[].status` | Individual agent | Agent | communication.json | Agent writes (self-reported) |
| `aggregation.*` | Orchestrator | Session | communication.json | Computed from agent statuses |
| `instructions_file` | Orchestrator | Session | communication.json | Path pointer (immutable) |
| `output_file` | Orchestrator/Agent | Session | communication.json | Path pointer (immutable) |

**Precedence Rules:**
1. **Immutable fields** (`workorder_id`, `feature_name`, file paths): NEVER modified after session creation
2. **Self-reported status**: Agents own their `status` field, orchestrator READS but does NOT write
3. **Aggregated status**: Orchestrator computes `aggregation.*` by reading all `agents[].status`
4. **Session status**: Orchestrator owns top-level `status` field (session lifecycle state)

## 3. Data Persistence

### Storage Schema

**communication.json:**
```json
{
  "workorder_id": "WO-{CATEGORY}-{ID}",          // Immutable
  "feature_name": "{session-name}",               // Immutable
  "created": "YYYY-MM-DD",                        // Immutable
  "status": "not_started|in_progress|complete",   // Orchestrator-owned
  "description": "...",                           // Immutable
  "instructions_file": "path/to/instructions.json", // Immutable

  "orchestrator": {
    "agent_id": "coderef",
    "agent_path": "C:\\...\\coderef",
    "role": "...",
    "output_file": "path/to/output",
    "status": "not_started|in_progress|complete", // Orchestrator-owned
    "notes": ""
  },

  "agents": [
    {
      "agent_id": "{agent-name}",
      "agent_path": "C:\\...\\{agent-project}",
      "output_file": "path/to/output",
      "status": "not_started|in_progress|complete", // Agent-owned
      "notes": ""
    }
  ],

  "aggregation": {
    "total_agents": N,
    "completed": X,
    "pending": Y,
    "not_started": Z
  }
}
```

**instructions.json:**
```json
{
  "workorder_id": "WO-{CATEGORY}-{ID}",
  "task": "...",
  "description": "...",

  "orchestrator_instructions": {
    "role": "...",
    "steps": {
      "step_1": "...",
      "step_2": "..."
    }
  },

  "agent_instructions": {
    "role": "...",
    "steps": {
      "step_1": "...",
      "step_2": "..."
    }
  },

  "context": { /* session-specific context */ },
  "output_format": "json|markdown|text",
  "output_template": { /* expected structure */ },
  "quality_standards": { /* validation rules */ }
}
```

### Versioning Strategy
- **No versioning currently:** Sessions are immutable after creation
- **Future consideration:** Add `schema_version` field if protocol changes

### Failure Modes & Recovery

| Failure | Detection | Recovery |
|---------|-----------|----------|
| Agent doesn't update status | Orchestrator checks `aggregation.not_started` count | Manual intervention - check agent logs |
| Invalid JSON in communication.json | Parse error on read | Restore from backup or manual fix |
| Missing output file | Orchestrator checks file existence | Re-run agent task |
| Agent writes to wrong path | Orchestrator can't find expected output | Update communication.json or move file |

### Cross-Agent Sync
- **No automatic sync:** Agents work independently, orchestrator aggregates manually
- **Status updates:** Agents must explicitly write status changes to communication.json
- **File locking:** Not currently implemented (potential race condition if concurrent writes)

## 4. State Lifecycle

### Canonical Sequence

```
1. INITIALIZATION
   - Orchestrator creates session directory
   - Orchestrator writes communication.json (all statuses: "not_started")
   - Orchestrator writes instructions.json (task specs)
   - Orchestrator updates SESSION-INDEX.md and workorder-log.txt

2. HANDOFF
   - Orchestrator generates handoff prompts for each agent
   - User manually pastes prompts into agent chat sessions
   - Agents read communication.json + instructions.json

3. AGENT EXECUTION
   - Each agent follows agent_instructions.steps
   - Agent writes output to agents[].output_file path
   - Agent updates agents[].status to "in_progress" → "complete"
   - Agent updates agents[].notes if needed

4. AGGREGATION CHECK
   - Orchestrator reads communication.json
   - Orchestrator computes aggregation.completed count
   - Orchestrator waits until aggregation.completed == aggregation.total_agents

5. ORCHESTRATOR SYNTHESIS
   - Orchestrator reads all agent output files
   - Orchestrator follows orchestrator_instructions.steps
   - Orchestrator writes orchestrator.output_file
   - Orchestrator updates orchestrator.status to "complete"

6. SESSION COMPLETION
   - Orchestrator updates top-level status to "complete"
   - Orchestrator updates SESSION-INDEX.md
   - Session directory becomes archival reference
```

## 5. Behaviors (Events & Side Effects)

### User Behaviors
| Behavior | Trigger | Side Effects |
|----------|---------|--------------|
| `/create-session` | User command | Creates session directory, communication.json, instructions.json |
| Paste handoff prompt | User action | Agent begins execution, reads instructions |
| Agent completes task | Agent writes output | Updates communication.json status field |
| Orchestrator synthesizes | Orchestrator reads outputs | Creates synthesis document, marks session complete |

### System Behaviors
| Behavior | Trigger | Side Effects |
|----------|---------|--------------|
| Status aggregation | Orchestrator reads communication.json | Computes completed/pending/not_started counts |
| SESSION-INDEX update | Session creation or completion | Appends new session entry |
| workorder-log append | Session creation | Adds WO-{ID} line to log |

## 6. Event & Callback Contracts

| Event | Trigger | Payload | Side Effects |
|-------|---------|---------|--------------|
| `session_created` | `/create-session` | `{session_name, workorder_id}` | Files created, logs updated |
| `agent_started` | Agent updates status | `{agent_id, status: "in_progress"}` | communication.json modified |
| `agent_completed` | Agent updates status | `{agent_id, status: "complete", output_file}` | communication.json modified, output file exists |
| `orchestrator_synthesized` | Orchestrator completes | `{orchestrator.status: "complete", output_file}` | Synthesis document created |
| `session_completed` | All agents + orchestrator done | `{status: "complete"}` | SESSION-INDEX updated |

## 7. Performance Considerations

### Known Limits
- **Agent concurrency:** No limit - agents work independently
- **Session size:** Tested with 9 agents, scales linearly
- **File I/O:** JSON parse/write for each status update (< 10ms)

### Bottlenecks
- **Manual handoff:** User must paste prompts into each agent session (slow, error-prone)
- **Status polling:** Orchestrator must manually check communication.json for completion

### Optimization Opportunities
- **Automated handoff:** CLI tool to open agent sessions and inject prompts
- **Webhooks/polling:** Agents could POST status updates to orchestrator API
- **Parallel synthesis:** Orchestrator could start partial synthesis as agents complete

### Deferred Optimizations
- **File locking:** Not implemented - acceptable risk for current usage (single orchestrator)
- **Schema validation:** Not enforced on write - manual JSON editing could break format
- **Rollback:** No transaction support - failed sessions require manual cleanup

## 8. Accessibility

### Current Gaps

| Issue | Severity | Affected Users |
|-------|----------|----------------|
| Manual handoff prompts | High | Orchestrator must copy/paste N times per session |
| No CLI automation | High | Cannot script session execution |
| JSON manual editing | Medium | Error-prone status updates |
| No progress UI | Low | Must read JSON files to check status |

### Required Tasks (Prioritized)
1. **[P0] CLI automation:** `coderef session start {session-name}` to auto-handoff agents
2. **[P1] Status dashboard:** Web UI to visualize session progress
3. **[P2] JSON schema validation:** Enforce communication.json structure on writes
4. **[P3] Agent API:** REST endpoints for agents to POST status updates

## 9. Testing Strategy

### Must-Cover Scenarios
-  Session creation with 2 agents (coderef-core-dashboard-integration)
-  Session creation with 9 agents (document-effectiveness)
-  Agent status updates (manual write to communication.json)
-  Orchestrator synthesis (manual read of agent outputs)
- ⏳ Concurrent agent execution (untested - agents currently run sequentially)
- ⏳ Session failure recovery (untested - no automated retry)

### Explicitly Not Tested
- **Concurrent writes to communication.json:** Acceptable risk - single orchestrator workflow
- **Invalid JSON recovery:** Manual intervention assumed
- **Cross-session dependencies:** Out of scope - sessions are independent

## 10. Non-Goals / Out of Scope

**Explicit Rejections:**
-  **Real-time collaboration:** Sessions are async, no live editing
-  **Agent-to-agent communication:** Agents work independently, only orchestrator aggregates
-  **Versioned outputs:** Agents overwrite output files, no history tracking
-  **Distributed orchestration:** Single orchestrator per session, no multi-node coordination
-  **Transaction support:** No rollback mechanism for failed sessions

## 11. Common Pitfalls & Sharp Edges

### Integration Gotchas
1. **Case-sensitive paths:** Windows paths in JSON use backslashes (`C:\\...`), must escape properly
2. **Agent ID mismatch:** `agent_id` in communication.json must match agent project expectations
3. **Output path typos:** If `output_file` path is wrong, orchestrator can't find output
4. **Status typos:** Only 3 valid values: `not_started`, `in_progress`, `complete` (no `completed`!)

### Configuration Mistakes
1. **Forgetting to update aggregation:** Orchestrator must manually recompute after agent status changes
2. **Immutable field edits:** Changing `workorder_id` or `feature_name` breaks log references
3. **Missing instructions.json:** Agents can't execute without task spec

### Edge Cases
1. **Agent completes but forgets to update status:** Orchestrator will wait forever (manual intervention required)
2. **Agent writes to wrong path:** Output exists but orchestrator looks elsewhere (path mismatch)
3. **Partial agent completion:** Orchestrator must decide whether to proceed with incomplete results

## 12. Workflow Diagram

> **Note:** This diagram is **illustrative**, not authoritative. State tables and text define truth.

```

 ORCHESTRATOR (coderef)                                      

         
          1. CREATE SESSION
         

 sessions/{session-name}/                                    
   - communication.json (agent roster + status)              
   - instructions.json (orchestrator + agent tasks)          

         
          2. GENERATE HANDOFF PROMPTS
         

 USER (manual)                                                
   - Paste prompts into agent chat sessions                  

         
          3. AGENTS EXECUTE
         

 Agent 1          Agent 2           Agent N                 
 - Read comm.json - Read comm.json  - Read comm.json        
 - Read instr.    - Read instr.     - Read instr.           
 - Execute task   - Execute task    - Execute task          
 - Write output   - Write output    - Write output          
 - Update status  - Update status   - Update status         

         
          4. ORCHESTRATOR CHECKS COMPLETION
         

 ORCHESTRATOR (coderef)                                      
   - Read communication.json                                 
   - Check aggregation.completed == total_agents             
   - If complete → proceed to synthesis                      

         
          5. SYNTHESIZE
         

 ORCHESTRATOR (coderef)                                      
   - Read all agent output files                             
   - Follow orchestrator_instructions.steps                  
   - Write orchestrator-output.{ext}                         
   - Update orchestrator.status = "complete"                 
   - Update session status = "complete"                      

         
          6. SESSION COMPLETE
         

 SESSION-INDEX.md updated                                    
 Session directory becomes archival reference                

```

## 13. File Path Conventions

### Absolute Paths (Windows)
- **Sessions root:** `C:\Users\willh\.mcp-servers\coderef\sessions\`
- **Session directory:** `{sessions_root}\{session-name}\`
- **Communication file:** `{session_dir}\communication.json`
- **Instructions file:** `{session_dir}\instructions.json`
- **Orchestrator output:** `{session_dir}\orchestrator-{name}.{ext}`
- **Agent output:** `{session_dir}\{agent-id}-{name}.{ext}`

### Agent Paths
| Agent ID | Project Path |
|----------|--------------|
| `coderef` | `C:\Users\willh\.mcp-servers\coderef` |
| `coderef-assistant` | `C:\Users\willh\Desktop\assistant` |
| `coderef-context` | `C:\Users\willh\.mcp-servers\coderef-context` |
| `coderef-workflow` | `C:\Users\willh\.mcp-servers\coderef-workflow` |
| `coderef-docs` | `C:\Users\willh\.mcp-servers\coderef-docs` |
| `coderef-personas` | `C:\Users\willh\.mcp-servers\coderef-personas` |
| `coderef-testing` | `C:\Users\willh\.mcp-servers\coderef-testing` |
| `papertrail` | `C:\Users\willh\.mcp-servers\papertrail` |
| `coderef-system` | `C:\Users\willh\Desktop\projects\coderef-system` |
| `coderef-dashboard` | `C:\Users\willh\Desktop\coderef-dashboard` |
| `coderef-packages` | `C:\Users\willh\Desktop\projects\coderef-system\packages` |

## 14. Example Session Walkthrough

### Scenario: Integrate @coderef/core into Dashboard

**1. Session Creation**
```bash
/create-session
# User provides: session-name, workorder-id, task description
# Orchestrator creates:
#   - sessions/coderef-core-dashboard-integration/communication.json
#   - sessions/coderef-core-dashboard-integration/instructions.json
```

**2. Initial State (communication.json)**
```json
{
  "workorder_id": "WO-CORE-DASHBOARD-INTEGRATION-001",
  "status": "not_started",
  "aggregation": {
    "total_agents": 2,
    "completed": 0,
    "not_started": 2
  }
}
```

**3. Agent Execution**
- User pastes handoff prompts into `coderef-packages` and `coderef-dashboard` sessions
- Each agent reads instructions, creates plan.json, updates status to "complete"

**4. Mid-Execution State**
```json
{
  "aggregation": {
    "completed": 1,
    "not_started": 1
  }
}
```

**5. Orchestrator Synthesis**
- Orchestrator reads both agent plan.json files
- Orchestrator creates `orchestrator-plan.json` (unified roadmap)
- Orchestrator updates `orchestrator.status` to "complete"

**6. Final State**
```json
{
  "status": "complete",
  "aggregation": {
    "completed": 2,
    "not_started": 0
  }
}
```

## Conclusion

The Sessions System provides a structured protocol for multi-agent coordination through immutable contracts (`communication.json` + `instructions.json`) and clear state ownership boundaries. Orchestrators delegate tasks via handoff prompts, agents execute autonomously and self-report status, and orchestrators aggregate results into synthesis documents.

**Maintenance Expectations:**
- communication.json is the runtime state authority - agents write status, orchestrator reads
- instructions.json is the task contract authority - defines what agents must do
- SESSION-INDEX.md is the historical record - tracks all sessions over time

**For Refactoring:**
- Preserve immutable fields (workorder_id, feature_name, file paths)
- Respect state ownership (agents own their status, orchestrator owns aggregation)
- Maintain file path conventions (absolute Windows paths with escaped backslashes)

**For Extension:**
- Add new agent types by extending communication.json agents[] array
- Add new session types by creating new workorder categories (WO-{NEW}-001)
- Add automation by building CLI tools that read/write communication.json programmatically

---

**Document Authority:** This resource sheet defines the architectural truth for the Sessions System. Code, JSON schemas, and implementation details must align with this specification.

**Last Updated:** 2026-01-04
**Version:** 1.0.0
**Maintained by:** coderef orchestrator
