# Architecture Reference - coderef-workflow

**Generated:** 2025-12-28
**Version:** 1.1.0

---

## Purpose

This document describes the **system architecture** of coderef-workflow, an MCP server that orchestrates the complete feature development lifecycle. It covers topology, design patterns, integration points, and architectural decisions.

## Overview

coderef-workflow is a **Python-based MCP server** that provides feature lifecycle management through 23 tools organized around a workorder-centric architecture. It integrates with coderef-context for code intelligence and coderef-docs for documentation generation.

**Architecture Style:** Event-driven microservice with async I/O
**Protocol:** Model Context Protocol (MCP) v1.0+
**Deployment:** Local process (not HTTP-based)

---

## What: System Topology

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Claude Code CLI                         │
│                    (MCP Client / User)                       │
└───────────────────────────┬─────────────────────────────────┘
                            │ MCP Protocol
                            │ (JSON-RPC over stdio)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   coderef-workflow                          │
│                     MCP Server                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │             server.py (Entry Point)                   │  │
│  │  - Tool registration (23 tools)                       │  │
│  │  - MCP protocol handling                              │  │
│  │  - Request routing                                    │  │
│  └───────────────┬──────────────────────────────────────┘  │
│                  │                                           │
│                  ▼                                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          tool_handlers.py (Dispatcher)                │  │
│  │  - 23 async handlers                                  │  │
│  │  - Input validation                                   │  │
│  │  - Response formatting                                │  │
│  └───┬────────────────┬─────────────────┬───────────────┘  │
│      │                │                 │                   │
│      ▼                ▼                 ▼                   │
│  ┌────────┐   ┌─────────────┐   ┌──────────┐              │
│  │  src/  │   │ generators/ │   │   JSON   │              │
│  │        │   │             │   │  Files   │              │
│  │ - exec │   │ - plan      │   │          │              │
│  │ - anal │   │ - analysis  │   │ context  │              │
│  │ - mcp  │   │             │   │ plan     │              │
│  │ - valid│   │             │   │ analysis │              │
│  └────────┘   └─────────────┘   └──────────┘              │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  │ MCP calls (optional)
                  ▼
┌─────────────────────────────────────────────────────────────┐
│              coderef-context MCP Server                      │
│  - coderef_scan (AST analysis)                              │
│  - coderef_query (dependency graphs)                        │
│  - coderef_patterns (code patterns)                         │
│  - coderef_impact (change impact)                           │
└─────────────────────────────────────────────────────────────┘
```

---

### Module Dependency Graph

```
server.py
├── tool_handlers.py ────────────┐
│   ├── src/validators.py        │
│   ├── src/plan_executor.py     │
│   │   └── reads: plan.json     │
│   ├── src/planning_analyzer.py │
│   │   ├── src/mcp_client.py ───┼──> coderef-context
│   │   └── reads: project files │
│   ├── src/mcp_client.py ────────┼──> coderef-context
│   ├── generators/plan_generator.py
│   │   ├── reads: context.json  │
│   │   ├── reads: analysis.json │
│   │   └── writes: plan.json    │
│   └── generators/analysis_generator.py
│       ├── reads: project files │
│       └── writes: analysis.json│
├── mcp (external library)       │
└── asyncio (Python stdlib)      │
                                 │
