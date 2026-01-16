# Agent Onboarding Ready - Phase 1

**Session:** WO-SCANNER-CONTEXT-ENHANCEMENT-001
**Date:** 2026-01-14
**Status:** ✅ Agent directories created, ready for onboarding

---

## ✅ What's Been Created

### Session Structure
```
C:\Users\willh\.mcp-servers\coderef\sessions\scanner-context-enhancement\
│
├── Session-level coordination
│   ├── communication.json (master roster)
│   ├── instructions.json (master orchestrator instructions)
│   ├── README.md (session overview)
│   ├── scanner-complete-context.md (master plan)
│   ├── phase1-progress.md (progress tracking)
│   ├── phase2-integration-targets.md (5 integration targets)
│   └── INTEGRATION-SUMMARY.md (quick reference)
│
├── coderef-context/ (Agent 1)
│   ├── communication.json (agent-specific tasks)
│   ├── instructions.json (detailed execution steps)
│   ├── resources/
│   │   └── index.md (links to all source documents)
│   └── outputs/ (agent creates outputs here)
│
└── coderef-core/ (Agent 2)
    ├── communication.json (agent-specific tasks)
    ├── instructions.json (detailed execution steps)
    ├── resources/
    │   └── index.md (links to all source documents)
    └── outputs/ (agent creates outputs here)
```

---

## 🎯 Agent 1: coderef-context

**Location:** `C:\Users\willh\.mcp-servers\coderef\sessions\scanner-context-enhancement\coderef-context\`

**Agent Home:** `C:\Users\willh\.mcp-servers\coderef-context`

**Tasks:** 7 (1 complete, 6 remaining)
1. ✅ Auto-include visual_architecture (commit 69aafd0)
2. ⏳ Add elements_by_type breakdown
3. ⏳ Add complexity_hotspots array
4. ⏳ Add documentation_summary
5. ⏳ Populate patterns.json
6. ⏳ Populate validation.json
7. ⏳ Create complexity.json

**Files Created:**
- ✅ `communication.json` - Task tracking, success metrics
- ✅ `instructions.json` - Detailed execution steps, code examples, context.json template
- ✅ `resources/index.md` - Links to CONTEXT-LEVERAGE-ANALYSIS.md, PROOF-OF-ENHANCEMENT.md, session docs

**What Agent Needs to Do:**
1. Navigate to `C:\Users\willh\.mcp-servers\coderef\sessions\scanner-context-enhancement\coderef-context\`
2. Read `resources/index.md` to understand all resources
3. Read `instructions.json` for detailed task specs
4. Use context.json template from instructions.json
5. Run `/create-workorder` in coderef-context project
6. Execute tasks 2-7
7. Create output in `outputs/coderef-context-phase1-output.json`
8. Update `communication.json` after each task

**Success Criteria:**
- Context quality: 40% → 95%
- Tool calls: 6 → 1
- Response time: ≤ 0.1s

---

## 🎯 Agent 2: coderef-core

**Location:** `C:\Users\willh\.mcp-servers\coderef\sessions\scanner-context-enhancement\coderef-core\`

**Agent Home:** `C:\Users\willh\Desktop\coderef-dashboard\packages\coderef-core`

**Tasks:** 4 quick wins (22 hours total)
1. ⏳ Pattern ordering (+15% performance)
2. ⏳ Configuration presets (30 sec setup)
3. ⏳ Structured error reporting (3x faster debugging)
4. ⏳ Python pattern expansion (+30% coverage)

**Files Created:**
- ✅ `communication.json` - Task tracking, success metrics
- ✅ `instructions.json` - Detailed execution steps, code examples, testing requirements
- ✅ `resources/index.md` - Links to Scanner-Effectiveness-Improvements-RESOURCE-SHEET.md, session docs

**What Agent Needs to Do:**
1. Navigate to `C:\Users\willh\.mcp-servers\coderef\sessions\scanner-context-enhancement\coderef-core\`
2. Read `resources/index.md` to understand all resources
3. Read `instructions.json` for detailed task specs
4. Use context.json template from instructions.json
5. Run `/create-workorder` in coderef-core project
6. Execute 4 quick wins sequentially
7. Test each quick win (benchmarks, accuracy, UX)
8. Create output in `outputs/coderef-dashboard-phase1-output.md`
9. Update `communication.json` after each quick win

**Success Criteria:**
- Scanner performance: +15%
- Configuration time: 30 sec (vs 15-30 min)
- Error resolution: 5-7 min (vs 20 min)
- Python patterns: 7 (vs 3)

---

## 🚀 Next Steps: Onboard Agents

### Option 1: User Onboards Manually

**For coderef-context agent:**
1. Open terminal in `C:\Users\willh\.mcp-servers\coderef-context`
2. Start Claude Code session
3. Say: "I'm working on session WO-SCANNER-CONTEXT-ENHANCEMENT-001. Read C:\Users\willh\.mcp-servers\coderef\sessions\scanner-context-enhancement\coderef-context\instructions.json and execute the tasks."

**For coderef-core agent:**
1. Open terminal in `C:\Users\willh\Desktop\coderef-dashboard\packages\coderef-core`
2. Start Claude Code session
3. Say: "I'm working on session WO-SCANNER-CONTEXT-ENHANCEMENT-001. Read C:\Users\willh\.mcp-servers\coderef\sessions\scanner-context-enhancement\coderef-core\instructions.json and execute the tasks."

---

### Option 2: Orchestrator Generates Handoff Prompts

I can generate ready-to-paste handoff prompts for each agent that include:
- Session context
- Link to their directory
- Step-by-step instructions
- Success criteria

**Would you like me to generate these prompts?**

---

## 📊 Resources Created

### Resources as Indexes (Not Copies)

Each agent's `resources/index.md` contains:
- **Links to source documents** (not copies)
- **Line number references** for specific sections
- **File path references** for implementation targets
- **Success metrics** from session plan
- **Testing requirements**

**Example from coderef-context/resources/index.md:**
```markdown
### Primary Analysis Document
**Location:** C:\Users\willh\.mcp-servers\coderef-context\CONTEXT-LEVERAGE-ANALYSIS.md

