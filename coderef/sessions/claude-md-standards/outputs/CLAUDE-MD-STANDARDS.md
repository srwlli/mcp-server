# CLAUDE.md Standards (v1.0.0)

**Purpose:** Authoritative guide for writing project-level CLAUDE.md files in the CodeRef ecosystem
**Applies to:** MCP servers, dashboards, orchestrators, and primary project repositories
**Created:** 2026-01-22
**Workorder:** WO-CLAUDE-MD-STANDARDS-001

---

## Executive Summary

CLAUDE.md is the AI context file that appears in **every single Claude Code session** for your project. It must be universally applicable, lean, and optimized for LLM consumption.

**Core Principles:**
1. **Keep it lean** - 530-600 lines target (LLMs can follow ~150-200 instructions consistently)
2. **Progressive disclosure** - Tell HOW to find information, not ALL the information
3. **No linting rules** - Use deterministic tools, not LLM descriptions of code style
4. **Delegate complexity** - Recommend subagents for complex multi-step tasks

**Based on:**
- Research of 20+ industry sources (Anthropic, community best practices)
- Audit of 8 CodeRef CLAUDE.md files (average score: 71.9/100)
- CLAUDEMD-TEMPLATE.json v1.0.0

---

## 1. Line Budget Standards

### Target Range
- **Minimum:** 475 lines (acceptable for focused tools)
- **Target:** 530-600 lines (ideal range)
- **Maximum:** 600 lines (hard limit)

### Why This Matters
- Frontier thinking LLMs can follow ~150-200 instructions with reasonable consistency
- Every line in CLAUDE.md consumes context window tokens in every session
- Bloated CLAUDE.md files reduce available space for actual code context

### Enforcement Rules

**Line Count Calculation:**
```bash
# Count total lines including blank lines
wc -l CLAUDE.md

# Exclude frontmatter (lines 1-8 if using YAML)
tail -n +9 CLAUDE.md | wc -l
```

**Violations and Severity:**
- **475-530 lines:** ✅ Acceptable (may need expansion for complex projects)
- **530-600 lines:** ✅ Ideal range
- **601-700 lines:** ⚠️ Warning (trim within 30 days)
- **701-900 lines:** ❌ Major (trim within 7 days)
- **901+ lines:** 🚨 Critical (trim immediately)

**Audit Findings:**
- 50% of CodeRef files exceeded 600-line target (4/8 files)
- Worst offender: coderef-workflow at 1,142 lines (191% over target)
- Total ecosystem bloat: +1,115 lines across all files

---

## 2. Required Sections

Based on CLAUDEMD-TEMPLATE.json v1.0.0 with CodeRef-specific enhancements.

### 2.1 Core Sections (Mandatory)

| Section | Purpose | Max Lines |
|---------|---------|-----------|
| **Quick Summary** | 3-5 sentence overview with core innovation | 30 |
| **Problem & Vision** | Why this exists, what it solves | 40 |
| **Architecture** | Core concepts, data flow, key integration points | 80 |
| **Workflows Catalog** | Table of all workflows with triggers | 30 |
| **Core Workflows** | Step-by-step for 3-5 most important workflows | 120 |
| **File Structure** | Directory tree with annotations | 40 |
| **Design Decisions** | ADR-style: chosen vs rejected with reasons | 60 |
| **Integration Guide** | How this connects to other systems | 50 |
| **Essential Commands** | Development, testing, deployment commands | 30 |

**Total Core:** ~480 lines

### 2.2 Enhanced Sections (Mandatory for CodeRef Projects)

| Section | Purpose | Max Lines |
|---------|---------|-----------|
| **Progressive Disclosure Guide** | Where to find detailed info (not the info itself) | 20 |
| **Tool Sequencing Patterns** | Common tool call sequences for this project | 30 |
| **Subagent Delegation Guide** | When to spawn Task tool subagents | 20 |

**Total Enhanced:** ~70 lines

