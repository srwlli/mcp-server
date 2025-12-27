# How to Run Proof Tests on All 4 MCP Servers

**Purpose:** Create real proof artifacts for coderef-context, coderef-workflow, coderef-docs, and coderef-personas

**Time per server:** 10-15 minutes (mostly automated)
**Total time:** ~1 hour for all 4 servers

---

## Quick Summary

For each server, you:
1. Create a test workorder context.json
2. Run `/create-workorder` workflow
3. Capture real coderef-context output (analysis.json + plan.json)
4. Document the proof

---

## Step 1: coderef-workflow (Already Done ✅)

**Status:** Complete
**Location:** `coderef/workorder/test-coderef-injection/`
**Files:**
- ✅ context.json
- ✅ analysis.json (real coderef_scan output)
- ✅ plan.json (real planning with injections)
- ✅ CODEREF_INJECTION_PROOF.md (documentation)

**Proof Shows:**
- 45 files, 127 components
- 8 modules depend on MCPToolClient
- 5 explicit calls to coderef-context tools
- 3 breaking changes identified

---

## Step 2: coderef-context

### Create Test Workorder

```bash
cd C:\Users\willh\.mcp-servers\coderef-context
mkdir -p coderef/workorder/test-coderef-context-injection
```

Create `coderef/workorder/test-coderef-context-injection/context.json`:

```json
{
  "feature_name": "test-coderef-context-injection",
  "goal": "Create a test workorder to prove coderef-context is functional and can analyze code",
  "description": "This is a TEST ONLY workorder. We will NOT execute this feature. The purpose is to run the complete /create-workorder workflow on the coderef-context project itself, then capture the real coderef-context self-analysis results as proof that code intelligence works.",
  "requirements": [
    "Run /create-workorder workflow completely",
    "Capture analysis.json with real coderef_scan results of coderef-context itself",
    "Capture plan.json with coderef_query, coderef_patterns results",
    "Document how coderef-context analyzes itself (recursive proof)",
    "Show the CLI wrapper, subprocess management, and tool handlers"
  ],
  "out_of_scope": [
    "EXECUTION - do not implement any code changes",
    "Agent assignments - this is planning phase only",
    "Actual feature implementation"
  ],
  "constraints": [
    "Planning documents only - NO code modifications",
    "Capture real coderef-context output, not mock data",
    "Analyze coderef-context project itself (recursive)"
  ]
}
```

### Run the Workflow

```bash
# From any directory
# Call the /create-workorder slash command or MCP tool
# Point it to: C:\Users\willh\.mcp-servers\coderef-context

# This will:
# 1. Analyze coderef-context project
# 2. Create analysis.json with real tool outputs
# 3. Create plan.json with planning results
# 4. Generate proof artifacts
```

### Expected Real Results

**coderef_scan will find:**
- ~30-40 files
- ~80-100 components (Python-only)
- Key classes: CoderefCLI, CoderefContext, SubprocessManager, JSONRPCHandler
- 10-15 MCP tools for code analysis

**coderef_query will show:**
- SubprocessManager called by all tool handlers
- JSONRPCHandler dependencies
- CLI wrapper dependencies

**coderef_patterns will detect:**
- Subprocess lifecycle patterns
- JSON-RPC protocol patterns
- Tool invocation patterns
- Error handling patterns

**coderef_impact will show:**
- CLI availability is critical dependency
- If @coderef/core unavailable, all tools fail
- High impact on workflow integration

### Create Proof Document

Create `PROOF_DOCUMENT_CODEREF_CONTEXT.md` explaining:
- coderef-context analyzed itself (recursive)
- Real findings about its own architecture
- Evidence that code intelligence works

---

## Step 3: coderef-docs

### Create Test Workorder

```bash
cd C:\Users\willh\.mcp-servers\coderef-docs
mkdir -p coderef/workorder/test-coderef-docs-injection
```

Create `coderef/workorder/test-coderef-docs-injection/context.json`:

```json
{
  "feature_name": "test-coderef-docs-injection",
  "goal": "Create a test workorder to prove coderef-docs documentation generation works",
  "description": "This is a TEST ONLY workorder. The purpose is to run the complete /create-workorder workflow on the coderef-docs project itself, then capture real coderef-context analysis of documentation generation system.",
  "requirements": [
    "Run /create-workorder workflow completely",
    "Capture analysis.json with real coderef_scan results of coderef-docs",
    "Show structure: generators/, templates/, tool_handlers.py",
    "Capture dependency analysis of documentation pipeline",
    "Prove docs generation system works with code intelligence"
  ],
  "out_of_scope": [
    "EXECUTION - do not implement any code changes",
    "Agent assignments - planning phase only",
    "Actual feature implementation"
  ],
  "constraints": [
    "Planning documents only - NO code modifications",
    "Capture real coderef-context output"
  ]
}
```

### Run the Workflow

```bash
# Call /create-workorder on coderef-docs project
# C:\Users\willh\.mcp-servers\coderef-docs
```

### Expected Real Results

**coderef_scan will find:**
- ~35-45 files
- ~90-110 components
- Key classes: FoundationDocGenerator, ChangelogGenerator, StandardsAuditor, QuickrefGenerator
- 11 MCP tools for documentation

