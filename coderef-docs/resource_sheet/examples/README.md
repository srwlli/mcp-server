# Resource Sheet Examples

This directory contains sample outputs from the Resource Sheet Generator.

## WO-RESOURCE-SHEET-MCP-TOOL-001

Generated using the composable module system with intelligent auto-detection.

## Examples Included

### 1. sample-authservice.md
Example output for an API service with authentication.

**Detected Characteristics:**
- makes_network_calls: true
- handles_auth: true
- has_error_handling: true
- is_class: true

**Selected Modules:**
- architecture (universal)
- integration (universal)
- testing (universal - stub)
- performance (universal - stub)

**Auto-Fill Rate:** 50% (2/4 modules fully implemented)

### 2. sample-authservice.schema.json
JSON Schema output for the same element.

### 3. sample-authservice.jsdoc.txt
JSDoc comment suggestions for inline documentation.

## How These Were Generated

```python
from generators.resource_sheet_generator import ResourceSheetGenerator

generator = ResourceSheetGenerator()
result = await generator.generate(
    element_name="AuthService",
    project_path="/sample/project",
    mode="template",  # Template mode for example
    auto_analyze=False,
    output_path="resource_sheet/examples"
)
```

## Phase 1 Limitations

- Only 4 universal modules implemented (2 full, 2 stubs)
- No conditional modules yet (endpoints, auth, errors, etc.)
- Auto-fill limited to 50% (architecture + integration modules only)

Phase 2 will add 11-15 conditional modules and increase auto-fill to 60%+.
