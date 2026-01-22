# Child CLAUDE.md Guide (v1.0.0)

**Purpose:** Standards for sub-package/module CLAUDE.md files in monorepos and multi-component projects
**Applies to:** Component libraries, dashboard packages, plugin systems, microservices in same repo
**Created:** 2026-01-22
**Workorder:** WO-CLAUDE-MD-STANDARDS-001

---

## Executive Summary

**Child CLAUDE.md** files provide focused context for sub-packages or modules within a larger project. They assume a parent CLAUDE.md exists and focus on component-specific details.

**Core Principles:**
1. **Leaner than parent** - 300-400 lines (vs 530-600 for parent)
2. **Reference parent for shared concepts** - Don't repeat ecosystem architecture
3. **Focus on component specifics** - What makes THIS component unique
4. **Progressive disclosure to parent** - Point to parent CLAUDE.md for project-wide context

**Based on:**
- CLAUDE-MD-STANDARDS.md v1.0.0 (project-level standards)
- Analysis of monorepo patterns (Next.js, Turborepo, NX)
- CodeRef Dashboard example (packages/dashboard/CLAUDE.md)

---

## 1. When to Use Child CLAUDE.md

### Use Cases

**✅ Create child CLAUDE.md when:**
- Monorepo with multiple publishable packages (e.g., `packages/ui`, `packages/api`)
- Component library with distinct subsystems (e.g., `src/components/coderef/`)
- Plugin system where each plugin has separate context (e.g., `plugins/auth/`)
- Microservices in same repo (e.g., `services/billing/`)

**❌ Don't create child CLAUDE.md when:**
- Single-package project (use parent CLAUDE.md only)
- Sub-directories that are tightly coupled to parent (use parent CLAUDE.md File Structure section)
- Test directories (not code context, covered by parent)
- Build/config directories (not code context)

### Decision Tree

```
Is this a separate publishable package?
├─ YES → Child CLAUDE.md
└─ NO → Is this a distinct subsystem with separate concerns?
    ├─ YES → Child CLAUDE.md (if >500 lines of unique context)
    └─ NO → Document in parent CLAUDE.md File Structure section
```

---

## 2. Line Budget Standards

### Target Range
- **Minimum:** 250 lines (very focused components)
- **Target:** 300-400 lines (ideal range)
- **Maximum:** 450 lines (hard limit)

### Why Shorter Than Parent?

**Parent CLAUDE.md (530-600 lines) covers:**
- Ecosystem architecture
- Cross-project integrations
- Shared design decisions
- Project-wide workflows

**Child CLAUDE.md (300-400 lines) covers:**
- Component-specific architecture
- Component-specific workflows
- Component-to-parent integration
- Component-specific tools

**Overlap eliminated:** No need to repeat ecosystem context that's in parent

---

## 3. Required Sections (Child)

Child CLAUDE.md has a streamlined section structure compared to parent.

### 3.1 Core Sections (Mandatory)

| Section | Purpose | Max Lines | vs Parent |
|---------|---------|-----------|-----------|
| **Quick Summary** | Component overview + parent reference | 20 | Shorter (parent has 30) |
| **Parent Context** | Pointer to parent CLAUDE.md | 10 | NEW (child-only) |
| **Component Purpose** | Why this component exists | 30 | Replaces "Problem & Vision" |
| **Architecture** | Component-specific concepts | 60 | Shorter (parent has 80) |
| **Workflows Catalog** | Component workflows only | 20 | Shorter (parent has 30) |
| **Core Workflows** | 2-3 key workflows | 80 | Shorter (parent has 120) |
| **File Structure** | Component files only | 30 | Shorter (parent has 40) |
| **Integration with Parent** | How this fits into parent | 40 | NEW (child-only) |
| **Essential Commands** | Component-specific commands | 20 | Shorter (parent has 30) |

**Total Core:** ~310 lines

### 3.2 Enhanced Sections (Optional for Children)

| Section | Purpose | Max Lines | When to Include |
|---------|---------|-----------|-----------------|
| **Progressive Disclosure Guide** | Where to find detailed info | 15 | If component has sub-docs |
| **Tool Sequencing Patterns** | Component-specific sequences | 20 | If component has unique tools |

