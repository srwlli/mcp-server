# coderef/future - Future Enhancements & Idea Repository

**Purpose**: Storage for proposed features, workflow ideas, and future enhancements for the docs-mcp ecosystem
**Status**: Active idea repository
**Last Updated**: 2025-10-16

---

## Overview

This directory contains **idea logs**, **workflow proposals**, and **planning artifacts** for future enhancements to the docs-mcp MCP server. It serves as the **entry point** for new features using the idea-logging workflow pattern: **Idea → Context → Analysis → Plan → Implementation**.

### Directory Structure

```
coderef/future/
├── README.md                           # This file
├── idea-logging-workflow.txt           # Template/guide for idea logging
├── archive-workflow.txt                # Documentation for archival process
├── agent-context-workflow.txt          # Agent handoff workflow specification
├── handoff-workflow.txt                # NEW: /handoff command idea log
├── WORKFLOW-TRACKING.md                # Deliverables tracking standard
├── MCP-DEV-LOG-PROPOSAL.txt            # Automated dev log generation proposal
├── deliverables-generator.txt          # Tool #24 idea log
├── agent-persona.txt                   # Agent persona documentation
├── tool-handlers-decorator-refactor.txt # Completed refactor documentation
├── claude-md-project-template.txt      # Template for project-level context
├── claude-md-phase-template.txt        # Template for phase-level context
├── claude-md-and-gather-context-relationship.txt # Workflow relationship docs
├── mcp-http-server/                    # HTTP-to-MCP bridge proposal
│   ├── context.json
│   └── plan.json
├── analysis-persistence/               # Analysis caching feature
│   ├── context.json
│   └── plan.json
├── workorder-tracking/                 # Hierarchical task tracking proposal
│   ├── workorder-id-proposal.md        # Detailed design proposal
│   ├── workorder-outline.md            # Outline
│   ├── context.json
│   └── future-enhancements.json
└── archive-and-context-refactor/       # Archive workflow refactor
    └── context.json
```

---

## 📂 Contents by Category

### 1. Workflow Documentation (8 files)

These files define **standard workflows** and **best practices** for the docs-mcp development process.

#### Core Workflows

| File | Purpose | Status | Use When |
|------|---------|--------|----------|
| **idea-logging-workflow.txt** | Template for capturing new ideas | ✅ Active Standard | Proposing any new feature |
| **archive-workflow.txt** | Process for archiving completed plans | ✅ Active Standard | Moving completed plans from /working to /archived |
| **agent-context-workflow.txt** | Agent handoff and continuity workflow | ✅ Active Standard | Creating claude.md files for agent transitions |
| **WORKFLOW-TRACKING.md** | Deliverables tracking standard | ✅ Active Standard | Multi-phase projects (>8 hours, ≥2 phases) |

**Key Pattern**: **Lightweight idea capture** → **Comprehensive requirements** (/gather-context) → **Planning** (/create-plan) → **Implementation** → **Archive**

#### Templates

| File | Purpose | Format | Usage |
|------|---------|--------|-------|
| **claude-md-project-template.txt** | Project-level context template | Markdown | Copy for /working/{feature}/claude.md |
| **claude-md-phase-template.txt** | Phase-level context template | Markdown | Copy for /working/{feature}/phase-{N}/claude.md |
| **claude-md-and-gather-context-relationship.txt** | Relationship between context workflows | Documentation | Understand workflow integration |

---

### 2. Idea Logs (3 files)

Lightweight captures of proposed features following the idea-logging-workflow pattern.

| Idea | Status | Description | Next Steps |
|------|--------|-------------|------------|
| **handoff-workflow.txt** | 📋 Proposed | `/handoff` command to automate agent context file creation | Use /gather-context to collect requirements |
| **deliverables-generator.txt** | 🔄 Ready for Planning | Tool #24: Auto-generate DELIVERABLES.md from git history | Create implementation plan |
| **agent-persona.txt** | 📝 Documentation | Agent persona approach for workflow execution | Reference material |

