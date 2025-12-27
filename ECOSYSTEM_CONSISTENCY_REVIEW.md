# CodeRef Ecosystem - Consistency Review

**Date:** December 26, 2025
**Scope:** All 4 MCP servers (coderef-context, coderef-workflow, coderef-docs, coderef-personas)
**Focus:** CLAUDE.md consistency, version alignment, mcp.json configuration

---

## Executive Summary

The ecosystem has **inconsistent documentation** across the 4 servers. Three servers have updated CLAUDE.md files, but **coderef-context is missing its CLAUDE.md entirely**. Global mcp.json configuration is present, but **NO local mcp.json files** exist in any server directory.

**Critical Issue:** coderef-context has no documentation in the current architecture.

---

## CLAUDE.md Analysis

### Overview Table

| Server | File | Lines | Version | Status | Latest Update |
|--------|------|-------|---------|--------|----------------|
| **coderef-context** | ❌ MISSING | — | — | ⚠️ UNDOCUMENTED | — |
| **coderef-workflow** | ✅ Present | 659 | 1.1.0 | ✅ Updated | 2025-12-25 (v1.1.0) |
| **coderef-docs** | ✅ Present | 245 | 3.1.0 | ✅ Updated | 2025-12-25 (v3.1.0) |
| **coderef-personas** | ✅ Present | 552 | 1.4.0 | ✅ Updated | 2025-12-25 (v1.4.0) |

**TOTAL LINES (with context):** 1,456 lines (missing 1 server)

---

## Critical Issue: Missing coderef-context CLAUDE.md

### Problem
**coderef-context has no CLAUDE.md file**, making it the only server without AI context documentation.

### Impact
- AI agents cannot quickly understand coderef-context architecture
- No documented tool catalog, use cases, or design decisions
- Inconsistent with ecosystem requirement: "All servers must have CLAUDE.md"
- Blocks proper integration documentation

### Recommended Fix
**Create `coderef-context/CLAUDE.md`** with:
- Purpose: Code intelligence via AST analysis and dependency tracking
- 10+ code analysis tools (coderef_scan, coderef_query, coderef_impact, etc.)
- Integration points with coderef-workflow
- Use cases and examples
- ~300-400 lines (similar to coderef-docs pattern)

---

## Version Alignment Analysis

### Current Versions

```
coderef-context:   [NO VERSION - MISSING CLAUDE.md]
coderef-workflow:  v1.1.0
coderef-docs:      v3.1.0
coderef-personas:  v1.4.0
```

### Version Pattern Observation
- **workflow**: v1.1.0 (enterprise-grade, workorder-centric)
- **docs**: v3.1.0 (mature, documentation focused)
- **personas**: v1.4.0 (evolved through optimizations)
- **context**: NO VERSION INFO (problem!)

### Recommendation
Define and document coderef-context version. Suggest: **v2.0.0** (as it wraps @coderef/core CLI and is a mature integration point)

---

## CLAUDE.md Content Analysis

### coderef-workflow CLAUDE.md (659 lines)

**Structure:** ✅ Follows standard 15-section template
- META (title, version, status, dates)
- Quick Summary + Latest Updates
- Global Deployment Rule
- Architecture & Integration
- Tech Stack & Project Structure
- Core Tools (23 MCP tools with table)
- Slash Commands (40+ commands)
- Key Concepts
- Design Decisions (4 decisions documented)
- File Structure
- Essential Commands
- Use Cases (3 scenarios)
- Recent Changes (v1.1.0 + v0.9.0)
- Next Steps

**Strengths:**
- ✅ Comprehensive tool catalog (23 tools)
- ✅ Excellent integration documentation (coderef-context usage)
- ✅ Complete design decision rationale
- ✅ Well-documented file structure

**Gaps:**
- ❌ Workorder ID format documented but no examples
- ❌ No specific coderef-context integration examples
- ⚠️ Mentions "40+ slash commands" but only lists 7 in documentation

---

### coderef-docs CLAUDE.md (245 lines)

**Structure:** ✅ Lean version of standard template
- META (title, version, status, dates)
- Quick Summary
- Global Deployment Rule
- Architecture (responsibilities + integration)
- Tools Catalog (11 tools with table)
- POWER Framework explanation
- File Structure
- Design Decisions (4 decisions)
- Essential Commands
- Use Cases (2 scenarios)
- Recent Changes (v3.1.0 + v3.0.0)
- Next Steps

**Strengths:**
- ✅ Concise and focused (minimal bloat)
- ✅ Clear tool catalog (11 tools)
- ✅ POWER framework well explained
- ✅ Design rationale documented
- ✅ 93% reduction from v2.0.0 (3,250 → 245 lines) - excellent

**Gaps:**
- ❌ No specific examples of POWER framework output
- ❌ Limited integration examples
- ⚠️ Minimal file structure documentation

---

