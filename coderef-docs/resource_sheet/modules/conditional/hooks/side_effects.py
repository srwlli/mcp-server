"""
Hook Side Effects documentation module.

WO-RESOURCE-SHEET-MCP-TOOL-001
"""

from typing import Dict, Any
from ....types import DocumentationModule


def auto_fill_side_effects(scan_data: Dict[str, Any]) -> str:
    """Auto-fill side effects documentation from coderef scan data."""
    if not scan_data:
        return ""

    code = scan_data.get("code", "")
    content = []

    # Detect side effects
    import re

    # Detect useEffect
    effects = re.findall(r"useEffect\(\s*\(\)\s*=>\s*{", code)
    if effects:
        content.append(f"**Side Effects:**\n")
        content.append(f"- {len(effects)} useEffect hook{'s' if len(effects) > 1 else ''}\n")

    # Detect subscriptions
    if "subscribe" in code.lower() or "addEventListener" in code:
        content.append("\n**Subscriptions:**\n")
        content.append("- Event subscriptions detected\n")

    # Detect cleanup
    if "removeEventListener" in code or "unsubscribe" in code.lower():
        content.append("\n**Cleanup:**\n")
        content.append("- Cleanup functions implemented\n")

    return "".join(content) if content else ""


hook_side_effects_module: DocumentationModule = {
    "id": "hook_side_effects",
    "name": "Hook Side Effects",
    "category": "hooks",
    "triggers": {
        "required_when": ["is_hook"],
        "optional_when": ["manages_state"],
        "incompatible_with": [],
    },
    "templates": {
        "markdown": {
            "title": "Hook Side Effects",
            "content": """
## {section_number}. Hook Side Effects

**Side Effects:**

{auto_fill_content}

**Effect Timing:**
- Runs on: {timing}
- Dependencies: {dependencies}
- Cleanup: {cleanup}

**External Interactions:**
- API calls: {api}
- Storage: {storage}
- DOM manipulation: {dom}

**Manual Review Required:**
- Effect dependencies complete?
- Race condition handling?
- Memory leak prevention?
""",
            "auto_fill": auto_fill_side_effects,
            "manual_prompts": [
                "Document all side effects",
                "Document effect dependencies",
                "Note cleanup requirements",
            ],
        },
        "schema": {
            "definition": {
                "type": "object",
                "properties": {
                    "side_effects": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {
                                    "type": "string",
                                    "enum": ["api", "storage", "dom", "subscription"],
                                },
                                "trigger": {"type": "string"},
                                "cleanup": {"type": "boolean"},
                            },
                            "required": ["type", "trigger"],
                        },
                    }
                },
            },
            "validation_rules": {
                "side_effects": "Must document all side effects",
            },
        },
        "jsdoc": {
            "patterns": [
                "/** @effect {description} */",
                "/** @side-effect {type} - {description} */",
            ],
            "examples": [
                "/** @effect Subscribes to user presence updates */",
                "/** @side-effect api - Fetches data on mount */",
            ],
        },
    },
}