**Total Enhanced:** ~35 lines (use if staying under 400-line budget)

### 3.3 Sections to SKIP (Use Parent Instead)

**❌ Don't duplicate in child:**
- Problem & Vision (use "Component Purpose" instead)
- Design Decisions (unless component-specific decisions exist)
- Integration Guide (use "Integration with Parent" instead)
- Next Steps / Roadmap (parent handles project roadmap)
- Recent Changes (parent handles version history)

---

## 4. Parent Context Section (NEW)

### Purpose

Immediately point AI to parent CLAUDE.md for ecosystem context.

### Template

```markdown
## Parent Context

**Parent Project:** [Project Name]
**Parent CLAUDE.md:** [Relative path to parent, e.g., `../../CLAUDE.md`]

**Read parent CLAUDE.md for:**
- Ecosystem architecture and integration points
- Project-wide workflows (workorder handoff, stub creation, etc.)
- Shared design decisions
- MCP server integrations (coderef-context, coderef-workflow, etc.)

**This document covers:** Component-specific architecture, workflows, and integration points unique to [component name].
```

### Example (coderef-dashboard child)

```markdown
## Parent Context

**Parent Project:** CodeRef Dashboard
**Parent CLAUDE.md:** `../../CLAUDE.md`

**Read parent CLAUDE.md for:**
- Dashboard architecture overview
- Board, Stub, Workorder data models
- Integration with MCP servers (coderef-context, papertrail, etc.)
- Project-wide workflows

**This document covers:** Universal Context Menu System implementation, EntityContextMenu component, TargetAdapter pattern, and multi-target converters.
```

---

## 5. Component Purpose Section

### Purpose

Replace parent's "Problem & Vision" with component-specific "why this exists."

### Template

```markdown
## Component Purpose

### The Problem (Component-Specific)

[1-2 sentences: What problem does THIS component solve within the parent project?]

### The Solution

[2-3 sentences: How does this component solve it? What's the core innovation?]

### How It Fits

[1-2 sentences: Where does this fit in the parent architecture?]
```

### Example (Universal Context Menu System)

```markdown
## Component Purpose

### The Problem

Adding files/stubs/workorders to boards required 3 separate implementations (AddFileToBoardMenu, BoardContextMenu, inline handlers). Each new target type (prompts, notes, sessions) required duplicating the entire context menu system.

### The Solution

Universal context menu system with pluggable TargetAdapters. EntityContextMenu<TEntity, TTarget> is target-agnostic, and converters handle entity-to-target transformations. Add new targets by creating a TargetAdapter, not rewriting UI code.

### How It Fits

Replaces all board context menu implementations in the dashboard. Designed for future expansion to prompts, notes, sessions, and favorites when those features are implemented.
```

---

## 6. Integration with Parent Section (NEW)

### Purpose

Document how this component connects to parent project systems.

### Template

```markdown
## Integration with Parent

### Data Flow

[How does data flow between this component and parent systems?]

### Dependencies on Parent

| Parent System | What This Component Uses | Why |
|---------------|-------------------------|-----|
| [System 1] | [API/Hook/Store] | [Purpose] |
| [System 2] | [API/Hook/Store] | [Purpose] |

### Parent Dependencies on This

| This Component Exports | Used By Parent For | Status |
|------------------------|-------------------|--------|
| [Export 1] | [Purpose] | ✅ Stable |
| [Export 2] | [Purpose] | 🚧 Experimental |

### Integration Patterns

[1-2 examples of how parent code calls this component]
```

### Example (Universal Context Menu System)

```markdown
## Integration with Parent

### Data Flow

```
User right-clicks StubCard/WorkorderCard
  ↓
EntityContextMenu renders with entity + available targets
  ↓
User selects target (e.g., "Add as New Board")
  ↓
TargetAdapter.addToTarget() called
  ↓
Parent's useBoards hook updates board state
  ↓
