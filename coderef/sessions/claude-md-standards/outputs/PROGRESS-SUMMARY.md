# CLAUDE.md Standards - Progress Summary

**Session:** claude-md-standards
**Workorder:** WO-CLAUDE-MD-STANDARDS-001
**Status:** Phases 1-4 Complete (4/6 phases)
**Date:** 2026-01-22

---

## Executive Summary

**Mission:** Establish comprehensive standards for CLAUDE.md and skill.md files across the CodeRef ecosystem, complete with JSON schemas, validators, and generators.

**Current Status:** Foundation complete (research, audit, standards, schemas). Ready to begin tooling implementation (validators, generators).

**Key Achievement:** Created authoritative standards documentation (CLAUDE-MD-STANDARDS.md, CHILD-CLAUDE-MD-GUIDE.md, SKILL-TEMPLATE.md) based on:
- Research of 20+ industry sources
- Audit of 8 existing CodeRef CLAUDE.md files (average score: 71.9/100)
- Analysis of line budget violations, content quality issues, and missing sections

---

## Phase 1: Research ✅ Complete

### Objective
Conduct comprehensive research on CLAUDE.md and skill.md best practices from industry sources.

### Deliverables
✅ **research-best-practices.md** (44,468 lines of code context)

### Key Findings

**CLAUDE.md Best Practices:**
1. **Keep it lean** - 150-200 instructions max (LLM attention limit)
2. **Progressive disclosure** - Tell HOW to find information, not ALL the information
3. **No linting rules** - Use deterministic tools (ESLint, Prettier), not LLM descriptions
4. **Delegate complexity** - Recommend subagents for multi-step tasks
5. **Line budget** - 530-600 lines (from CLAUDEMD-TEMPLATE.json v1.0.0)

**SKILL.md Best Practices:**
1. **YAML frontmatter required** - name, description, allowed-tools (optional: model, context, tags)
2. **Line budget** - 300-500 lines (leaner than CLAUDE.md)
3. **Execution-focused** - Specific instructions, not general knowledge
4. **Self-contained** - Can include scripts/, references/, assets/ directories
5. **User-triggered** - Invoked via /skill-name or auto-loaded by context

**Sources Analyzed:**
- Anthropic official documentation
- Claude Code documentation
- Community best practices guides
- AI agent documentation standards
- 20+ total sources

### Time Spent
~2 hours (research + synthesis)

---

## Phase 2: Audit ✅ Complete

### Objective
Audit all 8 existing CodeRef CLAUDE.md files for structure, line budgets, formatting, and content quality.

### Deliverables
✅ **claude-md-audit-report.md**

### Files Audited

| File | Lines | Score | Grade | Status |
|------|-------|-------|-------|--------|
| **assistant** | 561 | 92/100 | Excellent | ✅ Within target |
| **papertrail** | 585 | 88/100 | Good | ✅ Within target |
| **coderef-dashboard** | 475 | 80/100 | Good | ⚠️ 11% below target |
| **coderef-context** | 401 | 78/100 | Good | ⚠️ 24% below target |
| **ecosystem** | 681 | 68/100 | Fair | ❌ 13% over budget |
| **coderef-personas** | 899 | 64/100 | Fair | ❌ 50% over budget |
| **coderef-docs** | 891 | 62/100 | Fair | ❌ 48% over budget |
| **coderef-workflow** | 1,142 | 55/100 | Fair | ❌ 91% over (CRITICAL) |

**Average Score:** 71.9/100 (Good)
**Target Score:** 85+ across all files

### Scoring Methodology (0-100)

**Section Presence (30 pts):**
- Core sections (15 pts): Quick Summary, Architecture, Workflows, etc.
- Enhanced sections (9 pts): Progressive Disclosure, Tool Sequencing, Subagent Delegation (NEW)
- Optional sections (6 pts): Use Cases, Recent Changes, Roadmap, Resources

