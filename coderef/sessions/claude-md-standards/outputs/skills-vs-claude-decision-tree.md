# Skills vs CLAUDE.md Decision Tree (v1.0.0)

**Purpose:** Decision guide for choosing between skill.md, CLAUDE.md, or other documentation formats
**Applies to:** All CodeRef projects
**Created:** 2026-01-22
**Workorder:** WO-CLAUDE-MD-STANDARDS-001

---

## Quick Decision Table

| Question | CLAUDE.md | Skill | Linter Config | Separate Doc |
|----------|-----------|-------|---------------|--------------|
| **Needed in every session?** | ✅ Yes | ❌ No | ❌ No | ❌ No |
| **Context or instructions?** | Context | Instructions | Rules | Context |
| **General or specific?** | General | Specific | N/A | General |
| **One-time or recurring?** | Recurring | One-time/rare | N/A | Reference |
| **LLM or deterministic?** | LLM | LLM | Deterministic | Either |

---

## Decision Flow

### Step 1: Is this deterministic or requires LLM reasoning?

```
Is this a rule that can be checked mechanically?
(e.g., "use 2 spaces for indentation", "imports must be sorted")
├─ YES → Linter config file (ESLint, Prettier, etc.)
└─ NO → Continue to Step 2
```

**Examples:**
- ✅ Linter: "Use 2 spaces for indentation" → `.prettierrc`
- ✅ Linter: "Imports must be sorted alphabetically" → `.eslintrc.json`
- ❌ NOT linter: "When to use useMemo vs useCallback" → Continue to Step 2

---

### Step 2: Will this be needed in every AI session?

```
Will the AI need this information in EVERY session?
├─ YES → CLAUDE.md
└─ NO → Continue to Step 3
```

**Examples:**
- ✅ CLAUDE.md: "Our architecture uses React 18 + Next.js 14" (needed always)
- ✅ CLAUDE.md: "Integration points with coderef-context MCP server" (needed always)
- ❌ NOT CLAUDE.md: "How to deploy to production" (needed rarely) → Continue to Step 3

---

### Step 3: Is this general knowledge or specific instructions?

```
Is this explaining HOW THE SYSTEM WORKS (knowledge)
or WHAT TO DO for a specific task (instructions)?
├─ KNOWLEDGE → CLAUDE.md
└─ INSTRUCTIONS → Continue to Step 4
```

**Examples:**
- ✅ CLAUDE.md (Knowledge): "Data flows from API → Store → Components"
- ✅ CLAUDE.md (Knowledge): "We use Zustand for state management"
- ❌ NOT CLAUDE.md (Instructions): "Run these 10 commands to deploy" → Continue to Step 4

---

### Step 4: Is this a one-time task or multi-step workflow?

```
Is this a single tool call or a complex workflow?
├─ SINGLE TOOL CALL → CLAUDE.md Essential Commands section
└─ MULTI-STEP WORKFLOW → Continue to Step 5
```

**Examples:**
- ✅ CLAUDE.md Essential Commands: `npm run build` (single command)
- ✅ CLAUDE.md Essential Commands: `npm test` (single command)
- ❌ NOT Essential Commands: Deploy (5+ steps with validation) → Continue to Step 5

---

### Step 5: Would this exceed CLAUDE.md line budget?

```
Would adding this workflow exceed 600-line CLAUDE.md limit?
├─ YES → Skill
└─ NO → Continue to Step 6
```

**Calculation:**
- Current CLAUDE.md: 550 lines
- Workflow to add: 80 lines
- Total: 630 lines → EXCEEDS 600-line limit → **Use Skill**

---

### Step 6: Is this recurring (every sprint) or rare (once per quarter)?

```
How often is this task performed?
├─ RECURRING (weekly/monthly) → CLAUDE.md Core Workflows
└─ RARE (quarterly/yearly) → Skill
```

**Examples:**
- ✅ CLAUDE.md: "Promote stub to workorder" (done weekly) → CLAUDE.md
- ✅ Skill: "Migrate database schema" (done once per major version) → Skill
- ✅ Skill: "Deploy to production" (done monthly) → Skill (risky, needs confirmation)

---

### Step 7: Is this documentation or executable workflow?

