# Explicit Context Enforcement System

**Version:** 2.0.0
**Date:** 2026-01-10
**Philosophy:** Explicits over heuristics - no guessing allowed

---

## Problem Solved

**Before:** Planning workflow guessed entry points, architecture patterns, and component relationships when documentation was missing.

**After:** Planning workflow FAILS FAST and demands explicit documentation before proceeding.

---

## The 4-Layer Enforcement System

### **Layer 1: Structured Foundation Docs (REQUIRED)**

ARCHITECTURE.md must have machine-readable METADATA section:

```markdown
# Architecture Reference

---
## METADATA (Required for Planning Validation)

**Entry Point:** server.py
**Main Components:** PlanningAnalyzer, PlanGenerator, WorkorderValidator
**Architecture Pattern:** MCP Server
**Framework:** Python + MCP Protocol
**Primary Language:** Python
---
```

**Why structured?**
- Machine-parseable (regex: `\*\*Entry Point:\*\* (\w+)`)
- Validation can check if field exists
- Zero ambiguity - no free-text guessing

---

### **Layer 2: Pre-Planning Validation (ENFORCED)**

Before /create-workorder starts, validation checks:

```python
await analyzer.validate_planning_prerequisites()
```

**Returns:**
```json
{
  "critical": [
    {
      "check": "Documented entry point",
      "message": "Entry point not documented in ARCHITECTURE.md",
      "fix": "Add to ARCHITECTURE.md: 'Entry point: server.py'",
      "reason": "Heuristic guessing is unreliable - document explicitly"
    }
  ],
  "warnings": [...],
  "passed": [...],
  "can_proceed": false  // ← BLOCKS PLANNING
}
```

**Critical issues = STOP:**
- Missing .coderef/ directory
- Missing ARCHITECTURE.md
- Missing entry point documentation

**Warnings = CONTINUE with notice:**
- Missing patterns.json
- Stale .coderef/ data (>10% drift)
- Missing README.md

---

### **Layer 3: Validation Checks**

#### **Check 1: .coderef/ Exists**
```python
if not check_coderef_available(str(self.project_path)):
    CRITICAL: "Run: coderef scan /path/to/project"
```

**Why critical:** No code intelligence = degraded planning

#### **Check 2: .coderef/ is Fresh**
```python
drift = self.check_coderef_freshness()
if drift > 10%:
    WARNING: "Re-run scan - 10+ files changed since last scan"
```

**Why warning:** Stale data leads to incorrect analysis

#### **Check 3: Foundation Docs Exist**
```python
if 'ARCHITECTURE.md' not in available_docs:
    CRITICAL: "Run: /generate-docs"
```

**Why critical:** Entry points and patterns must be documented

#### **Check 4: Entry Point is Documented**
```python
entry_point = self._extract_entry_point_from_docs()
if not entry_point:
    CRITICAL: "Add 'Entry point: X' to ARCHITECTURE.md"
```

**Why critical:** No guessing server/app/main - must be explicit

#### **Check 5: Coding Patterns Available**
```python
patterns = read_coderef_output('patterns')
if not patterns:
    WARNING: "Run full scan for pattern detection"
```

**Why warning:** Improves plan quality but not blocking

---

### **Layer 4: /create-workorder Integration**

```python
# Step 0: Validate prerequisites (NEW - BLOCKING)
validation = await analyzer.validate_planning_prerequisites()

if not validation['can_proceed']:
    print("❌ Cannot create plan - missing required explicit context:\n")
    for issue in validation['critical']:
        print(f"  • {issue['message']}")
        print(f"    Fix: {issue['fix']}\n")
    print("The CodeRef system requires explicit documentation, not heuristics.")
    print("Please fix the above issues and retry /create-workorder")
    return  # STOP HERE - no planning allowed

# If warnings, show them but continue
if validation['warnings']:
    print("⚠️  Planning with degraded context:\n")
    for warning in validation['warnings']:
        print(f"  • {warning['message']}")
        print(f"    Recommended: {warning['fix']}\n")

# Proceed with planning only if explicits exist
gather_context(...)
analyze_project(...)
create_plan(...)
```

---

## Example: Full Validation Flow

### **Scenario: New Project**

```bash
$ /create-workorder

# Validation runs...

❌ Cannot create plan - missing required explicit context:

  • .coderef/ directory not found
    Fix: Run: coderef scan /path/to/project

  • ARCHITECTURE.md not found
    Fix: Run: /generate-docs or manually create foundation docs

  • Entry point not documented in ARCHITECTURE.md
    Fix: Add to ARCHITECTURE.md: "Entry point: server.py"

The CodeRef system requires explicit documentation, not heuristics.
Please fix the above issues and retry /create-workorder
```

### **User fixes issues:**

```bash
$ coderef scan .
$ /generate-docs
# Edit ARCHITECTURE.md, add: **Entry Point:** server.py

$ /create-workorder

✅ Planning Prerequisites Validated

Passed checks:
  + .coderef/ directory exists
  + .coderef/ data is fresh
  + ARCHITECTURE.md exists
  + README.md exists
  + Entry point documented: server

⚠️  Planning with degraded context:

  • No coding patterns found in .coderef/reports/patterns.json
    Recommended: Run: python scripts/populate-coderef.py /path/to/project

Proceeding with planning...
```

---

## Benefits

**1. Zero Guessing**
- No hardcoded `target_element = "main"`
- No heuristic fallbacks (server, app, index)
- Documented knowledge only

**2. Quality Gate**
- Forces teams to document architecture
- Prevents planning with incomplete context
- Ensures .coderef/ is up-to-date

**3. Clear Errors**
- Tells you exactly what's missing
- Provides exact command to fix
- Explains why it's required

**4. Gradual Improvement**
- Critical issues block planning
- Warnings allow planning but notify
- Easy migration path for existing projects

---

## Migration Guide

### **For Existing Projects:**

1. **Run scan:**
   ```bash
   coderef scan /path/to/project
   ```

2. **Generate foundation docs:**
   ```bash
   /generate-docs
   ```

3. **Add METADATA section to ARCHITECTURE.md:**
   ```markdown
   ## METADATA (Required for Planning Validation)

   **Entry Point:** <your-main-file>
   **Main Components:** <Component1>, <Component2>, <Component3>
   **Architecture Pattern:** <MCP Server|REST API|CLI Tool>
   ```

4. **Retry planning:**
   ```bash
   /create-workorder
   ```

### **For New Projects:**

1. **Scan first:**
   ```bash
   coderef scan /path/to/project
   ```

2. **Generate structured docs:**
   ```bash
   /generate-docs --template explicit
   ```

3. **Plan with explicit context:**
   ```bash
   /create-workorder
   ```

---

## Files Modified

1. **planning_analyzer.py**
   - Added `validate_planning_prerequisites()` (98 lines)
   - Added `_extract_entry_point_from_docs()` (52 lines, supports structured METADATA)
   - Added `_select_analysis_target()` (uses documented entry point first)

2. **ARCHITECTURE-TEMPLATE-EXPLICIT.md** (NEW)
   - Structured template with required METADATA section
   - Machine-parseable fields
   - Validation-friendly format

---

## Next Steps

1. ✅ Validation system implemented
2. ⏳ Integrate into /create-workorder slash command
3. ⏳ Update /generate-docs to use EXPLICIT template
4. ⏳ Migration guide for existing 5 MCP servers
5. ⏳ Test with real planning workflow

---

**The Rule:** If you can't extract it explicitly, you can't plan with it.

**The Goal:** 100% documented context, 0% heuristic guessing.
