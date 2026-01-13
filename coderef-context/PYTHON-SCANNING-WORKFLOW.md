# Python Scanning Workflow - Using @coderef/core CLI

**Date:** 2026-01-13
**Issue:** WO-CONTEXT-INTEGRATION-001 P1-2 requirement misunderstood
**Resolution:** Use existing `@coderef/core` CLI for Python scanning (already works!)

---

## What Was Wrong

### Original Requirement (P1-2)
```
"Support Python code scanning (not just TypeScript)"
Rationale: "coderef-context is Python but CLI only scans TypeScript -
           index.json empty for itself"
```

**This was MISLEADING.** The CLI **already supports Python** via regex patterns!

### What We Mistakenly Did
Created a new Python AST scanner in the MCP server:
- ❌ `src/python_scanner.py` - Duplicate Python scanning logic
- ❌ Enhanced `coderef_scan` tool with `include_python` parameter
- ❌ Added `scan_python_files()` to CodeRefReader

**Problem:** This duplicates functionality that already exists in `@coderef/core` CLI.

---

## How Python Scanning Actually Works

### 1. The CLI Already Has Python Support

**Location:** `packages/core/scanner.ts` (lines 66-69)

```typescript
py: [
  { type: 'function', pattern: /def\s+([a-zA-Z0-9_]+)\s*\(/g, nameGroup: 1 },
  { type: 'class', pattern: /class\s+([a-zA-Z0-9_]+)\s*(?:\(|:)/g, nameGroup: 1 },
  { type: 'method', pattern: /\s+def\s+([a-zA-Z0-9_]+)\s*\(self/g, nameGroup: 1 }
]
```

**Accuracy:** 85% (regex-based)

### 2. **NEW (2026-01-13):** All 10 Languages Now Default!

**Recent Update:** The dashboard and core now scan **all 10 supported languages by default:**

```typescript
// packages/dashboard/src/app/api/scanner/lib/scanExecutor.ts:246
['ts', 'tsx', 'js', 'jsx', 'py', 'go', 'rs', 'java', 'cpp', 'c']

// packages/dashboard/src/app/api/scan/route.ts:146
lang: options.lang || ['ts', 'tsx', 'js', 'jsx', 'py', 'go', 'rs', 'java', 'cpp', 'c']

// packages/coderef-core/src/context/context-generator.ts:71
const languages = options.languages || ['ts', 'tsx', 'js', 'jsx', 'py', 'go', 'rs', 'java', 'cpp', 'c'];
```

**Impact:**
- ✅ Scanner UI automatically includes Python
- ✅ API routes automatically include Python
- ✅ Context generation automatically includes Python
- ✅ **No need to specify `--lang py` anymore!**

### 3. The populate-coderef.py Script Already Uses Python

**Location:** `scripts/populate-coderef.py` (line 62)

```python
lang = "py,ts,tsx,js,jsx"  # Support both Python and TypeScript projects
```

**Recommendation:** Update this to match the new defaults:
```python
lang = "py,ts,tsx,js,jsx,go,rs,java,cpp,c"  # All 10 supported languages
```

**Line 81:**
```python
if run_save(f'{cli} scan "{project}" -l {lang} --json', coderef_dir / 'index.json'):
```

### 3. Testing: It Works!

```bash
$ coderef scan C:/Users/willh/.mcp-servers/coderef-context --lang py --json

# Result: 249 Python elements found
# - Functions: 80
# - Classes: 15
# - Methods: 154
```

---

## Correct Workflow for Python Projects

### For MCP Server Projects (like coderef-context)

**Step 1: Run populate script**
```bash
cd C:/Users/willh/Desktop/projects/coderef-system
python scripts/populate-coderef.py C:/Users/willh/.mcp-servers/coderef-context
```

This automatically:
- Scans with `-l py,ts,tsx,js,jsx`
- Creates `.coderef/index.json` with Python elements
- Generates all 16 output types

