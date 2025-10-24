# MCP Agent Knowledge Structure Template

**Version:** 1.0.0
**Purpose:** Reusable template for organizing agent-specific knowledge using modular, granular files

---

## Overview

This template provides a standardized structure for storing specialized knowledge that MCP agents (like coderef-expert, docs-expert, etc.) can access via the `Read` tool.

**Benefits:**
- ✅ Modular: Update individual knowledge modules without touching agent files
- ✅ Granular: Agents load only what they need (faster, more efficient)
- ✅ Maintainable: Clear organization, easy to find and update
- ✅ Reusable: Same pattern across all MCP agents

---

## Directory Structure

```
{mcp-server-name}/knowledge/
├── system/
│   ├── overview.md              # High-level architecture
│   ├── locations.md             # File paths, directory structure
│   └── getting-started.md       # How to use the system
├── {domain-1}/
│   ├── component-1.md           # Specific component details
│   ├── component-2.md
│   └── component-3.md
├── {domain-2}/
│   ├── component-a.md
│   └── component-b.md
└── workflows/
    ├── workflow-1.md            # Common task workflows
    ├── workflow-2.md
    └── integration.md           # Integration patterns
```

---

## File Structure Standards

### Module File Format

Each knowledge module should follow this structure:

```markdown
# {Component Name}

**File:** {path/to/source-file.ts}
**Lines:** {line-count}
**Purpose:** {one-sentence description}

---

## Overview

{2-3 sentence high-level description}

## Key Concepts

{Important concepts, patterns, algorithms}

## API / Interface

{Functions, classes, methods - what they do}

## Examples

{Code examples, usage patterns}

## Common Operations

{How to use this component for typical tasks}

## Related Components

- {Link to related module 1}
- {Link to related module 2}
```

### System Overview Template

```markdown
# System Overview

**Project:** {project-name}
**Version:** {version}
**Last Updated:** {date}

## Architecture

{High-level architecture diagram or description}

## Key Components

1. **{Component 1}** - {Description}
2. **{Component 2}** - {Description}
3. **{Component 3}** - {Description}

## Technology Stack

- **Language:** {TypeScript, Python, etc.}
- **Framework:** {Express, FastAPI, etc.}
- **Key Libraries:** {List}

## Directory Structure

{Annotated directory tree}
```

### Locations Template

```markdown
# System Locations

## Primary Locations

- **Main Codebase:** {absolute-path}
- **MCP Server:** {absolute-path}
- **Documentation:** {absolute-path}

## Key Directories

- **Source:** {path}
- **Tests:** {path}
- **Config:** {path}
- **Build:** {path}

## Important Files

- **{file-1}:** {path} - {purpose}
- **{file-2}:** {path} - {purpose}
```

---

## Agent Integration Pattern

### Claude Code Agent File

Create: `.claude/agents/{agent-name}.md`

```markdown
---
name: {agent-name}
description: Expert in {system-name}
tools: Read, Write, Bash, Grep, Glob
model: sonnet
---

You are an expert in {system-name}.

## System Context

**Locations:**
- Main: {path}
- MCP: {path}

## Knowledge Base

On activation, always read:
- Read {path}/knowledge/system/overview.md
- Read {path}/knowledge/system/locations.md

For specific tasks, read relevant modules:
- {Domain 1} tasks → Read {path}/knowledge/{domain-1}/*.md
- {Domain 2} tasks → Read {path}/knowledge/{domain-2}/*.md
- Workflows → Read {path}/knowledge/workflows/*.md

## Guidelines

{Agent-specific behavior, style, approach}
```

---

## Example: CodeRef System

### Directory Structure
```
coderef-mcp/knowledge/
├── system/
│   ├── overview.md
│   ├── locations.md
│   ├── getting-started.md
│   └── roadmap.md
├── typescript/
│   ├── scanner.md
│   ├── parser.md
│   ├── drift-detector.md
│   ├── indexer.md
│   └── validator.md
├── python/
│   ├── mcp-server.md
│   ├── tool-handlers.md
│   └── bridge-pattern.md
└── workflows/
    ├── scanning.md
    ├── drift-detection.md
    └── integration.md
```

