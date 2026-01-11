# Agent 2 Research Summary - Session Monitoring

**Agent:** coderef-dashboard-monitor
**Workorder:** WO-SESSIONS-HUB-002-MONITOR
**Date:** 2026-01-11
**Status:** Research Complete

---

## Key Findings from Phase 1 Design

### System 2: Session Monitoring Overview

**Purpose:** Real-time tracking and visualization of active/completed multi-agent sessions

**Core Components to Build:**
1. **SessionReader API** (`src/lib/api/sessions.ts`)
   - Scan session directories
   - Parse communication.json files
   - Return structured session data
   - Provide real-time status updates

2. **SessionsList Component** - Browse all sessions with filters
3. **SessionDetail Component** - Display orchestrator + agents + status
4. **AgentCard Component** - Individual agent status cards
5. **OutputViewer Component** - Modal to preview agent output files

**Data Sources:**
- `communication.json` - Session structure, agent roster, status
- `instructions.json` - Task definitions per agent
- `context-backbone.md` - Comprehensive context (future)
- Agent output files (*.json, *.md)

---

## SessionReader API Design

Based on Phase 1 specs and existing WorkorderReader pattern:

```typescript
// Core Functions
export async function getAllSessions(): Promise<Session[]> {
  // 1. Scan configured session directories
  // 2. Read each communication.json
  // 3. Calculate aggregation stats (total_agents, completed_agents)
  // 4. Return array of sessions
}

export async function getSessionById(sessionId: string): Promise<SessionDetail> {
  // 1. Find session directory
  // 2. Read communication.json + instructions.json
  // 3. Parse orchestrator + agents
  // 4. Return full session object
}

export async function getAgentOutput(sessionId: string, agentId: string): Promise<string> {
  // 1. Read agent's output_file path from communication.json
  // 2. Read file contents
  // 3. Return as string (caller handles format detection)
}

export async function refreshSessionStatus(sessionId: string): Promise<SessionStatus> {
  // 1. Re-read communication.json
  // 2. Recalculate aggregation counts
  // 3. Return updated status
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
  forbidden_files?: string[];
}
```

---

## Component Structure Plan

### SessionsList Component
- **Purpose:** Display all active sessions in a list/grid view
- **Features:**
  - List all sessions from `getAllSessions()`
  - Display: workorder ID, feature name, status badge, progress (X/Y agents)
  - Status badges: 🟡 Not Started, 🔵 In Progress, 🟢 Complete
  - Search/filter by workorder ID or feature name
  - Click session → navigate to SessionDetail
  - Real-time updates via polling (SWR, every 10 seconds)

### SessionDetail Component
- **Purpose:** Display detailed view of a single session
- **Features:**
  - Orchestrator panel (top)
  - Agents grid (below orchestrator)
  - Real-time status updates (poll every 10 seconds)
  - "Refresh" button for manual update
  - Display aggregation stats (X/Y agents complete)

### AgentCard Component
- **Purpose:** Display individual agent info in SessionDetail
- **Features:**
  - Agent ID + workorder ID (if present)
  - Role description
  - Status badge with color coding
  - Phases (if present) with checkboxes
  - Output file link → opens OutputViewer
  - Notes (if present)
  - Forbidden files list (if present)

### OutputViewer Component
- **Purpose:** Display agent output files in a modal
- **Features:**
  - Modal component (backdrop + close button)
  - Load file contents using `getAgentOutput()`
  - Detect file type (JSON, Markdown, text)
  - Render appropriately:
    - JSON: Syntax highlighting (consider highlight.js or prism.js)
    - Markdown: Rendered preview (react-markdown)
    - Text: Plain text display with monospace font
  - Download button
  - Close button

---

## Foundation Architecture Insights

From ARCHITECTURE.md:

**Key Patterns:**
- **File System Data Layer** - No database, read directly from files
- **API Routes** - Next.js App Router pattern (`src/app/api/`)
- **Component Structure** - Dashboard-specific components in `packages/dashboard/src/components/`
- **TypeScript Strict Mode** - Full type safety required
- **Tailwind CSS** - Use `ind-*` design tokens for theming
- **React Context** - For global state (theme, sidebar, projects, explorer)

**Existing Components to Reference:**
- **WorkorderCard** - Similar card pattern for SessionsList
- **StatsCard** - For displaying aggregation metrics
- **FilterBar** - If we need session filtering
- **UnifiedCard** - Base card component wrapper

**Styling Tokens:**
```css
--ind-bg: Background color
--ind-panel: Panel background
--ind-border: Border color
--ind-text: Primary text
--ind-text-muted: Muted text
--ind-accent: Accent color (dynamic)
--ind-success: Success state (green)
--ind-warning: Warning state (yellow)
--ind-error: Error state (red)
```

---

## Test Data Analysis

Examined `communication.json` from current session:

**Structure:**
- `workorder_id`: "WO-SESSIONS-HUB-002"
- `feature_name`: "sessions-hub-phase2-multiagent"
- `status`: "not_started" | "in_progress" | "complete"
- `orchestrator`: Object with agent_id, role, output_file, status
- `agents`: Array of agent objects
- `parallel_execution`: Object with enabled, can_run_simultaneously, must_run_sequentially
- `aggregation`: Object with total_agents, completed, in_progress, not_started, blocked