UI re-renders with new board/list/card
```

### Dependencies on Parent

| Parent System | What This Component Uses | Why |
|---------------|-------------------------|-----|
| useBoards hook | Board state management | Reading boards, creating boards/lists/cards |
| useBoardHierarchy hook | List/card fetching | Lazy-loading lists and cards for context menu |
| Board types | Type definitions | Type-safe adapters and converters |

### Parent Dependencies on This

| This Component Exports | Used By Parent For | Status |
|------------------------|-------------------|--------|
| EntityContextMenu | Right-click menus in StubCard, WorkorderCard | ✅ Stable |
| BoardTargetAdapter | Board CRUD operations | ✅ Stable |
| Entity converters | File/Stub/Workorder transformations | ✅ Stable |
| TargetAdapter interface | Future target types (prompts, notes) | 🚧 Ready for extension |
```

---

## 7. File Structure Section (Component-Scoped)

### Scope

Show ONLY component files, not entire parent project.

### Template

```markdown
## File Structure

```
component-name/
├── CLAUDE.md                        # This file - component AI context
├── README.md                        # Component user docs
├── src/
│   ├── ComponentName.tsx            # Main component
│   ├── types.ts                     # Component-specific types
│   └── lib/
│       ├── adapters.ts              # Adapter implementations
│       └── converters.ts            # Converter implementations
└── __tests__/
    └── ComponentName.test.tsx       # Component tests
```

**Parent project structure:** See `../../CLAUDE.md` File Structure section
```

### Anti-Pattern (Showing Full Parent Tree)

**❌ Don't do this:**
```markdown
## File Structure

```
project/
├── packages/
│   ├── dashboard/                   # THIS COMPONENT
│   │   ├── src/
│   │   │   └── components/
│   │   │       └── coderef/
│   │   │           └── EntityContextMenu.tsx
│   ├── api/                         # NOT RELEVANT TO THIS COMPONENT
│   ├── ui/                          # NOT RELEVANT TO THIS COMPONENT
├── apps/
│   └── web/                         # NOT RELEVANT TO THIS COMPONENT
```
```

**✅ Do this instead:**
```markdown
## File Structure

```
packages/dashboard/src/components/coderef/
├── EntityContextMenu.tsx            # Universal context menu component
├── AddFileToBoardMenu.tsx          # Backward-compatible wrapper
├── ContextMenu.tsx                  # Base context menu primitive
└── types/
    └── file-board-integration.ts    # Type definitions
```

**Full parent structure:** See `../../CLAUDE.md` File Structure section
```

---

## 8. Essential Commands Section (Component-Specific)

### Scope

Show ONLY commands specific to this component, not parent-wide commands.

### Template

```markdown
## Essential Commands

### Development (Component)
```bash
# Run component tests
npm test -- ComponentName

# Run component in isolation (if applicable)
npm run dev:component

# Type check component
npx tsc --noEmit src/components/component-name/**/*.ts
```

### Parent Commands
See `../../CLAUDE.md` Essential Commands for project-wide commands (build, lint, deploy, etc.)
```

### Example (Universal Context Menu System)

```markdown
## Essential Commands

### Development (Context Menu System)
```bash
# Run entity converter tests
npm test -- entity-converters.test.ts

# Run adapter tests
npm test -- target-adapters.test.ts

# Type check context menu components
npx tsc --noEmit src/components/coderef/**/*.tsx
```

### Parent Commands
See `../../CLAUDE.md` Essential Commands for:
- Full dashboard build (`npm run build`)
- Dashboard dev server (`npm run dev`)
- End-to-end tests (`npm run test:e2e`)
```

---

## 9. Validation Checklist (Child)

Use this checklist before committing changes to child CLAUDE.md:

### Line Budget
- [ ] Total lines ≤ 450 (run `wc -l CLAUDE.md`)
- [ ] Target range: 300-400 lines
- [ ] If >450 lines, extract to component-specific docs

### Required Sections
- [ ] Quick Summary (component overview + parent reference)
- [ ] Parent Context (pointer to parent CLAUDE.md)
- [ ] Component Purpose (problem, solution, how it fits)
- [ ] Architecture (component-specific concepts)
- [ ] Workflows Catalog (component workflows only)
- [ ] Core Workflows (2-3 key workflows)
- [ ] File Structure (component files only)
- [ ] Integration with Parent (data flow, dependencies)
- [ ] Essential Commands (component-specific commands)

