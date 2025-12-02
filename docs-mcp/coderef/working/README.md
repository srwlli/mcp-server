# Working Features Directory

**Purpose:** Active feature development and implementation planning
**Status:** In Progress
**Last Updated:** 2025-10-20

---

## 📊 Workorder Activity Log

**Global Log:** `coderef/workorder-log.txt`

All workorder activity is tracked in a single chronological log file (latest first):

```
WO-UNIFIED-MCP-HTTP-SERVER-001 | docs-mcp | Add unified MCP server support... | 2025-10-20T23:00:00
WO-HANDOFF-AUTOMATION-001 | docs-mcp | Implement handoff automation... | 2025-10-20T22:30:00
WO-WORKORDER-LOG-001 | docs-mcp | Implement workorder logging system... | 2025-10-21T02:08:51
```

**View Activity:**
```bash
# View all workorders
/get-workorder-log

# Filter by project
/get-workorder-log --project docs-mcp

# Filter by pattern
/get-workorder-log --pattern WO-AUTH

# Get latest 10
/get-workorder-log --limit 10
```

**Auto-Logging:**
Many tools automatically log to workorder-log.txt when they complete:
- `/create-plan` - Logs when plan created
- `/update-deliverables` - Logs when deliverables updated
- `/archive-feature` - Logs when feature archived
- And more...

**Manual Logging:**
```bash
/log-workorder --id WO-CUSTOM-001 --project my-project --description "Custom work"
```

---

## 📁 Active Features

### 1. **unified-mcp-http-server** 🚀 PRIORITY
**Workorder:** WO-UNIFIED-MCP-HTTP-SERVER-001
**Status:** Ready for Implementation
**Goal:** Expose all 4 MCP servers (docs-mcp, coderef-mcp, hello-world-mcp, personas-mcp) through unified HTTP endpoint

**Files:**
- `plan.json` (25 KB) - Complete implementation plan with 5 phases, 20 tasks
- `HANDOFF.md` (33 KB) - Comprehensive agent handoff guide with dry-run

**Next Agent:**
1. Read `HANDOFF.md` (15-20 min reading time)
2. Follow Phase 1: Exploration & Verification
3. Implement Phases 2-5 sequentially
4. Estimated time: 3-4 hours total

**Current State:**
- ✅ ChatGPT integration working (docs-mcp only)
- ❌ Other 3 servers not accessible yet
- ✅ Implementation plan complete
- ✅ Handoff document complete

---

### 2. **handoff-automation** ⏳ PLANNED
**Workorder:** WO-HANDOFF-AUTOMATION-001
**Status:** Design Complete, Not Started
**Goal:** Automate agent handoff context generation to reduce handoff time from 20-30 min to 2-3 min

**Files:**
- `context.json` (5.0 KB) - Feature requirements
- `plan.json` (33 KB) - Original implementation plan (v1.0)
- `DELIVERABLES.md` (5.0 KB) - Task tracking template
- `ENHANCED-DESIGN.md` (14 KB) - **NEW** Two-tool system design (v2.0)

**Two-Tool Approach:**
1. `/handoff` - Quick context (80% use case, 2-3 min, 50-100 lines)
2. `/handoff-full` - Comprehensive guide (20% use case, 7-13 min, 500-1,500 lines)

**Enhancements:**
- ⭐ Code skeleton auto-generation
- ⭐ Smart phase detection
- ⭐ Git integration (uncommitted + commits)
- ⭐ Visual scanning with emojis
- ⭐ 90-95% auto-populated

**Next Steps:**
1. Review `ENHANCED-DESIGN.md`
2. Update `plan.json` for two-tool approach
3. Implement `/handoff` (quick) first
4. Then implement `/handoff-full`

---

## 🎯 Priority Order

| Priority | Feature | Status | Blocking? |
|----------|---------|--------|-----------|
| **1** | unified-mcp-http-server | Ready | Yes - ChatGPT only has 33/all tools |
| **2** | handoff-automation | Designed | No - manual handoffs work |

---

## 📊 Workflow States

Features in this directory follow this lifecycle:

```
Context Gathering → Planning → Ready for Implementation → In Progress → Complete → Archived
     ↓                 ↓              ↓                        ↓            ↓         ↓
context.json    plan.json    HANDOFF.md               DELIVERABLES.md  ✅ Done   archived/
```

**Current States:**
- `unified-mcp-http-server`: **Ready for Implementation** (has plan.json + HANDOFF.md)
- `handoff-automation`: **Planning Complete** (has plan.json + ENHANCED-DESIGN.md)

---

## 🔄 Agent Handoff Process