**Agent Object Structure:**
- `agent_id`: "coderef-dashboard-monitor"
- `workorder_id`: "WO-SESSIONS-HUB-002-MONITOR"
- `role`: "Build System 2 (Session Monitoring) - Sprint 5"
- `phases`: Array of phase names
- `output_file`: Path to deliverables
- `forbidden_files`: Array of file patterns
- `status`: Agent status
- `notes`: Agent notes
- `depends_on`: Array of agent IDs (optional)

**Aggregation Calculation:**
- Count agents by status
- Calculate progress percentage
- Identify blocked agents

---

## SessionReader Implementation Approach

**Pattern:** Follow existing WorkorderReader pattern from dashboard

1. **Directory Scanning:**
   - Scan configured session directories (add to `projects.config.json`)
   - Use Node.js `fs` module for file system access
   - Read all `communication.json` files

2. **Data Parsing:**
   - Use `JSON.parse()` with try/catch
   - Validate required fields
   - Handle missing/malformed files gracefully

3. **Aggregation:**
   - Count agents by status (not_started, in_progress, complete, blocked)
   - Calculate completion percentage
   - Return structured data

4. **Error Handling:**
   - Log errors to console (development)
   - Return partial data if some files fail
   - Never throw errors that break the UI

---

## Real-Time Update Strategy

**Phase 1 (MVP):** Manual refresh button
**Phase 2:** Polling with SWR
**Phase 3:** WebSocket integration (future)

**SWR Configuration:**
```typescript
import useSWR from 'swr';

const { data, error, mutate } = useSWR(
  `/api/sessions/${sessionId}`,
  fetcher,
  {
    refreshInterval: 10000, // Poll every 10 seconds
    revalidateOnFocus: true,
    revalidateOnReconnect: true
  }
);
```

---

## Forbidden File Compliance

**CRITICAL: I MUST NOT TOUCH:**
- `packages/dashboard/src/components/SessionsHub/SessionCreation/**`
- `packages/dashboard/src/api/sessions/create/**`

These belong to Agent 1 (Creator). Any modifications will cause file conflicts.

**MY TERRITORY:**
- `packages/dashboard/src/components/SessionsHub/SessionMonitoring/`
- `packages/dashboard/src/lib/api/sessions.ts`

---

## Component Location Plan

Based on existing structure and design specs:

```
packages/dashboard/src/
├── lib/
│   └── api/
│       └── sessions.ts              # NEW: SessionReader API functions
├── components/
│   └── SessionsHub/
│       └── SessionMonitoring/       # NEW: My directory
│           ├── SessionsList.tsx     # NEW: List all sessions
│           ├── SessionDetail.tsx    # NEW: Session detail view
│           ├── AgentCard.tsx        # NEW: Agent status card
│           ├── OutputViewer.tsx     # NEW: Output file modal
│           └── index.tsx            # NEW: Container/exports
└── app/
    └── api/
        └── sessions/
            └── route.ts             # NEW: GET /api/sessions (optional)
```

**Alternative:** SessionReader could be a standalone file or part of existing API structure.

---

## Next Steps (Phase 1: Planning)

1. ✅ **Research Complete** - Read design docs, foundation docs, test data
2. ⏭️ **Gather Context** - Use `mcp__coderef-workflow__gather_context`
3. ⏭️ **Create Plan** - Use `mcp__coderef-workflow__create_plan`
4. ⏭️ **Execute Plan** - Use `mcp__coderef-workflow__execute_plan`

This will create:
- `coderef/workorder/sessions-hub-monitor/context.json`
- `coderef/workorder/sessions-hub-monitor/plan.json`
- TodoWrite task list

---

## Success Criteria Checklist

From CLAUDE.md instructions:

- [ ] Can view list of all sessions
- [ ] Can view session details with orchestrator + agents
- [ ] Can see agent progress in real-time (polling)
- [ ] Can view agent output files
- [ ] Status badges work (not_started, in_progress, complete, blocked)
- [ ] No forbidden file violations

---

## Questions & Decisions

**Q:** Should SessionReader be an API route or a library function?
**A:** Library function in `src/lib/api/sessions.ts` - can be used by both API routes and client components

**Q:** How to handle missing output files?
**A:** Display "No output yet" message instead of error

**Q:** Should we display context-backbone.md?
**A:** Not in Sprint 5 - focus on core monitoring. Can add in Sprint 6 or future enhancement.

**Q:** Real-time updates from the start?
**A:** Start with manual refresh button, add SWR polling in same sprint if time permits

---

## Estimated Effort

**Sprint 5 Breakdown (from Phase 1 design):**
- SessionReader API: 3-4 hours
- SessionsList component: 2-3 hours
- SessionDetail component: 2-3 hours
- AgentCard component: 1-2 hours
- OutputViewer modal: 2 hours
- **Total: 10-12 hours**

---

**Research Status:** ✅ Complete
**Next Action:** Proceed to Phase 1 Planning with coderef-workflow tools