### Content Quality
- [ ] Parent CLAUDE.md referenced in Quick Summary
- [ ] No duplication of parent content (ecosystem architecture, shared decisions)
- [ ] Integration with Parent section documents data flow
- [ ] File Structure scoped to component only (not full parent tree)
- [ ] Essential Commands scoped to component (references parent for project commands)

### Progressive Disclosure
- [ ] Points to parent CLAUDE.md for ecosystem context
- [ ] Points to component-specific docs (if exist)
- [ ] No code style rules (delegated to parent linter configs)

---

## 10. Examples

### Example 1: Monorepo Package (Good)

**Location:** `packages/ui/CLAUDE.md`

```markdown
# UI Component Library - AI Context

**Package:** @coderef/ui
**Parent:** CodeRef Dashboard
**Version:** 1.0.0

## Quick Summary

Reusable UI component library for CodeRef Dashboard. Provides buttons, inputs, modals, and layout primitives built on Tailwind CSS and Radix UI.

**Parent CLAUDE.md:** `../../CLAUDE.md`

## Parent Context

**Read parent for:** Dashboard architecture, theming system, accessibility standards

**This document covers:** Component API, usage patterns, and testing guidelines

## Component Purpose

### The Problem
Dashboard had 15+ ad-hoc button implementations with inconsistent styling, accessibility, and behavior.

### The Solution
Unified component library with strict API contracts, built-in accessibility, and comprehensive Storybook documentation.

### How It Fits
Consumed by dashboard app (`apps/web`) and potentially future CodeRef projects.

## Architecture

### Core Concepts

**1. Composition over Configuration**
Components accept minimal props and compose via React children.

**2. Radix UI Primitives**
All interactive components built on Radix UI for accessibility.

**3. Tailwind Variants**
Styling via `cva` (class-variance-authority) for type-safe variants.

[... remaining sections ...]
```

**Line count:** 320 lines
**Assessment:** ✅ Perfect - references parent, focused on component specifics, within budget

---

### Example 2: Plugin System (Good)

**Location:** `plugins/auth/CLAUDE.md`

```markdown
# Authentication Plugin - AI Context

**Plugin:** auth
**Parent:** Multi-Tenant SaaS Platform
**Version:** 2.1.0

## Quick Summary

Authentication plugin providing OAuth2, JWT, and session management for multi-tenant platform.

**Parent CLAUDE.md:** `../../CLAUDE.md`

## Parent Context

**Read parent for:** Plugin system architecture, tenant isolation model, database schema

**This document covers:** Auth flows, token management, and security policies

## Component Purpose

### The Problem
Platform needed tenant-aware authentication with support for OAuth2 providers (Google, GitHub, Microsoft) and custom JWT issuance.

### The Solution
Plugin-based auth system that integrates with parent's tenant context. Supports multiple auth strategies per tenant.

### How It Fits
Registered as plugin in parent's plugin registry. Invoked via `context.auth.*` API in request handlers.

[... remaining sections ...]
```

**Line count:** 340 lines
**Assessment:** ✅ Good - clear integration points, focused scope

---

### Example 3: Microservice in Monorepo (Avoid)

**Location:** `services/billing/CLAUDE.md`

**❌ Anti-pattern:**
```markdown
# Billing Service - AI Context

## Quick Summary
Billing service handles subscription management, payments, and invoicing for the platform.

## Problem & Vision

### The Problem
[300 lines describing entire platform billing architecture, payment provider integrations, compliance requirements...]

## Architecture

### Ecosystem Overview
[200 lines duplicating parent CLAUDE.md's architecture section...]
```

**Line count:** 780 lines
**Issues:**
- Exceeds 450-line child limit
- Duplicates parent content (ecosystem overview)
- Missing Parent Context section
- Should extract detailed compliance docs to separate files

**✅ Fix:**
1. Add Parent Context section pointing to `../../CLAUDE.md`
2. Replace "Problem & Vision" with "Component Purpose" (30 lines)
3. Remove ecosystem overview duplication
4. Extract compliance docs to `docs/compliance.md`
5. **Result:** 350 lines, focused on billing-specific context