### Standard Workflow:
1. **Read** `{feature}/HANDOFF.md` (if exists) or `{feature}/plan.json`
2. **Update** `{feature}/DELIVERABLES.md` as you complete tasks
3. **Commit** progress regularly with workorder ID in message
4. **Log progress:** Tools auto-log to `coderef/workorder-log.txt` on completion
5. **When blocked:** Document in DELIVERABLES.md or create new HANDOFF.md
6. **When complete:** Run `/update-deliverables` and `/archive-feature`

### Quick Reference:
- **Plan exists?** → Read plan.json for task breakdown
- **Handoff exists?** → Read HANDOFF.md for implementation guidance
- **Stuck?** → Check plan.json section 7 (edge cases) and section 2 (risks)
- **View activity?** → Run `/get-workorder-log` to see recent work
- **Done?** → Update DELIVERABLES.md, commit, run `/update-deliverables`

---

## 🛠️ Available Tools

### Planning & Context:
- `/gather-context` - Collect feature requirements
- `/analyze-for-planning` - Analyze project structure
- `/create-plan` - Generate implementation plan
- `/validate-plan` - Score plan quality (0-100)

### Execution:
- `/execute-plan` - Generate TodoWrite task list from plan
- `/update-deliverables` - Update DELIVERABLES.md with git metrics

### Workorder Tracking:
- `/log-workorder` - Manually log workorder to global log
- `/get-workorder-log` - View and query workorder history
- **Auto-logging:** Many tools auto-log on completion (create-plan, update-deliverables, etc.)

### Handoff (Future):
- `/handoff` - Quick context (planned, not yet available)
- `/handoff-full` - Comprehensive guide (planned, not yet available)

---

## 📝 File Naming Conventions

| File | Purpose | Required? |
|------|---------|-----------|
| `context.json` | Feature requirements from `/gather-context` | Recommended |
| `analysis.json` | Project analysis from `/analyze-for-planning` | Recommended |
| `plan.json` | Implementation plan from `/create-plan` | **Required** |
| `DELIVERABLES.md` | Task tracking and metrics | Auto-generated |
| `HANDOFF.md` | Agent handoff guide (manual or automated) | Optional |
| `communication.json` | Multi-agent coordination | For parallel work |

---

## 🚀 Quick Start for New Agent

**Taking over `unified-mcp-http-server`?**

```bash
# 1. Navigate to feature
cd coderef/working/unified-mcp-http-server

# 2. Read handoff (15-20 min)
cat HANDOFF.md

# 3. Review plan
cat plan.json | jq '.UNIVERSAL_PLANNING_STRUCTURE."9_implementation_checklist"'

# 4. Start with Phase 1
# Follow HANDOFF.md dry-run starting at "Phase 1: Exploration"

# 5. Track progress
# Update DELIVERABLES.md as you complete tasks
```

**Starting new feature?**

```bash
# 1. Gather context
/gather-context

# 2. Analyze project
/analyze-for-planning

# 3. Create plan
/create-plan

# 4. Validate plan
/validate-plan

# 5. Execute
/execute-plan  # Generates TodoWrite task list
```

---

## 📂 Directory Structure

```
coderef/
├── workorder-log.txt                      ← Global workorder activity log
│
└── working/
    ├── README.md                          ← You are here
    │
    ├── unified-mcp-http-server/           ← PRIORITY 1
    │   ├── plan.json                      ← Implementation plan (5 phases)
    │   └── HANDOFF.md                     ← Start here! (1,143 lines)
    │
    ├── handoff-automation/                ← PRIORITY 2
    │   ├── context.json                   ← Requirements
    │   ├── analysis.json                  ← Project analysis
    │   ├── plan.json                      ← Implementation plan
    │   ├── DELIVERABLES.md                ← Task tracking
    │   └── ENHANCED-DESIGN.md             ← NEW Two-tool design
    │
    └── workorder-log/                     ← Workorder tracking system
        ├── context.json                   ← Feature requirements
        └── plan.json                      ← Implementation plan
```

---

## 🔗 Related Resources

- **Archived Features:** `coderef/archived/` - Completed features for reference
- **Standards:** `coderef/standards/` - UI/UX/behavior standards
- **Templates:** `templates/` - Documentation templates
- **Inventory:** `coderef/inventory/` - Project manifests

---

## ❓ Need Help?

- **Understanding workflow?** Read `/coderef/future/README.md`
- **Planning questions?** Check `CLAUDE.md` planning workflow section
- **Tool usage?** See `USER-GUIDE.md`
- **Standards?** Review `coderef/standards/*.md`

---

**Last Updated:** 2025-10-20
**Active Features:** 2 (1 ready, 1 designed)
**Maintainer:** willh + Claude Code AI
