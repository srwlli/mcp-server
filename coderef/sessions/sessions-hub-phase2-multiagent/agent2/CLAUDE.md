# Agent 2: Sessions Hub Monitor

**Workorder:** WO-SESSIONS-HUB-002-MONITOR
**Role:** Build System 2 (Session Monitoring)
**Sprint:** 5 (Session Reader + Monitor UI)
**Project:** coderef-dashboard
**Output Directory:** `C:\Users\willh\Desktop\coderef-dashboard\packages\dashboard\src\components\SessionsHub\SessionMonitoring\`

---

## Phase 0: Research & Onboarding (START HERE)

**BEFORE WRITING ANY CODE**, research the project context and understand the design.

### Step 1: Read Phase 1 Design Documents

**Location:** `C:\Users\willh\Desktop\coderef-dashboard\.coderef\sessions\sessions-hub-phase1\`

**Required Reading:**
1. **dashboard-audit-v2.md** - Comprehensive Phase 1 design spec
   - System 2 (Session Monitoring) detailed specification
   - Component hierarchy and data flow
   - UI mockups and user flows
   - SessionReader API design

2. **orchestrator-phase1-audit-v2.md** - Approved design document
   - Design decisions and rationale
   - Technical constraints
   - Quality standards

3. **ARCHITECTURE-DIAGRAM.md** (if exists) - System architecture
4. **SUMMARY.md** (if exists) - Phase 1 outcomes

**What to Look For:**
- What SessionMonitoring components were designed?
- How should SessionReader API work?
- What data structures are expected?
- What real-time update patterns were planned?

### Step 2: Read Foundation Documentation

**Location:** `C:\Users\willh\Desktop\coderef-dashboard\`

**Required Reading:**
1. **ARCHITECTURE.md** - Project architecture patterns
   - Next.js API route conventions
   - File system access patterns
   - Real-time data fetching (SWR)
   - Component organization

2. **COMPONENTS.md** - Existing component library
   - What list/grid components exist?
   - What modal/preview components exist?
   - What status badge components exist?

3. **SCHEMA.md** (if exists) - Data schemas
   - communication.json format
   - Session data structures

### Step 3: Study Test Data

**Location:** `C:\Users\willh\.mcp-servers\coderef\sessions\`

**Examine Existing Sessions:**
- `leveraging-coderef-system/communication.json` - Live example
- `sessions-hub-phase1/` (if exists) - Phase 1 session data
- Understand communication.json structure
- Identify edge cases (blocked agents, parallel execution, etc.)

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
- `plan.json` - Your sprint implementation plan
- TodoWrite checklist - Trackable tasks

### Step 5: Validate Against Design

Before coding, verify:
- ✅ Your plan matches Phase 1 design specs
- ✅ SessionReader API matches design document
- ✅ Component structure aligns with design
- ✅ Real-time patterns follow Next.js conventions

**Output:** Create `research-summary.md` documenting:
- Key findings from Phase 1 design
- SessionReader API implementation approach
- Component structure plan
- Test data analysis

---

## Your Mission

Build the **Session Monitoring** system that allows users to:
1. View list of all active sessions
2. View session details (orchestrator + agents)
3. Track agent progress in real-time
4. View agent output files
5. Monitor session completion status

---

## Critical Constraints

### Forbidden Files
**YOU MUST NOT TOUCH THESE FILES:**
- `packages/dashboard/src/components/SessionsHub/SessionCreation/**`
- `packages/dashboard/src/api/sessions/create/**`

These belong to Agent 1 (Creator). File conflicts will break parallel execution.

### Your Territory
**YOU OWN THESE DIRECTORIES:**
- `packages/dashboard/src/components/SessionsHub/SessionMonitoring/`
- `packages/dashboard/src/lib/api/sessions.ts`

---

## Sprint 5: Session Reader + Monitor UI

**Components to Build:**

### 1. SessionReader API (`src/lib/api/sessions.ts`)

**Purpose:** Read session directories and parse communication.json files

**Functions:**
```typescript
// Scan all session directories
export async function getAllSessions(): Promise<Session[]> {
  // Scan C:\Users\willh\.mcp-servers\coderef\sessions\
  // Read each communication.json
  // Return array of sessions
}

// Get single session details
export async function getSessionById(sessionId: string): Promise<SessionDetail> {
  // Read communication.json
  // Parse orchestrator + agents
  // Return full session object
}

// Get agent output file
export async function getAgentOutput(sessionId: string, agentId: string): Promise<string> {
  // Read agent's output_file from communication.json
  // Return file contents
}

// Refresh session status (polling endpoint)
export async function refreshSessionStatus(sessionId: string): Promise<SessionStatus> {
  // Re-read communication.json
  // Return updated aggregation counts
}
```

**Data Structures:**
```typescript
interface Session {
  workorder_id: string;
  feature_name: string;
  status: 'not_started' | 'in_progress' | 'complete';
  created: string;
  description: string;
  total_agents: number;
  completed_agents: number;
}

interface SessionDetail extends Session {
  orchestrator: OrchestratorInfo;
  agents: AgentInfo[];
  parallel_execution?: ParallelExecutionInfo;
}

interface AgentInfo {
  agent_id: string;
  workorder_id?: string;
  role: string;
  status: 'not_started' | 'in_progress' | 'complete' | 'blocked';
  output_file: string;
  phases?: string[];
  notes: string;
}
```

---

### 2. SessionsList Component (`SessionMonitoring/SessionsList.tsx`)

**Purpose:** Display all active sessions in a list/grid view

**Features:**
- List all sessions from `getAllSessions()`
- Display: workorder ID, feature name, status badge, progress (X/Y agents complete)
- Status badges:
  - 🟡 Not Started (yellow)
  - 🔵 In Progress (blue)
  - 🟢 Complete (green)
- Search/filter by workorder ID or feature name
- Click session → navigate to SessionDetail
- Real-time updates (poll every 10 seconds using SWR)

**Layout:**
```
┌─────────────────────────────────────────────┐
│ Active Sessions (5)                         │
├─────────────────────────────────────────────┤
│ [Search: ___________________________]       │
│                                             │
│ ┌─────────────────────────────────────────┐ │
│ │ 🔵 WO-SESSIONS-HUB-002                  │ │
│ │ sessions-hub-phase2-multiagent          │ │
│ │ Agents: 1/3 complete                    │ │
│ │ Created: 2026-01-11                     │ │
│ └─────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────┐ │
│ │ 🟢 WO-DOCUMENT-EFFECTIVENESS-001        │ │
│ │ document-effectiveness                  │ │
│ │ Agents: 9/9 complete                    │ │
│ │ Created: 2026-01-10                     │ │
│ └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

---

### 3. SessionDetail Component (`SessionMonitoring/SessionDetail.tsx`)

**Purpose:** Display detailed view of a single session

**Features:**
- Orchestrator panel (top)
- Agents grid (below orchestrator)
- Real-time status updates (poll every 10 seconds)
- "Refresh" button for manual update

**Layout:**
```
┌───────────────────────────────────────────────────────┐
│ Session: sessions-hub-phase2-multiagent               │
│ WO-SESSIONS-HUB-002 | Status: 🔵 In Progress          │
├───────────────────────────────────────────────────────┤
│                                                       │
│ Orchestrator: coderef-assistant                       │
│ Role: Coordinate parallel execution                  │
│ Status: 🔵 In Progress                                │
│ Output: orchestrator-output.json [View]              │
│                                                       │
├───────────────────────────────────────────────────────┤
│                                                       │
│ Agents (3)                                            │
│                                                       │
│ ┌────────────┐ ┌────────────┐ ┌────────────┐        │
│ │ Agent 1    │ │ Agent 2    │ │ Agent 3    │        │
│ │ Creator    │ │ Monitor    │ │ Integration│        │
│ │ 🟢 Complete│ │ 🔵 Progress│ │ 🟡 Blocked │        │
│ │ [View]     │ │ [View]     │ │            │        │
│ └────────────┘ └────────────┘ └────────────┘        │
└───────────────────────────────────────────────────────┘
```

---

### 4. AgentCard Component (`SessionMonitoring/AgentCard.tsx`)

**Purpose:** Display individual agent info in SessionDetail

**Features:**
- Agent ID + workorder ID (if present)
- Role description
- Status badge
- Phases (if present) with checkboxes
- Output file link → opens OutputViewer
- Notes (if present)

**Layout:**
```
┌─────────────────────────────────────┐
│ coderef-dashboard-creator           │
│ WO-SESSIONS-HUB-002-CREATOR         │
├─────────────────────────────────────┤
│ Role: Build System 1 (Creation)     │
│ Status: 🟢 Complete                 │
│                                     │
│ Phases:                             │
│ ✅ Sprint 1: Stub + Instructions    │
│ ✅ Sprint 2: Attachments            │
│ ✅ Sprint 3: Agent Assignment       │
│ ✅ Sprint 4: Session Generation     │
│                                     │
│ Output: creator-deliverables.md     │
│ [View Output]                       │
│                                     │
│ Notes: Completed all components     │
└─────────────────────────────────────┘
```

---

### 5. OutputViewer Component (`SessionMonitoring/OutputViewer.tsx`)

**Purpose:** Display agent output files in a modal

**Features:**
- Modal component
- Load file contents using `getAgentOutput()`
- Detect file type (JSON, markdown, text)
- Render appropriately:
  - JSON: Syntax highlighting
  - Markdown: Rendered preview
  - Text: Plain text display
- Download button
- Close button

---

## Test Data

**Use existing session examples:**
- `C:\Users\willh\.mcp-servers\coderef\sessions\leveraging-coderef-system\communication.json`
- `C:\Users\willh\Desktop\coderef-dashboard\.coderef\sessions\sessions-hub-phase1\` (if exists)

You don't need Agent 1 (Creator) to finish before you can build. Use existing communication.json files to test your Monitor UI.

---

## Deliverables Checklist

When you complete Sprint 5, create this file:

**File:** `C:\Users\willh\.mcp-servers\coderef\sessions\sessions-hub-phase2-multiagent\monitor-deliverables.md`

```markdown
# Monitor Agent Deliverables

## Components Created
- SessionMonitoring/SessionsList.tsx
- SessionMonitoring/SessionDetail.tsx
- SessionMonitoring/AgentCard.tsx
- SessionMonitoring/OutputViewer.tsx
- SessionMonitoring/index.tsx (container)

## API Functions Created
- src/lib/api/sessions.ts:
  - getAllSessions()
  - getSessionById()
  - getAgentOutput()
  - refreshSessionStatus()

## Files Modified
- (list any existing files you modified)

## Challenges
- (document any challenges and solutions)

## Forbidden File Compliance
✅ No files in SessionCreation/ directory touched
✅ No modifications to packages/dashboard/src/api/sessions/create/

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
  feature_name: "sessions-hub-monitor",
  description: "Build Session Monitoring system (Sprint 5)",
  goal: "Enable users to monitor multi-agent session progress in real-time",
  requirements: [
    "SessionReader API to scan and parse session directories",
    "SessionsList component with real-time updates",
    "SessionDetail component showing orchestrator + agents",
    "AgentCard component for individual agent status",
    "OutputViewer modal for agent output files"
  ],
  constraints: [
    "Cannot modify SessionCreation/ directory (Agent 1's territory)",
    "Must follow Phase 1 design specs",
    "Must use SWR for real-time polling"
  ]
})
```

2. **Create Plan** (generates plan.json):
```typescript
mcp__coderef-workflow__create_plan({
  project_path: "C:\\Users\\willh\\Desktop\\coderef-dashboard",
  feature_name: "sessions-hub-monitor",
  workorder_id: "WO-SESSIONS-HUB-002-MONITOR"
})
```

3. **Execute Plan** (generates TodoWrite checklist):
```typescript
mcp__coderef-workflow__execute_plan({
  project_path: "C:\\Users\\willh\\Desktop\\coderef-dashboard",
  feature_name: "sessions-hub-monitor"
})
```

**This creates:**
- `coderef/workorder/sessions-hub-monitor/context.json`
- `coderef/workorder/sessions-hub-monitor/plan.json`
- TodoWrite task list in your IDE

---

## Phase Progression

1. **Phase 0:** Research (read docs, examine test data)
2. **Phase 1:** Planning (gather_context → create_plan → execute_plan)
3. **Build SessionReader API** → Can read session directories and parse communication.json
4. **Build SessionsList** → Can display all sessions
5. **Build SessionDetail** → Can display session details
6. **Build AgentCard** → Can display agent info
7. **Build OutputViewer** → Can preview agent output files

**After Sprint 5:**
- Run `/update-deliverables` (git metrics)
- Update `communication.json` → set your status to "complete"
- Create `monitor-deliverables.md`
- Notify orchestrator

---

## Reference Files

**Session Files:**
- Communication: `C:\Users\willh\.mcp-servers\coderef\sessions\sessions-hub-phase2-multiagent\communication.json`
- Instructions: `C:\Users\willh\.mcp-servers\coderef\sessions\sessions-hub-phase2-multiagent\instructions.json`

**Test Data:**
- `C:\Users\willh\.mcp-servers\coderef\sessions\leveraging-coderef-system\communication.json`

**Target Project:**
- `C:\Users\willh\Desktop\coderef-dashboard\`

---

## Success Criteria

✅ Can view list of all sessions
✅ Can view session details with orchestrator + agents
✅ Can see agent progress in real-time (polling)
✅ Can view agent output files
✅ Status badges work (not_started, in_progress, complete, blocked)
✅ No forbidden file violations

---

**You are Agent 2 of 3. Work independently. Agent 1 (Creator) is working in parallel on SessionCreation/. Agent 3 (Integration) will combine your work after you're both done.**

Good luck! 📊
