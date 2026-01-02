"""
State Management documentation module.

WO-RESOURCE-SHEET-MCP-TOOL-001
"""

from typing import Dict, Any
from ....types import DocumentationModule


def auto_fill_state(scan_data: Dict[str, Any]) -> str:
    """Auto-fill state management documentation from coderef scan data."""
    if not scan_data:
        return ""

    code = scan_data.get("code", "")
    content = []

    # Detect React hooks
    import re

    state_hooks = re.findall(r"useState|useReducer|useContext", code)
    if state_hooks:
        content.append("**State Hooks Used:**\n")
        for hook in sorted(set(state_hooks)):
            content.append(f"- `{hook}`\n")

    # Detect state variables
    state_vars = re.findall(r"const \[(\w+),\s*set\w+\] = useState", code)
    if state_vars:
        content.append("\n**State Variables:**\n")
        for var in state_vars:
            content.append(f"- `{var}` - (document type and purpose)\n")

    # Detect Redux/Zustand patterns
    if "useSelector" in code or "useDispatch" in code:
        content.append("\n**Redux Integration:**\n")
        content.append("- Uses Redux hooks (useSelector, useDispatch)\n")

    if "create(" in code and "zustand" in scan_data.get("imports", []):
        content.append("\n**Zustand Store:**\n")
        content.append("- Custom Zustand store detected\n")

    return "".join(content) if content else ""


state_module: DocumentationModule = {
    "id": "state_management",
    "name": "State Management",
    "category": "state",
    "triggers": {
        "required_when": ["manages_state"],
        "optional_when": ["is_component", "is_hook"],
        "incompatible_with": [],
    },
    "templates": {
        "markdown": {
            "title": "State Management",
            "content": """
## {section_number}. State Management

**State Structure:**

{auto_fill_content}

**State Updates:**
- Update patterns: {update_patterns}
- Immutability: {immutability}
- Batching: {batching}

**State Synchronization:**
- Local vs global: {scope}
- Persistence: {persistence}
- Hydration: {hydration}

**Manual Review Required:**
- State initialization logic?
- State derivation or computed values?
- State normalization strategy?
""",
            "auto_fill": auto_fill_state,
            "manual_prompts": [
                "Document state update patterns",
                "Document state persistence strategy",
                "Note any state derivation logic",
            ],
        },
        "schema": {
            "definition": {
                "type": "object",
                "properties": {
                    "state": {
                        "type": "object",
                        "properties": {
                            "variables": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "type": {"type": "string"},
                                        "initial_value": {"type": "string"},
                                        "scope": {
                                            "type": "string",
                                            "enum": ["local", "global", "shared"],
                                        },
                                    },
                                    "required": ["name", "type", "scope"],
                                },
                            }
                        },
                    }
                },
            },
            "validation_rules": {
                "state": "Must document all stateful variables",
            },
        },
        "jsdoc": {
            "patterns": [
                "/** @state {{type}} {name} - {description} */",
                "/** @updates {state_name} */",
            ],
            "examples": [
                "/** @state {number} count - Current counter value */",
                "/** @updates count - Increments by 1 on button click */",
            ],
        },
    },
}