**Your focus areas:**
- Lines 172-245: Priority 1 enhancements
- Lines 246-290: Priority 2 (populate reports)
```

**Benefit:** Agents read from source of truth, no duplication, always up-to-date

---

## ✅ Phase 1 Gate Check

Before Phase 2 can start, both agents must complete:

**coderef-context:**
- ✅ Context quality: 95%
- ✅ Tool calls: 1 (from 6)
- ✅ Reports populated: patterns.json, validation.json, complexity.json

**coderef-core:**
- ✅ Scanner performance: +15%
- ✅ Configuration presets: 7 presets working
- ✅ Structured errors: ScanError interface implemented
- ✅ Python patterns: 7 patterns (from 3)

---

## 🔄 Workflow Pattern

```
Orchestrator (this project)
  ↓ Created agent directories with communication.json, instructions.json, resources/
  ↓
Agent (in their own project)
  ↓ Reads instructions.json
  ↓ Reads resources/index.md to find source documents
  ↓ Uses context.json template to create workorder
  ↓ Runs /create-workorder → generates plan.json
  ↓ Executes plan
  ↓ Creates output in session directory outputs/
  ↓ Updates communication.json status
  ↓
Orchestrator
  ↓ Monitors communication.json files
  ↓ Aggregates progress from both agents
  ↓ Validates Phase 1 gate check criteria
  ↓ Creates Phase 2 agent directories when Phase 1 complete
```

---

## 📁 File Inventory

**Session-level files:** 7
- communication.json, instructions.json, README.md
- scanner-complete-context.md, phase1-progress.md
- phase2-integration-targets.md, INTEGRATION-SUMMARY.md

**Per-agent files:** 4 (× 2 agents = 8 total)
- communication.json (agent-specific)
- instructions.json (agent-specific)
- resources/index.md (links to sources)
- outputs/ (empty, agent creates here)

**Total:** 15 files created

---

## 🎁 What This Achieves

### Clear Separation
- Session-level: Orchestrator coordination
- Agent-level: Autonomous execution

### Self-Contained
- Each agent has everything they need in their directory
- No cross-references between agents
- Resources are indexes (not copies)

### Scalable
- Phase 2 agents (coderef-workflow, coderef-docs) will follow same pattern
- Phase 3 agents (coderef-testing, papertrail) will follow same pattern
- Pattern repeats for 9 total agents

### Auditable
- Each agent updates their communication.json
- Orchestrator aggregates from all communication.json files
- Clear ownership and progress tracking

---

**Status:** ✅ Ready for agent onboarding
**Next Step:** User onboards agents OR orchestrator generates handoff prompts
**Last Updated:** 2026-01-14
