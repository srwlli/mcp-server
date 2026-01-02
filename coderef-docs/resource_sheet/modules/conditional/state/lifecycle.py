"""
Lifecycle documentation module.

WO-RESOURCE-SHEET-MCP-TOOL-001
"""

from typing import Dict, Any
from ....types import DocumentationModule


def auto_fill_lifecycle(scan_data: Dict[str, Any]) -> str:
    """Auto-fill lifecycle documentation from coderef scan data."""
    if not scan_data:
        return ""

    code = scan_data.get("code", "")
    content = []

    # Detect React lifecycle hooks
    import re

    lifecycle_hooks = re.findall(r"useEffect|useLayoutEffect|useMemo|useCallback", code)
    if lifecycle_hooks:
        content.append("**Lifecycle Hooks:**\n")
        for hook in sorted(set(lifecycle_hooks)):
            count = lifecycle_hooks.count(hook)
            content.append(f"- `{hook}` ({count} usage{'s' if count > 1 else ''})\n")

    # Detect cleanup functions
    if "return () =>" in code or "return function" in code:
        content.append("\n**Cleanup:**\n")
        content.append("- Cleanup function detected in useEffect\n")

    # Detect dependencies
    deps = re.findall(r"\[([^\]]+)\]\s*\)\s*$", code, re.MULTILINE)
    if deps:
        content.append("\n**Effect Dependencies:**\n")
        content.append("- Dependencies tracked (review for completeness)\n")

    return "".join(content) if content else ""


lifecycle_module: DocumentationModule = {
    "id": "lifecycle",
    "name": "Component Lifecycle",
    "category": "state",
    "triggers": {
        "required_when": ["has_lifecycle_methods"],
        "optional_when": ["is_component", "manages_state"],
        "incompatible_with": [],
    },
    "templates": {
        "markdown": {
            "title": "Component Lifecycle",
            "content": """
## {section_number}. Component Lifecycle

**Lifecycle Hooks:**

{auto_fill_content}

**Mount Phase:**
- Initialization: {init}
- Side effects: {mount_effects}
- Subscriptions: {subscriptions}

**Update Phase:**
- Re-render triggers: {triggers}
- Optimization: {optimization}
- Memoization: {memoization}

**Unmount Phase:**
- Cleanup: {cleanup}
- Subscription cancellation: {cancel}

**Manual Review Required:**
- Are effect dependencies complete?
- Any memory leaks from uncleaned subscriptions?
- Optimization opportunities (useMemo, useCallback)?
""",
            "auto_fill": auto_fill_lifecycle,
            "manual_prompts": [
                "Document mount/unmount behavior",
                "Document re-render optimization",
                "Note cleanup requirements",
            ],
        },
        "schema": {
            "definition": {
                "type": "object",
                "properties": {
                    "lifecycle": {
                        "type": "object",
                        "properties": {
                            "effects": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "hook": {"type": "string"},
                                        "dependencies": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                        },
                                        "cleanup": {"type": "boolean"},
                                    },
                                    "required": ["hook", "dependencies"],
                                },
                            }
                        },
                    }
                },
            },
            "validation_rules": {
                "lifecycle": "Must document all effects and their dependencies",
            },
        },
        "jsdoc": {
            "patterns": [
                "/** @lifecycle {phase} - {description} */",
                "/** @effect {description} */",
                "/** @cleanup {description} */",
            ],
            "examples": [
                "/** @lifecycle mount - Subscribes to WebSocket connection */",
                "/** @effect Fetches user data on mount and when userId changes */",
                "/** @cleanup Cancels pending requests and closes WebSocket */",
            ],
        },
    },
}