### Agent Activation Flow

```
User: /coderef-expert
  ↓
Agent loads: .claude/agents/coderef-expert.md
  ↓
Agent reads:
  - knowledge/system/overview.md      # Context
  - knowledge/system/locations.md     # Paths
  ↓
User: "Help me with scanning"
  ↓
Agent reads:
  - knowledge/typescript/scanner.md   # Specific knowledge
  ↓
Agent: "Ready! I know scanner.ts details."
```

---

## Best Practices

### 1. Granularity
- ✅ One component per file
- ✅ Each file 100-300 lines max
- ❌ Don't create massive monolithic files

### 2. Naming
- ✅ Use kebab-case: `drift-detector.md`
- ✅ Descriptive: `typescript-scanner.md` not `scanner.md` (if ambiguous)
- ❌ Avoid abbreviations

### 3. Cross-References
- ✅ Link to related modules: "See also: [Parser](parser.md)"
- ✅ Explicit paths: "Read knowledge/workflows/integration.md"

### 4. Maintenance
- ✅ Update knowledge when code changes
- ✅ Version tag at top: `Last Updated: 2025-01-15`
- ✅ Link to source: `File: packages/core/scanner.ts`

### 5. Agent Instructions
- ✅ Tell agent WHEN to read each module
- ✅ Distinguish "always read" vs "on-demand"
- ✅ Clear task → module mapping

---

## Creating Knowledge for New Agent

### Step 1: Identify Domains
What are the major areas of knowledge?
- Example: TypeScript packages, Python server, Workflows

### Step 2: List Components
Within each domain, what are the key components?
- Example: scanner, parser, drift-detector, indexer

### Step 3: Create Structure
```bash
mkdir -p {mcp-server}/knowledge/{domain-1}
mkdir -p {mcp-server}/knowledge/{domain-2}
mkdir -p {mcp-server}/knowledge/system
mkdir -p {mcp-server}/knowledge/workflows
```

### Step 4: Extract Knowledge
For each component:
1. Read source code
2. Extract: purpose, API, examples, usage
3. Create module file using template

### Step 5: Create Agent
1. Create `.claude/agents/{agent-name}.md`
2. Point to knowledge base
3. Define activation behavior

### Step 6: Test
1. Activate agent
2. Verify it reads correct modules
3. Ask task-specific questions
4. Confirm agent has right knowledge

---

## Template Usage Checklist

- [ ] Create `{mcp-server}/knowledge/` directory
- [ ] Create `system/` subdirectory with overview.md, locations.md
- [ ] Create domain subdirectories (e.g., `typescript/`, `python/`)
- [ ] Create `workflows/` subdirectory
- [ ] Extract knowledge from source code into modules
- [ ] Create `.claude/agents/{agent-name}.md`
- [ ] Configure agent to read knowledge on activation
- [ ] Test agent activation and knowledge access
- [ ] Document custom patterns (if any)

---

## Examples in the Wild

### 1. coderef-expert
- **Knowledge Base:** `coderef-mcp/knowledge/`
- **Domains:** typescript/, python/, workflows/
- **Agent:** `.claude/agents/coderef-expert.md`

### 2. docs-expert
- **Knowledge Base:** `docs-mcp/knowledge/`
- **Domains:** tools/, workflows/, standards/
- **Agent:** `.claude/agents/docs-expert.md`

### 3. {your-agent}
- **Knowledge Base:** `{mcp-server}/knowledge/`
- **Domains:** {domain-1}/, {domain-2}/
- **Agent:** `.claude/agents/{agent-name}.md`

---

## Support

**Issues?** Review this template and adjust structure as needed for your specific use case.

**Questions?** Common patterns:
- Large system → More granular domains
- Small system → Fewer, broader modules
- Complex integrations → Dedicated workflows/ directory

---

**Last Updated:** 2025-01-15
**Version:** 1.0.0
**Maintained by:** MCP Agent Knowledge Architecture Working Group