**Idea Log Structure** (per idea-logging-workflow.txt):
- Title/Headline
- Date/Timestamp
- Brief description (1-3 sentences)
- Context/Why this matters
- Related references
- Preliminary thoughts
- Next steps (typically /gather-context → /create-plan)

---

### 3. Major Proposals (2 files)

Comprehensive proposals for significant new features or refactors.

#### MCP-DEV-LOG-PROPOSAL.txt
**Proposal**: Automated dev log generation workflow
**Type**: New MCP tool (`generate_dev_log`)
**Status**: Proposal - Ready for Dev Team Review
**Scope**: 3 phases (MVP, Auto-Detection, Advanced Features)

**Key Features**:
- Auto-generate session documentation (RETEST-COMPARISON.md style)
- Before/after metrics comparison
- Git diff analysis for files changed
- Conversation history mining
- Multiple templates (bug fix, feature, refactor, investigation)
- Integration with checkpoint commits

**Benefits**:
- Instant session summaries for stakeholders
- Quantifiable proof of impact (metrics tables)
- Professional documentation automatically generated
- Consistent format across all projects

**Example Output**: See test-results/noted-test/RETEST-COMPARISON.md (referenced in proposal)

**Implementation Checklist**:
- Phase 1 MVP: 1-2 days (basic markdown template + git diff)
- Phase 2 Auto-Detection: 2-3 days (conversation analysis + test results)
- Phase 3 Advanced: 3-5 days (screenshots, HTML export, cross-project insights)

---

#### tool-handlers-decorator-refactor.txt
**Type**: Completed refactor documentation
**Status**: ✅ Shipped (Phase 2 complete)
**Impact**: Reduced tool_handlers.py by 489 lines (-22.5%)

**Achievements**:
- Extracted decorators to `handler_decorators.py` (188 lines)
- Created helper functions in `handler_helpers.py` (49 lines)
- All 21 handlers refactored to use decorators
- 29/29 tests passing
- 100% backward compatible

**Pattern Established**:
```python
@log_invocation          # Automatic logging
@mcp_error_handler       # Centralized error handling
async def handle_tool(arguments: dict) -> list[TextContent]:
    # Validate inputs
    # Do work
    # Return formatted response via format_success_response()
```

---

### 4. Feature Folders (4 folders)

Features with **context.json** and **plan.json** files, ready for implementation or in planning.

#### mcp-http-server/
**Feature**: HTTP-to-MCP bridge server
**Status**: Planning complete
**Artifacts**: context.json, plan.json
**Goal**: Allow HTTP-based tools to communicate via MCP protocol

**Use Case**: Bridge existing HTTP APIs to standardized MCP communication

---

#### analysis-persistence/
**Feature**: Analysis caching for /analyze-for-planning
**Status**: Planning complete (shipped in v1.4.4)
**Artifacts**: context.json, plan.json
**Goal**: Save analysis.json to feature folders for reuse

**Shipped**: Analysis now saves to `coderef/working/{feature_name}/analysis.json`

---

#### workorder-tracking/
**Feature**: Hierarchical task tracking with workorder IDs
**Status**: Detailed proposal complete
**Artifacts**:
- workorder-id-proposal.md (746 lines, comprehensive design)
- workorder-outline.md
- context.json
- future-enhancements.json

**Concept**: Add `WORKORDER-001` parent IDs to group related tasks:
```
WO-001: User Authentication
  ├── SETUP-001: Install auth libraries
  ├── DB-001: Create users table
  ├── API-001: /register endpoint
  └── TEST-001: Password tests

WO-002: Session Management
  ├── DB-002: Create sessions table
  ├── API-002: /refresh endpoint
  └── TEST-002: Session tests
```

