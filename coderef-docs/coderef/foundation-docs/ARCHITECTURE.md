# Architecture Reference

**Version:** 3.4.0
**Last Updated:** 2026-01-10
**Server:** coderef-docs
**Pattern:** Modular MCP Server with POWER Framework

---

## Purpose

This document describes the architectural design of the coderef-docs MCP server, including system patterns, component interactions, data flow, and key design decisions. It provides a comprehensive understanding of how the system is structured and why.

---

## Overview

coderef-docs is a **modular Python MCP server** that generates documentation using the POWER framework templates with optional code intelligence injection from @coderef/core CLI.

**Core Principles:**
1. **Single Responsibility** - Each component has one clear purpose
2. **Dependency Injection** - Configurable paths and dependencies
3. **Graceful Degradation** - Falls back when optional features unavailable
4. **Separation of Concerns** - Tools, generators, validators are independent
5. **Consistency** - Standardized error handling and logging across all components

---

## System Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────┐
│                    MCP Protocol Layer                    │
│                   (JSON-RPC 2.0 / stdio)                 │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                     server.py                            │
│              (Tool Registration & Routing)               │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                  tool_handlers.py                        │
│           (13 Handlers with Decorators)                  │
│                                                          │
│  @log_invocation + @mcp_error_handler                   │
└─────────────────────────────────────────────────────────┘
                            ↓
        ┌───────────────────┼───────────────────┐
        ↓                   ↓                   ↓
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│  Generators  │   │  Extractors  │   │  Validators  │
├──────────────┤   ├──────────────┤   ├──────────────┤
│ Foundation   │   │ CLI Wrapper  │   │ Input Rules  │
│ Changelog    │   │ Cache (LRU)  │   │ Schemas      │
│ Standards    │   │ Fallback     │   │ Boundaries   │
│ Audit        │   └──────────────┘   └──────────────┘
│ Quickref     │
│ Resource*    │ *NEW v3.4.0
└──────────────┘
```

---

## Component Layers

### Layer 1: Protocol Interface

**Component:** server.py
**Responsibility:** MCP protocol compliance, tool registration, request routing
**Technology:** mcp.server (Model Context Protocol SDK)

**Key Functions:**
- `list_tools()` - Returns 13 tool schemas
- `call_tool(name, arguments)` - Routes to appropriate handler
- `health_check()` - Validates @coderef/core CLI availability

---

### Layer 2: Business Logic

**Component:** tool_handlers.py
**Responsibility:** Implement core functionality for each of 13 tools
**Pattern:** Decorator pattern for cross-cutting concerns

**Decorators:**
```python
@log_invocation  # Logs tool entry/exit with timing
@mcp_error_handler  # Catches exceptions, formats errors
async def handle_tool(arguments):
    ...
```

**Tools Categorization:**
1. **Template Tools** (2) - list_templates, get_template
2. **Foundation Docs** (2) - generate_foundation_docs, generate_individual_doc
3. **Resource Sheets** (1) - generate_resource_sheet (NEW v3.4.0)
4. **Changelog** (3) - get_changelog, add_changelog_entry, record_changes
5. **Standards** (3) - establish_standards, audit_codebase, check_consistency
6. **Validation** (2) - validate_document, check_document_health

---

### Layer 3: Domain Logic

**Components:** generators/*
**Responsibility:** Document generation workflows
**Pattern:** Strategy pattern (different generators for different docs)

**Generator Hierarchy:**
```
BaseGenerator (abstract)
    ├── FoundationGenerator (5-doc workflow)
    ├── ChangelogGenerator (CRUD + validation)
    ├── StandardsGenerator (pattern extraction)
    ├── AuditGenerator (compliance checking)
    ├── QuickrefGenerator (interactive Q&A)
    └── ResourceSheetGenerator (module composition) *NEW v3.4.0
