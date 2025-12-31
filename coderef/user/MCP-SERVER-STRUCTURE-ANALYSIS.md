# MCP Server Structure Analysis - Separation of Concerns

**Document Version:** 1.0.0
**Created:** 2025-12-31
**Purpose:** Analyze current MCP server file organization and recommend structure improvements
**Status:** Analysis Complete

---

## Executive Summary

**Problem:** Inconsistent separation of concerns across the 5 MCP servers. Some servers have clean module separation (coderef-docs, coderef-workflow), while others are monolithic (coderef-context, coderef-personas, coderef-testing).

**Impact:**
- Hard to maintain and test individual components
- Code reuse is difficult
- Server.py files become bloated (coderef-context: 1073 lines, coderef-workflow: 1500+ lines)
- No clear pattern for where new functionality should live

**Recommendation:** Adopt the **coderef-docs pattern** as the ecosystem standard - clean separation with `generators/`, `utils/`, and domain-specific modules at root level.

---

## Current State Analysis

### 1. coderef-context (Simplest - Needs Structure)

**Current Structure:**
```
coderef-context/
├── server.py                 # 1073 lines - MONOLITHIC
├── src/                      # Empty placeholder
├── tests/                    # Local tests (should move to coderef/testing/)
│   ├── conftest.py
│   ├── test_tools.py
│   └── test_tools_integration.py
└── docs/                     # Documentation files only
```

**Problems:**
- ❌ All 11 MCP tool handlers crammed into server.py (1073 lines)
- ❌ No module separation - scan, query, impact, complexity all mixed together
- ❌ No utility layer for shared functions (CLI command building, output parsing)
- ❌ Empty `src/` directory (dead placeholder)
- ❌ Tests in local directory instead of global `coderef/testing/`

**What It Should Be:**
```
coderef-context/
├── server.py                 # MCP server only (~200 lines)
├── processors/               # NEW - Processing logic
│   ├── __init__.py
│   ├── scan_processor.py     # Scan, validate, drift
│   ├── query_processor.py    # Query, impact, complexity
│   ├── output_processor.py   # Diagram, patterns, coverage
│   └── tag_processor.py      # Tag management
├── utils/                    # NEW - Shared utilities
│   ├── __init__.py
│   ├── cli_runner.py         # Subprocess execution
│   ├── result_parser.py      # JSON parsing, error handling
│   └── cache_manager.py      # Result caching
└── scripts/                  # NEW - Standalone tools
    ├── organize-scan.py      # Organize .coderef/ results
    └── scan-and-cache.sh     # Wrapper scripts
```

