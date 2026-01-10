# MCP Integration Guide - coderef-docs + coderef-context

**Version:** 1.0.0
**Feature:** WO-INTEGRATING-CODEREF-CONTEXT-001
**Last Updated:** 2026-01-10

---

## Purpose

This guide explains how coderef-docs integrates with coderef-context MCP tools for enhanced code intelligence during documentation generation.

**Key Innovation:** Orchestrated MCP tool workflow where Claude acts as the coordinator between two MCP servers.

---

## Architecture Pattern

### Why MCP Servers Can't Call Each Other

MCP (Model Context Protocol) servers are designed to be called by AI agents like Claude, not by other MCP servers. Each server:
- Runs as an independent process
- Communicates via stdio (standard input/output)
- Has no knowledge of other MCP servers

**Therefore, direct MCP-to-MCP calls are not possible.**

### The Orchestration Pattern

Instead, we use **Claude as the orchestrator**:

```
User Request: "Generate foundation docs"
           ↓
Claude calls: mcp__coderef_docs__generate_foundation_docs
           ↓
coderef-docs responds: "Instructions + Recommendation to call coderef_scan"
           ↓
Claude calls: mcp__coderef_context__coderef_scan (generates .coderef/ data)
           ↓
Claude calls: mcp__coderef_docs__generate_individual_doc (reads .coderef/ data)
           ↓
Foundation docs generated with real code intelligence!
```

---

## Implementation Details

### 1. Reading .coderef/ Data (Not Generating It)

**File:** `generators/coderef_foundation_generator.py`

```python
def _load_coderef_data(self) -> Optional[Dict[str, Any]]:
    """
    Load .coderef/index.json and graph.json if available.

    MCP Integration Pattern:
    - This method reads existing .coderef/ data (never generates it)
    - If data missing, Claude should call mcp__coderef_context__coderef_scan
    - After MCP tool call, this method reads the newly generated files
    - No direct MCP-to-MCP calls (not supported by protocol)
    """
    index_path = self.project_path / '.coderef' / 'index.json'

    if not index_path.exists():
        logger.info(
            "No .coderef/index.json found - using regex fallback. "
            "For better accuracy, use mcp__coderef_context__coderef_scan first."
        )
        return None

    # Read existing data...
    elements = json.loads(index_path.read_text(encoding='utf-8'))
    # ...
```

**Key Points:**
- ✅ Reads existing files only
- ✅ Never calls subprocess or CLI
- ✅ Provides clear logging when data missing
- ✅ Falls back to regex detection

### 2. Providing MCP Integration Instructions

**File:** `tool_handlers.py`

```python
async def handle_generate_foundation_docs(arguments: dict):
    # ...
    result += "MCP INTEGRATION (coderef-context):\n"
    result += "- For better accuracy, call mcp__coderef_context__coderef_scan before generation\n"
    result += "- Generator will read .coderef/index.json after MCP scan completes\n"
    result += "- No direct MCP-to-MCP calls (use Claude as orchestrator)\n"
    result += "- Fallback to regex detection if .coderef/ data unavailable\n"
    # ...
```

**Key Points:**
- ✅ Explicit instructions for Claude
- ✅ Explains the orchestration pattern
- ✅ Clarifies fallback behavior

### 3. MCP Integration Helper Module

**File:** `mcp_integration.py`

Provides utility functions for:
- Formatting MCP tool call instructions
- Processing MCP tool responses
- Categorizing code elements
- Handling relationship data

**Example Usage:**

```python
from mcp_integration import get_scan_instructions, process_scan_response

# Get instructions for Claude
instructions = get_scan_instructions(project_path)
# Returns: {action, tool_name, example_call, expected_response}

# Process results after Claude calls the MCP tool
categorized = process_scan_response(scan_results)
# Returns: {functions: [...], classes: [...], components: [...]}
```

---

## Usage Workflows

### Workflow 1: Generate Foundation Docs (Recommended)

1. **User calls:**
   ```
   mcp__coderef_docs__generate_foundation_docs(project_path="/path/to/project")
   ```

2. **coderef-docs responds:**
   ```
   === FOUNDATION DOCS - SEQUENTIAL GENERATION ===

   MCP INTEGRATION (coderef-context):
   - For better accuracy, call mcp__coderef_context__coderef_scan before generation
   - Generator will read .coderef/index.json after MCP scan completes
   ...
   ```

