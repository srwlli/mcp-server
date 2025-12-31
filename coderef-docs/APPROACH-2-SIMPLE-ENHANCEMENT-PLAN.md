# Approach 2: Simple Enhancement Plan

**Status:** Alternative Implementation (Not Selected)
**Created:** 2025-12-31
**Estimated Effort:** ~50 LOC changes, 30-60 minutes

---

## Overview

This plan describes a **minimal integration approach** for adding .coderef/ support to the establish_standards tool. Unlike Approach 1 (full integration), this approach requires minimal code changes and can be implemented quickly.

**Key Difference:**
- **Approach 1 (Implemented):** Integrates .coderef/ reading directly into StandardsGenerator class (~200 LOC)
- **Approach 2 (This Plan):** Wrapper function at tool handler level (~50 LOC)

---

## Implementation Strategy

### Option A: Tool Handler Wrapper

**Location:** `tool_handlers.py:731` (handle_establish_standards function)

**Changes:**
```python
async def handle_establish_standards(arguments: dict) -> list[TextContent]:
    """Handle establish_standards tool call."""
    project_path = validate_project_path_input(arguments.get("project_path", ""))
    scan_depth = validate_scan_depth(arguments.get("scan_depth", ScanDepth.STANDARD.value))

    project_path_obj = Path(project_path)

    # NEW: Check for .coderef/ data first
    coderef_index_path = project_path_obj / '.coderef' / 'index.json'

    if coderef_index_path.exists():
        # FAST PATH: Call enhance-standards.py script
        logger.info("Using .coderef/ data (fast path)")
        return await _generate_standards_from_coderef(project_path_obj, coderef_index_path)
    else:
        # SLOW PATH: Use existing StandardsGenerator
        logger.info("Using full codebase scan (slow path)")
        standards_dir = project_path_obj / Paths.STANDARDS_DIR
        standards_dir.mkdir(parents=True, exist_ok=True)

        generator = StandardsGenerator(project_path_obj, scan_depth)
        result_dict = generator.save_standards(standards_dir)

        return _format_establish_standards_response(result_dict)
```

**New Helper Function:**
```python
async def _generate_standards_from_coderef(
    project_path: Path,
    index_path: Path
) -> list[TextContent]:
    """
    Generate standards using .coderef/index.json (fast path).

    Calls enhance-standards.py script logic directly.
    """
    import json

    # Read index
    index_data = json.loads(index_path.read_text(encoding='utf-8'))

    # Extract components
    components = [e for e in index_data if e.get('type') == 'component']

    # Analyze component files
    component_patterns = {}
    for comp in components:
        file_path = Path(comp['file'])
        if file_path.exists():
            component_patterns[comp['name']] = _analyze_component_source(file_path)

    # Generate standards docs
    standards_dir = project_path / 'coderef' / 'standards'
    standards_dir.mkdir(parents=True, exist_ok=True)

    # Generate 4 docs
    _write_component_index(components, standards_dir)
    _write_ui_standards(component_patterns, standards_dir)
    _write_behavior_standards(component_patterns, standards_dir)
    _write_ux_patterns(standards_dir)

    # Return formatted response
    return [TextContent(
        type="text",
        text=json.dumps({
            "success": True,
            "files": [str(f) for f in standards_dir.glob("*.md")],
            "components_count": len(components),
            "source": ".coderef/index.json"
        })
    )]
```

**Estimated Changes:**
- 1 new helper function (~30 LOC)
- 4 new generation functions (~15 LOC each = 60 LOC)
- Modified handle_establish_standards (~10 LOC)
- **Total: ~100 LOC**

---

### Option B: Subprocess Call to enhance-standards.py

**Location:** `tool_handlers.py:731`

**Changes:**
```python
async def handle_establish_standards(arguments: dict) -> list[TextContent]:
    """Handle establish_standards tool call."""
    project_path = validate_project_path_input(arguments.get("project_path", ""))
    project_path_obj = Path(project_path)

    # Check for .coderef/
    coderef_index_path = project_path_obj / '.coderef' / 'index.json'

    if coderef_index_path.exists():
        # Call enhance-standards.py script
        import subprocess
        script_path = Path(__file__).parent.parent.parent / 'scripts' / 'enhance-standards.py'

        process = await asyncio.create_subprocess_exec(
            'python', str(script_path), str(project_path_obj),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            return [TextContent(type="text", text="Standards generated via enhance-standards.py")]
        else:
            # Fallback to full scan
            pass

    # Existing StandardsGenerator code...
```

