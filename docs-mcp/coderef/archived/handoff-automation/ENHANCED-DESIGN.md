# Enhanced Two-Tool Handoff System Design

**Version:** 2.0
**Created:** 2025-10-20
**Status:** Design Phase

---

## 🎯 Design Philosophy

**Problem:** One-size-fits-all handoff doesn't work
- Simple features need quick context (2-3 min)
- Complex features need comprehensive guidance (detailed implementation)

**Solution:** Two tools with smart defaults
1. `/handoff` - Quick lightweight context (80% use case)
2. `/handoff-full` - Comprehensive implementation guide (20% use case)

---

## 🔧 Tool 1: `/handoff` (Quick Context)

### Purpose
Generate lightweight agent context files for standard feature handoffs.

### Command
```bash
/handoff --feature <feature-name> [--mode minimal|full]
```

### Output File
`coderef/working/{feature-name}/claude.md` (~50-100 lines)

### Auto-Populated Sections
```markdown
# Agent Handoff Context: {feature-name}

**Generated:** {timestamp}
**Workorder:** {from plan.json}
**Mode:** {minimal|full}
**Agent:** {current-agent} → {next-agent}

## 📋 Project Overview
{plan.json: section 1 executive_summary.purpose}
{plan.json: section 1 executive_summary.value_proposition[0]}

## ✅ Current Progress
**Phase:** {detect from task status}
**Completed:** {count ☑ in plan.json section 9}
**Remaining:** {count ☐ in plan.json section 9}

Recent commits:
{git log --grep={feature-name} --oneline -5}

## 🚧 Work In Progress
Current task: {first ⏳ or ☐ task in section 9}

Files modified (uncommitted):
{git status --short}

## ⏭️ Next Steps
1. {next ☐ task from section 9}
2. {next ☐ task from section 9}
3. {next ☐ task from section 9}

## ⚠️ Blockers / Notes
{extract from plan.json gaps_and_risks OR manual entry}

## 📁 Key Files
Modified: {plan.json: section 3 affected_files MODIFIED}
Reference: {plan.json: section 0 reference_components}

## 🔗 Resources
- Plan: coderef/working/{feature-name}/plan.json
- Context: coderef/working/{feature-name}/context.json
- Analysis: coderef/working/{feature-name}/analysis.json

---
**For detailed implementation guidance, run:** `/handoff-full`
```

### Enhancements Beyond Original Plan
1. **Agent tracking** - Shows current → next agent transition
2. **Phase detection** - Auto-detects current phase from task status
3. **Git integration** - Shows uncommitted changes + recent commits
4. **Task highlighting** - Uses emoji (✅ ☐ ⏳) for visual scanning
5. **Smart mode** - Minimal mode omits git/file details

### Time to Generate
- **Automated:** 2-3 minutes
- **Manual input:** None (100% auto-populated)

---

## 🔧 Tool 2: `/handoff-full` (Comprehensive Handoff)

### Purpose
Generate comprehensive implementation guide with code examples, testing procedures, and troubleshooting for complex features.

### Command
```bash
/handoff-full --feature <feature-name>
```

### Output File
`coderef/working/{feature-name}/HANDOFF.md` (~500-1,500 lines)

### Auto-Generated Sections
```markdown
# 🔄 Agent Handoff - {Feature Name}

**Workorder:** {plan.json: workorder_id}
**Status:** {plan.json: status}
**Estimated Time:** {plan.json: estimated_effort}
**Priority:** {infer from context}

---

## 📋 Context Summary

### Current State
{Auto-generated from plan.json + git status}

### Goal
{plan.json: section 1 executive_summary.purpose}

---

## 📁 Key Files

### 1. Implementation Plan
**Location:** {plan path}
**Contents:** {summary of 10 sections}
**Status:** {plan.json: status}

### 2. File to Modify
{plan.json: section 3 affected_files}
**Changes Needed:** {summary}

### 3. Reference Files
{plan.json: section 0 reference_components}

---

## 🎯 Implementation Dry-Run

{FOR EACH PHASE in plan.json section 6}

### Phase {N}: {phase.title} ({phase.effort_level} effort)

#### Tasks
{FOR EACH task in phase.tasks}
- {task.id}: {task.description}

#### {task.id}: {task.description}
**Location:** {inferred or from plan}

```{language}
{AUTO-GENERATED CODE SKELETON based on task description}
```

**Expected Outcome:** {task completion criteria}

---

## ⚠️ Potential Issues & Solutions

{Auto-extract from plan.json section 2 risk_assessment}
{Auto-extract from plan.json section 7 edge_case_scenarios}

### Issue 1: {risk.risk}
**Problem:** {risk description}
**Symptoms:** {auto-generate from risk.impact}
**Solution:** {risk.mitigation}

---

## 📊 Success Metrics

### Before (Current State)
{Extract from plan.json section 8 success_criteria}

### After (Target State)
{Extract from plan.json section 8 success_criteria}

---

## 🔗 Resources

### Files
{Auto-list from plan}

### Commands
```bash
{Auto-generate common commands for this project}
```

---

## 🎯 Next Steps for Implementing Agent

1. **Read this entire handoff document** (estimated: {calculate based on length})
2. **Start with Phase 1** {phase.title}
3. **Follow dry-run sequence** through all {count} phases
4. **Run all tests** before deploying
5. **Monitor deployment** and verify success

**Estimated Total Time:** {plan.json: estimated_effort}

---

**Created:** {timestamp}
**Workorder:** {plan.json: workorder_id}
**By:** {agent-name}

---

🚀 **Ready for next agent to begin implementation!**
```