**coderef_query will show:**
- ToolHandlers are central hub (used by all tools)
- Generators depend on POWER templates
- Git integration dependencies

**coderef_patterns will detect:**
- Generator pattern (all generators inherit from base)
- Template loading patterns
- Git command patterns
- POWER framework structure

**coderef_impact will show:**
- If POWER template system changes, all docs affected
- If git integration unavailable, record_changes fails
- Foundation docs depend on coderef-context (important!)

---

## Step 4: coderef-personas

### Create Test Workorder

```bash
cd C:\Users\willh\.mcp-servers\coderef-personas
mkdir -p coderef/workorder/test-coderef-personas-injection
```

Create `coderef/workorder/test-coderef-personas-injection/context.json`:

```json
{
  "feature_name": "test-coderef-personas-injection",
  "goal": "Create a test workorder to prove coderef-personas expertise injection works",
  "description": "This is a TEST ONLY workorder. The purpose is to run the complete /create-workorder workflow on the coderef-personas project itself, then capture real coderef-context analysis of the persona system.",
  "requirements": [
    "Run /create-workorder workflow completely",
    "Capture analysis.json with real coderef_scan results of coderef-personas",
    "Show persona definitions: Ava, Marcus, Quinn, Lloyd, etc.",
    "Capture dependency analysis of persona activation system",
    "Prove expertise injection mechanism works"
  ],
  "out_of_scope": [
    "EXECUTION - do not implement any code changes",
    "Agent assignments - planning phase only"
  ],
  "constraints": [
    "Planning documents only - NO code modifications",
    "Capture real coderef-context output"
  ]
}
```

### Run the Workflow

```bash
# Call /create-workorder on coderef-personas project
# C:\Users\willh\.mcp-servers\coderef-personas
```

### Expected Real Results

**coderef_scan will find:**
- ~30-40 files
- ~70-90 components
- Key: 9 persona definitions (Ava, Marcus, Quinn, etc.)
- PersonaManager class
- 6-8 MCP tools for persona management

**coderef_query will show:**
- PersonaManager called by all persona tools
- Persona definitions dependencies
- System prompt loading dependencies

**coderef_patterns will detect:**
- Persona definition pattern (consistent structure)
- System prompt injection pattern
- Persona activation pattern
- Behavior modification patterns

**coderef_impact will show:**
- If PersonaManager changes, all personas fail
- If persona definitions change, behavior changes
- System prompt size affects token usage

---

## Running All 4 Tests (Complete Sequence)

### Option 1: Manual (Step-by-Step)

```bash
# Server 1: coderef-workflow (ALREADY DONE)
cd C:\Users\willh\.mcp-servers\coderef-workflow
# Files already exist: analysis.json, plan.json, CODEREF_INJECTION_PROOF.md

# Server 2: coderef-context
cd C:\Users\willh\.mcp-servers\coderef-context
mkdir -p coderef/workorder/test-coderef-context-injection
# Create context.json (use template above)
# Run /create-workorder workflow
# Wait for analysis.json, plan.json generation
# Verify proof artifacts exist

# Server 3: coderef-docs
cd C:\Users\willh\.mcp-servers\coderef-docs
mkdir -p coderef/workorder/test-coderef-docs-injection
# Create context.json (use template above)
# Run /create-workorder workflow
# Wait for artifacts

# Server 4: coderef-personas
cd C:\Users\willh\.mcp-servers\coderef-personas
mkdir -p coderef/workorder/test-coderef-personas-injection
# Create context.json (use template above)
# Run /create-workorder workflow
# Wait for artifacts
```

### Option 2: Automated Script

Create `run-all-proof-tests.sh`:

```bash
#!/bin/bash

SERVERS=("coderef-context" "coderef-docs" "coderef-personas")
BASE_PATH="/c/Users/willh/.mcp-servers"

for SERVER in "${SERVERS[@]}"; do
  echo "======================================"
  echo "Running proof test for: $SERVER"
  echo "======================================"

  cd "$BASE_PATH/$SERVER"

  # Create directory
  mkdir -p "coderef/workorder/test-${SERVER}-injection"

  # Context.json already created (you did it manually)

  # Run the workflow (this part is manual - calls /create-workorder)
  echo "Created directory: coderef/workorder/test-${SERVER}-injection"
  echo "Next: Run /create-workorder on this project"
  echo "Files will be created in: coderef/workorder/test-${SERVER}-injection/"
  echo ""

  sleep 2
done

echo "======================================"
echo "All servers ready for proof tests"
echo "======================================"
```

---

## Verifying Proof Artifacts

After running all 4:

```bash
# Check all proof artifacts exist
ls -la C:\Users\willh\.mcp-servers\coderef-workflow\coderef\workorder\test-coderef-injection\
ls -la C:\Users\willh\.mcp-servers\coderef-context\coderef\workorder\test-coderef-context-injection\
ls -la C:\Users\willh\.mcp-servers\coderef-docs\coderef\workorder\test-coderef-docs-injection\
ls -la C:\Users\willh\.mcp-servers\coderef-personas\coderef\workorder\test-coderef-personas-injection\

# Each should have:
# - context.json
# - analysis.json (with real coderef_scan output)
# - plan.json (with planning results)
# - (optional) PROOF_DOCUMENT_XXX.md
```

