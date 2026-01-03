# 🔴 URGENT: Agent Handoff - Phase 3B Required

**Agent:** coderef-system
**Workorder:** WO-RESOURCE-SHEET-MCP-TOOL-001 Phase 3B
**Priority:** HIGH
**Status:** BLOCKED - Waiting for your work
**Deadline:** Complete before Phase 4 testing

---

## Your Mission

You are the **coderef-system agent**. The resource sheet generator is 75% complete but **BLOCKED** waiting for you to integrate graph queries from coderef-context MCP.

**Current problem:** Auto-fill functions use regex parsing instead of dependency graph → only 50% auto-fill rate
**Your job:** Connect coderef_query MCP tools to auto-fill functions → achieve 60-80% auto-fill rate

---

## What You Must Do

### Task 1: GRAPH-001 - Enhance CodeAnalyzer

**File to modify:** `resource_sheet/detection/analyzer.py`

**Current implementation (BROKEN):**
```python
async def analyze_element(self, element_name, project_path, use_coderef_scan=True):
    # Just reads .coderef/index.json as flat JSON
    # Doesn't actually query the graph
```

**What you must change:**

1. **Import MCP tools at top of file:**
```python
# Add these imports
from mcp import mcp__coderef_context__coderef_query
from mcp import mcp__coderef_context__coderef_impact
```

2. **Add query methods to CodeAnalyzer class:**
```python
async def query_dependencies(self, element_name: str, project_path: str) -> list:
    """Query what this element depends on."""
    result = await mcp__coderef_context__coderef_query({
        "project_path": project_path,
        "query_type": "depends-on",
        "target": element_name
    })
    return result.get("dependencies", [])

async def query_callers(self, element_name: str, project_path: str) -> list:
    """Query what calls this element."""
    result = await mcp__coderef_context__coderef_query({
        "project_path": project_path,
        "query_type": "calls-me",
        "target": element_name
    })
    return result.get("callers", [])

async def query_imports(self, element_name: str, project_path: str) -> list:
    """Query what imports this element."""
    result = await mcp__coderef_context__coderef_query({
        "project_path": project_path,
        "query_type": "imports-me",
        "target": element_name
    })
    return result.get("importers", [])
```

3. **Update analyze_element to populate scan_data with graph results:**
```python
async def analyze_element(self, element_name, project_path, use_coderef_scan=True):
    # ... existing code ...

    # ADD THIS SECTION
    if use_coderef_scan:
        scan_data["dependencies"] = await self.query_dependencies(element_name, project_path)
        scan_data["callers"] = await self.query_callers(element_name, project_path)
        scan_data["imports"] = await self.query_imports(element_name, project_path)

    return analysis
```

---

### Task 2: GRAPH-002 - Update Auto-Fill Functions

**Files to modify:** All auto_fill_* functions in modules

**Pattern to follow:**

**BEFORE (BAD - uses regex):**
```python
def auto_fill_architecture(scan_data: Dict[str, Any]) -> str:
    code = scan_data.get("code", "")
    import re
    deps = re.findall(r'import (\w+)', code)  # ❌ FRAGILE
```

**AFTER (GOOD - uses graph):**
```python
def auto_fill_architecture(scan_data: Dict[str, Any]) -> str:
    dependencies = scan_data.get("dependencies", [])  # ✅ FROM GRAPH
    content = []

    if dependencies:
        content.append("**Dependencies:**\n")
        for dep in dependencies:
            content.append(f"- `{dep['name']}`: {dep['type']}\n")

    return "".join(content)
```

**Files to update:**

1. `resource_sheet/modules/universal/architecture.py` - auto_fill_architecture()
2. `resource_sheet/modules/universal/integration.py` - auto_fill_integration()
3. `resource_sheet/modules/conditional/network/endpoints.py` - auto_fill_endpoints()
4. `resource_sheet/modules/conditional/hooks/signature.py` - auto_fill_hook_signature()
5. All other conditional modules (11 total)

---

## Success Criteria

**You are DONE when:**
- ✅ CodeAnalyzer calls coderef_query MCP tools (GRAPH-001)
- ✅ All auto-fill functions use `scan_data["dependencies"]` instead of regex (GRAPH-002)
- ✅ Auto-fill rate >= 60% (test on 3 elements: AuthService, Button, useLocalStorage)
- ✅ Graph queries complete in < 500ms per element

**How to test:**
```python
# Run this in coderef-docs project
from generators.resource_sheet_generator import ResourceSheetGenerator

generator = ResourceSheetGenerator()
result = await generator.generate(
    element_name="ResourceSheetGenerator",
    project_path="/path/to/coderef-docs",
    mode="reverse-engineer"
)

# Check auto_fill_rate in result
print(f"Auto-fill rate: {result['auto_fill_rate']}")  # Should be >= 60%
```

---

## Reference Files

**Read these first:**
1. `fix-instructions-phase3b.json` - Full task specification
2. `resource_sheet/detection/analyzer.py` - File you'll modify
3. `resource_sheet/modules/universal/architecture.py` - Example auto-fill function

**Documentation:**
- CodeRef Context MCP Tools: See `mcp__coderef_context__coderef_query` tool definition
- Query types: `depends-on`, `calls-me`, `imports-me`, `calls`, `imports`

---

## When You're Done

1. **Test auto-fill rate** on 3 test elements (should be 60-80%)
2. **Update communication.json:**
```json
{
  "phase_3b_status": "complete",
  "auto_fill_rate_achieved": "68%",  // your actual result
  "graph_query_time": "350ms",       // your actual timing
  "completed_by": "coderef-system-agent",
  "completed_at": "2026-01-03T..."
}
```

3. **Notify orchestrator:** Update the main workorder that Phase 3B is complete

---

## Questions?

- **Can't find MCP tools?** They're available as `mcp__coderef_context__coderef_query` - check your imports
- **Graph queries slow?** Add caching layer or reduce query depth
- **Regex still needed?** Only for fallback when .coderef/index.json doesn't exist

---

**START HERE:** Read `fix-instructions-phase3b.json` then modify `resource_sheet/detection/analyzer.py`

**You are BLOCKED until this is complete.** Phase 4 testing cannot start without 60%+ auto-fill rate.
