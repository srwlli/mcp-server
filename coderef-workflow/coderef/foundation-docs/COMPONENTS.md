# Components Reference - coderef-workflow

**Generated:** 2025-12-28
**Version:** 1.1.0

---

## Purpose

This document describes the **module and package architecture** of coderef-workflow. Since this is a backend MCP server (not a UI application), "components" refer to Python modules, generators, and tool handlers rather than UI components.

## Overview

coderef-workflow is organized into **4 primary module groups**:

1. **Core Modules** (`server.py`, `src/`) - MCP server and tool implementations
2. **Generators** (`generators/`) - Plan and analysis generation logic
3. **Tool Handlers** (`tool_handlers.py`) - MCP tool request/response handlers
4. **Utilities** (`validators.py`, `mcp_client.py`) - Shared utilities

---

## What: Module Structure

### 1. Core Modules

#### `server.py`

MCP server entry point and tool registration.

**Responsibilities:**
- Initialize MCP server with `@server` decorator
- Register all 23 tools with schema definitions
- Route tool calls to `tool_handlers.py`
- Handle server lifecycle (startup/shutdown)

**Key Exports:**
```python
from mcp.server import Server
from mcp.types import Tool, TextContent

# MCP server instance
app = Server("coderef-workflow")

# Tool definitions
TOOLS = [
    Tool(name="gather_context", description="...", inputSchema={...}),
    Tool(name="create_plan", description="...", inputSchema={...}),
    # ... 21 more tools
]

# Tool call handler
@app.call_tool()
async def handle_tool_call(name: str, arguments: dict) -> list[TextContent]:
    """Route tool calls to appropriate handlers"""
```

**Dependencies:**
- `tool_handlers.py` - For actual tool implementation
- `mcp` library - MCP protocol implementation
- `asyncio` - Async runtime

---

#### `tool_handlers.py`

Implements all 23 MCP tool handlers.

**Responsibilities:**
- Handle tool requests from `server.py`
- Validate input parameters
- Coordinate with generators and utilities
- Return formatted MCP responses

**Structure:**
```python
# Handler map (dispatcher pattern)
TOOL_HANDLERS = {
    'gather_context': handle_gather_context,
    'analyze_project_for_planning': handle_analyze_project,
    'create_plan': handle_create_plan,
    'execute_plan': handle_execute_plan,  # Note: maps to /align-plan command
    # ... 19 more handlers
}

# Individual handlers
async def handle_gather_context(arguments: dict) -> list[TextContent]:
    """Gather feature requirements and constraints"""

async def handle_create_plan(arguments: dict) -> list[TextContent]:
    """Generate 10-section implementation plan"""

# ... more handlers
```

**Key Patterns:**
- All handlers are `async def`
- Input validation via `validators.py`
- Returns `list[TextContent]` for MCP protocol
- Error handling with try/except and graceful fallbacks

---

### 2. Generators

#### `generators/plan_generator.py`

Generates plan.json from context and analysis.

**Responsibilities:**
- Read context.json and analysis.json
- Generate 10-section plan structure
- Populate with LLM-generated content (via Claude API)
- Validate plan schema
- Save to `coderef/workorder/{feature}/plan.json`

**Key Classes:**
```python
class PlanGenerator:
    """Generate implementation plans from context"""

    async def generate_plan(
        self,
        project_path: str,
        feature_name: str,
        workorder_id: Optional[str] = None
    ) -> dict:
        """
        Generate complete 10-section plan

        Returns:
            dict: plan.json structure with all sections populated
        """
```

**Generation Flow:**
1. Load context.json and analysis.json
2. Build prompt with project context
3. Call LLM to generate plan sections
4. Parse and structure response into 10 sections
5. Validate against schema
6. Add workorder_id to META_DOCUMENTATION
7. Save plan.json

---

#### `generators/analysis_generator.py`

Analyzes project for planning context.

**Responsibilities:**
- Scan project directory structure
- Detect tech stack and frameworks
- Identify coding patterns
- Find similar features in `coderef/archived/`
- Generate analysis.json

**Key Classes:**
```python
class AnalysisGenerator:
    """Analyze project for implementation planning"""

    async def analyze_project(
        self,
        project_path: str,
        feature_name: Optional[str] = None
    ) -> dict:
        """
        Analyze project structure and patterns

        Returns:
            dict: analysis.json structure
        """
```

