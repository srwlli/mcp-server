# Agent 1: Sessions Hub Creator

**Workorder:** WO-SESSIONS-HUB-002-CREATOR
**Role:** Build System 1 (Session Creation)
**Sprints:** 1-4 (Stub Selection → Instructions → Attachments → Agent Assignment → Session Generation)
**Project:** coderef-dashboard
**Output Directory:** `C:\Users\willh\Desktop\coderef-dashboard\packages\dashboard\src\components\SessionsHub\SessionCreation\`

---

## Phase 0: Research & Onboarding (START HERE)

**BEFORE WRITING ANY CODE**, research the project context and understand the design.

### Step 1: Read Phase 1 Design Documents

**Location:** `C:\Users\willh\Desktop\coderef-dashboard\.coderef\sessions\sessions-hub-phase1\`

**Required Reading:**
1. **dashboard-audit-v2.md** - Comprehensive Phase 1 design spec
   - System 1 (Session Creation) detailed specification
   - Component hierarchy and data flow
   - UI mockups and user flows

2. **orchestrator-phase1-audit-v2.md** - Approved design document
   - Design decisions and rationale
   - Technical constraints
   - Quality standards

3. **ARCHITECTURE-DIAGRAM.md** (if exists) - System architecture
4. **SUMMARY.md** (if exists) - Phase 1 outcomes

**What to Look For:**
- What components were designed in Phase 1?
- What UI patterns were established?
- What data structures were defined?
- What user flows were planned?

### Step 2: Read Foundation Documentation

**Location:** `C:\Users\willh\Desktop\coderef-dashboard\`

**Required Reading:**
1. **ARCHITECTURE.md** - Project architecture patterns
   - Next.js conventions
   - Component organization
   - API patterns
   - State management approach

2. **COMPONENTS.md** - Existing component library
   - What UI components already exist?
   - What can be reused?
   - What component patterns are established?

3. **SCHEMA.md** (if exists) - Data schemas
   - Session data structures
   - Communication.json format
   - Instructions.json format

### Step 3: Study Existing Patterns

**Location:** `C:\Users\willh\Desktop\coderef-dashboard\packages\dashboard\src\components\PromptingWorkflow\`

**What to Research:**
- How does PromptingWorkflow handle forms?
- What validation patterns exist?
- What UI components are used?
- How is state managed?
- What's the file structure?

**DON'T copy code blindly. UNDERSTAND the patterns and adapt them.**

### Step 4: Create Your Implementation Plan

After research, use the coderef-workflow tools:

```bash
# 1. Gather context
mcp__coderef-workflow__gather_context

# 2. Create implementation plan
mcp__coderef-workflow__create_plan

