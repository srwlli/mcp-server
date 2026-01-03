# Multi-Agent Session Plan: Reference Sheet Reconciliation

## THE GOAL

**Consolidate two separate resource sheet systems into ONE unified system.**

### Current State (The Problem)

**Tool 1:** `.claude/commands/create-resource-sheet.md` (240 lines)
- Agent instruction framework (HOW to generate docs)
- Writing guidelines & voice standards
- Refactor safety validation
- Output format specification
- Maintenance protocol
- **Missing:** Element classification and specialized templates

**Tool 2:** `.claude/commands/resource-sheet-catalog.md` (634 lines)
- 20 element type classifications (WHAT to document)
- Element-specific checklists per type
- Required sections per element type
- **Missing:** Agent execution framework, quality controls, validation

### What Tool 1 Offers That Tool 2 Needs

✅ **Agent instruction framework** - Step-by-step execution guide
✅ **Writing quality standards** - Voice, tone, precision rules
✅ **Refactor safety validation** - Pre-submission checklist
✅ **Output format specification** - Exact markdown structure
✅ **Maintenance protocol** - Update/deprecation/versioning process

### What Tool 2 Offers That Tool 1 Needs

✅ **Element classification** - 20 specialized types
✅ **Element-specific checklists** - Focus areas per type
✅ **Prioritized requirements** - What matters most per type
✅ **Required sections** - Type-specific documentation needs

### The Gap

**Tool 2 has the WHAT** (20 specialized templates)
**Tool 1 has the HOW** (agent execution framework)

Tool 2 is a reference catalog without execution guidance.
Tool 1 is an execution framework without specialization.

---

## CRITICAL CONSTRAINT

✅ **The `/create-resource-sheet` command MUST continue working**
✅ This is the user interface - it stays
✅ We consolidate the backend (merge the two .md files into one unified system)

---

## Step-by-Step Execution

### **Step 1: Agent Kickoff (Parallel Execution)**

Three agents start simultaneously, each with a specific task:

**Agent 1 - coderef (Main MCP Server) - THE SYNTHESIZER**
- **Reads:** All three plan.json files
  - Plan 1 (coderef-assistant): Slash command consolidation approach
  - Plan 2 (coderef-docs): Documentation workflow approach
  - Plan 3 (coderef-system): Graph integration approach
- **Does:** Compares approaches and answers THE KEY QUESTIONS:
  - How to merge the two files structurally?
  - Keep all 20 element types or simplify?
  - Single template with conditional sections OR modular approach?
  - How does element type detection work?
  - What's the migration path from old to new?
- **Creates:**
  - `coderef-output.json` - Comparison matrix & synthesis data
  - `coderef-output.md` - Unified consolidation design

**Agent 2 - coderef-docs - THE DOCUMENTER**
- **Reads:** Own plan (Plan 2) as reference
- **Does:** Designs documentation standards for unified system:
  - What's the consolidated documentation structure?
  - How to maintain it going forward?
  - How does this fit into coderef-workflow?
  - Standards for the merged system?
- **Creates:**
  - `coderef-docs-output.json` - Documentation template schemas
  - `coderef-docs-output.md` - Standards guide for unified system

**Agent 3 - papertrail - THE TEMPLATE GENERATOR**
- **Reads:** All three plans for context
- **Does:** Creates auto-generation system for unified templates:
  - Template schema for consolidated system
  - How to generate element-specific variants
  - Validation rules for quality control
  - Auto-detection logic for element types
- **Creates:**
  - `papertrail-output.json` - Template generation schema
  - `papertrail-output.md` - Generation rules and validation guide

---

### **Step 2: Agents Update Status**

As each agent completes:
1. Updates `instructions.json` → `communication.agents[].status` = "complete"
2. Updates `aggregation.completed` count
3. Signals completion

---

### **Step 3: Orchestrator Collection (Me - coderef-assistant)**

Once all agents finish:
1. **Read all outputs:**
   - `coderef-output.json` (consolidation design)
   - `coderef-docs-output.json` (documentation standards)
   - `papertrail-output.json` (generation schema)

2. **Verify completeness:**
   - Does synthesis answer how to merge the files?
   - Do templates cover all 20 element types?
   - Does validation ensure quality?
   - Are outputs aligned with each other?

3. **Compile coordination summary:**
   - What each agent delivered
   - Overall session status
   - Links to all outputs

---

### **Step 4: Orchestrator Handoff Package**

I create final outputs:
- `orchestrator-output.json` - Session metadata
- `orchestrator-output.md` - Human-readable summary with:
  - Agent completion status
  - Links to all 6 output files (3 JSON + 3 MD)
  - Synthesized consolidation approach
  - Next steps for workorder creation

---

### **Step 5: User Review & Decision**

You review the handoff package:
- Read coderef's consolidation design (how to merge the two tools)
- Review coderef-docs standards (how to document the unified system)
- Review papertrail schema (how to auto-generate with validation)
- Decide on final approach

---

### **Step 6: Create Final Workorder**

Based on synthesis, we:
1. Use coderef-workflow's `gather_context` tool
2. Create `context.json` with final consolidation requirements
3. Use coderef-workflow's `create_plan` tool
4. Generate `plan.json` for implementation
5. Execute the unified plan

---

## File Structure After Completion

```
C:\Users\willh\.mcp-servers\coderef\sessions\reference-sheet-reconciliation\
├── WILL-READ-THIS-YOU-IDIOT.md (this file - session guide)
├── instructions.json (master session file with agent assignments)
├── coderef-output.json (synthesis data)
├── coderef-output.md (consolidation design report)
├── coderef-docs-output.json (documentation template schemas)
├── coderef-docs-output.md (standards guide)
├── papertrail-output.json (generation schema)
├── papertrail-output.md (generation rules guide)
├── orchestrator-output.json (session metadata)
└── orchestrator-output.md (handoff package with next steps)
```

---

## Key Benefits

✅ **Parallel Work:** All 3 agents work simultaneously
✅ **Specialized Expertise:** Each agent contributes their strength
✅ **Centralized Coordination:** Orchestrator ensures alignment
✅ **Structured Output:** Consistent JSON + Markdown format
✅ **Traceable:** All decisions documented in session files
✅ **Goal-Focused:** ONE unified system, not two fragmented tools

---

## What You Get

**From coderef (synthesizer):**
> "Here's how to merge the two tools: [structural design]. Here's how element detection works. Here's the migration path."

**From coderef-docs (documenter):**
> "Here's the documentation standards for the unified system. Here's how to maintain it."

**From papertrail (generator):**
> "Here's the template schema. Here's the auto-generation rules. Here's validation."

**From orchestrator (me):**
> "Here's everything packaged for your decision. Make the call, then we create the workorder."

---

## Success Criteria

**Before this session:**
- 2 separate tools with fragmented functionality
- Tool 1 has HOW, Tool 2 has WHAT
- Duplication and inconsistency

**After this session:**
- Clear design for ONE unified system
- Tool 1's execution framework + Tool 2's specialization
- `/create-resource-sheet` command continues working
- Ready-to-implement workorder

---

Ready to execute?