### coderef-personas CLAUDE.md (552 lines)

**Structure:** ✅ Follows standard template with persona specialization
- META (title, version, status, dates)
- Quick Summary + Project Vision
- Global Deployment Rule
- Architecture (persona activation)
- Current Implementation (5 personas documented)
- Personas Can Use MCP Tools (integration example)
- Tech Stack
- Project Structure
- Core Expert Persona (mcp-expert details)
- Persona Capabilities (14 expertise areas)
- Design Decisions (4 decisions)
- Essential Commands
- Use Cases
- Recent Changes (v1.4.0 + v1.3.0)
- Integration Guide

**Strengths:**
- ✅ Clear persona activation pattern
- ✅ Comprehensive expertise documentation
- ✅ Good integration examples (personas calling other MCP tools)
- ✅ v1.4.0 optimization documented (85% reduction: 1,017 → 153 lines)

**Gaps:**
- ❌ Limited use case examples (only theoretical)
- ❌ No practical persona switching examples
- ⚠️ Architecture described as "no hierarchical dependencies" - could use clarity

---

## mcp.json Configuration Analysis

### Global Configuration (~/.mcp.json)

**Location:** `C:\Users\willh\.mcp.json`

**Configuration:**
```json
{
  "mcpServers": {
    "coderef-personas": {
      "command": "python",
      "args": ["C:/Users/willh/.mcp-servers/coderef-personas/server.py"],
      "cwd": "C:/Users/willh/.mcp-servers/coderef-personas"
    },
    "coderef-context": {
      "command": "python",
      "args": ["C:/Users/willh/.mcp-servers/coderef-context/server.py"],
      "cwd": "C:/Users/willh/.mcp-servers/coderef-context",
      "env": {
        "CODEREF_CLI_PATH": "C:/Users/willh/Desktop/projects/coderef-system/packages/cli"
      },
      "description": "MCP server exposing @coderef/core CLI tools to Claude agents",
      "tools": [
        "coderef_scan", "coderef_query", "coderef_impact", "coderef_complexity",
        "coderef_patterns", "coderef_coverage", "coderef_context", "coderef_validate",
        "coderef_drift", "coderef_diagram"
      ]
    },
    "coderef-docs": {
      "command": "python",
      "args": ["C:/Users/willh/.mcp-servers/coderef-docs/server.py"],
      "cwd": "C:/Users/willh/.mcp-servers/coderef-docs"
    },
    "coderef-workflow": {
      "command": "python",
      "args": ["C:/Users/willh/.mcp-servers/coderef-workflow/server.py"],
      "cwd": "C:/Users/willh/.mcp-servers/coderef-workflow"
    }
  }
}
```

### Local mcp.json Files

**Status:** ❌ NO local mcp.json files in any server directory

**Checked:**
- ❌ `coderef-context/mcp.json` - NOT FOUND
- ❌ `coderef-workflow/mcp.json` - NOT FOUND
- ❌ `coderef-docs/mcp.json` - NOT FOUND
- ❌ `coderef-personas/mcp.json` - NOT FOUND

### Configuration Analysis

**Strengths:**
- ✅ All 4 servers configured in global config
- ✅ coderef-context has environment variable setup (CODEREF_CLI_PATH)
- ✅ coderef-context documents all 10 available tools in config
- ✅ All servers use correct Python entry point (server.py)

**Inconsistencies:**
- ⚠️ **Only coderef-context has metadata** (description, tools list)
  - coderef-docs, coderef-personas, coderef-workflow lack metadata
- ⚠️ **Only coderef-context has environment variables**
  - Other servers may need config but aren't documented
- ❌ **No local mcp.json files** (all configuration is global only)

**Recommendation:**
Either:
1. **Add metadata to other servers** in global .mcp.json (consistent with coderef-context pattern), or
2. **Remove metadata from coderef-context** for consistency

---

## Consistency Issues Identified

### Issue 1: Missing coderef-context CLAUDE.md
**Severity:** 🔴 CRITICAL

No documentation exists for coderef-context.

**Solution:** Create coderef-context/CLAUDE.md following ecosystem template

---

### Issue 2: Uneven mcp.json Metadata
**Severity:** 🟡 MEDIUM

Only coderef-context has description and tools list in .mcp.json.

**Solution:** Either standardize all 4 servers with metadata or remove from coderef-context

---

### Issue 3: Version Number Inconsistency
**Severity:** 🟡 MEDIUM

Three servers have versions (1.1.0, 3.1.0, 1.4.0) but coderef-context has no version.

**Solution:** Define coderef-context version (suggest v2.0.0)

---

### Issue 4: Documentation Comprehensiveness Gap
**Severity:** 🟡 MEDIUM

CLAUDE.md files vary significantly:
- coderef-workflow: 659 lines (comprehensive)
- coderef-personas: 552 lines (comprehensive)
- coderef-docs: 245 lines (lean)
- coderef-context: 0 lines (missing)

