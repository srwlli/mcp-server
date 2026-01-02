"""
Events documentation module.

WO-RESOURCE-SHEET-MCP-TOOL-001
"""

from typing import Dict, Any
from ....types import DocumentationModule


def auto_fill_events(scan_data: Dict[str, Any]) -> str:
    """Auto-fill events documentation from coderef scan data."""
    if not scan_data:
        return ""

    code = scan_data.get("code", "")
    content = []

    # Detect event handlers (onClick, onChange, onSubmit, etc.)
    import re

    event_handlers = re.findall(r"on[A-Z]\w+", code)
    if event_handlers:
        content.append("**Detected Event Handlers:**\n")
        for handler in sorted(set(event_handlers)):
            content.append(f"- `{handler}` - (document trigger and behavior)\n")

    # Detect custom events (emit, dispatch, trigger)
    custom_events = re.findall(r"(?:emit|dispatch|trigger)\(['\"](\w+)['\"]", code)
    if custom_events:
        content.append("\n**Custom Events Emitted:**\n")
        for event in sorted(set(custom_events)):
            content.append(f"- `{event}` - (document payload and conditions)\n")

    return "".join(content) if content else ""


events_module: DocumentationModule = {
    "id": "events",
    "name": "Events & Interactions",
    "category": "ui",
    "triggers": {
        "required_when": ["has_event_handlers"],
        "optional_when": ["is_component", "has_jsx"],
        "incompatible_with": [],
    },
    "templates": {
        "markdown": {
            "title": "Events & Interactions",
            "content": """
## {section_number}. Events & Interactions

**Event Handlers:**

{auto_fill_content}

**Event Flow:**
- Bubbling: {bubbling}
- Capture: {capture}
- Delegation: {delegation}

**Manual Review Required:**
- Are there synthetic events or event pooling considerations?
- Any event debouncing or throttling?
- Custom event dispatching?
""",
            "auto_fill": auto_fill_events,
            "manual_prompts": [
                "Document event bubbling behavior",
                "Document event capture usage",
                "Note any event delegation patterns",
            ],
        },
        "schema": {
            "definition": {
                "type": "object",
                "properties": {
                    "events": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "handler": {"type": "string"},
                                "payload": {"type": "object"},
                                "bubbles": {"type": "boolean"},
                            },
                            "required": ["name", "handler"],
                        },
                    }
                },
            },
            "validation_rules": {
                "events": "Must document all event handlers",
            },
        },
        "jsdoc": {
            "patterns": [
                "/** @fires {event_name} - {description} */",
                "/** @listens {event_name} */",
            ],
            "examples": [
                "/** @fires submit - Form submission with validated data */",
                "/** @listens click - Button click handler */",
            ],
        },
    },
}