**Separation of Concerns:**
- **server.py**: MCP protocol only (tool registration, request routing)
- **processors/**: Business logic for each tool domain
- **utils/**: Shared infrastructure (CLI execution, parsing, caching)
- **scripts/**: Standalone automation tools

---

### 2. coderef-docs (BEST - Reference Pattern)

**Current Structure:**
```
coderef-docs/
├── server.py                 # 645 lines - MCP server only
├── generators/               # 14 modules - CLEAN SEPARATION
│   ├── foundation_generator.py
│   ├── planning_generator.py
│   ├── changelog_generator.py
│   ├── quickref_generator.py
│   ├── standards_generator.py
│   └── ... (9 more)
├── templates/                # Template files
│   └── power/
├── schemas/                  # Validation schemas
├── utils/                    # Empty (could be used)
├── extractors.py             # Root utility
├── cli_utils.py              # Root utility
├── constants.py              # Root constants
├── handler_helpers.py        # Root handlers
└── tests/                    # Local tests (should move)
```

**Strengths:**
- ✅ Clear domain separation in `generators/` (14 focused modules)
- ✅ Template organization in `templates/power/`
- ✅ Utility functions extracted to root modules (extractors.py, cli_utils.py)
- ✅ Constants centralized (constants.py)
- ✅ Server.py focused on MCP protocol (645 lines is reasonable for 26 tools)

**Minor Issues:**
- ⚠️ Utilities at root level (extractors.py, cli_utils.py) - could move to `utils/`
- ⚠️ Tests in local directory instead of `coderef/testing/`

**This is the GOLD STANDARD pattern** - other servers should follow this.

---

### 3. coderef-workflow (Good - Similar to coderef-docs)

**Current Structure:**
```
coderef-workflow/
├── server.py                 # 1500+ lines - Could be cleaner
├── generators/               # CLEAN SEPARATION
│   ├── analysis_generator.py
│   ├── planning_generator.py
│   ├── deliverables_generator.py
│   └── agent_communication_generator.py
├── templates/                # Template files
├── docs/                     # Documentation
├── constants.py              # Root constants
├── handler_helpers.py        # Root handlers
├── plan_format_validator.py  # Root validator
└── tests/                    # Local tests (should move)
```

**Strengths:**
- ✅ Generator separation (4 focused modules)
- ✅ Constants centralized
- ✅ Domain logic extracted from server.py

**Issues:**
- ⚠️ Server.py still large (1500+ lines for 26 tools)
- ⚠️ Could extract more utilities to dedicated modules
- ⚠️ Tests in local directory

---

### 4. coderef-personas (Decent - Domain Focused)

**Current Structure:**
```
coderef-personas/
├── server.py                 # 800 lines - Reasonable
├── personas/                 # Domain organization
│   └── base/                 # 9 persona JSON files
├── src/                      # Empty placeholder
├── templates/                # Template files
└── tests/                    # Local tests (should move)
```

**Strengths:**
- ✅ Domain-focused organization (personas/)
- ✅ Simple server (only 4 tools)

**Issues:**
- ⚠️ All logic in server.py (could extract persona_manager.py)
- ⚠️ Empty `src/` directory
- ⚠️ No utilities module for shared functions

---

### 5. coderef-testing (Simple - Needs Structure)

**Current Structure:**
```
coderef-testing/
├── server.py                 # 700 lines - Monolithic
├── src/                      # Empty placeholder
├── personas/                 # Inherited (not used?)
└── tests/                    # Local tests (should move)
```

**Problems:**
- ❌ All test execution logic in server.py
- ❌ No separation between pytest integration, coverage analysis, reporting
- ❌ Empty `src/` directory
- ❌ `personas/` directory seems misplaced (copy/paste from coderef-personas?)

**What It Should Be:**
```
coderef-testing/
├── server.py                 # MCP server only (~200 lines)
├── runners/                  # NEW - Test execution
│   ├── __init__.py
│   ├── pytest_runner.py      # Pytest integration
│   ├── coverage_runner.py    # Coverage analysis
│   └── test_discovery.py     # Test file discovery
├── utils/                    # NEW - Shared utilities
│   ├── __init__.py
│   ├── result_parser.py      # Parse test output
│   └── report_generator.py   # Generate reports
└── scripts/                  # NEW - Standalone tools
    └── run-tests.sh          # Wrapper scripts
```

---

## Recommended Standard Structure

Based on the analysis, here's the **recommended structure for all MCP servers**:

```
{server-name}/
├── server.py                 # MCP server ONLY (200-300 lines)
│   # Responsibilities:
│   # - Tool registration
│   # - Request routing to processors
│   # - Error handling at MCP protocol level
│   # - NO business logic
│
├── processors/               # Business logic (primary modules)
│   ├── __init__.py
│   ├── {domain}_processor.py
│   └── ... (one per domain)
│   # Responsibilities:
│   # - Tool-specific business logic
│   # - Orchestration of utilities
│   # - Data transformation
│
├── generators/               # (if server generates artifacts)
│   ├── __init__.py
│   └── {artifact}_generator.py
│   # Responsibilities:
│   # - Document/artifact generation
│   # - Template rendering
│   # - Output formatting
│
├── utils/                    # Shared infrastructure
│   ├── __init__.py
│   ├── cli_runner.py         # Subprocess execution
│   ├── result_parser.py      # Parsing logic
│   └── cache_manager.py      # Caching (if needed)
│   # Responsibilities:
│   # - Reusable functions
│   # - Infrastructure code
│   # - No domain logic
│
├── scripts/                  # Standalone CLI tools
│   └── {task}.py
│   # Responsibilities:
│   # - Direct execution (python scripts/task.py)
│   # - Wrapper scripts (bash/sh)
│   # - Automation tools
│
├── templates/                # Template files (if applicable)
│   └── {category}/
│
├── schemas/                  # Validation schemas (if applicable)
│   └── {schema}.json
│
├── constants.py              # Constants (at root is fine)
├── type_defs.py              # Type definitions (at root is fine)
└── pyproject.toml            # Package config
```

**DO NOT HAVE:**
- ❌ `src/` directory (if empty, delete it)
- ❌ Local `tests/` directory (use global `coderef/testing/`)
- ❌ Duplicate directories from copy/paste (e.g., personas/ in coderef-testing)

---

## Key Principles

### 1. Server.py Should Be Thin
**Target:** 200-300 lines (max 500 for complex servers)

**Only Contains:**
- MCP protocol setup
- Tool registration
- Request routing to processors
- Error handling at protocol level

**Example:**
```python
# server.py (GOOD)
@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "coderef_scan":
        from processors.scan_processor import handle_scan
        return await handle_scan(arguments)
    # ... route to other processors
```

**Anti-pattern:**
```python
# server.py (BAD)
@server.call_tool()
async def handle_call_tool(name: str, arguments: dict):
    if name == "coderef_scan":
        # 200 lines of business logic here... ❌
```

### 2. Processors = Business Logic
One processor per domain or tool group.

**coderef-context example:**
- `scan_processor.py` - scan, validate, drift
- `query_processor.py` - query, impact, complexity
- `output_processor.py` - diagram, patterns, coverage

**coderef-docs example:**
- `foundation_generator.py` - README, ARCHITECTURE, SCHEMA
- `changelog_generator.py` - CHANGELOG operations
- `quickref_generator.py` - Quickref guides

### 3. Utils = Infrastructure
No domain knowledge. Pure utility functions.

**Examples:**
- `cli_runner.py` - Execute subprocess commands
- `result_parser.py` - Parse JSON, handle errors
- `cache_manager.py` - Read/write cache files
- `file_utils.py` - File I/O operations

### 4. Scripts = Automation
Directly executable tools for manual or CI/CD use.

**Examples:**
- `organize-scan.py` - Copy .coderef/ results to coderef/scans/
- `run-tests.sh` - Wrapper for pytest execution
- `generate-docs.py` - Batch documentation generation

### 5. Tests = Global Location
All tests go in `coderef/testing/`, not local `tests/` directories.

**Reasoning:**
- Single test suite for entire ecosystem
- Shared fixtures and utilities
- Consistent test reporting
- Easier CI/CD integration

---

## Migration Path

### Phase 1: coderef-context (Highest Priority)
1. Create `processors/` directory
2. Extract scan/query/impact logic from server.py
3. Create `utils/` for CLI execution
4. Move tests to `coderef/testing/`
5. Delete empty `src/` directory

### Phase 2: coderef-testing
1. Create `runners/` directory
2. Extract pytest/coverage logic
3. Create `utils/` for result parsing
4. Remove misplaced `personas/` directory
5. Move tests to `coderef/testing/`

### Phase 3: coderef-workflow
1. Audit server.py (1500+ lines)
2. Extract more utilities to dedicated modules
3. Move tests to `coderef/testing/`

### Phase 4: coderef-personas
1. Extract persona management to `processors/persona_manager.py`
2. Create `utils/` for template rendering
3. Delete empty `src/` directory

### Phase 5: coderef-docs (Minimal - Already Good)
1. Move extractors.py, cli_utils.py to `utils/`
2. Move tests to `coderef/testing/`

---

## Benefits of This Structure

### For Developers
- ✅ Easy to find code (domain-based organization)
- ✅ Easy to test individual components
- ✅ Easy to reuse utilities across servers
- ✅ Smaller, focused files (200-300 lines vs 1000+)

### For AI Agents
- ✅ Clear separation makes it easier to understand responsibilities
- ✅ Can read individual processors without loading entire server
- ✅ Can modify one domain without affecting others
- ✅ Easier to generate new processors using templates

### For Maintenance
- ✅ Changes isolated to specific modules
- ✅ Testing is easier (unit test processors independently)
- ✅ Debugging is easier (clear call path: server → processor → utils)
- ✅ Refactoring is safer (clear boundaries)

---

## Comparison: Before vs After

### Before (coderef-context)
```
coderef-context/
├── server.py                 # 1073 lines ❌
├── src/                      # Empty ❌
└── tests/                    # Wrong location ❌
```

**Problems:**
- Monolithic server.py
- No module separation
- Hard to test
- Hard to extend

### After (coderef-context)
```
coderef-context/
├── server.py                 # 200 lines ✅
├── processors/               # Domain logic ✅
│   ├── scan_processor.py
│   ├── query_processor.py
│   └── output_processor.py
├── utils/                    # Shared code ✅
│   ├── cli_runner.py
│   └── result_parser.py
└── scripts/                  # Automation ✅
    └── organize-scan.py
```

**Benefits:**
- Clean separation
- Easy to test
- Easy to extend
- Follows ecosystem pattern

---

## Action Items

### Immediate (This Session)
1. ✅ Document current state (this file)
2. ⏳ Implement coderef-context refactor
3. ⏳ Create processors/ and utils/ structure
4. ⏳ Extract scan_processor.py from server.py

### Short Term (Next 1-2 Sessions)
1. Complete coderef-context refactor
2. Refactor coderef-testing (similar issues)
3. Update documentation with new patterns

### Long Term (Future)
1. Refactor remaining servers
2. Create server template generator
3. Establish coding standards document

---

## Conclusion

**Current State:** Inconsistent separation across 5 servers
**Target State:** Unified pattern based on coderef-docs structure
**Priority:** Start with coderef-context (most monolithic, highest value)

**Key Takeaway:** The `processors/` + `utils/` + `scripts/` pattern from coderef-docs should become the ecosystem standard. This provides:
- Clear responsibilities (MCP protocol vs business logic vs infrastructure)
- Easy testing (unit test processors independently)
- Better maintainability (smaller focused files)
- Consistent developer experience across all servers

---

**Document Status:** ✅ Complete
**Next Step:** Implement coderef-context refactor using this pattern
