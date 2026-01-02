"""
Error Handling documentation module.

WO-RESOURCE-SHEET-MCP-TOOL-001
"""

from typing import Dict, Any
from ....types import DocumentationModule


def auto_fill_errors(scan_data: Dict[str, Any]) -> str:
    """Auto-fill error handling documentation from coderef scan data."""
    if not scan_data:
        return ""

    code = scan_data.get("code", "")
    content = []

    # Detect try/catch blocks
    import re

    try_blocks = len(re.findall(r"\btry\s*\{", code))
    if try_blocks > 0:
        content.append(f"**Error Handling:**\n")
        content.append(f"- {try_blocks} try/catch block{'s' if try_blocks > 1 else ''}\n")

    # Detect error types
    error_types = re.findall(r"catch\s*\(\s*(\w+)\s*:", code)
    if error_types:
        content.append("\n**Error Types:**\n")
        for err_type in sorted(set(error_types)):
            content.append(f"- `{err_type}`\n")

    # Detect error boundaries (React)
    if "componentDidCatch" in code or "ErrorBoundary" in code:
        content.append("\n**Error Boundary:**\n")
        content.append("- React Error Boundary implemented\n")

    return "".join(content) if content else ""


error_handling_module: DocumentationModule = {
    "id": "error_handling",
    "name": "Error Handling",
    "category": "network",
    "triggers": {
        "required_when": ["has_error_handling"],
        "optional_when": ["makes_network_calls"],
        "incompatible_with": [],
    },
    "templates": {
        "markdown": {
            "title": "Error Handling",
            "content": """
## {section_number}. Error Handling

**Error Detection:**

{auto_fill_content}

**Error Recovery:**
- Fallbacks: {fallbacks}
- User feedback: {feedback}
- Logging: {logging}

**Error Types:**
- Network errors: {network}
- Validation errors: {validation}
- Business logic errors: {business}

**Manual Review Required:**
- Global error handler configured?
- Error reporting service (Sentry, etc.)?
- User-facing error messages?
""",
            "auto_fill": auto_fill_errors,
            "manual_prompts": [
                "Document error recovery strategies",
                "Document error logging/reporting",
                "Note user-facing error handling",
            ],
        },
        "schema": {
            "definition": {
                "type": "object",
                "properties": {
                    "error_handling": {
                        "type": "object",
                        "properties": {
                            "strategy": {
                                "type": "string",
                                "enum": ["throw", "return", "callback"],
                            },
                            "error_boundary": {"type": "boolean"},
                            "logging": {"type": "boolean"},
                            "user_feedback": {"type": "boolean"},
                        },
                        "required": ["strategy"],
                    }
                },
            },
            "validation_rules": {
                "error_handling": "Must document error handling strategy",
            },
        },
        "jsdoc": {
            "patterns": [
                "/** @throws {{ErrorType}} - {description} */",
                "/** @catches {error_type} */",
            ],
            "examples": [
                "/** @throws {NetworkError} - When API request fails */",
                "/** @catches ValidationError - Returns default value on error */",
            ],
        },
    },
}
