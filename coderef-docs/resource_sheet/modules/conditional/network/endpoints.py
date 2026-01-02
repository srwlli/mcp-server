"""
API Endpoints documentation module.

WO-RESOURCE-SHEET-MCP-TOOL-001
"""

from typing import Dict, Any
from ....types import DocumentationModule


def auto_fill_endpoints(scan_data: Dict[str, Any]) -> str:
    """Auto-fill endpoints documentation from coderef scan data."""
    if not scan_data:
        return ""

    code = scan_data.get("code", "")
    content = []

    # Detect API endpoints
    import re

    # Detect fetch/axios calls
    endpoints = re.findall(r'["\']([/\w-]+(?:/[:\w-]+)*)["\']', code)
    http_methods = re.findall(r'\.(get|post|put|patch|delete)\(', code)

    if endpoints:
        content.append("**API Endpoints:**\n")
        for endpoint in sorted(set(endpoints)):
            if endpoint.startswith("/"):
                content.append(f"- `{endpoint}` - (document method and purpose)\n")

    if http_methods:
        content.append("\n**HTTP Methods:**\n")
        for method in sorted(set(http_methods)):
            content.append(f"- `{method.upper()}`\n")

    return "".join(content) if content else ""


endpoints_module: DocumentationModule = {
    "id": "endpoints",
    "name": "API Endpoints",
    "category": "network",
    "triggers": {
        "required_when": ["makes_network_calls"],
        "optional_when": [],
        "incompatible_with": [],
    },
    "templates": {
        "markdown": {
            "title": "API Endpoints",
            "content": """
## {section_number}. API Endpoints

**Endpoints:**

{auto_fill_content}

**Request Format:**
- Headers: {headers}
- Body: {body}
- Query params: {query}

**Response Format:**
- Success (2xx): {success}
- Error (4xx/5xx): {error}

**Manual Review Required:**
- Rate limiting considerations?
- Pagination support?
- API versioning?
""",
            "auto_fill": auto_fill_endpoints,
            "manual_prompts": [
                "Document request/response format",
                "Document error responses",
                "Note rate limiting or pagination",
            ],
        },
        "schema": {
            "definition": {
                "type": "object",
                "properties": {
                    "endpoints": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "path": {"type": "string"},
                                "method": {
                                    "type": "string",
                                    "enum": ["GET", "POST", "PUT", "PATCH", "DELETE"],
                                },
                                "request": {"type": "object"},
                                "response": {"type": "object"},
                            },
                            "required": ["path", "method"],
                        },
                    }
                },
            },
            "validation_rules": {
                "endpoints": "Must document all API endpoints",
            },
        },
        "jsdoc": {
            "patterns": [
                "/** @endpoint {method} {path} - {description} */",
                "/** @returns {Promise<Response>} */",
            ],
            "examples": [
                "/** @endpoint GET /api/users - Fetches user list */",
                "/** @returns {Promise<User[]>} Array of user objects */",
            ],
        },
    },
}
