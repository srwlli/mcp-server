# coderef-context MCP Implementation Plan

**Current State & Division of Labor**

---

## The Plan (Simple)

**Agent does**: Audit core & CLI, document specs
**Lloyd does**: Build MCP wrapper, implement handlers

```
┌─────────────────────────────────────────────────────┐
│ Step 1: Agent Audits (WO-CODEREF-TOOLS-AUDIT-001)   │
│ ┌───────────────────────────────────────────────┐   │
│ │ • Examine @coderef/core modules               │   │
│ │ • List all tools (Scanner, Analyzer, etc)     │   │
│ │ • Examine packages/cli commands               │   │
│ │ • Identify what's exposed vs what's not       │   │
│ │ • Create CLI_SPEC.md with full specs          │   │
│ │ • Implement any missing CLI commands          │   │
│ └───────────────────────────────────────────────┘   │
│              DELIVERABLE: CLI_SPEC.md                │
└─────────────────────────────────────────────────────┘
          ↓ (when ready)
┌─────────────────────────────────────────────────────┐
│ Step 2: Lloyd Implements (coderef-context MCP)      │
│ ┌───────────────────────────────────────────────┐   │
│ │ • Read CLI_SPEC.md                            │   │
│ │ • Implement handlers for all tools            │   │
│ │ • Map CLI commands → MCP tools                │   │
│ │ • Parse JSON output for agents                │   │
│ │ • Error handling & edge cases                 │   │
│ │ • Register in .mcp.json                       │   │
│ │ • Test with real agents                       │   │
│ └───────────────────────────────────────────────┘   │
│         DELIVERABLE: Functional MCP Server           │
└─────────────────────────────────────────────────────┘
          ↓ (when ready)
┌─────────────────────────────────────────────────────┐
│ Step 3: Validate with Agents                        │
│ ┌───────────────────────────────────────────────┐   │
│ │ • Agents call tools during implementation     │   │
│ │ • Verify all 10 tools work                    │   │
│ │ • Fix any issues                              │   │
│ │ • Optimize performance                        │   │
│ └───────────────────────────────────────────────┘   │
│         DELIVERABLE: Production-Ready System        │
└─────────────────────────────────────────────────────┘
```

---

## Current Status: Setup Complete ✅

### What's Done
- ✅ **WO-CODEREF-TOOLS-AUDIT-001 created** - Agent task fully specified
- ✅ **stub.json created** - Detailed instructions for agent
- ✅ **coderef-context MCP skeleton created** - Server structure ready
- ✅ **10 tools defined** - Tool specs in server.py
- ✅ **README created** - Explains the system
- ✅ **This plan created** - Clear division of labor

### What's Waiting
- ⏳ **CLI_SPEC.md** - Agent must create this (describes all CLI commands and their JSON output)
- ⏳ **Tool handlers** - Lloyd will implement once CLI_SPEC.md exists
- ⏳ **Registration** - Add to .mcp.json once done

---

## The 10 Tools (MCP Tools vs CLI Commands)

Each MCP tool wraps a CLI command:

| MCP Tool | CLI Command | Purpose |
|----------|-------------|---------|
| `/scan` | `node cli.js scan` | Discover code elements |
| `/query` | `node cli.js query` | Relationships (what-calls, what-imports) |
| `/impact` | `node cli.js impact` | Change impact analysis |
| `/complexity` | `node cli.js complexity` | Metrics (LOC, cyclomatic, coverage) |
| `/patterns` | `node cli.js patterns` | Pattern discovery |
| `/coverage` | `node cli.js coverage` | Test coverage analysis |
| `/context` | `node cli.js context` | Comprehensive codebase context |
| `/validate` | `node cli.js validate` | CodeRef2 reference validation |
| `/drift` | `node cli.js drift` | Reference drift detection |
| `/diagram` | `node cli.js diagram` | Visual dependency diagrams |

---

## Agent's Job (WO-CODEREF-TOOLS-AUDIT-001)

### Task 1: Audit @coderef/core
**Location**: `C:\Users\willh\Desktop\projects\coderef-system\packages\core\src`

Examine these modules:
- `analyzer/` - Scanner, GraphBuilder, GraphAnalyzer, etc.
- `query/` - QueryExecutor (8 query types)
- `context/` - ComplexityScorer, EdgeCaseDetector, TestPatternAnalyzer, etc.
- `validator/` - CodeRefValidator
- `export/` - GraphExporter
- `integration/` - RAG/semantic search

**Deliverable**: List each tool with what it does, inputs, outputs

### Task 2: Audit packages/cli
**Location**: `C:\Users\willh\Desktop\projects\coderef-system\packages\cli\src`

Examine CLI commands (already identified):
- scan, query, impact, coverage, context, validate, drift, diagram, etc.

For each, document:
- Command name & arguments
- Input parameters
- Output format (must be JSON with `--json` flag)
- What @coderef/core tool it uses

**Deliverable**: Table showing CLI → core tool mapping

### Task 3: Identify Gaps
Compare:
- What @coderef/core CAN do (from audit 1)
- What packages/cli EXPOSES (from audit 2)

Find tools with no CLI command. Examples:
- Is there a dedicated complexity scoring CLI command?
- Is there a pattern discovery CLI command?
- Are all query types exposed?

**Deliverable**: Gap list

### Task 4: Fill Gaps (If Any)
If gaps exist, implement missing CLI commands so agents can access all @coderef/core tools.

