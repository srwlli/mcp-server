# Phase 2: Integration Targets for visual_architecture Enhancement

**Session:** WO-SCANNER-CONTEXT-ENHANCEMENT-001
**Phase:** Phase 2 (Week 3-4)
**Status:** PLANNED (Phase 1 must complete first)
**Enhancement:** Leverage visual_architecture field now auto-included in coderef_context

---

## Context: What Changed in Phase 1

**Commit:** 69aafd0
**Date:** 2026-01-14
**Change:** `coderef_context` now auto-includes `visual_architecture` field

**Before:**
```json
{
  "success": true,
  "context": {
    "version": "2.0.0",
    "files": 12,
    "elements": 1752
  }
}
```

**After:**
```json
{
  "success": true,
  "context": {
    "version": "2.0.0",
    "files": 12,
    "elements": 1752
  },
  "visual_architecture": "# Dependency Diagram\n\n```mermaid\ngraph LR\n  ..." // 2,898 chars, 73 lines
}
```

**Benefit:** Eliminates need for separate `coderef_diagram` calls

---

## 🎯 Target 1: coderef-workflow - /create-workorder Planning

### Current State

**File:** `generators/planning_analyzer.py` line ~1343-1355

**Code:**
```python
# Current: Makes 2 separate MCP calls
context = await call_mcp_tool("coderef_context", {...})
diagram = await call_mcp_tool("coderef_diagram", {  # ← REDUNDANT CALL
    "project_path": project_path,
    "diagram_type": "dependencies",
    "format": "mermaid"
})
```

**Issue:**
- 2 MCP tool calls per workorder creation
- `coderef_diagram` now redundant since diagram included in context

### Proposed Change

**File:** `generators/planning_analyzer.py` line ~1343-1355

**New Code:**
```python
# Enhanced: Get everything in 1 call
context = await call_mcp_tool("coderef_context", {
    "project_path": project_path,
    "output_format": "json"
})

# Extract diagram from context response (no separate call needed)
visual_arch = context.get("visual_architecture", None)
if visual_arch:
    # Diagram available for planning prompt
    analysis["architecture_diagram"] = visual_arch
```

**Benefits:**
- ✅ 1 fewer MCP call per workorder (2 → 1)
- ✅ 50% reduction in tool calls
- ✅ Faster planning workflow
- ✅ Same diagram content, cleaner code

**Testing:**
1. Create test workorder with `/create-workorder`
2. Verify plan.json includes architecture context
3. Measure MCP call count (should be 1 for context, not 2)

---

## 📚 Target 2: coderef-docs - Foundation Docs (ARCHITECTURE.md)

### Current State

**File:** `generators/coderef_foundation_generator.py` line ~295-320

**Code:**
```python
# Current: Reads index.json manually
index_path = project_path / ".coderef/index.json"
if index_path.exists():
    with open(index_path) as f:
        index = json.load(f)
```

**Issue:**
- Manual file reading (not using MCP)
- No automatic diagram inclusion
- ARCHITECTURE.md missing visual component

### Proposed Change

**File:** `generators/coderef_foundation_generator.py` line ~295-320

**New Code:**
```python
# Enhanced: Use MCP to get complete context + diagram
try:
    context = await call_coderef_context(project_path)
    elements = context.get("context", {}).get("elements", 0)
    visual_arch = context.get("visual_architecture", None)
except Exception as e:
    # Fallback to manual file reading
    visual_arch = None
```

**Template Update:**
```python
# In ARCHITECTURE.md template
architecture_section = f"""
## Architecture Overview

{visual_arch if visual_arch else "Run `coderef scan` to generate architecture diagram"}

### Key Modules
...
"""
```

**Benefits:**
- ✅ Every ARCHITECTURE.md includes visual diagram automatically
- ✅ Single source of truth (MCP vs manual files)
- ✅ Diagrams always match latest scan
- ✅ Better developer onboarding

**Testing:**
1. Generate foundation docs with `generate_foundation_docs`
2. Verify ARCHITECTURE.md includes Mermaid diagram
3. Confirm diagram matches `.coderef/exports/diagram-wrapped.md`

---

## 📖 Target 3: coderef-docs - my-guide.md (Concise Reference)

### Current State

**File:** `generators/user_guide_generator.py` (generate_my_guide)

**Structure (60-80 lines):**
```markdown
# My Guide - {project_name}

## MCP Tools
- coderef_scan
- coderef_context
...