---

## 11. Child vs Parent Comparison Table

| Aspect | Parent CLAUDE.md | Child CLAUDE.md |
|--------|-----------------|-----------------|
| **Line Budget** | 530-600 lines | 300-400 lines |
| **Scope** | Entire project | Single component |
| **Audience** | Anyone working on project | Anyone working on component |
| **Quick Summary** | Project overview | Component overview + parent reference |
| **Architecture** | Ecosystem architecture | Component-specific architecture |
| **Workflows** | Project-wide workflows | Component-specific workflows |
| **Integration** | External integrations | Integration with parent |
| **Design Decisions** | Project-wide ADRs | Component-specific ADRs (if significant) |
| **Recent Changes** | Project version history | Usually omitted (use parent) |
| **File Structure** | Full project tree | Component files only |
| **Commands** | Project build/test/deploy | Component test/dev commands |
| **Parent Context Section** | N/A (is the parent) | **Required** - points to parent |

---

## 12. Migration Guide

### For Existing Child CLAUDE.md Files

**Step 1: Assess if child is needed**
```bash
# Count unique lines vs parent
diff CLAUDE.md ../../CLAUDE.md | grep "^<" | wc -l

# If <200 unique lines, consider merging into parent File Structure section
```

**Step 2: Add Parent Context Section**
```markdown
## Parent Context

**Parent CLAUDE.md:** `../../CLAUDE.md`

**Read parent for:** [List 3-5 parent sections that apply]
**This document covers:** [Component-specific scope]
```

**Step 3: Remove Duplicated Content**
- Delete ecosystem architecture (if duplicates parent)
- Delete project-wide integration guide (keep component-to-parent only)
- Delete shared design decisions (keep component-specific only)

**Step 4: Replace Sections**
- "Problem & Vision" → "Component Purpose"
- "Integration Guide" → "Integration with Parent"

**Step 5: Scope File Structure**
```markdown
## File Structure

[Component files only]

**Full parent structure:** See `../../CLAUDE.md` File Structure section
```

**Step 6: Validate**
```bash
# Check line count
wc -l CLAUDE.md

# Target: 300-400 lines
# If >450, extract component docs to separate files
```

---

### For New Child CLAUDE.md Files

**Step 1: Use Generator (Phase 6 deliverable)**
```bash
# Generate child CLAUDE.md
mcp__coderef-docs__generate_child_claude_md \
  --component-path /path/to/component \
  --parent-path /path/to/parent/CLAUDE.md \
  --component-type "ui-library" \
  --auto-fill true

# Output: CLAUDE.md (320 lines, child-specific sections, validated)
```

**Step 2: Customize Required Sections**

Fill in component-specific content:
1. Component Purpose - Why does this component exist?
2. Architecture - What are the 2-3 core concepts?
3. Integration with Parent - How does data flow?

**Step 3: Validate Before First Commit**
```bash
mcp__papertrail__validate_claude_md CLAUDE.md --type child

# Target score: 85+ for new child CLAUDE.md
```

**Step 4: Commit**
```bash
git add CLAUDE.md
git commit -m "docs: Add child CLAUDE.md for [component name]

Generated from CHILD-CLAUDE-MD-GUIDE v1.0.0
Score: 88/100

WO-[PROJECT]-COMPONENT-SETUP-001"
```

---

## 13. Common Mistakes

### Mistake 1: Duplicating Parent Content

**❌ Wrong:**
```markdown
## Architecture

### Ecosystem Overview
Assistant is a focused orchestrator CLI that coordinates work across multiple projects...
[200 lines duplicating parent's ecosystem architecture]

### Component Architecture
This component implements the context menu system...
```

**✅ Right:**
```markdown
## Architecture

**Ecosystem context:** See `../../CLAUDE.md` Architecture section for full ecosystem overview.

**This component:** Universal context menu system with pluggable TargetAdapters.

### Core Concepts
[Component-specific concepts only]
```

### Mistake 2: Missing Parent Reference

**❌ Wrong:**
```markdown
## Quick Summary

UI component library for buttons, inputs, and modals.
```

