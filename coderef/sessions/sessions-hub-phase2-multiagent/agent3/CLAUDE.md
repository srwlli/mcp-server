# Agent 3: Sessions Hub Integration

**Workorder:** WO-SESSIONS-HUB-002-INTEGRATION
**Role:** Integrate Creator + Monitor Systems
**Sprint:** 6 (SessionsHub Container + Tab Navigation)
**Project:** coderef-dashboard
**Output Directory:** `C:\Users\willh\Desktop\coderef-dashboard\packages\dashboard\src\components\SessionsHub\`

---

## Phase 0: Research & Onboarding (START HERE)

**BEFORE WRITING ANY CODE**, research the project context and understand what Agent 1 and Agent 2 built.

### Step 1: Wait for Dependencies

**Check communication.json:**
```bash
cat C:\Users\willh\.mcp-servers\coderef\sessions\sessions-hub-phase2-multiagent\communication.json
```

**Verify:**
- ✅ Agent 1 (coderef-dashboard-creator) status = "complete"
- ✅ Agent 2 (coderef-dashboard-monitor) status = "complete"

**If NOT complete, STOP HERE. You are blocked.**

### Step 2: Read Agent Deliverables

**Required Reading:**
1. **creator-deliverables.md** - What Agent 1 built
   - Components created
   - API routes created
   - File structure

2. **monitor-deliverables.md** - What Agent 2 built
   - Components created
   - SessionReader API implementation
   - File structure

**What to Look For:**
- What are the entry points? (SessionCreation/index.tsx, SessionMonitoring/index.tsx)
- What props do these components expect?
- What state management do they use?
- What dependencies do they have?

### Step 3: Read Phase 1 Design Documents

**Location:** `C:\Users\willh\Desktop\coderef-dashboard\.coderef\sessions\sessions-hub-phase1\`

**Required Reading:**
1. **dashboard-audit-v2.md** - Phase 1 design
   - SessionsHub container specification
   - Tab navigation design
   - Integration requirements

2. **orchestrator-phase1-audit-v2.md** - Approved design
   - Integration quality standards
   - Testing requirements

### Step 4: Read Foundation Documentation

**Location:** `C:\Users\willh\Desktop\coderef-dashboard\`

**Required Reading:**
1. **ARCHITECTURE.md** - Project architecture
   - Next.js routing patterns
   - Page structure conventions
   - Navigation integration

2. **COMPONENTS.md** - Component patterns
   - How are tabs implemented elsewhere?
   - What navigation components exist?

### Step 5: Inspect Agent 1 and Agent 2 Code

**Manually review:**
- `packages/dashboard/src/components/SessionsHub/SessionCreation/index.tsx`
- `packages/dashboard/src/components/SessionsHub/SessionMonitoring/index.tsx`

**Understand:**
- What props do they export?
- What dependencies do they import?
- How do they manage state?
- Are there any integration hooks?

### Step 6: Create Your Implementation Plan

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
- `context.json` - Your understanding of integration requirements
- `plan.json` - Your integration plan
- TodoWrite checklist - Trackable tasks

### Step 7: Validate Integration Plan

Before coding, verify:
- ✅ Tab navigation matches Phase 1 design
- ✅ Component imports align with Agent 1 + Agent 2 exports
- ✅ URL routing follows Next.js conventions
- ✅ End-to-end flow is clear

**Output:** Create `research-summary.md` documenting:
- Agent 1 deliverables summary
- Agent 2 deliverables summary
- Integration points identified
- Testing plan

---

## Your Mission

Integrate the **Session Creation** (Agent 1) and **Session Monitoring** (Agent 2) systems into a unified SessionsHub interface with tab navigation.

---

## Critical Dependency

**YOU ARE BLOCKED UNTIL:**
- ✅ Agent 1 (Creator) status = "complete"
- ✅ Agent 2 (Monitor) status = "complete"

Check `communication.json` to verify both agents finished before starting.

---

## No Forbidden Files

You have access to ALL SessionsHub files because you're integrating both systems.

**Your Territory:**
- `packages/dashboard/src/components/SessionsHub/` (root level only)
- Can import from `SessionCreation/` (Agent 1's work)
- Can import from `SessionMonitoring/` (Agent 2's work)

---

## Sprint 6: Integration + Tab Navigation

**Components to Build:**

### 1. SessionsHub Container (`SessionsHub/index.tsx`)

**Purpose:** Top-level component with tab navigation

**Features:**
- Tab navigation: "Create Session" | "Monitor Sessions"
- Tab state management (URL params or local state)
- Render SessionCreation (Agent 1) or SessionMonitoring (Agent 2) based on active tab
- Breadcrumb navigation
- Integration with PromptingWorkflow (if needed)

**Layout:**
```
┌─────────────────────────────────────────────────────┐
│ Sessions Hub                                        │
├─────────────────────────────────────────────────────┤
│ [Create Session] [Monitor Sessions] ← TAB NAV      │
├─────────────────────────────────────────────────────┤
│                                                     │
│ {Active Tab Content}                                │
│                                                     │
│ Tab 1: SessionCreation/                             │
│   → StubSelector                                    │
│   → InstructionEditor                               │
│   → AttachmentManager                               │
│   → AgentAssigner                                   │
│   → SessionGenerator                                │
│                                                     │
│ Tab 2: SessionMonitoring/                           │
│   → SessionsList                                    │
│   → SessionDetail (when session selected)           │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Code Structure:**
```typescript
import { SessionCreation } from './SessionCreation';
import { SessionMonitoring } from './SessionMonitoring';

export function SessionsHub() {
  const [activeTab, setActiveTab] = useState<'create' | 'monitor'>('create');

  return (
    <div className="sessions-hub">
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="create">Create Session</TabsTrigger>
          <TabsTrigger value="monitor">Monitor Sessions</TabsTrigger>
        </TabsList>

        <TabsContent value="create">
          <SessionCreation />
        </TabsContent>

        <TabsContent value="monitor">
          <SessionMonitoring />
        </TabsContent>
      </Tabs>
    </div>
  );
}
```

