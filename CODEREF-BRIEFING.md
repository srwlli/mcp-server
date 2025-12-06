# CodeRef MCP Tools - Agent Briefing

## What It Is

CodeRef scans codebases to build a dependency graph. You can query "what calls X?" and get answers without an IDE.

**Why it matters for you:** You're in a terminal, not VS Code. You don't have "Find All References". CodeRef gives you that.

---

## Available MCP Tools

You have access to these tools (prefix: `mcp__coderef-mcp__`):

| Tool | What it does |
|------|--------------|
| `mcp__coderef__scan_realtime` | Scan a directory, build dependency graph |
| `mcp__coderef__nl_query` | Ask questions in plain English |
| `mcp__coderef__query` | Query the dependency graph directly |
| `mcp__coderef__analyze` | Impact analysis, coverage, complexity |
| `mcp__coderef__validate` | Check CodeRef tag syntax |
| `mcp__coderef__audit` | Codebase health check |

---

## Quick Start

### 1. Scan a codebase first

```json
{
  "source_dir": "./src",
  "languages": ["ts", "tsx", "py"],
  "analyzer": "ast"
}
```

This builds the index. Do this once per project.

### 2. Ask questions

**Graph queries (free, instant):**
- "what calls login?"
- "find tests for UserService"
- "dependencies of authenticate"

**These work immediately after scanning.**

### 3. Get impact analysis

Before changing code:
```
mcp__coderef__analyze with reference="functionName" and analysis_type="impact"
```

Returns: affected files, risk level (LOW/MEDIUM/HIGH), test coverage.

---

## Query Types

| Query | Example |
|-------|---------|
| Callers | "what calls login?" |
| Callees | "what does login call?" |
| Tests | "find tests for UserService" |
| Impact | "impact of changing login" |
| Dependencies | "dependencies of authenticate" |
| Search | "find all functions in auth" |

---

## What It Actually Scans

- **TypeScript/JavaScript:** Functions, classes, methods, components, hooks
- **Python:** Functions, classes, methods, decorators

**Accuracy:** AST mode = 99% precision

---

## Practical Use Cases

### Understanding unfamiliar code
```
1. scan_realtime on the directory
2. nl_query: "find all functions in auth"
3. nl_query: "what calls authenticate"
```

### Before refactoring
```
1. analyze with type="impact" on the function
2. Check risk level and affected files
3. Proceed if LOW/MEDIUM, be careful if HIGH
```

### Finding dead code
```
nl_query: "find functions with no callers"
```

---

## What It Doesn't Do

- No IDE features (no go-to-definition, no hover)
- No real-time file watching
- No automatic tag insertion
- RAG/semantic queries need API key (optional)

---

## File Locations

| Component | Path |
|-----------|------|
| MCP Server | `C:\Users\willh\.mcp-servers\coderef-mcp\` |
| CLI | `C:\Users\willh\Desktop\projects - current-location\coderef-system\packages\cli\` |
| Core | `C:\Users\willh\Desktop\projects - current-location\coderef-system\packages\core\` |

---

## TL;DR

1. **Scan first:** `scan_realtime` with your source directory
2. **Ask questions:** `nl_query` with plain English
3. **Check impact:** `analyze` before changing things

That's it. Don't overthink it.

---

*Last updated: 2025-12-03*