**Step 2: MCP server reads the results**
```python
# coderef_scan tool just reads index.json
result = await call_tool("coderef_scan", {
    "project_path": "C:/Users/willh/.mcp-servers/coderef-context"
})

# Returns: 249 elements (all Python functions, classes, methods)
```

### For Pure Python Projects

**Option A: Use populate script**
```bash
python scripts/populate-coderef.py /path/to/python/project
```

**Option B: Use CLI directly**
```bash
coderef scan /path/to/python/project --lang py --json > .coderef/index.json
```

### For Mixed Projects (Python + TypeScript)

```bash
# Populate script already handles this!
python scripts/populate-coderef.py /path/to/mixed/project

# Or manually:
coderef scan /path/to/mixed/project --lang py,ts,tsx,js,jsx --json
```

---

## What Needed Adjustment (Not New Scanner)

### The Real Issue

The `.coderef/index.json` was **empty** because:
1. ❌ The populate script **wasn't run recently**
2. ❌ The old v1.x format didn't match v2.0 structure

**NOT because Python wasn't supported!**

### What Should Have Been Done (P1-2)

Instead of creating a new Python scanner:

✅ **Document the workflow:**
- Add this PYTHON-SCANNING-WORKFLOW.md
- Update INTEGRATION.md with Python scanning examples
- Add to quickref.md: "Run populate-coderef.py to scan Python projects"

✅ **Improve populate script (if needed):**
- Better error messages
- Detect project language automatically
- Add `--force-refresh` flag

✅ **Enhance CLI Python patterns (in @coderef/core):**
- Add async function detection: `async def`
- Add decorator detection: `@decorator`
- Add type hints: `def foo(x: int) -> str:`
- Improve method detection (not just `self`, but `cls` too)

---

## Adjustments for Plan.json / Context.json

### Update P1-2 Requirement

**Old (misleading):**
```json
{
  "title": "Support Python code scanning (not just TypeScript)",
  "rationale": "CLI only scans TypeScript - index.json empty for itself",
  "implementation": "Add Python AST scanner (use ast module)"
}
```

**Corrected:**
```json
{
  "title": "Document and test Python scanning workflow",
  "rationale": "CLI already supports Python (regex), but workflow is undocumented.
               index.json was empty because populate script wasn't run, not because
               Python wasn't supported.",
  "implementation": "Document workflow: populate-coderef.py automatically scans
                     Python with -l py flag. Test on coderef-context server.
                     Optionally enhance CLI patterns in @coderef/core for better
                     Python detection (decorators, async, type hints)."
}
```

### Success Criteria (Corrected)

**What we actually needed:**
- ✅ Document Python scanning workflow
- ✅ Verify populate-coderef.py works with Python projects
- ✅ Test on coderef-context itself (249 elements found!)
- ✅ Update INTEGRATION.md with Python examples
- ⏳ (Optional) Enhance CLI regex patterns for Python

**What we didn't need:**
- ❌ New Python AST scanner in MCP server
- ❌ Duplicate scanning logic
- ❌ Live scanning capability in read-only server

---

## Architecture Decision: Keep Scanning in CLI

**Why all scanning should happen in @coderef/core CLI:**

1. **Single Source of Truth**
   - One scanner implementation (not multiple)
   - Consistent output format
   - Easier to maintain

2. **Language-Agnostic Extension**
   - CLI can add new languages: Go, Rust, Java, etc.
   - MCP server stays read-only (simpler, faster)
   - No need to reimplement scanners in multiple languages

3. **Performance**
   - CLI written in TypeScript (fast, compiled)
   - MCP server stays lightweight (just reads files)
   - Scanning is one-time cost (results cached in .coderef/)

4. **Separation of Concerns**
   - CLI = Data Generation (scanning, analysis)
   - MCP Server = Data Access (reading, querying)
   - Clear boundaries, easier to test

---

## Future Enhancements (Optional)

If Python scanning needs improvement, enhance **@coderef/core CLI**, not MCP server:

### Add to packages/core/scanner.ts