**Analysis Steps:**
1. Scan for foundation docs (ARCHITECTURE.md, SCHEMA.md, etc.)
2. Detect tech stack from package files (pyproject.toml, package.json)
3. Identify coding standards from existing code
4. Find key architectural patterns
5. Search archived features for similar implementations
6. Identify gaps and risks

---

### 3. Source Modules (`src/`)

#### `src/plan_executor.py`

Executes implementation plans and generates task lists.

**Responsibilities:**
- Read plan.json
- Extract tasks from section 6 (implementation phases)
- Generate TodoWrite-formatted task list
- Print tasks to CLI terminal

**Key Functions:**
```python
async def execute_plan(
    project_path: str,
    feature_name: str
) -> dict:
    """
    Generate TodoWrite task list from plan.json

    Returns:
        dict: {
            "feature_name": str,
            "workorder_id": str,
            "task_count": int,
            "tasks": list[dict]  # TodoWrite format
        }
    """
```

**Task Extraction Logic:**
1. Load plan.json
2. Parse section 6 (implementation phases)
3. Extract all tasks with IDs, descriptions
4. Convert to TodoWrite format (content, activeForm, status)
5. Return structured task list

---

#### `src/planning_analyzer.py`

Project analysis for planning workflow.

**Responsibilities:**
- Call coderef-context for code intelligence (if available)
- Fallback to filesystem analysis if coderef-context unavailable
- Generate project analysis report

**Integration Points:**
- **With coderef-context:** Calls `coderef_scan`, `coderef_patterns` tools
- **Without coderef-context:** Manual file scanning and pattern detection

---

#### `src/mcp_client.py`

Async client for calling other MCP servers (e.g., coderef-context).

**Responsibilities:**
- Connect to coderef-context MCP server
- Call tools asynchronously
- Handle connection errors gracefully
- Return formatted responses

**Key Classes:**
```python
class MCPClient:
    """Async client for inter-MCP communication"""

    async def call_tool(
        self,
        tool_name: str,
        arguments: dict
    ) -> dict:
        """
        Call tool on remote MCP server

        Returns:
            dict: Tool response

        Raises:
            ConnectionError: If MCP server unavailable
        """
```

---

#### `src/validators.py`

Input validation for all tools.