```

---

### Layer 4: Integration

**Component:** extractors.py
**Responsibility:** Code intelligence extraction from @coderef/core CLI
**Pattern:** Adapter pattern (wraps external CLI)

**Features:**
- LRU caching (@lru_cache decorator)
- Subprocess management
- JSON parsing
- Graceful fallback to placeholders

**CLI Integration:**
```python
def extract_apis(project_path: str) -> Dict:
    # Call: coderef scan {project_path} --json
    # Parse: JSON output
    # Return: {endpoints: [...], patterns: [...]}
```

---

### Layer 5: Cross-Cutting Concerns

**Validation:** validation.py - Input boundary checks (REF-003)
**Error Handling:** error_responses.py - Consistent formatting (ARCH-001)
**Logging:** logger_config.py - Structured logging (ARCH-003)
**Constants:** constants.py - Global config (REF-002)

---

## Data Flow

### Foundation Docs Generation Flow

```
User Request (project_path)
    ↓
generate_foundation_docs(project_path)
    ↓
Sequential Generation [1/5] → [5/5]
    ↓
For each template:
    ├→ Read POWER template
    ├→ (Optional) Extract code intelligence
    ├→ Return template + instructions
    └→ Claude populates template
    ↓
Save to output location
    ├→ README.md → project root
    └→ Others → coderef/foundation-docs/
```

### Resource Sheet Generation Flow (NEW v3.4.0)

```
User Request (element_name, mode, format)
    ↓
Detect Code Characteristics (20+ boolean flags)
    ↓
Select Modules (4 universal + conditional)
    ↓
Compose Documentation
    ├→ Markdown format
    ├→ JSON Schema format
    └→ JSDoc format
    ↓
Auto-Fill (50% in Phase 1)
    ├→ Architecture module (from .coderef/index.json)
    ├→ Integration module (dependencies, imports)
    └→ Stubs (testing, performance)
    ↓
Return 3-format output
```

### Changelog Recording Flow

```
User Request (version, workorder_id?)
    ↓
Auto-Detect Git Changes
    ├→ git diff --name-only
    ├→ git diff --stat
    └→ git log -1
    ↓
Suggest change_type & severity
    ↓
AI Agent Reviews & Confirms
    ↓
Validate Against Schema
    ↓
Write to CHANGELOG.json
```

---

## Design Patterns

### 1. Decorator Pattern

**Usage:** Cross-cutting concerns (logging, error handling)

```python
@log_invocation
@mcp_error_handler
async def handle_generate_docs(args):
    # Core logic without boilerplate
```

**Benefits:**
- Separation of concerns
- Reusable across all 13 handlers
- Consistent behavior

---

### 2. Strategy Pattern

**Usage:** Different generators for different doc types

```python
class BaseGenerator:
    def generate(self): pass

class FoundationGenerator(BaseGenerator):
    def generate(self): # 5-doc workflow

class ChangelogGenerator(BaseGenerator):
    def generate(self): # CHANGELOG.json CRUD
```

---

### 3. Adapter Pattern

**Usage:** @coderef/core CLI integration

```python
# External CLI with complex API
def extract_apis(project_path):
    # Adapts CLI to simple Dict interface
```

---

### 4. Template Method Pattern

**Usage:** BaseGenerator workflow

```python
class BaseGenerator:
    def generate(self):
        self.read_template()
        self.extract_context()  # Overridable
        self.populate_template()
        self.save_output()
