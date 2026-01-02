"""
Accessibility documentation module.

WO-RESOURCE-SHEET-MCP-TOOL-001
"""

from typing import Dict, Any
from ....types import DocumentationModule


def auto_fill_accessibility(scan_data: Dict[str, Any]) -> str:
    """Auto-fill accessibility documentation from coderef scan data."""
    if not scan_data:
        return ""

    code = scan_data.get("code", "")
    content = []

    # Detect ARIA attributes
    import re

    aria_attrs = re.findall(r"aria-[\w-]+", code)
    if aria_attrs:
        content.append("**Detected ARIA Attributes:**\n")
        for attr in sorted(set(aria_attrs)):
            content.append(f"- `{attr}`\n")

    # Detect role attributes
    roles = re.findall(r'role=["\'](\w+)["\']', code)
    if roles:
        content.append("\n**Detected Roles:**\n")
        for role in sorted(set(roles)):
            content.append(f"- `{role}`\n")

    # Detect semantic HTML
    semantic_tags = re.findall(r"<(nav|main|article|section|aside|header|footer)", code)
    if semantic_tags:
        content.append("\n**Semantic HTML Elements:**\n")
        for tag in sorted(set(semantic_tags)):
            content.append(f"- `<{tag}>`\n")

    return "".join(content) if content else ""


accessibility_module: DocumentationModule = {
    "id": "accessibility",
    "name": "Accessibility (A11y)",
    "category": "ui",
    "triggers": {
        "required_when": ["has_aria_attributes"],
        "optional_when": ["is_component", "has_jsx"],
        "incompatible_with": [],
    },
    "templates": {
        "markdown": {
            "title": "Accessibility (A11y)",
            "content": """
## {section_number}. Accessibility (A11y)

**ARIA Implementation:**

{auto_fill_content}

**Keyboard Navigation:**
- Tab order: {tab_order}
- Focus management: {focus}
- Keyboard shortcuts: {shortcuts}

**Screen Reader Support:**
- Labels: {labels}
- Live regions: {live_regions}
- Announcements: {announcements}

**Manual Review Required:**
- WCAG compliance level (A, AA, AAA)?
- Any dynamic content that needs announcements?
- Focus trap considerations?
""",
            "auto_fill": auto_fill_accessibility,
            "manual_prompts": [
                "Document keyboard navigation support",
                "Document screen reader behavior",
                "Note WCAG compliance level",
            ],
        },
        "schema": {
            "definition": {
                "type": "object",
                "properties": {
                    "accessibility": {
                        "type": "object",
                        "properties": {
                            "wcag_level": {
                                "type": "string",
                                "enum": ["A", "AA", "AAA"],
                            },
                            "aria_attributes": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "keyboard_support": {"type": "boolean"},
                            "screen_reader_tested": {"type": "boolean"},
                        },
                    }
                },
            },
            "validation_rules": {
                "accessibility": "Must meet minimum WCAG AA standards",
            },
        },
        "jsdoc": {
            "patterns": [
                "/** @a11y {description} */",
                "/** @aria {attribute} - {usage} */",
            ],
            "examples": [
                "/** @a11y Fully keyboard navigable with tab and arrow keys */",
                "/** @aria aria-label - Provides accessible name for icon button */",
            ],
        },
    },
}