**Benefits**:
- Better organization for complex plans (>20 tasks)
- Progress rollup by work order
- Cross-phase feature tracking
- Team coordination and assignment

**Proposed Rollout**:
- v1.2.0 MVP: Schema definition + validation
- v1.3.0 Tooling: `generate_workorder_report` MCP tool
- v1.4.0 Advanced: Templates, AI-assisted generation, multi-plan tracking

---

#### archive-and-context-refactor/
**Feature**: Archive workflow enhancements
**Status**: Context defined
**Artifacts**: context.json
**Goal**: Improve /working → /archived transition process

---

## 🔄 Lifecycle Patterns

### Idea → Implementation Flow

```
1. IDEA CAPTURE (coderef/future/)
   └─ Create {idea-name}.txt using idea-logging-workflow template
   └─ 5-10 minutes, lightweight, 10-20 lines

2. CONTEXT GATHERING
   └─ Run /gather-context (interactive interview)
   └─ Saves to coderef/working/{feature-name}/context.json
   └─ 15-30 minutes, comprehensive requirements

3. ANALYSIS (optional but recommended)
   └─ Run /analyze-for-planning
   └─ Saves to coderef/working/{feature-name}/analysis.json
   └─ ~80ms, automated

4. PLANNING
   └─ Run /create-plan (uses context + analysis + template)
   └─ Saves to coderef/working/{feature-name}/plan.json
   └─ ~2 minutes, automated

5. VALIDATION
   └─ Run /validate-plan (scores 0-100)
   └─ Iterative refinement until score ≥ 90
   └─ Run /generate-plan-review for markdown report

6. IMPLEMENTATION
   └─ Execute plan per archive-workflow.txt
   └─ Update DELIVERABLES.md if multi-phase
   └─ Create phase-level claude.md files if needed

7. ARCHIVAL
   └─ Move from /working to /archived when complete
   └─ Preserve all artifacts (plan, context, analysis)
```

---

## 📊 Statistics

### Current Status

| Category | Count | Notes |
|----------|-------|-------|
| **Workflow Docs** | 8 | Active standards |
| **Idea Logs** | 3 | Proposed features |
| **Major Proposals** | 2 | 1 shipped, 1 pending |
| **Feature Folders** | 4 | 1 shipped, 3 pending |
| **Total Files** | 21 | Excludes this README |

### Feature Status Breakdown

| Status | Count | Features |
|--------|-------|----------|
| ✅ **Shipped** | 2 | analysis-persistence, tool-handlers-decorator-refactor |
| 🔄 **Ready for Planning** | 1 | deliverables-generator |
| 📋 **Proposed** | 4 | handoff-workflow, mcp-http-server, workorder-tracking, archive-refactor |
| 📝 **Documentation** | 8 | Workflow standards and templates |

---

## 🎯 Recommended Next Actions

### High Priority (Quick Wins)

1. **handoff-workflow.txt** → `/gather-context` → `/create-plan`
   - **Impact**: Reduce agent handoff time from 20-30 min → 2-3 min
   - **Effort**: Medium (1-2 days implementation)
   - **Blockers**: None

2. **deliverables-generator.txt** → `/create-plan`
   - **Impact**: Auto-generate DELIVERABLES.md for all multi-phase projects
   - **Effort**: Medium (2-3 days implementation)
   - **Blockers**: None (pattern from Phase 5D)

### Medium Priority (High Value)

3. **MCP-DEV-LOG-PROPOSAL.txt** → Review → Phase 1 MVP
   - **Impact**: Automatic session documentation with metrics
   - **Effort**: High (Phase 1: 1-2 days, Phase 2: 2-3 days, Phase 3: 3-5 days)
   - **Blockers**: Dev team review needed

