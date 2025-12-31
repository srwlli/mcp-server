# MCP Server Structure - Before & After

**Document Version:** 1.0.0
**Created:** 2025-12-31
**Purpose:** Visual comparison of current vs. new MCP server structure

---

## 1. coderef-context

### BEFORE (Current)
```
coderef-context/
├── server.py                 # 1073 lines - MONOLITHIC ❌
├── src/                      # Empty placeholder ❌
├── tests/                    # Local tests (should be global) ❌
│   ├── conftest.py
│   ├── test_tools.py
│   └── test_tools_integration.py
├── CLAUDE.md
├── README.md
└── pyproject.toml
```

### AFTER (New)
```
coderef-context/
├── server.py                 # 200-300 lines - MCP protocol only ✅
├── processors/               # NEW - Business logic ✅
│   ├── __init__.py
│   ├── scan_processor.py     # scan, validate, drift tools
│   ├── query_processor.py    # query, impact, complexity tools
│   ├── output_processor.py   # diagram, patterns, coverage tools
│   └── tag_processor.py      # tag tool
├── utils/                    # NEW - Shared utilities ✅
│   ├── __init__.py
│   ├── cli_runner.py         # Subprocess execution
│   ├── result_parser.py      # JSON parsing, error handling
│   └── cache_manager.py      # Optional caching layer
├── scripts/                  # NEW - Standalone tools ✅
│   ├── organize-scan.py      # Organize .coderef/ results
│   └── scan-and-cache.sh     # Wrapper scripts
├── CLAUDE.md
├── README.md
└── pyproject.toml
```

**Changes:**
- ❌ Delete `src/` (empty)
- ❌ Delete `tests/` (move to global `coderef/testing/`)
- ✅ Create `processors/` with 4 domain modules
- ✅ Create `utils/` for infrastructure
- ✅ Create `scripts/` for automation
- ✅ Refactor `server.py` to 200-300 lines (just routing)

---

## 2. coderef-docs

### BEFORE (Current)
```
coderef-docs/
├── server.py                 # 645 lines - Reasonable ✅
├── generators/               # 14 modules - GOOD ✅
│   ├── foundation_generator.py
│   ├── planning_generator.py
│   ├── changelog_generator.py
│   ├── quickref_generator.py
│   ├── standards_generator.py
│   └── ... (9 more)
├── templates/                # Template files ✅
│   └── power/
├── schemas/                  # Validation schemas ✅
├── extractors.py             # Root utility ⚠️
├── cli_utils.py              # Root utility ⚠️
├── constants.py              # Root constants ✅
├── handler_helpers.py        # Root handlers ⚠️
├── tests/                    # Local tests ❌
└── pyproject.toml
```

### AFTER (New)
```
coderef-docs/
├── server.py                 # 645 lines - Keep as-is ✅
├── generators/               # 14 modules - Keep as-is ✅
│   ├── foundation_generator.py
│   ├── planning_generator.py
│   ├── changelog_generator.py
│   ├── quickref_generator.py
│   ├── standards_generator.py
│   └── ... (9 more)
├── templates/                # Template files ✅
│   └── power/
├── schemas/                  # Validation schemas ✅
├── utils/                    # NEW - Move utilities here ✅
│   ├── __init__.py
│   ├── extractors.py         # Moved from root
│   ├── cli_utils.py          # Moved from root
│   └── handler_helpers.py    # Moved from root
├── constants.py              # Keep at root ✅
└── pyproject.toml
```

**Changes:**
- ❌ Delete `tests/` (move to global `coderef/testing/`)
- ✅ Create `utils/` directory
- ✅ Move `extractors.py` to `utils/`
- ✅ Move `cli_utils.py` to `utils/`
- ✅ Move `handler_helpers.py` to `utils/`

---

## 3. coderef-workflow

### BEFORE (Current)
```
coderef-workflow/
├── server.py                 # 1500+ lines - Large ⚠️
├── generators/               # 4 modules - GOOD ✅
│   ├── analysis_generator.py
│   ├── planning_generator.py
│   ├── deliverables_generator.py
│   └── agent_communication_generator.py
├── templates/                # Template files ✅
├── docs/                     # Documentation ✅
├── constants.py              # Root constants ✅
├── handler_helpers.py        # Root handlers ⚠️
├── plan_format_validator.py  # Root validator ⚠️
├── tests/                    # Local tests ❌
└── pyproject.toml
```

### AFTER (New)
```
coderef-workflow/
├── server.py                 # 400-500 lines - Slimmed down ✅
├── generators/               # 4 modules - Keep as-is ✅
│   ├── analysis_generator.py
│   ├── planning_generator.py
│   ├── deliverables_generator.py
│   └── agent_communication_generator.py
├── processors/               # NEW - Extract from server.py ✅
│   ├── __init__.py
│   ├── workorder_processor.py    # Workorder operations
│   ├── plan_processor.py         # Plan CRUD operations
│   └── agent_processor.py        # Multi-agent coordination
├── templates/                # Template files ✅
├── docs/                     # Documentation ✅
├── utils/                    # NEW - Utilities ✅
│   ├── __init__.py
│   ├── handler_helpers.py    # Moved from root
│   └── plan_format_validator.py  # Moved from root
├── constants.py              # Keep at root ✅
└── pyproject.toml
```

