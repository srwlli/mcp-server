"""
Resource Sheet MCP Tool - Composable Documentation Module System.

WO-RESOURCE-SHEET-MCP-TOOL-001

This package provides a composable module-based approach to generating
authoritative technical documentation for code elements.

Instead of 20 rigid templates, it uses ~30-40 small modules that compose
intelligently based on code characteristics.

## Architecture

The system uses a 3-step workflow:

1. **DETECT** - Analyze code to detect characteristics (state, network, JSX, etc.)
   - Uses `detection.CodeAnalyzer` to read from coderef_scan or file content
   - `detection.CharacteristicsDetector` maps code patterns to boolean flags

2. **SELECT** - Choose appropriate modules based on characteristics
   - `modules.ModuleRegistry` maintains all available modules
   - Selection logic matches characteristics to module triggers

3. **ASSEMBLE** - Compose selected modules into documentation
   - `composition.DocumentComposer` assembles modules into 3 formats
   - Outputs: Markdown + JSON Schema + JSDoc

## Module Types

**Universal Modules** (always included):
- architecture - Component hierarchy and dependencies
- integration - How element connects to other code
- testing - Test patterns and coverage (stub in Phase 1)
- performance - Limits and bottlenecks (stub in Phase 1)

**Conditional Modules** (Phase 2):
- UI modules (props, events, accessibility)
- State modules (state, lifecycle)
- Network modules (endpoints, auth, retry, errors)
- Hook modules (signature, side_effects, cleanup)

## Usage

```python
from generators.resource_sheet_generator import ResourceSheetGenerator

generator = ResourceSheetGenerator()
result = await generator.generate(
    element_name="AuthService",
    project_path="/path/to/project",
    mode="reverse-engineer",
    auto_analyze=True
)

# Outputs created at:
# - coderef/foundation-docs/AUTHSERVICE.md
# - coderef/schemas/authservice.schema.json
# - coderef/foundation-docs/authservice.jsdoc.txt
```

## Phase 1 Status (Complete)

- ✅ 4 universal modules (2 full, 2 stubs)
- ✅ Detection engine (20+ characteristics)
- ✅ Module registry and selection
- ✅ Document composer (3 formats)
- ✅ MCP tool integration
- ✅ 13/13 tests passing (100%)

Phase 2 will add 11-15 conditional modules and improve auto-fill rate to 60%+.
"""

from .modules import ModuleRegistry
from .detection import CodeAnalyzer, CharacteristicsDetector
from .composition import DocumentComposer

__all__ = [
    "ModuleRegistry",
    "CodeAnalyzer",
    "CharacteristicsDetector",
    "DocumentComposer",
]

__version__ = "0.1.0"