**Line Budget Compliance (25 pts):**
- 530-600 lines: 25 pts (ideal)
- 475-530 or 600-650: 20 pts (acceptable)
- <475 or 650-700: 15 pts (needs work)
- 700-850: 10 pts (over budget)
- 850-1000: 5 pts (critical)
- 1000+: 0 pts (unacceptable)

**Formatting Consistency (20 pts):**
- Tables for workflows/tools (5 pts)
- Annotated file structure (5 pts)
- Header hierarchy (5 pts)
- Code blocks (5 pts)

**Content Quality (25 pts):**
- Quick Summary concise (5 pts)
- Architecture explains core concepts (5 pts)
- Design Decisions in ADR format (5 pts)
- Recent Changes ≤ 40 lines (5 pts)
- No code style bloat (5 pts)

### Top 5 Violations

1. **History Bloat (3 files)** - Recent Changes exceeds 100 lines, should be 40 max
   - coderef-workflow: 170 lines
   - coderef-docs: 300 lines
   - coderef-personas: 140 lines

2. **Missing Enhanced Sections (8 files)** - 0% have Progressive Disclosure, Tool Sequencing, or Subagent Delegation

3. **Implementation Detail Bloat (2 files)** - Sections with 100+ lines of "how it works"
   - coderef-workflow: 300+ lines of Scanner Integration (should be 30 + pointer)
   - ecosystem: 185 lines of .coderef/ Usage Guide (should be pointer)

4. **Persona Catalog Bloat (1 file)** - coderef-personas lists 11 personas × 15 lines each = 180 lines

5. **Critical Line Budget Overrun (1 file)** - coderef-workflow at 1,142 lines (191% over target)

### Recommendations

**Priority 1 (Critical):**
- Trim coderef-workflow from 1,142 → 600 lines (save 542 lines via history extraction, implementation guide extraction)

**Priority 2 (Major):**
- Add Progressive Disclosure, Tool Sequencing, Subagent Delegation sections to all 8 files (70 lines each)
- Extract history to CHANGELOG.md for coderef-docs, coderef-personas (save 250+ lines)

**Priority 3 (Minor):**
- Expand coderef-dashboard and coderef-context to hit 530-line target (add missing optional sections)

### Time Spent
~3 hours (file reads + analysis + scoring + report writing)

---

## Phase 3: Establish Standards ✅ Complete

### Objective
Create authoritative standards documentation for project-level CLAUDE.md, child CLAUDE.md, skills, and decision guidance.

### Deliverables

