"""
Authentication documentation module.

WO-RESOURCE-SHEET-MCP-TOOL-001
"""

from typing import Dict, Any
from ....types import DocumentationModule


def auto_fill_auth(scan_data: Dict[str, Any]) -> str:
    """Auto-fill authentication documentation from coderef scan data."""
    if not scan_data:
        return ""

    code = scan_data.get("code", "")
    imports = scan_data.get("imports", [])
    content = []

    # Detect auth headers
    import re

    if "Authorization" in code or "Bearer" in code:
        content.append("**Authentication:**\n")
        content.append("- Bearer token authentication detected\n")

    # Detect auth libraries
    auth_libs = [lib for lib in ["jwt", "auth0", "passport", "next-auth"] if lib in imports]
    if auth_libs:
        content.append("\n**Auth Libraries:**\n")
        for lib in auth_libs:
            content.append(f"- `{lib}`\n")

    # Detect token handling
    if "token" in code.lower() or "getToken" in code:
        content.append("\n**Token Management:**\n")
        content.append("- Token storage/retrieval detected\n")

    return "".join(content) if content else ""


auth_module: DocumentationModule = {
    "id": "auth",
    "name": "Authentication & Authorization",
    "category": "network",
    "triggers": {
        "required_when": ["handles_auth"],
        "optional_when": ["makes_network_calls"],
        "incompatible_with": [],
    },
    "templates": {
        "markdown": {
            "title": "Authentication & Authorization",
            "content": """
## {section_number}. Authentication & Authorization

**Auth Strategy:**

{auto_fill_content}

**Token Management:**
- Storage: {storage}
- Refresh: {refresh}
- Expiration: {expiration}

**Permissions:**
- Role-based: {roles}
- Resource-based: {resources}

**Manual Review Required:**
- Token refresh strategy?
- Session management?
- Permission scopes?
""",
            "auto_fill": auto_fill_auth,
            "manual_prompts": [
                "Document authentication method",
                "Document token refresh logic",
                "Note permission/authorization rules",
            ],
        },
        "schema": {
            "definition": {
                "type": "object",
                "properties": {
                    "authentication": {
                        "type": "object",
                        "properties": {
                            "method": {
                                "type": "string",
                                "enum": ["jwt", "session", "oauth", "api_key"],
                            },
                            "token_storage": {
                                "type": "string",
                                "enum": ["cookie", "localStorage", "memory"],
                            },
                            "refresh_enabled": {"type": "boolean"},
                        },
                        "required": ["method"],
                    }
                },
            },
            "validation_rules": {
                "authentication": "Must document auth method and token handling",
            },
        },
        "jsdoc": {
            "patterns": [
                "/** @auth {method} - {description} */",
                "/** @requires-auth {permission} */",
            ],
            "examples": [
                "/** @auth JWT - Requires valid Bearer token */",
                "/** @requires-auth admin - Admin role required */",
            ],
        },
    },
}
