# Refactor Plan: Replace CLI with Direct @coderef/core Calls

**Goal:** Replace subprocess CLI calls with direct @coderef/core function calls in the coderef-context MCP server.

**Current:** `subprocess.run(["node", "cli.js", "scan", path])` → CLI parses args → calls core
**Target:** `subprocess.run(["node", "-e", "import('@coderef/core').then(...)"])` → direct core call

---

## Approach: Node.js One-Liner Bridge

Since the MCP server is **Python** and @coderef/core is **JavaScript**, we need Node.js. But instead of calling the full CLI, we'll:

1. **Create JavaScript wrapper functions** that directly import and call @coderef/core
2. **Call them via Node.js `-e` flag** (execute inline script)
3. **Stream JSON results** back to Python

---

## Example: `coderef_scan` Tool

### Current Implementation (server.py lines 467-527)
```python
async def handle_coderef_scan(args: dict) -> list[TextContent]:
    cmd = [
        *CLI_COMMAND, "scan",  # CLI_COMMAND = ["node", "cli.js"]
        project_path,
        "--lang", ",".join(languages),
        "--json"
    ]

    process = await asyncio.create_subprocess_exec(*cmd, ...)
    stdout, stderr = await process.communicate()
    data = json.loads(stdout.decode())
    return [TextContent(type="text", text=json.dumps(data))]
```

### New Implementation (Direct Core)
```python
async def handle_coderef_scan(args: dict) -> list[TextContent]:
    # JavaScript inline script that calls @coderef/core directly
    js_code = f"""
    import {{ scanCurrentElements }} from '@coderef/core';
    const elements = await scanCurrentElements(
      '{project_path}',
      {json.dumps(languages)},
      {{ recursive: true }}
    );
    console.log(JSON.stringify(elements));
    """

    cmd = [
        "node",
        "--input-type=module",  # Allow ES module imports
        "-e", js_code
    ]

    process = await asyncio.create_subprocess_exec(*cmd, ...)
    stdout, stderr = await process.communicate()
    data = json.loads(stdout.decode())
    return [TextContent(type="text", text=json.dumps(data))]
```

**Benefits:**
- ✅ No CLI argument parsing overhead
- ✅ Direct function calls (faster)
- ✅ Simpler debugging (inline scripts)
- ✅ Works with @coderef/core ES modules

**Challenges:**
- ⚠️ Need to resolve @coderef/core import path
- ⚠️ Must escape special characters in inline scripts
- ⚠️ Error handling needs to parse stderr

---

## Better Approach: Wrapper Script Files

Instead of inline `-e` scripts, create **small JavaScript wrapper files**:

### File: `src/wrappers/scan.mjs`
```javascript
#!/usr/bin/env node
import { scanCurrentElements } from '@coderef/core';

const args = JSON.parse(process.argv[2]);
const { projectPath, languages, options } = args;

try {
  const elements = await scanCurrentElements(projectPath, languages, options);
  console.log(JSON.stringify({ success: true, data: elements }));
} catch (error) {
  console.error(JSON.stringify({
    success: false,
    error: error.message
  }));
  process.exit(1);
}
```

### Python calls it:
```python
async def handle_coderef_scan(args: dict) -> list[TextContent]:
    wrapper_script = os.path.join(os.path.dirname(__file__), "src/wrappers/scan.mjs")

    cmd = [
        "node",
        wrapper_script,
        json.dumps({
            "projectPath": project_path,
            "languages": languages,
            "options": {"recursive": True}
        })
    ]

    process = await asyncio.create_subprocess_exec(*cmd, ...)
    stdout, stderr = await process.communicate()
    result = json.loads(stdout.decode())

    if not result['success']:
        return [TextContent(type="text", text=f"Error: {result['error']}")]

    return [TextContent(type="text", text=json.dumps(result['data']))]
```

---

## Implementation Plan

### Phase 1: Create Wrapper Scripts (4 hours)

Create one wrapper per MCP tool:

1. **`src/wrappers/scan.mjs`** - Wraps `scanCurrentElements()`
2. **`src/wrappers/query.mjs`** - Wraps `AnalyzerService.query()`
3. **`src/wrappers/impact.mjs`** - Wraps `ImpactSimulator.analyze()`
4. **`src/wrappers/complexity.mjs`** - Wraps `ComplexityScorer.score()`
5. **`src/wrappers/patterns.mjs`** - Wraps `PatternDetector.find()`
6. **`src/wrappers/coverage.mjs`** - Wraps coverage analysis
7. **`src/wrappers/context.mjs`** - Wraps `ContextGenerator.generate()`
8. **`src/wrappers/validate.mjs`** - Wraps reference validation
9. **`src/wrappers/drift.mjs`** - Wraps drift detection
10. **`src/wrappers/diagram.mjs`** - Wraps diagram generation
11. **`src/wrappers/tag.mjs`** - Wraps tagging
12. **`src/wrappers/export.mjs`** - Wraps export

### Phase 2: Update Python Handlers (3 hours)

Replace each `handle_coderef_*` function:
- Remove CLI command building
- Call wrapper script with JSON args
- Parse JSON response
- Handle errors properly

### Phase 3: Update Path Resolution (1 hour)

```python
def get_core_path():
    """Get @coderef/core package location"""
    # Try environment variable first
    if "CODEREF_CORE_PATH" in os.environ:
        return os.environ["CODEREF_CORE_PATH"]

    # Fall back to default
    return r"C:\Users\willh\Desktop\projects\coderef-system\packages\core"

CORE_PATH = get_core_path()

# Set NODE_PATH so wrappers can import @coderef/core
os.environ["NODE_PATH"] = CORE_PATH
```

### Phase 4: Testing (2 hours)

Test each tool:
```python
# Test scan
await handle_coderef_scan({"project_path": "C:/test", "languages": ["ts"]})

# Test query
await handle_coderef_query({"target": "myFunction", "query_type": "calls"})

# ... test all 12 tools
```

---

## File Structure

```
coderef-context/
├── server.py (modified)
├── src/
│   └── wrappers/
│       ├── scan.mjs
│       ├── query.mjs
│       ├── impact.mjs
│       ├── complexity.mjs
│       ├── patterns.mjs
│       ├── coverage.mjs
│       ├── context.mjs
│       ├── validate.mjs
│       ├── drift.mjs
│       ├── diagram.mjs
│       ├── tag.mjs
│       └── export.mjs
└── processors/
    └── export_processor.py (unchanged)
```

---

## Benefits

| Metric | Before (CLI) | After (Wrappers) | Improvement |
|--------|--------------|------------------|-------------|
| Subprocess startup | ~200-300ms | ~100-150ms | 2x faster |
| Argument parsing | ~50ms | 0ms | Eliminated |
| Code complexity | High (CLI layers) | Low (direct calls) | Simpler |
| Debugging | Hard (multi-process) | Easy (single script) | Better DX |
| Type safety | None | Import types | Safer |

---

## Risks & Mitigations

1. **ES Module Resolution**
   - Risk: Node.js can't find @coderef/core
   - Mitigation: Set NODE_PATH environment variable

2. **Error Handling**
   - Risk: JavaScript errors not caught by Python
   - Mitigation: Wrap all calls in try/catch, return JSON errors

3. **Path Escaping**
   - Risk: Windows paths break JSON parsing
   - Mitigation: Use `json.dumps()` for all paths

4. **Breaking Changes**
   - Risk: @coderef/core API changes break wrappers
   - Mitigation: Pin @coderef/core version, add integration tests

---

## Next Steps

1. ✅ Review this plan
2. ⏳ Create `src/wrappers/scan.mjs` (prototype)
3. ⏳ Test scan wrapper with real project
4. ⏳ Create remaining 11 wrappers
5. ⏳ Update `server.py` handlers
6. ⏳ Run full test suite
7. ⏳ Update documentation

**Ready to proceed?**
