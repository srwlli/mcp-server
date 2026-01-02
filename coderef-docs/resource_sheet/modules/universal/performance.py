"""
Performance Module - Limits, Bottlenecks, and Budgets.

WO-RESOURCE-SHEET-MCP-TOOL-001
"""

from ...types import DocumentationModule, ModuleTriggers, ModuleTemplates, ModuleExtraction


# Module Definition (stub for Phase 1)
performance_module = DocumentationModule(
    id="performance",
    name="Performance Characteristics",
    description="Documents performance limits, bottlenecks, and budgets",
    category="universal",
    triggers=ModuleTriggers(required_when=[], optional_when=[], incompatible_with=[]),
    templates=ModuleTemplates(
        markdown={
            "section_title": "## 4. Performance",
            "content": "⚠️ Performance documentation module - to be implemented",
            "auto_fill": lambda data: "",
            "manual_prompts": [],
        },
        schema={"definition": {}, "validation_rules": {}},
        jsdoc={"patterns": [], "examples": []},
    ),
    extraction=ModuleExtraction(
        from_coderef_scan=lambda data: {},
        from_ast=lambda ast: {},
        from_user=[],
        validation=lambda data: {"valid": True, "errors": [], "warnings": []},
    ),
    version="1.0.0",
    auto_fill_capable=False,
)