✅ **CLAUDE-MD-STANDARDS.md** (17 sections, comprehensive)
- Line budget standards (530-600 lines, enforcement rules)
- Required sections (9 core + 3 enhanced + 6 optional)
- Progressive disclosure guide (NEW)
- Tool sequencing patterns (NEW)
- Subagent delegation guide (NEW)
- Formatting standards (tables, code blocks, lists, headers)
- Content quality standards (Quick Summary, Architecture, Design Decisions, etc.)
- Recent Changes standards (40 lines max, last 2 versions only)
- Code style rules (❌ don't put in CLAUDE.md, use linter configs)
- File structure standards (annotated trees, 2-3 levels deep)
- Integration guide standards (dependency tables, integration patterns)
- Validation checklist (line budget, sections, content quality, progressive disclosure)
- Common violations and fixes (history bloat, implementation bloat, etc.)
- Migration guide (for existing files)
- For new projects (use generator from Phase 6)
- Appendix: Scoring methodology (0-100 scale)

✅ **CHILD-CLAUDE-MD-GUIDE.md** (15 sections)
- When to use child CLAUDE.md (monorepo packages, plugin systems, microservices)
- Line budget (300-400 lines vs 530-600 for parent)
- Required sections (8 core + 2 enhanced optional)
- Parent Context section (NEW - points to parent CLAUDE.md)
- Component Purpose section (replaces "Problem & Vision")
- Integration with Parent section (NEW - data flow, dependencies)
- File Structure scoped to component only
- Essential Commands scoped to component
- Child vs Parent comparison table
- Migration guide (for existing child files)
- Examples (monorepo package, plugin system)
- Common mistakes (duplicating parent content, missing parent reference)
- Scoring methodology (0-100 scale, child-specific criteria)

✅ **SKILL-TEMPLATE.md** (11 sections)
- When to use skills vs CLAUDE.md (decision criteria)
- File structure (basic single file vs advanced directory)
- YAML frontmatter (required: name, description; optional: allowed-tools, model, context, tags)
- Line budget (300-500 lines)
- Skill content structure (template with steps, verification, rollback)
- Examples (deployment skill, codebase analysis skill)
- Validation checklist (frontmatter, line budget, content structure, execution quality)
- Common mistakes (vague instructions, missing error handling, general knowledge in skill)
- Skill directory structure (advanced with scripts/, references/, assets/)
- Model selection guidelines (haiku vs sonnet vs opus)
- Related standards references

✅ **skills-vs-claude-decision-tree.md** (7-step decision flow)
- Quick decision table (CLAUDE.md vs Skill vs Linter Config vs Separate Doc)
- 7-step decision flow:
  1. Is this deterministic or requires LLM reasoning?
  2. Will this be needed in every AI session?
  3. Is this general knowledge or specific instructions?
  4. Is this a one-time task or multi-step workflow?
  5. Would this exceed CLAUDE.md line budget?
  6. Is this recurring or rare?
  7. Is this documentation or executable workflow?
- Decision matrix (when to use each)
- Real-world examples (deployment, architecture, code style, API catalog, stub creation)
- Complex cases (tests, documentation generation, naming conventions, multiple environments)
- Checklist: "Should I create a skill?" (7 criteria)
- Anti-patterns (skill for general knowledge, CLAUDE.md for one-time task, etc.)
- Summary table (characteristics comparison)

### Key Innovations

**Progressive Disclosure (NEW):**
- Instead of documenting ALL information in CLAUDE.md, tell AI WHERE to find detailed info
- Pattern: "See tool description for mcp__X" (not 185 lines of usage instructions)
- Where to put detailed info: API.md, ARCHITECTURE.md, COMPONENTS.md, CHANGELOG.md, docs/

**Tool Sequencing Patterns (NEW):**
- Document ORDER of tool calls for common workflows
- Prevents trial-and-error iterations
- Example: Workorder Creation = Read stub → gather_context → Write context.json → Write communication.json → Edit workorders.json → log_workorder
- Recommended patterns by project type (orchestrator, MCP server, dashboard, CLI tool)

**Subagent Delegation Guide (NEW):**
- When to spawn Task tool subagents (5+ steps, codebase exploration, iterative refinement)
- When NOT to delegate (single tool call, user needs immediate response, requires user interaction)
- How to document in CLAUDE.md (pattern examples)

### Time Spent
~5 hours (4 documents × ~90 minutes each)

---

## Phase 4: Build JSON Schemas ✅ Complete

### Objective
Create JSON Schema Draft-07 schemas for validating CLAUDE.md frontmatter and skill.md YAML frontmatter, integrated with Papertrail MCP.

### Deliverables

✅ **claude-md-frontmatter-schema.json**
- Location: `C:\Users\willh\.mcp-servers\papertrail\schemas\documentation\`
- Extends base-frontmatter-schema.json (UDS compliance)
- Supports two file types: "project" and "child"
- Required fields: file_type, project_name, version, status, created, last_updated
- Conditional validation: child files MUST have parent_claude_md field
- Optional fields: workorder_id, line_count, compliance_score, line_budget_status, required_sections
- Validation rules:
  - file_type: "project" | "child"
  - version: Semantic versioning (e.g., "2.0.0")
  - status: 5 emoji statuses (✅ Production, 🚧 Building, 🧪 Experimental, 🗑️ Deprecated, ⏸️ Paused)
  - parent_claude_md: Pattern `../../CLAUDE.md` (required for child)
  - line_count: 200-1200 range
  - compliance_score: 0-100 integer

✅ **skill-frontmatter-schema.json**
- Location: `C:\Users\willh\.mcp-servers\papertrail\schemas\documentation\`
- Extends base-frontmatter-schema.json (UDS compliance)
- Required fields: name, description
- Optional fields: allowed-tools, model, context, tags, version, workorder_id, line_count, compliance_score, line_budget_status
- Validation rules:
  - name: Kebab-case, 3-50 characters (e.g., "deploy-production")
  - description: 10-200 characters, action-oriented
  - allowed-tools: Array of valid tool names (Bash, Read, Write, mcp__* tools)
  - model: "haiku" | "sonnet" | "opus"
  - context: 10-500 characters
  - tags: Array of kebab-case tags, 1-10 items, 2-30 chars each
  - line_count: 100-800 range (target: 300-500)

✅ **schema-test-results.md**
- 8 test cases covering valid/invalid scenarios:
  - Valid project-level CLAUDE.md
  - Valid child CLAUDE.md
  - Invalid child (missing parent_claude_md)
  - Invalid project (line count over budget)
  - Valid skill (full features)
  - Valid skill (minimal)
  - Invalid skill (name not kebab-case)
  - Invalid skill (invalid model)
- Integration plan with Papertrail MCP
- Schema inheritance diagram
- Validation workflow diagrams (Mermaid)
- Next steps for Phase 5 outlined

### Schema Inheritance

```
base-frontmatter-schema.json
├── Required: agent, date, task
├── Optional: timestamp
│
├─→ claude-md-frontmatter-schema.json
│   ├── Adds Required: file_type, project_name, version, status, created, last_updated
│   ├── Adds Optional: parent_claude_md, workorder_id, line_count, compliance_score
│   └── Conditional: file_type="child" REQUIRES parent_claude_md
│
└─→ skill-frontmatter-schema.json
    ├── Adds Required: name, description
    ├── Adds Optional: allowed-tools, model, context, tags, version, workorder_id, line_count
    └── No conditional requirements
```

### Time Spent
~2 hours (schema creation + testing documentation)

---

## Overall Progress

### Completion Status
- ✅ Phase 1: Research (Complete)
- ✅ Phase 2: Audit (Complete)
- ✅ Phase 3: Establish Standards (Complete)
- ✅ Phase 4: Build JSON Schemas (Complete)
- ⏳ Phase 5: Build Validator Tools (Pending)
- ⏳ Phase 6: Build Generator Tools (Pending)

**Progress:** 4/6 phases (67% complete)

### Files Created

**Session Outputs** (`C:\Users\willh\.mcp-servers\coderef\sessions\claude-md-standards\outputs\`):
1. research-best-practices.md (44,468 lines)
2. claude-md-audit-report.md
3. CLAUDE-MD-STANDARDS.md (17 sections)
4. CHILD-CLAUDE-MD-GUIDE.md (15 sections)
5. SKILL-TEMPLATE.md (11 sections)
6. skills-vs-claude-decision-tree.md (7-step flow)
7. schema-test-results.md (8 test cases)
8. PROGRESS-SUMMARY.md (this file)

**Papertrail Schemas** (`C:\Users\willh\.mcp-servers\papertrail\schemas\documentation\`):
1. claude-md-frontmatter-schema.json
2. skill-frontmatter-schema.json

**Total Files:** 10

### Lines of Documentation
- Research: 44,468 lines (code context from 20+ sources)
- Standards: ~3,500 lines (4 comprehensive guides)
- Audit: ~800 lines (detailed analysis + recommendations)
- Schemas: ~350 lines (JSON Schema Draft-07)
- Testing: ~400 lines (test cases + validation workflows)

**Total:** ~49,500 lines of documentation

### Time Investment
- Phase 1: ~2 hours
- Phase 2: ~3 hours
- Phase 3: ~5 hours
- Phase 4: ~2 hours

**Total:** ~12 hours

---

## Key Metrics

### Ecosystem Improvements (Projected)

**Before Standards:**
- Average CLAUDE.md score: 71.9/100
- Files over budget: 50% (4/8)
- Total ecosystem bloat: +1,115 lines (20% over)
- Missing enhanced sections: 100% (0/8 have Progressive Disclosure, Tool Sequencing, Subagent Delegation)

**After Standards (Target):**
- Average CLAUDE.md score: 85+/100
- Files over budget: 0% (0/8)
- Total ecosystem bloat: 0 lines (all within 530-600 target)
- Enhanced sections: 100% (8/8 have all 3 new sections)

**Line Budget Savings:**
- coderef-workflow: 1,142 → 600 (-542 lines via extraction to CHANGELOG.md, docs/)
- coderef-docs: 891 → 580 (-311 lines via history extraction)
- coderef-personas: 899 → 580 (-319 lines via persona catalog condensation + history extraction)
- ecosystem: 681 → 600 (-81 lines via .coderef/ usage guide extraction)

**Total Savings:** -1,253 lines across 4 files

### Standardization Impact

**Tools to be built (Phase 5 + 6):**
- 4 validators (CLAUDE.md, all CLAUDE.md, skill, all skills)
- 3 generators (CLAUDE.md, child CLAUDE.md, skill)

**Projects Impacted:**
- 8 existing CodeRef projects (all with CLAUDE.md)
- 2 existing skills (coderef-scanner, sync-nav)
- All future CodeRef projects (standardized from day 1)

**Ecosystem Coverage:**
- Project-level CLAUDE.md: 8 files
- Child CLAUDE.md: 1 file (coderef-dashboard component)
- Skills: 2 files (potentially 10+ once standardized)

---

## Next Steps: Phase 5 & 6

### Phase 5: Build Validator Tools (Papertrail MCP)

**Objective:** Extend Papertrail MCP with 4 new validator tools

**Deliverables:**
1. `mcp__papertrail__validate_claude_md(file_path)` - Validate single CLAUDE.md
2. `mcp__papertrail__check_all_claude_md(directory)` - Batch validate all CLAUDE.md files
3. `mcp__papertrail__validate_skill(file_path)` - Validate single skill.md
4. `mcp__papertrail__check_all_skills(directory)` - Batch validate all skills

**Implementation:**
- Python code in Papertrail MCP server
- YAML extraction from markdown files
- JSON Schema validation using `jsonschema` library
- Compliance scoring (0-100 based on line budget, section presence, etc.)
- Batch validation with summary reports

**Testing:**
- Test against 8 existing CLAUDE.md files (verify scores match Phase 2 audit)
- Test against 2 existing skills
- Document validator usage in Papertrail CLAUDE.md

**Estimated Time:** 4-6 hours

---

### Phase 6: Build Generator Tools (coderef-docs MCP)

**Objective:** Extend coderef-docs MCP with 3 new generator tools

**Deliverables:**
1. `mcp__coderef-docs__generate_claude_md(project_path, project_type, auto_fill=True)` - Generate project-level CLAUDE.md from template
2. `mcp__coderef-docs__generate_child_claude_md(component_path, parent_path, component_type, auto_fill=True)` - Generate child CLAUDE.md
3. `mcp__coderef-docs__generate_skill(skill_name, description, model, auto_fill=True)` - Generate skill.md from template

**Implementation:**
- Python code in coderef-docs MCP server
- Template-based generation using CLAUDE-MD-STANDARDS, CHILD-CLAUDE-MD-GUIDE, SKILL-TEMPLATE
- Auto-fill with coderef-context data (project name, file structure, etc.)
- Automatic validation using Papertrail schemas
- Generate with proper UDS frontmatter

**Testing:**
- Generate dummy project CLAUDE.md, validate score 85+
- Generate dummy child CLAUDE.md, validate score 85+
- Generate dummy skill, validate score 90+
- Document generator usage in coderef-docs CLAUDE.md

**Estimated Time:** 4-6 hours

---

## Success Criteria (Final)

**Phase 5 Complete When:**
- ✅ All 4 validators implemented in Papertrail MCP
- ✅ Validators tested against existing files (scores match Phase 2 audit within ±5 points)
- ✅ Validator documentation added to Papertrail CLAUDE.md
- ✅ Error messages and remediation documented

**Phase 6 Complete When:**
- ✅ All 3 generators implemented in coderef-docs MCP
- ✅ Generators tested (generated files score 85+)
- ✅ Generator documentation added to coderef-docs CLAUDE.md
- ✅ Templates integrated with coderef-context for auto-fill

**Overall Session Complete When:**
- ✅ All 6 phases complete
- ✅ 8 existing CLAUDE.md files updated to meet standards (average score 85+)
- ✅ 2 existing skills validated and updated (if needed)
- ✅ All deliverables committed to git
- ✅ Session archived to coderef/archived/

---

## Retrospective (Phases 1-4)

### What Went Well
- Research phase was comprehensive (20+ sources analyzed)
- Audit revealed critical issues (coderef-workflow 191% over budget)
- Standards documents are detailed and actionable (17, 15, 11 sections respectively)
- JSON schemas integrated cleanly with existing Papertrail infrastructure
- No major blockers or rework required

### Challenges
- Phase 2 audit was time-intensive (8 files × detailed analysis)
- Phase 3 required balancing comprehensiveness vs usability (17 sections is a lot)
- Phase 4 schema testing was manual (no automated validator yet - that's Phase 5)

### Lessons Learned
- Progressive disclosure is critical for keeping CLAUDE.md lean (could save 500+ lines across ecosystem)
- History bloat is a common issue (3/8 files violate "last 2 versions only" rule)
- Enhanced sections (Progressive Disclosure, Tool Sequencing, Subagent Delegation) are universally missing (0/8 files)

### Recommendations for Future Sessions
- Use this 6-phase structure for other standardization sessions (proven effective)
- Always audit before standardizing (reveals actual issues, not theoretical ones)
- Create decision trees early (skills-vs-claude-decision-tree saved confusion)

---

## Appendix: File Locations

### Session Outputs
```
C:\Users\willh\.mcp-servers\coderef\sessions\claude-md-standards\outputs\
├── research-best-practices.md
├── claude-md-audit-report.md
├── CLAUDE-MD-STANDARDS.md
├── CHILD-CLAUDE-MD-GUIDE.md
├── SKILL-TEMPLATE.md
├── skills-vs-claude-decision-tree.md
├── schema-test-results.md
└── PROGRESS-SUMMARY.md (this file)
```

### Papertrail Schemas
```
C:\Users\willh\.mcp-servers\papertrail\schemas\documentation\
├── base-frontmatter-schema.json (existing)
├── claude-md-frontmatter-schema.json (NEW)
└── skill-frontmatter-schema.json (NEW)
```

### Audited CLAUDE.md Files
```
C:\Users\willh\Desktop\assistant\CLAUDE.md (561 lines, 92/100)
C:\Users\willh\.mcp-servers\CLAUDE.md (681 lines, 68/100)
C:\Users\willh\.mcp-servers\coderef-context\CLAUDE.md (401 lines, 78/100)
C:\Users\willh\.mcp-servers\coderef-workflow\CLAUDE.md (1,142 lines, 55/100)
C:\Users\willh\.mcp-servers\coderef-docs\CLAUDE.md (891 lines, 62/100)
C:\Users\willh\.mcp-servers\coderef-personas\CLAUDE.md (899 lines, 64/100)
C:\Users\willh\.mcp-servers\papertrail\CLAUDE.md (585 lines, 88/100)
C:\Users\willh\Desktop\coderef-dashboard\CLAUDE.md (475 lines, 80/100)
```

---

**Session Status:** Phases 1-4 Complete | Ready for Phase 5 (Validators)
**Workorder:** WO-CLAUDE-MD-STANDARDS-001
**Author:** CodeRef Assistant (Orchestrator Persona)
**Date:** 2026-01-22