## Slash Commands
- /create-workorder
...

## Workflows
...
```

**Issue:**
- No visual architecture section
- Users don't see project structure at a glance

### Proposed Change

**File:** `generators/user_guide_generator.py` (generate_my_guide)

**New Structure:**
```markdown
# My Guide - {project_name}

## Architecture

{visual_architecture}

## MCP Tools
...

## Slash Commands
...

## Workflows
...
```

**Code:**
```python
def generate_my_guide(project_path: str) -> str:
    # Get architecture diagram
    context = await call_coderef_context(project_path)
    visual_arch = context.get("visual_architecture", "Run `coderef scan` first")

    return f"""
# My Guide - {project_name}

## Architecture

{visual_arch}

## MCP Tools
{tool_list}
...
"""
```

**Benefits:**
- ✅ Visual reference in concise guide
- ✅ Developers see structure immediately
- ✅ ~15 lines added (stays under 100 line target)

**Testing:**
1. Generate my-guide.md with `generate_my_guide`
2. Verify Architecture section appears before MCP Tools
3. Confirm diagram renders correctly

---

## 📘 Target 4: coderef-docs - USER-GUIDE.md (Comprehensive Guide)

### Current State

**File:** `generators/user_guide_generator.py` (generate_user_guide)

**Section 3: Architecture**
```markdown
## 3. Architecture

### Overview
The project follows a {architecture_pattern} architecture.

### Key Components
- Component 1
- Component 2
```

**Issue:**
- Text-only architecture description
- No visual component
- Harder to understand structure

### Proposed Change

**File:** `generators/user_guide_generator.py` (generate_user_guide)

**Enhanced Section 3:**
```markdown
## 3. Architecture

### Visual Overview

{visual_architecture}

### Architecture Pattern
The project follows a {architecture_pattern} architecture.

### Key Components
- Component 1
- Component 2

### Module Relationships
See diagram above for dependency relationships and data flow.
```

**Code:**
```python
def generate_user_guide(project_path: str) -> str:
    context = await call_coderef_context(project_path)
    visual_arch = context.get("visual_architecture", "")

    architecture_section = f"""
## 3. Architecture

### Visual Overview

{visual_arch}

### Architecture Pattern
...
"""
```

**Benefits:**
- ✅ Complete visual onboarding
- ✅ Users understand structure + relationships
- ✅ Reduces onboarding time

**Testing:**
1. Generate USER-GUIDE.md with `generate_user_guide`
2. Verify Section 3 includes visual diagram before text
3. Confirm 10-section structure maintained

---

## 🏗️ Target 5: coderef-docs - Standards Establishment

### Current State

**File:** `generators/standards_generator.py` line ~61-90

**Code:**
```python
# Current: Only uses code patterns
patterns = await call_coderef_patterns(project_path)
# Analyzes: handlers, decorators, naming conventions
```

**Issue:**
- No architectural context for pattern analysis
- Standards docs don't reference actual file structure
- Misses architectural patterns (layering, separation of concerns)

### Proposed Change

**File:** `generators/standards_generator.py` line ~61-90

**Enhanced Code:**
```python
# Enhanced: Get both code patterns + architectural context
patterns = await call_coderef_patterns(project_path)
context = await call_coderef_context(project_path)
visual_arch = context.get("visual_architecture", None)

# Analyze architectural patterns from diagram
arch_patterns = analyze_architectural_patterns(visual_arch)
# e.g., "Layered architecture with clear separation between handlers, services, models"
```

**Template Update:**
```markdown
# UI Standards

## Architectural Context

{visual_architecture}

### Component Organization
Based on the architecture diagram above, components follow this structure:
- Layer 1: Handlers (entry points)
- Layer 2: Services (business logic)
- Layer 3: Data access