**Changes:**
- ❌ Delete `tests/` (move to global `coderef/testing/`)
- ✅ Create `processors/` with 3 domain modules
- ✅ Create `utils/` directory
- ✅ Move `handler_helpers.py` to `utils/`
- ✅ Move `plan_format_validator.py` to `utils/`
- ✅ Extract logic from `server.py` to `processors/`

---

## 4. coderef-personas

### BEFORE (Current)
```
coderef-personas/
├── server.py                 # 800 lines - Reasonable ⚠️
├── personas/                 # Domain organization ✅
│   └── base/                 # 9 persona JSON files
├── src/                      # Empty placeholder ❌
├── templates/                # Template files ✅
├── tests/                    # Local tests ❌
└── pyproject.toml
```

### AFTER (New)
```
coderef-personas/
├── server.py                 # 300-400 lines - Slimmed down ✅
├── personas/                 # Domain organization ✅
│   └── base/                 # 9 persona JSON files
├── processors/               # NEW - Business logic ✅
│   ├── __init__.py
│   ├── persona_manager.py    # Load, validate, activate personas
│   └── custom_persona_creator.py  # Custom persona workflow
├── templates/                # Template files ✅
├── utils/                    # NEW - Utilities ✅
│   ├── __init__.py
│   └── template_renderer.py  # Template rendering logic
└── pyproject.toml
```

**Changes:**
- ❌ Delete `src/` (empty)
- ❌ Delete `tests/` (move to global `coderef/testing/`)
- ✅ Create `processors/` with 2 domain modules
- ✅ Create `utils/` directory
- ✅ Extract logic from `server.py`

---

## 5. coderef-testing

### BEFORE (Current)
```
coderef-testing/
├── server.py                 # 700 lines - Monolithic ❌
├── src/                      # Empty placeholder ❌
├── personas/                 # Misplaced (copy/paste?) ❌
├── tests/                    # Local tests ❌
└── pyproject.toml
```

### AFTER (New)
```
coderef-testing/
├── server.py                 # 200-300 lines - MCP protocol only ✅
├── runners/                  # NEW - Test execution ✅
│   ├── __init__.py
│   ├── pytest_runner.py      # Pytest integration
│   ├── coverage_runner.py    # Coverage analysis
│   └── test_discovery.py     # Test file discovery
├── utils/                    # NEW - Shared utilities ✅
│   ├── __init__.py
│   ├── result_parser.py      # Parse test output
│   └── report_generator.py   # Generate reports
├── scripts/                  # NEW - Standalone tools ✅
│   └── run-tests.sh          # Wrapper scripts
└── pyproject.toml
```

**Changes:**
- ❌ Delete `src/` (empty)
- ❌ Delete `personas/` (misplaced)
- ❌ Delete `tests/` (move to global `coderef/testing/`)
- ✅ Create `runners/` with 3 modules
- ✅ Create `utils/` with 2 modules
- ✅ Create `scripts/` for automation
- ✅ Refactor `server.py` to 200-300 lines

---

## Summary of Changes

### Common Pattern (All Servers)

**Delete:**
- ❌ Empty `src/` directories
- ❌ Local `tests/` directories (move to `coderef/testing/`)
- ❌ Misplaced directories (e.g., `personas/` in coderef-testing)

**Create:**
- ✅ `processors/` or `generators/` - Domain-specific business logic
- ✅ `utils/` - Shared infrastructure and utilities
- ✅ `scripts/` (optional) - Standalone CLI tools

**Move:**
- ✅ Root-level utilities → `utils/` directory
- ✅ Business logic from `server.py` → `processors/`

**Keep:**
- ✅ `constants.py`, `type_defs.py` at root (acceptable)
- ✅ `templates/`, `schemas/`, `docs/` directories
- ✅ `server.py` (but slim it down to 200-500 lines)

### File Count Comparison

| Server | Before | After | Change |
|--------|--------|-------|--------|
| coderef-context | 3 files/dirs | 3 dirs + modules | +processors, +utils, +scripts |
| coderef-docs | Utilities at root | Organized in utils/ | Cleaner |
| coderef-workflow | Large server.py | Extracted processors/ | Better separation |
| coderef-personas | 800-line server | Extracted processors/ | Cleaner |
| coderef-testing | Monolithic | runners/ + utils/ | Much better |

---

## Global Testing Structure

### NEW: coderef/testing/

```
coderef/testing/
├── coderef-context/          # Tests for coderef-context
│   ├── test_scan_processor.py
│   ├── test_query_processor.py
│   └── test_cli_runner.py
├── coderef-docs/             # Tests for coderef-docs
│   ├── test_foundation_generator.py
│   └── test_changelog_generator.py
├── coderef-workflow/         # Tests for coderef-workflow
│   ├── test_planning_generator.py
│   └── test_workorder_processor.py
├── coderef-personas/         # Tests for coderef-personas
│   └── test_persona_manager.py
├── coderef-testing/          # Tests for coderef-testing
│   ├── test_pytest_runner.py
│   └── test_coverage_runner.py
├── conftest.py               # Shared fixtures
└── pytest.ini                # Global pytest config
```

**Benefits:**
- ✅ Single test suite for entire ecosystem
- ✅ Shared fixtures and utilities
- ✅ Consistent test reporting
- ✅ Easier CI/CD integration

---

**Status:** Structure designed, ready for implementation