```
Is this reference material (read-only) or actionable steps (execute)?
├─ REFERENCE MATERIAL → Separate doc (ARCHITECTURE.md, API.md, etc.)
└─ ACTIONABLE STEPS → Skill
```

**Examples:**
- ✅ Separate doc: "API endpoint catalog" → `API.md`
- ✅ Separate doc: "Component library reference" → `COMPONENTS.md`
- ✅ Skill: "Generate API docs from code" → Skill

---

## Decision Matrix

### When to Use CLAUDE.md

**Use CLAUDE.md for:**

| Use Case | Why CLAUDE.md | Example |
|----------|--------------|---------|
| **Project architecture** | Needed every session for context | "We use React 18 + Next.js 14 App Router" |
| **Core concepts** | Fundamental knowledge | "Stub → Workorder lifecycle" |
| **Integration points** | How systems connect | "Integrates with coderef-context MCP server" |
| **Data flow** | How data moves through system | "User action → Store → API → Database" |
| **Design decisions** | Why we chose X over Y | "Chose Zustand over Redux for simplicity" |
| **Common workflows** | Frequent operations (weekly+) | "Create stub", "Handoff to agent" |
| **File structure** | Where things live | Directory tree with annotations |
| **Tool references** | Pointers to tools | "Use mcp__coderef-context__coderef_scan for analysis" |

**Line budget:** 530-600 lines

---

### When to Use Skills

**Use skills for:**

| Use Case | Why Skill | Example |
|----------|-----------|---------|
| **Deployment** | Rare, risky, multi-step | `/deploy-production` |
| **Database migration** | One-time, requires confirmation | `/migrate-db-v2-to-v3` |
| **Codebase analysis** | Tool-intensive, rare | `/scan-codebase` |
| **Documentation generation** | One-off task | `/generate-api-docs` |
| **Refactoring** | Specific, infrequent | `/refactor-auth-system` |
| **Setup tasks** | One-time per environment | `/setup-dev-environment` |
| **Audit tasks** | Periodic review | `/audit-security` |
| **Bulk operations** | Rare, risky | `/rename-all-files` |

**Line budget:** 300-500 lines

---

### When to Use Linter Configs

**Use linter configs for:**

| Use Case | Why Linter | File |
|----------|-----------|------|
| **Code style** | Mechanically checkable | `.eslintrc.json`, `.prettierrc` |
| **Formatting** | Deterministic rules | `.editorconfig` |
| **Import sorting** | Can be auto-fixed | `.eslintrc.json` (import rules) |
| **Naming conventions** | Pattern matching | `.eslintrc.json` (naming rules) |
| **File structure rules** | Deterministic | `.eslintrc.json` (file naming) |

**Never document linter rules in CLAUDE.md or skills** - just reference the config file

---

### When to Use Separate Docs

**Use separate docs for:**

| Use Case | Why Separate | File |
|----------|-------------|------|
| **API reference** | Too detailed for CLAUDE.md | `API.md` |
| **Component catalog** | Too detailed for CLAUDE.md | `COMPONENTS.md` |
| **Architecture diagrams** | Visual, reference material | `ARCHITECTURE.md` |
| **User guide** | End-user documentation | `USER-GUIDE.md` |
| **Changelog** | Historical context | `CHANGELOG.md` |
| **Troubleshooting** | Reference material | `TROUBLESHOOTING.md` |

**Progressive disclosure:** Reference in CLAUDE.md, details in separate file

---

## Real-World Examples

### Example 1: Deployment Workflow

**Question:** Should "Deploy to production" be in CLAUDE.md or skill?

**Analysis:**
1. ❌ Not deterministic → Continue
2. ❌ Not needed every session → Continue
3. ❌ Instructions, not knowledge → Continue
4. ❌ Multi-step workflow (10+ steps) → Continue
5. ✅ Would add 100+ lines to CLAUDE.md → **Skill**

**Decision:** `/deploy-production` skill

**CLAUDE.md reference:**
```markdown
## Essential Commands

### Deployment
See `/deploy-production` skill for production deployment workflow.
```

---

### Example 2: Project Architecture

**Question:** Should "React 18 + Next.js 14 architecture" be in CLAUDE.md or skill?