```typescript
py: [
  // Existing
  { type: 'function', pattern: /def\s+([a-zA-Z0-9_]+)\s*\(/g, nameGroup: 1 },
  { type: 'class', pattern: /class\s+([a-zA-Z0-9_]+)\s*(?:\(|:)/g, nameGroup: 1 },
  { type: 'method', pattern: /\s+def\s+([a-zA-Z0-9_]+)\s*\(self/g, nameGroup: 1 },

  // NEW: Better Python support
  { type: 'function', pattern: /async\s+def\s+([a-zA-Z0-9_]+)\s*\(/g, nameGroup: 1 },  // async
  { type: 'method', pattern: /\s+def\s+([a-zA-Z0-9_]+)\s*\(cls/g, nameGroup: 1 },      // classmethod
  { type: 'decorator', pattern: /@([a-zA-Z0-9_\.]+)/g, nameGroup: 1 },                 // decorators
  { type: 'constant', pattern: /^([A-Z][A-Z0-9_]*)\s*=/gm, nameGroup: 1 }              // constants
]
```

### Or: Add Python AST Scanner to CLI

Create `packages/core/src/analyzer/python-ast-scanner.ts`:
- Call Python's `ast` module via subprocess
- Parse output and convert to CodeRef format
- 99% accuracy (same as TypeScript AST scanner)

**But NOT in the MCP server** - keep it in the CLI where all scanning belongs.

---

## Testing the Corrected Workflow

### Test 1: Scan coderef-context (Python MCP server)
```bash
cd C:/Users/willh/Desktop/projects/coderef-system
python scripts/populate-coderef.py C:/Users/willh/.mcp-servers/coderef-context

# Verify:
cat C:/Users/willh/.mcp-servers/coderef-context/.coderef/index.json | python -c "import json,sys; print(f'Elements: {len(json.load(sys.stdin))}')"
# Expected: 249 elements
```

✅ **Result:** Works perfectly! 249 Python elements found.

### Test 2: Call MCP tool
```python
result = await call_tool("coderef_scan", {
    "project_path": "C:/Users/willh/.mcp-servers/coderef-context"
})

# Returns: {"success": true, "elements_found": 249, "elements": [...]}
```

✅ **Result:** MCP server reads the scanned data correctly.

### Test 3: Pure Python project
```bash
# Test on any Python project
python scripts/populate-coderef.py /path/to/django/project

# Should find all Python functions, classes, methods
```

---

## Summary

**What we learned:**
- ✅ The CLI **already supports Python** (regex, 85% accuracy)
- ✅ The populate script **already uses Python** (`-l py` flag)
- ✅ The MCP server just needs to **read** the results (already does this)
- ❌ We **didn't need** a new Python scanner in the MCP server

**What to adjust in workflow/documentation:**
1. ✅ Document the correct workflow (this file)
2. ✅ Update plan.json P1-2 requirement (clarify it's about workflow, not new scanner)
3. ✅ Update INTEGRATION.md with Python scanning examples
4. ✅ Test on real Python projects (done - coderef-context works!)
5. ⏳ (Optional) Enhance CLI regex patterns for better Python support

**Architecture principle:**
- **Scanning happens in CLI** (@coderef/core)
- **Reading happens in MCP server** (coderef-context)
- **Keep them separate** (single responsibility)

---

**Reverted Files:**
- `src/python_scanner.py` - **DELETED** (unnecessary duplication)
- `src/handlers_refactored.py` - Removed `include_python` logic
- `src/coderef_reader.py` - Removed `scan_python_files()` method
- `server.py` - Removed `include_python` parameter

**Kept Files (P1, P2 work):**
- ✅ `coderef_incremental_scan` tool (P1-1) - Valid enhancement
- ✅ `quickref.md` (P2-1) - Useful documentation
- ✅ `generate_foundation_docs` tool (P2-2) - Valid enhancement
- ✅ `validate_coderef_outputs` tool (P2-3) - Valid enhancement
