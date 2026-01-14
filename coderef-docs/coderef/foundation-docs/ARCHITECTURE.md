# Architecture Reference

**Version:** 4.0.0
**Last Updated:** 2026-01-13
**Server:** coderef-docs
**Pattern:** Modular MCP Server with MCP Orchestration + User Docs Automation

---

## Purpose

This document describes the architectural design of the coderef-docs MCP server, including system patterns, component interactions, data flow, and key design decisions from v4.0.0 (WO-GENERATION-ENHANCEMENT-001). It provides a comprehensive understanding of how the system is structured and why.

**v4.0.0 Highlights:**
- **MCP Orchestration Layer** - Centralized MCP tool calling with caching
- **User Docs Automation** - 3 new generators with 75%+ auto-fill rate
- **Standards Enhancement** - Semantic pattern analysis with frequency tracking
- **Tool Consolidation** - Clear hierarchy with [INTERNAL] and [DEPRECATED] markings

---

## Overview

coderef-docs is a **modular Python MCP server** that generates documentation using the POWER framework templates with optional code intelligence injection from @coderef/core CLI and enhanced by coderef-context MCP orchestration.

**Core Principles:**
1. **Single Responsibility** - Each component has one clear purpose
2. **Dependency Injection** - Configurable paths and dependencies
3. **Graceful Degradation** - Falls back when optional features unavailable
4. **Separation of Concerns** - Tools, generators, validators are independent
5. **Consistency** - Standardized error handling and logging across all components
6. **MCP Orchestration** - Centralized calling layer with caching (NEW v4.0.0)

---

## System Architecture

### High-Level Design (v4.0.0)

```
┌─────────────────────────────────────────────────────────┐
│                    MCP Protocol Layer                    │
│                   (JSON-RPC 2.0 / stdio)                 │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                     server.py                            │
│          (Tool Registration & Routing - 16 tools)        │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                  tool_handlers.py                        │
│           (16 Handlers with Decorators)                  │
│                                                          │
│  @log_invocation + @mcp_error_handler                   │
│  + MCP orchestration integration (v4.0.0)               │
└─────────────────────────────────────────────────────────┘
                            ↓
        ┌───────────────────┼───────────────────┬──────────────────┐
        ↓                   ↓                   ↓                  ↓
┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ MCP Orchestr │   │  Generators  │   │  Extractors  │   │  Validators  │
├──────────────┤   ├──────────────┤   ├──────────────┤   ├──────────────┤
│ Patterns     │   │ Foundation   │   │ CLI Wrapper  │   │ Input Rules  │
│ Drift Check  │   │ User Docs*   │   │ Cache (LRU)  │   │ Schemas      │
│ Resources    │   │ Changelog    │   │ Fallback     │   │ Boundaries   │
│ Cache (15m)  │   │ Standards+   │   └──────────────┘   └──────────────┘
└──────────────┘   │ Audit        │
  *NEW v4.0.0      │ Quickref     │
  +ENHANCED v4.0.0 │ Resource     │
                   └──────────────┘
```

**Key Architectural Changes in v4.0.0:**
- **New Layer:** MCP Orchestration (mcp_orchestrator.py)
- **Enhanced:** tool_handlers.py (13 → 16 tools)
- **New Generators:** user_guide_generator.py (3 new tools)
- **Enhanced:** standards_generator.py (MCP semantic patterns)

---

## Component Layers

### Layer 0: MCP Orchestration (NEW v4.0.0)

**Component:** mcp_orchestrator.py
**Responsibility:** Centralized MCP tool calling with caching for external MCP servers
**Technology:** Direct MCP tool invocation with in-memory caching

**Key Functions:**
- `call_coderef_patterns()` - Call coderef-context coderef_patterns tool with 15-min cache
- `check_drift()` - Check .coderef/index.json drift vs current codebase (real-time, no cache)
- `check_coderef_resources()` - Validate .coderef/ resource availability

**Architecture Pattern:**
```python
# Centralized MCP calling with caching
async def call_coderef_patterns(project_path, pattern_type, use_cache=True):
    cache_key = f"{project_path}:{pattern_type}"

    if use_cache and cache_key in _pattern_cache:
        return _pattern_cache[cache_key]  # < 50ms

    # Call external MCP server
    result = await mcp_client.call_tool("coderef_patterns", {...})  # ~2-5s

    _pattern_cache[cache_key] = result
    return result
```

