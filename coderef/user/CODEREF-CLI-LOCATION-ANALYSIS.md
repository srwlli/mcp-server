# CodeRef CLI Location Analysis - Should We Move It?

**Document Version:** 1.0.0
**Created:** 2025-12-31
**Question:** Should we move coderef-system CLI from `C:/Users/willh/Desktop/projects/coderef-system` to `C:/Users/willh/.mcp-servers/`?
**Status:** Analysis Complete

---

## Executive Summary

**Short Answer:** **NO - Keep coderef-system CLI where it is.**

**Reasoning:**
1. coderef-system is a **development project** with multiple packages (core, CLI, generators, web, RAG)
2. .mcp-servers is for **deployed MCP servers** (Python wrappers that consume the CLI)
3. Mixing development repos with deployed servers violates separation of concerns
4. Current architecture (CLI wrapping via subprocess) works perfectly

**Recommendation:** Keep current structure but improve documentation of the relationship.

---

## Current Architecture

### What We Have

```
C:/Users/willh/Desktop/projects/coderef-system/    # DEVELOPMENT REPO
├── packages/
│   ├── core/                     # @coderef/core library (TypeScript)
│   ├── cli/                      # @coderef/cli (wraps core, 11 commands)
│   ├── generators/               # Code generation tools
│   ├── web/                      # Web UI
│   └── coderef-rag-mcp/          # RAG integration
├── package.json                  # Monorepo root (pnpm workspaces)
├── .git/                         # Git repository
└── node_modules/                 # Development dependencies

C:/Users/willh/.mcp-servers/                        # MCP DEPLOYMENT
├── coderef-context/              # Python MCP wrapper
│   └── server.py                 # Calls coderef CLI via subprocess
├── coderef-docs/                 # Python MCP wrapper
├── coderef-workflow/             # Python MCP wrapper
├── coderef-personas/             # Python MCP wrapper
└── coderef-testing/              # Python MCP wrapper
```

### How They Interact

```
Claude Agent
    │
    ├─ Calls MCP tool: coderef_scan
    │
    ├─ coderef-context/server.py (Python)
    │   ├─ Builds command: ["node", "C:/Users/.../cli/dist/cli.js", "scan", ...]
    │   └─ Runs subprocess
    │
    ├─ @coderef/cli (Node.js)
    │   ├─ Parses arguments
    │   └─ Calls @coderef/core library
    │
    └─ @coderef/core (TypeScript)
        ├─ AST analysis
        ├─ Dependency graph
        └─ Returns JSON
```

**Key Point:** coderef-context is a **consumer**, not the **source**.

---

## Analysis: Why Keep Separate

### 1. Separation of Concerns

| Directory | Purpose | Contents | Development Activity |
|-----------|---------|----------|---------------------|
| **coderef-system** | Source of truth | TypeScript library + CLI | ✅ Active development |
| **.mcp-servers** | MCP deployment | Python wrappers | ⚠️ Configuration only |

**If we move coderef-system to .mcp-servers:**
- ❌ Mixes development repo with deployment configs
- ❌ .mcp-servers becomes cluttered with node_modules, TypeScript builds
- ❌ Unclear which directory is "the project" vs "the deployment"

### 2. Development Workflow

**Current (Clean):**
```bash
# Work on coderef-system
cd C:/Users/willh/Desktop/projects/coderef-system
pnpm install
pnpm build
pnpm test
git commit -m "Add new feature"

# MCP servers just reference it
export CODEREF_CLI_PATH="C:/Users/willh/Desktop/projects/coderef-system/packages/cli"
python ~/.mcp-servers/coderef-context/server.py
```

**If moved to .mcp-servers (Confusing):**
```bash
# Work on coderef-system... but it's in a weird place?
cd C:/Users/willh/.mcp-servers/coderef-system
pnpm install  # Wait, why is there a TypeScript project in .mcp-servers?
pnpm build
git commit  # This repo doesn't belong here conceptually

# MCP servers reference... themselves?
export CODEREF_CLI_PATH="C:/Users/willh/.mcp-servers/coderef-system/packages/cli"
```

**Problem:** .mcp-servers implies "deployed MCP servers," not "active development projects."

### 3. Git Repository Structure

**Current:**
```
C:/Users/willh/Desktop/projects/coderef-system/.git    # coderef-system repo
C:/Users/willh/.mcp-servers/.git                       # MCP servers repo (all 5 servers)
```

Two independent repos:
- ✅ coderef-system = TypeScript library + CLI (independent evolution)
- ✅ .mcp-servers = Python MCP wrappers (stable wrappers)

**If moved:**
```
C:/Users/willh/.mcp-servers/coderef-system/.git        # Nested repo???
C:/Users/willh/.mcp-servers/.git                       # Parent repo
```

- ❌ Git submodule? (complex, fragile)
- ❌ Separate nested repo? (confusing, "why is there another .git here?")
- ❌ Flatten into parent? (loses coderef-system project independence)