JSON Files <────────────────────┘
├── coderef/workorder/{feature}/
│   ├── context.json
│   ├── analysis.json
│   ├── plan.json
│   ├── communication.json (multi-agent)
│   └── DELIVERABLES.md
└── coderef/workorder-log.txt
```

---

### Planning Workflow System

The **Planning Workflow System** is a core subsystem responsible for generating comprehensive implementation plans from raw feature requirements. It orchestrates 6 specialized tools through a multi-phase workflow.

#### Architecture Components

```
Feature Idea
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│                  PHASE 1: CONTEXT GATHERING                  │
├─────────────────────────────────────────────────────────────┤
│  gather_context()                                           │
│  ├─ Interactive Q&A with user/agent                         │
│  ├─ Captures: description, goal, requirements, constraints  │
│  └─ Outputs: context.json                                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  PHASE 2: PROJECT ANALYSIS                   │
├─────────────────────────────────────────────────────────────┤
│  analyze_project_for_planning()                             │
│  ├─ Scans foundation docs (ARCHITECTURE, SCHEMA)            │
│  ├─ Extracts coding standards and patterns                  │
│  ├─ Calls coderef-context for dependency analysis           │
│  ├─ Identifies similar completed features (from archive)    │
│  └─ Outputs: analysis.json (30-60 sec analysis)             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  PHASE 3: PLAN GENERATION                    │
├─────────────────────────────────────────────────────────────┤
│  get_planning_template() → create_plan()                    │
│  ├─ Loads feature-implementation-planning-standard.json     │
│  ├─ Synthesizes context.json + analysis.json + template     │
│  ├─ Generates 10-section plan with phased tasks             │
│  ├─ Assigns workorder ID (WO-{FEATURE}-###)                 │
│  └─ Outputs: plan.json + DELIVERABLES.md template           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  PHASE 4: VALIDATION                         │
├─────────────────────────────────────────────────────────────┤
│  validate_implementation_plan()                             │
│  ├─ Scores plan quality (0-100)                             │
│  ├─ Checks 15-point quality checklist                       │
│  ├─ Identifies critical/major/minor issues                  │
│  └─ Outputs: validation results (approve if score >= 85)    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  PHASE 5: REVIEW REPORTING                   │
├─────────────────────────────────────────────────────────────┤
│  generate_plan_review_report()                              │
│  ├─ Transforms validation results to markdown               │
│  ├─ Creates human-readable review with grade                │
│  ├─ Provides actionable recommendations                     │
│  └─ Outputs: coderef/reviews/review-{name}-{date}.md        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
                Ready for Execution
             (execute_plan / align_plan)
```

#### Data Flow

1. **Inputs:**
   - User requirements (via gather_context)
   - Project codebase (scanned by analyze_project_for_planning)
   - Planning template (feature-implementation-planning-standard.json)

2. **Intermediate Artifacts:**
   - `context.json` - Feature requirements, goals, constraints
   - `analysis.json` - Project patterns, standards, tech stack
   - `plan.json` - 10-section implementation plan with tasks

3. **Outputs:**
   - Validated plan ready for execution
   - Review report with quality score
   - DELIVERABLES.md template for metrics tracking

#### Tool Integration

```python
# Planning tools call coderef-context for code intelligence
analyze_project_for_planning()
  └─> mcp_client.call("coderef_scan", {"project_path": "..."})
      └─> Returns: dependency graph, API endpoints, entities

# Results injected into plan.json section 3: CURRENT_STATE_ANALYSIS
plan.json["3_current_state_analysis"]["existing_components"] = scan_results
```

#### Quality Assurance

The planning system enforces quality through:
- **Template Compliance:** All plans follow 10-section structure
- **Validation Scoring:** 15-point checklist (completeness, clarity, actionability)
- **Iterative Refinement:** AI agents refine plans until score >= 85
- **Review Reports:** Markdown reports for human review

#### Performance Characteristics

| Phase | Tool | Typical Duration |
|-------|------|------------------|
| 1 | gather_context | 30-60 seconds |
| 2 | analyze_project_for_planning | 30-60 seconds |
| 3 | create_plan | 10-60 seconds |
| 4 | validate_implementation_plan | 2-5 seconds |
| 5 | generate_plan_review_report | 1-2 seconds |
| **Total** | **Full workflow** | **~2-3 minutes** |

**Note:** Phase 2 and 3 can be parallelized in future versions for ~50% speedup.

---

## Why: Design Decisions

### 1. MCP Protocol Over REST/GraphQL

**Chosen:** Model Context Protocol (MCP)
**Rejected:** REST API, GraphQL, gRPC

**Reasons:**
- **AI-First Design:** MCP is specifically designed for AI agent interactions
- **Tool Discovery:** Automatic schema discovery via `list_tools()`
- **Type Safety:** JSON Schema validation for all inputs/outputs
- **Simplicity:** Stdio-based communication (no HTTP server needed)
- **Async Native:** Built-in async/await support

**Trade-offs:**
- ✅ Perfect for AI agents
- ❌ Not suitable for web browsers
- ✅ No network overhead (local process)
- ❌ Limited to single-machine deployment

---

### 2. Workorder-Centric Architecture

**Chosen:** Every feature gets a unique workorder ID (WO-{FEATURE}-###)
**Rejected:** Simple feature directories without tracking

**Reasons:**
- **Audit Trail:** Complete history of all features across projects
- **Multi-Agent Coordination:** Unique IDs prevent task conflicts
- **Traceability:** Link features to git commits, PRs, documentation
- **Recovery:** Easy to find and restore archived features

**Implementation:**
```
coderef/workorder/
├── execute-plan-rename/
│   ├── context.json
│   ├── analysis.json
│   ├── plan.json (contains workorder_id: "WO-EXECUTE-PLAN-RENAME-001")
│   └── DELIVERABLES.md
└── ...

coderef/workorder-log.txt:
WO-EXECUTE-PLAN-RENAME-001 | coderef-workflow | Rename execute_plan → align_plan | 2025-12-27T15:48:00Z
```

---

### 3. JSON Files Over Database

**Chosen:** File-based JSON storage
**Rejected:** SQLite, PostgreSQL, MongoDB

**Reasons:**
- **Version Control:** JSON files tracked in git for complete history
- **Portability:** Works across all platforms without dependencies
- **Transparency:** Human-readable for debugging
- **Backup:** Automatic via git commits
- **No Setup:** No database installation or migrations

**Trade-offs:**
- ✅ Simple and transparent
- ❌ No ACID transactions (mitigated: single-file atomic writes)
- ✅ Git-trackable
- ❌ No complex queries (mitigated: targeted file reads)

---

### 4. Async Throughout

**Chosen:** All functions async/await
**Rejected:** Synchronous with threading

**Reasons:**
- **MCP Requirement:** MCP protocol requires async tool handlers
- **Performance:** Non-blocking I/O for file operations
- **Integration:** Async calls to coderef-context MCP server
- **Consistency:** Single concurrency model throughout codebase

**Pattern:**
```python
# All tool handlers are async
async def handle_create_plan(arguments: dict) -> list[TextContent]:
    # Non-blocking file reads
    context = await read_json_async(context_path)

    # Non-blocking MCP calls
    analysis = await mcp_client.call_tool("coderef_scan", {...})

    # Non-blocking file writes
    await write_json_async(plan_path, plan)
```

---

### 5. Graceful Fallbacks

**Chosen:** Degrade gracefully when coderef-context unavailable
**Rejected:** Hard dependency requiring coderef-context

**Reasons:**
- **Resilience:** System works even if coderef-context is down
- **Independence:** Core functionality doesn't require external services
- **User Experience:** Users aren't blocked by missing dependencies

**Implementation:**
```python
try:
    # Try code intelligence
    result = await mcp_client.call_tool("coderef_scan", {...})
    analysis = parse_coderef_result(result)
except ConnectionError:
    # Fallback to filesystem scan
    logger.warning("coderef-context unavailable, using filesystem scan")
    analysis = await filesystem_scan(project_path)
```

---

## When: Data Flow Patterns

### Pattern 1: Feature Planning Flow

```
User initiates: /create-workorder
                    ↓
┌─────────────────────────────────────────┐
│ 1. gather_context                       │
│    Input: Interactive Q&A               │
│    Output: context.json                 │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│ 2. coderef_foundation_docs              │
│    Input: project_path                  │
│    Output: ARCHITECTURE.md, SCHEMA.md   │
│           API.md, COMPONENTS.md         │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│ 3. analyze_project_for_planning         │
│    Input: project_path                  │
│    Process:                             │
│      - Call coderef-context (if avail)  │
│      - Scan filesystem (fallback)       │
│    Output: analysis.json                │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│ 4. create_plan                          │
│    Input: context.json, analysis.json   │
│    Process:                             │
│      - Generate 10-section plan         │
│      - Add workorder_id to META         │
│    Output: plan.json, DELIVERABLES.md   │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│ 5. validate_implementation_plan         │
│    Input: plan.json                     │
│    Output: Score (0-100), issues list   │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│ 6. execute_plan (/align-plan)           │
│    Input: plan.json                     │
│    Output: TodoWrite task list          │
│    Side effect: Tasks printed to CLI    │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│ 7. Git commit (all planning artifacts)  │
└─────────────────────────────────────────┘
```

---

### Pattern 2: Multi-Agent Coordination

```
create_plan() with multi_agent: true
                    ↓
┌─────────────────────────────────────────┐
│ generate_agent_communication            │
│   Input: plan.json                      │
│   Output: communication.json            │
│   Contains:                             │
│     - Tasks array (all tasks)           │
│     - Agent assignments (1-N)           │
│     - Forbidden files per agent         │
│     - Progress tracking                 │
└─────────────────┬───────────────────────┘
                  ↓
          ┌───────┴───────┐
          ▼               ▼
┌──────────────┐  ┌──────────────┐
│  Agent 1     │  │  Agent 2     │
│              │  │              │
│ assign_agent │  │ assign_agent │
│ _task()      │  │ _task()      │
└──────┬───────┘  └──────┬───────┘
       │                 │
       │ Updates         │ Updates
       │ communication   │ communication
       │ .json.tasks     │ .json.tasks
       │                 │
       ▼                 ▼
┌──────────────────────────────┐
│ verify_agent_completion      │
│   - Check git diffs          │
│   - Validate success criteria│
│   - Update agent status      │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│ aggregate_agent_deliverables │
│   - Sum LOC across agents    │
│   - Merge commit counts      │
│   - Calculate total time     │
└──────────────────────────────┘
```

---

### Pattern 3: Task Status Tracking

```
execute_plan() generates TodoWrite list
                    ↓
Agent implements task IMPL-001
                    ↓
┌─────────────────────────────────────────┐
│ update_task_status(IMPL-001,            │
│                    "in_progress")        │
│   Process:                              │
│     - Read plan.json                    │
│     - Update section 6 task status      │
│     - Update section 9 checkbox         │
│     - Recalculate progress %            │
│     - Add timestamp                     │
│     - Write plan.json                   │
└─────────────────┬───────────────────────┘
                  ↓
       Task implementation work...
                  ↓
┌─────────────────────────────────────────┐
│ update_task_status(IMPL-001,            │
│                    "completed")          │
│   Process: (same as above)              │
│   Result: progress.percent incremented  │
└─────────────────────────────────────────┘
```

---

## How: Key Architectural Patterns

### 1. Dispatcher Pattern (Tool Handlers)

**Purpose:** Route tool calls to appropriate handlers

**Implementation:**
```python
# tool_handlers.py
TOOL_HANDLERS = {
    'gather_context': handle_gather_context,
    'create_plan': handle_create_plan,
    'execute_plan': handle_execute_plan,
    # ... 20 more
}

async def route_tool_call(name: str, arguments: dict) -> list[TextContent]:
    """O(1) lookup and dispatch"""
    handler = TOOL_HANDLERS.get(name)
    if not handler:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

    return await handler(arguments)
```

**Benefits:**
- O(1) lookup performance
- Easy to add new tools
- Testable in isolation
- Explicit mapping

---

### 2. Generator Pattern (Plan/Analysis Creation)

**Purpose:** Separate data generation logic from handlers

**Implementation:**
```python
# generators/plan_generator.py
class PlanGenerator:
    async def generate_plan(self, context, analysis) -> dict:
        """Generate 10-section plan from inputs"""
        plan = {}
        plan["META_DOCUMENTATION"] = self._build_meta(context)
        plan["0_PREPARATION"] = self._build_preparation(analysis)
        plan["1_EXECUTIVE_SUMMARY"] = await self._generate_summary(context)
        # ... 7 more sections
        return plan
```

**Benefits:**
- Reusable across different handlers
- Easier to test generation logic
- Clear separation of concerns
- Can swap generators without changing handlers

---

### 3. Async Client Pattern (MCP Integration)

**Purpose:** Call other MCP servers (coderef-context) asynchronously

**Implementation:**
```python
# src/mcp_client.py
class MCPClient:
    def __init__(self, server_name: str):
        self.server_name = server_name

    async def call_tool(self, tool_name: str, arguments: dict) -> dict:
        """Non-blocking MCP tool call"""
        # Connect to MCP server via stdio
        # Send JSON-RPC request
        # Await response
        # Parse and return
```

**Benefits:**
- Non-blocking calls
- Consistent interface for all MCP servers
- Error handling in one place
- Easy to mock for testing

---

### 4. Validation-First Pattern

**Purpose:** Validate all inputs before processing

**Implementation:**
```python
async def handle_create_plan(arguments: dict) -> list[TextContent]:
    # Step 1: Validate inputs
    project_path = arguments.get("project_path")
    if not project_path or not Path(project_path).exists():
        return error_response("Invalid project_path")

    feature_name = arguments.get("feature_name")
    if not validate_feature_name(feature_name):
        return error_response("Invalid feature_name format")

    # Step 2: Process (only if validation passed)
    result = await generate_plan(project_path, feature_name)
    return success_response(result)
```

**Benefits:**
- Fail fast with clear error messages
- Consistent validation across all tools
- Easier debugging
- Better user experience

---

## Examples

### Example 1: Adding Code Intelligence to a Tool

```python
# tool_handlers.py
async def handle_my_tool(arguments: dict) -> list[TextContent]:
    """Tool that benefits from code intelligence"""

    # Initialize MCP client
    from src.mcp_client import MCPClient
    mcp = MCPClient("coderef-context")

    try:
        # Try to get code intelligence
        scan_result = await mcp.call_tool("coderef_scan", {
            "project_path": arguments["project_path"],
            "languages": ["py"],
            "use_ast": True
        })

        # Use rich code intelligence
        functions = scan_result.get("elements", {}).get("functions", [])
        analysis = f"Found {len(functions)} functions"

    except ConnectionError:
        # Graceful fallback
        logger.warning("coderef-context unavailable")
        analysis = "Code intelligence unavailable, using basic analysis"

    return [TextContent(type="text", text=analysis)]
```

---

### Example 2: Error Handling Pattern

```python
async def handle_tool(arguments: dict) -> list[TextContent]:
    """Consistent error handling"""
    try:
        # Validate
        if not valid_input(arguments):
            raise ValueError("Invalid input")

        # Process
        result = await do_work(arguments)

        # Success response
        return [TextContent(type="text", text=json.dumps(result))]

    except ValueError as e:
        # Validation error
        return [TextContent(type="text", text=f"Validation error: {e}")]

    except FileNotFoundError as e:
        # File not found
        return [TextContent(type="text", text=f"File not found: {e}")]

    except Exception as e:
        # Unexpected error
        logger.error(f"Unexpected error in tool: {e}", exc_info=True)
        return [TextContent(type="text", text=f"Internal error: {e}")]
```

---

## Performance Considerations

### Tool Performance Targets

| Tool | Target Time | Actual (Typical) |
|------|-------------|------------------|
| `gather_context` | < 1s | 0.5s (I/O only) |
| `analyze_project_for_planning` | < 30s | 5-30s (depends on project size) |
| `create_plan` | < 60s | 10-60s (includes LLM call) |
| `validate_implementation_plan` | < 5s | 2-5s (JSON validation) |
| `execute_plan` | < 1s | 0.3s (JSON read + parse) |
| `update_task_status` | < 1s | 0.2s (JSON read/write) |

### Optimization Strategies

1. **Caching:** Analysis results cached in analysis.json (reused by create_plan)
2. **Async I/O:** All file operations non-blocking
3. **Lazy Loading:** Only load JSON files when needed
4. **Minimal Dependencies:** Few external dependencies = fast startup

---

## Security Considerations

### File System Access

- Tools can read/write to `coderef/workorder/` and `coderef/archived/` only
- Validation ensures paths stay within project boundaries
- No execution of user-provided code

### Input Validation

- All inputs validated before processing
- Feature names: Alphanumeric + hyphens/underscores only
- File paths: Must be absolute, must exist
- JSON schemas: Validated against jsonschema

### External Calls

- MCP calls to coderef-context are optional (graceful fallback)
- No network requests (all local)
- No execution of external binaries

---

## Deployment Architecture

### Local Deployment (Current)

```
User Machine:
├── Claude Code CLI (MCP Client)
├── coderef-workflow MCP Server (Python process)
├── coderef-context MCP Server (Node.js process)
└── coderef-docs MCP Server (Python process)

Communication: stdio (JSON-RPC)
Data Storage: Local filesystem (coderef/workorder/)
```

### Future: Multi-User Deployment (Potential)

```
Shared Server:
├── MCP Gateway (HTTP → stdio adapter)
├── coderef-workflow instances (per project)
├── Shared coderef/workorder/ (with access control)
└── Git repository (for version control)

Clients:
└── Claude Code CLI (HTTP MCP client)
```

---

## References

- **API.md** - Complete tool reference
- **SCHEMA.md** - Data models and validation
- **COMPONENTS.md** - Module structure
- **CLAUDE.md** - Complete AI context documentation
- **MCP Specification** - https://modelcontextprotocol.io

---

**For AI agents:** coderef-workflow follows a clear architectural pattern: MCP protocol → Dispatcher → Handlers → Generators → JSON files. All operations are async, all inputs validated, all external calls graceful. When extending, follow established patterns and maintain backward compatibility.
