"""
Props documentation module.

WO-RESOURCE-SHEET-MCP-TOOL-001
"""

from typing import Dict, Any
from ....types import DocumentationModule, CodeCharacteristics


def auto_fill_props(scan_data: Dict[str, Any]) -> str:
    """Auto-fill props documentation from coderef scan data."""
    if not scan_data:
        return ""

    # Extract props from code analysis
    props = scan_data.get("props", [])
    interfaces = scan_data.get("interfaces", [])

    content = []

    # Document TypeScript/PropTypes interfaces
    for interface in interfaces:
        if "Props" in interface.get("name", ""):
            content.append(f"**{interface['name']}**\n")
            for prop in interface.get("properties", []):
                name = prop.get("name", "unknown")
                type_str = prop.get("type", "any")
                required = "Required" if prop.get("required", False) else "Optional"
                default = prop.get("default", "N/A")
                content.append(
                    f"- `{name}` ({type_str}) - {required}\n"
                    f"  - Default: `{default}`\n"
                )

    # Fallback to detected props from code
    if not content and props:
        content.append("**Detected Props:**\n")
        for prop in props:
            content.append(f"- `{prop}` - (type to be documented)\n")

    return "".join(content) if content else ""


props_module: DocumentationModule = {
    "id": "props",
    "name": "Props & Configuration",
    "category": "ui",
    "triggers": {
        "required_when": ["has_props", "is_component"],
        "optional_when": [],
        "incompatible_with": ["is_function", "is_class"],
    },
    "templates": {
        "markdown": {
            "title": "Props & Configuration",
            "content": """
## {section_number}. Props & Configuration

**Component Props:**

{auto_fill_content}

**Prop Validation:**
- Validation rules: {validation}
- Default props: {defaults}

**Manual Review Required:**
- Are there computed props or derived state?
- Any prop transformations or normalizations?
""",
            "auto_fill": auto_fill_props,
            "manual_prompts": [
                "Document validation rules",
                "Document default props",
                "Note any computed or derived props",
            ],
        },
        "schema": {
            "definition": {
                "type": "object",
                "properties": {
                    "props": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "type": {"type": "string"},
                                "required": {"type": "boolean"},
                                "default": {"type": "string"},
                                "description": {"type": "string"},
                            },
                            "required": ["name", "type"],
                        },
                    }
                },
            },
            "validation_rules": {
                "props": "Must document all public props",
            },
        },
        "jsdoc": {
            "patterns": [
                "/** @param {Props} props - Component properties */",
                "/** @prop {{type}} {name} - {description} */",
            ],
            "examples": [
                "/** @prop {string} title - Button label */",
                "/** @prop {boolean} [disabled=false] - Disable button */",
            ],
        },
    },
}