### 4. Package Management

**coderef-system uses:**
- `pnpm` workspaces (monorepo structure)
- `node_modules` (100+ dependencies)
- TypeScript compilation
- Vitest for testing
- ESLint, Prettier

**MCP servers use:**
- Python virtual environments
- `pyproject.toml` / `uv.lock`
- pytest for testing
- No Node.js dependencies

**If mixed:**
- ❌ .mcp-servers would have BOTH Python and Node.js build systems
- ❌ `node_modules` in a directory called ".mcp-servers" (conceptual mismatch)
- ❌ pnpm workspace competing with Python package structure

### 5. Deployment Independence

**Key Insight:** coderef-system CLI could be:
- Installed globally (`npm install -g @coderef/cli`)
- Published to npm registry
- Used by other tools (not just MCP servers)

**Example future uses:**
```bash
# VSCode extension
coderef scan ./src

# CI/CD pipeline
coderef validate --ci

# ChatGPT plugin
coderef context --json

# GitHub Action
coderef impact --element=AuthService
```

**If tied to .mcp-servers:**
- ❌ Implies CLI is "only for MCP servers" (limits future use)
- ❌ Other consumers would reference `.mcp-servers/coderef-system` (weird path)

---

## Analysis: What About Papertrail?

You mentioned papertrail and other MCP servers. Let me check current structure:

**Assumption:** Papertrail is probably a pure MCP server (Python-only, no upstream CLI dependency).

**Difference:**
```
Papertrail (hypothetical)
├── server.py              # Self-contained Python server
└── pyproject.toml         # Python dependencies only

coderef-system
├── packages/core/         # TypeScript library (THE SOURCE)
├── packages/cli/          # CLI wrapper
└── package.json           # Node.js monorepo

coderef-context
├── server.py              # MCP wrapper (CONSUMER of coderef CLI)
└── pyproject.toml
```

**Key Difference:**
- **Papertrail:** Self-contained MCP server → Belongs in .mcp-servers ✅
- **coderef-system:** Development project with CLI → Belongs in projects/ ✅
- **coderef-context:** Thin wrapper → Belongs in .mcp-servers ✅

---

## Recommended Structure

### Keep Current Architecture

```
C:/Users/willh/Desktop/projects/
├── coderef-system/                        # DEVELOPMENT REPO
│   ├── packages/
│   │   ├── core/                          # Source of truth
│   │   ├── cli/                           # CLI tool
│   │   └── ...
│   └── package.json
│
C:/Users/willh/.mcp-servers/               # MCP DEPLOYMENT
├── coderef-context/                       # Python wrapper (subprocess → CLI)
├── coderef-docs/                          # Python wrapper
├── coderef-workflow/                      # Python wrapper
├── coderef-personas/                      # Python wrapper
├── coderef-testing/                       # Python wrapper
├── papertrail/                            # Self-contained MCP server
└── other-mcp-servers/                     # Other pure MCP servers
```

### Configuration (.mcp.json)

```json
{
  "mcpServers": {
    "coderef-context": {
      "command": "python",
      "args": ["C:/Users/willh/.mcp-servers/coderef-context/server.py"],
      "env": {
        "CODEREF_CLI_PATH": "C:/Users/willh/Desktop/projects/coderef-system/packages/cli"
      },
      "description": "MCP wrapper for @coderef/cli (wraps external CLI via subprocess)"
    },
    "papertrail": {
      "command": "python",
      "args": ["C:/Users/willh/.mcp-servers/papertrail/server.py"],
      "description": "Self-contained MCP server (no external dependencies)"
    }
  }
}
```

**Clear distinction:**
- ✅ coderef-context references external CLI (CODEREF_CLI_PATH points outside .mcp-servers)
- ✅ papertrail is self-contained (no external paths needed)

---

## Alternative: Global CLI Install

**Option:** Install coderef CLI globally and remove path dependency

```bash
# Option 1: Publish to npm
cd C:/Users/willh/Desktop/projects/coderef-system/packages/cli
npm publish @coderef/cli

# Install globally
npm install -g @coderef/cli

# Now coderef-context can just use "coderef" command
# No CODEREF_CLI_PATH needed
```

**Pros:**
- ✅ Cleaner .mcp.json (no hardcoded paths)
- ✅ CLI updates independently
- ✅ Other tools can use CLI easily

**Cons:**
- ⚠️ Development workflow requires `npm link` or republishing
- ⚠️ Versioning complexity (MCP server vs CLI version mismatch)

**Recommendation:** Keep local path for now (development phase), publish later (production phase)

---

## Comparison Table