### Enhancements Beyond Original Plan
1. **Code skeleton generation** - Auto-generate basic code structure from task descriptions
2. **Estimated reading time** - Calculate based on document length
3. **Common commands** - Auto-detect project type and suggest relevant commands
4. **Phase summaries** - Extract and format phase objectives
5. **Risk extraction** - Pull from multiple plan sections
6. **Success metrics** - Before/after comparison tables
7. **Smart formatting** - Use emojis and tables for scannability
8. **Deployment checklists** - Auto-generate from testing strategy

### Time to Generate
- **Automated:** 5-8 minutes (includes code skeleton generation)
- **Manual enhancement:** 2-5 minutes (add specific insights)
- **Total:** 7-13 minutes vs 30+ minutes manual

---

## 🔀 Smart Routing Logic

### When to Use Each Tool

**Use `/handoff` (Quick) when:**
- ✅ Feature has complete plan.json
- ✅ Implementation is straightforward
- ✅ Tasks are well-defined in plan
- ✅ No complex edge cases
- ✅ Standard workflow (setup → implement → test → deploy)
- **Examples:** Documentation updates, simple CRUD features, configuration changes

**Use `/handoff-full` (Comprehensive) when:**
- ✅ Complex multi-server integration (like unified-mcp-http-server)
- ✅ High risk or novel architecture
- ✅ Multiple potential issues identified
- ✅ Requires detailed troubleshooting guidance
- ✅ Critical production system
- ✅ First-time implementation of new pattern
- **Examples:** Multi-server systems, new infrastructure, API rewrites

### Auto-Detection (Future Enhancement)
```python
def recommend_handoff_type(plan_json: dict) -> str:
    """Recommend quick vs full handoff based on plan analysis."""

    risk_score = plan_json.get("2_risk_assessment", {}).get("complexity_score", 0)
    edge_cases = len(plan_json.get("7_testing_strategy", {}).get("edge_case_scenarios", []))
    phases = len(plan_json.get("6_implementation_phases", []))

    # Scoring logic
    if risk_score >= 7 or edge_cases >= 5 or phases >= 5:
        return "full"  # Recommend comprehensive handoff
    else:
        return "quick"  # Recommend quick handoff
```

---

## 📋 Template Structure

### Quick Context Template (claude-quick.txt)
```
{50-100 lines}
- Project Overview (5 lines)
- Current Progress (10 lines)
- Work In Progress (10 lines)
- Next Steps (10 lines)
- Blockers (5 lines)
- Key Files (10 lines)
- Resources (5 lines)
```

### Comprehensive Template (handoff-full.txt)
```
{500-1,500 lines depending on plan complexity}
- Context Summary (50 lines)
- Key Files (100 lines)
- Implementation Dry-Run (500-1,000 lines)
  - Phase 1 (100-200 lines per phase)
  - Phase 2...
- Potential Issues (100-200 lines)
- Success Metrics (50 lines)
- Resources (50 lines)
```

---

## 🎨 Key Enhancements Over Original Plan

### 1. **Code Skeleton Auto-Generation** ⭐ NEW
**What:** Generate basic code structure from task descriptions
**How:** Parse task descriptions for patterns like "Create function X", "Add endpoint Y"
**Example:**
```python
# Task: "Create _load_mcp_servers() function"
# Auto-generates:

def _load_mcp_servers() -> Dict[str, Any]:
    """
    Dynamically import all MCP servers from sibling directories.

    TODO: Implement server loading logic
    See: plan.json section 5 task IMPL-002 for details
    """
    pass
```

### 2. **Smart Phase Detection** ⭐ NEW
**What:** Auto-detect current phase from task completion status
**How:** Count ☑ vs ☐ in section 9, map to phases in section 6
**Example:**
```
Phase 1: Setup (3/3 complete) ✅
Phase 2: Implementation (2/5 in progress) 🚧 ← YOU ARE HERE
Phase 3: Testing (0/4 pending) ⏳
```

### 3. **Git Integration** ⭐ ENHANCED
**What:** Show uncommitted changes + recent commits
**How:**
- `git status --short` for WIP files
- `git log --grep={feature} --oneline -5` for progress
**Example:**
```markdown
## Work In Progress
Files modified (uncommitted):
 M http_server.py
 A coderef/working/unified-mcp-http-server/HANDOFF.md

Recent commits:
c8db783 Add comprehensive handoff document
b5614fa Add implementation plan
```

