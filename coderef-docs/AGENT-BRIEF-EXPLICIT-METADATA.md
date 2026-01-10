# Agent Brief: Add Explicit METADATA to Foundation Docs

**Assigned To:** Docs Generation Agent
**Workorder:** Modify foundation doc generators to output machine-readable METADATA sections
**Priority:** HIGH - Required for planning validation in coderef-workflow

---

## Objective

Update `coderef_foundation_generator.py` to add structured METADATA sections to all generated foundation docs. This enables planning validation to extract explicit entry points, components, and architecture patterns instead of guessing.

---

## Files to Modify

**Primary:** `C:\Users\willh\.mcp-servers\coderef-docs\generators\coderef_foundation_generator.py`

**Methods to update:**
1. `_generate_architecture_md()` - Line 960 (CRITICAL)
2. `_generate_readme_md()` - (Recommended)
3. `_generate_api_md()` - (Recommended)
4. `_generate_components_md()` - (Recommended)
5. `_generate_schema_md()` - (Recommended)

---

## Required Changes

### 1. ARCHITECTURE.md (CRITICAL - Must Do)

**Insert at line 966** (after `lines = ['# Architecture Documentation', '']`):

```python
# Add structured METADATA section
lines.append('---')
lines.append('## METADATA (Required for Planning Validation)')
lines.append('')
lines.append(f"**Entry Point:** {self._detect_entry_point(context, coderef_data)}")
lines.append(f"**Main Components:** {self._extract_main_components(coderef_data)}")
lines.append(f"**Architecture Pattern:** {self._detect_architecture_pattern(context)}")
lines.append(f"**Framework:** {context.get('framework', 'Unknown')}")
lines.append(f"**Primary Language:** {context.get('primary_language', 'Unknown')}")
lines.append('')
lines.append('---')
lines.append('')
```

### 2. Add Helper Methods

**Add these 3 methods to the class** (around line 1100):

```python
def _detect_entry_point(self, context: Dict, coderef_data: Optional[Dict]) -> str:
    """Detect main entry point from coderef data or project structure."""
    if coderef_data and coderef_data.get('elements'):
        # Priority: server.py, app.py, main.py, index.py
        for elem in coderef_data['elements']:
            name = elem.get('name', '').lower()
            if name in ['server', 'app', 'main', 'index']:
                return elem.get('file', 'Unknown').split('/')[-1]

    # Fallback: Check common patterns
    project_path = Path(context.get('project_path', '.'))
    for entry in ['server.py', 'app.py', 'main.py', 'index.py']:
        if (project_path / entry).exists():
            return entry

    return 'Unknown'

def _extract_main_components(self, coderef_data: Optional[Dict]) -> str:
    """Extract 3-5 main components from coderef data."""
    if not coderef_data or not coderef_data.get('elements'):
        return 'Unknown'

    # Get top classes/modules
    classes = [e for e in coderef_data['elements'] if e.get('type') == 'class'][:3]
    if classes:
        names = [c.get('name', 'Unknown') for c in classes]
        return ', '.join(names)

    return 'Unknown'

def _detect_architecture_pattern(self, context: Dict) -> str:
    """Detect architecture pattern from project structure."""
    framework = context.get('framework', '').lower()

    if 'mcp' in framework or 'model context protocol' in framework:
        return 'MCP Server'
    elif 'flask' in framework or 'fastapi' in framework:
        return 'REST API'
    elif 'cli' in framework:
        return 'CLI Tool'

    return 'Unknown'
```

---

## Validation

After editing, test with:

```bash
cd C:\Users\willh\.mcp-servers\coderef-docs
python -c "
from generators.coderef_foundation_generator import CoderefFoundationGenerator
from pathlib import Path

gen = CoderefFoundationGenerator(Path.cwd())
arch = gen._generate_architecture_md({}, {}, None)
print(arch[:500])
"
```

**Expected output should contain:**
```
## METADATA (Required for Planning Validation)

**Entry Point:** server.py
**Main Components:** ...
```

---

## Success Criteria

✅ ARCHITECTURE.md has METADATA section at top
✅ Entry Point is auto-detected (not "Unknown")
✅ Main Components lists 3-5 actual components
✅ Pattern is detected (MCP Server, REST API, etc.)
✅ Planning validation in coderef-workflow can parse entry point

---

## Notes

- **DO NOT** break existing doc generation
- **DO NOT** remove existing content
- **ADD** METADATA section before existing content
- Use helper methods to avoid hardcoding values
- Gracefully handle missing data (return "Unknown" instead of crashing)
