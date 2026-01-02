"""
Hook Signature documentation module.

WO-RESOURCE-SHEET-MCP-TOOL-001
"""

from typing import Dict, Any
from ....types import DocumentationModule


def auto_fill_hook_signature(scan_data: Dict[str, Any]) -> str:
    """Auto-fill hook signature documentation from coderef scan data."""
    if not scan_data:
        return ""

    code = scan_data.get("code", "")
    content = []

    # Detect hook function signature
    import re

    hook_match = re.search(r"function (use\w+)\s*\(([^)]*)\)", code)
    if hook_match:
        hook_name = hook_match.group(1)
        params = hook_match.group(2)
        content.append(f"**Hook Signature:**\n")
        content.append(f"```typescript\n{hook_name}({params})\n```\n")

    # Detect return value
    return_match = re.search(r"return\s+({[^}]+}|\[[^\]]+\]|\w+)", code)
    if return_match:
        content.append("\n**Returns:**\n")
        content.append(f"- Type: `{return_match.group(1)[:50]}...`\n")

    return "".join(content) if content else ""


hook_signature_module: DocumentationModule = {
    "id": "hook_signature",
    "name": "Hook Signature",
    "category": "hooks",
    "triggers": {
        "required_when": ["is_hook"],
        "optional_when": [],
        "incompatible_with": ["is_class", "is_component"],
    },
    "templates": {
        "markdown": {
            "title": "Hook Signature",
            "content": """
## {section_number}. Hook Signature

**Function Signature:**

{auto_fill_content}

**Parameters:**
- Required: {required_params}
- Optional: {optional_params}
- Defaults: {defaults}

**Return Value:**
- Type: {return_type}
- Structure: {structure}
- Stable reference: {stable}

**Manual Review Required:**
- Are parameter types documented?
- Return value memoization?
- TypeScript generics used?
""",
            "auto_fill": auto_fill_hook_signature,
            "manual_prompts": [
                "Document all parameters",
                "Document return value structure",
                "Note memoization strategy",
            ],
        },
        "schema": {
            "definition": {
                "type": "object",
                "properties": {
                    "hook": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "parameters": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "type": {"type": "string"},
                                        "required": {"type": "boolean"},
                                        "default": {"type": "string"},
                                    },
                                    "required": ["name", "type"],
                                },
                            },
                            "returns": {"type": "string"},
                        },
                        "required": ["name", "parameters", "returns"],
                    }
                },
            },
            "validation_rules": {
                "hook": "Must document signature completely",
            },
        },
        "jsdoc": {
            "patterns": [
                "/** @hook {name} */",
                "/** @param {{type}} {name} - {description} */",
                "/** @returns {{type}} {description} */",
            ],
            "examples": [
                "/** @hook useAuth */",
                "/** @param {string} userId - User ID to authenticate */",
                "/** @returns {AuthState} Authentication state object */",
            ],
        },
    },
}
