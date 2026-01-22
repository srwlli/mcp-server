# CLAUDE.md & Skills Best Practices Research Report

**Session:** WO-CLAUDE-MD-STANDARDS-001
**Phase:** 1 - External Research
**Date:** 2026-01-22
**Status:** Complete

---

## Executive Summary

This report synthesizes industry best practices for CLAUDE.md and SKILL.md documentation based on official Anthropic guidelines, community resources, and AI agent documentation standards research. Key findings reveal that effective CLAUDE.md files should be **lean, focused, and context-aware**, prioritizing progressive disclosure over comprehensive documentation.

**Key Insight:** CLAUDE.md is NOT a comprehensive manual—it's a curated set of guardrails and pointers. Think of it as an onboarding guide for your AI co-developer.

---

## 1. CLAUDE.md Best Practices (2025)

### 1.1 Core Principles

#### **Keep It Lean and Focused**
- CLAUDE.md goes into **every single session** - ensure contents are universally applicable
- Frontier thinking LLMs can follow **~150-200 instructions** with reasonable consistency
- Smaller models (and non-thinking models) can attend to **fewer instructions**
- Smaller models degrade MUCH worse, MUCH more quickly with instruction bloat

**Source:** [My 7 essential Claude Code best practices for production-ready AI in 2025](https://www.eesel.ai/blog/claude-code-best-practices)

#### **Use Progressive Disclosure**
- Don't tell Claude all the information it could possibly need
- Instead, **tell it how to find** important information
- Claude can retrieve info when needed, avoiding context bloat

**Example:** Instead of documenting every API endpoint, point to OpenAPI schema location

**Source:** [Writing a good CLAUDE.md | HumanLayer Blog](https://www.humanlayer.dev/blog/writing-a-good-claude-md)

#### **Never Send an LLM to Do a Linter's Job**
- LLMs are expensive and slow compared to traditional linters/formatters
- **Avoid code style details** in CLAUDE.md - use deterministic tools instead
- Code style guidelines add irrelevant snippets, degrading performance

**Source:** [Claude Code: Best practices for agentic coding](https://www.anthropic.com/engineering/claude-code-best-practices)

### 1.2 What to Include

**Common Commands:**
- `npm run test`, `npm run build`, etc.
- Essential development workflows

**Code Style Guidelines (High-Level Only):**
- "Use ES modules, not CommonJS"
- "Always use functional components with hooks"
- Architectural preferences, NOT linting rules

**Key Files or Architectural Patterns:**
- "State management is handled by Zustand; see src/stores for examples"
- Point to WHERE patterns are, not full documentation

**Testing Instructions:**
- "New components require a corresponding test file using React Testing Library"
- When/how to run tests

**Source:** [What's a Claude.md File? 5 Best Practices to Use](https://apidog.com/blog/claude-md/)

### 1.3 Context Management

#### **Strategic Documentation**
- Treat CLAUDE.md as high-level guardrails and pointers
- Use it to guide where to invest in AI-friendly tools
- NOT a comprehensive manual

#### **Subagents for Complexity**
- Strong use of subagents for complex problems
- Telling Claude to use subagents early preserves context availability
- Subagents can verify details or investigate questions independently

**Source:** [Claude's Context Engineering Secrets: Best Practices Learned from Anthropic | Bojie Li](https://01.me/en/2025/12/context-engineering-from-claude/)

#### **Context Compression**
- Periodically reset or prune context during long sessions
- Prefer retrieval and summaries over dumping raw logs
- Store just: the plan, key decisions, and latest artifacts

**Source:** [A Guide to Claude Code 2.0 and getting better at using coding agents | sankalp's blog](https://sankalp.bearblog.dev/my-experience-with-claude-code-20-and-how-to-get-better-at-using-coding-agents/)

### 1.4 Structure and Formatting

#### **Use Markdown Headings for Sections**
- Separating instructions into dedicated sections helps model prioritize
- Use whitespace and line breaks to separate instructions

#### **Clear, Concise Language**
- Leave no room for misinterpretation
- Avoid technical jargon or overly complex sentences
- Use headings and ordered/unordered list markdown

**Source:** [Prompting guide | ElevenLabs Documentation](https://elevenlabs.io/docs/agents-platform/best-practices/prompting-guide)

---

## 2. SKILL.md Format and Structure

### 2.1 Required Components

Every skill consists of:

1. **SKILL.md file** (required) with:
   - **YAML frontmatter** (between `---` markers)
   - **Markdown instructions** (what Claude does when skill is active)

2. **Optional resources:**
   - `scripts/` - Executable code (Python/Bash/etc.)
   - `references/` - Documentation loaded into context as needed
   - `assets/` - Files used in output (templates, icons, fonts)

**Source:** [Extend Claude with skills - Claude Code Docs](https://code.claude.com/docs/en/skills)

### 2.2 YAML Frontmatter Schema

**Required fields:**
```yaml
---
name: skill-name          # Required: kebab-case identifier
description: Brief description  # Required: One-line purpose
---
```

**Optional fields:**
```yaml
allowed-tools: Read, Grep, Glob  # Tool restrictions
model: haiku                      # AI model (haiku/sonnet)
context: fork                     # Context mode (fork/default)
tags: [tag1, tag2]               # Categorization
```

**Source:** [What Is SKILL.md in Claude Skills? Structure, Resources & Loading](https://skywork.ai/blog/ai-agent/claude-skills-skill-md-resources-runtime-loading/)

### 2.3 Best Practices for Skills

#### **Keep SKILL.md Under 500 Lines**
- Move detailed reference material to separate files in `references/`
- Skills should be focused on a single narrow task

#### **Invocation Modes**
- Users can type `/skill-name` to invoke directly
- Claude can load automatically when relevant to conversation

#### **File Organization**
```
.claude/skills/skill-name/
├── SKILL.md           # Required: Frontmatter + instructions
├── scripts/           # Optional: Executable code
├── references/        # Optional: Documentation
└── assets/            # Optional: Output templates
```

**Source:** [skills/skills/skill-creator/SKILL.md at main · anthropics/skills](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md)

### 2.4 Skills vs CLAUDE.md Decision Guide

**Use a Skill when:**
- Focused, tool-restricted behavior needed
- Model-specific optimization (e.g., haiku for speed)
- Isolated, reusable workflow
- Context fork required (avoid polluting main session)

**Use CLAUDE.md when:**
- Project-level context needed across all sessions
- Comprehensive architecture understanding
- Universal guardrails and conventions
- High-level pointers to resources

**Source:** [Claude Agent Skills: A First Principles Deep Dive](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/)

---

## 3. AI Agent Documentation Standards

### 3.1 System Prompt Structure

A system prompt (like CLAUDE.md) serves as the **personality and policy blueprint** of your AI agent, defining:

1. **Role** - Agent's persona and expertise
2. **Goals** - What the agent should accomplish
3. **Allowable Tools** - Tool restrictions
4. **Step-by-Step Instructions** - For certain tasks
5. **Guardrails** - What the agent should NOT do

**Source:** [LLM Agents | Prompt Engineering Guide](https://www.promptingguide.ai/research/llm-agents)

### 3.2 Agent Experience (AX) Design

Design documentation for "Agent Experience" using:

- **Clean, parseable formats** - OpenAPI schemas for APIs
- **llms.txt files** - Summary documentation for LLM consumption
- **Explicit type definitions** - Clear interfaces
- **MCP (Model Context Protocol)** - Standardized tool integration

**Source:** [AddyOsmani.com - How to write a good spec for AI agents](https://addyosmani.com/blog/good-spec/)

### 3.3 Tool Documentation

- **Clearly define** when and how each tool should be used
- Don't rely solely on tool descriptions
- Provide **usage context and sequencing logic**

**Example:** Instead of just listing `fetch()`, document: "Use fetch() for external APIs; use internal API client for authenticated requests"

**Source:** [A practical guide to building agents](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf)

### 3.4 Narrow Agent Responsibilities

Each agent should have:

- **Narrow, clearly defined** knowledge base
- **Specific responsibilities** (not kitchen-sink approach)
- **Fewer edge cases** to handle
- **Clearer success criteria**

**Source:** [The ultimate LLM agent build guide](https://www.vellum.ai/blog/the-ultimate-llm-agent-build-guide)

---

## 4. Comparison with Current CLAUDEMD-TEMPLATE.json

### 4.1 Alignment Analysis

**✅ Current Template Strengths:**

1. **Lean Length Target (530-600 lines)** - Aligns with "keep it lean" principle
2. **Compact Tool Documentation (Tables)** - Matches "avoid code style details" guideline
3. **Examples Over Prose** - Aligns with "clear, concise language" best practice
4. **Trim History (Last 2 Versions Only)** - Reduces context bloat
5. **Integration First** - Progressive disclosure (point to where to find info)
6. **Use Cases** - Concrete examples for clarity

**❌ Current Template Gaps:**

1. **No Progressive Disclosure Guidance** - Template doesn't emphasize "how to find" over "what to know"
2. **No Tool Usage Sequencing** - Missing "when and how" to use tools
3. **No Subagent Guidance** - No recommendation to delegate complex tasks
4. **No Agent Experience (AX) Principles** - Missing llms.txt, OpenAPI schema pointers
5. **No Skills vs CLAUDE.md Decision Guide** - When to create a skill instead

### 4.2 Section-by-Section Review

| Template Section | Best Practice Alignment | Recommendation |
|------------------|------------------------|----------------|
| Quick Summary | ✅ Concise, high-level | Keep |
| Problem & Vision | ⚠️ Optional, can bloat | Keep optional, add size limit (50 lines max) |
| Architecture | ✅ High-level patterns | Add "Progressive Disclosure" subsection |
| Tools/Features Catalog | ✅ Tables, compact | Add "Tool Sequencing" column |
| Core Workflows | ⚠️ Can get verbose | Add 100-line budget, move details to separate files |
| File Structure | ✅ ASCII tree | Keep |
| Design Decisions | ✅ Rationale-focused | Keep |
| Integration Guide | ✅ Pointers to external systems | Keep |
| Essential Commands | ⚠️ Missing context | Add "when to use" guidance |
| Use Cases | ✅ Examples | Keep |
| Recent Changes | ✅ Last 2 versions only | Keep |
| Next Steps/Roadmap | ⚠️ Can get stale | Keep, but add "update frequency" guideline |
| Resources | ✅ Links, no duplication | Keep |

---

## 5. Recommendations for Template v1.1.0

### 5.1 Add New Sections

**1. Progressive Disclosure (10-15 lines)**
- Document WHERE to find detailed info (not the info itself)
- Point to llms.txt, OpenAPI schemas, architecture diagrams
- Teach Claude to retrieve, not memorize

**2. Tool Usage Sequencing (15-20 lines)**
- When to use each tool
- Tool dependencies (e.g., "Run linter BEFORE committing")
- Avoid: Tool descriptions only

**3. Subagent Delegation Guide (10-15 lines)**
- When to spawn subagents (complex investigations, parallel work)
- How to structure delegation prompts
- Benefits: Context preservation, parallelization

### 5.2 Update Existing Sections

**Core Workflows:**
- Add 100-line hard budget (currently unlimited)
- Encourage moving detailed workflows to separate files in `docs/workflows/`
- Link to workflow files instead of documenting inline

**Essential Commands:**
- Add "Context" column to command table
- Example: `npm test` → "Run before committing; use --watch during development"

**Problem & Vision (Optional):**
- Add 50-line budget
- Clarify when to include: "New concept, solving specific problem, not well-known pattern"

### 5.3 Add Quality Principles

**New Principle: "Progressive Disclosure Over Comprehensiveness"**
- Tell Claude how to find information, not all the information
- Point to schemas, docs, and tools - don't duplicate them

**New Principle: "Delegate Complexity to Subagents"**
- Complex investigations → Spawn subagent
- Parallel work → Multiple subagents
- Preserves main session context

**New Principle: "Design for Agent Experience (AX)"**
- Include llms.txt pointers for documentation
- Reference OpenAPI schemas for APIs
- Explicit type definitions for interfaces

### 5.4 Add Skills Guidance

**New Section: "Skills vs CLAUDE.md Decision Tree" (10-15 lines)**

**Create a Skill if:**
- Task is narrow and reusable (e.g., "generate API client from OpenAPI spec")
- Needs tool restrictions (e.g., read-only analysis)
- Requires model optimization (e.g., haiku for speed)
- Should fork context (avoid polluting main session)

**Document in CLAUDE.md if:**
- Applies to all project sessions
- Provides architectural context
- High-level guardrails or pointers

---

## 6. Industry Patterns Not in Template

### 6.1 llms.txt Convention

**What:** A standard file format for AI-friendly documentation
**Purpose:** Summaries optimized for LLM consumption
**Recommendation:** Add to template as optional resource pointer

**Example:**
```markdown
## Resources
- [Full Documentation](./docs/API.md)
- [LLM Summary](./docs/llms.txt) - AI-optimized API reference
```

**Source:** [AddyOsmani.com - How to write a good spec for AI agents](https://addyosmani.com/blog/good-spec/)

### 6.2 MCP (Model Context Protocol)

**What:** Standardized protocol for tool integration (Anthropic)
**Purpose:** Consistent tool interfaces across agents
**Recommendation:** Add to Integration Guide section

**Example:**
```markdown
## Integration Guide

### MCP Servers
- **coderef-context** - Code analysis MCP server
- **coderef-workflow** - Planning and execution MCP server
```

### 6.3 OpenAPI Schema References

**What:** Point to API schemas instead of documenting endpoints
**Purpose:** Avoid duplication, enable auto-discovery
**Recommendation:** Add to Progressive Disclosure section

**Example:**
```markdown
## Progressive Disclosure

### API Documentation
- OpenAPI Schema: `./docs/openapi.yaml`
- Use schema for endpoint discovery (don't document inline)
```

---

## 7. Skills Template Recommendations

### 7.1 Proposed SKILL-TEMPLATE.md Structure

```markdown
---
name: skill-name
description: One-line purpose of this skill
allowed-tools: Read, Write, Bash  # Optional: Tool restrictions
model: sonnet                      # Optional: haiku/sonnet (default: sonnet)
context: default                   # Optional: default/fork (default: default)
tags: [category, type]            # Optional: Categorization
---

# Skill Name

## Overview
Brief description of what this skill does (2-3 sentences).

## When to Use This Skill
- Use case 1
- Use case 2

## Workflow

### Step 1: [Action]
Description of first step.

### Step 2: [Action]
Description of second step.

## Queries This Skill Answers
- "Question pattern 1?"
- "Question pattern 2?"

## Output Format
Describe expected output format (JSON, markdown, etc.).

## Examples

### Example 1: [Scenario]
**Input:** Description of input
**Output:** Expected output

## Error Handling
Common errors and how to resolve them.

## Resources
- [Reference Doc 1](../references/doc1.md)
- [Reference Doc 2](../references/doc2.md)
```

### 7.2 Frontmatter Schema

**Required:**
- `name` (string, kebab-case)
- `description` (string, 1-2 sentences)

**Optional:**
- `allowed-tools` (array of strings, e.g., `[Read, Grep, Glob]`)
- `model` (enum: `haiku` | `sonnet`, default: `sonnet`)
- `context` (enum: `default` | `fork`, default: `default`)
- `tags` (array of strings, for categorization)

### 7.3 Content Sections

**Required:**
1. **Overview** (10-20 lines) - What the skill does
2. **Workflow** (50-100 lines) - Step-by-step instructions
3. **Examples** (20-40 lines) - Concrete scenarios

**Optional:**
4. **When to Use** (5-10 lines) - Use case triggers
5. **Queries** (5-10 lines) - Question patterns this skill answers
6. **Output Format** (5-10 lines) - Expected output structure
7. **Error Handling** (10-20 lines) - Common errors and fixes
8. **Resources** (5-10 lines) - Links to reference docs

**Total Budget:** 300-500 lines (frontmatter + content)

---

## 8. Key Findings Summary

### 8.1 Critical Insights

1. **CLAUDE.md is NOT a manual** - It's a curated set of guardrails and pointers
2. **150-200 instruction limit** - LLMs can follow ~150-200 instructions consistently
3. **Progressive disclosure wins** - Tell Claude how to find info, not all the info
4. **Never use LLMs for linting** - Use deterministic tools for code style
5. **Subagents preserve context** - Delegate complexity early to maintain main session quality

### 8.2 Template Strengths

- ✅ 530-600 line target aligns with "keep it lean" principle
- ✅ Compact tool tables avoid code style bloat
- ✅ Examples over prose matches best practices
- ✅ Trim history (last 2 versions) reduces context bloat
- ✅ Integration-first approach enables progressive disclosure

### 8.3 Template Gaps

- ❌ No progressive disclosure guidance (tell how to find, not what to know)
- ❌ No tool usage sequencing (when and how to use tools)
- ❌ No subagent delegation guide
- ❌ No Agent Experience (AX) principles (llms.txt, OpenAPI schemas)
- ❌ No skills vs CLAUDE.md decision tree

### 8.4 Skills Best Practices

- ✅ YAML frontmatter with required `name` and `description`
- ✅ 300-500 line budget for SKILL.md
- ✅ Optional resources in `scripts/`, `references/`, `assets/`
- ✅ Use skills for narrow, reusable, tool-restricted workflows
- ✅ Use CLAUDE.md for universal project context

---

## 9. Next Steps

### Phase 2: Audit Existing Files
- Score all 35+ CLAUDE.md files against these best practices
- Identify violations:
  - Line budget overruns
  - Missing progressive disclosure
  - Lack of tool sequencing
  - No subagent guidance

### Phase 3: Establish Standards
- Create CLAUDE-MD-STANDARDS.md incorporating these findings
- Add 3 new sections: Progressive Disclosure, Tool Sequencing, Subagent Guide
- Create SKILL-TEMPLATE.md with frontmatter schema
- Document skills vs CLAUDE.md decision tree

### Phase 4: Build Schema
- JSON Schema for CLAUDE.md validation (15 standard + 3 optional sections)
- JSON Schema for SKILL.md frontmatter validation
- Include line budget metadata

### Phase 5: Build Validator
- Papertrail MCP tools: `validate_claude_md`, `check_all_claude_md`, `validate_skill`
- Check structure, sections, line budgets, formatting
- Return 0-100 score with detailed errors/warnings

### Phase 6: Build Generator
- coderef-docs MCP tools: `generate_claude_md`, `generate_child_claude_md`, `generate_skill`
- Auto-populate from package.json, README.md, existing docs
- Template-based with substitution

---

## Sources

### CLAUDE.md Best Practices
- [My 7 essential Claude Code best practices for production-ready AI in 2025](https://www.eesel.ai/blog/claude-code-best-practices)
- [Claude Agent SDK Best Practices for AI Agent Development (2025)](https://skywork.ai/blog/claude-agent-sdk-best-practices-ai-agents-2025/)
- [Claude Code: Best practices for agentic coding](https://www.anthropic.com/engineering/claude-code-best-practices)
- [What's a Claude.md File? 5 Best Practices to Use](https://apidog.com/blog/claude-md/)
- [Writing a good CLAUDE.md | HumanLayer Blog](https://www.humanlayer.dev/blog/writing-a-good-claude-md)
- [Claude's Context Engineering Secrets: Best Practices Learned from Anthropic | Bojie Li](https://01.me/en/2025/12/context-engineering-from-claude/)
- [A Guide to Claude Code 2.0 and getting better at using coding agents | sankalp's blog](https://sankalp.bearblog.dev/my-experience-with-claude-code-20-and-how-to-get-better-at-using-coding-agents/)

### Skills Documentation
- [Extend Claude with skills - Claude Code Docs](https://code.claude.com/docs/en/skills)
- [GitHub - anthropics/skills: Public repository for Agent Skills](https://github.com/anthropics/skills)
- [Agent Skills - Claude Docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [skills/skills/skill-creator/SKILL.md at main · anthropics/skills](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md)
- [What Is SKILL.md in Claude Skills? Structure, Resources & Loading](https://skywork.ai/blog/ai-agent/claude-skills-skill-md-resources-runtime-loading/)
- [Claude Agent Skills: A First Principles Deep Dive](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/)

### AI Agent Documentation Standards
- [Prompting guide | ElevenLabs Documentation](https://elevenlabs.io/docs/agents-platform/best-practices/prompting-guide)
- [LLM Agents | Prompt Engineering Guide](https://www.promptingguide.ai/research/llm-agents)
- [A practical guide to building agents](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf)
- [AddyOsmani.com - How to write a good spec for AI agents](https://addyosmani.com/blog/good-spec/)
- [The ultimate LLM agent build guide](https://www.vellum.ai/blog/the-ultimate-llm-agent-build-guide)

---

**Report Compiled:** 2026-01-22
**Total Sources:** 20 articles, guides, and official documentation
**Research Status:** ✅ Complete
**Next Phase:** Audit existing CLAUDE.md files against these best practices
