"""
Retry Logic documentation module.

WO-RESOURCE-SHEET-MCP-TOOL-001
"""

from typing import Dict, Any
from ....types import DocumentationModule


def auto_fill_retry(scan_data: Dict[str, Any]) -> str:
    """Auto-fill retry logic documentation from coderef scan data."""
    if not scan_data:
        return ""

    code = scan_data.get("code", "")
    content = []

    # Detect retry patterns
    import re

    if "retry" in code.lower() or "attempt" in code.lower():
        content.append("**Retry Logic:**\n")
        content.append("- Retry mechanism detected\n")

    # Detect retry libraries
    if "axios-retry" in scan_data.get("imports", []):
        content.append("\n**Retry Library:**\n")
        content.append("- `axios-retry` configured\n")

    # Detect exponential backoff
    if "exponential" in code.lower() or "backoff" in code.lower():
        content.append("\n**Backoff Strategy:**\n")
        content.append("- Exponential backoff detected\n")

    return "".join(content) if content else ""


retry_module: DocumentationModule = {
    "id": "retry",
    "name": "Retry Logic",
    "category": "network",
    "triggers": {
        "required_when": ["has_retry_logic"],
        "optional_when": ["makes_network_calls"],
        "incompatible_with": [],
    },
    "templates": {
        "markdown": {
            "title": "Retry Logic",
            "content": """
## {section_number}. Retry Logic

**Retry Configuration:**

{auto_fill_content}

**Retry Parameters:**
- Max attempts: {max_attempts}
- Backoff strategy: {backoff}
- Timeout: {timeout}

**Retry Conditions:**
- Status codes: {status_codes}
- Error types: {error_types}
- Idempotency: {idempotency}

**Manual Review Required:**
- Circuit breaker pattern used?
- Jitter added to backoff?
- Maximum backoff duration?
""",
            "auto_fill": auto_fill_retry,
            "manual_prompts": [
                "Document retry parameters",
                "Document retry conditions",
                "Note circuit breaker usage",
            ],
        },
        "schema": {
            "definition": {
                "type": "object",
                "properties": {
                    "retry": {
                        "type": "object",
                        "properties": {
                            "max_attempts": {"type": "number"},
                            "backoff": {
                                "type": "string",
                                "enum": ["linear", "exponential", "constant"],
                            },
                            "retry_on": {
                                "type": "array",
                                "items": {"type": "number"},
                            },
                        },
                        "required": ["max_attempts", "backoff"],
                    }
                },
            },
            "validation_rules": {
                "retry": "Must document retry configuration",
            },
        },
        "jsdoc": {
            "patterns": [
                "/** @retry {max_attempts} attempts - {backoff} */",
                "/** @retry-on {status_codes} */",
            ],
            "examples": [
                "/** @retry 3 attempts - exponential backoff */",
                "/** @retry-on [500, 502, 503, 504] - Server errors */",
            ],
        },
    },
}
