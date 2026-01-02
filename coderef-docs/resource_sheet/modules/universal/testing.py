"""
Testing Module - Test Patterns, Coverage, and Mocks.

WO-RESOURCE-SHEET-MCP-TOOL-001
"""

from ...types import DocumentationModule, ModuleTriggers, ModuleTemplates, ModuleExtraction


# Module Definition (stub for Phase 1)
testing_module = DocumentationModule(
    id="testing",
    name="Testing Strategy",
    description="Documents test patterns, coverage, and mocking approaches",
    category="universal",
    triggers=ModuleTriggers(required_when=[], optional_when=[], incompatible_with=[]),
    templates=ModuleTemplates(
        markdown={
            "section_title": "## 3. Testing Strategy",
            "content": "⚠️ Testing documentation module - to be implemented",
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