| Aspect | Current Structure | If Moved to .mcp-servers | Global npm Install |
|--------|------------------|-------------------------|-------------------|
| **Separation of Concerns** | ✅ Clean (dev vs deploy) | ❌ Mixed | ✅ Clean |
| **Development Workflow** | ✅ Natural | ❌ Confusing | ⚠️ Requires npm link |
| **Git Structure** | ✅ Independent repos | ❌ Nested or submodule | ✅ Independent |
| **Package Management** | ✅ Clear (pnpm vs Python) | ❌ Mixed node_modules | ✅ Clear |
| **Future Extensibility** | ✅ CLI is standalone | ❌ Tied to .mcp-servers | ✅ CLI is standalone |
| **Deployment** | ⚠️ Path dependency | ❌ Still path dependency | ✅ No paths needed |
| **Version Control** | ✅ Easy | ❌ Complex | ⚠️ Version sync issues |

**Winner:** Current structure (keep separate)

---

## What About Other Use Cases?

### 1. "We want all MCP-related code in one place"

**Response:** coderef-system is not "MCP code" - it's a TypeScript code analysis library that happens to be consumed by an MCP server.

**Analogy:**
```
.mcp-servers/postgres-mcp/     # MCP server for PostgreSQL
└── server.py                  # Calls `psql` command

C:/Program Files/PostgreSQL/   # PostgreSQL itself (NOT in .mcp-servers)
```

We don't move PostgreSQL into .mcp-servers just because an MCP server uses it.

### 2. "We want easier path management"

**Response:** Use environment variables or global install (see Alternative above)

**Current approach is correct:**
```json
"env": {
  "CODEREF_CLI_PATH": "C:/Users/willh/Desktop/projects/coderef-system/packages/cli"
}
```

This makes the dependency **explicit** (good for understanding architecture).

### 3. "We want to simplify onboarding"

**Response:** Document the relationship clearly (this file does that)

**Onboarding steps:**
```bash
# Step 1: Clone coderef-system (the source)
cd ~/Desktop/projects
git clone <coderef-system-repo>
cd coderef-system
pnpm install
pnpm build

# Step 2: Configure MCP servers (the wrappers)
cd ~/.mcp-servers
# Edit .mcp.json to point CODEREF_CLI_PATH to step 1 location

# Step 3: Start MCP servers
python coderef-context/server.py
```

**Clear, documented workflow beats mixing directories.**

---

## Conclusion

**Decision:** **Keep coderef-system in C:/Users/willh/Desktop/projects/**

**Reasoning:**
1. ✅ Separation of concerns (development repo vs MCP deployment)
2. ✅ Clean development workflow (TypeScript project in expected location)
3. ✅ Git independence (two separate repos, easier to manage)
4. ✅ Package management clarity (pnpm vs Python, no mixing)
5. ✅ Future-proof (CLI can be used beyond MCP servers)

**What to Do Instead:**
1. Document the relationship clearly (this file)
2. Keep current subprocess architecture
3. Consider global npm install later (production phase)
4. Update .mcp.json with clear comments explaining the dependency

**Final Word:** The current structure is **correct by design**. coderef-system is a development project that happens to have a CLI consumer (coderef-context MCP server). Moving it to .mcp-servers would blur the line between source and consumer, creating confusion and maintenance issues.

---

## Recommended Documentation Updates

### Update .mcp.json with Comments

```json
{
  "mcpServers": {
    "coderef-context": {
      "command": "python",
      "args": ["C:/Users/willh/.mcp-servers/coderef-context/server.py"],
      "env": {
        "CODEREF_CLI_PATH": "C:/Users/willh/Desktop/projects/coderef-system/packages/cli"
      },
      "description": "MCP wrapper for @coderef/cli (wraps external CLI via subprocess)",
      "_comment": "This server wraps the @coderef/core CLI tool. The CLI is a separate TypeScript project maintained at the CODEREF_CLI_PATH location. This is intentional - the CLI is the source of truth, and this MCP server is just a consumer."
    }
  }
}
```

### Create .mcp-servers/README.md

```markdown
# MCP Servers Directory

This directory contains **deployed MCP servers** (Python wrappers for Claude Code).

## Structure

- `coderef-context/` - MCP wrapper for @coderef/cli (calls external CLI via subprocess)
- `coderef-docs/` - Documentation generation MCP server
- `coderef-workflow/` - Planning & orchestration MCP server
- `coderef-personas/` - Expert agent personas MCP server
- `coderef-testing/` - Test automation MCP server

## External Dependencies

Some MCP servers wrap external tools:

- **coderef-context** → Depends on `@coderef/cli` (located at `C:/Users/willh/Desktop/projects/coderef-system/packages/cli`)

This is intentional. The CLI is a separate TypeScript development project. This MCP server is just a consumer.

## Why Not Move coderef-system Here?

coderef-system is a TypeScript development project (monorepo with core, CLI, generators, web packages). It belongs in the projects directory, not here. This directory is for deployed MCP servers only.
```

---

**Document Status:** ✅ Complete
**Recommendation:** Keep current structure, improve documentation
