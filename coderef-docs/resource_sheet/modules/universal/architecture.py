"""
Architecture Module - Component Hierarchy and Dependencies.

WO-RESOURCE-SHEET-MCP-TOOL-001

Universal module always included in resource sheets.
Documents component structure, dependencies, and architectural patterns.
"""

from ...types import DocumentationModule, ModuleTriggers, ModuleTemplates, ModuleExtraction


def auto_fill_architecture(data: dict) -> str:
    """
    Auto-fill architecture section from extracted data.

    Args:
        data: Extracted element data from coderef_scan

    Returns:
        Formatted markdown content
    """
    element_type = data.get("type", "Unknown")
    dependencies = data.get("dependencies", [])
    exports = data.get("exports", [])

    content = f"**Type:** {element_type}\n\n"

    if dependencies:
        content += "**Dependencies:**\n"
        for dep in dependencies[:10]:  # Top 10
            content += f"- `{dep}`\n"
        if len(dependencies) > 10:
            content += f"- ...and {len(dependencies) - 10} more\n"
        content += "\n"

    if exports:
        content += "**Exports:**\n"
        for exp in exports:
            content += f"- `{exp}`\n"
        content += "\n"

    return content


def extract_from_coderef_scan(scan_data: dict) -> dict:
    """
    Extract architecture data from coderef_scan output.

    Args:
        scan_data: Output from coderef_scan tool

    Returns:
        Extracted architecture data
    """
    return {
        "type": scan_data.get("type", "Unknown"),
        "dependencies": scan_data.get("imports", []),
        "exports": scan_data.get("exports", []),
        "file_path": scan_data.get("file_path", ""),
        "lines_of_code": scan_data.get("loc", 0),
    }


def validate_architecture_data(data: dict) -> dict:
    """
    Validate extracted architecture data.

    Args:
        data: Extracted data to validate

    Returns:
        Validation result with errors and warnings
    """
    errors = []
    warnings = []

    if not data.get("type"):
        errors.append("Missing element type")

    if not data.get("file_path"):
        warnings.append("No file path provided")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


# Module Definition
architecture_module = DocumentationModule(
    # Identity
    id="architecture",
    name="Architecture Overview",
    description="Documents component hierarchy, dependencies, and architectural patterns",
    category="universal",
    # Triggers (always included - no specific triggers)
    triggers=ModuleTriggers(
        required_when=[],  # Always included
        optional_when=[],
        incompatible_with=[],
    ),
    # Templates
    templates=ModuleTemplates(
        markdown={
            "section_title": "## 1. Architecture",
            "content": """
**Type:** {{type}}

**Dependencies:**
{{#each dependencies}}
- `{{this}}`
{{/each}}

**Exports:**
{{#each exports}}
- `{{this}}`
{{/each}}

**File Location:** `{{file_path}}`

**Lines of Code:** {{lines_of_code}}
            """.strip(),
            "auto_fill": auto_fill_architecture,
            "manual_prompts": [
                "Are there additional architectural patterns to document?",
                "Any key design decisions to note?",
            ],
        },
        schema={
            "definition": {
                "architecture": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string"},
                        "dependencies": {"type": "array", "items": {"type": "string"}},
                        "exports": {"type": "array", "items": {"type": "string"}},
                        "file_path": {"type": "string"},
                        "lines_of_code": {"type": "number"},
                    },
                    "required": ["type", "file_path"],
                }
            },
            "validation_rules": {},
        },
        jsdoc={
            "patterns": [
                "/** @module {{element_name}} */",
                "/** @category {{type}} */",
                "/** @file {{file_path}} */",
            ],
            "examples": [
                "/** @module AuthService */",
                "/** @category API Client */",
            ],
        },
    ),
    # Extraction
    extraction=ModuleExtraction(
        from_coderef_scan=extract_from_coderef_scan,
        from_ast=lambda ast: {},  # Not implemented yet
        from_user=[
            {"question": "Element type?", "type": "string"},
            {"question": "Main dependencies?", "type": "array"},
        ],
        validation=validate_architecture_data,
    ),
    # Metadata
    version="1.0.0",
    auto_fill_capable=True,
)