**Deliverable**: New CLI commands for any gaps

### Task 5: Document CLI_SPEC.md
Create comprehensive spec that Lloyd will use:

```markdown
# CLI_SPEC.md

## Command: scan

**What it does**: Discover code elements

**CLI invocation**:
\`\`\`bash
node cli.js scan <path> --lang ts,tsx --analyzer ast --json
\`\`\`

**Parameters**:
- path: Project directory
- --lang: Languages to scan
- --analyzer: ast or regex
- --json: Return JSON

**JSON Output Schema**:
{
  "elements": [
    {
      "type": "function|class|component|hook",
      "name": "string",
      "file": "string",
      "line": "number",
      "exported": "boolean",
      "parameters": ["string"],
      "calls": ["string"]
    }
  ]
}

---

## Command: query

... (same pattern for each command)
```

This is what Lloyd needs to implement the handlers.

---

## Lloyd's Job (coderef-context MCP)

Once CLI_SPEC.md exists, implement handlers like:

```python
async def handle_coderef_scan(args: dict) -> list[TextContent]:
    """Wrap node cli.js scan command"""
    project_path = args['project_path']
    languages = args.get('languages', ['ts', 'tsx'])
    use_ast = args.get('use_ast', True)

    # Build CLI command from CLI_SPEC.md
    cmd = [
        'node', CLI_BIN, 'scan',
        project_path,
        '--lang', ','.join(languages),
        '--analyzer', 'ast' if use_ast else 'regex',
        '--json'
    ]

    # Execute subprocess
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

    if result.returncode != 0:
        return [TextContent(text=f"Error: {result.stderr}")]

    # Parse JSON
    data = json.loads(result.stdout)

    # Return formatted result
    return [TextContent(text=json.dumps({
        "success": True,
        "elements_found": len(data.get('elements', [])),
        "elements": data.get('elements', [])
    }, indent=2))]
```

---

## Current Files

### Created by Me (Lloyd)
- `/coderef-context/server.py` - MCP server skeleton with 10 tool definitions
- `/coderef-context/pyproject.toml` - Package config
- `/coderef-context/README.md` - Overview
- `/coderef-context/IMPLEMENTATION_PLAN.md` - This file

### Created by Agent
- `/packages/stub.json` - Audit task specification
- `/packages/CORE_TOOLS_INVENTORY.md` - Agent's audit output (expected)
- `/packages/CLI_COMMAND_COVERAGE.md` - Agent's audit output (expected)
- `/packages/CLI_SPEC.md` - Agent's main deliverable (expected)

---

## Timeline

### Agent: 3-5 Days
- Day 1-2: Audit @coderef/core modules
- Day 2-3: Audit packages/cli commands
- Day 3-4: Identify gaps and document specs
- Day 4-5: (Optional) Implement missing CLI commands

**Deliverable**: CLI_SPEC.md

### Lloyd: 2-3 Days (Once CLI_SPEC.md Ready)
- Day 1: Implement handlers for /scan, /query, /impact
- Day 2: Implement handlers for /complexity, /patterns, /coverage
- Day 3: Implement handlers for /context, /validate, /drift, /diagram
- Day 3: Testing and registration

**Deliverable**: Functional coderef-context MCP server

### Total: ~7-8 Days
- Agent: 3-5 days
- Lloyd: 2-3 days
- Testing: 1-2 days

---

## Success Criteria

**Agent's work is done when**:
- ✅ CLI_SPEC.md fully documents all 10 CLI commands
- ✅ Each command's JSON output is specified
- ✅ Any gaps are identified and fixed
- ✅ Lloyd can read CLI_SPEC.md and implement without ambiguity

**Lloyd's work is done when**:
- ✅ All 10 tool handlers are implemented
- ✅ Tools return JSON that agents can parse
- ✅ Error handling works (missing files, parse failures, etc.)
- ✅ coderef-context is registered in .mcp.json
- ✅ Tested with real agents calling the tools

**System works when**:
- ✅ Agents can call /scan and get code elements
- ✅ Agents can call /query and understand dependencies
- ✅ Agents can call /impact and assess risk
- ✅ All 10 tools work reliably
- ✅ Agents use tools intelligently during implementation

---

## Questions for Agent

When creating CLI_SPEC.md, make sure to answer:

1. **For each CLI command**:
   - What does it do?
   - What are all the parameters?
   - What's the exact command-line invocation?
   - What JSON does it output?
   - What are the JSON field names and types?
   - What error messages might it produce?

2. **For CLI commands not yet existing**:
   - Is there a CLI command for: complexity scoring? pattern discovery? etc.
   - If not, should we add one, or is it less important?

3. **For JSON output**:
   - Does every command support `--json` flag?
   - Are the outputs complete (no truncation)?
   - Are field names consistent across commands?

---

## What Lloyd Can't Do Until CLI_SPEC.md Exists

- Implement the tool handlers (need to know exact CLI syntax)
- Know which parameters to accept (need CLI specs)
- Parse JSON response correctly (need output schema)
- Handle errors properly (need to know what errors are possible)

So the agent's audit work is the critical path. Everything waits for CLI_SPEC.md.

---

**Status**: 🔵 Ready for Agent to Start
**Next**: Agent begins WO-CODEREF-TOOLS-AUDIT-001
**Blocked**: On CLI_SPEC.md delivery
