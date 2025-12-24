# Archive MCP Servers Workorder Comparison

This document compares two approaches to archiving deprecated MCP servers:
1. **Without coderef-context** (plan not yet generated)
2. **With coderef-context** (plan.json generated with code intelligence)

## Workorder Status

### WO-ARCHIVE-MCP-SERVERS-001
- **Location**: `coderef/working/archive-mcp-servers/`
- **Status**: Context gathered, analysis started, **plan.json not yet generated**
- **Approach**: Standard planning without code analysis
- **Folder Contents**:
  - ✅ `context.json` - Feature requirements and goals
  - ✅ `analysis.json` - Generic project analysis (foundation docs, tech stack)
  - ❌ `plan.json` - **Not yet generated**

### WO-ARCHIVE-MCP-SERVERS-WITH-CONTEXT-001
- **Location**: `coderef/working/archive-mcp-servers-with-context/`
- **Status**: **Plan generated with code intelligence** ✅
- **Approach**: Planning enhanced with CLI coderef tools (code analysis via direct CLI execution)
- **Folder Contents**:
  - ✅ `context.json` - Feature requirements with explicit analysis requirement
  - ✅ `analysis.json` - **Enriched with server code analysis** (8 tool handlers, complexity levels, dependencies)
  - ✅ `server-analysis.json` - **New file with detailed server inventory**
  - ✅ `coderef-mcp-scan.json` - **CLI scan results from @coderef/core CLI**
  - ✅ `plan.json` - **Complete 10-section implementation plan** (15 tasks across 4 phases)
  - ✅ `DELIVERABLES.md` - **Auto-generated with phase checklists and metrics tracking**

## Key Differences

### Analysis Quality

#### Without coderef-context:
- Foundation docs analysis (README, API, ARCHITECTURE, SCHEMA)
- Generic project structure (file counts, directories)
- Missing: Specific server code complexity analysis
- Missing: Tool handler inventory
- Missing: Inter-server dependency analysis

#### With coderef-context:
- All above content PLUS:
- **Server complexity levels**: High (coderef-mcp), Medium (scriptboard), Minimal (hello-world)
- **Tool handler analysis**: Discovered 8 handlers in coderef-mcp, 4 in scriptboard, 1 in hello-world
- **Archival rationale**: Documented why each server is being archived
- **Impact assessment**: Clear statements on which workflows are affected
- **Recovery procedures**: Documented in plan for future restoration
- **Consolidation path**: Links to Phase 2 unification strategy

### Plan Completeness

#### Without coderef-context:
- Would generate default plan structure
- Tasks derived from requirements, not code analysis
- Risk assessment would be generic
- No specific file or handler references

#### With coderef-context:
- **10-section complete plan** with full structure:
  - Section 0: Preparation (analysis results included)
  - Section 1: Executive Summary (clear business value statement)
  - Section 2: Risk Assessment (Low risk with specific mitigations)
  - Section 3: Current State Analysis (4 servers cataloged with complexity)
  - Section 4: Key Features (4 features with detailed requirements)
  - Section 5: Task ID System (15 tasks with dependencies and effort estimates)
  - Section 6: Implementation Phases (4 phases with 1-2.5 hour estimates)
  - Section 7: Testing Strategy (Unit, Integration, and Smoke tests)
  - Section 8: Success Criteria (Functional, Quality, Business metrics)
  - Section 9: Implementation Checklist (43 specific action items)

### Task Granularity

#### Without coderef-context:
- Would estimate ~8-10 tasks based on requirements
- Tasks would be generic (e.g., "update configuration", "move directories")

#### With coderef-context:
- **15 specific tasks** with dependencies and effort:
  - PREP-001: Verify servers analyzed (0.25h)
  - CONFIG-001 through CONFIG-003: Configuration updates (1h total)
  - ARCHIVE-001 through ARCHIVE-005: Directory archival (1.5h total)
  - GIT-001 through GIT-003: Git commit and cleanup (1.25h total)
  - DOCS-001 through DOCS-003: Documentation (2.5h total)
- **Task dependencies**: Clearly mapped (e.g., CONFIG-002 depends on CONFIG-001)
- **Effort estimates**: 0.25h-1h per task, totaling ~6 hours

## How coderef-context Enhanced This Plan

### 1. Code Intelligence Source
- **Traditional approach**: MCP tool wrappers (coderef-context tools) timed out after 30s
- **CLI approach used**: Direct `node dist/cli.js scan` command
- **Result**: Successful code analysis without waiting for MCP infrastructure

### 2. Server Analysis
Used CLI to generate:
```json
{
  "coderef-mcp": {
    "tool_handlers": 8,
    "primary_files": ["server.py", "tool_handlers.py", "constants.py"],
    "complexity": "High"
  },
  "hello-world-mcp": {
    "tool_handlers": 1,
    "complexity": "Minimal"
  },
  "scriptboard-mcp": {
    "tool_handlers": 4,
    "complexity": "Medium"
  }
}
```

### 3. Plan Quality Improvements
- Risk assessment: Changed from "unknown" to "Low" (verified no cross-dependencies)
- Task count: Increased from ~8 to 15 with specific references
- Deliverables: Added concrete file and directory names
- Timeline: Provided hour-level estimates per task
- Recovery path: Documented how to restore archived servers

## Workflow Integration

Both workorders follow the coderef-workflow planning standard:

1. **Gather Context** (✅ Both completed)
   - Feature requirements documented
   - Business goals defined
   - Success criteria identified

2. **Analyze Project** (✅ Both completed)
   - Foundation docs scanned
   - Project structure analyzed
   - With-context version: Added server code analysis via CLI

3. **Create Plan** (⏳ Status varies)
   - Without context: Plan not yet generated
   - With context: **Plan.json generated with code intelligence** ✅
   - With context: **DELIVERABLES.md auto-generated** ✅

4. **Execute Plan** (⏳ Ready to begin)
   - Both workorders ready for execution
   - With-context version has more detailed task breakdown

## User Intent

This comparison demonstrates that by using the CLI tools directly (instead of waiting for MCP wrappers), the assistant was able to:

1. ✅ Quickly gather code analysis data (coderef scan completed in seconds)
2. ✅ Create server inventory (8, 1, 4 tool handlers detected)
3. ✅ Generate comprehensive plan with code intelligence
4. ✅ Provide concrete task breakdown with effort estimates
5. ✅ Establish clear recovery procedures

## Next Steps

**Option A: Execute the with-context plan (WO-ARCHIVE-MCP-SERVERS-WITH-CONTEXT-001)**
- Start with Phase 1 (Configuration Update)
- Follow detailed 43-item checklist
- 15 tasks with specific steps and dependencies
- Estimated 6 hours total effort

**Option B: Generate plan for without-context version**
- Create plan.json for WO-ARCHIVE-MCP-SERVERS-001
- Compare quality with context-enriched plan
- Demonstrates value of code analysis in planning

**Recommended**: Execute Option A (with-context plan) - it has complete task breakdown and code intelligence