### 2.3 Optional Sections

| Section | Purpose | Max Lines | When to Include |
|---------|---------|-----------|-----------------|
| **Use Cases** | End-to-end scenarios | 40 | Complex workflows with multiple actors |
| **Recent Changes** | Changelog (last 2 versions ONLY) | 40 | Active development (v1.x+) |
| **Next Steps / Roadmap** | Planned features | 20 | Communicating future direction |
| **Resources** | Links to external docs | 10 | When external docs exist |

**Total Optional:** ~110 lines (use selectively to stay under 600-line budget)

### 2.4 Audit Findings

**Section Presence:**
- 88% of files have all 15 sections (7/8 files)
- 100% use tables for tools/workflows (excellent formatting)
- 0% have Progressive Disclosure Guide (new requirement)
- 0% have Tool Sequencing Patterns (new requirement)
- 0% have Subagent Delegation Guide (new requirement)

---

## 3. Progressive Disclosure (NEW)

### What is Progressive Disclosure?

Instead of documenting ALL information in CLAUDE.md, tell the AI **where to find** detailed information.

### Anti-Pattern (Bloated)
```markdown
## Scanner Integration

### Overview
The universal `.coderef/` structure provides agents with static code intelligence...

### Directory Structure
- `index.json` - Master index of all code elements
- `graph.json` - Dependency graph
- `complexity.json` - Complexity metrics

### Usage
To scan a project, call mcp__coderef-context__coderef_scan with...
[185 lines of detailed usage instructions]
```

### Pattern (Progressive Disclosure)
```markdown
## Scanner Integration

CodeRef-context provides static code intelligence via `.coderef/` structure.

**For detailed usage:**
- Scanner tools: See `mcp__coderef-context__coderef_scan` tool description
- File structure: See `.coderef/README.md` in scanned projects
- Integration examples: Use Task tool to read `coderef-context/CLAUDE.md` section "Core Workflows"

**Quick reference:**
- Scan project: `coderef_scan(project_path)`
- Query relationships: `coderef_query(target, query_type)`
- Check complexity: `coderef_complexity(element)`
```

### Where to Put Detailed Info

| Information Type | Best Location | Reference in CLAUDE.md |
|------------------|---------------|------------------------|
| Tool usage details | MCP tool descriptions (built-in to Claude) | "See tool description for mcp__X" |
| API reference | Separate API.md file | "See API.md for full reference" |
| Architecture diagrams | Separate ARCHITECTURE.md file | "See ARCHITECTURE.md for diagrams" |
| Component catalog | Separate COMPONENTS.md file | "See COMPONENTS.md for component list" |
| Historical context | Separate CHANGELOG.md file | "See CHANGELOG.md for version history" |
| Implementation guides | Separate docs/ folder | "See docs/implementing-X.md" |

### Audit Findings

**Common Bloat Sources:**
1. **Scanner integration guides:** 300+ lines in coderef-workflow (should be 30 lines + pointer)
2. **Version history:** 170+ lines in coderef-workflow, 300+ in coderef-docs (should be 40 lines max, last 2 versions)
3. **Persona listings:** 180+ lines in coderef-personas (should be summary table + pointer to personas directory)
4. **Tool catalogs:** 185+ lines in ecosystem CLAUDE.md (should be pointer to .coderef/index.json)

---

## 4. Tool Sequencing Patterns (NEW)

### What is Tool Sequencing?

Document the **order of tool calls** for common workflows specific to your project.

### Why This Matters

LLMs benefit from explicit sequencing guidance:
- Prevents calling tools in wrong order
- Reduces trial-and-error iterations
- Makes workflows more deterministic

### Example: Workorder Creation Workflow