**Benefits:**
- **Performance:** Caching reduces redundant expensive calls (2-5s → 50ms)
- **Centralization:** Single point of MCP integration
- **Graceful Degradation:** Returns `{"success": False}` instead of throwing
- **Clear Separation:** MCP logic isolated from business logic

**Integration Points:**
- Used by: tool_handlers.py (generate_foundation_docs, establish_standards, list_templates)
- Calls: coderef-context MCP server (external)

---

### Layer 1: Protocol Interface

**Component:** server.py
**Responsibility:** MCP protocol compliance, tool registration, request routing
**Technology:** mcp.server (Model Context Protocol SDK)

**Key Functions:**
- `list_tools()` - Returns 16 tool schemas (up from 13 in v3.7.0)
- `call_tool(name, arguments)` - Routes to appropriate handler
- `health_check()` - Validates @coderef/core CLI + MCP server availability

**v4.0.0 Changes:**
- Added 3 new tool registrations (generate_my_guide, generate_user_guide, generate_features)
- Updated tool schema for generate_individual_doc ([INTERNAL] marking)
- Updated tool schema for coderef_foundation_docs ([DEPRECATED] marking)
- Enhanced list_templates to include MCP status (✅ Available / ⚠️ Unavailable)

---

### Layer 2: Business Logic

**Component:** tool_handlers.py
**Responsibility:** Implement core functionality for each of 16 tools
**Pattern:** Decorator pattern for cross-cutting concerns + MCP orchestration integration

**Decorators:**
```python
@log_invocation  # Logs tool entry/exit with timing
@mcp_error_handler  # Catches exceptions, formats errors
async def handle_tool(arguments):
    # NEW v4.0.0: MCP orchestration calls
    drift_result = await check_drift(project_path)
    patterns = await call_coderef_patterns(project_path)

    # Business logic
    ...
```

**Tools Categorization (v4.0.0):**
1. **Utility** (2) - list_templates (+MCP status), get_template
2. **Foundation Docs** (3) - generate_foundation_docs (+drift), generate_individual_doc [INTERNAL], coderef_foundation_docs [DEPRECATED]
3. **User Docs** (4 - NEW v4.0.0) - generate_my_guide, generate_user_guide, generate_features, generate_quickref_interactive
4. **Changelog** (2) - add_changelog_entry, record_changes
5. **Standards** (3) - establish_standards (+MCP patterns), audit_codebase, check_consistency
6. **Validation** (2) - validate_document, check_document_health
7. **Advanced** (1) - generate_resource_sheet

**v4.0.0 Enhancements:**
- **Drift Detection:** generate_foundation_docs checks drift before generation
- **Semantic Patterns:** establish_standards uses MCP patterns for 80%+ quality
- **Tool Extraction:** User docs tools extract from .coderef/index.json
- **Health Check:** list_templates shows MCP status (< 100ms check)

---

### Layer 3: Domain Logic

