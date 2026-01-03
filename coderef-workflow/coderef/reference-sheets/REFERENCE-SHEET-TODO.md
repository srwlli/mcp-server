# Reference Sheet TODO List

**Project:** coderef-workflow MCP Server
**Created:** 2026-01-02
**Status:** Planning Phase

---

## 🔴 High Priority (4 files - 8,285 LOC)

### 1. tool_handlers.py
- **Lines:** 4,404
- **Complexity:** 41 async functions (24+ MCP tools)
- **Purpose:** All MCP tool implementations
- **Reference Sheet:** `tool-handlers-reference.md`
- **Sections Needed:**
  - Tool name → handler function mapping table
  - Input validation requirements per tool
  - Return format examples
  - Error handling patterns
  - Common async patterns

### 2. generators/coderef_foundation_generator.py
- **Lines:** 1,683
- **Complexity:** Complex document generation logic
- **Purpose:** Generate ARCHITECTURE/SCHEMA/API/COMPONENTS docs
- **Reference Sheet:** `foundation-generator-reference.md`
- **Sections Needed:**
  - Template structure overview
  - Data extraction methods catalog
  - Output format specifications
  - .coderef/ integration points

### 3. handler_helpers.py
- **Lines:** 1,329
- **Complexity:** 24 helper functions
- **Purpose:** Shared utility functions across all handlers
- **Reference Sheet:** `handler-helpers-reference.md`
- **Sections Needed:**
  - Helper function catalog (name, signature, use case)
  - Common integration patterns
  - Usage examples per helper
  - When to use which helper

### 4. type_defs.py
- **Lines:** 829
- **Complexity:** 65 type definitions/classes
- **Purpose:** Type system for entire MCP server
- **Reference Sheet:** `type-defs-reference.md`
- **Sections Needed:**
  - Type hierarchy diagram
  - Required vs optional fields per type
  - Type usage examples
  - Common type combinations

---

## 🟡 Medium Priority (3 files - 2,816 LOC)

### 5. server.py
- **Lines:** 1,123
- **Complexity:** MCP server entry point, all tool registrations
- **Purpose:** Server initialization and tool routing
- **Reference Sheet:** `server-reference.md`
- **Sections Needed:**
  - Tool registration pattern
  - Server lifecycle hooks
  - Configuration options
  - Middleware/decorator patterns

### 6. generators/planning_analyzer.py
- **Lines:** 919
- **Complexity:** Project analysis with .coderef/ integration
- **Purpose:** Analyze projects for planning workflows
- **Reference Sheet:** `planning-analyzer-reference.md`
- **Sections Needed:**
  - Analysis methods catalog
  - .coderef/ integration patterns (v1.3.0)
  - Fallback strategies (3-tier system)
  - Drift detection workflow

### 7. validation.py
- **Lines:** 774
- **Complexity:** Input validation for 24+ tools
- **Purpose:** Centralized validation logic
- **Reference Sheet:** `validation-reference.md`
- **Sections Needed:**
  - Validator function catalog
  - Validation rules reference per tool
  - Error message formats
  - Custom validator creation guide

---

## 🟢 Lower Priority (3 files - 2,876 LOC)

### 8. generators/standards_generator.py
- **Lines:** 1,112
- **Purpose:** Standards establishment (/establish-standards)
- **Reference Sheet:** `standards-generator-reference.md`
- **Sections Needed:**
  - Standards format specification
  - Scanning patterns
  - UI/UX/behavior pattern detection

### 9. generators/audit_generator.py
- **Lines:** 916
- **Purpose:** Codebase auditing (/audit-codebase)
- **Reference Sheet:** `audit-generator-reference.md`
- **Sections Needed:**
  - Audit rules catalog
  - Severity level definitions
  - Violation detection methods

### 10. generators/risk_generator.py
- **Lines:** 848
- **Purpose:** Risk assessment (/assess-risk)
- **Reference Sheet:** `risk-generator-reference.md`
- **Sections Needed:**
  - Risk dimension definitions (5 dimensions)
  - Scoring algorithm explanation
  - Multi-option comparison format

---

## 📊 Summary Statistics

| Priority | Files | Total LOC | % of Codebase | Avg Functions/Types |
|----------|-------|-----------|---------------|---------------------|
| 🔴 High  | 4     | 8,285     | 35%           | 32                  |
| 🟡 Medium| 3     | 2,816     | 12%           | 15                  |
| 🟢 Low   | 3     | 2,876     | 12%           | Specialized         |
| **Total**| **10**| **13,977**| **59%**       | -                   |

**Total Codebase:** ~23,600 LOC (excluding .venv)

---

## 🎯 Implementation Strategy

### Phase 1: Core Infrastructure (High Priority)
1. `tool-handlers-reference.md` - Enable quick tool lookup
2. `type-defs-reference.md` - Define data contracts
3. `handler-helpers-reference.md` - Shared utilities guide
4. `foundation-generator-reference.md` - Doc generation

### Phase 2: Workflow Logic (Medium Priority)
5. `planning-analyzer-reference.md` - Planning workflow
6. `validation-reference.md` - Input validation
7. `server-reference.md` - Server architecture

### Phase 3: Specialized Generators (Lower Priority)
8. `standards-generator-reference.md`
9. `audit-generator-reference.md`
10. `risk-generator-reference.md`

---

## 📋 Template Structure (Standard Format)

Each reference sheet should follow this structure:

```markdown
# {Module Name} Reference Sheet

**File:** {file_path}
**Lines:** {line_count}
**Purpose:** {one_sentence_description}
**Last Updated:** {date}

---

## Quick Reference

{2-3 sentence overview}

---

## Function/Class Catalog

### {function_name}

**Signature:** `{full_signature}`
**Purpose:** {what_it_does}
**Parameters:**
- `param1` (type): description
- `param2` (type): description

**Returns:** {return_type_and_description}

**Example:**
```python
{code_example}
```

**Notes:**
- Important behavior detail
- Edge cases
- Related functions

---

## Common Patterns

### Pattern 1: {pattern_name}
{description_and_example}

---

## Integration Guide

{how_to_use_with_other_modules}

---

## Troubleshooting

{common_issues_and_solutions}
```

---

## 🚀 Next Steps

1. **Generate .coderef/ data** (optional, for accurate function inventory):
   ```bash
   python scripts/populate-coderef.py C:\Users\willh\.mcp-servers\coderef-workflow
   ```

2. **Start with Phase 1** (High Priority files)

3. **Use this checklist** to track progress:
   - [ ] tool-handlers-reference.md
   - [ ] type-defs-reference.md
   - [ ] handler-helpers-reference.md
   - [ ] foundation-generator-reference.md
   - [ ] planning-analyzer-reference.md
   - [ ] validation-reference.md
   - [ ] server-reference.md
   - [ ] standards-generator-reference.md
   - [ ] audit-generator-reference.md
   - [ ] risk-generator-reference.md

---

**Status:** 0/10 complete (0%)
**Estimated Effort:** 10-15 hours total (1-1.5 hours per sheet)