**Responsibilities:**
- Validate feature names (alphanumeric, hyphens, underscores)
- Validate workorder IDs (WO-{FEATURE}-### format)
- Validate file paths (absolute, exists)
- Validate JSON schemas

**Key Functions:**
```python
def validate_feature_name(name: str) -> bool:
    """Validate feature name format"""
    return bool(re.match(r'^[a-z0-9_-]+$', name))

def validate_workorder_id(wo_id: str) -> bool:
    """Validate workorder ID format"""
    return bool(re.match(r'^WO-[A-Z0-9-]+-\d{3}$', wo_id))

def validate_plan_schema(plan: dict) -> list[str]:
    """
    Validate plan.json against schema

    Returns:
        list[str]: Validation error messages (empty if valid)
    """
```

---

## Why: Design Decisions

### Module Separation
**Chosen:** Separate modules for generators, handlers, utilities
**Rejected:** Monolithic server.py with all logic

**Reasons:**
- **Testability:** Each module independently testable
- **Reusability:** Generators reusable in other contexts
- **Clarity:** Clear separation of concerns
- **Maintainability:** Easy to locate and modify specific functionality

### Async Throughout
**Chosen:** All functions async/await
**Rejected:** Synchronous with threading

**Reasons:**
- **MCP Requirement:** MCP protocol requires async handlers
- **Performance:** Non-blocking I/O for file operations
- **Integration:** Async client for coderef-context calls
- **Consistency:** All tool handlers follow same pattern

### Handler Dispatch Pattern
**Chosen:** Dictionary-based dispatcher in tool_handlers.py
**Rejected:** If/elif chain or decorator routing

**Reasons:**
- **Performance:** O(1) lookup vs O(n) if/elif
- **Extensibility:** Easy to add new handlers
- **Testability:** Can test handlers independently
- **Clarity:** Explicit mapping visible at top of file

---

## When: Module Usage Patterns

### Tool Call Flow

```
1. MCP Request arrives at server.py
   “
2. server.py routes to tool_handlers.py via TOOL_HANDLERS dict
   “
3. Handler validates input via src/validators.py
   “
4. Handler calls generator (e.g., plan_generator.py)
   “
5. Generator may call coderef-context via src/mcp_client.py
   “
6. Generator returns result
   “
7. Handler formats as TextContent
   “
8. Response returned to MCP client
```

### Plan Generation Flow

```
1. handle_create_plan() called
   “
2. Load context.json and analysis.json
   “
3. Call PlanGenerator.generate_plan()
   “
4. PlanGenerator builds LLM prompt
   “
5. Call Claude API for plan generation
   “
6. Parse response into 10 sections
   “
7. Validate schema via validators.py
   “
8. Add workorder_id to META_DOCUMENTATION
   “
9. Save plan.json
   “
10. Return success response
```

---

## Examples

### Example 1: Adding a New Tool

**Step 1:** Define tool in `server.py`
```python
TOOLS.append(
    Tool(
        name="my_new_tool",
        description="Does something useful",
        inputSchema={
            "type": "object",
            "properties": {
                "param": {"type": "string", "description": "..."}
            },
            "required": ["param"]
        }
    )
)
```

**Step 2:** Add handler in `tool_handlers.py`
```python
async def handle_my_new_tool(arguments: dict) -> list[TextContent]:
    """Handle my_new_tool requests"""
    # Validate input
    param = arguments.get("param")
    if not param:
        return [TextContent(type="text", text="Error: param required")]

    # Do work
    result = await do_something(param)

    # Return response
    return [TextContent(type="text", text=f"Success: {result}")]

# Add to dispatcher
TOOL_HANDLERS['my_new_tool'] = handle_my_new_tool
```

**Step 3:** Add to documentation
- Update API.md with tool parameters/response
- Update CLAUDE.md tool count
- Add slash command if needed

---

### Example 2: Calling coderef-context from a Tool

```python
# In tool handler
from src.mcp_client import MCPClient

async def handle_my_tool(arguments: dict) -> list[TextContent]:
    """Tool that needs code intelligence"""

    # Initialize MCP client
    client = MCPClient("coderef-context")

    try:
        # Call coderef-context tool
        result = await client.call_tool("coderef_scan", {
            "project_path": arguments["project_path"],
            "languages": ["ts", "tsx", "js", "jsx"]
        })

        # Use result
        code_intel = result["elements"]

    except ConnectionError:
        # Graceful fallback if coderef-context unavailable
        logger.warning("coderef-context unavailable, using filesystem scan")
        code_intel = await filesystem_scan(arguments["project_path"])

    return [TextContent(type="text", text=f"Found {len(code_intel)} elements")]
```

---

## Dependencies

### Internal Dependencies

```
server.py
     tool_handlers.py
        src/validators.py
        src/plan_executor.py
        src/planning_analyzer.py
        src/mcp_client.py
        generators/plan_generator.py
        generators/analysis_generator.py
     mcp (external library)
```

### External Dependencies

- **mcp** (v1.0+) - Model Context Protocol implementation
- **asyncio** - Async runtime
- **jsonschema** (v4.0+) - JSON validation
- **pathlib** - Path operations
- **typing** - Type hints

---

## Testing

### Test Structure

```
tests/
   test_plan_executor.py        # Tests for src/plan_executor.py
   test_planning_analyzer.py    # Tests for src/planning_analyzer.py
   test_mcp_client.py            # Tests for src/mcp_client.py
   test_validators.py            # Tests for src/validators.py
   test_plan_generator.py        # Tests for generators/plan_generator.py
   test_analysis_generator.py    # Tests for generators/analysis_generator.py
```

### Testing Patterns

**Unit Tests:**
```python
import pytest
from src.validators import validate_feature_name

def test_validate_feature_name_valid():
    assert validate_feature_name("my-feature") == True
    assert validate_feature_name("feature_123") == True

def test_validate_feature_name_invalid():
    assert validate_feature_name("My Feature!") == False
    assert validate_feature_name("feature@123") == False
```

**Async Tests:**
```python
import pytest
from src.plan_executor import execute_plan

@pytest.mark.asyncio
async def test_execute_plan():
    result = await execute_plan(
        project_path="/test/project",
        feature_name="test-feature"
    )
    assert result["task_count"] > 0
    assert "workorder_id" in result
```

---

## References

- **API.md** - MCP tool endpoints that call these modules
- **SCHEMA.md** - Data structures these modules work with
- **ARCHITECTURE.md** - Overall system design
- **CLAUDE.md** - Complete AI context documentation

---

**For AI agents:** coderef-workflow is organized into focused modules with clear responsibilities. When adding features, follow the established patterns: async throughout, validation first, graceful fallbacks. Test each module independently before integration.