**Analysis:**
1. ❌ Not deterministic (requires LLM understanding) → Continue
2. ✅ Needed every session (AI needs context for all code changes) → **CLAUDE.md**

**Decision:** CLAUDE.md Architecture section

**Example:**
```markdown
## Architecture

### Core Concepts

**1. React 18 + Next.js 14 App Router**
Server Components for data fetching, Client Components for interactivity.

**2. State Management**
Zustand for global state, React Query for server state.
```

---

### Example 3: Code Style Rules

**Question:** Should "Use 2 spaces for indentation" be in CLAUDE.md or skill?

**Analysis:**
1. ✅ Deterministic (can be checked mechanically) → **Linter config**

**Decision:** `.prettierrc` config file

**`.prettierrc`:**
```json
{
  "tabWidth": 2,
  "useTabs": false
}
```

**CLAUDE.md reference:**
```markdown
## Code Quality

**Formatting:** Run `npm run format` to auto-fix. Config: `.prettierrc`
```

---

### Example 4: API Endpoint Catalog

**Question:** Should "List of all 50 API endpoints" be in CLAUDE.md or skill?

**Analysis:**
1. ❌ Not deterministic → Continue
2. ❌ Not needed every session (reference material) → Continue
3. ✅ Knowledge, but too detailed for CLAUDE.md → **Separate doc**

**Decision:** `API.md` separate file

**CLAUDE.md reference:**
```markdown
## Progressive Disclosure Guide

**API reference:** See [API.md](API.md) for complete endpoint catalog
```

---

### Example 5: Stub Creation Workflow

**Question:** Should "Create new stub" be in CLAUDE.md or skill?

**Analysis:**
1. ❌ Not deterministic → Continue
2. ✅ Needed frequently (every new idea) → CLAUDE.md
3. ❌ Instructions, but → Check frequency
4. ✅ Recurring (weekly) → **CLAUDE.md**

**Decision:** CLAUDE.md Core Workflows section

**Example:**
```markdown
## Core Workflows

### Stub Creation Workflow

When user has a new idea:
1. Create folder: `coderef/working/{feature-name}/`
2. Assign next STUB-XXX from projects.md
3. Create stub.json with metadata
[... 10 more lines of steps ...]
```

---

## Complex Cases

### Case 1: "Should I create a skill for running tests?"

**Analysis:**
- Tests run frequently (daily)
- Single command: `npm test`
- Not risky (no side effects)

**Decision:** CLAUDE.md Essential Commands (not a skill)

```markdown
## Essential Commands

### Testing
```bash
npm test                  # Run all tests
npm run test:watch        # Run tests in watch mode
npm run test:coverage     # Run tests with coverage
```
```

---

### Case 2: "Should I create a skill for generating documentation?"

**Analysis:**
- Documentation generation is infrequent (monthly)
- Multi-step workflow (scan code, generate docs, validate)
- Requires tool sequencing (coderef_scan → generate_docs → validate)
- Adds 60+ lines

**Decision:** Skill

```markdown
---
name: generate-docs
description: Generate foundation docs (README, ARCHITECTURE, API) from codebase
allowed-tools:
  - mcp__coderef-context__coderef_scan
  - mcp__coderef-docs__generate_foundation_docs
  - mcp__papertrail__validate_document
---
```

---

### Case 3: "Should I document our naming conventions in CLAUDE.md?"

**Analysis:**
- Naming conventions are deterministic (pattern matching)
- Can be enforced by ESLint

**Decision:** Linter config (not CLAUDE.md, not skill)

**`.eslintrc.json`:**
```json
{
  "rules": {
    "@typescript-eslint/naming-convention": [
      "error",
      {
        "selector": "variable",
        "format": ["camelCase"]
      },
      {
        "selector": "typeLike",
        "format": ["PascalCase"]
      }
    ]
  }
}
```

**CLAUDE.md reference:**
```markdown
## Code Quality

**Naming conventions:** Enforced by ESLint. Config: `.eslintrc.json`
```

---

### Case 4: "Should I create a skill for each deployment environment?"

**Options:**
1. One skill per environment: `/deploy-staging`, `/deploy-production`, `/deploy-qa`
2. One skill with parameter: `/deploy [environment]`
3. CLAUDE.md workflow with environment parameter

