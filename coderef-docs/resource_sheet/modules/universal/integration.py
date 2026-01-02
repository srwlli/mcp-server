"""
Integration Module - How Element Connects to Other Code.

WO-RESOURCE-SHEET-MCP-TOOL-001

Universal module documenting integration points, consumers, and dependencies.
"""

from ...types import DocumentationModule, ModuleTriggers, ModuleTemplates, ModuleExtraction


def auto_fill_integration(data: dict) -> str:
    """Auto-fill integration section from extracted data."""
    used_by = data.get("used_by", [])
    uses = data.get("uses", [])
    events = data.get("events", {})

    content = ""

    if used_by:
        content += "**Used By:**\n"
        for consumer in used_by[:10]:
            content += f"- `{consumer}`\n"
        if len(used_by) > 10:
            content += f"- ...and {len(used_by) - 10} more\n"
        content += "\n"

    if uses:
        content += "**Uses:**\n"
        for dependency in uses[:10]:
            content += f"- `{dependency}`\n"
        if len(uses) > 10:
            content += f"- ...and {len(uses) - 10} more\n"
        content += "\n"

    if events:
        content += "**Events:**\n"
        for event_type, event_list in events.items():
            content += f"\n*{event_type.capitalize()}:*\n"
            for event in event_list:
                content += f"- `{event}`\n"

    return content


def extract_from_coderef_scan(scan_data: dict) -> dict:
    """Extract integration data from coderef_scan output."""
    return {
        "used_by": scan_data.get("consumers", []),
        "uses": scan_data.get("dependencies", []),
        "events": {
            "emits": scan_data.get("events_emitted", []),
            "listens": scan_data.get("events_listened", []),
        },
    }


def validate_integration_data(data: dict) -> dict:
    """Validate extracted integration data."""
    warnings = []

    if not data.get("used_by") and not data.get("uses"):
        warnings.append("No integration points detected - is this element isolated?")

    return {
        "valid": True,  # Integration data is always optional
        "errors": [],
        "warnings": warnings,
    }


# Module Definition
integration_module = DocumentationModule(
    id="integration",
    name="Integration Points",
    description="Documents how this element integrates with other code",
    category="universal",
    triggers=ModuleTriggers(
        required_when=[],  # Always included
        optional_when=[],
        incompatible_with=[],
    ),
    templates=ModuleTemplates(
        markdown={
            "section_title": "## 2. Integration Points",
            "content": """
**Used By:** (Consumers of this element)
{{#each used_by}}
- `{{this}}`
{{/each}}

**Uses:** (Dependencies)
{{#each uses}}
- `{{this}}`
{{/each}}

**Events:**
{{#if events.emits}}
*Emits:*
{{#each events.emits}}
- `{{this}}`
{{/each}}
{{/if}}

{{#if events.listens}}
*Listens:*
{{#each events.listens}}
- `{{this}}`
{{/each}}
{{/if}}
            """.strip(),
            "auto_fill": auto_fill_integration,
            "manual_prompts": [
                "Any indirect integration points not detected?",
                "Are there runtime dependencies?",
            ],
        },
        schema={
            "definition": {
                "integration": {
                    "type": "object",
                    "properties": {
                        "used_by": {"type": "array", "items": {"type": "string"}},
                        "uses": {"type": "array", "items": {"type": "string"}},
                        "events": {
                            "type": "object",
                            "properties": {
                                "emits": {"type": "array", "items": {"type": "string"}},
                                "listens": {"type": "array", "items": {"type": "string"}},
                            },
                        },
                    },
                }
            },
            "validation_rules": {},
        },
        jsdoc={
            "patterns": [
                "/** @emits {{event_name}} - {{description}} */",
                "/** @listens {{event_name}} */",
                "/** @requires {{dependency}} */",
            ],
            "examples": [
                "/** @emits auth:login - Fired when user logs in */",
                "/** @requires axios */",
            ],
        },
    ),
    extraction=ModuleExtraction(
        from_coderef_scan=extract_from_coderef_scan,
        from_ast=lambda ast: {},
        from_user=[
            {"question": "What depends on this?", "type": "array"},
            {"question": "What does this depend on?", "type": "array"},
        ],
        validation=validate_integration_data,
    ),
    version="1.0.0",
    auto_fill_capable=True,
)