### 4. **Issue Extraction** ⭐ ENHANCED
**What:** Pull potential issues from multiple plan sections
**How:** Extract from:
- Section 2: risk_assessment
- Section 7: edge_case_scenarios
- Section 0: gaps_and_risks
**Example:** Auto-generates 7 issue blocks with symptoms + solutions

### 5. **Emoji Visual Scanning** ⭐ NEW
**What:** Use emojis for quick visual parsing
**How:**
- ✅ Completed tasks
- 🚧 In progress
- ⏳ Pending
- ⚠️ Issues/risks
- 📁 Files
- 🔗 Links
**Benefit:** Agents can scan document 3x faster

### 6. **Resource Auto-Linking** ⭐ NEW
**What:** Auto-detect and link to related resources
**How:** Scan for:
- Other plans in coderef/working/
- Related documentation
- Similar features in archived/
**Example:**
```markdown
## Related Work
- coderef/archived/multi-agent-coordination/ (similar pattern)
- CHATGPT-INTEGRATION-TROUBLESHOOTING.md (integration reference)
```

### 7. **Estimated Reading Time** ⭐ NEW
**What:** Calculate time to read handoff based on length
**How:** `reading_time = line_count / 40` (avg 40 lines/min)
**Example:**
```markdown
**Estimated Reading Time:** 15-20 minutes
```

---

## 🏗️ Implementation Architecture

### File Structure
```
generators/
  handoff_generator.py          # Base handoff generation
  handoff_full_generator.py     # Enhanced full handoff (NEW)

templates/handoff/
  claude-quick.txt              # Quick context template
  handoff-full.txt              # Comprehensive template (NEW)

tool_handlers.py
  handle_generate_handoff()     # Quick handoff handler
  handle_generate_handoff_full() # Full handoff handler (NEW)

server.py
  Tool: generate_handoff         # Quick tool
  Tool: generate_handoff_full    # Full tool (NEW)

.claude/commands/
  handoff.md                     # Quick slash command
  handoff-full.md                # Full slash command (NEW)
```

### Shared Components
Both tools share:
- `_parse_plan_json()` - Extract plan data
- `_parse_git_history()` - Get commits
- `_detect_current_phase()` - Phase detection
- `_extract_risks()` - Risk extraction

### Unique Components

**Quick tool:**
- `_render_quick_template()` - Simple rendering
- 50-100 line output
- Minimal code examples

**Full tool:**
- `_generate_code_skeletons()` - Code generation ⭐ NEW
- `_extract_all_issues()` - Comprehensive issue list ⭐ NEW
- `_calculate_reading_time()` - Time estimation ⭐ NEW
- 500-1,500 line output
- Full implementation dry-run

---

## 📊 Comparison Matrix

| Feature | Original Plan | `/handoff` (Quick) | `/handoff-full` (Comprehensive) |
|---------|--------------|-------------------|--------------------------------|
| **Output File** | claude.md | claude.md | HANDOFF.md |
| **Lines** | 50-100 | 50-100 | 500-1,500 |
| **Time to Generate** | 3 min | 2-3 min | 7-13 min |
| **Auto-Population** | 80% | 90% ⭐ | 95% ⭐ |
| **Code Examples** | ❌ No | ❌ No | ✅ Yes (skeletons) ⭐ |
| **Issue Troubleshooting** | ⚠️ Basic | ⚠️ Basic | ✅ Comprehensive ⭐ |
| **Phase Detection** | ❌ No | ✅ Yes ⭐ | ✅ Yes ⭐ |
| **Git Integration** | ⚠️ Basic | ✅ Enhanced ⭐ | ✅ Enhanced ⭐ |
| **Visual Scanning** | ❌ No | ✅ Emojis ⭐ | ✅ Emojis + Tables ⭐ |
| **Reading Time Est** | ❌ No | ❌ No | ✅ Yes ⭐ |
| **Use Case** | All | 80% Standard | 20% Complex |

---

## 🎯 Migration Path

### Phase 1: Implement Quick Tool (Priority 1)
```
✅ Implement generate_handoff (quick version)
✅ Use for standard features
✅ Validate auto-population works
```

### Phase 2: Implement Full Tool (Priority 2)
```
✅ Implement generate_handoff_full
✅ Add code skeleton generation
✅ Add comprehensive issue extraction
✅ Use for complex features like unified-mcp-http-server
```

### Phase 3: Add Intelligence (Priority 3)
```
✅ Auto-recommend quick vs full based on plan analysis
✅ Smart code generation from task patterns
✅ Cross-feature resource linking
```

---

## 🚀 Next Steps

1. **Update context.json** with two-tool approach
2. **Update plan.json** to include both tools
3. **Create templates** for quick and full modes
4. **Implement core generators**
5. **Add slash commands** /handoff and /handoff-full
6. **Test with real features**
7. **Iterate based on usage**

---

**Created:** 2025-10-20
**Status:** Design Complete - Ready for Implementation
**Workorder:** WO-HANDOFF-AUTOMATION-001 (updated for v2.0)

⭐ **Enhancements marked with stars are NEW beyond original plan**