## Code Patterns
...
```

**Benefits:**
- ✅ Standards align with real architecture
- ✅ Reference actual file structure
- ✅ Identify architectural patterns (not just code patterns)
- ✅ Better compliance (standards match reality)

**Testing:**
1. Run `establish_standards` with enhanced code
2. Verify standards docs include architectural context
3. Confirm standards reference actual file structure from diagram

---

## 📊 Summary: Changes Required

| Target | File | Function | Lines | Change Type | MCP Calls Saved |
|--------|------|----------|-------|-------------|-----------------|
| 1. Workflow Planning | `planning_analyzer.py` | `analyze_project_for_planning()` | ~1343-1355 | Remove redundant call | -1 |
| 2. Foundation Docs | `coderef_foundation_generator.py` | `_try_read_coderef_data()` | ~295-320 | Use MCP + embed diagram | 0 (adds call, but replaces file read) |
| 3. My Guide | `user_guide_generator.py` | `generate_my_guide()` | New section | Add Architecture section | 0 (already calls MCP) |
| 4. User Guide | `user_guide_generator.py` | `generate_user_guide()` | Section 3 | Enhance with visual | 0 (already calls MCP) |
| 5. Standards | `standards_generator.py` | `fetch_mcp_patterns()` | ~61-90 | Add architectural context | 0 (adds 1 call for context) |

**Total MCP Calls Saved:** 1 per planning workflow
**Total Enhancements:** 5 documentation workflows improved

---

## 🎁 Overall Benefits Summary

### Performance
- **Planning:** 2 MCP calls → 1 MCP call (50% reduction)
- **Docs Generation:** Same call count, but richer outputs
- **Standards:** +1 MCP call, but 2x better quality

### Consistency
- **Single source:** All workflows use same diagram from `coderef_context`
- **No drift:** Diagram always matches latest `.coderef/` scan
- **Reduced maintenance:** One place to update diagram logic

### Automation
- **ARCHITECTURE.md:** Diagram auto-included (no manual embedding)
- **my-guide.md:** Visual reference without extra effort
- **USER-GUIDE.md:** Complete onboarding automatically
- **Standards docs:** Architectural context included

### User Experience
- **Developers:** See structure immediately in all docs
- **Onboarding:** Visual aids speed up understanding
- **Agents:** Get architectural context in every planning workflow
- **Compliance:** Standards reference real architecture

---

## Implementation Order (Phase 2)

### Week 3: coderef-workflow Integration
1. **Day 1-2:** Modify `planning_analyzer.py` to eliminate `coderef_diagram` call
2. **Day 3:** Test planning workflow with enhanced context
3. **Day 4:** Measure MCP call reduction, validate plan.json quality

### Week 4: coderef-docs Integration
1. **Day 1:** Update `coderef_foundation_generator.py` for ARCHITECTURE.md
2. **Day 2:** Update `user_guide_generator.py` for my-guide.md and USER-GUIDE.md
3. **Day 3:** Update `standards_generator.py` for standards docs
4. **Day 4:** Integration testing across all 4 doc workflows
5. **Day 5:** Phase 2 validation and gate check

---

## Phase 2 Gate Check Criteria

Before proceeding to Phase 3:
- ✅ Workflow planning uses visual_architecture (1 MCP call, not 2)
- ✅ ARCHITECTURE.md includes diagram automatically
- ✅ my-guide.md has Architecture section with diagram
- ✅ USER-GUIDE.md Section 3 includes visual overview
- ✅ Standards docs reference architectural context
- ✅ Integration tests pass 95%+
- ✅ No regressions in existing workflows

---

## Testing Checklist

### coderef-workflow
- [ ] Run `/create-workorder` for test feature
- [ ] Verify only 1 MCP call to `coderef_context` (not 2)
- [ ] Confirm plan.json includes architecture context
- [ ] Validate planning speed improvement

### coderef-docs - Foundation Docs
- [ ] Run `generate_foundation_docs` for test project
- [ ] Verify ARCHITECTURE.md includes Mermaid diagram
- [ ] Confirm diagram matches `.coderef/exports/diagram-wrapped.md`
- [ ] Check API.md, README.md, COMPONENTS.md unchanged

### coderef-docs - User Docs
- [ ] Run `generate_my_guide` for test project
- [ ] Verify Architecture section appears before MCP Tools
- [ ] Confirm diagram renders correctly
- [ ] Validate guide stays under 100 lines
- [ ] Run `generate_user_guide` for test project
- [ ] Verify Section 3 includes visual overview
- [ ] Confirm 10-section structure maintained

### coderef-docs - Standards
- [ ] Run `establish_standards` for test project
- [ ] Verify standards docs include architectural context
- [ ] Confirm standards reference actual file structure
- [ ] Validate pattern quality improvement (55% → 80%)

---

**Status:** PLANNED (awaiting Phase 1 completion)
**Dependencies:** Phase 1 must achieve 95% context quality
**Estimated Effort:** 8-10 days (Week 3-4)
**Last Updated:** 2026-01-14