```markdown
## Tool Sequencing Patterns

### Pattern 1: Workorder Creation
**Scenario:** User promotes stub to active workorder

**Sequence:**
1. `Read` - Load stub.json from orchestrator
2. `mcp__coderef-workflow__gather_context` - Generate context.json
3. `Write` - Save context.json in TARGET project (not orchestrator)
4. `Write` - Save communication.json in TARGET project
5. `Edit` - Update orchestrator's workorders.json
6. `mcp__coderef-docs__log_workorder` - Log to global workorder history

**Common mistake:** Writing context.json to orchestrator folder instead of target project
```

### Example: Foundation Docs Generation

```markdown
### Pattern 2: Foundation Docs Generation
**Scenario:** Generate README, ARCHITECTURE, API docs for new project

**Sequence:**
1. `mcp__coderef-context__coderef_scan` - Scan project for code elements
2. `mcp__coderef-docs__generate_foundation_docs` - Generate all 5 docs
3. `mcp__papertrail__validate_document` - Validate each generated doc
4. `Bash(git add)` - Stage generated files
5. `Bash(git commit)` - Commit with attribution

**Common mistake:** Skipping validation step, resulting in schema violations
```

### Recommended Patterns by Project Type

| Project Type | Key Patterns to Document |
|--------------|-------------------------|
| **Orchestrator** | Stub creation, workorder handoff, status checks |
| **MCP Server** | Tool registration, schema validation, error handling |
| **Dashboard** | Component creation, API integration, state management |
| **CLI Tool** | Command parsing, config loading, output formatting |

---

## 5. Subagent Delegation Guide (NEW)

### What is Subagent Delegation?

Use the `Task` tool to spawn specialized subagents for complex, multi-step work that would bloat CLAUDE.md if fully documented.

### When to Recommend Subagents

**✅ Delegate to subagent when:**
- Task requires 5+ sequential steps
- Task involves exploring codebase (e.g., "where are errors handled?")
- Task requires iterative refinement (e.g., "fix all type errors")
- Task involves cross-file coordination