**✅ Right:**
```markdown
## Quick Summary

Reusable UI component library for CodeRef Dashboard.

**Parent CLAUDE.md:** `../../CLAUDE.md` - Read for dashboard architecture, theming, and accessibility standards.
```

### Mistake 3: Including Full Project Tree

**❌ Wrong:**
```markdown
## File Structure

```
project/
├── apps/
│   └── web/
├── packages/
│   ├── ui/              # THIS COMPONENT
│   ├── api/
│   └── database/
```
```

**✅ Right:**
```markdown
## File Structure

```
packages/ui/
├── CLAUDE.md
├── src/
│   ├── Button.tsx
│   └── Input.tsx
```

**Full parent structure:** See `../../CLAUDE.md`
```

### Mistake 4: Over-Explaining Parent Systems

**❌ Wrong:**
```markdown
## Integration with Parent

The parent dashboard uses React 18 with Next.js 14 App Router. It has a complex state management system using Zustand with persistence middleware. The board system is built on...
[300 lines explaining parent internals]
```

**✅ Right:**
```markdown
## Integration with Parent

### Dependencies on Parent

| Parent System | What This Component Uses |
|---------------|-------------------------|
| useBoards hook | Board state management |
| Board types | Type definitions |

**For parent architecture details:** See `../../CLAUDE.md` Architecture section
```

---

## 14. Scoring Methodology (Child)

Child CLAUDE.md uses modified scoring (0-100 scale) with child-specific criteria.

### Score Calculation

**Section Presence (30 points):**
- Core sections (24): 3 pts each × 8 sections (Quick Summary, Parent Context, Component Purpose, Architecture, Workflows, File Structure, Integration with Parent, Essential Commands)
- Enhanced sections (6): 3 pts each × 2 sections (Progressive Disclosure, Tool Sequencing)

**Line Budget Compliance (25 points):**
- 300-400 lines: 25 pts
- 250-300 or 400-450: 20 pts
- 200-250 or 450-500: 15 pts
- <200 or 500-600: 10 pts (too short or bloated)
- 600+: 0 pts (critical bloat)

**Parent Integration (20 points):**
- Parent Context section present (5 pts)
- Parent CLAUDE.md referenced in Quick Summary (5 pts)
- No duplication of parent content (5 pts)
- Integration with Parent section documents data flow (5 pts)

**Content Quality (25 points):**
- Component Purpose explains why component exists (5 pts)
- File Structure scoped to component only (5 pts)
- Essential Commands scoped to component (5 pts)
- Integration points documented (5 pts)
- No code style bloat (5 pts)

### Target Scores

- **85-100:** Excellent (model child CLAUDE.md)
- **75-84:** Good (ready for production)
- **65-74:** Fair (needs refinement)
- **<65:** Poor (significant work required)

---

## 15. Related Standards

This document defines child CLAUDE.md standards. See also:

- **CLAUDE-MD-STANDARDS.md** - Project-level CLAUDE.md standards (parent files)
- **SKILL-TEMPLATE.md** - Standards for skill.md files
- **skills-vs-claude-decision-tree.md** - When to use CLAUDE.md vs skill.md
- **claude-md-schema.json** - JSON Schema for validation (supports `type: "child"`)

---

## Version History

### v1.0.0 (2026-01-22)
- Initial release
- Defined 300-400 line budget (vs 530-600 for parent)
- Established child-specific sections (Parent Context, Component Purpose, Integration with Parent)
- Provided migration guide for existing child files
- Documented scoring methodology (0-100 scale, child-specific criteria)

**Workorder:** WO-CLAUDE-MD-STANDARDS-001
**Session:** claude-md-standards
**Author:** CodeRef Assistant (Orchestrator Persona)

---

**Next Steps:**
1. Review and approve this child CLAUDE.md guide
2. Create SKILL-TEMPLATE.md (Phase 3)
3. Create skills-vs-claude-decision-tree.md (Phase 3)
4. Build JSON schemas with child support (Phase 4)
5. Build validator tools with child detection (Phase 5)
6. Build generator tools for child CLAUDE.md (Phase 6)