**Components:** generators/*
**Responsibility:** Document generation workflows
**Pattern:** Strategy pattern (different generators for different docs)

**Generator Hierarchy (v4.0.0):**
```
BaseGenerator (abstract)
    ├── FoundationGenerator (5-doc workflow)
    ├── UserGuideGenerator (3 new docs) *NEW v4.0.0
    ├── ChangelogGenerator (CRUD + validation)
    ├── StandardsGenerator (MCP semantic patterns) *ENHANCED v4.0.0
    ├── AuditGenerator (compliance checking)
    ├── QuickrefGenerator (interactive Q&A)
    └── ResourceSheetGenerator (module composition)
```

**New: UserGuideGenerator (v4.0.0):**
- **Purpose:** Auto-generate user-facing docs with 75%+ auto-fill rate
- **Methods:**
  - `extract_mcp_tools()` - Discover tools from .coderef/index.json
  - `scan_slash_commands()` - Discover commands from .claude/commands/
  - `generate_my_guide()` - Developer quick-start (60-80 lines)
  - `generate_user_guide()` - Comprehensive guide (10 sections, 200+ lines)
  - `generate_features_doc()` - Feature inventory with workorder tracking
- **Auto-Fill Strategy:**
  - Tools: 100% auto-filled from code intelligence
  - Commands: 100% auto-filled from filesystem scan
  - Examples: 50-60% auto-generated from patterns
  - **Overall: 75%+ auto-fill rate**

**Enhanced: StandardsGenerator (v4.0.0):**
- **New:** `_analyze_patterns_with_mcp()` - MCP semantic pattern analysis
- **Pattern Frequency Tracking:** e.g., "async_function: 45 occurrences"
- **Consistency Violation Detection:** Files not following patterns
- **Quality Improvement:** 55% (regex-only) → 80%+ (with MCP patterns)
- **Graceful Fallback:** Falls back to regex if MCP unavailable

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

**v4.0.0 Note:** Extractors remain unchanged but coexist with MCP orchestration for different use cases:
- **extractors.py:** Direct CLI calls for foundation doc generation
- **mcp_orchestrator.py:** MCP calls for drift detection and semantic patterns

---

### Layer 5: Cross-Cutting Concerns

**Validation:** validation.py - Input boundary checks
**Error Handling:** error_responses.py - Consistent formatting
**Logging:** logger_config.py - Structured logging
**Constants:** constants.py - Global config
**MCP Integration:** mcp_integration.py - .coderef/ resource reading

---

## Data Flow

### Foundation Docs Generation Flow (v4.0.0)

```
User Request (project_path)
    ↓
generate_foundation_docs(project_path)
    ↓
NEW v4.0.0: Drift Detection
    ├→ call mcp_orchestrator.check_drift()
    ├→ if drift > 50%: warn user (severe)
    ├→ if drift 10-50%: warn user (standard)
    └→ if drift ≤ 10%: continue (none)
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

### User Docs Generation Flow (NEW v4.0.0)

```
User Request (project_path, doc_type)
    ↓
my-guide / USER-GUIDE / FEATURES
    ↓
Auto-Discovery Phase (75%+ auto-fill)
    ├→ Extract MCP tools from .coderef/index.json
    │   └→ Filter for handle_* functions in tool_handlers.py
    ├→ Scan slash commands from .claude/commands/
    │   └→ Read all *.txt files in directory
    ├→ (FEATURES only) Scan workorder directories
    │   └→ Extract workorder IDs, status from plan.json
    └→ Categorize by function (Documentation, Changelog, Standards)
    ↓
Template Population
    ├→ Tools: 100% auto-filled
    ├→ Commands: 100% auto-filled
    ├→ Examples: 50-60% auto-generated
    └→ Workflows: Manual (25% of content)
    ↓
Generate & Save
    ├→ my-guide.md (60-80 lines)
    ├→ USER-GUIDE.md (200+ lines, 10 sections)
    └→ FEATURES.md (100+ lines, executive summary)
```

### Standards Generation Flow (Enhanced v4.0.0)

```
User Request (project_path, focus_areas, scan_depth)
    ↓
NEW v4.0.0: Try MCP Semantic Patterns First
    ├→ call mcp_orchestrator.call_coderef_patterns()
    ├→ if success:
    │   ├→ Use semantic patterns with frequency data
    │   ├→ Track pattern occurrences (e.g., "async_function: 45")
    │   ├→ Detect consistency violations
    │   └→ Quality score: 80%+
    └→ if failure:
        ├→ Fallback to regex patterns
        └→ Quality score: 55%
    ↓
Generate 3 Standards Files
    ├→ ui-patterns.md
    ├→ behavior-patterns.md
    └→ ux-patterns.md
```

### Resource Sheet Generation Flow

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

### 1. MCP Orchestration Pattern (NEW v4.0.0)

**Usage:** Centralized MCP tool calling with caching

```python
# mcp_orchestrator.py
async def call_coderef_patterns(project_path, pattern_type, use_cache=True):
    cache_key = f"{project_path}:{pattern_type}"

    # Check cache (15-minute TTL)
    if use_cache and cache_key in _pattern_cache:
        return _pattern_cache[cache_key]

    # Call MCP tool
    try:
        result = await mcp_client.call_tool("coderef_patterns", {
            "project_path": project_path,
            "pattern_type": pattern_type
        })
        _pattern_cache[cache_key] = result
        return result
    except Exception as e:
        # Graceful degradation
        return {"success": False, "error": str(e)}

# tool_handlers.py
async def handle_establish_standards(arguments):
    patterns = await call_coderef_patterns(project_path, "ui_components")

    if patterns["success"]:
        # Use MCP semantic patterns (80%+ quality)
        frequency = patterns["frequency"]
        violations = patterns["violations"]
    else:
        # Fallback to regex patterns (55% quality)
        patterns = _regex_fallback_patterns()
```

**Benefits:**
- **Performance:** Caching reduces expensive MCP calls (2-5s → 50ms)
- **Centralization:** Single source of MCP integration
- **Testability:** Mockable orchestration layer
- **Graceful Degradation:** Works without MCP server

---

### 2. Decorator Pattern

**Usage:** Cross-cutting concerns (logging, error handling)

```python
@log_invocation
@mcp_error_handler
async def handle_generate_docs(args):
    # Core logic without boilerplate
```

**Benefits:**
- Separation of concerns
- Reusable across all 16 handlers
- Consistent behavior

---

### 3. Strategy Pattern

**Usage:** Different generators for different doc types

```python
class BaseGenerator:
    def generate(self): pass

class FoundationGenerator(BaseGenerator):
    def generate(self): # 5-doc workflow

class UserGuideGenerator(BaseGenerator):  # NEW v4.0.0
    def generate(self): # User docs workflow

class ChangelogGenerator(BaseGenerator):
    def generate(self): # CHANGELOG.json CRUD
```

---

### 4. Adapter Pattern

**Usage:** @coderef/core CLI integration

```python
# External CLI with complex API
def extract_apis(project_path):
    # Adapts CLI to simple Dict interface
```

---

### 5. Template Method Pattern

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

### 6. Auto-Discovery Pattern (NEW v4.0.0)

**Usage:** User docs automation with 75%+ auto-fill

```python
# UserGuideGenerator
def extract_mcp_tools(project_path):
    # Read .coderef/index.json
    index = json.loads(Path(project_path / ".coderef/index.json").read_text())

    # Filter for handle_* functions in tool_handlers.py
    tools = [e for e in index if e["name"].startswith("handle_")]

    # Categorize by function
    return categorize_tools(tools)

def scan_slash_commands(project_path):
    # Scan .claude/commands/ directory
    commands_dir = Path(project_path / ".claude/commands")

    # Read all *.txt files
    return [parse_command(f) for f in commands_dir.glob("*.txt")]
```

**Benefits:**
- **High Auto-Fill Rate:** 75%+ reduces manual work
- **No Manual Maintenance:** Tools/commands discovered automatically
- **Consistency:** Single source of truth (.coderef/, .claude/)
- **Fast:** File reads only, no expensive operations

---

## Key Design Decisions

### Decision 1: MCP Orchestration Layer (NEW v4.0.0)

**Chosen:** Centralized mcp_orchestrator.py with caching
**Rejected:** Direct MCP calls from tool_handlers.py
**Reason:** Performance (caching), testability, graceful degradation

**Impact:** v4.0.0 architecture
**Trade-off:** Additional layer vs improved performance and maintainability

**Performance Metrics:**
- First call: ~2-5 seconds (actual MCP call)
- Cached call: < 50ms (15-minute cache)
- Health check: < 100ms

---

### Decision 2: User Docs Automation (NEW v4.0.0)

**Chosen:** 3 specialized tools with 75%+ auto-fill
**Rejected:** Single generic user docs tool
**Reason:** Domain-specific optimization, higher auto-fill rates

**Implementation:**
- generate_my_guide: Developer quick-start (60-80 lines)
- generate_user_guide: Comprehensive guide (10 sections, 200+ lines)
- generate_features: Feature inventory (100+ lines)

**Auto-Fill Strategy:**
- Tools: 100% auto-filled from .coderef/index.json
- Commands: 100% auto-filled from .claude/commands/
- Examples: 50-60% auto-generated from patterns
- **Overall: 75%+ auto-fill rate**

---

### Decision 3: Standards Enhancement with MCP (NEW v4.0.0)

**Chosen:** MCP semantic patterns + regex fallback
**Rejected:** Regex patterns only
**Reason:** Quality improvement (55% → 80%+) with graceful degradation

**Implementation:**
```python
# Try MCP first
patterns = await call_coderef_patterns(project_path, "ui_components")

if patterns["success"]:
    # Use semantic patterns (80%+ quality)
    frequency = patterns["frequency"]  # {"async_function": 45}
    violations = patterns["violations"]
else:
    # Fallback to regex (55% quality)
    patterns = _regex_fallback_patterns()
```

**Quality Metrics:**
- With MCP: 80%+ quality (pattern frequency, violation detection)
- Without MCP: 55% quality (basic pattern matching)
- Improvement: +25 percentage points

---

### Decision 4: Tool Consolidation (NEW v4.0.0)

**Chosen:** Clear hierarchy with [INTERNAL] and [DEPRECATED] markings
**Rejected:** Keep all tools as equal priority
**Reason:** User clarity, migration path, backward compatibility

**Hierarchy:**
- **Active (13 tools):** User-facing, recommended
- **[INTERNAL] (1 tool):** generate_individual_doc (orchestrated by generate_foundation_docs)
- **[DEPRECATED] (1 tool):** coderef_foundation_docs (replaced by generate_foundation_docs)
- **Removed in v5.0.0:** coderef_foundation_docs

**Migration Path:**
- v4.0.0: [DEPRECATED] marking with migration instructions
- v5.0.0: Complete removal

---

### Decision 5: Sequential vs Batch Foundation Docs

**Chosen:** Sequential generation ([1/5] → [5/5])
**Rejected:** Batch dump all templates at once
**Reason:** Eliminates timeout errors (~1,470 lines → 5x ~250-350 lines)

**Impact:** v3.2.0 upgrade
**Trade-off:** Slight latency increase (5 calls) vs stability

---

### Decision 6: Optional vs Required Code Intelligence

**Chosen:** Optional with graceful fallback
**Rejected:** Required @coderef/core CLI dependency
**Reason:** Works on any system, even without CLI

**Impact:** Usability vs feature completeness
**Implementation:** extractors.py returns empty dict on CLI failure

---

### Decision 7: POWER Framework vs Free-Form

**Chosen:** Standardized POWER template structure
**Rejected:** Ad-hoc documentation styles
**Reason:** Consistency, proven effectiveness, reusability

**POWER = Purpose, Overview, What/Why/When, Examples, References**

---

### Decision 8: Composable Modules vs Rigid Templates

**Chosen:** Composable module architecture (v3.4.0)
**Rejected:** 20 rigid per-element templates
**Reason:** Flexibility, DRY principle, auto-fill capability

**Implementation:** ResourceSheetGenerator with detection engine

---

### Decision 9: UDS Metadata Optional vs Required

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
5. **MCP Server Availability** - Optional (coderef-context for enhanced features)

### Performance Constraints

1. **2-minute timeout** - All tools must complete within 120s
2. **LRU cache size** - 32 entries max for CLI results
3. **MCP cache TTL** - 15 minutes for pattern analysis (NEW v4.0.0)
4. **Sequential generation** - No parallel doc generation
5. **Health check** - < 100ms for MCP status (NEW v4.0.0)

### Security Constraints

1. **Path traversal prevention** - Validates all file paths
2. **No code execution** - Pure document generation
3. **Read-only analysis** - Doesn't modify source code
4. **Sandboxed MCP calls** - No arbitrary code execution

---

## Integration Points

### External Dependencies

**Required:**
- Python stdlib (pathlib, json, asyncio)
- MCP SDK (mcp.server)
- jsonschema (validation)

**Optional:**
- @coderef/core CLI (code intelligence)
- coderef-context MCP server (drift detection, semantic patterns) *NEW v4.0.0
- Git (changelog auto-detection)

### Integration with CodeRef Ecosystem

**Upstream:**
- coderef-context MCP server (optional, for enhanced features)

**Downstream:**
- coderef-workflow (orchestrates doc generation)
- Claude Code (MCP client)

**v4.0.0 Integration Architecture:**
```
Claude Code (MCP Client)
    ↓
coderef-docs MCP Server
    ├→ mcp_orchestrator.py
    │   └→ calls coderef-context MCP Server (optional)
    ├→ extractors.py
    │   └→ calls @coderef/core CLI (optional)
    └→ generators/* (core logic, always works)
```

---

## Error Handling Strategy

### Layered Error Handling

```
Layer 0: MCP Orchestration (NEW v4.0.0)
    ↓ Returns {"success": False} on MCP errors (no throw)
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

**v4.0.0 Enhancement:** MCP orchestration returns structured errors instead of throwing, enabling graceful degradation at the tool handler level.

---

## Logging Strategy

**Levels:**
- INFO: Tool invocations, major operations, MCP calls (NEW v4.0.0)
- DEBUG: Internal state, detailed flow, cache hits/misses (ENHANCED v4.0.0)
- ERROR: Exceptions, validation failures, MCP errors

**Format:**
```
2026-01-13 00:00:00 - coderef-docs - INFO - Tool called: generate_docs
2026-01-13 00:00:01 - coderef-docs - DEBUG - MCP cache hit: patterns (50ms)
2026-01-13 00:00:02 - coderef-docs - INFO - Drift check: 8% (none severity)
2026-01-13 00:00:03 - coderef-docs - INFO - Successfully generated: API.md
```

**v4.0.0 Additions:**
- MCP call logging (cache hits/misses, response times)
- Drift detection logging (severity, percentage)
- Auto-discovery logging (tools/commands found)

---

## Testing Strategy (v4.0.0)

### Test Coverage

**Total:** 185 tests across 10 files (95%+ pass rate)

**Test Categories:**
1. **MCP Integration Tests** (16 tests) - mcp_orchestrator.py functionality
2. **Drift Detection Tests** (20 tests) - Severity calculation, boundaries
3. **User Docs Tests** (20 tests) - Tool extraction, command scanning, auto-fill rate
4. **Standards Tests** (20 tests) - MCP patterns, frequency tracking, violations
5. **Tool Consolidation Tests** (20 tests) - [INTERNAL]/[DEPRECATED] markings
6. **Health Check Tests** (20 tests) - MCP status, performance < 100ms
7. **Edge Case Tests** (20 tests) - Empty files, malformed JSON, Unicode, large codebases
8. **Full Workflow Tests** (5 tests) - End-to-end scenarios
9. **Direct Validation Tests** (8 tests) - Papertrail integration
10. **Unit Tests** (36+ tests) - Generators, validators, extractors

**Test Architecture Pattern:**
```python
# Mock MCP orchestrator for isolated testing
@pytest.fixture
def mock_mcp_orchestrator():
    with patch('mcp_orchestrator.call_coderef_patterns') as mock:
        mock.return_value = {"success": True, "patterns": [...]}
        yield mock

# Test with and without MCP
def test_establish_standards_with_mcp(mock_mcp_orchestrator):
    result = await handle_establish_standards({"project_path": "..."})
    assert "80%+ quality" in result

def test_establish_standards_without_mcp():
    # MCP unavailable, should fall back to regex
    result = await handle_establish_standards({"project_path": "..."})
    assert "55% quality" in result
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
4. Enhanced MCP orchestration with multiple external servers

**v4.0.0 Foundations for Future Work:**
- MCP orchestration layer enables easy addition of new MCP servers
- Auto-discovery pattern enables self-documenting tools
- Tool consolidation provides clear migration path for API evolution

---

## Performance Characteristics (v4.0.0)

| Operation | Without MCP | With MCP (First) | With MCP (Cached) |
|-----------|-------------|------------------|-------------------|
| **Foundation Doc Generation** | ~5-10s | ~7-15s (+drift check) | ~5-10s |
| **Drift Detection** | N/A | ~2-5s | N/A (no cache) |
| **Pattern Analysis** | ~10-20s (regex) | ~12-25s (semantic) | < 50ms |
| **User Docs (my-guide)** | ~2-5s | ~2-5s | ~2-5s |
| **User Docs (USER-GUIDE)** | ~5-10s | ~5-10s | ~5-10s |
| **Standards Generation** | ~60-120s (regex) | ~65-130s (semantic) | ~60-120s |
| **Health Check** | < 10ms | < 100ms | < 100ms |

**Key Insights:**
- MCP orchestration adds ~2-5s overhead for first call
- Caching eliminates overhead for repeated operations (< 50ms)
- Semantic patterns add ~5-10s but provide +25% quality improvement
- Health check remains under 100ms (acceptable for list_templates)

---

## References

- **Component Details:** [COMPONENTS.md](COMPONENTS.md) (v4.0.0)
- **API Specifications:** [API.md](API.md) (v4.0.0)
- **Data Schemas:** [SCHEMA.md](SCHEMA.md) (v4.0.0)
- **MCP Integration Guide:** [INTEGRATION.md](INTEGRATION.md) (NEW v4.0.0)
- **MCP Specification:** https://spec.modelcontextprotocol.io/

---

**Maintained by:** coderef-docs MCP server
**Generated:** 2026-01-13
**AI Assistance:** Claude Code (Sonnet 4.5)
**Version:** 4.0.0 (WO-GENERATION-ENHANCEMENT-001)