```

---

## Key Design Decisions

### Decision 1: Sequential vs Batch Foundation Docs

**Chosen:** Sequential generation ([1/5] → [5/5])
**Rejected:** Batch dump all templates at once
**Reason:** Eliminates timeout errors (~1,470 lines → 5x ~250-350 lines)

**Impact:** v3.2.0 upgrade
**Trade-off:** Slight latency increase (5 calls) vs stability

---

### Decision 2: Optional vs Required Code Intelligence

**Chosen:** Optional with graceful fallback
**Rejected:** Required @coderef/core CLI dependency
**Reason:** Works on any system, even without CLI

**Impact:** Usability vs feature completeness
**Implementation:** extractors.py returns empty dict on CLI failure

---

### Decision 3: POWER Framework vs Free-Form

**Chosen:** Standardized POWER template structure
**Rejected:** Ad-hoc documentation styles
**Reason:** Consistency, proven effectiveness, reusability

**POWER = Purpose, Overview, What/Why/When, Examples, References**

---

### Decision 4: Composable Modules vs Rigid Templates

**Chosen:** Composable module architecture (v3.4.0)
**Rejected:** 20 rigid per-element templates
**Reason:** Flexibility, DRY principle, auto-fill capability

**Implementation:** ResourceSheetGenerator with detection engine

---

### Decision 5: UDS Metadata Optional vs Required

**Chosen:** Optional (only for workorder docs)
**Rejected:** Required for all documentation
**Reason:** Backward compatibility, not all docs need tracking

**Scope:**
- ✅ Workorder docs (plan.json, DELIVERABLES.md)
- ❌ Foundation docs (README, ARCHITECTURE)

---

## Architectural Constraints

### Technical Constraints

1. **Python 3.10+** - Required for modern typing features
2. **MCP Protocol 1.0** - JSON-RPC 2.0 over stdio
3. **File System Access** - Requires read/write permissions
4. **Git Repository** - Optional (for changelog auto-detection)

### Performance Constraints

1. **2-minute timeout** - All tools must complete within 120s
2. **LRU cache size** - 32 entries max for CLI results
3. **Sequential generation** - No parallel doc generation

### Security Constraints

1. **Path traversal prevention** - Validates all file paths
2. **No code execution** - Pure document generation
3. **Read-only analysis** - Doesn't modify source code

---

## Integration Points

### External Dependencies

**Required:**
- Python stdlib (pathlib, json, asyncio)
- MCP SDK (mcp.server)
- jsonschema (validation)

**Optional:**
- @coderef/core CLI (code intelligence)
- Git (changelog auto-detection)

### Integration with CodeRef Ecosystem

**Upstream:** None (standalone server)
**Downstream:**
- coderef-workflow (orchestrates doc generation)
- Claude Code (MCP client)

---

## Error Handling Strategy

### Layered Error Handling

```
Layer 1: Validation (validation.py)
    ↓ ValueError on invalid input
Layer 2: Tool Handlers (@mcp_error_handler)
    ↓ Catches all exceptions
Layer 3: Error Responses (error_responses.py)
    ↓ Formats user-friendly messages
Layer 4: MCP Protocol
    ↓ Returns TextContent with error
```

### Error Response Format

```json
{
  "type": "text",
  "text": "❌ Error: [what went wrong]\n\nDetails: [context]\n\nSuggestion: [how to fix]"
}
```

---

## Logging Strategy

**Levels:**
- INFO: Tool invocations, major operations
- DEBUG: Internal state, detailed flow
- ERROR: Exceptions, validation failures

**Format:**
```
2026-01-10 00:00:00 - coderef-docs - INFO - Tool called: generate_docs
2026-01-10 00:00:01 - coderef-docs - DEBUG - Reading template: api
2026-01-10 00:00:02 - coderef-docs - INFO - Successfully generated: API.md
```

---

## Future Architecture Considerations

**Planned:**
1. REST API wrapper (HTTP server mode)
2. Multi-language template support
3. Plugin architecture for custom generators
4. Distributed generation (parallel doc creation)

**Under Consideration:**
1. Database integration for changelog
2. Real-time collaboration support
3. Version control integration beyond git

---

## References

- **Component Details:** [COMPONENTS.md](COMPONENTS.md)
- **API Specifications:** [API.md](API.md)
- **Data Schemas:** [SCHEMA.md](SCHEMA.md)
- **MCP Specification:** https://spec.modelcontextprotocol.io/

---

**Maintained by:** coderef-docs MCP server
**Generated:** 2026-01-10
**AI Assistance:** Claude Code (Sonnet 4.5)