---

### 2. SessionsHub Route (`app/sessions/page.tsx`)

**Purpose:** Next.js page route for `/sessions`

**Features:**
- Import SessionsHub container
- Add page metadata (title, description)
- Handle authentication (if required)

**Code:**
```typescript
import { SessionsHub } from '@/components/SessionsHub';

export const metadata = {
  title: 'Sessions Hub | CodeRef Dashboard',
  description: 'Create and monitor multi-agent sessions',
};

export default function SessionsPage() {
  return <SessionsHub />;
}
```

---

### 3. Navigation Integration

**Update:** Main navigation to include Sessions Hub link

**Files to Modify:**
- Navigation component (find in `src/components/` or `app/`)
- Add link: "Sessions" → `/sessions`
- Icon: 🎯 or similar

---

### 4. Cross-System Integration

**SessionCreationComplete → SessionMonitoring Navigation:**

When user completes session creation (Agent 1's SessionCreationComplete component), provide button to navigate to Monitor tab:

```typescript
// In SessionCreationComplete.tsx (Agent 1's component)
<Button onClick={() => router.push('/sessions?tab=monitor')}>
  View in Session Monitor
</Button>
```

This requires URL param handling in SessionsHub:

```typescript
const searchParams = useSearchParams();
const initialTab = searchParams.get('tab') === 'monitor' ? 'monitor' : 'create';
const [activeTab, setActiveTab] = useState(initialTab);
```

---

### 5. End-to-End Testing

**Test Flow:**

1. **Create Session Flow:**
   - Navigate to `/sessions` → Create tab
   - Select stub (STUB-082)
   - Write instructions (add 2 blocks)
   - Attach foundation doc (ARCHITECTURE.md)
   - Assign blocks to Agent 1
   - Generate session
   - Verify files created in `C:\Users\willh\.mcp-servers\coderef\sessions\{session-name}\`

2. **Monitor Session Flow:**
   - Click "View in Session Monitor" button
   - Verify navigates to Monitor tab
   - Verify new session appears in SessionsList
   - Click session → verify SessionDetail shows orchestrator + agents
   - Click agent → verify AgentCard shows details
   - Click "View Output" → verify OutputViewer opens

3. **Tab Navigation:**
   - Switch between Create and Monitor tabs
   - Verify state persists (if needed)
   - Verify URL updates (if using URL params)

---

## Deliverables Checklist

When you complete Sprint 6, create this file:

**File:** `C:\Users\willh\.mcp-servers\coderef\sessions\sessions-hub-phase2-multiagent\integration-deliverables.md`

```markdown
# Integration Agent Deliverables

## Components Created
- SessionsHub/index.tsx (container with tab navigation)
- app/sessions/page.tsx (Next.js route)

## Files Modified
- Navigation component (added Sessions link)
- SessionCreationComplete.tsx (added Monitor tab link)
- SessionsHub/index.tsx (URL param handling for tab state)

## Integration Points
- ✅ SessionCreation → SessionMonitoring navigation works
- ✅ Tab navigation working (Create | Monitor)
- ✅ /sessions route accessible
- ✅ Sessions link in main navigation

## End-to-End Test Results
- ✅ Create session flow works
- ✅ Monitor session flow works
- ✅ Tab switching works
- ✅ Cross-tab navigation works

## Challenges
- (document any challenges and solutions)

## Status
Complete
```

---

## Workflow: Research → Plan → Execute

### After Phase 0 Research (and Agent 1 + Agent 2 Complete)

**Use coderef-workflow MCP tools to create your workorder:**

1. **Gather Context** (creates context.json):
```typescript
mcp__coderef-workflow__gather_context({
  project_path: "C:\\Users\\willh\\Desktop\\coderef-dashboard",
  feature_name: "sessions-hub-integration",
  description: "Integrate SessionCreation and SessionMonitoring systems (Sprint 6)",
  goal: "Provide unified SessionsHub interface with tab navigation",
  requirements: [
    "SessionsHub container component with Create/Monitor tabs",
    "/sessions Next.js page route",
    "Navigation integration (add Sessions link to main nav)",
    "Cross-tab navigation (Create → Monitor)",
    "End-to-end flow testing"
  ],
  constraints: [
    "Blocked until Agent 1 and Agent 2 complete",
    "Must follow Phase 1 design specs",
    "Must integrate cleanly with PromptingWorkflow"
  ]
})
```

2. **Create Plan** (generates plan.json):
```typescript
mcp__coderef-workflow__create_plan({
  project_path: "C:\\Users\\willh\\Desktop\\coderef-dashboard",
  feature_name: "sessions-hub-integration",
  workorder_id: "WO-SESSIONS-HUB-002-INTEGRATION"
})
```

3. **Execute Plan** (generates TodoWrite checklist):
```typescript
mcp__coderef-workflow__execute_plan({
  project_path: "C:\\Users\\willh\\Desktop\\coderef-dashboard",
  feature_name: "sessions-hub-integration"
})
```

**This creates:**
- `coderef/workorder/sessions-hub-integration/context.json`
- `coderef/workorder/sessions-hub-integration/plan.json`
- TodoWrite task list in your IDE

---

## Phase Progression

1. **Phase 0:** Research (read Agent 1 + Agent 2 deliverables, understand Phase 1 design)
2. **Phase 1:** Planning (gather_context → create_plan → execute_plan)
3. **Verify Dependencies** → Check Agent 1 + Agent 2 status = "complete"
4. **Build SessionsHub Container** → Tab navigation working
5. **Add /sessions Route** → Page accessible
6. **Integrate Navigation** → Sessions link in main nav
7. **Test End-to-End** → Full flow works
8. **Document Deliverables** → Create integration-deliverables.md

**After Sprint 6:**
- Run `/update-deliverables` (git metrics)
- Update `communication.json` → set your status to "complete"
- Create `integration-deliverables.md`
- Notify orchestrator

---

## Reference Files

**Session Files:**
- Communication: `C:\Users\willh\.mcp-servers\coderef\sessions\sessions-hub-phase2-multiagent\communication.json`
- Instructions: `C:\Users\willh\.mcp-servers\coderef\sessions\sessions-hub-phase2-multiagent\instructions.json`

**Agent 1 Deliverables:**
- `C:\Users\willh\.mcp-servers\coderef\sessions\sessions-hub-phase2-multiagent\creator-deliverables.md`

**Agent 2 Deliverables:**
- `C:\Users\willh\.mcp-servers\coderef\sessions\sessions-hub-phase2-multiagent\monitor-deliverables.md`

**Target Project:**
- `C:\Users\willh\Desktop\coderef-dashboard\`

---

## Success Criteria

✅ SessionsHub container with tab navigation working
✅ /sessions route accessible
✅ Sessions link in main navigation
✅ Create → Monitor cross-navigation works
✅ End-to-end flow tested successfully
✅ All components from Agent 1 + Agent 2 integrated

---

## Dependencies Check

**Before you start, verify:**

```bash
# Read communication.json
cat C:\Users\willh\.mcp-servers\coderef\sessions\sessions-hub-phase2-multiagent\communication.json

# Check Agent 1 status
"coderef-dashboard-creator": { "status": "complete" } ✅

# Check Agent 2 status
"coderef-dashboard-monitor": { "status": "complete" } ✅

# If both complete, you're unblocked. Start Sprint 6.
```

---

**You are Agent 3 of 3. Wait for Agent 1 and Agent 2 to finish, then integrate both systems into a unified SessionsHub interface.**

Good luck! 🔗