3. **Claude (optionally) calls:**
   ```
   mcp__coderef_context__coderef_scan(
       project_path="/path/to/project",
       languages=["ts", "tsx", "js", "jsx", "py"],
       use_ast=True
   )
   ```
   *(Generates `.coderef/index.json` and `.coderef/graph.json`)*

4. **Claude calls:**
   ```
   mcp__coderef_docs__generate_individual_doc(
       project_path="/path/to/project",
       template_name="api"
   )
   ```
   *(Reads `.coderef/index.json` for real code data)*

5. **Result:**
   Foundation docs generated with actual function/class names from codebase!

### Workflow 2: Use Existing .coderef/ Data (Fastest)

1. **Pre-existing .coderef/ structure:**
   ```
   project/.coderef/
   ├── index.json  (already exists)
   └── graph.json  (already exists)
   ```

2. **Claude calls:**
   ```
   mcp__coderef_docs__generate_foundation_docs(project_path="/path/to/project")
   ```

3. **coderef-docs automatically:**
   - Detects existing .coderef/ data
   - Loads elements and graph
   - Generates docs with real code intelligence
   - No MCP tool calls needed!

### Workflow 3: Fallback (No .coderef/ Data)

1. **No .coderef/ structure exists**

2. **Claude calls:**
   ```
   mcp__coderef_docs__generate_foundation_docs(project_path="/path/to/project")
   ```

3. **coderef-docs:**
   - Detects missing .coderef/ data
   - Falls back to regex-based detection
   - Generates docs with regex patterns
   - Still functional, but less accurate

4. **Logged message:**
   ```
   No .coderef/index.json found - using regex fallback.
   For better accuracy, use mcp__coderef_context__coderef_scan first.
   ```

---

## Requirements Met

✅ **Requirement 1:** Call coderef-context MCP tools directly (not via CLI subprocess)
- Implementation: Orchestration pattern where Claude calls MCP tools
- Verification: No subprocess calls in code, only file reads

✅ **Requirement 2:** Generate foundation docs using real code analysis
- Implementation: Reads .coderef/index.json populated by coderef_scan
- Verification: Docs contain actual function/class names from scan

✅ **Requirement 3:** Use existing .coderef/ data (do not auto-generate)
- Implementation: `_load_coderef_data()` only reads files
- Verification: No CLI subprocess calls, no auto-generation logic

✅ **Requirement 4:** Extract APIs, schemas, and components via coderef_scan and coderef_query
- Implementation: Claude calls these tools, coderef-docs processes results
- Verification: Integration instructions provided in tool responses

---

## Testing

### Unit Tests

```python
# Test .coderef/ data loading
def test_load_coderef_data_exists():
    # Verify reads existing files correctly

def test_load_coderef_data_missing():
    # Verify fallback when files missing
```

### Integration Tests

```python
# Test MCP orchestration pattern
async def test_mcp_integration_workflow():
    # 1. Call generate_foundation_docs
    # 2. Verify instructions returned
    # 3. Simulate coderef_scan call
    # 4. Call generate_individual_doc
    # 5. Verify docs use real code data
```

---

## Key Design Decisions

### Decision 1: Orchestration Pattern vs Direct Calls

**Chosen:** Claude orchestrates between MCP servers
**Rejected:** Direct MCP-to-MCP calls (not supported)
**Reason:** MCP protocol doesn't support server-to-server communication

### Decision 2: Read-Only vs Generate .coderef/

**Chosen:** Read existing .coderef/ files only
**Rejected:** Auto-generate .coderef/ data via subprocess
**Reason:** Requirement explicitly states "use existing data, do not auto-generate"

### Decision 3: Instructions vs Silent Failure

**Chosen:** Provide explicit MCP integration instructions
**Rejected:** Silent fallback without guidance
**Reason:** Helps Claude understand the orchestration pattern and when to call coderef-context tools

---

## References

- **MCP Specification:** https://spec.modelcontextprotocol.io/
- **coderef-context Tools:** C:\Users\willh\.mcp-servers\coderef-context\README.md
- **Workorder Plan:** coderef/workorder/integrating-coderef-context/plan.json
- **Feature Context:** coderef/workorder/integrating-coderef-context/context.json

---

**Maintained by:** willh, Claude Code AI
**Status:** ✅ Complete