---

## Creating Proof Documents

For each server, create `PROOF_DOCUMENT_{SERVER}.md`:

### Template

```markdown
# Proof: {SERVER} Code Analysis

**Date:** 2025-12-26
**Server:** {SERVER}
**Project Analyzed:** C:\Users\willh\.mcp-servers\{SERVER}

## What This Proves

- coderef_scan can analyze {SERVER} project structure
- coderef_query can find dependencies within {SERVER}
- coderef_patterns can detect patterns in {SERVER} code
- coderef_impact can analyze breaking changes in {SERVER}

## Real Results from coderef_scan

[Include numbers from analysis.json]
- Files: XX
- Components: YY
- Key classes: [list them]
- MCP tools: ZZ

## Real Results from coderef_query

[Include dependency findings]

## Real Results from coderef_patterns

[Include pattern findings]

## Real Results from coderef_impact

[Include impact findings]

## Proof Markers

All results marked with:
- "tool_invoked": "{tool_name}"
- "timestamp": "ISO8601"
- "proof_of_injection": "Explanation"

## Conclusion

coderef-context successfully analyzed {SERVER} and provided real code intelligence.
```

---

## Creating Central Proof Registry

Create `coderef/proofs/index.json`:

```json
{
  "proofs": [
    {
      "id": "coderef-workflow-injection-001",
      "server": "coderef-workflow",
      "date": "2025-12-26",
      "status": "complete",
      "workorder": "WO-TEST-INJECTION-001",
      "location": "coderef/workorder/test-coderef-injection/",
      "findings": {
        "files_analyzed": 45,
        "components": 127,
        "breaking_changes": 3,
        "coderef_tools_invoked": 4
      }
    },
    {
      "id": "coderef-context-injection-001",
      "server": "coderef-context",
      "date": "2025-12-26",
      "status": "pending",
      "workorder": "WO-TEST-CONTEXT-INJECTION-001",
      "location": "coderef/workorder/test-coderef-context-injection/",
      "findings": {}
    },
    {
      "id": "coderef-docs-injection-001",
      "server": "coderef-docs",
      "date": "2025-12-26",
      "status": "pending",
      "workorder": "WO-TEST-DOCS-INJECTION-001",
      "location": "coderef/workorder/test-coderef-docs-injection/",
      "findings": {}
    },
    {
      "id": "coderef-personas-injection-001",
      "server": "coderef-personas",
      "date": "2025-12-26",
      "status": "pending",
      "workorder": "WO-TEST-PERSONAS-INJECTION-001",
      "location": "coderef/workorder/test-coderef-personas-injection/",
      "findings": {}
    }
  ],
  "summary": {
    "total_proofs": 4,
    "complete": 1,
    "pending": 3,
    "total_files_analyzed": "~155-185",
    "total_components": "~370-450",
    "ecosystem_coverage": "100%"
  }
}
```

---

## Timeline & Effort

| Server | Step | Time | Effort |
|--------|------|------|--------|
| All | Create context.json files | 10 min | Low |
| coderef-context | Run /create-workorder | 5 min | Auto |
| coderef-docs | Run /create-workorder | 5 min | Auto |
| coderef-personas | Run /create-workorder | 5 min | Auto |
| All | Create proof documents | 15 min | Medium |
| All | Verify & registry | 5 min | Low |
| **Total** | | **45 min** | **Medium** |

---

## Checklist

- [ ] coderef-workflow proof (already done ✅)
- [ ] coderef-context context.json created
- [ ] coderef-context /create-workorder run
- [ ] coderef-context proof verified (analysis.json + plan.json exist)
- [ ] coderef-docs context.json created
- [ ] coderef-docs /create-workorder run
- [ ] coderef-docs proof verified
- [ ] coderef-personas context.json created
- [ ] coderef-personas /create-workorder run
- [ ] coderef-personas proof verified
- [ ] Proof documents created for all 3
- [ ] Central registry (index.json) updated
- [ ] All findings summarized

---

## Result

After completion, you'll have:

✅ **4 Real Proof Artifacts** (one per server)
- Each analyzes its own project (recursive)
- Each shows code intelligence working
- Each generates 45+ files of analysis
- Each proves the system works with real data

✅ **Comprehensive Evidence**
- coderef-context proves code analysis works
- coderef-workflow proves planning works
- coderef-docs proves docs generation works
- coderef-personas proves expertise injection works

✅ **Professional Documentation**
- 4 PROOF_DOCUMENT.md files
- Central registry (index.json)
- Complete audit trail
- Timestamps and markers

---

## Next Steps

1. Create context.json for coderef-context, coderef-docs, coderef-personas
2. Run `/create-workorder` workflow on each
3. Verify artifacts are created
4. Create proof documents
5. Update central registry
6. Use as evidence that all 4 servers work correctly

**Estimated completion:** Tomorrow (after running all 4 workflows)