**Solution:** Create coderef-context CLAUDE.md ~350 lines, aiming for consistency

---

### Issue 5: mcp.json Metadata Distribution
**Severity:** 🟠 MINOR

Configuration metadata is inconsistent:
- coderef-context: Has `description`, `tools` array (most detailed)
- coderef-workflow, coderef-docs, coderef-personas: Minimal configuration

**Solution:** Decide on metadata standard and apply to all servers

---

## Detailed Comparison Table

| Aspect | coderef-context | coderef-workflow | coderef-docs | coderef-personas |
|--------|-----------------|------------------|--------------|------------------|
| **CLAUDE.md** | ❌ MISSING | ✅ 659 lines | ✅ 245 lines | ✅ 552 lines |
| **Version** | ❌ NONE | 1.1.0 | 3.1.0 | 1.4.0 |
| **Last Update** | — | 2025-12-25 | 2025-12-25 | 2025-12-25 |
| **Tool Count** | 10 tools | 23 tools | 11 tools | 5 personas |
| **mcp.json** | Global only | Global only | Global only | Global only |
| **mcp.json Metadata** | ✅ Full | ❌ Minimal | ❌ Minimal | ❌ Minimal |
| **Design Decisions** | — | ✅ 4 documented | ✅ 4 documented | ✅ 4 documented |
| **Use Cases** | — | ✅ 3 scenarios | ✅ 2 scenarios | ✅ 3+ scenarios |

---

## Recommendations

### Priority 1: Create coderef-context CLAUDE.md (CRITICAL)

**File:** `coderef-context/CLAUDE.md`
**Target Size:** ~350-400 lines
**Structure:**
1. Meta documentation
2. Quick summary
3. Architecture & tool catalog
4. Design decisions
5. Integration with coderef-workflow
6. Use cases
7. Recent changes

**Key Content:**
- Document 10 code analysis tools
- Explain AST-based analysis approach
- Show integration pattern with coderef-workflow
- Provide examples of each tool

**Timeline:** IMMEDIATE (blocks full ecosystem documentation)

---

### Priority 2: Standardize mcp.json Metadata (MEDIUM)

**Option A (Recommended):** Add metadata to all servers
```json
"coderef-workflow": {
  "description": "Feature lifecycle orchestration and planning",
  "tools": ["gather_context", "create_plan", "execute_plan", ...],
  ...
}
```

**Option B:** Remove metadata from coderef-context
- Keep it minimal across all servers
- More consistent with "no local config" philosophy

**Timeline:** After coderef-context CLAUDE.md

---

### Priority 3: Define Version for coderef-context (MEDIUM)

**Recommendation:** v2.0.0

**Rationale:**
- v1.x suggests immature; coderef-context is stable
- Wraps @coderef/core which is mature TypeScript project
- Multiple major features (scan, query, impact, patterns, complexity, etc.)
- Well-integrated into ecosystem

**Update:** Add to new coderef-context/CLAUDE.md

---

### Priority 4: Document Integration Patterns (LOW)

Update coderef-workflow CLAUDE.md to include:
- Specific examples of coderef-context tool calls
- JSON request/response examples
- Error handling patterns
- Fallback mechanisms

---

## Global Deployment Rule Compliance

All servers follow the **Global Deployment Rule:**

✅ All configuration in global `~/.mcp.json`
✅ No local mcp.json files (following "single global source of truth")
✅ coderef/workorder, coderef/archived, coderef/standards all global
✅ Slash commands in `~/.claude/commands/`

**Status:** ✅ COMPLIANT

---

## Summary

| Category | Status | Issue Count |
|----------|--------|------------|
| **CLAUDE.md Completeness** | 🔴 75% | 1 critical (missing coderef-context) |
| **Version Alignment** | 🟡 75% | 1 medium (no coderef-context version) |
| **mcp.json Configuration** | 🟡 Inconsistent | 1 medium (metadata distribution) |
| **Global Deployment** | ✅ Compliant | 0 issues |
| **Documentation Quality** | ✅ Good | 0 issues |

**Overall:** Ecosystem is 75% consistent with **ONE CRITICAL GAP** (missing coderef-context CLAUDE.md)

---

## Action Items

- [ ] **CRITICAL:** Create coderef-context/CLAUDE.md (~350 lines)
- [ ] **MEDIUM:** Standardize mcp.json metadata across all 4 servers
- [ ] **MEDIUM:** Define and document coderef-context version (v2.0.0)
- [ ] **LOW:** Add integration examples to coderef-workflow CLAUDE.md
- [ ] **LOW:** Create ecosystem-wide consistency checklist

---

**Review Date:** December 26, 2025
**Reviewed By:** Claude Code AI
**Status:** ✅ Review Complete - 1 Critical Issue Identified