**Estimated Changes:**
- 1 modified function (~20 LOC)
- **Total: ~20 LOC**

**Pros:**
- Minimal code changes
- Reuses existing script
- Easy to maintain

**Cons:**
- Subprocess overhead
- Harder to test
- Error handling complexity

---

## Comparison: Approach 1 vs Approach 2

| Criteria | Approach 1 (Implemented) | Approach 2 (This Plan) |
|----------|-------------------------|------------------------|
| **LOC Changes** | ~200 LOC | ~50-100 LOC |
| **Integration Depth** | Deep (StandardsGenerator class) | Shallow (tool handler) |
| **Code Reuse** | Medium (new _read_coderef_index method) | High (reuses enhance-standards.py) |
| **Maintainability** | Better (single source of truth) | Worse (2 code paths) |
| **Performance** | Best (no subprocess) | Good (subprocess overhead if Option B) |
| **Testing** | Easier (unit tests) | Harder (integration tests) |
| **Error Handling** | Robust (try/except, fallback) | Complex (subprocess errors) |
| **Code Clarity** | Clear (single class) | Mixed (handler + script) |

---

## Recommendation

**Approach 1 is recommended** for the following reasons:

1. **Single Source of Truth:** All standards generation logic lives in StandardsGenerator class
2. **Better Maintainability:** No duplication between enhance-standards.py and tool handler
3. **Easier Testing:** Can unit test _read_coderef_index() method directly
4. **No Subprocess Overhead:** Direct Python function calls (faster)
5. **Clearer Code:** StandardsGenerator handles both fast path and slow path

**Approach 2 is acceptable if:**
- Quick implementation is critical (30-60 min vs 2-3 hours)
- enhance-standards.py script needs to remain standalone
- Subprocess overhead is acceptable

---

## Implementation Steps (If Approach 2 Chosen)

### Step 1: Choose Option A or B

**Option A:** In-process generation (recommended, ~100 LOC)
**Option B:** Subprocess call (quick, ~20 LOC)

### Step 2: Implement Changes

**For Option A:**
1. Add `_generate_standards_from_coderef()` helper function
2. Add 4 generation functions (_write_component_index, etc.)
3. Modify handle_establish_standards to check for .coderef/
4. Add error handling and logging

**For Option B:**
1. Add subprocess call to enhance-standards.py
2. Add error handling for subprocess failures
3. Add fallback to StandardsGenerator on error

### Step 3: Test Both Paths

```python
# Test 1: Fast path (with .coderef/)
project_with_coderef = Path("C:/Users/willh/.mcp-servers/coderef-context")
result = await handle_establish_standards({"project_path": str(project_with_coderef)})
assert ".coderef/index.json" in result

# Test 2: Slow path (without .coderef/)
project_without_coderef = Path("/tmp/test-project")
result = await handle_establish_standards({"project_path": str(project_without_coderef)})
assert "full scan" in result
```

### Step 4: Update Documentation

- Update tool_handlers.py docstring
- Update TOOLS_REFERENCE.md with .coderef/ support
- Add note about fast path vs slow path

---

## Timeline

| Task | Effort (Option A) | Effort (Option B) |
|------|-------------------|-------------------|
| Implementation | 2-3 hours | 30-60 minutes |
| Testing | 1 hour | 1 hour |
| Documentation | 30 minutes | 30 minutes |
| **Total** | **3.5-4.5 hours** | **2-2.5 hours** |

---

## Conclusion

**Approach 1 (Full Integration)** was selected and implemented because:
- Better long-term maintainability
- Clearer code architecture
- Easier to test and debug
- No subprocess overhead

**Approach 2 (Simple Enhancement)** remains documented as an alternative for:
- Quick prototyping
- Keeping enhance-standards.py standalone
- Minimal code changes required

Both approaches achieve the same goal: **10x faster standards generation by leveraging .coderef/ data**.

---

**Status:** ✅ Approach 1 Implemented (2025-12-31)
**Alternative:** This plan documents Approach 2 for reference