**Analysis:**
- Each environment has different steps (staging runs E2E tests, production requires approval)
- Each deployment is risky and infrequent

**Decision:** One skill per environment (clearer, safer)

**Skills:**
- `.claude/skills/deploy-staging.md`
- `.claude/skills/deploy-production.md`
- `.claude/skills/deploy-qa.md`

**CLAUDE.md reference:**
```markdown
## Deployment

**Staging:** `/deploy-staging` - Deploy to staging with E2E tests
**Production:** `/deploy-production` - Deploy to production (requires approval)
**QA:** `/deploy-qa` - Deploy to QA environment
```

---

## Checklist: "Should I Create a Skill?"

Use this checklist to decide:

### ✅ Create a Skill If:
- [ ] Task is performed rarely (monthly or less)
- [ ] Task has 5+ sequential steps
- [ ] Task requires tool sequencing (call A, then B based on A's result)
- [ ] Task is risky (deployment, database migration, bulk deletion)
- [ ] Task requires user confirmation before proceeding
- [ ] Task would add 60+ lines to CLAUDE.md
- [ ] Task is one-time (setup, migration)

### ❌ Don't Create a Skill If:
- [ ] Task is a single command
- [ ] Task is performed frequently (daily/weekly)
- [ ] Task is general knowledge (how system works)
- [ ] Task is deterministic (use linter config)
- [ ] Task is reference material (use separate doc)
- [ ] Information is needed in every session

---

## Anti-Patterns

### Anti-Pattern 1: Skill for General Knowledge

**❌ Wrong:**
```markdown
---
name: understand-architecture
description: Explain project architecture
---

# Understand Architecture

Our project uses React 18 with Next.js 14...
[300 lines of architecture explanation]
```

**✅ Right:**
Put in CLAUDE.md Architecture section (needed in every session)

---

### Anti-Pattern 2: CLAUDE.md for One-Time Task

**❌ Wrong (in CLAUDE.md):**
```markdown
## Core Workflows

### Migrate Database from v2 to v3

[100 lines of migration steps]
```

**✅ Right:**
Create `/migrate-db-v2-to-v3` skill (one-time task, risky)

---

### Anti-Pattern 3: Skill for Single Command

**❌ Wrong:**
```markdown
---
name: run-tests
description: Run test suite
---

# Run Tests

```bash
npm test
```
```

**✅ Right:**
Put in CLAUDE.md Essential Commands (single command, frequent)

---

### Anti-Pattern 4: CLAUDE.md for Linter Rules

**❌ Wrong (in CLAUDE.md):**
```markdown
## Code Style

- Use 2 spaces for indentation
- Semicolons required at end of statements
- Single quotes for strings
- Trailing commas in multi-line objects
[50 more linting rules]
```

**✅ Right:**
Use `.eslintrc.json` and `.prettierrc` (deterministic rules)

---

## Summary Table

| Characteristic | CLAUDE.md | Skill | Linter | Separate Doc |
|----------------|-----------|-------|--------|--------------|
| **Frequency** | Every session | Rare (monthly-) | N/A | Reference |
| **Type** | Knowledge | Instructions | Rules | Knowledge |
| **Scope** | General | Specific | Mechanical | Detailed |
| **Line budget** | 530-600 | 300-500 | N/A | Unlimited |
| **Invocation** | Automatic | User-triggered | Automatic | As needed |
| **Examples** | Architecture, integrations | Deployment, migration | Code style | API catalog |

---

## Version History

### v1.0.0 (2026-01-22)
- Initial release
- Defined 7-step decision flow
- Provided decision matrix for each documentation type
- Documented real-world examples and complex cases
- Created anti-pattern guide

**Workorder:** WO-CLAUDE-MD-STANDARDS-001
**Session:** claude-md-standards
**Author:** CodeRef Assistant (Orchestrator Persona)

---

**Related Standards:**
- **CLAUDE-MD-STANDARDS.md** - Project-level CLAUDE.md standards
- **CHILD-CLAUDE-MD-GUIDE.md** - Sub-package CLAUDE.md standards
- **SKILL-TEMPLATE.md** - Skill.md template and standards