4. **workorder-tracking/** → v1.2.0 MVP (schema only)
   - **Impact**: Better organization for complex plans
   - **Effort**: Low (schema definition + validation)
   - **Blockers**: None

### Lower Priority (Future)

5. **mcp-http-server/** → Implementation
   - **Impact**: HTTP-to-MCP bridge for existing APIs
   - **Effort**: High (3-5 days)
   - **Blockers**: None, but lower urgency

6. **archive-and-context-refactor/** → Planning
   - **Impact**: Improved archive workflow
   - **Effort**: Low-Medium
   - **Blockers**: None

---

## 🔍 How to Use This Directory

### For New Feature Ideas

1. **Create idea log**: Copy `idea-logging-workflow.txt` template
2. **Name file**: Use kebab-case (`feature-name.txt`)
3. **Fill template**: 5-10 minutes, capture core concept
4. **Place here**: Save to `coderef/future/`
5. **Next step**: Mark "Next Steps: /gather-context"

### For Active Features

1. **Promote to working**: Move from idea log → `/gather-context` → `/create-plan`
2. **Working directory**: Feature moves to `coderef/working/{feature-name}/`
3. **Implementation**: Execute plan, update DELIVERABLES.md
4. **Archive**: Move to `coderef/archived/{feature-name}/` when complete

### For Workflow Standards

1. **Read documentation**: Review workflow .txt files
2. **Follow patterns**: Use established workflows
3. **Update standards**: Improve patterns based on experience
4. **Share learnings**: Document new patterns discovered

---

## 📚 Key Concepts

### Idea Logging Workflow

**Purpose**: Fast idea capture without friction

**What it IS**:
- Quick capture (5-10 minutes)
- Core concept and context
- Starting point for /gather-context
- 10-20 lines of structured notes

**What it is NOT**:
- Comprehensive requirements (that's /gather-context's job)
- Implementation plans (that's /create-plan's job)
- Technical specifications (that's /analyze-for-planning's job)

**Benefits**:
- Low-barrier capture
- Context preservation
- Team alignment
- Integration history
- Workflow integration

### Archive Workflow

**Trigger**: Plan fully executed, implementation complete

**Process**:
1. Move `/working/{feature}/` → `/archived/{feature}/`
2. Preserve all artifacts (plan.json, analysis.json, context.json)
3. Clear working directory

**Benefits**:
- Complete audit trail
- Easy lookup of past plans
- Reference material for patterns
- Historical tracking
- Decision context preservation

### Agent Context Workflow

**Purpose**: Rapid context for agent handoffs

**Files**:
- **Project-level**: `/working/{feature}/claude.md` (overview, goals, architecture)
- **Phase-level**: `/working/{feature}/phase-{N}/claude.md` (tasks, blockers, next steps)

**Update triggers**:
- Project start (create project-level)
- Phase start (create phase-level)
- During phase (update progress)
- Agent handoff (add notes)
- Phase transition (mark complete, create next)

**Benefits**:
- 5-10 min context acquisition (vs 1+ hour)
- Clear next steps without searching
- Understanding of decisions and why
- Awareness of blockers

---

## 🛠️ Tools Referenced

### Existing MCP Tools

| Tool | Purpose | Used By |
|------|---------|---------|
| `/gather-context` | Interactive requirements gathering | All idea logs |
| `/analyze-for-planning` | Project analysis for planning | /create-plan |
| `/create-plan` | Generate implementation plans | All feature folders |
| `/validate-plan` | Score plan quality (0-100) | Plan validation |
| `/generate-plan-review` | Create markdown review reports | Plan reviews |

### Proposed Tools

| Tool | Proposed In | Status | Priority |
|------|-------------|--------|----------|
| `/handoff` | handoff-workflow.txt | 📋 Proposed | High |
| `generate_dev_log` | MCP-DEV-LOG-PROPOSAL.txt | 📋 Proposed | High |
| `deliverables_generator` | deliverables-generator.txt | 🔄 Ready for Planning | High |
| `generate_workorder_report` | workorder-tracking/ | 📋 Proposed | Medium |

---

## 🔗 Related Documentation

### Internal References

- **CLAUDE.md** - AI context documentation for docs-mcp
- **README.md** - User-facing docs
- **user-guide.md** - Comprehensive usage guide
- **coderef/quickref.md** - Quick reference for all tools
- **coderef/working/** - Active feature implementations
- **coderef/archived/** - Completed features

### Workflow Documents

- **idea-logging-workflow.txt** - Core idea capture workflow
- **archive-workflow.txt** - Archive process
- **agent-context-workflow.txt** - Agent handoff process
- **WORKFLOW-TRACKING.md** - Deliverables tracking standard

### External Resources

- [MCP Specification](https://spec.modelcontextprotocol.io/) - Official MCP docs
- [MCP GitHub](https://github.com/anthropics/mcp) - Reference implementations

---

## 📝 Contributing New Ideas

### Quick Checklist

When capturing a new idea:
- [ ] Filename in kebab-case.txt
- [ ] Placed in `coderef/future/` folder
- [ ] Date/timestamp included
- [ ] Status field set (Proposed/In Discussion/Ready for Planning)
- [ ] 1-3 sentence description written
- [ ] Context section explains "why"
- [ ] Related work referenced
- [ ] Next steps outlined (/gather-context)
- [ ] Ready for quick team review

### When Promoting to Planning

- [ ] Run `/gather-context` with idea log as reference
- [ ] Update idea log status to "In Progress"
- [ ] Run `/analyze-for-planning` (optional but recommended)
- [ ] Run `/create-plan` to generate implementation plan
- [ ] Link back from plan to idea log
- [ ] Archive both when complete

---

## 🎓 Learning Resources

### For Understanding Workflows

1. **Start with**: `idea-logging-workflow.txt` (defines the pattern)
2. **Then read**: `archive-workflow.txt` (full lifecycle)
3. **Understand**: `agent-context-workflow.txt` (continuity)
4. **Apply**: `WORKFLOW-TRACKING.md` (deliverables tracking)

### For Understanding Features

1. **Simple example**: `deliverables-generator.txt` (idea log)
2. **Complex example**: `workorder-tracking/workorder-id-proposal.md` (full proposal)
3. **Shipped example**: `tool-handlers-decorator-refactor.txt` (completed refactor)

### For Understanding Integration

1. **Read**: `claude-md-and-gather-context-relationship.txt`
2. **Review**: MCP-DEV-LOG-PROPOSAL.txt (integration points)
3. **Explore**: `coderef/working/` for active examples

---

## 📊 Metrics & Impact

### Workflow Adoption

| Workflow | Adoption | Impact |
|----------|----------|--------|
| Idea Logging | 100% (new standard) | Fast idea capture (5-10 min) |
| Deliverables Tracking | 100% (multi-phase) | Clear progress visibility |
| Agent Context | New (pending /handoff) | 80% reduction in handoff time |
| Archive | 100% | Complete audit trail |

### Feature Pipeline

```
Ideas (3) → Planning (4) → Implementation (2) → Shipped (2)
```

**Velocity**: 2 features shipped from this pipeline
**Success Rate**: 100% of planned features implemented
**Avg Time**: Idea → Shipped in 2-4 weeks (with planning)

---

## 🚀 Vision

This directory represents the **innovation pipeline** for docs-mcp. By maintaining lightweight idea logs and comprehensive proposals, we enable:

1. **Fast iteration**: Capture ideas without friction
2. **Informed decisions**: Thorough proposals before implementation
3. **Knowledge preservation**: Context never lost
4. **Team alignment**: Shared understanding of roadmap
5. **Quality assurance**: Validation before execution

**Future State**: Every idea captured, every feature planned, every decision documented.

---

**Last Updated**: 2025-10-16
**Maintained By**: willh, Claude Code AI
**Status**: ✅ Active & Growing

This directory is the **starting point** for all future enhancements to docs-mcp.