# 3. Generate todos
mcp__coderef-workflow__execute_plan
```

This will create:
- `context.json` - Your understanding of requirements
- `plan.json` - Your sprint-by-sprint implementation plan
- TodoWrite checklist - Trackable tasks

### Step 5: Validate Against Design

Before coding, verify:
- ✅ Your plan matches Phase 1 design specs
- ✅ Component names align with design document
- ✅ Data structures match established schemas
- ✅ UI patterns follow existing conventions

**Output:** Create `research-summary.md` documenting:
- Key findings from Phase 1 design
- Reusable patterns identified
- Component structure plan
- Questions/clarifications needed

---

## Your Mission

Build the **Session Creation** system that allows users to:
1. Select a stub (e.g., STUB-082)
2. Write freeform instructions (multiple blocks with type tags)
3. Attach context files (foundation docs, archived features)
4. Assign instructions/attachments to specific agents
5. Generate session files (context-backbone.md, communication.json, instructions.json)

---

## Critical Constraints

### Forbidden Files
**YOU MUST NOT TOUCH THESE FILES:**
- `packages/dashboard/src/components/SessionsHub/SessionMonitoring/**`
- `packages/dashboard/src/lib/api/sessions.ts`

These belong to Agent 2 (Monitor). File conflicts will break parallel execution.

### Your Territory
**YOU OWN THESE DIRECTORIES:**
- `packages/dashboard/src/components/SessionsHub/SessionCreation/`
- `packages/dashboard/src/api/sessions/create/`

---

## Sprint Breakdown

### Sprint 1: Stub Selection + Instruction Editor

**Components to Build:**

1. **StubSelector.tsx**
   - List hardcoded stubs (STUB-082, 054, 055, 056, 057)
   - Display: stub ID, feature name, description, target project
   - Search/filter functionality
   - Emit `selectedStub` event

2. **InstructionEditor.tsx**
   - Freeform textarea with markdown support
   - Markdown preview toggle
   - Character count display
   - Toolbar: Bold, Italic, List, Code block

3. **InstructionBlock System**
   - Add/remove/reorder blocks
   - Block properties: id (UUID), content (string), type (enum), assignedTo (array)
   - Block types: task | guideline | example | constraint
   - Color-coded borders: task=green, guideline=blue, example=purple, constraint=orange
   - Block numbering (auto-generated)

4. **SessionCreation.tsx (Container)**
   - Form validation:
     - Stub must be selected
     - At least one instruction block required
     - Each block must have content
   - Display validation errors in red
   - Disable "Next" button until validation passes

**Reference Patterns:**
- Check `packages/dashboard/src/components/PromptingWorkflow/` for similar patterns (don't copy code, understand approach)

---

### Sprint 2: Attachment System

**Components to Build:**

1. **AttachmentManager.tsx**
   - Browse foundation docs (ARCHITECTURE.md, SCHEMA.md, COMPONENTS.md)
   - Browse archived features (`coderef/archived/`)
   - Browse custom files (user file picker)
   - Display: filename, type (foundation|archived|custom), size
   - Add/remove attachments
   - Preview attachment content (modal)

2. **ContextDiscoveryAPI.tsx**
   - API endpoint: `/api/sessions/context-discovery`
   - Scans target project for foundation docs
   - Scans coderef/archived/ for features
   - Returns: `{ foundation: [], archived: [], custom: [] }`

3. **AttachmentPreview.tsx**
   - Modal component
   - Renders markdown, JSON, or plain text
   - Syntax highlighting for code
   - Read-only view

**Integration:**
- Add AttachmentManager to SessionCreation.tsx
- Validate: At least one attachment recommended (warning, not error)

---

### Sprint 3: Agent Assignment

**Components to Build:**

1. **AgentAssigner.tsx**
   - List available agents (from target project's communication.json template)
   - Drag-and-drop interface:
     - Drag instruction blocks → assign to agents
     - Drag attachments → assign to agents
   - Visual indicators: assigned blocks/attachments highlighted
   - Multi-select: One block can be assigned to multiple agents

2. **AgentCard.tsx**
   - Display agent info: agent_id, role, status
   - Drop zone for blocks/attachments
   - List assigned items
   - Remove assignment button

3. **DependencyManager.tsx**
   - Define agent dependencies (Agent B waits for Agent A)
   - Visual graph of dependencies
   - Cycle detection (prevent circular dependencies)
   - Export dependencies to communication.json format

**Integration:**
- Add AgentAssigner to SessionCreation.tsx
- Validate: All instruction blocks must be assigned to at least one agent

---

### Sprint 4: Session Generation

**Components to Build:**

1. **SessionGenerator.tsx**
   - Preview session files before creation:
     - `context-backbone.md` (instructions + attachments for all agents)
     - `communication.json` (agent roster + assignments + dependencies)
     - `instructions.json` (orchestrator + agent instructions)
   - Edit generated files (advanced users)
   - "Generate Session" button → creates files in target project

2. **Generation Logic:**
   - Read selected stub metadata
   - Aggregate instruction blocks by agent
   - Aggregate attachments by agent
   - Generate context-backbone.md:
     ```markdown
     # Session Context: {stub.feature_name}

     ## Overview
     {stub.description}

     ## Agent Instructions

     ### Agent 1: {agent_id}
     {assigned instruction blocks}

     ### Agent 2: {agent_id}
     {assigned instruction blocks}

     ## Attachments
     {list of context files}
     ```
   - Generate communication.json using template
   - Generate instructions.json using template

3. **SessionCreationComplete.tsx**
   - Success screen
   - Display: session directory path, files created
   - "Open Session Monitor" button → navigate to SessionMonitoring (Agent 2's component)
   - "Create Another Session" button → reset form

**API Endpoint:**
- `POST /api/sessions/create`
- Request: `{ stub, instructions, attachments, agents, dependencies }`
- Response: `{ session_path, files_created }`

---

## Deliverables Checklist

When you complete all 4 sprints, create this file:

**File:** `C:\Users\willh\.mcp-servers\coderef\sessions\sessions-hub-phase2-multiagent\creator-deliverables.md`

```markdown
# Creator Agent Deliverables

## Components Created
- SessionCreation/StubSelector.tsx
- SessionCreation/InstructionEditor.tsx
- SessionCreation/InstructionBlock.tsx
- SessionCreation/AttachmentManager.tsx
- SessionCreation/AttachmentPreview.tsx
- SessionCreation/AgentAssigner.tsx
- SessionCreation/AgentCard.tsx
- SessionCreation/DependencyManager.tsx
- SessionCreation/SessionGenerator.tsx
- SessionCreation/SessionCreationComplete.tsx
- SessionCreation/index.tsx (container)

## API Routes Created
- /api/sessions/context-discovery
- /api/sessions/create

## Files Modified
- (list any existing files you modified)

## Challenges
- (document any challenges and solutions)

## Forbidden File Compliance
✅ No files in SessionMonitoring/ directory touched
✅ No modifications to packages/dashboard/src/lib/api/sessions.ts

## Status
Complete
```

---

## Workflow: Research → Plan → Execute

### After Phase 0 Research

**Use coderef-workflow MCP tools to create your workorder:**

1. **Gather Context** (creates context.json):
```typescript
mcp__coderef-workflow__gather_context({
  project_path: "C:\\Users\\willh\\Desktop\\coderef-dashboard",
  feature_name: "sessions-hub-creator",
  description: "Build Session Creation system (Sprints 1-4)",
  goal: "Enable users to create multi-agent sessions through UI",
  requirements: [
    "Stub selection interface",
    "Multi-block instruction editor with type tags",
    "Attachment manager for foundation docs and archived features",
    "Agent assignment with drag-and-drop",
    "Session file generation (context-backbone.md, communication.json, instructions.json)"
  ],
  constraints: [
    "Cannot modify SessionMonitoring/ directory (Agent 2's territory)",
    "Must follow Phase 1 design specs",
    "Must reuse existing patterns from PromptingWorkflow/"
  ]
})
```

2. **Create Plan** (generates plan.json):
```typescript
mcp__coderef-workflow__create_plan({
  project_path: "C:\\Users\\willh\\Desktop\\coderef-dashboard",
  feature_name: "sessions-hub-creator",
  workorder_id: "WO-SESSIONS-HUB-002-CREATOR"
})
```

3. **Execute Plan** (generates TodoWrite checklist):
```typescript
mcp__coderef-workflow__execute_plan({
  project_path: "C:\\Users\\willh\\Desktop\\coderef-dashboard",
  feature_name: "sessions-hub-creator"
})
```

**This creates:**
- `coderef/workorder/sessions-hub-creator/context.json`
- `coderef/workorder/sessions-hub-creator/plan.json`
- TodoWrite task list in your IDE

---

## Phase Progression

1. **Phase 0:** Research (read docs, understand design)
2. **Phase 1:** Planning (gather_context → create_plan → execute_plan)
3. **Sprint 1:** StubSelector + InstructionEditor → Basic form working
4. **Sprint 2:** AttachmentManager → Can attach context files
5. **Sprint 3:** AgentAssigner → Can assign blocks/attachments to agents
6. **Sprint 4:** SessionGenerator → Can generate session files

**After Sprint 4:**
- Run `/update-deliverables` (git metrics)
- Update `communication.json` → set your status to "complete"
- Create `creator-deliverables.md`
- Notify orchestrator

---

## Reference Files

**Session Files:**
- Communication: `C:\Users\willh\.mcp-servers\coderef\sessions\sessions-hub-phase2-multiagent\communication.json`
- Instructions: `C:\Users\willh\.mcp-servers\coderef\sessions\sessions-hub-phase2-multiagent\instructions.json`

**Existing Patterns:**
- `C:\Users\willh\Desktop\coderef-dashboard\packages\dashboard\src\components\PromptingWorkflow\`

**Target Project:**
- `C:\Users\willh\Desktop\coderef-dashboard\`

---

## Success Criteria

✅ User can select stub
✅ User can write multi-block instructions with type tags
✅ User can attach foundation docs and archived features
✅ User can assign instructions/attachments to agents
✅ User can generate session files (context-backbone.md, communication.json, instructions.json)
✅ No forbidden file violations

---

**You are Agent 1 of 3. Work independently. Agent 2 (Monitor) is working in parallel on SessionMonitoring/. Agent 3 (Integration) will combine your work after you're both done.**

Good luck! 🎨