**❌ DO NOT delegate when:**
- Task is a single tool call
- User needs immediate response (subagent has latency overhead)
- Task requires user interaction (subagents can't ask follow-up questions)

### How to Document in CLAUDE.md

```markdown
## Subagent Delegation Guide

### Pattern: Codebase Exploration
**User asks:** "Where are errors from the client handled?"

**Don't:** Run Grep/Glob directly and manually trace through files

**Do:** Spawn Explore subagent
```
Use Task tool with subagent_type=Explore to find error handling locations.
Example prompt: "Find all client error handling code and explain the flow"
```

### Pattern: Multi-Step Refactoring
**User asks:** "Refactor the authentication system to use OAuth2"

**Don't:** Try to coordinate all changes in main session

**Do:** Spawn general-purpose subagent
```
Use Task tool with subagent_type=general-purpose for multi-step refactoring.
Example prompt: "Refactor authentication system from JWT to OAuth2, preserving existing API contracts"
```
```

### Audit Findings

**Current state:** 0/8 files have subagent delegation guidance
**Impact:** Main sessions bloat with complex coordination logic that subagents handle better
**Example:** coderef-workflow's Scanner Integration section (300+ lines) could be reduced to 50 lines + subagent delegation pattern

---

## 6. Formatting Standards

### 6.1 Tables

**✅ Use tables for:**
- Workflows catalog (name, purpose, trigger)
- Tool catalogs (tool, purpose, when to use)
- File structure annotations
- Design decisions (chosen vs rejected)
- Integration points (depends on, used by)

**Example:**
```markdown
| Workflow | Purpose | Trigger |
|----------|---------|---------|
| Stub Creation | Capture idea as STUB-XXX | User has new idea |
| Handoff Protocol | Delegate to project agent | Workorder created |
```

**Audit finding:** 100% of files use tables correctly (excellent!)

### 6.2 Code Blocks

**✅ Use code blocks for:**
- Command examples
- File structure trees
- Configuration snippets
- Data flow diagrams (ASCII)
- Example API calls

**❌ DO NOT use code blocks for:**
- Full implementation details (violates progressive disclosure)
- Code style rules (use linter config files instead)

### 6.3 Lists

**Bullet lists:** Unordered information (features, capabilities)
**Numbered lists:** Sequential steps (workflows, instructions)
**Definition lists:** Key-value pairs (terms and definitions)

### 6.4 Headers

**Hierarchy:**
- `## ` - Top-level sections (Quick Summary, Architecture, etc.)
- `### ` - Subsections (Core Concepts, Data Flow, etc.)
- `#### ` - Sub-subsections (use sparingly, indicates over-nesting)

**Avoid:**
- `##### ` or deeper (indicates content should be extracted to separate file)

**Audit finding:** 100% of files follow header hierarchy correctly

---

## 7. Content Quality Standards

### 7.1 Quick Summary Section

**Requirements:**
- 3-5 sentences maximum
- State project type (CLI, MCP server, dashboard, etc.)
- Highlight core innovation (what makes this unique)
- Include latest version and status

**Example (assistant/CLAUDE.md - scored 92/100):**
```markdown
## Quick Summary

**Assistant** is a focused orchestrator CLI that coordinates work across multiple projects without executing code directly in those projects.

**Core Innovation:** Centralized workorder tracking with delegation-first architecture. Each target project has its own embedded agent with full context - Assistant identifies work, delegates to project agents, and aggregates results.

**Latest Update (v2.0.0):**
- Integrated with 6 MCP servers
- Added STUB-XXX and WO-XXX ID tracking system
- Implemented communication.json handoff protocol
```

### 7.2 Architecture Section

**Requirements:**
- Core Concepts subsection (3-5 key concepts, 2-3 sentences each)
- Data Flow diagram (ASCII or pointer to external diagram)
- Key Integration Points table

**Anti-pattern:** Explaining every function and class (use ARCHITECTURE.md instead)

**Pattern:** Explain the 3-5 "big ideas" that make the system work

### 7.3 Design Decisions Section

**Format:** ADR-style (Architecture Decision Record)

**Template:**
```markdown
## Design Decisions

### 1. [Decision Title]
- ✅ Chosen approach: [What was chosen]
- ❌ Rejected alternative: [What was rejected]
- Reason: [Why, focusing on tradeoffs]
```

**Audit finding:** 88% of files have Design Decisions section (7/8)

---

## 8. Recent Changes Section Standards

### Line Budget
**Maximum:** 40 lines
**Coverage:** Last 2 versions ONLY
**Format:** Reverse chronological (newest first)

### What to Include

**✅ Include:**
- Version number and date
- Major features added
- Breaking changes
- Deprecations

**❌ Exclude:**
- Minor bug fixes
- Internal refactorings
- Implementation details

### Anti-Pattern (170 lines - coderef-workflow)
```markdown
### Recent Changes

#### v2.1.0 - Scanner Integration Enhancement (2026-01-15)
**Major Enhancement:** Complete integration of coderef-context scanner...

[150+ lines of detailed implementation notes]

#### v2.0.0 - CSV Automation (2025-12-20)
[80+ lines of CSV automation details]

#### v1.5.0 - UDS Integration (2025-11-10)
[100+ lines of UDS integration details]
```

### Pattern (40 lines max)
```markdown
### Recent Changes

#### v2.1.0 - Scanner Integration (2026-01-15)
- ✅ Integrated coderef-context scanner for type-aware planning
- ✅ Added complexity-based effort estimation
- ✅ Automated CSV tool/resource tracking
- 🗑️ Deprecated manual context gathering

#### v2.0.0 - UDS Integration (2025-12-20)
- ✅ Integrated Papertrail MCP for document validation
- ✅ Added workorder tracking with communication.json protocol
- Breaking: context.json now requires workorder_id field
```

### Where to Put Old History

**Solution:** Extract to `CHANGELOG.md` or `coderef/foundation-docs/CHANGELOG.md`

**In CLAUDE.md:**
```markdown
## Recent Changes

[Last 2 versions - 40 lines max]

**Full history:** See [CHANGELOG.md](CHANGELOG.md) for versions prior to v2.0.0
```

### Audit Findings

**Violations:**
- coderef-workflow: 170+ lines (should be 40)
- coderef-docs: 300+ lines covering v1.0 through v4.1 (should be 40 for v4.0 and v4.1 only)
- coderef-personas: 140+ lines (should be 40)

**Impact:** +390 lines of historical bloat across 3 files

---

## 9. Code Style and Linting Rules

### ❌ DO NOT Include in CLAUDE.md

**Never document:**
- Indentation rules (tabs vs spaces)
- Naming conventions (camelCase, snake_case)
- Import ordering
- Line length limits
- Comment formatting
- File naming conventions

**Why:** These are deterministic rules that belong in linter config files:
- `.eslintrc.json` for JavaScript/TypeScript
- `.prettierrc` for formatting
- `pyproject.toml` for Python
- `.editorconfig` for editor settings

### ✅ What to Include Instead

**In CLAUDE.md:**
```markdown
## Code Quality

**Linting:** Run `npm run lint` before committing. Config: `.eslintrc.json`
**Formatting:** Run `npm run format` to auto-fix. Config: `.prettierrc`
**Type checking:** Run `npm run typecheck`. Strict mode enabled.
```

**Pointer to deterministic tools, not LLM descriptions of rules.**

### Audit Findings

**Good news:** 100% of files avoid code style bloat (8/8 files)
**Best practice:** CodeRef ecosystem consistently delegates to linter configs

---

## 10. File Structure Section Standards

### Format: Annotated Directory Tree

**Template:**
```markdown
## File Structure

```
project/
├── CLAUDE.md                    # This file - AI context
├── README.md                    # User documentation
├── src/
│   ├── main.ts                  # Entry point
│   └── lib/
│       └── core.ts              # Core business logic
├── coderef/
│   ├── foundation-docs/         # Generated docs (README, ARCHITECTURE, API)
│   └── working/                 # Active workorders
└── tests/
    └── core.test.ts             # Unit tests
```
```

### Best Practices

**✅ Do:**
- Show 2-3 levels deep (top-level + important subdirectories)
- Annotate each entry with purpose
- Highlight key files (CLAUDE.md, README.md, main entry point)
- Use `coderef/` folder structure consistently

**❌ Don't:**
- Show every file (use `tree` command output - violates progressive disclosure)
- Include node_modules, .git, build artifacts
- Go more than 3 levels deep (extract to ARCHITECTURE.md)

### Audit Findings

**Compliance:** 100% of files have annotated file structure (8/8)
**Quality:** High - most files show appropriate depth and annotations

---

## 11. Integration Guide Standards

### Purpose

Document how this project connects to other systems in the ecosystem.

### Format: Dependency Table + Integration Patterns

**Template:**
```markdown
## Integration Guide

### Dependencies

| System | Relationship | Used For |
|--------|--------------|----------|
| coderef-context | Depends on | Code analysis, complexity scoring |
| coderef-workflow | Depends on | Planning, deliverables tracking |
| Target projects | Used by | Workorder delegation |

### Integration Pattern: Workorder Handoff

**Flow:**
1. Orchestrator creates context.json in TARGET project (not orchestrator)
2. Orchestrator generates handoff prompt
3. User pastes prompt into target project agent
4. Agent executes, updates communication.json
5. Orchestrator reads communication.json (read-only)
```

### What to Include

**✅ Include:**
- Dependency table (depends on, used by)
- 2-3 key integration patterns (how systems connect)
- Data flow for cross-system workflows

**❌ Exclude:**
- Full API reference (use API.md)
- Implementation details of other systems (use progressive disclosure)

### Audit Findings

**Compliance:** 100% of files have Integration Guide (8/8)
**Quality:** Varies - assistant and papertrail have excellent integration guides, others could improve

---

## 12. Validation Checklist

Use this checklist before committing changes to CLAUDE.md:

### Line Budget
- [ ] Total lines ≤ 600 (run `wc -l CLAUDE.md`)
- [ ] If 601-700 lines, created plan to trim within 30 days
- [ ] If 701+ lines, trimmed immediately before commit

### Required Sections (Core)
- [ ] Quick Summary (3-5 sentences, core innovation highlighted)
- [ ] Problem & Vision
- [ ] Architecture (Core Concepts + Data Flow + Integration Points)
- [ ] Workflows Catalog (table format)
- [ ] Core Workflows (3-5 workflows, step-by-step)
- [ ] File Structure (annotated tree)
- [ ] Design Decisions (ADR format)
- [ ] Integration Guide (dependency table + patterns)
- [ ] Essential Commands

### Required Sections (Enhanced - NEW)
- [ ] Progressive Disclosure Guide (where to find detailed info)
- [ ] Tool Sequencing Patterns (2-3 common sequences)
- [ ] Subagent Delegation Guide (when to spawn Task tool)

### Content Quality
- [ ] Recent Changes ≤ 40 lines (last 2 versions only)
- [ ] No code style rules (delegated to linter configs)
- [ ] Tables used for workflows, tools, integrations
- [ ] Code blocks used for commands, examples, file trees
- [ ] Headers follow hierarchy (##, ###, #### max)

### Progressive Disclosure
- [ ] Tool details delegated to tool descriptions
- [ ] API reference delegated to API.md
- [ ] Architecture diagrams delegated to ARCHITECTURE.md
- [ ] Historical context delegated to CHANGELOG.md

### Formatting
- [ ] No trailing whitespace
- [ ] Consistent list formatting (bullet vs numbered)
- [ ] Consistent code fence language tags (```markdown, ```bash, ```typescript)

---

## 13. Common Violations and Fixes

Based on audit of 8 CodeRef CLAUDE.md files.

### Violation 1: History Bloat (3 files)

**Symptom:** Recent Changes section exceeds 100 lines

**Examples:**
- coderef-workflow: 170 lines (should be 40)
- coderef-docs: 300 lines (should be 40)
- coderef-personas: 140 lines (should be 40)

**Fix:**
1. Extract versions older than last 2 to `CHANGELOG.md`
2. Keep only last 2 versions in CLAUDE.md
3. Add pointer: "Full history: See [CHANGELOG.md](CHANGELOG.md)"

**Effort:** 30 minutes per file

### Violation 2: Implementation Detail Bloat (2 files)

**Symptom:** Sections with 100+ lines of "how it works" details

**Examples:**
- coderef-workflow: 300+ lines of Scanner Integration details (should be 30 + pointer)
- ecosystem: 185 lines of ".coderef/ Usage Guide" (should be pointer to README)

**Fix:**
1. Extract detailed guide to separate file (e.g., `docs/scanner-integration.md`)
2. Replace with 20-30 line summary + pointer
3. Use progressive disclosure: "For detailed usage, see docs/X.md"

**Effort:** 1 hour per section

### Violation 3: Missing Enhanced Sections (8 files)

**Symptom:** 0% of files have Progressive Disclosure, Tool Sequencing, or Subagent Delegation guides

**Impact:** Main sessions bloat with repetitive instructions that should be standardized

**Fix:**
1. Add "Progressive Disclosure Guide" section (20 lines max)
2. Add "Tool Sequencing Patterns" section (30 lines max)
3. Add "Subagent Delegation Guide" section (20 lines max)

**Effort:** 45 minutes per file (use this standards doc as template)

### Violation 4: Persona Catalog Bloat (1 file)

**Symptom:** coderef-personas lists 11 personas with 15+ lines each (180 total)

**Example:**
```markdown
### Implemented Personas

**Core Personas (4):**

1. ✅ **lloyd-expert** (v1.2.0)
   - Role: Multi-Agent Coordinator
   - Expertise: Project coordination, workorder tracking...
   [15+ lines]

[Repeated for 10 more personas = 180 lines]
```

**Fix:**
1. Replace with summary table (20 lines):
   ```markdown
   | Persona | Role | Version | Status |
   |---------|------|---------|--------|
   | lloyd-expert | Multi-Agent Coordinator | v1.2.0 | ✅ Active |
   | ... | ... | ... | ... |
   ```
2. Add pointer: "See `personas/` directory for full persona definitions"

**Effort:** 30 minutes

### Violation 5: Critical Line Budget Overrun (1 file)

**Symptom:** coderef-workflow at 1,142 lines (191% over target)

**Root causes:**
- History bloat: 170 lines (should be 40) → save 130 lines
- Scanner integration: 300 lines (should be 30) → save 270 lines
- CSV automation: 80 lines (should be pointer) → save 60 lines
- Missing progressive disclosure → could save 100+ lines

**Fix plan:**
1. Extract history to CHANGELOG.md → -130 lines
2. Extract scanner guide to docs/scanner-integration.md → -270 lines
3. Extract CSV automation to docs/csv-automation.md → -60 lines
4. Add progressive disclosure pointers → +30 lines

**Result:** 1,142 → 712 lines (still 112 over, needs further pruning)

**Effort:** 3 hours (most complex fix)

---

## 14. Migration Guide

### For Existing CLAUDE.md Files

**Step 1: Assess Current State**
```bash
# Count lines
wc -l CLAUDE.md

# Check for violations
grep -n "###.*Personas" CLAUDE.md  # Persona bloat?
grep -n "## Recent Changes" -A 100 CLAUDE.md | wc -l  # History bloat?
```

**Step 2: Fix Line Budget Violations**

If ≥ 700 lines:
1. Extract history to CHANGELOG.md (save ~100 lines)
2. Extract implementation guides to docs/ (save ~200 lines)
3. Condense persona/tool catalogs to tables (save ~100 lines)

**Step 3: Add Enhanced Sections**
1. Add "Progressive Disclosure Guide" after Integration Guide
2. Add "Tool Sequencing Patterns" after Essential Commands
3. Add "Subagent Delegation Guide" after Tool Sequencing

**Step 4: Validate**
```bash
# Run validator (Phase 5 deliverable)
mcp__papertrail__validate_claude_md CLAUDE.md

# Check score (target: 80+)
# Expected output: Section presence, line budget, formatting, content quality scores
```

**Step 5: Commit**
```bash
git add CLAUDE.md
git commit -m "refactor: Bring CLAUDE.md into compliance with v1.0.0 standards

- Trim to 580 lines (was 850)
- Extract history to CHANGELOG.md
- Add progressive disclosure guide
- Add tool sequencing patterns
- Add subagent delegation guide

Score: 88/100 (was 65/100)

WO-CLAUDE-MD-STANDARDS-001"
```

---

## 15. For New Projects

**Step 1: Use Generator (Phase 6 deliverable)**
```bash
# Generate from template
mcp__coderef-docs__generate_claude_md \
  --project-path /path/to/project \
  --project-type "mcp-server" \
  --auto-fill true

# Output: CLAUDE.md (530 lines, all sections present, validated)
```

**Step 2: Customize Required Sections**

Fill in project-specific content:
1. Quick Summary - What makes this project unique?
2. Architecture - What are the 3-5 core concepts?
3. Workflows Catalog - What are the key workflows?
4. Design Decisions - What were the key tradeoffs?

**Step 3: Add Tool Sequencing Patterns**

Identify 2-3 common tool sequences:
1. Primary workflow (most frequent)
2. Error recovery workflow (most critical)
3. Integration workflow (most complex)

**Step 4: Validate Before First Commit**
```bash
mcp__papertrail__validate_claude_md CLAUDE.md

# Target score: 85+ for new projects
```

**Step 5: Commit with Workorder ID**
```bash
git add CLAUDE.md
git commit -m "docs: Add CLAUDE.md for AI context

Generated from CLAUDE-MD-STANDARDS v1.0.0
Score: 88/100

WO-[PROJECT]-SETUP-001"
```

---

## 16. Appendix: Scoring Methodology

Based on audit of 8 CodeRef files (Phase 2 deliverable).

### Score Calculation (0-100)

**Section Presence (30 points):**
- Core sections (15): 1.67 pts each × 9 sections
- Enhanced sections (9): 3 pts each × 3 sections (Progressive Disclosure, Tool Sequencing, Subagent Delegation)
- Optional sections (6): 1 pt each × 6 sections

**Line Budget Compliance (25 points):**
- 530-600 lines: 25 pts
- 475-530 or 600-650: 20 pts
- 400-475 or 650-700: 15 pts
- 350-400 or 700-850: 10 pts
- <350 or 850-1000: 5 pts
- 1000+: 0 pts

**Formatting Consistency (20 points):**
- Tables for workflows/tools (5 pts)
- Annotated file structure (5 pts)
- Header hierarchy followed (5 pts)
- Code blocks used correctly (5 pts)

**Content Quality (25 points):**
- Quick Summary concise (5 pts)
- Architecture explains core concepts (5 pts)
- Design Decisions in ADR format (5 pts)
- Recent Changes ≤ 40 lines (5 pts)
- No code style bloat (5 pts)

### Grade Scale

- **90-100:** Excellent (ready for production)
- **80-89:** Good (minor improvements needed)
- **70-79:** Fair (needs attention)
- **60-69:** Poor (significant work required)
- **<60:** Critical (major overhaul required)

### Current Ecosystem Scores

| File | Score | Grade | Priority |
|------|-------|-------|----------|
| assistant | 92 | Excellent | Maintain |
| papertrail | 88 | Good | Minor tweaks |
| coderef-dashboard | 80 | Good | Add enhanced sections |
| coderef-context | 78 | Fair | Add enhanced sections |
| ecosystem | 68 | Fair | Trim bloat |
| coderef-personas | 64 | Fair | Condense personas |
| coderef-docs | 62 | Fair | Extract history |
| coderef-workflow | 55 | Critical | Major overhaul |

**Average:** 71.9/100 (Good)
**Target:** 85+ across all files

---

## 17. Related Standards

This document defines project-level CLAUDE.md standards. See also:

- **CHILD-CLAUDE-MD-GUIDE.md** - Standards for sub-package/module CLAUDE.md files (Phase 3 deliverable)
- **SKILL-TEMPLATE.md** - Standards for skill.md files (Phase 3 deliverable)
- **skills-vs-claude-decision-tree.md** - When to use CLAUDE.md vs skill.md (Phase 3 deliverable)
- **claude-md-schema.json** - JSON Schema for validation (Phase 4 deliverable)
- **skill-frontmatter-schema.json** - JSON Schema for skill YAML frontmatter (Phase 4 deliverable)

---

## Version History

### v1.0.0 (2026-01-22)
- Initial release based on research + audit findings
- Defined 530-600 line budget
- Established 9 core + 3 enhanced + 6 optional sections
- Introduced Progressive Disclosure, Tool Sequencing, Subagent Delegation as required sections
- Provided migration guide for existing files
- Documented scoring methodology (0-100 scale)

**Workorder:** WO-CLAUDE-MD-STANDARDS-001
**Session:** claude-md-standards
**Author:** CodeRef Assistant (Orchestrator Persona)

---

**Next Steps:**
1. Review and approve this standards document
2. Create CHILD-CLAUDE-MD-GUIDE.md (Phase 3)
3. Create SKILL-TEMPLATE.md (Phase 3)
4. Build JSON schemas (Phase 4)
5. Build validator tools (Phase 5)
6. Build generator tools (Phase 6)
